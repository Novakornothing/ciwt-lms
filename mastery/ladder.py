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
HOW = {'R1': 'said more simply', 'R2': 'as an analogy', 'R3': 'as a picture or step by step', 'R4': 'as something to try'}


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

    class LadderProfileReset(db.Model):
        """The student reset "What helps you learn": evidence before reset_at is ignored."""
        __tablename__ = 'ladder_profile_reset'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        reset_at = db.Column(db.DateTime, default=utcnow)

    from types import SimpleNamespace
    _cache['m'] = SimpleNamespace(LadderSetting=LadderSetting, LadderState=LadderState, LadderEvent=LadderEvent,
                                  LadderProfileReset=LadderProfileReset)
    return _cache['m']


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
                    'overrides': {}, 'row': None}
        return {'enabled': bool(s.enabled), 'max_rung': int(s.max_rung or 0), 'micro_checks': bool(s.micro_checks),
                'adapt_first': bool(s.adapt_first), 'overrides': _loads(s.overrides_json, {}), 'row': s}

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
        }

    def render_section(c):
        return render_template('ladder/_section.html', L=c)

    def lesson_entries(course, label):
        return {k[2]: v for k, v in LD.ladder().items() if k[0] == course and k[1] == label}

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
            c = section_ctx(user, section, lesson, sec, ent, st, cfg, show_rung='R0' if want else None)
            out.append(src[pos:sec['start']])
            out.append(render_section(c))
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
    def analytics(section):
        course = course_code(section)
        states = m.LadderState.query.filter_by(section_id=section.id, course=course).all()
        evs = m.LadderEvent.query.filter_by(section_id=section.id, course=course).all()
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
            rows.append({'label': label, 'sid': sid, 'heading': raw.get('heading') or sid, 'students': n,
                         'escalated': len(p['escalated']), 'exhausted': len(p['exhausted']), 'requests': p['requests'],
                         'misses': p['misses'], 'resolved': dict(p['resolved']),
                         'escalation_rate': round(100 * len(p['escalated']) / n) if n else 0,
                         'top_mc': [((mcs.get(k) or _global_mc(k) or {}).get('label', k), v) for k, v in top_mc]})
        rows.sort(key=lambda r: (-r['escalated'], -r['exhausted'], -r['escalation_rate'], r['label'], r['sid']))
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

    @login_required
    def ladder_class(section_id):
        section = ctx.staff_section(section_id)
        cfg = settings(section.id)
        a = analytics(section)
        secs = course_sections(section)
        return render_template('ladder/instructor.html', section=section, cfg=cfg, a=a, secs=secs,
                               P=LP, LABEL=LS.LABEL, demo=a['demo'])

    @login_required
    def ladder_settings(section_id):
        section = ctx.staff_section(section_id)
        s = m.LadderSetting.query.filter_by(section_id=section.id).first()
        if not s:
            s = m.LadderSetting(section_id=section.id, overrides_json='{}')
            db.session.add(s)
        f = request.form
        if f.get('form') == 'override':
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
            out.append({'kind': 'ladder', 'obj': ent.get('obj'), 'when': r.exhausted_at, 'text': text + ' ' + note,
                        'ladder': {'label': r.label, 'sid': r.sid, 'heading': heading, 'tried': st['tried']}})
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

    for rule, ep, fn, methods in [
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
                           needs_me_reasons=needs_me_reasons, class_exhausted=class_exhausted,
                           for_objectives=for_objectives, analytics=analytics)


def _lkey(label):
    try:
        a, b = label.split('.')
        return (int(a), int(b))
    except (ValueError, AttributeError):
        return (999, 999)
