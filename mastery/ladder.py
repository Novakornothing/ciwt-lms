"""Explanation ladder engine (pass 19): per-student, in-place re-explanation of lesson sections.

Content comes from curriculum_v2/ladder (one file per chapter; every rung is "Pending SME review"). This module
owns the tables, the lesson-page rendering, the student routes (micro-check answer, "Explain it another way",
browse a rung, Helix offer), the learner profile ("What helps you learn"), the instructor controls and analytics,
and the hooks other features use (Who needs me, the briefing, mastery reviews, the chapter check result page).

Rules that never bend:
* Micro-checks never touch grades, the gradebook, quiz/test attempts or the mastery estimates. They are practice.
* Helix is used only when the student's consent is current and Helix is on for the class, and only to OFFER the
  next rung (the student decides). The server re-checks consent before logging an offer.
* The original explanation (R0) is never removed: "See the original" is on every swapped section, and nothing is
  shown first in its place unless the instructor turns on "adapt first presentation" for the class.
Policy (progression, profile threshold): mastery/ladder_policy.py.
"""
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from curriculum_v2 import ladder as LD
from curriculum_v2.ladder import schema as LS
from curriculum_v2.ladder import sections as LSEC
from . import ladder_policy as LP

_cache = {}
DEMO_DOMAIN = '@lms.local'
SOURCES = ('button', 'dontget', 'helix')
REWRITE_MIN = 5          # analytics: flag "the original may need rewriting" with at least 5 first answers ...
REWRITE_SHARE = 0.5      # ... and at least half of them wrong on the original's check
HOW = {'R1': 'said more simply', 'R2': 'as an analogy', 'R3': 'as a picture or step by step', 'R4': 'as something to try'}


STYLE = {'R0': 'Original', 'R1': 'Plain language', 'R2': 'Analogy', 'R3': 'Visual / step by step', 'R4': 'Try it'}

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def define_ladder_models(db):
    if 'm' in _cache:
        return _cache['m']

    class LadderSetting(db.Model):
        """Per-class switches. No row = defaults (on, 4 rungs, micro-checks shown, original always first)."""
        __tablename__ = 'ladder_setting'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), unique=True, nullable=False)
        enabled = db.Column(db.Boolean, default=True)
        max_rung = db.Column(db.Integer, default=4)
        micro_checks = db.Column(db.Boolean, default=True)
        adapt_first = db.Column(db.Boolean, default=False)
        require_check_to_advance = db.Column(db.Boolean, default=True)   # comprehension gate (default on)
        gate_quiz_on_ladder = db.Column(db.Boolean, default=False)       # strict: chapter quiz waits for the gate too
        overrides_json = db.Column(db.Text, default='{}')     # {"label|sid": {"off": true} | {"max": 2}}
        updated_at = db.Column(db.DateTime, default=utcnow)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    class LadderState(db.Model):
        """Where one student is on one section's ladder, in one class."""
        __tablename__ = 'ladder_state'
        __table_args__ = (db.UniqueConstraint('user_id', 'section_id', 'course', 'label', 'sid', name='uq_ladder_state'),)
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        course = db.Column(db.String(20), nullable=False)
        label = db.Column(db.String(10), nullable=False)
        sid = db.Column(db.String(80), nullable=False)
        lesson_id = db.Column(db.Integer)
        current = db.Column(db.String(4), default='R0')
        tried_json = db.Column(db.Text, default='["R0"]')
        resolved = db.Column(db.String(4))
        misses = db.Column(db.Integer, default=0)
        requests = db.Column(db.Integer, default=0)
        adapted = db.Column(db.Boolean, default=False)
        exhausted_at = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=utcnow)
        updated_at = db.Column(db.DateTime, default=utcnow)

    class LadderEvent(db.Model):
        """Append-only log: check | request | show | see_original | helix_offer | resolved | exhausted | reset."""
        __tablename__ = 'ladder_event'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), index=True)
        course = db.Column(db.String(20))
        label = db.Column(db.String(10))
        sid = db.Column(db.String(80))
        kind = db.Column(db.String(20), nullable=False)
        rung = db.Column(db.String(4))
        check_id = db.Column(db.String(160))
        answer = db.Column(db.String(400))
        correct = db.Column(db.Boolean)
        mc = db.Column(db.String(60))
        source = db.Column(db.String(20))
        from_rung = db.Column(db.String(4))                  # request: the rung the student was on
        created_at = db.Column(db.DateTime, default=utcnow, index=True)

    class LadderBypass(db.Model):
        """Instructor exemption from the comprehension gate: one student, one lesson (lesson_id NULL = every lesson)."""
        __tablename__ = 'ladder_bypass'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        lesson_id = db.Column(db.Integer)
        created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
        created_at = db.Column(db.DateTime, default=utcnow)

    class LadderProfileReset(db.Model):
        """The student reset "What helps you learn": evidence before reset_at is ignored."""
        __tablename__ = 'ladder_profile_reset'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        reset_at = db.Column(db.DateTime, default=utcnow)

    from types import SimpleNamespace
    _cache['m'] = SimpleNamespace(LadderSetting=LadderSetting, LadderState=LadderState, LadderEvent=LadderEvent,
                                  LadderProfileReset=LadderProfileReset, LadderBypass=LadderBypass)
    return _cache['m']


def ensure_ladder_schema(db):
    """Idempotent: gate columns on ladder_setting for databases created before the comprehension gate."""
    from sqlalchemy import inspect, text
    insp = inspect(db.engine)
    if 'ladder_setting' in insp.get_table_names():
        cols = {c['name'] for c in insp.get_columns('ladder_setting')}
        with db.engine.begin() as conn:
            if 'require_check_to_advance' not in cols:
                conn.execute(text('ALTER TABLE ladder_setting ADD COLUMN require_check_to_advance BOOLEAN DEFAULT 1'))
                conn.execute(text('UPDATE ladder_setting SET require_check_to_advance = 1'))
            if 'gate_quiz_on_ladder' not in cols:
                conn.execute(text('ALTER TABLE ladder_setting ADD COLUMN gate_quiz_on_ladder BOOLEAN DEFAULT 0'))
                conn.execute(text('UPDATE ladder_setting SET gate_quiz_on_ladder = 0'))


def _h(s):
    return hashlib.sha256(s.encode()).hexdigest()


def _loads(s, default):
    try:
        return json.loads(s) if s else default
    except ValueError:
        return default


def is_demo_user(u):
    return (getattr(u, 'email', '') or '').endswith(DEMO_DOMAIN)


