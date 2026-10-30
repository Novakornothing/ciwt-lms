"""School-ready pass: comprehension gate, LTI, sections hub, outcomes, accessibility, FERPA, staff roles."""
import re

from tests.test_ladder_engine import _ans, _check_ids, _lesson, _reset, _section_for, lesson11  # noqa: F401


def _lesson_ids(html):
    return re.findall(r'id="ladder-sec-([^"]+)"', html)


# ---------------------------------------------------------------- 0. comprehension gate
def test_gate_banner_locks_and_advance_redirect(student, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    html = student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    sids = _lesson_ids(html)
    assert sids and 'id="ladderGate"' in html and f'0 of {len(sids)}' in html
    assert 'Complete the quick check above to unlock this section' in html
    assert f'href="#ladder-sec-{sids[0]}"' in html and '/advance?' in html
    r = student.get(f'/student/section/{s}/lesson/{l}/advance?to=module')
    assert r.status_code == 303 and r.headers['Location'].endswith(f'#ladder-sec-{sids[0]}')
    g = student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()
    assert g['blocked'] and g['total'] == len(sids) and g['done'] == 0
    # verify every section correctly -> gate opens
    for sid in sids:
        html = student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
        cid, _ = _check_ids(html, sid)
        if not cid:
            continue
        with app.app_context():
            right = _ans(cid, True)
        student.post(f'/student/section/{s}/ladder/{l}/{sid}/answer', data={'check_id': cid, 'answer': right})
    g = student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()
    assert not g['blocked'] and g['done'] == g['total']
    r = student.get(f'/student/section/{s}/lesson/{l}/advance?to=module')
    assert r.status_code == 303 and '#ladder-sec-' not in r.headers['Location']


def test_gate_setting_off_and_bypass(student, instructor, mod, app, lesson11):
    uid = _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'bypass', 'user_id': uid, 'lesson_id': l})
    g = student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()
    assert g['exempt'] and not g['blocked']
    assert 'id="ladderGate"' not in student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'bypass', 'action': 'remove', 'user_id': uid, 'lesson_id': l})
    assert student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()['blocked']
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'class', 'gate_form': '1', 'enabled': 'on', 'micro_checks': 'on'})
    g = student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()
    assert not g['on'] and not g['blocked']
    _reset(mod, app, 'student1@lms.local')


def test_quiz_strict_gate_only_when_enabled(student, instructor, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    with app.app_context():
        q = mod.Quiz.query.filter_by(module_id=m).first()
    if not q:
        return
    assert student.get(f'/student/quiz/{s}/{q.id}').status_code == 200        # default: quiz not gated
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'class', 'gate_form': '1', 'enabled': 'on',
                                                             'micro_checks': 'on', 'require_check_to_advance': 'on',
                                                             'gate_quiz_on_ladder': 'on'})
    r = student.get(f'/student/quiz/{s}/{q.id}')
    assert r.status_code == 303 and '#ladder-sec-' in r.headers['Location']
    _reset(mod, app, 'student1@lms.local')


# ---------------------------------------------------------------- 1. LTI roster removal, auto-passback, exemptions
from tests.test_lti import ensure_learner_launched, env  # noqa: E402,F401


def _lti_policy(instructor, **on):
    r = instructor.post('/instructor/section/1/lti/settings', data={k: 'on' for k, v in on.items() if v})
    assert r.status_code == 303


def test_lti_roster_removes_dropped_only_when_opted_in(app, mod, env, instructor):
    ensure_learner_launched(app, env)
    m = env['m']
    with app.app_context():
        u = mod.User(email='dropped-lti@lms.local', first_name='Dropped', last_name='Learner', role='student')
        u.set_password('x'); mod.db.session.add(u); mod.db.session.flush()
        mod.db.session.add(m.LtiUserLink(platform_id=env['pid'], sub='gone-1', user_id=u.id, how='roster'))
        mod.db.session.add(mod.Enrollment(user_id=u.id, section_id=1)); mod.db.session.commit()
        gone = u.id
    instructor.post('/instructor/section/1/lti/roster')
    with app.app_context():
        assert mod.Enrollment.query.filter_by(user_id=gone, section_id=1).count() == 1      # default: nobody removed
    _lti_policy(instructor, remove_dropped=True)
    instructor.post('/instructor/section/1/lti/roster')
    with app.app_context():
        assert mod.Enrollment.query.filter_by(user_id=gone, section_id=1).count() == 0
        two = m.LtiUserLink.query.filter_by(sub='mock-student-2').first()
        assert mod.Enrollment.query.filter_by(user_id=two.user_id, section_id=1).count() == 1
        log = m.LtiSyncLog.query.filter_by(kind='roster').order_by(m.LtiSyncLog.id.desc()).first()
        assert '1 removed' in log.detail
    h = instructor.get('/instructor/section/1/lti').get_data(as_text=True)
    assert 'Sync history' in h and 'Roster and grade policy' in h
    _lti_policy(instructor)


