"""Lab progress: persistent per-student lab state, grading records and the instructor lab results page.

Before this module, a lab's state lived in the Flask session cookie (``lab_state_<id>`` per lab). That had
three problems: a reload lost the visible progress, opening a handful of labs pushed the signed cookie past
the 4 KB browser limit, and nothing but a bare completion row reached the instructor. Now:

* ``LabProgress`` (one row per student and lab) stores the engine state, the objectives met, the terminal
  transcript (capped), an undo stack, hint and attempt counts, the score (objectives met, 0-100) and timing.
  Every action autosaves, so a reload, a phone going to sleep or a different device resumes where the
  student stopped.
* Completion still writes ``LabCompletion`` (skills-exam stations read it), now only from server-side state:
  ``/mark-done`` no longer trusts a client-supplied list of objectives.
* Classroom labs (CL-*) are signed off by the instructor against the 4-criterion lab rubric and stored in
  the same table, so they reach progress, the gradebook "Labs" category and the results page.
* ``/instructor/section/<id>/labs/results`` shows every student against every lab of the course, with a CSV.

Routes keep the endpoint names the templates already use (``interactive_lab``, ``interactive_lab_cmd`` ...).
"""
import csv
import json
from datetime import datetime, timezone
from io import StringIO
from types import SimpleNamespace

from flask import Response, abort, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

import lab_runtime as RT

