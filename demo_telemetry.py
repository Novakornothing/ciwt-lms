"""Rich, idempotent demo telemetry seeder for Novak LMS™ flagship dashboards.

Ensures that when an evaluator enters the 1-Click Student, Instructor, or Admin Demo on
Novak LMS™ (either locally or on Render's persistent /var/data/ciwt/ciwt_lms.db disk),
every flagship dashboard across ALL 5 sections (Sections 1, 2, 3, 4, and 5 CLIENT-101)
is populated with realistic, up-to-date activity:
1. Active ClassSection for Course 3 (CLIENT — Operating Systems — CLIENT-101)
2. "Who Needs Me" Co-Pilot (/instructor/section/<1..5>/who-needs-me) with active students needing
   attention today (exhausted ladder, repeated mix-up, lab habit) and recent activity timestamps.
3. Practice Exam & Speed-Drill (/instructor/section/<1..5>/exam-sim, /student/section/<1..5>/exam-sim,
   /portfolio) with Voucher Ready, Borderline, and Remediation sittings across FC0-U71, 220-1201, 220-1202,
   and N10-009, synced gradebook rows, and Leitner spaced-repetition Speed-Drill stats.
4. Institutional Outcomes (/admin/outcomes) & Gradebook across all 5 sections.
5. Helix MediaPipe 478-landmark attention sessions on ALL 5 sections (1, 2, 3, 4, 5).
6. TQI Convening Packets, EOC Surveys, Critiques, and Actions across ALL 5 sections (1, 2, 3, 4, 5).
"""
import json
import random
from datetime import timedelta


# Phase 1 plain-English names: existing demo rows were seeded with older feature names.
CLIENT_SECTION_NAME = 'Operating Systems Fall 2026 — Section E'

DEMO_TEXT_RENAMES = [('CLIENT-101 Lab & CompTIA Tech+', 'Operating Systems Lab & CompTIA Tech+'), ('Your CLIENT-101 Windows 11', 'Your Operating Systems Windows 11'), ('NETOPS Linux VM Routing', 'Basic Networking Linux VM Routing'), ('submitting the NETOPS labs', 'submitting the Basic Networking labs'), ('Demo EOC reaction for TQI packet.', 'Demo end-of-course survey comment.'), ('Exhausted explanation ladder on section 2', 'Tried all 5 ways on section 2'), ('Walk through Rung 2 analogy', 'Walk through the Analogy view'), ('Exam-Day Simulator — CompTIA A+ Core 1 & Core 2 Voucher Readiness', 'Practice Exams — CompTIA A+ Core 1 & Core 2 Exam Readiness'), ('in the Exam-Day Simulator', 'in Practice Exams'), ('Exam-Day Readiness Simulator', 'Practice Exams'), ('Exam-Day Simulator', 'Practice Exam'), ('Adaptive 4-Rung Ladders, Helix Attention & Live VMs', '5 Ways to Learn, Eye Tracking & Live VMs'), ('our 4-rung adaptive explanation ladder (Plain Language -> Analogy -> Visual Diagram -> Interactive Try-It)', '5 Ways to Learn (Standard, Plain English, Analogy, Visual, Try-It)'), ('opt-in Helix 478-landmark attention tracking', 'opt-in Eye Tracking'), ('The 4-rung adaptive explanations', 'The 5 Ways to Learn explanations'), ('The 4-rung explanation ladder (especially Rung 2 analogies and Rung 3 visual traces)', 'The 5 Ways to Learn (especially the Analogy and Visual views)'), ('Who Needs Me co-pilot and Helix attention heatmaps', 'Students Needing Help and Eye Tracking heatmaps'), ('took a few extra tries on the explanation ladder', 'took a few extra tries across the 5 Ways to Learn'), ('walking through Rung 3 (Visual step-by-step)', 'walking through the Visual view'), ('The Rung 2 analogies', 'The Analogy views'), ('Great work reaching Voucher Ready', 'Great work reaching Exam Ready'), ('final proctored voucher sitting', 'final proctored exam'), ('mastery and voucher-readiness benchmarks', 'mastery and exam-readiness benchmarks')]


def _plain(text):
    if not text:
        return text
    for a, b in DEMO_TEXT_RENAMES:
        text = text.replace(a, b)
    return text


def _mastery_models(A):
    mx = A.app.extensions.get('ciwt_mastery')
    if mx and hasattr(mx, 'models'):
        yield mx.models.MasteryCheckin, ('note', 'reasons_json')


def refresh_demo_text_names(A):
    """Rewrite seeded demo messages / critiques / survey comments to the current feature names. Idempotent."""
    n = 0
    for model, cols in ((A.StaffMessage, ('subject', 'body')), (A.TqiCritique, ('body',)),
                        (A.TqiAction, ('body',)), (A.TqiEocResponse, ('comment',))) + tuple(_mastery_models(A)):
        for row in model.query.all():
            for col in cols:
                old = getattr(row, col, None)
                new = _plain(old)
                if new != old:
                    setattr(row, col, new)
                    n += 1
    if n:
        A.db.session.commit()
    return n


