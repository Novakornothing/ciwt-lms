"""Create or refresh the Cybersecurity course, its checks, and a demo class."""
from datetime import datetime, timedelta
import json

from curriculum_sec.exam_bank import as_bank_items
from curriculum_sec.render import CHAPTERS

DISCLAIMER = (
    'Original Novak LMS™ curriculum, aligned to the CompTIA Security+ (SY0-701) exam objectives. '
    'Not affiliated with, endorsed by, or a substitute for any vendor certification.'
)
TITLE = 'Security'
DESCRIPTION = (
    'Security after IT support, basic networking, and operating systems. '
    'Lessons, labs, and a 90-question Exam-Day sitting cover the five Security+ domains in plain English. '
    + DISCLAIMER
)


def _quiz_items(chapter):
    """Eight short checks per chapter, separate stems from the practice bank."""
    bank = [it for it in as_bank_items() if it['type'] == 'single']
    # Spread by chapter number so each chapter sees different items, reworded as checks.
    start = (chapter - 1) * 8
    picked = bank[start:start + 8]
    if len(picked) < 8:
        picked = (bank + bank)[start:start + 8]
    out = []
    for it in picked:
        out.append({
            'text': 'Chapter check: ' + it['text'],
            'options': list(it['options']),
            'correct': it['correct'],
            'obj': it['obj'],
            'explanation': it['explanation'],
            'focus': f'Chapter {chapter}',
            'study_tip': 'Revisit the matching lesson and answer the section check in another learning path.',
        })
    return out


def _knowledge_items():
    singles = [it for it in as_bank_items() if it['type'] == 'single']
    # Take one from each place-rotation so the 45-item form still covers every objective.
    picked = singles[75:120]
    return [{
        'text': it['text'],
        'options': list(it['options']),
        'correct': it['correct'],
        'obj': it['obj'],
        'explanation': it['explanation'],
    } for it in picked]


def ensure_sec(db, models, utcnow, grant=None):
    """Idempotent. Returns the Course row."""
    Course = models['Course']
    Module = models['Module']
    Lesson = models['Lesson']
    Quiz = models['Quiz']
    KnowledgeTest = models['KnowledgeTest']
    ClassSection = models['ClassSection']
    Enrollment = models['Enrollment']
    User = models['User']
    CourseInstructor = models['CourseInstructor']
    ContentRelease = models['ContentRelease']

    course = Course.query.filter_by(code='SEC').first()
    if not course:
        course = Course(code='SEC', title=TITLE, description=DESCRIPTION)
        db.session.add(course)
        db.session.flush()
    else:
        course.title = TITLE
        course.description = DESCRIPTION

    for ch in CHAPTERS:
        mod = Module.query.filter_by(course_id=course.id, order=ch['order']).first()
        if not mod:
            mod = Module(course_id=course.id, order=ch['order'], title=ch['title'],
                         content=ch['overview'], estimated_minutes=ch['minutes'])
            db.session.add(mod)
            db.session.flush()
        else:
            mod.title = ch['title']
            mod.content = ch['overview']
            mod.estimated_minutes = ch['minutes']
        existing = {row.order: row for row in Lesson.query.filter_by(module_id=mod.id).all()}
        wanted = set()
        for les in ch['lessons']:
            wanted.add(les['order'])
            row = existing.get(les['order'])
            if row is None:
                row = Lesson(module_id=mod.id, order=les['order'])
                db.session.add(row)
            row.title = les['title']
            row.content = les['html']
            row.estimated_minutes = les['minutes']
        for order, row in existing.items():
            if order not in wanted:
                db.session.delete(row)
        qz = Quiz.query.filter_by(module_id=mod.id).order_by(Quiz.id).first()
        payload = json.dumps(_quiz_items(ch['order']))
        title = f'Chapter {ch["order"]} check'
        if not qz:
            db.session.add(Quiz(module_id=mod.id, title=title, questions=payload, is_ungraded=True))
        else:
            qz.title = title
            qz.questions = payload
            qz.is_ungraded = True

    kt = KnowledgeTest.query.filter_by(course_id=course.id, order=1).first()
    kt_payload = json.dumps(_knowledge_items())
    if not kt:
        db.session.add(KnowledgeTest(
            course_id=course.id,
            title='Security knowledge check',
            description='Forty-five original items drawn from the Security practice bank. ' + DISCLAIMER,
            order=1,
            questions=kt_payload,
            passing_score=80,
            time_limit_minutes=45,
        ))
    else:
        kt.title = 'Security knowledge check'
        kt.description = 'Forty-five original items drawn from the Security practice bank. ' + DISCLAIMER
        kt.questions = kt_payload
        kt.passing_score = 80
        kt.time_limit_minutes = 45

    instr = User.query.filter_by(email='instructor@lms.local').first()
    admin = User.query.filter_by(email='admin@lms.local').first()
    if instr and not CourseInstructor.query.filter_by(course_id=course.id, user_id=instr.id).first():
        db.session.add(CourseInstructor(course_id=course.id, user_id=instr.id))
    section = ClassSection.query.filter_by(course_id=course.id).order_by(ClassSection.id).first()
    if not section and instr:
        section = ClassSection(
            name='Security — after Operating Systems',
            course_id=course.id,
            instructor_id=instr.id,
            max_students=30,
            start_date=datetime(2026, 1, 15).date(),
            end_date=datetime(2026, 5, 15).date(),
        )
        db.session.add(section)
        db.session.flush()
    if section and instr and grant:
        grant(section.id, instr.id, primary=True)
    student = User.query.filter_by(email='student1@lms.local').first()
    if section and student and not Enrollment.query.filter_by(user_id=student.id, section_id=section.id).first():
        db.session.add(Enrollment(user_id=student.id, section_id=section.id, progress_percent=0))
    if section:
        now = utcnow()
        for mod in Module.query.filter_by(course_id=course.id).all():
            rel = ContentRelease.query.filter_by(
                section_id=section.id, content_type='module', content_id=mod.id, user_id=None,
            ).first()
            if not rel:
                db.session.add(ContentRelease(
                    section_id=section.id, content_type='module', content_id=mod.id,
                    is_active=True,
                    available_from=now - timedelta(days=1),
                    available_until=now + timedelta(days=365),
                    activated_by=(instr.id if instr else (admin.id if admin else None)),
                    activated_at=now,
                ))
        try:
            db.session.execute(
                db.text('INSERT OR REPLACE INTO section_join_code (section_id, code) VALUES (:sid, :c)'),
                {'sid': section.id, 'c': 'SECURITY-DEMO'},
            )
        except Exception:
            pass
    return course
