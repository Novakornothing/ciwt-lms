"""Cybersecurity course: seed, five learning paths, labs, and the practice bank."""
import labs_sec
from curriculum_sec.exam_bank import as_bank_items
from curriculum_sec.render import CHAPTERS, lesson_count
from curriculum_v2.ladder import schema as S
from curriculum_v2.ladder.sections import sections


def _commands(lab):
    return [c for c in (lab.get('solution') or {}).get('vm_commands') or [] if c and len(c) > 8]


def _hint_blob(lab):
    parts = []
    coaching = lab.get('coaching') or {}
    parts.append(coaching.get('stage2') or '')
    parts.append(coaching.get('stage3') or '')
    parts.extend(lab.get('hints') or [])
    for hints in (lab.get('obj_hints') or {}).values():
        parts.extend(hints or [])
    return '\n'.join(parts)


def test_course_shape_and_five_paths():
    assert lesson_count() >= 40
    assert len(CHAPTERS) == 10
    from curriculum_v2.objectives import OBJECTIVES
    from curriculum_sec.objectives import SEC_OBJECTIVES
    from curriculum_v2.misconceptions import MISCONCEPTIONS
    import importlib
    objs = dict(OBJECTIVES)
    objs.update(SEC_OBJECTIVES)
    for ch in CHAPTERS:
        assert len(ch['lessons']) >= 4
        mod = importlib.import_module(f"curriculum_v2.ladder.sec.ch{ch['order']:02d}")
        errors, _warnings = S.validate_module(mod, objs, MISCONCEPTIONS, labs=None)
        assert errors == [], errors
        for les in ch['lessons']:
            assert 'data-skill="SEC-' in les['html']
            assert 'In plain English' in les['html']
            secs = sections(les['html'])
            assert len(secs) >= 3, les['title']
            label = f"{ch['order']}.{les['order']}"
            for sec in secs:
                ent = mod.LESSONS[label][sec['sid']]
                assert ent['type'] == 'section'
                for rung, kind in (('R1', 'plain'), ('R2', 'analogy'), ('R3', 'visual'), ('R4', 'try')):
                    assert ent['rungs'][rung]['kind'] == kind
                    assert ent['rungs'][rung]['checks']
                assert ent['checks']
                S.validate_against_lesson(les['title'], ent, sec['html'], sec['r0_sha'], errors, [])
            assert errors == [], errors


def test_twenty_labs_and_stage_two_three_hide_commands():
    labs = labs_sec.SEC_VM_LABS + labs_sec.SEC_ACTIVITY_LABS
    assert len(labs) == 20
    assert len({lab['id'] for lab in labs}) == 20
    for lab in labs:
        blob = _hint_blob(lab)
        for cmd in _commands(lab):
            assert cmd not in blob, (lab['id'], cmd)
        assert 'Stage 1' in lab['coaching']['stage1']
        assert 'Stage 2' in lab['coaching']['stage2']
        assert 'Stage 3' in lab['coaching']['stage3']


def test_practice_bank_size():
    items = as_bank_items()
    singles = [it for it in items if it['type'] == 'single']
    pbqs = [it for it in items if it['type'] in ('order', 'match')]
    assert len(singles) >= 120
    assert len(pbqs) >= 4
    assert len({it['id'] for it in items}) == len(items)