def test_lti_auto_passback_and_exempt_full(app, mod, env, instructor, monkeypatch):
    ensure_learner_launched(app, env)
    api = env['api']
    with app.app_context():
        uid = env['m'].LtiUserLink.query.filter_by(sub='mock-student-1').first().user_id
        user = mod.db.session.get(mod.User, uid)
        real = app.extensions['ciwt_gradebook'].compute

        def fake(section):
            return {'rows': [{'user': user, 'grade': None, 'cells': [{'item': {'type': 'quiz', 'id': 1}, 'status': 'exempt', 'score': None}]}]}
        monkeypatch.setattr(app.extensions['ciwt_gradebook'], 'compute', fake)
    _lti_policy(instructor, auto_passback=True)
    with app.test_request_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        n0 = len(env['st']['scores'])
        log = api.send_scores(sec, user, {uid}, auto=True)
        assert log.kind == 'auto-scores' and log.skipped >= 1 and len(env['st']['scores']) == n0   # exempt: skipped
    _lti_policy(instructor, auto_passback=True, exempt_full=True)
    with app.test_request_context():
        log = api.send_scores(mod.db.session.get(mod.ClassSection, 1), user, {uid}, auto=True)
        sent = [s for s in env['st']['scores'] if s['userId'] == 'mock-student-1']
        assert log.ok >= 1 and sent[-1]['scoreGiven'] == 100 and 'Exempt' in sent[-1].get('comment', '')
    monkeypatch.setattr(app.extensions['ciwt_gradebook'], 'compute', real)
    _lti_policy(instructor)


