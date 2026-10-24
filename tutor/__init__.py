"""Curriculum-grounded AI tutor (Priority 3, part 1). Pending SME review.

Students ask questions at /tutor or from the drawer on lesson and lab pages. Answers are built only from this course's
lesson sections, explanation-ladder rungs, glossary and lab guides (tutor.retrieval, BM25), and every answer cites the
exact section, rung and glossary terms it used. Graded answer keys are never indexed; requests for quiz/test answers and
off-topic questions are refused (tutor.guard). When NOVAK_AI_API_KEY is set, an OpenAI-compatible chat endpoint may
rephrase the retrieved passages, but its output is accepted only if every sentence is grounded in those passages;
otherwise the deterministic extractive answer is returned. Instructors can turn the tutor off per class and see the
questions their students ask.
"""
import json
import os
import re
import urllib.request
from collections import Counter
from datetime import datetime, timezone

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import guard as G
from . import retrieval as R

_models = {}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def define_models(db):
    if 'm' in _models:
        return _models['m']

    class TutorSetting(db.Model):
        __tablename__ = 'tutor_setting'
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), primary_key=True)
        enabled = db.Column(db.Boolean, default=True, nullable=False)
        updated_at = db.Column(db.DateTime, default=utcnow)

    class TutorQuestion(db.Model):
        __tablename__ = 'tutor_question'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), index=True)
        course = db.Column(db.String(20))
        question = db.Column(db.Text, nullable=False)
        outcome = db.Column(db.String(20), nullable=False)    # answered|cheat|offtopic|disabled
        cites_json = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=utcnow)

    _models['m'] = (TutorSetting, TutorQuestion)
    return _models['m']


# ---------------------------------------------------------------------------------------------- answer engine
def grounded(answer, passages):
    """True when every sentence of an LLM answer is built from words in the retrieved passages."""
    vocab = set(R.tokens(' '.join(passages)))
    sents = [s for s in re.split(r'(?<=[.!?])\s+', answer or '') if s.strip()]
    if not sents:
        return False
    for s in sents:
        t = [w for w in R.tokens(s) if not w.isdigit() and not re.fullmatch(r'\[\d+\]', w)]
        if t and sum(w in vocab for w in t) / len(t) < 0.7:
            return False
    return True