def test_sec_seed_enroll_lesson_lab_and_practice(student, instructor, admin, anon, mod):
    with mod.app.app_context():
        course = mod.Course.query.filter_by(code='SEC').one()
        assert course.title == 'Cybersecurity'
        assert 'ciwt' not in (course.description or '').lower()
        chapters = mod.Module.query.filter_by(course_id=course.id).count()
        lessons = mod.Lesson.query.join(mod.Module).filter(mod.Module.course_id == course.id).count()
        assert chapters == 10
        assert lessons >= 40
        student_row = mod.User.query.filter_by(email='student1@lms.local').one()
        section = mod.ClassSection.query.filter_by(course_id=course.id).first()
        assert section is not None
        assert mod.Enrollment.query.filter_by(user_id=student_row.id, section_id=section.id).first()
        lesson = mod.Lesson.query.join(mod.Module).filter(mod.Module.course_id == course.id).order_by(mod.Module.order, mod.Lesson.order).first()
        module = mod.db.session.get(mod.Module, lesson.module_id)
        sec_id, mod_id, les_id = section.id, module.id, lesson.id
    page = student.get(f'/student/module/{sec_id}/{mod_id}/lesson/{les_id}')
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert 'Plain English' in html and 'Try-It' in html
    assert 'data-step-rung="R1"' in html
    assert html.count('id="novakStepStyleBar"') == 1 and '5 Ways to Learn:' in html
    assert 'id="lessonRail"' in html and html.count('data-rail-rung=') == 5
    lab = student.get('/labs/sec-vm-perms')
    assert lab.status_code == 200
    assert 'Stage 2' in lab.get_data(as_text=True)
    assert 'labConfig' in lab.get_data(as_text=True)
    dash = student.get('/student')
    assert dash.status_code == 200
    assert 'Cybersecurity' in dash.get_data(as_text=True)
    started = student.post('/practice/start', data={'exam': 'S'})
    assert started.status_code in (302, 303)
    take = student.get(started.headers['Location'])
    assert take.status_code == 200
    body = take.get_data(as_text=True)
    assert 'Cybersecurity foundations practice' in body
    assert 'id="assessQuestions"' in body
    dash_html = dash.get_data(as_text=True)
    assert 'Course Chapters' in dash_html and 'Hands-On Labs' in dash_html and 'Practice Exams' in dash_html
    assert '>SEC<' not in dash_html and 'SEC ·' not in dash_html
    assert 'Cybersecurity' in instructor.get('/instructor').get_data(as_text=True)
    exports = admin.get('/admin/exports').get_data(as_text=True)
    assert 'Cybersecurity' in exports and '>SEC<' not in exports
    tour = anon.get('/demo/tour').get_data(as_text=True)
    assert 'Cybersecurity' in tour and 'Threats, access, firewalls' in tour
    found = student.get('/api/search?q=iptables').get_json()['command_card']
    assert found and any('sec-vm-iptables' in (p.get('url') or '') for p in found.get('practice') or [])
    aged = student.get('/api/search?q=chage').get_json()['command_card']
    assert aged and any('sec-vm-users' in (p.get('url') or '') for p in aged.get('practice') or [])
    hashed = student.get('/api/search?q=sha256sum').get_json()['command_card']
    assert hashed and any('sec-vm-hash' in (p.get('url') or '') for p in hashed.get('practice') or [])
    import command_cards as CC
    for query in ('iptables', 'sha256sum', 'chage', 'find -perm', 'ss', 'journalctl', 'grep Failed /var/log/auth.log'):
        card = CC.card_for(query)
        assert card, query
    import interactive_labs as IL
    ipt = CC.labs_using('iptables', IL.LABS)
    assert any(lab.get('id') == 'sec-vm-iptables' for lab in ipt)
    assert any(lab.get('id') == 'sec-vm-hash' for lab in CC.labs_using('sha256sum', IL.LABS))
    assert any(lab.get('id') == 'sec-vm-users' for lab in CC.labs_using('chage', IL.LABS))
    assert any(lab.get('id') == 'sec-vm-suid' for lab in CC.labs_using('find', IL.LABS))
    assert any(lab.get('id') == 'sec-vm-proc' for lab in CC.labs_using('ss', IL.LABS))
    assert any(lab.get('id') == 'sec-vm-authlog' for lab in CC.labs_using('journalctl', IL.LABS))
    assert any(lab.get('id') == 'sec-vm-authlog' for lab in CC.labs_using('grep', IL.LABS))
    import io
    import zipfile
    import scorm_xapi
    data, _mime, name = scorm_xapi.build_scorm_package_zip('SEC', '1.2')
    assert name.startswith('novak-lms-sec-')
    manifest = zipfile.ZipFile(io.BytesIO(data)).read('imsmanifest.xml').decode()
    assert '<title>Cybersecurity</title>' in manifest
    assert 'ile_cin' not in manifest and 'A-150' not in manifest and '>SEC<' not in manifest