# ---------------------------------------------------------------- 2. sections hub, clone, roster
def test_hub_clone_roster_import_transfer_drop_and_join(app, mod, instructor, student2, instructor2):
    h = instructor.get('/instructor/sections').get_data(as_text=True)
    assert 'Your sections' in h and 'Ladder resolution' in h and 'Clone' in h
    assert 'id="appNav"' in instructor.get('/instructor/sections').get_data(as_text=True)
    r = instructor.post('/instructor/section/1/clone')
    assert r.status_code == 303
    new_id = int(r.headers['Location'].rstrip('/').split('/')[-2])
    sr = app.extensions['ciwt_school']
    with app.app_context():
        src, new = mod.db.session.get(mod.ClassSection, 1), mod.db.session.get(mod.ClassSection, new_id)
        assert new.course_id == src.course_id and mod.Enrollment.query.filter_by(section_id=new_id).count() == 0
        assert sr.join_code(new) != sr.join_code(src)
        lm = mod.mastery_api.ladder.models
        if lm.LadderSetting.query.filter_by(section_id=1).first():
            assert lm.LadderSetting.query.filter_by(section_id=new_id).first()
    csv_rows = 'email,full_name,role\nnew-csv@lms.local,Casey Import,student\nstudent2@lms.local,,student\ninstructor2@lms.local,,observer\nbad-row\n'
    r = instructor.post(f'/instructor/section/{new_id}/roster', data={'action': 'import', 'csv': csv_rows})
    with app.app_context():
        s2 = mod.User.query.filter_by(email='student2@lms.local').first()
        assert mod.Enrollment.query.filter_by(section_id=new_id).count() == 2
        assert sr.SectionStaff.query.filter_by(section_id=new_id).first().role == 'observer'
    # transfer student2 back to section 1 (same course), then drop
    instructor.post(f'/instructor/section/{new_id}/roster', data={'action': 'transfer', 'user_id': s2.id, 'to': 1})
    with app.app_context():
        assert not mod.Enrollment.query.filter_by(section_id=new_id, user_id=s2.id).first()
        assert mod.Enrollment.query.filter_by(section_id=1, user_id=s2.id).first()
        casey = mod.User.query.filter_by(email='new-csv@lms.local').first()
    instructor.post(f'/instructor/section/{new_id}/roster', data={'action': 'drop', 'user_id': casey.id})
    with app.app_context():
        assert mod.Enrollment.query.filter_by(section_id=new_id).count() == 0
        old = sr.join_code(mod.db.session.get(mod.ClassSection, new_id))
    instructor.post(f'/instructor/section/{new_id}/roster', data={'action': 'regen'})
    with app.app_context():
        code = sr.join_code(mod.db.session.get(mod.ClassSection, new_id))
        assert code != old
    assert student2.post('/join', data={'code': old}).status_code == 302
    student2.post('/join', data={'code': code})
    with app.app_context():
        assert mod.Enrollment.query.filter_by(section_id=new_id, user_id=s2.id).first()
    # 6. observer: can view, cannot change
    assert instructor2.get(f'/instructor/section/{new_id}/roster').status_code == 200
    assert instructor2.get(f'/instructor/section/{new_id}/setup').status_code == 200
    assert instructor2.post(f'/instructor/section/{new_id}/roster', data={'action': 'regen'}).status_code == 403
    assert instructor2.post(f'/instructor/section/{new_id}/ladder/settings', data={'form': 'class'}).status_code == 403
    # TA: grading allowed paths stay open, LTI / privacy / roster changes refused
    instructor.post(f'/instructor/section/{new_id}/roster', data={'action': 'staff', 'email': 'instructor2@lms.local', 'role': 'ta'})
    with app.app_context():
        assert sr.SectionStaff.query.filter_by(section_id=new_id).first().role == 'ta'
        assert sr.can_edit_grades(mod.User.query.filter_by(email='instructor2@lms.local').first(), mod.db.session.get(mod.ClassSection, new_id))
    assert instructor2.post(f'/instructor/section/{new_id}/lti/settings', data={}).status_code == 403
    assert instructor2.get(f'/instructor/section/{new_id}/privacy').status_code == 403
    assert instructor2.post(f'/instructor/section/{new_id}/roster', data={'action': 'regen'}).status_code == 403
    assert instructor2.get(f'/instructor/section/{new_id}/outcomes').status_code == 200
    with app.app_context():   # tidy: remove the clone
        mod.Enrollment.query.filter_by(section_id=new_id).delete()
        sr.SectionStaff.query.filter_by(section_id=new_id).delete()
        mod.db.session.commit()


def test_setup_page_has_seven_areas(instructor, student):
    h = instructor.get('/instructor/section/1/setup').get_data(as_text=True)
    for key in ('roster', 'adaptive', 'ladder', 'helix', 'staff', 'lti', 'a11y'):
        assert f'id="setup-{key}"' in h
    assert student.get('/instructor/section/1/setup').status_code in (302, 403)
    assert student.get('/instructor/sections').status_code in (302, 403)


# ---------------------------------------------------------------- 3. outcomes
def test_outcomes_per_objective_columns_and_exports(instructor, admin):
    h = instructor.get('/instructor/section/1/outcomes').get_data(as_text=True)
    assert 'Cert objective' in h and 'Ladder resolution (R0 R1 R2 R3 R4 · Exhausted)' in h and 'Download JSON' in h
    c = instructor.get('/instructor/section/1/outcomes?format=csv').get_data(as_text=True)
    assert 'course_objective_id,course_objective,cert_objectives,students,initial_mastery_pct' in c
    j = instructor.get('/instructor/section/1/outcomes?format=json').get_json()
    assert j['status'].startswith('Pending SME review') and 'objectives' in j['mastery']
    if j['mastery']['objectives']:
        o = j['mastery']['objectives'][0]
        assert set(o['rungs']) == {'R0', 'R1', 'R2', 'R3', 'R4', 'EX'} and 'lab_pct' in o and 'attempts' in o and 'cert' in o
    assert admin.get('/admin/outcomes?format=json').status_code == 200
    from institutional.outcomes import cert_map
    assert any(c['label'].startswith(('220-1201', '220-1202', 'N10-009')) for c in cert_map('IT-5.2'))


