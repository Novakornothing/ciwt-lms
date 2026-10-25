"""Rich, idempotent demo telemetry seeder for Novak LMS™ flagship dashboards.

Ensures that when an evaluator enters the 1-Click Student, Instructor, or Admin Demo on
Novak LMS™ (either locally or on Render's persistent /var/data/ciwt/ciwt_lms.db disk),
every flagship dashboard is populated with realistic, up-to-date activity:
1. Active ClassSection for Course 3 (CLIENT — Client Systems & Shop Procedures)
2. "Who Needs Me" Co-Pilot (/instructor/section/1/who-needs-me & /instructor/section/2/who-needs-me)
   with 4 active students needing attention today (exhausted ladder, repeated mix-up, lab habit, stuck review)
   and recent activity timestamps across the roster (no stale "41 days ago" inactivity).
3. Exam-Day Simulator & Speed-Drill (/instructor/section/1/exam-sim, /instructor/section/2/exam-sim,
   /student/section/1/exam-sim, /portfolio) with Voucher Ready, Borderline, and Remediation sittings,
   synced gradebook rows, and Leitner spaced-repetition Speed-Drill stats.
4. Institutional Outcomes (/admin/outcomes) with realistic BKT mastery, 4-rung ladder resolution
   breakdown across R1–R4 (~89% resolved), and Diagnose -> Fix -> Verify lab process telemetry.
5. Helix MediaPipe 478-landmark attention sessions on both Section 1 (ITSUP) and Section 2 (NETOPS).
"""
import json
import random
from datetime import timedelta


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
        TestAttempt = A.TestAttempt
        ContentRelease = A.ContentRelease
        TimeLog = A.TimeLog
        LabCompletion = A.LabCompletion
        utcnow = A.utcnow

        # Only run if the standard demo cohort exists
        instr1 = User.query.filter_by(email='instructor@lms.local').first()
        s1 = User.query.filter_by(email='student1@lms.local').first()
        if not instr1 or not s1:
            return {'ok': False, 'reason': 'no_demo_users'}

        now = utcnow()
        rnd = random.Random(20261024)

        # Scrub any legacy 'CIWT' / 'ciwt' strings in Course, Module, Lesson, and LabEvent rows
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
        labs_api_0 = app.extensions.get('ciwt_lab_progress')
        if labs_api_0:
            for le_row in labs_api_0.LabEvent.query.filter(labs_api_0.LabEvent.action.ilike('%ciwt%')).all():
                le_row.action = le_row.action.replace('ciwt.internal', 'novak.internal').replace('ciwt.lab', 'novak.lab').replace('ciwt.local', 'novak.local')
        db.session.commit()

        # ------------------------------------------------------------------ 1. Course 3 (CLIENT) Active Section
        client_course = Course.query.filter_by(code='CLIENT').first()
        sec_client = None
        if client_course:
            sec_client = ClassSection.query.filter_by(course_id=client_course.id).first()
            if sec_client and 'CLIENT-101' not in (sec_client.name or ''):
                sec_client.name = 'Client Systems & Shop Procedures — CLIENT-101'
                db.session.commit()
            if not sec_client:
                sec_client = ClassSection(
                    name='Client Systems & Shop Procedures — CLIENT-101',
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
                                                  progress_percent=rnd.randint(35, 92)))
                for mod in Module.query.filter_by(course_id=client_course.id).all():
                    db.session.add(ContentRelease(
                        section_id=sec_client.id, content_type='module', content_id=mod.id,
                        is_active=True, available_from=now - timedelta(days=14),
                        available_until=now + timedelta(days=90),
                        activated_by=instr1.id, activated_at=now - timedelta(days=14),
                    ))
                db.session.commit()

        sec1 = db.session.get(ClassSection, 1)
        sec2 = db.session.get(ClassSection, 2)
        if not sec1 or not sec2:
            return {'ok': False, 'reason': 'missing_sections_1_2'}
        if not Enrollment.query.filter_by(user_id=s1.id, section_id=sec2.id).first():
            db.session.add(Enrollment(user_id=s1.id, section_id=sec2.id, progress_percent=78))
            db.session.commit()

        # Refresh TestAttempt timestamps if any are older than 6 days so no student shows "No activity for 41 days"
        recent_cutoff = now - timedelta(days=5)
        old_attempts = TestAttempt.query.filter(TestAttempt.completed_at < recent_cutoff).all()
        if old_attempts:
            from app import KnowledgeTest
            kt_map = {k.id: json.loads(k.questions or '[]') for k in KnowledgeTest.query.all()}
            struggler_uids = {u.id for u in User.query.filter(User.email.in_(['student3@lms.local', 'student4@lms.local', 'student5@lms.local', 'student6@lms.local', 'student7@lms.local', 'student8@lms.local'])).all()}
            for idx, ta in enumerate(old_attempts):
                age_hours = 4 + (idx * 3) % 96  # spread within the last 4 hours to 4 days
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

        # Ensure every enrolled student in Section 1 and Section 2 has a recent study TimeLog within last 1-4 days
        for sec in (sec1, sec2):
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

        # ------------------------------------------------------------------ 2. Helix Attention (MediaPipe + Section 2)
        HelixGazeSession = A.HelixGazeSession
        HelixConsent = A.HelixConsent
        from helix.models import POLICY_VERSION
        # Upgrade any legacy seeded WebGazer demo sessions to MediaPipe with realistic accuracy
        legacy_hx = HelixGazeSession.query.filter_by(is_demo=True, mode='gaze', engine='webgazer').all()
        for idx, s in enumerate(legacy_hx):
            acc = 82 + (idx * 3) % 12  # 82% - 93%
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
            s.calib_ms = 15800 + (idx % 5) * 900
            s.calib_mode = 'dots'
            s.camera_res = '1280x720'
            s.hires = True
            s.browser = 'Chrome 131'
            s.started_at = now - timedelta(hours=6 + (idx * 2) % 60)
            s.ended_at = s.started_at + timedelta(milliseconds=s.total_ms or 180000)
            s.last_seen_at = s.ended_at
        db.session.commit()

        # Seed Section 2 (NETOPS) Helix demo sessions if empty
        if HelixGazeSession.query.filter_by(section_id=sec2.id).count() == 0:
            sec2_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                             .filter(Enrollment.section_id == sec2.id, User.role == 'student')
                             .order_by(User.id).limit(8).all())
            A._seed_helix_demo(sec2, sec2_students)

        # Ensure students who have demo Helix sessions have a matching HelixConsent row
        # (Skip student2@lms.local so unit tests expecting student2 to start unconsented if run on a copy still pass)
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

        # ------------------------------------------------------------------ 3. 4-Rung Ladder States & Active Struggles
        from curriculum_v2 import ladder as LD
        from mastery.ladder import define_ladder_models
        LM = define_ladder_models(db)
        LadderState, LadderEvent = LM.LadderState, LM.LadderEvent

        if LadderState.query.count() == 0:
            for sec, code in ((sec1, 'ITSUP'), (sec2, 'NETOPS')):
                enrolled = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                            .filter(Enrollment.section_id == sec.id, User.role == 'student')
                            .order_by(User.id).all())
                lessons_by_lbl = {}
                for m_row in Module.query.filter_by(course_id=sec.course_id).all():
                    for l_row in Lesson.query.filter_by(module_id=m_row.id).all():
                        lessons_by_lbl[f'{m_row.order}.{l_row.order}'] = l_row.id
                entries = [(k, v) for k, v in sorted(LD.ladder().items())
                           if k[0] == code and v.get('type') == 'section' and k[1] in ('1.1', '1.2', '1.3', '2.1', '2.2')]
                if not entries:
                    continue
                # Seed resolved struggles across R1, R2, R3, R4 for most students (~89% resolution rate)
                rungs_cycle = ['R1', 'R2', 'R1', 'R3', 'R2', 'R4', 'R1', 'R3', 'R2', 'R1']
                for si, stu in enumerate(enrolled[:14]):
                    for ei, ((_c, lbl, sid), ent) in enumerate(entries[:4]):
                        lid = lessons_by_lbl.get(lbl)
                        # Pick 2 students per section to have an EXHAUSTED ladder section (shows in Who Needs Me!)
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
                            # Log a wrong check with a misconception tag so Who Needs Me cites it
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

        # ------------------------------------------------------------------ 4. Quizzes & Active Misconceptions (Who Needs Me)
        from curriculum_v2 import misconceptions as MCS
        if QuizAttempt.query.count() == 0:
            for sec in (sec1, sec2):
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
                        # Students at index 2, 3, 5 in each section get repeated tagged misconceptions on Ch 1 & 2 quizzes
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
                        # If struggler on quiz 0, add a second attempt hitting the same misconception so hits >= 2!
                        if struggler and qi == 0:
                            db.session.add(QuizAttempt(
                                user_id=stu.id, quiz_id=qz.id, section_id=sec.id,
                                answers=json.dumps(answers), score=score,
                                completed_at=now - timedelta(hours=1, minutes=15 + si * 5),
                            ))
            db.session.commit()

        # ------------------------------------------------------------------ 5. Interactive & Real Linux VM Labs + Diagnose-First Telemetry
        labs_api = app.extensions.get('ciwt_lab_progress')
        if labs_api and labs_api.LabProgress.query.count() == 0:
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
            for sec, lab_id, done_objs, ev_list in lab_specs:
                enrolled = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                            .filter(Enrollment.section_id == sec.id, User.role == 'student')
                            .order_by(User.id).limit(12).all())
                for si, stu in enumerate(enrolled):
                    comp_at = now - timedelta(hours=5 + si * 3)
                    # Student index 3 in each section exhibits trial-and-error guessing on their first lab (shows on Who Needs Me!)
                    is_lab_struggler = (si == 3 and lab_id in ('win-ipconfig', 'sw-vlan-access'))
                    if is_lab_struggler:
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
                        lp = LP(
                            user_id=stu.id, lab_id=lab_id, state_json='{}',
                            done_json=json.dumps(done_objs), transcript_json='[]', undo_json='[]',
                            section_id=sec.id, score=100.0, best_score=100.0, actions=len(ev_list), wrong=0, hints_used=0, resets=0,
                            started_at=comp_at - timedelta(minutes=14), updated_at=comp_at,
                            completed_at=comp_at,
                        )
                        db.session.add(lp)
                        if not LabCompletion.query.filter_by(user_id=stu.id, lab_id=lab_id, section_id=sec.id).first():
                            db.session.add(LabCompletion(
                                user_id=stu.id, lab_id=lab_id, section_id=sec.id, completed_at=comp_at,
                            ))
                        for seq_i, (k, act, outc, newly_list) in enumerate(ev_list, 1):
                            db.session.add(LE(
                                user_id=stu.id, lab_id=lab_id, attempt=1, seq=seq_i,
                                at=comp_at - timedelta(minutes=10 - seq_i * 2),
                                kind=k, action=act, outcome=outc,
                                newly=json.dumps(newly_list) if newly_list else None, score=100.0,
                            ))
            db.session.commit()

        # ------------------------------------------------------------------ 6. Exam-Day Simulator & Speed-Drill
        es_api = app.extensions.get('ciwt_exam_sim')
        if es_api and es_api.Attempt.query.count() == 0:
            from curriculum_v2.cert import exam_sim as ES, speed_drill as SD
            ESA, ESG, ESD = es_api.Attempt, es_api.Grade, es_api.Accommodation
            b = ES.P.bank()

            def _seed_sitting(user, section, exam_key, mode, target_ratio, hours_ago, strict=True):
                chosen = ES.build_form(exam_key, mode, rng=random.Random(f'{user.id}:{exam_key}:{mode}'))
                answers = {}
                for i, (iid, _oid) in enumerate(chosen):
                    it = b.get(iid)
                    if not it:
                        continue
                    want_right = (random.Random(f'{user.id}:{i}:{exam_key}').random() < target_ratio)
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
                # Compute domain breakdown [correct, total]
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
                # Also sync to ExamSimGrade so Gradebook shows it out-of-the-box
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

            sec1_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                             .filter(Enrollment.section_id == sec1.id, User.role == 'student')
                             .order_by(User.id).all())
            # Student 1 (demo student account): Voucher Ready on 220-1201 and 220-1202
            if sec1_students:
                _seed_sitting(sec1_students[0], sec1, 'A1', 'full', 0.91, hours_ago=14, strict=True)
                _seed_sitting(sec1_students[0], sec1, 'A2', 'full', 0.88, hours_ago=6, strict=True)
            # Rest of Section 1 sample (mix of Voucher Ready, Borderline, Needs Remediation)
            ratios_s1 = [0.90, 0.86, 0.56, 0.52, 0.74, 0.58, 0.89, 0.76, 0.92, 0.85, 0.64, 0.88]
            for idx, stu in enumerate(sec1_students[1:13], 1):
                r = ratios_s1[(idx - 1) % len(ratios_s1)]
                _seed_sitting(stu, sec1, 'A1', 'full', r, hours_ago=4 + idx * 3, strict=(idx % 2 == 0))
                if idx % 2 == 0:
                    _seed_sitting(stu, sec1, 'A2', 'full', min(0.94, r + 0.04), hours_ago=2 + idx * 2, strict=True)

            # Section 2 (NETOPS — N10-009)
            sec2_students = (User.query.join(Enrollment, Enrollment.user_id == User.id)
                             .filter(Enrollment.section_id == sec2.id, User.role == 'student')
                             .order_by(User.id).all())
            ratios_s2 = [0.91, 0.87, 0.55, 0.51, 0.76, 0.60, 0.89, 0.77, 0.93, 0.84]
            for idx, stu in enumerate(sec2_students[:10]):
                r = ratios_s2[idx % len(ratios_s2)]
                _seed_sitting(stu, sec2, 'N', 'full', r, hours_ago=3 + idx * 4, strict=True)

            # Sample ADA Time Accommodation in Section 1 & Section 2
            if len(sec1_students) > 4 and not ESD.query.filter_by(section_id=sec1.id).first():
                db.session.add(ESD(section_id=sec1.id, user_id=sec1_students[4].id, multiplier=1.5))
            if len(sec2_students) > 3 and not ESD.query.filter_by(section_id=sec2.id).first():
                db.session.add(ESD(section_id=sec2.id, user_id=sec2_students[3].id, multiplier=1.25))
            db.session.commit()

        # Seed Speed-Drill Leitner stats for student1 and demo students
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

        return {'ok': True}