TRANSCRIPT_MAX = 400       # lines kept for resume
UNDO_MAX = 20              # snapshots kept for undo
_models = {}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def define_models(db):
    if 'm' in _models:
        return _models['m']

    class LabProgress(db.Model):
        __tablename__ = 'lab_progress'
        __table_args__ = (db.UniqueConstraint('user_id', 'lab_id', name='uq_lab_progress_user_lab'),)
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        lab_id = db.Column(db.String(80), nullable=False, index=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
        state_json = db.Column(db.Text)
        done_json = db.Column(db.Text)
        transcript_json = db.Column(db.Text)
        undo_json = db.Column(db.Text)
        hints_used = db.Column(db.Integer, default=0)
        actions = db.Column(db.Integer, default=0)      # commands typed, GUI actions or answer checks
        wrong = db.Column(db.Integer, default=0)        # rejected answers / unrecognised commands
        score = db.Column(db.Float, default=0)          # 0-100: objectives met (classroom labs: rubric points)
        best_score = db.Column(db.Float, default=0)
        started_at = db.Column(db.DateTime, default=utcnow)
        updated_at = db.Column(db.DateTime, default=utcnow)
        completed_at = db.Column(db.DateTime)
        resets = db.Column(db.Integer, default=0)
        graded_by = db.Column(db.Integer)               # classroom sign-off: instructor id
        rubric_json = db.Column(db.Text)                # classroom sign-off: [4 criterion levels]
        feedback = db.Column(db.Text)

    class LabEvent(db.Model):
        """Ordered action log per lab attempt, for process grading (how a student troubleshot, not just whether
        they finished). One row per command, GUI action, answer check, hint, undo, reset and completion."""
        __tablename__ = 'lab_event'
        __table_args__ = (db.Index('ix_lab_event_attempt', 'user_id', 'lab_id', 'attempt', 'seq'),)
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        lab_id = db.Column(db.String(80), nullable=False)
        attempt = db.Column(db.Integer, nullable=False, default=1)     # 1 + number of resets before it
        seq = db.Column(db.Integer, nullable=False, default=0)
        at = db.Column(db.DateTime, default=utcnow)
        kind = db.Column(db.String(16), nullable=False)               # cmd|event|check|hint|undo|reset|complete|vm
        action = db.Column(db.Text)                                   # the command / event / step id (+ answer JSON)
        outcome = db.Column(db.String(16))                            # ok|unknown|wrong|error|progress
        newly = db.Column(db.Text)                                    # objective ids earned by this action (JSON)
        score = db.Column(db.Float)                                   # score after the action
        detail = db.Column(db.Text)                                   # short output excerpt / feedback

    _models['m'] = SimpleNamespace(LabProgress=LabProgress, LabEvent=LabEvent)
    return _models['m']


def _j(text, default):
    try:
        return json.loads(text) if text else default
    except (TypeError, ValueError):
        return default


def register(app, db, deps):
    """deps: User, ClassSection, Enrollment, Module, LabCompletion, instructor_can_access_section,
    record_completion(lab_id, done, section_id, test_id), audit(action, detail)."""
    import stateful_sim as _SS
    app.jinja_env.globals.update(sim_packet_flow=_SS.has_packet_flow, sim_hw_ids=_SS.HW_IDS)
    m = define_models(db)
    LP = m.LabProgress
    LE = m.LabEvent
    d = SimpleNamespace(**deps)
    with app.app_context():
        LP.__table__.create(db.engine, checkfirst=True)
        LE.__table__.create(db.engine, checkfirst=True)

    def log(row, kind, action, outcome='ok', newly=None, detail=None):
        """Queue one event-log row (committed with the caller's commit)."""
        attempt = (row.resets or 0) + 1
        last = (db.session.query(db.func.max(LE.seq)).filter_by(user_id=row.user_id, lab_id=row.lab_id, attempt=attempt).scalar() or 0)
        db.session.add(LE(user_id=row.user_id, lab_id=row.lab_id, attempt=attempt, seq=last + 1, at=utcnow(), kind=kind,
                          action=(action or '')[:1000], outcome=outcome, newly=json.dumps(list(newly or [])) if newly else None,
                          score=row.score, detail=(detail or '')[:400] or None))

    def process_summary(evs):
        """Per attempt: actions, unknown/wrong, hints, undo, first-progress and completion times (process grading inputs)."""
        out = {}
        for e in evs:
            a = out.setdefault(e.attempt, {'attempt': e.attempt, 'start': e.at, 'end': e.at, 'actions': 0, 'unknown': 0, 'wrong': 0,
                                           'errors': 0, 'hints': 0, 'undo': 0, 'progress': 0, 'complete': None, 'repeats': 0, '_last': None})
            a['end'] = e.at
            if e.kind in ('cmd', 'event', 'check', 'vm'):
                a['actions'] += 1
                if e.action and e.action == a['_last']:
                    a['repeats'] += 1
                a['_last'] = e.action
            a['unknown'] += e.outcome == 'unknown'
            a['wrong'] += e.outcome == 'wrong'
            a['errors'] += e.outcome == 'error'
            a['hints'] += e.kind == 'hint' and e.outcome == 'ok'
            a['undo'] += e.kind == 'undo'
            a['progress'] += bool(e.newly)
            if e.kind == 'complete' and not a['complete']:
                a['complete'] = e.at
        rows = []
        for a in out.values():
            a.pop('_last', None)
            a['minutes'] = round(((a['complete'] or a['end']) - a['start']).total_seconds() / 60, 1)
            rows.append(a)
        return rows

    def events_for(user_id, lab_id, attempt=None):
        q = LE.query.filter_by(user_id=user_id, lab_id=lab_id)
        if attempt:
            q = q.filter_by(attempt=attempt)
        return q.order_by(LE.attempt, LE.seq).all()


    # ------------------------------------------------------------------ pass 20: dynamic lab process analysis
    from mastery import lab_diagnosis as LD
    RUNG_NAME = {'R1': 'Simpler words', 'R2': 'Different analogy', 'R3': 'Visual walk-through', 'R4': 'Try it'}

    def lesson_links(res, section=None, user_id=None):
        """Resolve each pattern's lesson ref to a title and (when the student can open it) a lesson URL + ladder anchor."""
        C, L = getattr(d, 'Course', None), getattr(d, 'Lesson', None)
        cache = {}
        for p in (res or {}).get('patterns', []):
            ref = p.get('ref')
            if not ref:
                continue
            ref.setdefault('rung_name', RUNG_NAME.get(ref['rung'], ref['rung']))
            ref.setdefault('title', f"{ref['course']} lesson {ref['label']}")
            if not (C and L):
                continue
            key = (ref['course'], ref['label'])
            if key not in cache:
                cache[key] = None
                try:
                    from curriculum_v2.ladder.sections import lesson_label
                    course = C.query.filter_by(code=ref['course']).first()
                    mod = course and d.Module.query.filter_by(course_id=course.id, order=int(ref['label'].split('.')[0])).first()
                    les = mod and next((x for x in L.query.filter_by(module_id=mod.id).all() if lesson_label(x.title) == ref['label']), None)
                    sec = section if (section is not None and course and section.course_id == course.id) else None
                    if les and sec is None and user_id and course:
                        en = (d.Enrollment.query.join(d.ClassSection, d.ClassSection.id == d.Enrollment.section_id)
                              .filter(d.Enrollment.user_id == user_id, d.ClassSection.course_id == course.id).first())
                        sec = en and db.session.get(d.ClassSection, en.section_id)
                    cache[key] = (les, mod, sec)
                except Exception:
                    cache[key] = None
            hit = cache[key]
            if hit and hit[0]:
                les, mod, sec = hit
                ref['title'] = les.title
                from curriculum_v2 import ladder as _LD
                from mastery.ladder import STYLE as _STYLE
                ref['heading'] = (_LD.ladder().get((ref['course'], ref['label'], ref['sid'])) or {}).get('heading') or ref['concept']
                ref['style'] = _STYLE.get(ref.get('rung') or '', 'another way')
                if sec is not None:
                    ref['url'] = (url_for('lesson_shortcut', section_id=sec.id, lesson_id=les.id, rung=ref.get('rung') or 'R1',
                                          sid=ref['sid']) + f"#ladder-sec-{ref['sid']}")
        return res

    def lab_analysis_for(user_id, lab_id, section=None):
        """Analysis of the student's latest attempt at one lab (None when nothing was recorded)."""
        lab = RT.get_lab(lab_id) or RT.classroom_lab(lab_id)
        latest = max([e.attempt for e in LE.query.filter_by(user_id=user_id, lab_id=lab_id).with_entities(LE.attempt).all()] or [0])
        if not latest:
            return None
        evs = events_for(user_id, lab_id, latest)
        if not evs:
            return None
        ldef = {'id': lab_id, 'objectives': [{'id': o['id'], 'text': o.get('text', o['id'])} for o in (lab or {}).get('objectives') or []]}
        return lesson_links(LD.analyze(evs, lab=ldef), section, user_id)

    def class_lab_analysis(section, lab_ids, uids, limit=20000):
        """Class roll-up from one query: latest attempt per (student, lab)."""
        if not uids or not lab_ids:
            return LD.class_summary([])
        rows = (LE.query.filter(LE.user_id.in_(uids), LE.lab_id.in_(lab_ids))
                .order_by(LE.user_id, LE.lab_id, LE.attempt, LE.seq).limit(limit).all())
        groups = {}
        for e in rows:
            g = groups.setdefault((e.user_id, e.lab_id), {'attempt': 0, 'evs': []})
            if e.attempt > g['attempt']:
                g['attempt'], g['evs'] = e.attempt, []
            g['evs'].append(e)
        anas = []
        for (_, lid), g in groups.items():
            lab = RT.get_lab(lid) or {}
            ldef = {'id': lid, 'objectives': [{'id': o['id'], 'text': o.get('text', o['id'])} for o in lab.get('objectives') or []]}
            anas.append(LD.analyze(g['evs'], lab=ldef))
        return lesson_links(LD.class_summary(anas), section)

    @login_required
    def interactive_lab_analysis(lab_id):
        """The student's own Dynamic Lab Process Analysis (during or after an attempt)."""
        lab = lab_or_404(lab_id)
        section = None
        try:
            sid = int(session.get('lab_section_id') or 0)
            section = sid and db.session.get(d.ClassSection, sid) or None
        except (TypeError, ValueError):
            section = None
        ana = lab_analysis_for(current_user.id, lab_id, section)
        if request.args.get('format') == 'json':
            return jsonify({k: ana[k] for k in ('attempt', 'summary', 'sequence', 'phases', 'minutes', 'concerns', 'strengths')} if ana else {})
        return render_template('lab_analysis.html', lab=lab, ana=ana)

    # ------------------------------------------------------------------ persistence helpers
    def get_row(lab_id, create=True, user_id=None):
        uid = user_id or current_user.id
        row = LP.query.filter_by(user_id=uid, lab_id=lab_id).first()
        if row is None and create:
            row = LP(user_id=uid, lab_id=lab_id, state_json=json.dumps(RT.fresh_state(lab_id, uid)),
                     done_json='[]', transcript_json='[]', undo_json='[]', started_at=utcnow(), updated_at=utcnow())
            db.session.add(row)
            db.session.commit()
        return row

    def load(row):
        st = _j(row.state_json, None)
        if st is None:
            st = RT.fresh_state(row.lab_id, row.user_id)
        return st, _j(row.done_json, [])

    def context_ids():
        sid = request.args.get('section_id') or session.get('lab_section_id')
        tid = request.args.get('test_id') or session.get('lab_test_id')
        try:
            sid = int(sid) if sid else None
        except (TypeError, ValueError):
            sid = None
        try:
            tid = int(tid) if tid else None
        except (TypeError, ValueError):
            tid = None
        return sid, tid

    def save(row, lab, state, done, lines=None, snapshot=None, wrong=False, count=True, ev=None):
        """Persist state; ev = (kind, action, outcome, newly, detail) appends to the attempt's event log."""
        was_complete = RT.is_complete(lab, _j(row.done_json, []))
        if snapshot is not None:
            undo = _j(row.undo_json, [])
            undo.append(snapshot)
            row.undo_json = json.dumps(undo[-UNDO_MAX:])
        if lines:
            tr = _j(row.transcript_json, [])
            tr.extend(lines)
            row.transcript_json = json.dumps(tr[-TRANSCRIPT_MAX:])
        row.state_json = json.dumps(state)
        row.done_json = json.dumps(list(done))
        if count:
            row.actions = (row.actions or 0) + 1
        if wrong:
            row.wrong = (row.wrong or 0) + 1
        row.score = RT.score(lab, done)
        row.best_score = max(row.best_score or 0, row.score)
        row.updated_at = utcnow()
        sid, tid = context_ids()
        if sid:
            row.section_id = sid
        complete = RT.is_complete(lab, done)
        if complete and not row.completed_at:
            row.completed_at = utcnow()
        if ev:
            log(row, *ev)
        if complete and not was_complete:
            log(row, 'complete', lab['id'], 'ok', None, f'score {row.score:.0f}; hints {row.hints_used or 0}; actions {row.actions or 0}')
        db.session.commit()
        if complete:
            try:
                d.record_completion(lab['id'], done, section_id=sid, test_id=tid)
            except Exception as exc:  # pragma: no cover - completion log must never break the lab
                print('lab completion note:', exc)
        return complete

    def payload_for(row, lab, state, done, extra=None):
        out = RT.view(lab, state, done)
        out.update({
            'done': list(done), 'score': row.score or 0, 'complete': RT.is_complete(lab, done),
            'hints_used': row.hints_used or 0, 'can_undo': bool(_j(row.undo_json, [])),
            'success_msg': lab.get('success_msg') if RT.is_complete(lab, done) else None,
        })
        if extra:
            out.update(extra)
        return out

    def lab_or_404(lab_id):
        lab = RT.get_lab(lab_id)
        if not lab:
            abort(404)
        return lab

    def lab_or_json_404(lab_id):
        lab = RT.get_lab(lab_id)
        if not lab:
            return None, (jsonify({'error': 'unknown lab'}), 404)
        return lab, None

    # ------------------------------------------------------------------ student routes
    @login_required
    def interactive_labs_index():
        labs = RT.list_labs()
        prog = {r.lab_id: r for r in LP.query.filter_by(user_id=current_user.id).all()}
        classroom = [RT.classroom_lab(c) for c in RT.classroom_ids()]
        return render_template('interactive_labs_index.html', labs=labs, progress=prog, groups=RT.KIND_GROUPS, classroom=classroom,
                               scenarios=RT.scenarios())

    @login_required
    def interactive_labs_verify():
        if current_user.role not in ('admin', 'instructor'):
            flash('Lab verify is for instructors and admins.', 'warning')
            return redirect(url_for('interactive_labs_index'))
        ok, report = RT.verify_all_labs()
        return render_template('interactive_labs_verify.html', ok=ok, report=report)

    @login_required
    def interactive_lab(lab_id):
        lab = lab_or_404(lab_id)
        if request.args.get('section_id'):
            session['lab_section_id'] = request.args.get('section_id')
        if request.args.get('test_id'):
            session['lab_test_id'] = request.args.get('test_id')
        elif request.args.get('section_id'):
            session.pop('lab_test_id', None)       # plain practice from a class page is not an exam station
        row = get_row(lab_id)
        state, done = load(row)
        d.audit('lab_open', lab_id)
        back = None
        if session.get('lab_test_id') and session.get('lab_section_id'):
            try:
                back = url_for('take_test', section_id=int(session['lab_section_id']), test_id=int(session['lab_test_id']))
            except Exception:
                back = None
        boot = payload_for(row, lab, state, done)
        boot['transcript'] = _j(row.transcript_json, [])
        if lab.get('kind') == 'vm':
            boot['vm_nonce'] = state.get('nonce')
        tpl = {'win11gui': 'win11_gui_lab.html', 'linuxgui': 'linux_gui_lab.html', 'activity': 'activity_lab.html', 'vm': 'vm_lab.html'}.get(lab.get('kind'), 'interactive_lab.html')
        vm_ok = None
        if lab.get('kind') == 'vm':
            import os
            vdir = os.path.join(app.static_folder, 'vendor', 'v86')
            vm_ok = all(os.path.isfile(os.path.join(vdir, f)) for f in ('libv86.js', 'v86.wasm', 'seabios.bin', 'vgabios.bin', lab['vm']['image']))
        fallback_labs = [x for x in (RT.get_lab(f) for f in lab.get('fallback') or []) if x]
        real_labs = [x for x in RT.VM.VM_LABS if lab['id'] in (x.get('fallback') or [])]
        # r5: a simulator opened from a real-VM page that is not a catalogue twin (a scenario stage such as scn-dns-fix)
        # links back to that page too; scenario stages are only offered when the student came from them (?from=),
        # so a generic simulator never skips a scenario's stage lock
        src = RT.get_lab(str(request.args.get('from') or '')[:80])
        if (src and src.get('kind') == 'vm' and lab['id'] in (src.get('fallback') or [])
                and all(x['id'] != src['id'] for x in real_labs)):
            real_labs = [src] + real_labs
        return render_template(tpl, lab=lab, boot=boot, prompt=boot.get('prompt', ''), practical_back=back, vm_assets_ok=vm_ok,
                               fallback_labs=fallback_labs, real_labs=real_labs,
                               palette=RT.palette(lab), steps=RT.public_steps(lab, state))

    @login_required
    def interactive_lab_state(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state, done = load(row)
        out = payload_for(row, lab, state, done)
        out['transcript'] = _j(row.transcript_json, [])
        return jsonify(out)

    @login_required
    def interactive_lab_cmd(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state, done = load(row)
        command = ((request.get_json(silent=True) or {}).get('command') or '')[:500]
        before = {'state': state, 'done': list(done)}
        result, state, done = RT.run_command(lab_id, state, done, command)
        prompt_before = RT.prompt(lab, before['state'])
        lines = [{'t': prompt_before + ' ' + command, 'c': 'cmd'}] + [{'t': ln} for ln in (result.get('lines') or [])]
        if result.get('clear'):
            row.transcript_json = '[]'
            lines = []
        changed = (state != before['state']) or (done != before['done'])
        newly = [o for o in done if o not in before['done']]
        out_lines = result.get('lines') or []
        save(row, lab, state, done, lines=lines, snapshot=before if changed else None,
             wrong=bool(result.get('unknown')), count=bool(command.strip()),
             ev=('cmd', command, 'unknown' if result.get('unknown') else ('progress' if newly else 'ok'), newly,
                 ' | '.join(str(x) for x in out_lines[:3])) if command.strip() else None)
        return jsonify(payload_for(row, lab, state, done, {'lines': result.get('lines') or [], 'clear': bool(result.get('clear')),
                                                           'newly': [o for o in done if o not in before['done']]}))

    @login_required
    def interactive_lab_packet_flow(lab_id):
        """Packet / frame walk evaluated against the student's live lab state (stateful_sim.packet_flow)."""
        import stateful_sim as SS
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        if not SS.has_packet_flow(lab):
            return jsonify({'error': 'No packet walk for this lab'}), 404
        state, done = load(get_row(lab_id))
        return jsonify(SS.packet_flow(lab, state, done, request.args.get('type', 'icmp')))

    @login_required
    def interactive_lab_event(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state, done = load(row)
        body = request.get_json(silent=True) or {}
        before = {'state': state, 'done': list(done)}
        result, state, done = RT.apply_event(lab_id, state, done, str(body.get('ev') or '')[:60], body.get('data') or {})
        changed = done != before['done'] or result.get('changed')
        newly = [o for o in done if o not in before['done']]
        evname = str(body.get('ev') or '')[:60]
        data = body.get('data') or {}
        safe = {k: ('***' if 'pass' in k.lower() or k in ('confirm',) else v) for k, v in data.items()} if isinstance(data, dict) else {}
        save(row, lab, state, done, snapshot=before if changed else None, wrong=bool(result.get('error')),
             ev=('event', evname + (' ' + json.dumps(safe, sort_keys=True) if safe else ''),
                 'error' if result.get('error') else ('progress' if newly else 'ok'), newly, result.get('error')))
        return jsonify(payload_for(row, lab, state, done, {'result': result, 'newly': [o for o in done if o not in before['done']]}))

    @login_required
    def interactive_lab_check(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state, done = load(row)
        body = request.get_json(silent=True) or {}
        before = {'state': state, 'done': list(done)}
        result, state, done = RT.check_step(lab_id, state, done, str(body.get('step') or ''), body.get('answer'))
        newly = [o for o in done if o not in before['done']]
        save(row, lab, state, done, snapshot=before if done != before['done'] else None, wrong=not result.get('correct'),
             ev=('check', str(body.get('step') or '') + ' ' + json.dumps(body.get('answer'), sort_keys=True)[:800],
                 'ok' if result.get('correct') else 'wrong', newly, result.get('message')))
        return jsonify(payload_for(row, lab, state, done, {'result': result, 'newly': [o for o in done if o not in before['done']]}))

    @login_required
    def interactive_lab_hint(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state, done = load(row)
        h = RT.next_hint(lab, state, done, row.hints_used or 0)
        if h.get('counted'):
            row.hints_used = (row.hints_used or 0) + 1
            state.setdefault('_hint_tier', {})[h['objective']] = h['tier']
            row.state_json = json.dumps(state)
        log(row, 'hint', f"{h.get('objective')} tier {h.get('tier')}", 'ok' if h.get('counted') else 'repeat')
        db.session.commit()
        return jsonify(payload_for(row, lab, state, done, {'hint': h}))

    @login_required
    def interactive_lab_undo(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        undo = _j(row.undo_json, [])
        if not undo:
            state, done = load(row)
            return jsonify(payload_for(row, lab, state, done, {'lines': ['Nothing to undo.'], 'undone': False}))
        snap = undo.pop()
        row.undo_json = json.dumps(undo)
        state, done = snap['state'], snap['done']
        # objectives already earned stay earned (undo is for configuration mistakes, not for un-learning)
        done = list(dict.fromkeys(list(done) + _j(row.done_json, [])))
        save(row, lab, state, done, lines=[{'t': '(undo: last change reverted)', 'c': 'sys'}], count=False, ev=('undo', '', 'ok'))
        return jsonify(payload_for(row, lab, state, done, {'lines': ['Last change undone.'], 'undone': True}))

    @login_required
    def interactive_lab_reset(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state = RT.fresh_state(lab_id, current_user.id, reseed=(row.resets or 0) + 1)
        row.state_json = json.dumps(state)
        row.done_json = '[]'
        row.transcript_json = '[]'
        row.undo_json = '[]'
        row.score = 0
        log(row, 'reset', 'start over', 'ok')     # closes the old attempt
        row.resets = (row.resets or 0) + 1
        row.updated_at = utcnow()
        db.session.commit()      # best_score and completed_at keep the record of earlier work
        out = payload_for(row, lab, state, [])
        out['ok'] = True
        out['steps'] = RT.public_steps(lab, state)
        return jsonify(out)

    @login_required
    def interactive_lab_complete(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state, _ = load(row)
        partial = ((request.get_json(silent=True) or {}).get('partial') or '')[:300]
        return jsonify(RT.complete(lab, state, partial))

    @login_required
    def interactive_lab_vm_log(lab_id):
        """Real-VM labs: the page reports each command line the student sent to the VM (and the boot time)."""
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        if lab.get('kind') != 'vm':
            return jsonify({'error': 'not a VM lab'}), 400
        row = get_row(lab_id)
        state, done = load(row)
        body = request.get_json(silent=True) or {}
        lines = [str(x)[:500] for x in (body.get('lines') or [])][:50]
        before = list(done)
        state, done = RT.vm_log(lab_id, state, done, lines, booted=bool(body.get('booted')))
        if body.get('booted'):
            log(row, 'vm', 'boot', 'ok', None, f"booted in {body.get('boot_ms')} ms; {str(body.get('ua') or '')[:120]}")
        for i, ln in enumerate(lines):
            log(row, 'vm', ln, 'ok')
        tr = [{'t': '$ ' + ln, 'c': 'cmd'} for ln in lines]
        save(row, lab, state, done, lines=tr, count=bool(lines))
        return jsonify(payload_for(row, lab, state, done, {'newly': [o for o in done if o not in before]}))

    @login_required
    def interactive_lab_vm_check(lab_id):
        """Real-VM labs: grade the probe output the page read back from the VM."""
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        if lab.get('kind') != 'vm':
            return jsonify({'error': 'not a VM lab'}), 400
        row = get_row(lab_id)
        state, done = load(row)
        body = request.get_json(silent=True) or {}
        before = list(done)
        probes = body.get('probes')
        if isinstance(probes, dict):
            probes = {str(k)[:16]: str(v)[:6000] for k, v in list(probes.items())[:4]}
        else:
            probes = str(body.get('probe') or '')[:6000]
        fabric = body.get('fabric') if isinstance(body.get('fabric'), dict) else None
        if fabric:
            fabric = {'events': [e for e in (fabric.get('events') or [])[-200:] if isinstance(e, dict)]}
        res, state, done = RT.vm_check(lab_id, state, done, probes, booted=True, fabric=fabric)
        newly = [o for o in done if o not in before]
        save(row, lab, state, done, wrong=bool(res.get('error')) or bool(res.get('messages')),
             ev=('check', 'vm probe ' + json.dumps({k[2:]: v for k, v in (state.get('probe_last') or {}).items() if k.startswith('c_')}, sort_keys=True)
                   + (' · network: ' + ', '.join(sorted({f"{e.get('type')} {e.get('msg') or e.get('q') or e.get('to') or ''}".strip() for e in (fabric or {}).get('events', [])}))[:300] if fabric and fabric.get('events') else ''),
                 'error' if res.get('error') else ('ok' if RT.is_complete(lab, done) else ('progress' if newly else 'wrong')),
                 newly, res.get('error') or '; '.join(res.get('messages') or [])))
        if lab.get('pbq') and res.get('messages') and not RT.is_complete(lab, done):
            res = dict(res, messages=[RT.SC.pbq_message(lab, done)])
        return jsonify(payload_for(row, lab, state, done, {'result': res, 'newly': newly}))

    @login_required
    def interactive_lab_vm_probe(lab_id):
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state, _ = load(row)
        if lab.get('kind') != 'vm':
            return jsonify({'error': 'not a VM lab'}), 400
        scripts = RT.VM.probe_scripts(state, lab)
        return jsonify({'script': scripts[RT.VM.machines(lab)[0]], 'scripts': scripts})

    @login_required
    def interactive_lab_mark_done(lab_id):
        """Legacy endpoint: records completion from the SERVER state only."""
        lab, err = lab_or_json_404(lab_id)
        if err:
            return err
        row = get_row(lab_id)
        state, done = load(row)
        complete = save(row, lab, state, done, count=False)
        return jsonify({'ok': True, 'complete': complete, 'done': done})

    # ------------------------------------------------------------------ lab scenarios (PBQ tickets)
    @login_required
    def scenario_lab(sid):
        s = RT.scenario(sid)
        if not s:
            abort(404)
        ids = [st['id'] for st in s['stages']]
        rows = {r.lab_id: r for r in LP.query.filter(LP.user_id == current_user.id, LP.lab_id.in_(ids)).all()}
        d.audit('lab_open', sid)
        return render_template('scenario_lab.html', s=s, st=RT.SC.status(s, rows))

    # ------------------------------------------------------------------ classroom labs (student view)
    @login_required
    def classroom_lab(cl_id):
        cl = RT.classroom_lab(cl_id)
        if not cl:
            abort(404)
        row = LP.query.filter_by(user_id=current_user.id, lab_id=cl_id).first()
        return render_template('classroom_lab.html', cl=cl, row=row, rubric=RT.lab_rubric(),
                               levels=_j(row.rubric_json, []) if row else [])

    # ------------------------------------------------------------------ instructor results
    def staff_section(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if current_user.role == 'admin':
            return section
        if current_user.role != 'instructor' or not d.instructor_can_access_section(current_user, section):
            abort(403)
        return section

    def results_data(section):
        labs = RT.course_lab_set(section.course)
        enrolls = d.Enrollment.query.filter_by(section_id=section.id).all()
        uids = [e.user_id for e in enrolls] or [0]
        users = sorted(d.User.query.filter(d.User.id.in_(uids)).all(), key=lambda u: (u.last_name or '', u.first_name or ''))
        ids = [l['id'] for l in labs] or ['']
        rows = LP.query.filter(LP.user_id.in_(uids), LP.lab_id.in_(ids)).all()
        by = {(r.user_id, r.lab_id): r for r in rows}
        table = []
        for u in users:
            cells = []
            for l in labs:
                r = by.get((u.id, l['id']))
                cells.append({'lab': l, 'row': r, 'score': None if r is None else round(max(r.best_score or 0, r.score or 0)),
                              'complete': bool(r and r.completed_at), 'started': r is not None})
            done_n = len([c for c in cells if c['complete']])
            mean = round(sum((c['score'] or 0) for c in cells) / len(cells)) if cells else 0
            table.append({'user': u, 'cells': cells, 'done': done_n, 'mean': mean,
                          'hints': sum((c['row'].hints_used or 0) for c in cells if c['row']),
                          'last': max([c['row'].updated_at for c in cells if c['row'] and c['row'].updated_at] or [None], key=lambda x: x or datetime.min)})
        col = []
        for i, l in enumerate(labs):
            sc = [t['cells'][i] for t in table]
            col.append({'lab': l, 'complete': len([c for c in sc if c['complete']]), 'started': len([c for c in sc if c['started']]),
                        'n': len(sc)})
        return labs, table, col

    @login_required
    def instructor_lab_results(section_id):
        section = staff_section(section_id)
        labs, table, col = results_data(section)
        focus = request.args.get('lab') or ''
        lab_ids = [focus] if focus else [l['id'] for l in labs if l.get('kind') != 'classroom']
        cls = class_lab_analysis(section, lab_ids, [t['user'].id for t in table])
        cls_title = next((l['title'] for l in labs if l['id'] == focus), '') if focus else 'all labs'
        return render_template('instructor_lab_results.html', section=section, labs=labs, table=table, col=col, cls=cls, cls_title=cls_title,
                               focus=focus, rubric=RT.lab_rubric(), classroom=[l for l in labs if l['kind'] == 'classroom'])

    @login_required
    def instructor_lab_results_csv(section_id):
        section = staff_section(section_id)
        labs, table, _ = results_data(section)
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(['last', 'first', 'email', 'labs_complete', 'lab_mean'] + [l['id'] for l in labs])
        for t in table:
            u = t['user']
            w.writerow([u.last_name, u.first_name, u.email, t['done'], t['mean']] +
                       ['' if c['score'] is None else f"{c['score']}{'' if c['complete'] else ' (in progress)'}" for c in t['cells']])
        d.audit('lab_results_csv', f'section={section.id}')
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': f'attachment; filename=lab-results-section-{section.id}.csv'})

    @login_required
    def instructor_lab_student(section_id, user_id, lab_id):
        section = staff_section(section_id)
        if not d.Enrollment.query.filter_by(section_id=section.id, user_id=user_id).first():
            abort(404)
        u = db.get_or_404(d.User, user_id)
        lab = RT.get_lab(lab_id) or RT.classroom_lab(lab_id)
        if not lab:
            abort(404)
        row = LP.query.filter_by(user_id=user_id, lab_id=lab_id).first()
        evs = events_for(user_id, lab_id)
        ana = lab_analysis_for(user_id, lab_id, section)
        return render_template('instructor_lab_student.html', section=section, student=u, lab=lab, row=row, ana=ana,
                               attempts=process_summary(evs), events=evs[-400:],
                               done=_j(row.done_json, []) if row else [], transcript=_j(row.transcript_json, []) if row else [],
                               rubric=RT.lab_rubric(), levels=_j(row.rubric_json, []) if row else [])

    @login_required
    def instructor_lab_events_csv(section_id):
        """Every student's ordered lab event log for the section (process-grading export)."""
        import csv
        import io
        section = staff_section(section_id)
        uids = [e.user_id for e in d.Enrollment.query.filter_by(section_id=section.id).all()]
        q = LE.query.filter(LE.user_id.in_(uids or [0]))
        if request.args.get('lab'):
            q = q.filter_by(lab_id=request.args['lab'])
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['user_id', 'lab_id', 'attempt', 'seq', 'at_utc', 'kind', 'action', 'outcome', 'newly', 'score_after', 'detail'])
        for e in q.order_by(LE.user_id, LE.lab_id, LE.attempt, LE.seq).limit(200000):
            w.writerow([e.user_id, e.lab_id, e.attempt, e.seq, e.at.isoformat(timespec='seconds'), e.kind, e.action, e.outcome,
                        e.newly or '', '' if e.score is None else round(e.score, 1), e.detail or ''])
        d.audit('lab_events_csv', f'section={section.id}')
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': f'attachment; filename=lab-events-section-{section.id}.csv'})

    @login_required
    def instructor_classroom_signoff(section_id):
        section = staff_section(section_id)
        f = request.form
        cl = RT.classroom_lab(f.get('lab_id') or '')
        try:
            uid = int(f.get('user_id') or 0)
        except ValueError:
            uid = 0
        if not cl or not d.Enrollment.query.filter_by(section_id=section.id, user_id=uid).first():
            flash('Choose a classroom lab and a student in this class.', 'warning')
            return redirect(url_for('instructor_lab_results', section_id=section.id))
        if f.get('clear') == '1':
            row = LP.query.filter_by(user_id=uid, lab_id=cl['id']).first()
            if row:
                db.session.delete(row)
                db.session.commit()
            d.audit('classroom_lab_clear', f"section={section.id} user={uid} lab={cl['id']}")
            flash('Sign-off removed.', 'info')
            return redirect(url_for('instructor_lab_results', section_id=section.id, lab=cl['id']) + '#signoff')
        levels = []
        for i in range(4):
            try:
                v = int(f.get(f'c{i}') or 0)
            except ValueError:
                v = 0
            if v not in (1, 2, 3, 4):
                flash('Score all four rubric criteria (1–4).', 'warning')
                return redirect(url_for('instructor_lab_results', section_id=section.id, lab=cl['id']) + '#signoff')
            levels.append(v)
        row = get_row(cl['id'], user_id=uid)
        row.rubric_json = json.dumps(levels)
        row.score = round(100.0 * sum(levels) / 16, 1)
        row.best_score = row.score
        row.done_json = json.dumps(['signed_off'])
        row.graded_by = current_user.id
        row.section_id = section.id
        row.feedback = (f.get('feedback') or '').strip()[:1000]
        row.completed_at = row.completed_at or utcnow()
        row.updated_at = utcnow()
        if row.id is None:
            db.session.flush()
        log(row, 'signoff', f'levels {levels} by instructor {current_user.id}', 'ok', None, row.feedback)
        db.session.commit()
        d.audit('classroom_lab_signoff', f"section={section.id} user={uid} lab={cl['id']} levels={levels}")
        flash(f"{cl['id']} signed off: {sum(levels)}/16 ({row.score:.0f}%).", 'success')
        return redirect(url_for('instructor_lab_results', section_id=section.id, lab=cl['id']) + '#signoff')

    # ------------------------------------------------------------------ data for other modules
    def lab_scores(section, user_ids):
        """{user_id: (score 0-100 or None, n_complete, n_labs)} over the course lab set; None = no lab started."""
        labs = RT.course_lab_set(section.course)
        ids = [l['id'] for l in labs]
        if not ids:
            return {}
        out = {}
        rows = LP.query.filter(LP.user_id.in_(list(user_ids) or [0]), LP.lab_id.in_(ids)).all()
        per = {}
        for r in rows:
            per.setdefault(r.user_id, {})[r.lab_id] = r
        for uid in user_ids:
            mine = per.get(uid) or {}
            if not mine:
                out[uid] = (None, 0, len(ids))
                continue
            total = sum(max(r.best_score or 0, r.score or 0) for r in mine.values())
            out[uid] = (round(total / len(mine), 1), len([r for r in mine.values() if r.completed_at]), len(ids))
        return out

    def lab_signature(user_ids):
        from sqlalchemy import func
        return tuple(db.session.query(func.count(LP.id), func.max(LP.updated_at)).filter(LP.user_id.in_(list(user_ids) or [0])).first())

    def progress_map(user_id):
        return {r.lab_id: r for r in LP.query.filter_by(user_id=user_id).all()}

    for rule, ep, fn, methods in [
        ('/live-labs', 'interactive_labs_index', interactive_labs_index, ['GET']),
        ('/labs', 'interactive_labs_index', interactive_labs_index, ['GET']),
        ('/labs/verify', 'interactive_labs_verify', interactive_labs_verify, ['GET']),
        ('/labs/classroom/<cl_id>', 'classroom_lab', classroom_lab, ['GET']),
        ('/labs/scenario/<sid>', 'scenario_lab', scenario_lab, ['GET']),
        ('/labs/<lab_id>', 'interactive_lab', interactive_lab, ['GET']),
        ('/labs/<lab_id>/analysis', 'interactive_lab_analysis', interactive_lab_analysis, ['GET']),
        ('/labs/<lab_id>/state', 'interactive_lab_state', interactive_lab_state, ['GET']),
        ('/labs/<lab_id>/cmd', 'interactive_lab_cmd', interactive_lab_cmd, ['POST']),
        ('/labs/<lab_id>/event', 'interactive_lab_event', interactive_lab_event, ['POST']),
        ('/labs/<lab_id>/packet-flow', 'interactive_lab_packet_flow', interactive_lab_packet_flow, ['GET']),
        ('/labs/<lab_id>/check', 'interactive_lab_check', interactive_lab_check, ['POST']),
        ('/labs/<lab_id>/hint', 'interactive_lab_hint', interactive_lab_hint, ['POST']),
        ('/labs/<lab_id>/undo', 'interactive_lab_undo', interactive_lab_undo, ['POST']),
        ('/labs/<lab_id>/reset', 'interactive_lab_reset', interactive_lab_reset, ['POST']),
        ('/labs/<lab_id>/complete', 'interactive_lab_complete', interactive_lab_complete, ['POST']),
        ('/labs/<lab_id>/vm-log', 'interactive_lab_vm_log', interactive_lab_vm_log, ['POST']),
        ('/labs/<lab_id>/vm-check', 'interactive_lab_vm_check', interactive_lab_vm_check, ['POST']),
        ('/labs/<lab_id>/vm-probe', 'interactive_lab_vm_probe', interactive_lab_vm_probe, ['GET']),
        ('/labs/<lab_id>/mark-done', 'interactive_lab_mark_done', interactive_lab_mark_done, ['POST']),
        ('/instructor/section/<int:section_id>/labs/results', 'instructor_lab_results', instructor_lab_results, ['GET']),
        ('/instructor/section/<int:section_id>/labs/results.csv', 'instructor_lab_results_csv', instructor_lab_results_csv, ['GET']),
        ('/instructor/section/<int:section_id>/labs/student/<int:user_id>/<lab_id>', 'instructor_lab_student', instructor_lab_student, ['GET']),
        ('/instructor/section/<int:section_id>/labs/events.csv', 'instructor_lab_events_csv', instructor_lab_events_csv, ['GET']),
        ('/instructor/section/<int:section_id>/labs/signoff', 'instructor_classroom_signoff', instructor_classroom_signoff, ['POST']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)

    @app.context_processor
    def _lab_progress_ctx():
        def lab_progress_for(user=None):
            u = user or current_user
            if not getattr(u, 'is_authenticated', False):
                return {}
            return progress_map(u.id)
        return {'lab_progress_for': lab_progress_for}

    api = SimpleNamespace(LabProgress=LP, LabEvent=LE, events_for=events_for, lab_analysis_for=lab_analysis_for, process_summary=process_summary, log=log, lab_scores=lab_scores, lab_signature=lab_signature, progress_map=progress_map)
    app.extensions['ciwt_lab_progress'] = api
    return api