def ensure_rich_demo_telemetry(app):
    """Idempotently populate or refresh rich demo telemetry on non-test databases."""
    with app.app_context():
        import app as A
        db = A.db
        User = A.User
        Course = A.Course
        ClassSection = A.ClassSection
        Enrollment = A.Enrollment
        Module = A.Module
        Lesson = A.Lesson
        Quiz = A.Quiz
        QuizAttempt = A.QuizAttempt
        KnowledgeTest = A.KnowledgeTest
        TestAttempt = A.TestAttempt
        ContentRelease = A.ContentRelease
        TimeLog = A.TimeLog
        LabCompletion = A.LabCompletion
        TqiPacket = A.TqiPacket
        TqiCritique = A.TqiCritique
        TqiEocResponse = A.TqiEocResponse
        TqiAction = A.TqiAction
        TQI_EOC_ITEMS = A.TQI_EOC_ITEMS
        utcnow = A.utcnow

        # Only run if the standard demo cohort exists
        instr1 = User.query.filter_by(email='instructor@lms.local').first()
        instr2 = User.query.filter_by(email='instructor2@lms.local').first() or instr1
        s1 = User.query.filter_by(email='student1@lms.local').first()
        if not instr1 or not s1:
            return {'ok': False, 'reason': 'no_demo_users'}

        now = utcnow()
        rnd = random.Random(20261025)

        # Scrub any legacy 'CIWT' / 'ciwt' strings in Course, Module, Lesson, Institution, and LabEvent rows
        for c_row in Course.query.all():
            if c_row.description and 'CIWT' in c_row.description:
                c_row.description = c_row.description.replace('CIWT', 'Novak LMS™')
        for m_row in Module.query.all():
            if m_row.content and 'CIWT' in m_row.content:
                m_row.content = m_row.content.replace('CIWT', 'Novak LMS™')
        for l_row in Lesson.query.all():
            if l_row.content and ('CIWT' in l_row.content or 'ciwt' in l_row.content):
                l_row.content = (l_row.content
                                 .replace('CIWT-W11-07', 'NOVAK-W11-07')
                                 .replace('CIWT-WIN-LAB', 'NOVAK-WIN-LAB')
                                 .replace(r'CIWT\Trainee', r'NOVAK\Trainee')
                                 .replace(r'ciwt\student', r'novak\student')
                                 .replace('All prior CIWT support chapters', 'All prior IT support chapters')
                                 .replace('CIWT', 'Novak LMS™'))
        inst_api = app.extensions.get('ciwt_institutional')
        if inst_api and hasattr(inst_api, 'Institution'):
            for inst_row in inst_api.Institution.query.all():
                if inst_row.name in ('CIWT', 'Novak Learning'):
                    inst_row.name = 'Novak LMS™'
        labs_api_0 = app.extensions.get('ciwt_lab_progress')
        if labs_api_0:
            for le_row in labs_api_0.LabEvent.query.filter(labs_api_0.LabEvent.action.ilike('%ciwt%')).all():
                le_row.action = le_row.action.replace('ciwt.internal', 'novak.internal').replace('ciwt.lab', 'novak.lab').replace('ciwt.local', 'novak.local')
        db.session.commit()

        # ------------------------------------------------------------------ 1. Course 3 (CLIENT-101) Active Section
        client_course = Course.query.filter_by(code='CLIENT').first()
        sec_client = None
        if client_course:
            sec_client = ClassSection.query.filter_by(course_id=client_course.id).first()
            if sec_client and sec_client.name != CLIENT_SECTION_NAME:
                sec_client.name = CLIENT_SECTION_NAME
                db.session.commit()
            if not sec_client:
                sec_client = ClassSection(
                    name=CLIENT_SECTION_NAME,
                    course_id=client_course.id,
                    instructor_id=instr1.id,
                    max_students=25,
                    is_active=True,
                    start_date=(now - timedelta(days=30)).date(),
                    end_date=(now + timedelta(days=90)).date(),
                )
                db.session.add(sec_client)
                db.session.flush()
            A.grant_section_instructor_access(sec_client.id, instr1.id, primary=True)
            demo_students = User.query.filter(User.email.like('student%@lms.local')).order_by(User.id).limit(14).all()
            for stu in demo_students:
                if not Enrollment.query.filter_by(user_id=stu.id, section_id=sec_client.id).first():
                    db.session.add(Enrollment(user_id=stu.id, section_id=sec_client.id,
                                              progress_percent=rnd.randint(45, 94)))
            for mod in Module.query.filter_by(course_id=client_course.id).all():
                if not ContentRelease.query.filter_by(section_id=sec_client.id, content_type='module', content_id=mod.id).first():
                    db.session.add(ContentRelease(
                        section_id=sec_client.id, content_type='module', content_id=mod.id,
                        is_active=True, available_from=now - timedelta(days=14),
                        available_until=now + timedelta(days=90),
                        activated_by=instr1.id, activated_at=now - timedelta(days=14),
                    ))
            db.session.commit()

        sec1 = db.session.get(ClassSection, 1)
        sec2 = db.session.get(ClassSection, 2)
        sec3 = db.session.get(ClassSection, 3)
        sec4 = db.session.get(ClassSection, 4)
        all_secs = [s for s in (sec1, sec2, sec3, sec4, sec_client) if s is not None]
        if not sec1 or not sec2:
            return {'ok': False, 'reason': 'missing_sections_1_2'}

        if not Enrollment.query.filter_by(user_id=s1.id, section_id=sec2.id).first():
            db.session.add(Enrollment(user_id=s1.id, section_id=sec2.id, progress_percent=78))
            db.session.commit()

        # Refresh TestAttempt timestamps if any are older than 6 days
        recent_cutoff = now - timedelta(days=5)
        old_attempts = TestAttempt.query.filter(TestAttempt.completed_at < recent_cutoff).all()
        if old_attempts:
            kt_map = {k.id: json.loads(k.questions or '[]') for k in KnowledgeTest.query.all()}
            struggler_uids = {u.id for u in User.query.filter(User.email.in_(['student3@lms.local', 'student4@lms.local', 'student5@lms.local', 'student6@lms.local', 'student7@lms.local', 'student8@lms.local'])).all()}
            for idx, ta in enumerate(old_attempts):
                age_hours = 4 + (idx * 3) % 96
                ta.completed_at = now - timedelta(hours=age_hours)
                ta.started_at = ta.completed_at - timedelta(minutes=42)
                qs = kt_map.get(ta.test_id) or []
                if qs and ta.user_id not in struggler_uids and ta.section_id in (1, 2, 4):
                    ans = {}
                    c_n = 0
                    for qi, q in enumerate(qs):
                        if (idx + qi) % 11 != 0:
                            ans[str(qi)] = q.get('correct')
                            c_n += 1
                        else:
                            wrong = [o for o in (q.get('options') or []) if o != q.get('correct')]
                            ans[str(qi)] = wrong[0] if wrong else q.get('correct')
                    ta.answers = json.dumps(ans)
                    ta.score = round(100.0 * c_n / len(qs), 1)
                    ta.passed = ta.score >= 80
            db.session.commit()

        from curriculum_v2.depth_wave1 import ensure_wave1_db_assessments
        ensure_wave1_db_assessments(db, Course, Module, Quiz, KnowledgeTest, TestAttempt)

        # Ensure Course 3 (CLIENT) has Knowledge Test A, B, C (orders 1, 2, 3) so Gradebook 'Knowledge tests (70%)' is populated
        if client_course and not KnowledgeTest.query.filter_by(course_id=client_course.id, order=1).first():
            from question_bank import tests_aplus
            from curriculum_v2.itsup_core import EXPANSION
            from curriculum_v2.exam_supplement import SUPPLEMENT
            cl_pool = [dict(q) for q in (list(EXPANSION) + list(SUPPLEMENT))
                       if str(q.get('obj', '')).startswith('IT-') and int(q['obj'].split('-')[1].split('.')[0]) >= 8]
            for _t, _d, _o, f_qs in tests_aplus():
                for q in f_qs:
                    if q.get('text') not in {x.get('text') for x in cl_pool}:
                        cl_pool.append(dict(q))
            forms = [
                ('Operating Systems Knowledge Test A', 'Scenario-based items across Windows client OS, cross-platform Linux/macOS, endpoint security, and software troubleshooting. 45 questions. Passing score 80%.', 1, cl_pool[:45]),
                ('Operating Systems Knowledge Test B', 'Scenario-based items across Windows client OS, cross-platform Linux/macOS, endpoint security, and software troubleshooting. 45 questions. Passing score 80%.', 2, cl_pool[15:60]),
                ('Operating Systems Knowledge Test C', 'Scenario-based items across Windows client OS, cross-platform Linux/macOS, endpoint security, and software troubleshooting. 45 questions. Passing score 80%.', 3, cl_pool[30:75]),
            ]
            for title, desc, order, qs_form in forms:
                db.session.add(KnowledgeTest(
                    course_id=client_course.id, title=title, description=desc, order=order,
                    questions=json.dumps(qs_form), passing_score=80, time_limit_minutes=75,
                ))
            db.session.commit()

        # Ensure every KnowledgeTest (both written Knowledge Tests A/B/C and Skills Midterm/Final) is released and has TestAttempts across ALL 5 sections
        for sec in all_secs:
            sec_tests = KnowledgeTest.query.filter_by(course_id=sec.course_id).order_by(KnowledgeTest.order).all()
            sec_enrolled = Enrollment.query.filter_by(section_id=sec.id).all()
            for ti, test in enumerate(sec_tests):
                rel = ContentRelease.query.filter_by(section_id=sec.id, content_type='test', content_id=test.id, user_id=None).first()
                if not rel:
                    db.session.add(ContentRelease(
                        section_id=sec.id, content_type='test', content_id=test.id, user_id=None,
                        is_active=True, available_from=now - timedelta(days=14),
                        available_until=now + timedelta(days=90),
                        activated_by=sec.instructor_id, activated_at=now - timedelta(days=14),
                    ))
                elif not rel.is_active:
                    rel.is_active = True
                if TestAttempt.query.filter_by(section_id=sec.id, test_id=test.id).count() > 0:
                    continue
                qs = json.loads(test.questions or '[]')
                for ei, enr in enumerate(sec_enrolled):
                    is_strug = ei in (2, 3, 4)
                    comp_at = now - timedelta(hours=4 + ei * 2 + ti * 6)
                    if isinstance(qs, dict) and qs.get('kind') == 'practical':
                        score = round(rnd.uniform(70.0, 78.0) if is_strug else rnd.uniform(86.0, 98.0), 1)
                        db.session.add(TestAttempt(
                            user_id=enr.user_id, test_id=test.id, section_id=sec.id,
                            answers=json.dumps({'practical': True}), score=score, passed=score >= 80,
                            started_at=comp_at - timedelta(minutes=38), completed_at=comp_at,
                        ))
                    elif isinstance(qs, list) and qs:
                        target_p = 0.65 if is_strug else 0.90
                        ans = {}
                        c_n = 0
                        for qi, q in enumerate(qs):
                            if not isinstance(q, dict):
                                continue
                            if rnd.random() < target_p:
                                ans[str(qi)] = q.get('correct')
                                c_n += 1
                            else:
                                wrong = [o for o in (q.get('options') or []) if o != q.get('correct')]
                                ans[str(qi)] = wrong[0] if wrong else q.get('correct')
                        score = round(100.0 * c_n / len(qs), 1)
                        db.session.add(TestAttempt(
                            user_id=enr.user_id, test_id=test.id, section_id=sec.id,
                            answers=json.dumps(ans), score=score, passed=score >= 80,
                            started_at=comp_at - timedelta(minutes=42), completed_at=comp_at,
                        ))
            db.session.commit()
            gb_api = app.extensions.get('ciwt_gradebook')
            if gb_api and hasattr(gb_api, 'invalidate'):
                gb_api.invalidate(sec.id)

        # Ensure every enrolled student in ALL 5 sections has a recent study TimeLog within last 1-4 days
        for sec in all_secs:
            first_les = (Lesson.query.join(Module, Module.id == Lesson.module_id)
                         .filter(Module.course_id == sec.course_id)
                         .order_by(Module.order, Lesson.order).first())
            if not first_les:
                continue
            enrolled_uids = [e.user_id for e in Enrollment.query.filter_by(section_id=sec.id).all()]
            for idx, uid in enumerate(enrolled_uids):
                latest_tl = (TimeLog.query.filter_by(user_id=uid, section_id=sec.id, kind='study')
                             .order_by(TimeLog.ended_at.desc()).first())
                if not latest_tl or not latest_tl.ended_at or latest_tl.ended_at < recent_cutoff:
                    ended = now - timedelta(hours=2 + (idx * 4) % 72)
                    secs = rnd.randint(2400, 7800)
                    db.session.add(TimeLog(
                        user_id=uid, section_id=sec.id, lesson_id=first_les.id,
                        kind='study', seconds=secs,
                        started_at=ended - timedelta(seconds=secs), ended_at=ended,
                    ))
        db.session.commit()

        # ------------------------------------------------------------------ 2. Helix Attention across ALL 5 sections
        HelixGazeSession = A.HelixGazeSession
        HelixConsent = A.HelixConsent
        from helix.models import POLICY_VERSION
        legacy_hx = HelixGazeSession.query.filter_by(is_demo=True, mode='gaze', engine='webgazer').all()
        for idx, s in enumerate(legacy_hx):
            acc = 82 + (idx * 3) % 12
            err_px = int(36 + (100 - acc) * 2.1)
            s.engine = 'mediapipe'
            s.delegate = 'GPU'
            s.calibration_score = acc
            s.validation_error_px = err_px
            s.validation_error_deg = round(err_px / 32.0, 2)
            s.validation_precision_px = int(16 + (100 - acc) * 0.9)
            s.distance_cm = 56 + (idx % 9)
            s.aoi_resolution = 'paragraph' if acc >= 84 else 'heading'
            s.orientation = 'landscape-primary'
            s.implicit_samples = 8 + (idx % 11)
            s.started_at = now - timedelta(hours=6 + (idx * 2) % 60)
            s.ended_at = s.started_at + timedelta(milliseconds=s.total_ms or 180000)
            s.last_seen_at = s.ended_at
        db.session.commit()

        for sec in all_secs:
            if HelixGazeSession.query.filter_by(section_id=sec.id).count() == 0:
                sec_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                .filter(Enrollment.section_id == sec.id, User.role == 'student')
                                .order_by(User.id).limit(8).all())
                A._seed_helix_demo(sec, sec_students)

        s2_user = User.query.filter_by(email='student2@lms.local').first()
        s2_uid = s2_user.id if s2_user else -1
        hx_uids = {r.user_id for r in HelixGazeSession.query.filter_by(is_demo=True).all()} - {s2_uid}
        for uid in hx_uids:
            c = HelixConsent.query.filter_by(user_id=uid, revoked_at=None).first()
            if not c:
                db.session.add(HelixConsent(user_id=uid, policy_version=POLICY_VERSION, camera_ok=True, passive_ok=True))
            elif c.policy_version != POLICY_VERSION:
                c.policy_version = POLICY_VERSION
        db.session.commit()

        # ------------------------------------------------------------------ 3. 4-Rung Ladder States across ALL 5 sections
        from curriculum_v2 import ladder as LD
        from curriculum_v2.ladder import sections as LSEC
        from mastery.ladder import define_ladder_models
        LM = define_ladder_models(db)
        LadderState, LadderEvent = LM.LadderState, LM.LadderEvent

        for sec in all_secs:
            if LadderState.query.filter_by(section_id=sec.id).count() > 0:
                continue
            code = sec.course.code if sec.course else 'ITSUP'
            enrolled = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                        .filter(Enrollment.section_id == sec.id, User.role == 'student')
                        .order_by(User.id).all())
            lessons_by_lbl = {}
            for m_row in Module.query.filter_by(course_id=sec.course_id).all():
                for l_row in Lesson.query.filter_by(module_id=m_row.id).all():
                    lbl = LSEC.lesson_label(l_row.title)
                    if lbl:
                        lessons_by_lbl[lbl] = l_row.id
                    lessons_by_lbl.setdefault(f'{m_row.order}.{l_row.order}', l_row.id)
            target_lbls = ('8.1', '8.2', '9.1', '10.1') if code == 'CLIENT' else ('1.1', '1.2', '1.3', '2.1', '2.2')
            entries = [(k, v) for k, v in sorted(LD.ladder().items())
                       if k[0] == code and v.get('type') == 'section' and k[1] in target_lbls]
            if not entries:
                continue
            rungs_cycle = ['R1', 'R2', 'R1', 'R3', 'R2', 'R4', 'R1', 'R3', 'R2', 'R1']
            for si, stu in enumerate(enrolled[:14]):
                for ei, ((_c, lbl, sid), ent) in enumerate(entries[:4]):
                    lid = lessons_by_lbl.get(lbl)
                    is_exhausted = (si in (2, 4) and ei == 1)
                    if is_exhausted:
                        tried = ['R0', 'R1', 'R2', 'R3', 'R4']
                        t_at = now - timedelta(hours=3 + si)
                        st_row = LadderState(
                            user_id=stu.id, section_id=sec.id, course=code, label=lbl, sid=sid,
                            lesson_id=lid, current='R4', tried_json=json.dumps(tried),
                            resolved=None, misses=3, requests=2, adapted=False,
                            exhausted_at=t_at, created_at=t_at - timedelta(minutes=18), updated_at=t_at,
                        )
                        db.session.add(st_row)
                        chks = LD.rung_checks(ent, 'R0')
                        chk = chks[0] if chks else {'id': f'L-{code}-{lbl}-{sid}-R0-0', 'options': ['a', 'b'], 'correct': 'a', 'mc': {}}
                        wrong_opt = next((o for o in chk['options'] if o != chk['correct']), chk['options'][0])
                        mc_tag = (chk.get('mc') or {}).get(wrong_opt)
                        db.session.add(LadderEvent(
                            user_id=stu.id, section_id=sec.id, course=code, label=lbl, sid=sid,
                            kind='check', rung='R0', check_id=chk['id'], answer=wrong_opt[:400],
                            correct=False, mc=mc_tag, created_at=t_at - timedelta(minutes=10),
                        ))
                        for r_step in ('R1', 'R2', 'R3', 'R4'):
                            db.session.add(LadderEvent(
                                user_id=stu.id, section_id=sec.id, course=code, label=lbl, sid=sid,
                                kind='request', rung=r_step, source='button', from_rung='R0',
                                created_at=t_at - timedelta(minutes=5),
                            ))
                        db.session.add(LadderEvent(
                            user_id=stu.id, section_id=sec.id, course=code, label=lbl, sid=sid,
                            kind='exhausted', rung='R4', created_at=t_at,
                        ))
                    else:
                        target_r = rungs_cycle[(si + ei) % len(rungs_cycle)]
                        order_r = ['R0', 'R1', 'R2', 'R3', 'R4']
                        tried = order_r[:order_r.index(target_r) + 1]
                        t_at = now - timedelta(hours=8 + (si * 2 + ei) % 48)
                        st_row = LadderState(
                            user_id=stu.id, section_id=sec.id, course=code, label=lbl, sid=sid,
                            lesson_id=lid, current=target_r, tried_json=json.dumps(tried),
                            resolved=target_r, misses=1, requests=max(0, len(tried) - 2),
                            adapted=False, exhausted_at=None,
                            created_at=t_at - timedelta(minutes=12), updated_at=t_at,
                        )
                        db.session.add(st_row)
                        chks = LD.rung_checks(ent, 'R0')
                        if chks:
                            chk0 = chks[0]
                            wrong_opt = next((o for o in chk0['options'] if o != chk0['correct']), chk0['options'][0])
                            mc_tag = (chk0.get('mc') or {}).get(wrong_opt)
                            db.session.add(LadderEvent(
                                user_id=stu.id, section_id=sec.id, course=code, label=lbl, sid=sid,
                                kind='check', rung='R0', check_id=chk0['id'], answer=wrong_opt[:400],
                                correct=False, mc=mc_tag, created_at=t_at - timedelta(minutes=8),
                            ))
                        for r_step in tried[1:]:
                            db.session.add(LadderEvent(
                                user_id=stu.id, section_id=sec.id, course=code, label=lbl, sid=sid,
                                kind='request', rung=r_step, source='helix' if r_step == 'R1' and si % 3 == 0 else 'button',
                                from_rung='R0', created_at=t_at - timedelta(minutes=4),
                            ))
                        db.session.add(LadderEvent(
                            user_id=stu.id, section_id=sec.id, course=code, label=lbl, sid=sid,
                            kind='resolved', rung=target_r, created_at=t_at,
                        ))
        db.session.commit()

        # ------------------------------------------------------------------ 4. Quizzes & Active Misconceptions across ALL 5 sections
        from curriculum_v2 import misconceptions as MCS
        for sec in all_secs:
            if QuizAttempt.query.filter_by(section_id=sec.id).count() > 0:
                continue
            enrolled = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                        .filter(Enrollment.section_id == sec.id, User.role == 'student')
                        .order_by(User.id).all())
            quizzes = (Quiz.query.join(Module, Module.id == Quiz.module_id)
                       .filter(Module.course_id == sec.course_id)
                       .order_by(Module.order, Quiz.id).limit(9).all())
            for qi, qz in enumerate(quizzes):
                q_items = json.loads(qz.questions or '[]')
                if not q_items:
                    continue
                for si, stu in enumerate(enrolled[:18]):
                    struggler = si in (2, 3, 4) and qi == 0
                    answers = {}
                    correct_n = 0
                    for idx, it in enumerate(q_items):
                        if not struggler and rnd.random() < 0.94:
                            answers[str(idx)] = it['correct']
                            correct_n += 1
                        else:
                            tagged = [dd for (b_id, dd) in MCS.TAGS if b_id == it.get('bank_id')]
                            wrong = tagged[0] if tagged else next((o for o in it['options'] if o != it['correct']), it['correct'])
                            answers[str(idx)] = wrong
                            if wrong == it['correct']:
                                correct_n += 1
                    score = round(100.0 * correct_n / len(q_items), 1)
                    completed = now - timedelta(hours=3 + si + qi * 6)
                    db.session.add(QuizAttempt(
                        user_id=stu.id, quiz_id=qz.id, section_id=sec.id,
                        answers=json.dumps(answers), score=score,
                        completed_at=completed,
                    ))
                    if struggler and qi == 0:
                        db.session.add(QuizAttempt(
                            user_id=stu.id, quiz_id=qz.id, section_id=sec.id,
                            answers=json.dumps(answers), score=score,
                            completed_at=now - timedelta(hours=1, minutes=15 + si * 5),
                        ))
        db.session.commit()

        # ------------------------------------------------------------------ 5. Interactive & Real Linux VM Labs across ALL 5 sections
        labs_api = app.extensions.get('ciwt_lab_progress')
        if labs_api:
            LP, LE = labs_api.LabProgress, labs_api.LabEvent
            lab_specs = [
                (sec1, 'linux-vm-perms', ['boot', 'mkdir', 'note', 'perms', 'owner', 'script', 'verified'], [
                    ('vm', 'stat -c "%a %U:%G" /srv/drop && ls -la /srv/drop', 'ok', ['boot', 'mkdir', 'note']),
                    ('vm', 'chmod 640 /srv/drop/note.txt && chown root:ops /srv/drop/note.txt && chmod 750 /srv/drop/run.sh', 'ok', ['perms', 'owner', 'script']),
                    ('vm', 'ls -la /srv/drop && stat /srv/drop/note.txt', 'ok', ['verified']),
                    ('complete', 'all objectives met', 'ok', []),
                ]),
                (sec1, 'linux-vm-dns', ['boot', 'diagnose', 'client', 'listen', 'record', 'mx', 'forward', 'verify'], [
                    ('vm', 'cat /etc/resolv.conf && ss -ulpn && dig @127.0.0.1 novak.internal', 'ok', ['boot', 'diagnose', 'client']),
                    ('vm', 'sed -i "s/127.0.0.1/0.0.0.0/" /etc/dnsmasq.conf && service dnsmasq restart', 'ok', ['listen', 'record', 'mx', 'forward']),
                    ('vm', 'dig @127.0.0.1 mail.novak.internal MX && nslookup intranet.novak.internal', 'ok', ['verify']),
                    ('complete', 'all objectives met', 'ok', []),
                ]),
                (sec1, 'win-ipconfig', ['run_hostname', 'run_ipconfig'], [
                    ('cmd', 'hostname', 'ok', ['run_hostname']),
                    ('cmd', 'ipconfig /all', 'ok', ['run_ipconfig']),
                    ('complete', 'all objectives met', 'ok', []),
                ]),
                (sec2, 'linux-vm-netclient', ['boot', 'diagnose', 'lease', 'route', 'dns', 'hosts', 'reach', 'neigh'], [
                    ('vm', 'ip addr show && ip route show && cat /etc/resolv.conf', 'ok', ['boot', 'diagnose']),
                    ('vm', 'udhcpc -i eth0 && ip route add default via 10.42.0.1 && echo "nameserver 10.42.0.1" > /etc/resolv.conf', 'ok', ['lease', 'route', 'dns', 'hosts']),
                    ('vm', 'ping -c 1 10.42.0.1 && ip neigh show', 'ok', ['reach', 'neigh']),
                    ('complete', 'all objectives met', 'ok', []),
                ]),
                (sec2, 'sw-vlan-access', ['enable', 'vlan20', 'access', 'verify'], [
                    ('cmd', 'show vlan brief', 'ok', ['enable']),
                    ('cmd', 'vlan 20', 'ok', ['vlan20']),
                    ('cmd', 'switchport access vlan 20', 'ok', ['access']),
                    ('cmd', 'show vlan brief', 'ok', ['verify']),
                    ('complete', 'all objectives met', 'ok', []),
                ]),
            ]
            if sec3:
                lab_specs.append((sec3, 'win-ipconfig', ['run_hostname', 'run_ipconfig'], [
                    ('cmd', 'hostname', 'ok', ['run_hostname']),
                    ('cmd', 'ipconfig /all', 'ok', ['run_ipconfig']),
                    ('complete', 'all objectives met', 'ok', []),
                ]))
            if sec4:
                lab_specs.append((sec4, 'sw-vlan-access', ['enable', 'vlan20', 'access', 'verify'], [
                    ('cmd', 'show vlan brief', 'ok', ['enable']),
                    ('cmd', 'vlan 20', 'ok', ['vlan20']),
                    ('cmd', 'switchport access vlan 20', 'ok', ['access']),
                    ('cmd', 'show vlan brief', 'ok', ['verify']),
                    ('complete', 'all objectives met', 'ok', []),
                ]))
            if sec_client:
                lab_specs.extend([
                    (sec_client, 'w11-inventory', ['hostname', 'ver', 'ram', 'bios'], [
                        ('cmd', 'hostname', 'ok', ['hostname']),
                        ('cmd', 'systeminfo', 'ok', ['ver', 'ram', 'bios']),
                        ('complete', 'all objectives met', 'ok', []),
                    ]),
                    (sec_client, 'linux-vm-users', ['boot', 'group', 'users', 'firstlogin', 'share', 'sudo', 'leaver', 'verify'], [
                        ('vm', 'cat /etc/group && id jdoe', 'ok', ['boot', 'group', 'users']),
                        ('vm', 'chmod 2770 /srv/helpdesk && usermod -L jdoe && visudo -c', 'ok', ['firstlogin', 'share', 'sudo', 'leaver']),
                        ('vm', 'ls -ld /srv/helpdesk && sudo -l -U ana', 'ok', ['verify']),
                        ('complete', 'all objectives met', 'ok', []),
                    ]),
                    (sec_client, 'w11-services', ['list', 'find', 'start', 'verify'], [
                        ('cmd', 'Get-Service', 'ok', ['list', 'find']),
                        ('cmd', 'Start-Service Spooler', 'ok', ['start']),
                        ('cmd', 'Get-Service Spooler', 'ok', ['verify']),
                        ('complete', 'all objectives met', 'ok', []),
                    ]),
                ])

            for sec, lab_id, done_objs, ev_list in lab_specs:
                if not sec or LabCompletion.query.filter_by(section_id=sec.id, lab_id=lab_id).count() > 0:
                    continue
                enrolled = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                            .filter(Enrollment.section_id == sec.id, User.role == 'student')
                            .order_by(User.id).limit(12).all())
                for si, stu in enumerate(enrolled):
                    comp_at = now - timedelta(hours=5 + si * 3)
                    is_lab_struggler = (si == 3 and lab_id in ('win-ipconfig', 'sw-vlan-access', 'w11-inventory'))
                    existing_lp = LP.query.filter_by(user_id=stu.id, lab_id=lab_id).first()
                    if is_lab_struggler:
                        if not existing_lp:
                            lp = LP(
                                user_id=stu.id, lab_id=lab_id, state_json='{}',
                                done_json=json.dumps(done_objs[:1]), transcript_json='[]', undo_json='[]',
                                section_id=sec.id, score=25.0, best_score=25.0, actions=6, wrong=5, hints_used=3, resets=1,
                                started_at=comp_at - timedelta(minutes=18), updated_at=now - timedelta(hours=2),
                                completed_at=None,
                            )
                            db.session.add(lp)
                            bad_cmds = ['fix network', 'reset all', 'ipconfig --fix-now', 'netsh magic', 'repair dns']
                            for seq_i, bcmd in enumerate(bad_cmds, 1):
                                db.session.add(LE(
                                    user_id=stu.id, lab_id=lab_id, attempt=2, seq=seq_i,
                                    at=now - timedelta(hours=2, minutes=10 - seq_i),
                                    kind='cmd', action=bcmd, outcome='unknown', newly=None, score=25.0,
                                ))
                    else:
                        if not existing_lp:
                            lp = LP(
                                user_id=stu.id, lab_id=lab_id, state_json='{}',
                                done_json=json.dumps(done_objs), transcript_json='[]', undo_json='[]',
                                section_id=sec.id, score=100.0, best_score=100.0, actions=len(ev_list), wrong=0, hints_used=0, resets=0,
                                started_at=comp_at - timedelta(minutes=14), updated_at=comp_at,
                                completed_at=comp_at,
                            )
                            db.session.add(lp)
                            for seq_i, (k, act, outc, newly_list) in enumerate(ev_list, 1):
                                db.session.add(LE(
                                    user_id=stu.id, lab_id=lab_id, attempt=1, seq=seq_i,
                                    at=comp_at - timedelta(minutes=10 - seq_i * 2),
                                    kind=k, action=act, outcome=outc,
                                    newly=json.dumps(newly_list) if newly_list else None, score=100.0,
                                ))
                        if not LabCompletion.query.filter_by(user_id=stu.id, lab_id=lab_id, section_id=sec.id).first():
                            db.session.add(LabCompletion(
                                user_id=stu.id, lab_id=lab_id, section_id=sec.id, completed_at=comp_at,
                            ))
            db.session.commit()

        # ------------------------------------------------------------------ 6. Practice Exam & Speed-Drill across ALL 5 sections
        es_api = app.extensions.get('ciwt_exam_sim')
        if es_api:
            from curriculum_v2.cert import exam_sim as ES, speed_drill as SD
            ESA, ESG, ESD = es_api.Attempt, es_api.Grade, es_api.Accommodation
            b = ES.P.bank()

            def _seed_sitting(user, section, exam_key, mode, target_ratio, hours_ago, strict=True):
                chosen = ES.build_form(exam_key, mode, rng=random.Random(f'{user.id}:{section.id}:{exam_key}:{mode}'))
                answers = {}
                for i, (iid, _oid) in enumerate(chosen):
                    it = b.get(iid)
                    if not it:
                        continue
                    want_right = (random.Random(f'{user.id}:{section.id}:{i}:{exam_key}').random() < target_ratio)
                    t = it['type']
                    if want_right:
                        if t == 'single':
                            answers[str(i)] = str(it['correct'])
                        else:
                            answers[str(i)] = json.dumps([str(c) for c in it['correct']])
                    else:
                        if t == 'single':
                            wrong = [o for o in it['options'] if o != it['correct']]
                            answers[str(i)] = str(wrong[0] if wrong else it['correct'])
                        elif t == 'multi':
                            wrong = [o for o in it['options'] if o not in it['correct']]
                            answers[str(i)] = json.dumps([str(x) for x in (wrong[:2] if wrong else it['correct'])])
                        else:
                            answers[str(i)] = json.dumps([str(c) for c in reversed(list(it['correct']))])
                correct_n = sum(1 for i, (iid, _o) in enumerate(chosen) if iid in b and ES.P.grade(b[iid], answers.get(str(i))))
                earned, possible = ES.earned_and_possible(chosen, answers, b)
                score = ES.scaled(earned, possible)
                by_dom = {}
                for i, (iid, oid) in enumerate(chosen):
                    it = b.get(iid)
                    if not it:
                        continue
                    dom = ES.OBJECTIVES[oid]['domain']
                    d = by_dom.setdefault(dom, [0, 0])
                    d[1] += 1
                    if ES.P.grade(it, answers.get(str(i))):
                        d[0] += 1
                dom_pcts = [round(100 * c / tot) if tot else 0 for c, tot in by_dom.values()]
                badge = ES.readiness(score, exam_key, dom_pcts)
                sub_at = now - timedelta(hours=hours_ago)
                att = ESA(
                    user_id=user.id, section_id=section.id, exam=exam_key, mode=mode,
                    strict=strict, items=json.dumps(chosen), answers=json.dumps(answers),
                    flags=json.dumps([0, 3]), started_at=sub_at - timedelta(minutes=52),
                    deadline=sub_at + timedelta(minutes=38), submitted_at=sub_at,
                    timed_out=False, score=score, correct=correct_n, total=len(chosen),
                    badge=badge, domains=json.dumps(by_dom),
                )
                db.session.add(att)
                db.session.flush()
                g = ESG.query.filter_by(section_id=section.id, user_id=user.id, exam=exam_key).first()
                if not g:
                    g = ESG(section_id=section.id, user_id=user.id, exam=exam_key)
                    db.session.add(g)
                g.attempt_id = att.id
                g.score = att.score
                g.pct = round(max(0, (att.score or 100) - 100) / 8, 1)
                g.status = ES.VOUCHER_STATUS.get(att.badge, '')
                g.synced_at = sub_at
                return att

            # Section 1 (ITSUP A)
            if ESA.query.filter_by(section_id=sec1.id).count() == 0:
                sec1_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                 .filter(Enrollment.section_id == sec1.id, User.role == 'student')
                                 .order_by(User.id).all())
                if sec1_students:
                    _seed_sitting(sec1_students[0], sec1, 'A1', 'full', 0.91, hours_ago=14, strict=True)
                    _seed_sitting(sec1_students[0], sec1, 'A2', 'full', 0.88, hours_ago=6, strict=True)
                ratios_s1 = [0.90, 0.86, 0.56, 0.52, 0.74, 0.58, 0.89, 0.76, 0.92, 0.85, 0.64, 0.88]
                for idx, stu in enumerate(sec1_students[1:13], 1):
                    r = ratios_s1[(idx - 1) % len(ratios_s1)]
                    _seed_sitting(stu, sec1, 'A1', 'full', r, hours_ago=4 + idx * 3, strict=(idx % 2 == 0))
                    if idx % 2 == 0:
                        _seed_sitting(stu, sec1, 'A2', 'full', min(0.94, r + 0.04), hours_ago=2 + idx * 2, strict=True)
                if len(sec1_students) > 4 and not ESD.query.filter_by(section_id=sec1.id).first():
                    db.session.add(ESD(section_id=sec1.id, user_id=sec1_students[4].id, multiplier=1.5))

            # Section 2 (NETOPS B)
            if ESA.query.filter_by(section_id=sec2.id).count() == 0:
                sec2_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                 .filter(Enrollment.section_id == sec2.id, User.role == 'student')
                                 .order_by(User.id).all())
                ratios_s2 = [0.91, 0.87, 0.55, 0.51, 0.76, 0.60, 0.89, 0.77, 0.93, 0.84]
                for idx, stu in enumerate(sec2_students[:10]):
                    r = ratios_s2[idx % len(ratios_s2)]
                    _seed_sitting(stu, sec2, 'N', 'full', r, hours_ago=3 + idx * 4, strict=True)
                if len(sec2_students) > 3 and not ESD.query.filter_by(section_id=sec2.id).first():
                    db.session.add(ESD(section_id=sec2.id, user_id=sec2_students[3].id, multiplier=1.25))

            # Section 3 (ITSUP C)
            if sec3 and ESA.query.filter_by(section_id=sec3.id).count() == 0:
                sec3_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                 .filter(Enrollment.section_id == sec3.id, User.role == 'student')
                                 .order_by(User.id).all())
                ratios_s3 = [0.89, 0.73, 0.58, 0.91, 0.85, 0.62, 0.88, 0.76]
                for idx, stu in enumerate(sec3_students[:8]):
                    r = ratios_s3[idx % len(ratios_s3)]
                    _seed_sitting(stu, sec3, 'A1', 'full', r, hours_ago=5 + idx * 3, strict=True)

            # Section 4 (NETOPS D)
            if sec4 and ESA.query.filter_by(section_id=sec4.id).count() == 0:
                sec4_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                 .filter(Enrollment.section_id == sec4.id, User.role == 'student')
                                 .order_by(User.id).all())
                ratios_s4 = [0.90, 0.86, 0.57, 0.75, 0.88, 0.61, 0.92, 0.84]
                for idx, stu in enumerate(sec4_students[:8]):
                    r = ratios_s4[idx % len(ratios_s4)]
                    _seed_sitting(stu, sec4, 'N', 'full', r, hours_ago=4 + idx * 3, strict=True)

            # Section 5 (CLIENT-101 — CompTIA Tech+ FC0-U71 & A+ Core 2 220-1202)
            if sec_client and ESA.query.filter_by(section_id=sec_client.id).count() == 0:
                sec5_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                 .filter(Enrollment.section_id == sec_client.id, User.role == 'student')
                                 .order_by(User.id).all())
                if sec5_students:
                    # Student1 Demo gets a Voucher Ready sitting on CompTIA Tech+ (FC0-U71) and A+ Core 2 (220-1202)
                    _seed_sitting(sec5_students[0], sec_client, 'T', 'full', 0.92, hours_ago=10, strict=True)
                    _seed_sitting(sec5_students[0], sec_client, 'A2', 'full', 0.89, hours_ago=18, strict=True)
                ratios_s5 = [0.91, 0.86, 0.56, 0.53, 0.72, 0.61, 0.90, 0.74, 0.93, 0.85]
                for idx, stu in enumerate(sec5_students[1:11], 1):
                    r = ratios_s5[(idx - 1) % len(ratios_s5)]
                    _seed_sitting(stu, sec_client, 'T', 'full', r, hours_ago=3 + idx * 3, strict=(idx % 2 == 0))
                    if idx % 2 == 0:
                        _seed_sitting(stu, sec_client, 'A2', 'full', min(0.94, r + 0.05), hours_ago=2 + idx * 2, strict=True)
                if len(sec5_students) > 3 and not ESD.query.filter_by(section_id=sec_client.id).first():
                    db.session.add(ESD(section_id=sec_client.id, user_id=sec5_students[3].id, multiplier=1.5))

            db.session.commit()

        # Seed Speed-Drill Leitner stats for student1
        SpeedDrillStat = getattr(A, 'SpeedDrillStat', None)
        if SpeedDrillStat is not None and SpeedDrillStat.query.count() == 0:
            from curriculum_v2.cert import speed_drill as SD
            for idx, card in enumerate(SD.CARDS[:42]):
                box = 5 if idx < 18 else (4 if idx < 30 else (2 if idx < 38 else 1))
                seen = 4 + (idx % 5)
                right = seen if box >= 4 else max(1, seen - 2)
                db.session.add(SpeedDrillStat(
                    user_id=s1.id, card_id=card['id'], box=box, seen=seen, right=right,
                    best_streak=19 if idx == 0 else (8 + idx % 9),
                    updated_at=now - timedelta(hours=2 + idx % 24),
                ))
            db.session.commit()

        # ------------------------------------------------------------------ 7. TQI Packets, EOC Surveys & Critiques for ALL 5 sections
        keys = [k for k, _g, _l in TQI_EOC_ITEMS]
        eoc_comments = [
            'The 5 Ways to Learn explanations and real Linux VM labs made troubleshooting click immediately.',
            'Hands-on Windows 11 PowerShell and Cisco IOS labs matched the daily objectives well.',
            'Practice Exam PBQs and the 98-card Speed-Drill were great preparation for certification.',
            'Clear pacing and strong lab feedback on Diagnose -> Fix -> Verify habits.',
        ]
        for sec in all_secs:
            pkt = TqiPacket.query.filter_by(section_id=sec.id).first()
            if not pkt:
                pkt = TqiPacket(
                    section_id=sec.id,
                    status='ready',
                    closeout_note='Convening packet verified: EOC reaction, item analysis, and lab process telemetry reviewed.',
                    auto_ready_at=now - timedelta(hours=4),
                )
                db.session.add(pkt)
            elif not pkt.closeout_note:
                pkt.closeout_note = 'Convening packet verified: EOC reaction, item analysis, and lab process telemetry reviewed.'
                if pkt.status == 'open':
                    pkt.status = 'ready'

            if TqiEocResponse.query.filter_by(section_id=sec.id).count() == 0:
                sec_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                .filter(Enrollment.section_id == sec.id, User.role == 'student')
                                .order_by(User.id).limit(12).all())
                for i, stu in enumerate(sec_students):
                    answers = {k: 4 + ((i + n) % 2) if (i + n) % 5 != 0 else 3 for n, k in enumerate(keys)}
                    db.session.add(TqiEocResponse(
                        section_id=sec.id,
                        user_id=stu.id,
                        answers_json=json.dumps(answers),
                        comment=eoc_comments[i % len(eoc_comments)],
                        created_at=now - timedelta(hours=8 + i),
                        updated_at=now - timedelta(hours=8 + i),
                    ))

            if TqiCritique.query.filter_by(section_id=sec.id).count() == 0:
                sec_instr = db.session.get(User, sec.instructor_id) or instr1
                sec_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                .filter(Enrollment.section_id == sec.id, User.role == 'student')
                                .order_by(User.id).limit(3).all())
                samples = [
                    (sec_students[0] if sec_students else sec_instr, 'student', 'labs', 5,
                     'Real Linux VM (v86) and stateful CLI labs matched the lesson objectives and reinforced verification before submit.'),
                    (sec_students[1] if len(sec_students) > 1 else sec_instr, 'student', 'curriculum', 4,
                     'The 5 Ways to Learn (especially the Analogy and Visual views) resolved tricky concepts quickly.'),
                    (sec_students[2] if len(sec_students) > 2 else sec_instr, 'student', 'test', 4,
                     'Practice Exam multi-part PBQs were realistic and the missed-objective drill pinpointed weak domains.'),
                    (sec_instr, 'instructor', 'instruction', 5,
                     'Students Needing Help and Eye Tracking heatmaps highlighted struggling students early for targeted 1-on-1 check-ins.'),
                    (sec_instr, 'instructor', 'closeout', 5,
                     'Convening closeout: class met mastery and exam-readiness benchmarks; keep emphasizing Diagnose -> Fix -> Verify in lab blocks.'),
                ]
                for u_obj, role, kind, rating, body in samples:
                    if not u_obj:
                        continue
                    db.session.add(TqiCritique(
                        section_id=sec.id, user_id=u_obj.id, role=role, kind=kind,
                        rating=rating, body=body, created_at=now - timedelta(hours=6),
                    ))

            if TqiAction.query.filter_by(section_id=sec.id).count() == 0:
                sec_instr = db.session.get(User, sec.instructor_id) or instr1
                db.session.add(TqiAction(
                    section_id=sec.id, area='labs', owner=sec_instr.full_name,
                    due_on=(now + timedelta(days=14)).strftime('%Y-%m-%d'),
                    body='Review Diagnose-First lab telemetry before the midterm practical and run a 10-minute Speed-Drill warm-up.',
                    created_by_id=sec_instr.id, created_at=now - timedelta(hours=5),
                ))
        db.session.commit()

        # ------------------------------------------------------------------ 8. StaffMessage Inbox, LearningPlan, MasteryCheckin & TutorQuestion
        StaffMessage = A.StaffMessage
        admin_user = User.query.filter_by(role='admin').first() or instr1
        if StaffMessage.query.count() == 0:
            s3_stu = User.query.filter_by(email='student3@lms.local').first() or s1
            s4_stu = User.query.filter_by(email='student4@lms.local').first() or s1
            s5_stu = User.query.filter_by(email='student5@lms.local').first() or s1
            s6_stu = User.query.filter_by(email='student6@lms.local').first() or s1
            threads_spec = [
                (instr1, s1, sec1.id, 'Practice Exams — CompTIA A+ Core 1 & Core 2 Exam Readiness',
                 'Hi Student1,\n\nGreat work reaching Exam Ready (829/900 on 220-1201 and 802/900 on 220-1202) in Practice Exams. Your Diagnose -> Fix -> Verify habits on the Linux VM permissions and DNS labs were spot-on. Let me know when you want to schedule your final proctored exam.',
                 'Thanks Jordan! The Analogy views and the 60-second port/protocol Speed-Drill really helped lock in the networking objectives. I am ready to sit Core 1 this Friday.'),
                (instr1, s1, sec_client.id if sec_client else sec1.id, 'Operating Systems Lab & CompTIA Tech+ (FC0-U71) Readiness Check',
                 'Hi Student1,\n\nYour Operating Systems Windows 11 service recovery and Linux account/sudo labs are 100% verified, and your CompTIA Tech+ (FC0-U71) sitting hit 836/900. Keep up the daily spaced review!',
                 'Will do — the instant-boot Linux VM snapshot made practicing the user/group permissions lab super fast.'),
                (instr1, s1, sec2.id, 'Basic Networking Linux VM Routing & VLAN Trunking Follow-up',
                 'Hi Student1,\n\nNice job verifying both `show interfaces trunk` and `ip neigh` before submitting the Basic Networking labs. You are on track for the Network+ (N10-009) full simulation this week.',
                 None),
                (instr1, s5_stu, sec1.id, 'Let us go through "Three kinds of work" & ESD Safety (IT-1.1 / IT-1.2) together',
                 'Hi Student5,\n\nI noticed Lesson 1.1 ("Three kinds of work") and the ESD power-off sequence took a few extra tries across the 5 Ways to Learn. That is useful signal for me, not a mark against you. Can we spend 10 minutes walking through the Visual view before tomorrow\'s lab?',
                 'Yes please — I kept mixing up service requests vs planned changes. Ten minutes before lab tomorrow works great.'),
                (instr1, s6_stu, sec2.id, 'Check-in on Layer-2 vs Layer-3 Hop Addressing (NO-1.1 / NO-1.2)',
                 'Hi Student6,\n\nOn the Chapter 1 check, remember that each router hop rewrites the Layer-2 frame MAC addresses and decrements TTL while keeping the source and destination IPv4 addresses intact (unless NAT is configured). Try the Packet-Flow Visualizer in Lab 1 to watch each hop live.',
                 'Got it, opening the Packet-Flow Visualizer now!'),
                (admin_user, s1, sec1.id, 'Welcome to Novak LMS™ — 5 Ways to Learn, Eye Tracking & Live VMs',
                 'Welcome to Novak LMS™! Every lesson includes 5 Ways to Learn (Standard, Plain English, Analogy, Visual, Try-It), opt-in Eye Tracking, 138 interactive and real Linux VM labs, and the Practice Exams.',
                 None),
            ]
            for idx_m, (sender, recip, sid_m, subj, body_txt, reply_txt) in enumerate(threads_spec):
                created_m = now - timedelta(hours=18 - idx_m * 2)
                root_msg = StaffMessage(
                    sender_id=sender.id, recipient_id=recip.id, section_id=sid_m,
                    subject=subj, body=body_txt, is_read=(idx_m > 0), created_at=created_m,
                )
                db.session.add(root_msg)
                db.session.flush()
                if reply_txt:
                    db.session.add(StaffMessage(
                        thread_id=root_msg.id, sender_id=recip.id, recipient_id=sender.id,
                        section_id=sid_m, subject=f'Re: {subj}', body=reply_txt,
                        is_read=True, created_at=created_m + timedelta(minutes=25),
                    ))
            db.session.commit()

        mx_api = app.extensions.get('ciwt_mastery')
        if mx_api and hasattr(mx_api, 'models'):
            LP_model = mx_api.models.LearningPlan
            MC_checkin = mx_api.models.MasteryCheckin
            if LP_model.query.count() == 0:
                prefs = ['alt', 'review', '', 'practice']
                for sec in all_secs:
                    sec_stus = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                .filter(Enrollment.section_id == sec.id, User.role == 'student')
                                .order_by(User.id).limit(8).all())
                    for idx_p, stu in enumerate(sec_stus):
                        db.session.add(LP_model(
                            section_id=sec.id, user_id=stu.id,
                            exam_date=(now + timedelta(days=21 + (idx_p * 7) % 42)).date(),
                            review_pref=prefs[idx_p % len(prefs)],
                            daily_size=8 if idx_p % 2 == 0 else 10,
                            updated_at=now - timedelta(hours=4 + idx_p),
                        ))
                db.session.commit()

            if MC_checkin.query.count() == 0:
                for sec in all_secs:
                    sec_stus = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                                .filter(Enrollment.section_id == sec.id, User.role == 'student')
                                .order_by(User.id).all())
                    for idx_c, stu in enumerate(sec_stus[2:4]):
                        db.session.add(MC_checkin(
                            section_id=sec.id, user_id=stu.id,
                            on_date=(now + timedelta(days=1 + idx_c)).date(),
                            note='Walk through the Analogy view and verify with one diagnostic command before making changes in lab.',
                            reasons_json=json.dumps(['Repeated misconception on chapter check', 'Tried all 5 ways on section 2']),
                            created_by=sec.instructor_id or instr1.id,
                            created_at=now - timedelta(hours=3 + idx_c),
                        ))
                db.session.commit()

        tutor_api = app.extensions.get('ciwt_tutor')
        if tutor_api and hasattr(tutor_api, 'TutorQuestion') and tutor_api.TutorQuestion.query.count() == 0:
            TQ = tutor_api.TutorQuestion
            tutor_samples = [
                (sec1, 'ITSUP', 'Why do we unplug AC power and hold the power button before touching RAM on a desktop?',
                 [{'type': 'lesson', 'label': '1.2', 'sid': 'esd-and-bench-safety'}, {'type': 'rung', 'label': '1.2', 'sid': 'esd-and-bench-safety', 'rung': 'R1'}]),
                (sec1, 'ITSUP', 'What is the difference between an incident ticket and a service request in IT support?',
                 [{'type': 'lesson', 'label': '1.1', 'sid': '2-three-kinds-of-work'}, {'type': 'rung', 'label': '1.1', 'sid': '2-three-kinds-of-work', 'rung': 'R2'}]),
                (sec1, 'ITSUP', 'When a Windows laptop gets 169.254.x.x (APIPA), what should I check first before replacing the NIC?',
                 [{'type': 'lesson', 'label': '5.1', 'sid': 'client-addressing'}, {'type': 'lab', 'lab_id': 'win-ipconfig'}]),
                (sec2, 'NETOPS', 'Why does VLAN 20 traffic fail to reach the router subinterface when show vlan brief shows the access port is active?',
                 [{'type': 'lesson', 'label': '2.2', 'sid': 'trunks-and-802-1q'}, {'type': 'lab', 'lab_id': 'sw-vlan-and-trunk'}]),
                (sec2, 'NETOPS', 'How do I check whether a DNS failure on Linux is caused by /etc/resolv.conf or a stale /etc/hosts override?',
                 [{'type': 'lesson', 'label': '4.3', 'sid': 'dns-resolution'}, {'type': 'lab', 'lab_id': 'linux-vm-dns'}]),
            ]
            if sec_client:
                tutor_samples.extend([
                    (sec_client, 'CLIENT', 'When a Windows 11 service like Print Spooler stops repeatedly, how do I inspect its dependencies and recovery action?',
                     [{'type': 'lesson', 'label': '8.2', 'sid': 'services-and-dependencies'}, {'type': 'lab', 'lab_id': 'w11-services'}]),
                    (sec_client, 'CLIENT', 'Why does NTFS effective permission deny access when the SMB share permission is set to Full Control?',
                     [{'type': 'lesson', 'label': '10.2', 'sid': 'share-vs-ntfs-permissions'}, {'type': 'rung', 'label': '10.2', 'sid': 'share-vs-ntfs-permissions', 'rung': 'R3'}]),
                ])
            for idx_q, (sec_q, c_code, q_text, cites) in enumerate(tutor_samples):
                if not sec_q:
                    continue
                db.session.add(TQ(
                    user_id=s1.id if idx_q % 2 == 0 else (User.query.filter_by(email=f'student{3 + (idx_q % 4)}@lms.local').first() or s1).id,
                    section_id=sec_q.id, course=c_code, question=q_text,
                    outcome='answered', cites_json=json.dumps(cites),
                    created_at=now - timedelta(hours=2 + idx_q * 3),
                ))
            db.session.commit()


        # ------------------------------------------------------------------ 9. Deep-Dive Completeness (Student1 NETOPS Mastery, R1-R4 Profile, Sec 3/4 Tutor, 100% TQI Ready)
        # 9a. Ensure Student1 has TestAttempts, QuizAttempts, LabProgress, and ExamSimAttempt in Section 2 (NETOPS)
        if sec2:
            s1_sec2_tests = KnowledgeTest.query.filter_by(course_id=sec2.course_id).order_by(KnowledgeTest.order).all()
            for ti, test in enumerate(s1_sec2_tests):
                if not TestAttempt.query.filter_by(user_id=s1.id, section_id=sec2.id, test_id=test.id).first():
                    qs = json.loads(test.questions or '[]')
                    comp_at = now - timedelta(hours=10 + ti * 4)
                    if isinstance(qs, dict) and qs.get('kind') == 'practical':
                        db.session.add(TestAttempt(
                            user_id=s1.id, test_id=test.id, section_id=sec2.id,
                            answers=json.dumps({'practical': True}), score=92.0, passed=True,
                            started_at=comp_at - timedelta(minutes=35), completed_at=comp_at,
                        ))
                    elif isinstance(qs, list) and qs:
                        ans = {}
                        c_n = 0
                        for qi, q in enumerate(qs):
                            if not isinstance(q, dict):
                                continue
                            if qi % 12 != 0:
                                ans[str(qi)] = q.get('correct')
                                c_n += 1
                            else:
                                wrong = [o for o in (q.get('options') or []) if o != q.get('correct')]
                                ans[str(qi)] = wrong[0] if wrong else q.get('correct')
                        score = round(100.0 * c_n / len(qs), 1)
                        db.session.add(TestAttempt(
                            user_id=s1.id, test_id=test.id, section_id=sec2.id,
                            answers=json.dumps(ans), score=score, passed=score >= 80,
                            started_at=comp_at - timedelta(minutes=40), completed_at=comp_at,
                        ))
            s1_sec2_quizzes = (Quiz.query.join(Module, Module.id == Quiz.module_id)
                               .filter(Module.course_id == sec2.course_id)
                               .order_by(Module.order, Quiz.id).all())
            for qi, qz in enumerate(s1_sec2_quizzes):
                if not QuizAttempt.query.filter_by(user_id=s1.id, section_id=sec2.id, quiz_id=qz.id).first():
                    q_items = json.loads(qz.questions or '[]')
                    if not q_items:
                        continue
                    ans = {str(idx): it['correct'] for idx, it in enumerate(q_items)}
                    db.session.add(QuizAttempt(
                        user_id=s1.id, quiz_id=qz.id, section_id=sec2.id,
                        answers=json.dumps(ans), score=100.0,
                        completed_at=now - timedelta(hours=8 + qi * 3),
                    ))
            if es_api and not es_api.Attempt.query.filter_by(user_id=s1.id, section_id=sec2.id, exam='N').first():
                from curriculum_v2.cert import exam_sim as ES
                chosen = ES.build_form('N', 'full', rng=random.Random(f'{s1.id}:sec2:N:full'))
                b_bank = ES.P.bank()
                answers = {}
                for i, (iid, _oid) in enumerate(chosen):
                    it = b_bank.get(iid)
                    if not it:
                        continue
                    if i % 11 != 0:
                        answers[str(i)] = str(it['correct']) if it['type'] == 'single' else json.dumps([str(c) for c in it['correct']])
                    else:
                        wrong = [o for o in it['options'] if o != it['correct']] if it['type'] == 'single' else list(reversed(list(it['correct'])))
                        answers[str(i)] = str(wrong[0] if wrong else it['correct']) if it['type'] == 'single' else json.dumps([str(c) for c in wrong])
                correct_n = sum(1 for i, (iid, _o) in enumerate(chosen) if iid in b_bank and ES.P.grade(b_bank[iid], answers.get(str(i))))
                earned, possible = ES.earned_and_possible(chosen, answers, b_bank)
                score = ES.scaled(earned, possible)
                by_dom = {}
                for i, (iid, oid) in enumerate(chosen):
                    it = b_bank.get(iid)
                    if not it:
                        continue
                    dom = ES.OBJECTIVES[oid]['domain']
                    d = by_dom.setdefault(dom, [0, 0])
                    d[1] += 1
                    if ES.P.grade(it, answers.get(str(i))):
                        d[0] += 1
                sub_at = now - timedelta(hours=12)
                att = es_api.Attempt(
                    user_id=s1.id, section_id=sec2.id, exam='N', mode='full',
                    strict=True, items=json.dumps(chosen), answers=json.dumps(answers),
                    flags=json.dumps([1]), started_at=sub_at - timedelta(minutes=50),
                    deadline=sub_at + timedelta(minutes=40), submitted_at=sub_at,
                    timed_out=False, score=score, correct=correct_n, total=len(chosen),
                    badge='ready', domains=json.dumps(by_dom),
                )
                db.session.add(att)
                db.session.flush()
                g = es_api.Grade.query.filter_by(section_id=sec2.id, user_id=s1.id, exam='N').first()
                if not g:
                    g = es_api.Grade(section_id=sec2.id, user_id=s1.id, exam='N')
                    db.session.add(g)
                g.attempt_id, g.score, g.pct, g.status, g.synced_at = att.id, att.score, round(max(0, (att.score - 100)) / 8, 1), 'EXAM READY', sub_at
            db.session.commit()
            if gb_api and hasattr(gb_api, 'invalidate'):
                gb_api.invalidate(sec2.id)

        # 9b. Ensure Student1 has at least one R4 ('Trying it hands-on') resolved LadderState + LadderEvent in Sections 1, 2, and 5
        for sec in (sec1, sec2, sec_client):
            if not sec:
                continue
            code = sec.course.code if sec.course else 'ITSUP'
            has_r4 = LadderState.query.filter_by(user_id=s1.id, section_id=sec.id, resolved='R4').first()
            if not has_r4:
                s1_rows = LadderState.query.filter_by(user_id=s1.id, section_id=sec.id).order_by(LadderState.id.desc()).all()
                if s1_rows:
                    r4_row = s1_rows[0]
                    r4_row.current = 'R4'
                    r4_row.resolved = 'R4'
                    r4_row.tried_json = json.dumps(['R0', 'R1', 'R2', 'R3', 'R4'])
                    t_at = now - timedelta(hours=5)
                    for r_step in ('R1', 'R2', 'R3', 'R4'):
                        db.session.add(LadderEvent(
                            user_id=s1.id, section_id=sec.id, course=code, label=r4_row.label, sid=r4_row.sid,
                            kind='request', rung=r_step, source='button', from_rung='R0',
                            created_at=t_at - timedelta(minutes=4),
                        ))
                    db.session.add(LadderEvent(
                        user_id=s1.id, section_id=sec.id, course=code, label=r4_row.label, sid=r4_row.sid,
                        kind='resolved', rung='R4', created_at=t_at,
                    ))
        db.session.commit()

        # 9c. Ensure Sections 3 and 4 also have TutorQuestion rows
        if tutor_api and hasattr(tutor_api, 'TutorQuestion'):
            TQ = tutor_api.TutorQuestion
            extra_tutor = [
                (sec3, 'ITSUP', 'How do I verify whether a display failure is the monitor cable vs the motherboard video output?',
                 [{'type': 'lesson', 'label': '2.2', 'sid': 'display-and-video-troubleshooting'}, {'type': 'lab', 'lab_id': 'hw-pc-build'}]),
                (sec3, 'ITSUP', 'Why should we test a backup restore to a scratch folder before relying on a nightly job?',
                 [{'type': 'lesson', 'label': '12.3', 'sid': 'backup-and-restore-testing'}, {'type': 'lab', 'lab_id': 'linux-vm-restore'}]),
                (sec4, 'NETOPS', 'When traceroute stops at the default gateway, how do I check the router interface and NAT masquerade rule?',
                 [{'type': 'lesson', 'label': '3.2', 'sid': 'routing-and-nat'}, {'type': 'lab', 'lab_id': 'linux-vm-nat'}]),
                (sec4, 'NETOPS', 'What is the difference between 802.1Q trunk native VLAN and allowed VLAN list on a switch uplink?',
                 [{'type': 'lesson', 'label': '2.2', 'sid': 'trunks-and-802-1q'}, {'type': 'lab', 'lab_id': 'sw-vlan-and-trunk'}]),
            ]
            for idx_q, (sec_q, c_code, q_text, cites) in enumerate(extra_tutor):
                if not sec_q or TQ.query.filter_by(section_id=sec_q.id, question=q_text).first():
                    continue
                sec_stu = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                           .filter(Enrollment.section_id == sec_q.id, User.role == 'student')
                           .order_by(User.id).first()) or s1
                db.session.add(TQ(
                    user_id=sec_stu.id, section_id=sec_q.id, course=c_code, question=q_text,
                    outcome='answered', cites_json=json.dumps(cites),
                    created_at=now - timedelta(hours=3 + idx_q * 2),
                ))
            db.session.commit()

        # 9d. Ensure ALL 5 sections meet 100% TQI Packet Ready criteria (>=60% EOC responses + critiques from all course instructors)
        for sec in all_secs:
            sec_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                            .filter(Enrollment.section_id == sec.id, User.role == 'student')
                            .order_by(User.id).all())
            need_eoc = max(1, int(round(len(sec_students) * 0.75)))
            existing_eoc_uids = {r.user_id for r in TqiEocResponse.query.filter_by(section_id=sec.id).all()}
            for i, stu in enumerate(sec_students):
                if len(existing_eoc_uids) >= need_eoc:
                    break
                if stu.id in existing_eoc_uids:
                    continue
                answers = {k: 4 + ((i + n) % 2) if (i + n) % 5 != 0 else 3 for n, k in enumerate(keys)}
                db.session.add(TqiEocResponse(
                    section_id=sec.id, user_id=stu.id,
                    answers_json=json.dumps(answers),
                    comment=eoc_comments[i % len(eoc_comments)],
                    created_at=now - timedelta(hours=6 + i),
                    updated_at=now - timedelta(hours=6 + i),
                ))
                existing_eoc_uids.add(stu.id)

            # Ensure every instructor associated with the section or course has a closeout/instruction critique
            course_instr_ids = {sec.instructor_id} if sec.instructor_id else set()
            for link in A.CourseInstructor.query.filter_by(course_id=sec.course_id).all():
                course_instr_ids.add(link.user_id)
            commented_instr_ids = {
                r.user_id for r in TqiCritique.query.filter(
                    TqiCritique.section_id == sec.id,
                    TqiCritique.role.in_(['instructor', 'admin']),
                ).all()
            }
            for iid in course_instr_ids - commented_instr_ids:
                if not iid:
                    continue
                db.session.add(TqiCritique(
                    section_id=sec.id, user_id=iid, role='instructor', kind='closeout', rating=5,
                    body='Convening review complete: EOC survey benchmarks, item analysis, and lab process telemetry verified.',
                    created_at=now - timedelta(hours=4),
                ))
            pkt = TqiPacket.query.filter_by(section_id=sec.id).first()
            if pkt:
                pkt.status = 'ready'
                pkt.auto_ready_at = pkt.auto_ready_at or (now - timedelta(hours=3))
        db.session.commit()

        try:
            refresh_demo_text_names(A)
        except Exception as e:  # pragma: no cover - never block startup on copy edits
            db.session.rollback()
            print('Demo text rename note:', e)
        return {'ok': True}