def register_ladder(app, db, ctx):
    """ctx: d (app models), eng (mastery engine, for Helix consent), enrolled_section, staff_section."""
    m = define_ladder_models(db)
    d = ctx.d

    # ------------------------------------------------------------------ settings
    def settings(section_id):
        s = m.LadderSetting.query.filter_by(section_id=section_id).first()
        if not s:
            return {'enabled': True, 'max_rung': LP.DEFAULT_MAX_RUNG, 'micro_checks': True, 'adapt_first': False,
                    'require_check': True, 'gate_quiz': False, 'overrides': {}, 'row': None}
        return {'enabled': bool(s.enabled), 'max_rung': int(s.max_rung or 0), 'micro_checks': bool(s.micro_checks),
                'adapt_first': bool(s.adapt_first), 'overrides': _loads(s.overrides_json, {}), 'row': s,
                'require_check': s.require_check_to_advance is not False, 'gate_quiz': bool(s.gate_quiz_on_ladder)}

    def course_code(section):
        c = getattr(section, 'course', None) or db.session.get(d.Course, section.course_id)
        return (c.code or '').upper() if c else ''

    def label_of(lesson):
        return LSEC.lesson_label(lesson.title)

    def allowed_for(cfg, label, sid):
        return LP.allowed_rungs(cfg['max_rung'], cfg['overrides'].get(f'{label}|{sid}'))

    # ------------------------------------------------------------------ profile
    def reset_at(user_id):
        r = (m.LadderProfileReset.query.filter_by(user_id=user_id)
             .order_by(m.LadderProfileReset.reset_at.desc()).first())
        return r.reset_at if r else None

    def profile_of(user_id):
        q = m.LadderEvent.query.filter(m.LadderEvent.user_id == user_id,
                                       m.LadderEvent.kind.in_(['check', 'request', 'resolved']))
        since = reset_at(user_id)
        if since:
            q = q.filter(m.LadderEvent.created_at > since)
        secs = {}
        for e in q.order_by(m.LadderEvent.created_at, m.LadderEvent.id).all():
            s = secs.setdefault((e.section_id, e.course, e.label, e.sid),
                                {'lesson': f'{e.course}|{e.label}', 'shown': set(), 'resolved': None})
            if e.kind == 'check' and e.rung:
                s['shown'].add(e.rung)
            elif e.kind == 'request' and e.from_rung:
                s['shown'].add(e.from_rung)
            elif e.kind == 'resolved':
                s['resolved'] = e.rung                      # the latest resolution of the section counts
        p = LP.profile(list(secs.values()))
        p['reset_at'] = since
        return p

    # ------------------------------------------------------------------ state
    def state_row(user_id, section_id, course, label, sid):
        return m.LadderState.query.filter_by(user_id=user_id, section_id=section_id, course=course, label=label,
                                             sid=sid).first()

    def as_state(row):
        return {'current': row.current or 'R0', 'tried': _loads(row.tried_json, ['R0']), 'resolved': row.resolved,
                'misses': row.misses or 0, 'requests': row.requests or 0, 'exhausted': bool(row.exhausted_at),
                'adapted': bool(row.adapted)}

    def save_state(row, st):
        now = utcnow()
        row.current, row.tried_json, row.resolved = st['current'], json.dumps(st['tried']), st['resolved']
        row.misses, row.requests = st['misses'], st['requests']
        row.adapted = bool(st.get('adapted'))
        if st['exhausted'] and not row.exhausted_at:
            row.exhausted_at = now
        if not st['exhausted']:
            row.exhausted_at = None
        row.updated_at = now

    def ensure_row(user, section, course, label, sid, lesson_id, cfg, prof):
        row = state_row(user.id, section.id, course, label, sid)
        if row:
            return row
        st = LP.start(allowed_for(cfg, label, sid), prof['best'], cfg['adapt_first'])
        row = m.LadderState(user_id=user.id, section_id=section.id, course=course, label=label, sid=sid,
                            lesson_id=lesson_id)
        save_state(row, st)
        db.session.add(row)
        return row

    def log(user_id, section_id, course, label, sid, kind, **kw):
        db.session.add(m.LadderEvent(user_id=user_id, section_id=section_id, course=course, label=label, sid=sid,
                                     kind=kind, **kw))

    # ------------------------------------------------------------------ rendering
    def rung_view(ent, rung):
        if rung == 'R0':
            return None
        r = ent['rungs'][rung]
        wd = r.get('widget')
        widget = None
        if wd:
            widget = dict(wd)
            if wd['type'] == 'order':
                widget['shuffled'] = sorted(wd['steps'], key=lambda s: _h(wd['prompt'] + s))
                if widget['shuffled'] == list(wd['steps']):
                    widget['shuffled'] = list(reversed(wd['steps']))
                widget['answer_json'] = json.dumps(list(wd['steps']))
            elif wd['type'] == 'sort':
                items = [(b, it) for b, its in wd['buckets'].items() for it in its]
                widget['items'] = sorted(items, key=lambda x: _h(x[1]))
                widget['answer_json'] = json.dumps({it: b for b, it in items})
        lab = r.get('lab')
        lab_info = None
        if lab:
            try:
                from interactive_labs import get_lab
                title = (get_lab(lab['id']) or {}).get('title') or lab['id']
            except Exception:
                title = lab['id']
            lab_info = dict(lab, title=title, url=url_for('interactive_lab', lab_id=lab['id']))
        return {'rung': rung, 'kind': r['kind'], 'title': r.get('title'), 'html': r['html'], 'widget': widget,
                'lab': lab_info, 'label': LS.LABEL[rung]}

    def pick_check(ent, rung, user_id, section_id, label, sid):
        chks = LD.rung_checks(ent, rung)
        if not chks:
            return None
        n = m.LadderEvent.query.filter_by(user_id=user_id, section_id=section_id, label=label, sid=sid, kind='check',
                                          rung=rung).count()
        c = chks[n % len(chks)]
        return {'id': c['id'], 'q': c['q'], 'options': c['options']}

    def section_ctx(user, section, lesson, sec, ent, st, cfg, show_rung=None, feedback=None):
        course, label, sid = ent['course'], label_of(lesson), sec['sid']
        allowed = allowed_for(cfg, label, sid)
        shown = show_rung or (st['resolved'] if st['resolved'] else st['current'])
        if shown != 'R0' and shown not in allowed and shown not in st['tried']:
            shown = 'R0'
        nxt_avail = any(r not in st['tried'] for r in allowed)
        api = lambda ep, **kw: url_for(ep, section_id=section.id, lesson_id=lesson.id, sid=sid, **kw)
        return {
            'sid': sid, 'heading': sec['heading'], 'orig_html': sec['html'], 'shown': shown,
            'view': rung_view(ent, shown), 'state': st, 'allowed': allowed,
            'tried_views': [{'rung': r, 'label': LS.LABEL[r]} for r in ['R0'] + [x for x in LP.RUNGS if x in st['tried']]],
            'next_available': nxt_avail, 'micro_checks': cfg['micro_checks'],
            'check': pick_check(ent, shown, user.id, section.id, label, sid) if cfg['micro_checks'] else None,
            'feedback': feedback, 'review': LS.REVIEW,
            'url_answer': api('ladder_answer'), 'url_another': api('ladder_another'),
            'url_event': api('ladder_event'), 'url_show': lambda r: api('ladder_show', rung=r),
            'lesson_url': url_for('view_lesson', section_id=section.id, module_id=lesson.module_id,
                                  lesson_id=lesson.id) + f'#ladder-{sid}',
            'course': course, 'label': label,
            'steps': [{'rung': r, 'short': STYLE[r], 'state': ('resolved' if st['resolved'] == r else 'current' if r == shown
                                                                else 'tried' if r in st['tried'] else 'todo')}
                      for r in ['R0'] + [x for x in LP.RUNGS if x in allowed or x in st['tried']]],
            'step_no': ([x for x in LP.RUNGS if x in allowed or x in st['tried']].index(shown) + 1) if shown != 'R0' and shown in LP.RUNGS else 0,
            'step_total': len([x for x in LP.RUNGS if x in allowed or x in st['tried']]),
            'style': STYLE.get(shown, ''),
            'next_style': next((STYLE[r] for r in LP.RUNGS if r in allowed and r not in st['tried']), None),
        }

    def clicked(user_id, section_id):
        """'What finally clicked' for one student: struggles (a miss or a request) and the explanation that resolved each."""
        rows = m.LadderState.query.filter_by(user_id=user_id, section_id=section_id).all()
        secs, by = [], {}
        for r in rows:
            tried = _loads(r.tried_json, ['R0'])
            if not ((r.misses or 0) or (r.requests or 0) or len(tried) > 1):
                continue
            head = (LD.ladder().get((r.course, r.label, r.sid)) or {}).get('heading') or r.sid
            if r.resolved:
                by[r.resolved] = by.get(r.resolved, 0) + 1
            secs.append({'label': r.label, 'sid': r.sid, 'heading': head, 'rung': r.resolved, 'misses': r.misses or 0,
                         'exhausted': bool(r.exhausted_at), 'style': STYLE.get(r.resolved or '', ''),
                         'text': (f"Clicked on {r.resolved}: {STYLE[r.resolved]} after {r.misses or 0} miss{'es' if (r.misses or 0) != 1 else ''}"
                                  if r.resolved else 'Every explanation tried, still open' if r.exhausted_at else 'Still working on it')})
        best = max(by, key=lambda k: (by[k], k != 'R0'), default=None)
        return {'struggles': len(secs), 'resolved': sum(by.values()), 'by': by, 'best': best,
                'best_text': (f'Best style: {STYLE[best]} (resolved {by[best]}/{len(secs)} struggles)' if best else None),
                'sections': sorted(secs, key=lambda s: (_lkey(s['label']), s['sid']))}

    def class_clicked(section_id):
        rows = m.LadderState.query.filter(m.LadderState.section_id == section_id, m.LadderState.resolved.isnot(None)).all()
        by = {}
        for r in rows:
            if (r.misses or 0) or (r.requests or 0) or len(_loads(r.tried_json, ['R0'])) > 1:
                by[r.resolved] = by.get(r.resolved, 0) + 1
        tot = sum(by.values())
        return [{'rung': k, 'style': STYLE[k], 'n': by.get(k, 0), 'pct': round(100 * by.get(k, 0) / tot) if tot else 0}
                for k in ['R0'] + list(LP.RUNGS)], tot

    def render_section(c):
        return render_template('ladder/_section.html', L=c)

    def lesson_entries(course, label):
        return {k[2]: v for k, v in LD.ladder().items() if k[0] == course and k[1] == label}

    # ------------------------------------------------------------------ comprehension gate
    def bypassed(user_id, section_id, lesson_id):
        return m.LadderBypass.query.filter(m.LadderBypass.section_id == section_id, m.LadderBypass.user_id == user_id,
                                           db.or_(m.LadderBypass.lesson_id.is_(None), m.LadderBypass.lesson_id == lesson_id)).first() is not None

    def gate(user, section, lesson):
        """Which laddered sections of this lesson the student still has to verify. A section counts as verified when
        its quick check was answered correctly (resolved) or every explanation was tried (exhausted: the student is
        never trapped, and the instructor sees them in Who needs me)."""
        out = {'on': False, 'total': 0, 'done': 0, 'pending': [], 'first': None, 'exempt': False, 'blocked': False}
        if not section or getattr(user, 'role', None) != 'student':
            return out
        cfg = settings(section.id)
        if not (cfg['enabled'] and cfg['micro_checks'] and cfg['require_check']):
            return out
        course, label = course_code(section), label_of(lesson)
        if not lesson_entries(course, label):
            return out
        rows = {r.sid: r for r in m.LadderState.query.filter_by(user_id=user.id, section_id=section.id, course=course,
                                                                 label=label).all()}
        for sec in LSEC.sections(LSEC.student_html(lesson.content or '')):
            ent = LD.entry(course, label, sec['sid'])
            if not ent or cfg['overrides'].get(f'{label}|{sec["sid"]}', {}).get('off'):
                continue
            r = rows.get(sec['sid'])
            out['total'] += 1
            if r and (r.resolved or r.exhausted_at):
                out['done'] += 1
            else:
                out['pending'].append({'sid': sec['sid'], 'heading': (LD.ladder().get((course, label, sec['sid'])) or {}).get('heading') or sec['sid']})
        out['on'] = out['total'] > 0
        out['first'] = out['pending'][0]['sid'] if out['pending'] else None
        out['exempt'] = out['on'] and bypassed(user.id, section.id, lesson.id)
        out['blocked'] = out['on'] and bool(out['pending']) and not out['exempt']
        return out

    def module_gate(user, section, module_id):
        """Strict quiz lock: first lesson in the chapter that still blocks (None = free to take the quiz)."""
        if not section or getattr(user, 'role', None) != 'student' or not settings(section.id)['gate_quiz']:
            return None
        for les in d.Lesson.query.filter_by(module_id=module_id).order_by(d.Lesson.order).all():
            g = gate(user, section, les)
            if g['blocked']:
                return les, g
        return None

    def render_lesson(user, section, module, lesson, html_filter=None):
        """Lesson HTML with every laddered section wrapped for this student, or None (ladder off / no content)."""
        if not section or user.role != 'student':
            return None
        cfg = settings(section.id)
        if not cfg['enabled']:
            return None
        course, label = course_code(section), label_of(lesson)
        raw = lesson_entries(course, label)
        if not raw:
            return None
        src = LSEC.student_html(lesson.content or '')
        secs = LSEC.sections(src)
        rows = {r.sid: r for r in m.LadderState.query.filter_by(user_id=user.id, section_id=section.id, course=course,
                                                                 label=label).all()}
        prof = None
        out, pos, n = [], 0, 0
        deep_sid, deep_rung = request.args.get('sid'), request.args.get('rung')
        if deep_sid and deep_rung in LP.RUNGS and deep_sid in raw and deep_rung in allowed_for(cfg, label, deep_sid):
            # lab re-teach link: open that section straight on the recommended explanation (counts as a request)
            if prof is None:
                prof = profile_of(user.id)
            row = ensure_row(user, section, course, label, deep_sid, lesson.id, cfg, prof)
            st0 = as_state(row)
            if not st0['resolved'] and deep_rung not in st0['tried']:
                st0['tried'].append(deep_rung)
                st0['current'] = deep_rung
                save_state(row, st0)
                log(user.id, section.id, course, label, deep_sid, 'request', from_rung=st0['tried'][-2], rung=deep_rung)
            db.session.commit()
            rows[deep_sid] = row
        g = gate(user, section, lesson)
        lock_after = g['first'] if g['blocked'] else None
        locked = False
        for sec in secs:
            ent = LD.entry(course, label, sec['sid'])
            if not ent or not allowed_for(cfg, label, sec['sid']) and not cfg['micro_checks']:
                continue
            if cfg['overrides'].get(f'{label}|{sec["sid"]}', {}).get('off'):
                continue
            if sec['sid'] in rows:
                st = as_state(rows[sec['sid']])
            else:
                if prof is None:
                    prof = profile_of(user.id)
                st = LP.start(allowed_for(cfg, label, sec['sid']), prof['best'], cfg['adapt_first'])
            want = request.args.get('ladder_original') == sec['sid']
            deep = deep_rung if deep_sid == sec['sid'] and deep_rung in (st['tried'] or []) else None
            c = section_ctx(user, section, lesson, sec, ent, st, cfg, show_rung='R0' if want else deep)
            out.append(src[pos:sec['start']])
            out.append(f'<span class="ladder-anchor" id="ladder-sec-{sec["sid"]}"></span>')
            if locked:
                out.append(f'<div class="ladder-lock" data-lock-sid="{sec["sid"]}" role="note"><i class="bi bi-lock" aria-hidden="true"></i> '
                           'Complete the quick check above to unlock this section.</div>')
            out.append(render_section(c))
            if lock_after and sec['sid'] == lock_after:
                locked = True
            pos = sec['end']
            n += 1
        if not n:
            return None
        out.append(src[pos:])
        return ''.join(out)

    # ------------------------------------------------------------------ student routes
    def _target(section_id, lesson_id, sid):
        section = ctx.enrolled_section(section_id)
        lesson = db.get_or_404(d.Lesson, lesson_id)
        if not d.is_content_available(section_id, 'module', lesson.module_id, current_user.id):
            abort(403)
        cfg = settings(section.id)
        if not cfg['enabled']:
            abort(404)
        course, label = course_code(section), label_of(lesson)
        sec = next((s for s in LSEC.sections(lesson.content or '') if s['sid'] == sid), None)
        ent = LD.entry(course, label, sid) if sec else None
        if not ent or cfg['overrides'].get(f'{label}|{sid}', {}).get('off'):
            abort(404)
        return section, lesson, cfg, course, label, sec, ent

    def wants_json():
        return request.headers.get('X-Requested-With') == 'fetch' or request.accept_mimetypes.best == 'application/json'

    def reply(section, lesson, sec, ent, st, cfg, feedback, event, show_rung=None):
        db.session.commit()
        c = section_ctx(current_user, section, lesson, sec, ent, st, cfg, show_rung=show_rung, feedback=feedback)
        if wants_json():
            return jsonify({'html': render_section(c), 'shown': c['shown'], 'event': event,
                            'label': LS.LABEL[c['shown']], 'feedback': feedback})
        if feedback:
            flash(feedback['text'], 'success' if feedback.get('ok') else 'info')
        return redirect(c['lesson_url'], code=303)

    @login_required
    def ladder_answer(section_id, lesson_id, sid):
        section, lesson, cfg, course, label, sec, ent = _target(section_id, lesson_id, sid)
        if not cfg['micro_checks']:
            abort(404)
        prof = profile_of(current_user.id)
        row = ensure_row(current_user, section, course, label, sid, lesson.id, cfg, prof)
        st = as_state(row)
        check_id, answer = request.form.get('check_id', ''), request.form.get('answer', '')
        rung = next((r for r in ('R0',) + LP.RUNGS if check_id.startswith(f'L-{course}-{label}-{sid}-{r}-')), None)
        chk = next((c for c in (LD.rung_checks(ent, rung) if rung else []) if c['id'] == check_id), None)
        if not chk or answer not in chk['options']:
            if wants_json():
                return jsonify({'error': 'Choose one of the answers first.'}), 400
            flash('Choose one of the answers first.', 'warning')
            return redirect(url_for('view_lesson', section_id=section.id, module_id=lesson.module_id,
                                    lesson_id=lesson.id) + f'#ladder-{sid}', code=303)
        if rung != 'R0' and rung not in st['tried']:
            abort(400)
        st = dict(st, current=rung)
        ok = answer == chk['correct']
        mc = None if ok else (chk['mc'] or {}).get(answer)
        log(current_user.id, section.id, course, label, sid, 'check', rung=rung, check_id=check_id, answer=answer[:400],
            correct=ok, mc=mc)
        seq = LP.order(allowed_for(cfg, label, sid), prof['best'])
        st, nxt, event = LP.after_answer(st, ok, seq)
        if event == 'resolved':
            log(current_user.id, section.id, course, label, sid, 'resolved', rung=rung)
            fb = {'ok': True, 'text': 'Right. ' + chk['why']}
        else:
            mct = LD.misconceptions().get(mc) or _global_mc(mc)
            hint = f' That answer usually means this mix-up: {mct["label"]}.' if mct else ''
            if nxt:
                fb = {'ok': False, 'text': f'Not quite.{hint} Here is the same idea {HOW[nxt]}, with a fresh question '
                                           'at the end.'}
            else:
                fb = {'ok': False, 'text': f'Not quite.{hint} You have now seen every explanation of this section. '
                                           'Your instructor can see that this one needs a conversation; that is useful '
                                           'to them and is not a mark against you.'}
            if event == 'exhausted':
                log(current_user.id, section.id, course, label, sid, 'exhausted', rung=rung)
        save_state(row, st)
        return reply(section, lesson, sec, ent, st, cfg, fb, event, show_rung=st['current'])

    def _global_mc(mc):
        if not mc:
            return None
        try:
            from curriculum_v2 import misconceptions as MCS
            return MCS.MISCONCEPTIONS.get(mc)
        except Exception:
            return None

    @login_required
    def ladder_another(section_id, lesson_id, sid):
        section, lesson, cfg, course, label, sec, ent = _target(section_id, lesson_id, sid)
        source = request.form.get('source', 'button')
        source = source if source in SOURCES else 'button'
        if source == 'helix' and ctx.eng.helix_state(section, current_user) != 'ok':
            source = 'button'
        prof = profile_of(current_user.id)
        row = ensure_row(current_user, section, course, label, sid, lesson.id, cfg, prof)
        st = as_state(row)
        seq = LP.order(allowed_for(cfg, label, sid), prof['best'])
        was = st['current']
        st, nxt, event = LP.after_request(st, seq)
        log(current_user.id, section.id, course, label, sid, 'request', rung=nxt, source=source, from_rung=was)
        if event == 'exhausted':
            log(current_user.id, section.id, course, label, sid, 'exhausted', rung=st['current'])
        save_state(row, st)
        fb = None if nxt else {'ok': False, 'text': 'That was the last explanation we have for this section. Your '
                                                    'instructor can see it needs a conversation. You can still look '
                                                    'back at any of them.'}
        return reply(section, lesson, sec, ent, st, cfg, fb, event, show_rung=st['current'])

    @login_required
    def ladder_show(section_id, lesson_id, sid, rung):
        section, lesson, cfg, course, label, sec, ent = _target(section_id, lesson_id, sid)
        if rung not in ('R0',) + LP.RUNGS:
            abort(404)
        row = state_row(current_user.id, section.id, course, label, sid)
        st = as_state(row) if row else LP.new_state()
        if rung != 'R0' and rung not in st['tried']:
            abort(404)
        log(current_user.id, section.id, course, label, sid, 'see_original' if rung == 'R0' else 'show', rung=rung)
        if row:
            row.current = rung if not st['resolved'] else row.current
        return reply(section, lesson, sec, ent, st, cfg, None, 'show', show_rung=rung)

    @login_required
    def ladder_event(section_id, lesson_id, sid):
        """Light-weight logging from the page: see_original toggles and Helix offers shown (consent re-checked)."""
        section, lesson, cfg, course, label, sec, ent = _target(section_id, lesson_id, sid)
        kind = request.form.get('kind') or (request.get_json(silent=True) or {}).get('kind')
        if kind == 'helix_offer':
            if ctx.eng.helix_state(section, current_user) != 'ok':
                return jsonify({'ok': False, 'reason': 'no_consent'}), 403
            log(current_user.id, section.id, course, label, sid, 'helix_offer', source='helix')
        elif kind == 'see_original':
            log(current_user.id, section.id, course, label, sid, 'see_original', rung='R0')
        else:
            abort(400)
        db.session.commit()
        return jsonify({'ok': True})

    # ------------------------------------------------------------------ profile pages
    def profile_rows(user_id, section_id=None):
        q = m.LadderState.query.filter_by(user_id=user_id)
        if section_id:
            q = q.filter_by(section_id=section_id)
        out = []
        for r in q.order_by(m.LadderState.updated_at.desc()).all():
            raw = LD.ladder().get((r.course, r.label, r.sid)) or {}
            st = as_state(r)
            out.append({'row': r, 'heading': raw.get('heading') or r.sid, 'state': st,
                        'tried': [LS.LABEL[x] for x in st['tried']],
                        'resolved_label': LS.LABEL.get(r.resolved) if r.resolved else None})
        return out

    @login_required
    def ladder_profile(section_id):
        section = ctx.enrolled_section(section_id)
        if request.method == 'POST':
            db.session.add(m.LadderProfileReset(user_id=current_user.id))
            log(current_user.id, section.id, None, None, None, 'reset')
            db.session.commit()
            flash('Reset. From now on the course starts learning what helps you from scratch. The sections you '
                  'already worked through keep the explanation that helped.', 'success')
            return redirect(url_for('ladder_profile', section_id=section.id), code=303)
        return render_template('ladder/profile.html', section=section, prof=profile_of(current_user.id),
                               rows=profile_rows(current_user.id, section.id), kind_label=LP.KIND_LABEL, P=LP,
                               cfg=settings(section.id), staff=False, student=current_user)

    @login_required
    def ladder_student(section_id, user_id):
        section = ctx.staff_section(section_id)
        if not d.Enrollment.query.filter_by(user_id=user_id, section_id=section.id).first():
            abort(404)
        student = db.get_or_404(d.User, user_id)
        return render_template('ladder/profile.html', section=section, prof=profile_of(user_id),
                               rows=profile_rows(user_id, section.id), kind_label=LP.KIND_LABEL, P=LP,
                               cfg=settings(section.id), staff=True, student=student)

    # ------------------------------------------------------------------ instructor
    def scope_sections(section):
        """Every section teaching the same course that the current user may see (admin: the whole tenant)."""
        out = []
        for s in d.ClassSection.query.filter_by(course_id=section.course_id).order_by(d.ClassSection.id).all():
            if s.id == section.id:
                out.append(s)
            elif current_user.role == 'admin':
                if getattr(s, 'institution_id', None) == getattr(section, 'institution_id', None):
                    out.append(s)
            elif d.can_access_section(current_user, s):
                out.append(s)
        return out

    def analytics(section, ids=None):
        course = course_code(section)
        ids = list(ids or [section.id])
        states = m.LadderState.query.filter(m.LadderState.section_id.in_(ids), m.LadderState.course == course).all()
        evs = m.LadderEvent.query.filter(m.LadderEvent.section_id.in_(ids), m.LadderEvent.course == course).all()
        users = {u.id: u for u in d.User.query.filter(d.User.id.in_({s.user_id for s in states} or {0})).all()}
        per = defaultdict(lambda: {'students': set(), 'escalated': set(), 'exhausted': set(), 'requests': 0,
                                   'misses': 0, 'resolved': defaultdict(int), 'mcs': defaultdict(int)})
        reach = defaultdict(lambda: [0, 0])          # rung -> [students who saw it, resolved there]
        for s in states:
            k = (s.label, s.sid)
            p = per[k]
            st = as_state(s)
            p['students'].add(s.user_id)
            if len([r for r in st['tried'] if r != 'R0']) > (1 if s.adapted else 0):
                p['escalated'].add(s.user_id)
            if s.exhausted_at:
                p['exhausted'].add(s.user_id)
            if s.resolved:
                p['resolved'][s.resolved] += 1
            for r in st['tried']:
                reach[r][0] += 1
            if s.resolved:
                reach[s.resolved][1] += 1
        first_r0 = {}
        for e in sorted(evs, key=lambda e: (e.created_at, e.id)):
            if e.kind == 'check' and e.rung == 'R0' and (e.label, e.sid, e.user_id) not in first_r0:
                first_r0[(e.label, e.sid, e.user_id)] = bool(e.correct)
        r0 = defaultdict(lambda: [0, 0])               # (label, sid) -> [first answers on the original, misses]
        for (label, sid, _u), ok in first_r0.items():
            r0[(label, sid)][0] += 1
            r0[(label, sid)][1] += 0 if ok else 1
        for e in evs:
            p = per[(e.label, e.sid)]
            if e.kind == 'request':
                p['requests'] += 1
            elif e.kind == 'check' and e.correct is False:
                p['misses'] += 1
                if e.mc:
                    p['mcs'][e.mc] += 1
        rows = []
        for (label, sid), p in per.items():
            raw = LD.ladder().get((course, label, sid)) or {}
            n = len(p['students'])
            mcs = LD.misconceptions()
            top_mc = sorted(p['mcs'].items(), key=lambda x: (-x[1], x[0]))[:2]
            n0, miss0 = r0[(label, sid)]
            rows.append({'label': label, 'sid': sid, 'heading': raw.get('heading') or sid, 'students': n,
                         'chapter': _lkey(label)[0], 'r0_answers': n0, 'r0_miss_rate': round(100 * miss0 / n0) if n0 else None,
                         'rewrite': n0 >= REWRITE_MIN and miss0 / n0 >= REWRITE_SHARE,
                         'escalated': len(p['escalated']), 'exhausted': len(p['exhausted']), 'requests': p['requests'],
                         'misses': p['misses'], 'resolved': dict(p['resolved']),
                         'escalation_rate': round(100 * len(p['escalated']) / n) if n else 0,
                         'top_mc': [((mcs.get(k) or _global_mc(k) or {}).get('label', k), v) for k, v in top_mc]})
        rows.sort(key=lambda r: (-r['escalated'], -r['exhausted'], -r['escalation_rate'], _lkey(r['label']), r['sid']))
        rungs = [{'rung': r, 'label': LS.LABEL[r], 'reached': reach[r][0], 'resolved': reach[r][1],
                  'rate': round(100 * reach[r][1] / reach[r][0]) if reach[r][0] else None} for r in ('R0',) + LP.RUNGS]
        demo = any(is_demo_user(u) for u in users.values())
        return {'rows': rows, 'rungs': rungs, 'students': len({s.user_id for s in states}), 'demo': demo,
                'course': course}

    def course_sections(section):
        """[(label, sid, heading, status)] for the class's course: every ladder entry, for the override list."""
        course = course_code(section)
        out = []
        for (c, label, sid), e in sorted(LD.ladder().items(), key=lambda kv: (_lkey(kv[0][1]), kv[0][2])):
            if c == course and e.get('type') in ('section', 'same_as'):
                out.append({'label': label, 'sid': sid, 'heading': e.get('heading') or sid, 'type': e['type']})
        return out

    def review_queue(section):
        """Per lesson of the class's course: laddered / same_as / skip counts and rung + check totals (SME review)."""
        course = course_code(section)
        by = defaultdict(lambda: {'section': 0, 'same_as': 0, 'skip': 0, 'checks': 0})
        for (c, label, _sid), e in LD.ladder().items():
            if c != course:
                continue
            b = by[label]
            b[e.get('type', 'skip')] = b.get(e.get('type', 'skip'), 0) + 1
            if e.get('type') == 'section':
                b['checks'] += len(e['checks']) + sum(len(r['checks']) for r in e['rungs'].values())
        return [dict(v, label=k, rungs=4 * v['section']) for k, v in sorted(by.items(), key=lambda kv: _lkey(kv[0]))]

    @login_required
    def ladder_class(section_id):
        section = ctx.staff_section(section_id)
        cfg = settings(section.id)
        scope = 'course' if request.args.get('scope') == 'course' else 'section'
        peers = scope_sections(section)
        a = analytics(section, [s.id for s in peers] if scope == 'course' else None)
        a_here = a if scope == 'section' else analytics(section)
        a['scope'] = scope
        a['scope_info'] = {'here_students': a_here['students'], 'n_sections': len(peers),
                           'course_name': getattr(getattr(section, 'course', None), 'title', None) or a['course']}
        if scope == 'course':
            a['scope_info']['course_students'] = a['students']
        chapters = sorted({r['chapter'] for r in a['rows']})
        ch = request.args.get('chapter', type=int)
        rows = [r for r in a['rows'] if not ch or r['chapter'] == ch]
        if request.args.get('format') == 'csv':
            import csv
            from io import StringIO
            buf = StringIO()
            w = csv.writer(buf)
            if scope == 'course':
                w.writerow([f'scope: all {len(peers)} {a["course"]} sections (curriculum average)'])
            w.writerow(['lesson', 'section', 'students', 'needed another way', 'rate %', 'saw every explanation',
                        'first answers on original', 'original miss %', 'original may need rewriting', 'requests',
                        'resolved by', 'top mix-ups', 'includes demo accounts'])
            for r in rows:
                w.writerow([r['label'], r['heading'], r['students'], r['escalated'], r['escalation_rate'], r['exhausted'],
                            r['r0_answers'], r['r0_miss_rate'] if r['r0_miss_rate'] is not None else '',
                            'yes' if r['rewrite'] else '', r['requests'],
                            '; '.join(f'{LS.LABEL[k]}: {v}' for k, v in sorted(r['resolved'].items())),
                            '; '.join(f'{lbl} ({n})' for lbl, n in r['top_mc']), 'yes' if a['demo'] else 'no'])
            from flask import Response
            return Response(buf.getvalue(), mimetype='text/csv', headers={
                'Content-Disposition': f'attachment; filename=explanations-{"course" if scope == "course" else "section"}-{section.id}.csv'})
        return render_template('ladder/instructor.html', section=section, cfg=cfg, a=a, rows=rows, chapters=chapters,
                               chapter=ch, secs=course_sections(section), queue=review_queue(section),
                               P=LP, LABEL=LS.LABEL, demo=a['demo'], REWRITE_MIN=REWRITE_MIN,
                               REWRITE_SHARE=REWRITE_SHARE, **_bypass_ctx(section))

    @login_required
    def ladder_settings(section_id):
        section = ctx.staff_section(section_id)
        s = m.LadderSetting.query.filter_by(section_id=section.id).first()
        if not s:
            s = m.LadderSetting(section_id=section.id, overrides_json='{}')
            db.session.add(s)
        f = request.form
        if f.get('form') == 'bypass':
            uid, lid = f.get('user_id', type=int), f.get('lesson_id', type=int)
            if not uid or not d.Enrollment.query.filter_by(user_id=uid, section_id=section.id).first():
                abort(400)
            q = m.LadderBypass.query.filter_by(section_id=section.id, user_id=uid, lesson_id=lid)
            if f.get('action') == 'remove':
                q.delete()
                msg = 'Exemption removed: the comprehension gate applies to this student again.'
            else:
                if not q.first():
                    db.session.add(m.LadderBypass(section_id=section.id, user_id=uid, lesson_id=lid, created_by=current_user.id))
                msg = 'Exemption saved: this student can move on without the section checks.'
        elif f.get('form') == 'override':
            ov = _loads(s.overrides_json, {})
            key = f'{f.get("label", "")}|{f.get("sid", "")}'
            if (f.get('label'), f.get('sid')) not in {(x['label'], x['sid']) for x in course_sections(section)}:
                abort(400)
            val = f.get('value', '')
            if val == 'off':
                ov[key] = {'off': True}
            elif val in ('1', '2', '3'):
                ov[key] = {'max': int(val)}
            else:
                ov.pop(key, None)
            s.overrides_json = json.dumps(ov, sort_keys=True)
            msg = 'Section override saved.'
        else:
            s.enabled = f.get('enabled') == 'on'
            s.micro_checks = f.get('micro_checks') == 'on'
            s.adapt_first = f.get('adapt_first') == 'on'
            if 'gate_form' in f:      # the comprehension-gate switches are on the same card
                s.require_check_to_advance = f.get('require_check_to_advance') == 'on'
                s.gate_quiz_on_ladder = f.get('gate_quiz_on_ladder') == 'on'
            mr = f.get('max_rung', type=int)
            s.max_rung = mr if mr in (1, 2, 3, 4) else 4
            msg = 'Explanation ladder settings saved. Grades are never affected by these settings.'
        s.updated_at, s.updated_by = utcnow(), current_user.id
        try:
            d.audit('ladder_settings', f'section {section.id}: {f.get("form") or "class"}')
        except Exception:
            pass
        db.session.commit()
        flash(msg, 'success')
        return redirect(url_for('ladder_class', section_id=section.id), code=303)

    @login_required
    def ladder_preview(section_id, label):
        """Staff: every rung and check (keys shown) for one lesson, for SME review."""
        section = ctx.staff_section(section_id)
        course = course_code(section)
        ents = []
        for (c, lab, sid), e in LD.ladder().items():
            if c == course and lab == label:
                ents.append((sid, e))
        if not ents:
            abort(404)
        lesson = None
        for les in d.Lesson.query.join(d.Module, d.Module.id == d.Lesson.module_id).filter(
                d.Module.course_id == section.course_id).all():
            if label_of(les) == label:
                lesson = les
                break
        order = {s['sid']: i for i, s in enumerate(LSEC.sections(lesson.content or ''))} if lesson else {}
        ents.sort(key=lambda x: order.get(x[0], 999))
        view = []
        for sid, e in ents:
            if e['type'] != 'section':
                view.append({'sid': sid, 'e': e})
                continue
            view.append({'sid': sid, 'e': e, 'checks': {r: LD.rung_checks(dict(e), r) for r in ('R0',) + LP.RUNGS},
                         'rungs': [rung_view(e, r) for r in LP.RUNGS]})
        return render_template('ladder/preview.html', section=section, label=label, lesson=lesson, view=view,
                               LABEL=LS.LABEL)

    # ------------------------------------------------------------------ hooks for other features
    def needs_me_reasons(user, section):
        """Who needs me: one reason per section where this student has seen every explanation and still missed."""
        out = []
        rows = (m.LadderState.query.filter_by(user_id=user.id, section_id=section.id)
                .filter(m.LadderState.exhausted_at.isnot(None)).order_by(m.LadderState.exhausted_at.desc()).all())
        for r in rows[:3]:
            raw = LD.ladder().get((r.course, r.label, r.sid)) or {}
            ent = LD.entry(r.course, r.label, r.sid) or {}
            st = as_state(r)
            kinds = ', '.join(LS.LABEL[x].replace('Explained another way: ', '').replace('Explained ', '').lower()
                              for x in st['tried'])
            last = (m.LadderEvent.query.filter_by(user_id=user.id, section_id=section.id, label=r.label, sid=r.sid,
                                                  kind='check', correct=False)
                    .order_by(m.LadderEvent.created_at.desc()).first())
            mct = (LD.misconceptions().get(last.mc) or _global_mc(last.mc)) if last and last.mc else None
            heading = raw.get('heading') or r.sid
            text = (f'Saw every explanation of “{heading}” (lesson {r.label}: {kinds}) and still missed the check '
                    f'({st["misses"]} misses, {st["requests"]} “explain another way”).')
            note = (f'One-on-one idea: ask them to talk you through “{heading}” in their own words'
                    + (f'; their last wrong answer points to “{mct["label"]}”' if mct else '') + '.')
            subject = f'Let us go through “{heading}” together'
            body = (f'Hi {user.first_name or ""},\n\nI can see you worked through every explanation of “{heading}” in lesson '
                    f'{r.label}. That is useful to me, not a mark against you. Could we spend ten minutes on it '
                    'together? Reply with a time that suits you, or bring it to the next class.\n')
            out.append({'kind': 'ladder', 'obj': ent.get('obj'), 'when': r.exhausted_at, 'text': text + ' ' + note,
                        'ladder': {'label': r.label, 'sid': r.sid, 'heading': heading, 'tried': st['tried'],
                                   'message_url': url_for('messages_new', to=user.id, subject=subject, body=body),
                                   'detail_url': url_for('ladder_student', section_id=section.id, user_id=user.id),
                                   'preview_url': url_for('ladder_preview', section_id=section.id, label=r.label) + f'#pv-{r.sid}'}})
        return out

    def class_exhausted(section):
        """[(label, sid, heading, [users])] sections where 2+ students ran out of explanations (briefing)."""
        rows = (m.LadderState.query.filter_by(section_id=section.id).filter(m.LadderState.exhausted_at.isnot(None)).all())
        by = defaultdict(list)
        for r in rows:
            by[(r.course, r.label, r.sid)].append(r.user_id)
        out = []
        for (c, label, sid), uids in by.items():
            raw = LD.ladder().get((c, label, sid)) or {}
            out.append({'label': label, 'sid': sid, 'heading': raw.get('heading') or sid, 'users': sorted(uids)})
        out.sort(key=lambda x: (-len(x['users']), x['label'], x['sid']))
        return out

    def for_objectives(user, section, objs=None, labels=None):
        """Mastery review / chapter check: per objective, the explanation that worked for this student (rung html)
        and the sections they never resolved, re-taught with the next rung they have not seen (or R1)."""
        course = course_code(section)
        cfg = settings(section.id)
        if not cfg['enabled'] or user.role != 'student':
            return {}
        rows = {(r.label, r.sid): r for r in m.LadderState.query.filter_by(user_id=user.id, section_id=section.id,
                                                                            course=course).all()}
        out = {}
        for (label, sid), r in sorted(rows.items(), key=lambda kv: (_lkey(kv[0][0]), kv[0][1])):
            ent = LD.entry(course, label, sid)
            if not ent or (objs is not None and ent['obj'] not in objs) or (labels is not None and label not in labels):
                continue
            st = as_state(r)
            bucket = out.setdefault(ent['obj'], {'worked': [], 'open': []})
            heading = (LD.ladder().get((course, label, sid)) or {}).get('heading') or sid
            if st['resolved'] and st['resolved'] != 'R0':
                bucket['worked'].append({'label': label, 'heading': heading, 'view': rung_view(ent, st['resolved'])})
            elif not st['resolved']:
                allowed = allowed_for(cfg, label, sid) or ['R1']
                nxt = next((x for x in allowed if x not in st['tried']), None)
                rung = nxt or (st['tried'][-1] if st['tried'][-1] != 'R0' else allowed[0])
                bucket['open'].append({'label': label, 'heading': heading, 'view': rung_view(ent, rung),
                                       'exhausted': st['exhausted']})
        return out

    def _bypass_ctx(section):
        studs = (d.User.query.join(d.Enrollment, d.Enrollment.user_id == d.User.id)
                 .filter(d.Enrollment.section_id == section.id, d.User.role == 'student').order_by(d.User.email).all())
        names = {u.id: u.full_name or u.email for u in studs}
        lessons = (d.Lesson.query.join(d.Module, d.Module.id == d.Lesson.module_id)
                   .filter(d.Module.course_id == section.course_id).order_by(d.Module.order, d.Lesson.order).all())
        ltitle = {l.id: l.title for l in lessons}
        byp = [{'user_id': b.user_id, 'lesson_id': b.lesson_id, 'who': names.get(b.user_id, '?'),
                'lesson': ltitle.get(b.lesson_id, 'All lessons') if b.lesson_id else 'All lessons'}
               for b in m.LadderBypass.query.filter_by(section_id=section.id).all()]
        return {'gate_students': studs, 'gate_lessons': lessons, 'bypasses': byp}

    @login_required
    def lesson_shortcut(section_id, lesson_id):
        """Short deep link (lab re-teach buttons): /student/section/<s>/lesson/<l>?rung=R2&sid=<slug>#ladder-sec-<slug>."""
        lesson = db.get_or_404(d.Lesson, lesson_id)
        q = {k: v for k, v in request.args.items() if k in ('rung', 'sid')}
        return redirect(url_for('view_lesson', section_id=section_id, module_id=lesson.module_id, lesson_id=lesson.id, **q))

    def _gate_target(section_id, lesson_id):
        section = ctx.enrolled_section(section_id)
        lesson = db.get_or_404(d.Lesson, lesson_id)
        if not d.is_content_available(section_id, 'module', lesson.module_id, current_user.id):
            abort(403)
        return section, lesson

    @login_required
    def ladder_gate(section_id, lesson_id):
        """Live gate status for the lesson page (progress banner + section locks)."""
        section, lesson = _gate_target(section_id, lesson_id)
        g = gate(current_user, section, lesson)
        return jsonify({k: g[k] for k in ('on', 'total', 'done', 'pending', 'first', 'exempt', 'blocked')})

    @login_required
    def lesson_advance(section_id, lesson_id):
        """Bottom-of-lesson button. Server-side comprehension gate: a student moves on only when every laddered section
        is verified (resolved or exhausted), unless the instructor turned the gate off or exempted them."""
        lesson = db.get_or_404(d.Lesson, lesson_id)
        here = url_for('view_lesson', section_id=section_id, module_id=lesson.module_id, lesson_id=lesson.id)
        to = request.args.get('to', 'next')
        if to == 'quiz':
            target = url_for('take_quiz', section_id=section_id, quiz_id=request.args.get('quiz_id', type=int) or abort(400))
        elif to == 'lab':
            target = here + '#chapter-lab'
        elif to == 'module':
            target = url_for('view_module', section_id=section_id, module_id=lesson.module_id)
        else:
            nxt = d.Lesson.query.filter_by(id=request.args.get('next_id', type=int), module_id=lesson.module_id).first_or_404()
            target = url_for('view_lesson', section_id=section_id, module_id=lesson.module_id, lesson_id=nxt.id)
        if current_user.role != 'student':
            return redirect(target)
        section, lesson = _gate_target(section_id, lesson_id)
        g = gate(current_user, section, lesson)
        if g['blocked']:
            left = len(g['pending'])
            flash(f'Almost there: {left} section{"s" if left != 1 else ""} in this lesson still need{"s" if left == 1 else ""} '
                  f'its quick check. Start with “{g["pending"][0]["heading"]}”. If a section does not click, press '
                  '“I don\'t get it” for another explanation.', 'info')
            return redirect(here + f'#ladder-sec-{g["first"]}', code=303)
        return redirect(target, code=303)

    for rule, ep, fn, methods in [
        ('/student/section/<int:section_id>/ladder/<int:lesson_id>/gate', 'ladder_gate', ladder_gate, ['GET']),
        ('/student/section/<int:section_id>/lesson/<int:lesson_id>', 'lesson_shortcut', lesson_shortcut, ['GET']),
        ('/student/section/<int:section_id>/lesson/<int:lesson_id>/advance', 'lesson_advance', lesson_advance, ['GET']),
        ('/student/section/<int:section_id>/ladder/<int:lesson_id>/<sid>/answer', 'ladder_answer', ladder_answer, ['POST']),
        ('/student/section/<int:section_id>/ladder/<int:lesson_id>/<sid>/another', 'ladder_another', ladder_another, ['POST']),
        ('/student/section/<int:section_id>/ladder/<int:lesson_id>/<sid>/show/<rung>', 'ladder_show', ladder_show, ['POST']),
        ('/student/section/<int:section_id>/ladder/<int:lesson_id>/<sid>/event', 'ladder_event', ladder_event, ['POST']),
        ('/student/section/<int:section_id>/what-helps-you-learn', 'ladder_profile', ladder_profile, ['GET', 'POST']),
        ('/instructor/section/<int:section_id>/ladder', 'ladder_class', ladder_class, ['GET']),
        ('/instructor/section/<int:section_id>/ladder/settings', 'ladder_settings', ladder_settings, ['POST']),
        ('/instructor/section/<int:section_id>/ladder/student/<int:user_id>', 'ladder_student', ladder_student, ['GET']),
        ('/instructor/section/<int:section_id>/ladder/preview/<label>', 'ladder_preview', ladder_preview, ['GET']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)

    from types import SimpleNamespace
    return SimpleNamespace(models=m, settings=settings, render_lesson=render_lesson, profile=profile_of,
                           gate=gate, module_gate=module_gate, bypassed=bypassed, clicked=clicked,
                           class_clicked=class_clicked, STYLE=STYLE,
                           needs_me_reasons=needs_me_reasons, class_exhausted=class_exhausted,
                           for_objectives=for_objectives, analytics=analytics)


def _lkey(label):
    try:
        a, b = label.split('.')
        return (int(a), int(b))
    except (ValueError, AttributeError):
        return (999, 999)