# ---------------------------------------------------------------- 4. accessibility
def test_accessibility_page_footer_and_doc(anon, instructor):
    h = anon.get('/accessibility').get_data(as_text=True)
    assert 'WCAG 2.1' in h and 'Helix' in h and 'VM labs' in h and 'live region' in h
    assert 'href="/accessibility"' in anon.get('/accessibility').get_data(as_text=True)
    import pathlib
    doc = pathlib.Path(__file__).resolve().parents[1] / 'docs' / 'ACCESSIBILITY_WCAG21_AA.md'
    t = doc.read_text()
    assert 'Pending SME review' in t and 'aria-live' in t and 'prefers-reduced-motion' in t


# ---------------------------------------------------------------- 5. FERPA + audit chain
def test_my_data_export_json_and_zip(student):
    j = student.get('/my-data?format=json').get_json()
    assert j['profile']['email'] == 'student1@lms.local' and 'tables' in j
    assert not any('password' in k for rows in j['tables'].values() for r in rows for k in r)
    z = student.get('/my-data?format=zip')
    assert z.mimetype == 'application/zip' and z.data[:2] == b'PK'
    assert student.get('/admin/ferpa').status_code in (302, 403) and student.get('/admin/audit-log').status_code in (302, 403)


def test_request_workflow_anonymize_and_audit_chain(app, mod, admin, instructor):
    with app.app_context():
        u = mod.User(email='ferpa-del@lms.local', first_name='Fern', last_name='Delete', role='student')
        u.set_password('pw12345678'); mod.db.session.add(u); mod.db.session.flush()
        mod.db.session.add(mod.Enrollment(user_id=u.id, section_id=1)); mod.db.session.commit()
        uid = u.id
    assert instructor.get(f'/instructor/section/1/privacy?user_id={uid}&format=json').get_json()['profile']['id'] == uid
    instructor.post('/instructor/section/1/privacy', data={'user_id': uid, 'kind': 'delete'})
    sr = app.extensions['ciwt_school']
    with app.app_context():
        req = sr.DataRequest.query.filter_by(user_id=uid).first()
        assert req and req.status == 'open'
        rid = req.id
    assert 'ferpa-del@lms.local' in admin.get('/admin/ferpa').get_data(as_text=True)
    admin.post('/admin/ferpa', data={'request_id': rid, 'action': 'delete', 'confirm': 'wrong'})
    with app.app_context():
        assert mod.db.session.get(mod.User, uid).email == 'ferpa-del@lms.local'
    admin.post('/admin/ferpa', data={'request_id': rid, 'action': 'delete', 'confirm': 'ferpa-del@lms.local'})
    with app.app_context():
        gone = mod.db.session.get(mod.User, uid)
        assert gone.email.endswith('@anonymized.invalid') and not mod.Enrollment.query.filter_by(user_id=uid).first()
        assert mod.db.session.get(sr.DataRequest, rid).status == 'done'
        acts = [e.action for e in mod.AuditEvent.query.order_by(mod.AuditEvent.id.desc()).limit(20)]
        assert 'ferpa_delete' in acts and 'ferpa_request' in acts and 'ferpa_export' in acts
        assert sr.verify_chain()['ok']
    h = admin.get('/admin/audit-log?action=ferpa').get_data(as_text=True)
    assert 'intact' in h and 'ferpa_delete' in h
    c = admin.get('/admin/audit-log?format=csv').get_data(as_text=True)
    assert c.startswith('id,utc,actor_id,role,action,detail,path,ip,section_id,prev_hash,hash')
    with app.app_context():   # tamper → detected
        e = mod.AuditEvent.query.filter(mod.AuditEvent.hash.isnot(None)).order_by(mod.AuditEvent.id).first()
        old = e.detail
        e.detail = (old or '') + ' (edited)'; mod.db.session.commit()
        bad = sr.verify_chain()
        e.detail = old; mod.db.session.commit()
        assert not bad['ok'] and bad['broken_at'] == e.id and sr.verify_chain()['ok']