def llm_rephrase(question, passages, post=None):
    """Optional hook. Returns None unless NOVAK_AI_API_KEY is configured and the reply passes the grounding check."""
    key = os.environ.get('NOVAK_AI_API_KEY')
    if not key or not passages:
        return None
    system = ('You are a course tutor. Answer ONLY from the numbered course passages. Cite them like [1]. If the passages do '
              'not answer the question, reply exactly NO_ANSWER. Never give answers to graded quiz or test questions.')
    user = 'Passages:\n' + '\n'.join(f'[{i}] {p}' for i, p in enumerate(passages, 1)) + f'\n\nQuestion: {question}'
    body = {'model': os.environ.get('NOVAK_AI_MODEL', 'novak-tutor'), 'temperature': 0,
            'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]}
    try:
        if post is None:
            req = urllib.request.Request(os.environ.get('NOVAK_AI_API_URL', 'https://api.openai.com/v1/chat/completions'),
                                         data=json.dumps(body).encode(), headers={'Authorization': f'Bearer {key}',
                                                                                    'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=12) as r:
                out = json.loads(r.read().decode())
        else:
            out = post(body)
        text = out['choices'][0]['message']['content'].strip()
    except Exception:
        return None
    if 'NO_ANSWER' in text or not grounded(text, passages):
        return None
    return text


class Tutor:
    def __init__(self, docs):
        self.idx = R.Index(docs)
        self.glossary = [d for d in docs if d['type'] == 'glossary']

    def ask(self, question, course, post=None):
        q = (question or '').strip()[:500]
        if G.is_cheating(q):
            return {'outcome': 'cheat', 'answer': G.CHEAT_REPLY, 'cites': [], 'glossary': []}
        hits = self.idx.search(q, course=course, k=8)
        n_terms = len(set(R.tokens(q)))
        if not hits or not G.on_topic(hits[0][0], self.idx.coverage(q, hits[0][1]), n_terms):
            return {'outcome': 'offtopic', 'answer': G.OFFTOPIC_REPLY, 'cites': [], 'glossary': []}
        top = hits[0][0]
        cites, passages, seen = [], [], set()
        for s, d in hits:
            if s < top * 0.35 or len(cites) >= 4:
                break
            key = (d['type'], d.get('label'), d.get('sid'), d.get('rung'), d.get('term'), d.get('lab_id'))
            if key in seen:
                continue
            sents = R.best_sentences(q, d['text'], 2) or [d['text'][:300]]
            seen.add(key)
            cites.append(dict({k: v for k, v in d.items() if k != 'text'}, quote=' '.join(sents)))
            passages.append(' '.join(sents))
        qt = set(R.tokens(q))
        body = ' '.join(passages).lower()
        gl = [{'term': g['term'], 'definition': g['text']} for g in self.glossary
              if g['term'].lower() in (q.lower() + ' ' + body) or set(R.tokens(g['term'])) <= qt
              or any(c.get('type') == 'glossary' and c.get('term') == g['term'] for c in cites)][:4]
        text = llm_rephrase(q, passages, post=post)
        mode = 'llm' if text else 'extractive'
        if not text:
            text = ' '.join(f'{p} [{i}]' for i, p in enumerate(passages, 1))
        return {'outcome': 'answered', 'answer': text, 'cites': cites, 'glossary': gl, 'mode': mode}


def common_terms(questions, n=12):
    c = Counter()
    for q in questions:
        c.update(set(R.tokens(q)))
    return c.most_common(n)


# ---------------------------------------------------------------------------------------------- Flask wiring
def register(app, db, d):
    TutorSetting, TutorQuestion = define_models(db)
    state = {}

    def load_docs():
        from curriculum_v2 import ladder as LD
        from curriculum_v2.ladder import sections as LSEC
        import interactive_labs as IL
        lessons = []
        for course in d['Course'].query.all():
            for m in d['Module'].query.filter_by(course_id=course.id).all():
                for les in d['Lesson'].query.filter_by(module_id=m.id).all():
                    label = LSEC.lesson_label(les.title)
                    for s in LSEC.sections(LSEC.student_html(les.content or '')):
                        lessons.append((course.code, label, les.title, m.id, les.id, s['sid'], s['heading'], s['html']))
        labs = []
        for code in ('ITSUP', 'NETOPS', 'CLIENT'):
            try:
                from types import SimpleNamespace as _NS
                labs += [(code, lab if isinstance(lab, dict) else IL.get_lab(lab)) for lab in IL.labs_for_course(_NS(code=code))]
            except Exception:
                pass
        return R.build_docs(lessons, LD.ladder(), d['glossary'], labs)

    def tutor():
        if 't' not in state:
            state['t'] = Tutor(load_docs())
        return state['t']

    def enabled(section_id):
        s = db.session.get(TutorSetting, section_id) if section_id else None
        return True if s is None else bool(s.enabled)

    def student_sections():
        rows = d['Enrollment'].query.filter_by(user_id=current_user.id).all()
        return [db.session.get(d['ClassSection'], r.section_id) for r in rows]

    def course_code(section):
        c = db.session.get(d['Course'], section.course_id)
        return c.code if c else None

    def links(res, section):
        for c in res['cites']:
            if c['type'] in ('lesson', 'rung') and section is not None:
                les = None
                if c['type'] == 'rung':
                    les = next((x for x in tutor().idx.docs if x['type'] == 'lesson' and x['course'] == c['course']
                                and x['label'] == c['label'] and x['sid'] == c['sid']), None)
                src = les or c
                if src.get('lesson_id'):
                    c['url'] = url_for('view_lesson', section_id=section.id, module_id=src['module_id'],
                                       lesson_id=src['lesson_id']) + f'#ladder-{c["sid"]}'
                    c['lesson'] = src.get('lesson')
            elif c['type'] == 'lab':
                c['url'] = url_for('interactive_lab', lab_id=c['lab_id'])
        return res

    def do_ask(question, section_id):
        secs = [s for s in student_sections() if s]
        section = next((s for s in secs if s.id == section_id), None) or (secs[0] if secs else None)
        if section is None:
            abort(404)
        course = course_code(section)
        if not enabled(section.id):
            res = {'outcome': 'disabled', 'answer': G.DISABLED_REPLY, 'cites': [], 'glossary': []}
        else:
            res = links(tutor().ask(question, course), section)
        db.session.add(TutorQuestion(user_id=current_user.id, section_id=section.id, course=course, question=question[:500],
                                     outcome=res['outcome'], cites_json=json.dumps(
                                         [{k: c.get(k) for k in ('type', 'label', 'sid', 'rung', 'term', 'lab_id')} for c in res['cites']])))
        db.session.commit()
        res['section_id'] = section.id
        return res

    @app.route('/tutor', methods=['GET', 'POST'])
    @login_required
    def tutor_page():
        if current_user.role != 'student':
            abort(403)
        secs = [s for s in student_sections() if s]
        sid = request.values.get('section_id', type=int) or (secs[0].id if secs else None)
        res, q = None, ''
        if request.method == 'POST':
            q = (request.form.get('q') or '').strip()
            if q:
                res = do_ask(q, sid)
        return render_template('tutor/tutor.html', sections=secs, section_id=sid, q=q, res=res,
                               on=enabled(sid) if sid else False)

    @app.route('/api/tutor/ask', methods=['POST'])
    @login_required
    def tutor_api_ask():
        if current_user.role != 'student':
            abort(403)
        data = request.get_json(silent=True) or request.form
        q = (data.get('q') or '').strip()
        if not q:
            return jsonify({'error': 'Ask a question first.'}), 400
        try:
            sid = int(data.get('section_id') or 0)
        except (TypeError, ValueError):
            sid = 0
        return jsonify(do_ask(q, sid))

    @app.route('/instructor/section/<int:section_id>/tutor', methods=['GET', 'POST'])
    @login_required
    def tutor_instructor(section_id):
        section = db.get_or_404(d['ClassSection'], section_id)
        if current_user.role not in ('instructor', 'admin') or not d['can_access_section'](current_user, section):
            abort(403)
        if request.method == 'POST':
            s = db.session.get(TutorSetting, section_id) or TutorSetting(section_id=section_id)
            s.enabled = request.form.get('enabled') == 'on'
            s.updated_at = utcnow()
            db.session.add(s)
            db.session.commit()
            d['audit']('tutor_toggle', f'section {section_id} enabled={s.enabled}')
            flash('AI tutor turned ' + ('on' if s.enabled else 'off') + ' for this class.', 'success')
            return redirect(url_for('tutor_instructor', section_id=section_id), code=303)
        qs = TutorQuestion.query.filter_by(section_id=section_id).order_by(TutorQuestion.created_at.desc()).limit(500).all()
        answered = [q.question for q in qs if q.outcome == 'answered']
        counts = Counter(q.outcome for q in qs)
        sec_hits = Counter()
        for q in qs:
            for c in json.loads(q.cites_json or '[]')[:1]:
                if c.get('label'):
                    sec_hits[f"{c['label']} · {c.get('sid')}"] += 1
        return render_template('tutor/instructor.html', section=section, on=enabled(section_id), recent=qs[:30],
                               terms=common_terms(answered), counts=counts, sections=sec_hits.most_common(8))

    @app.context_processor
    def _tutor_ctx():
        def default_section():
            if not current_user.is_authenticated or current_user.role != 'student':
                return None
            r = d['Enrollment'].query.filter_by(user_id=current_user.id).first()
            return r.section_id if r else None
        return {'tutor_drawer_on': lambda section_id: bool(section_id) and enabled(section_id),
                'tutor_default_section': default_section}

    api = type('TutorAPI', (), {})()
    api.TutorSetting, api.TutorQuestion, api.tutor, api.enabled = TutorSetting, TutorQuestion, tutor, enabled
    app.extensions['ciwt_tutor'] = api
    return api
