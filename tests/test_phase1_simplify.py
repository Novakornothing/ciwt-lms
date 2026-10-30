"""Phase 1: plain-English names, course renames, hub budget, 60-second tour, student/instructor/admin tabs,
Cmd-K command cards, reader preferences."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW_TITLES = {'ITSUP': 'IT Support', 'NETOPS': 'Basic Networking', 'CLIENT': 'Operating Systems'}


def test_course_titles_renamed_and_codes_kept(app, mod):
    with app.app_context():
        got = {c.code: c.title for c in mod.Course.query.filter(mod.Course.code.in_(NEW_TITLES)).all()}
        assert got == NEW_TITLES
        names = [s.name for s in mod.ClassSection.query.all()]
    assert not any('Shop Procedures' in n or 'Client Systems' in n for n in names)


def test_new_titles_show_for_every_role(student, instructor, admin):
    assert 'IT Support' in student.get('/student').get_data(as_text=True)
    ih = instructor.get('/instructor').get_data(as_text=True)
    ah = admin.get('/admin').get_data(as_text=True)
    for h in (ih, ah):
        assert 'Shop Procedures' not in h
    assert any(t in ih for t in NEW_TITLES.values())


def test_no_old_jargon_in_main_pages(student, instructor, admin, anon):
    pages = [anon.get('/landing'), student.get('/student'), instructor.get('/instructor'), admin.get('/admin'),
             anon.get('/demo/tour')]
    for r in pages:
        h = r.get_data(as_text=True)
        for old in ('VOUCHER READY', 'Who Needs Me', 'Exam-Day Simulator', 'PBQ Workbench', 'Rung ', 'BKT',
                    'Shop Procedures', 'CIWT'):
            assert old not in h, (r.request.path, old)


def test_demo_tour_page_and_data(anon):
    r = anon.get('/demo/tour')
    assert r.status_code == 200
    h = r.get_data(as_text=True)
    for s in ('id="tour"', 'id="coursePick"', 'data-way=', 'id="camOn"', 'id="labForm"', 'data-view=',
              'id="tourCreate"', 'id="tourEnter"', 'js/demo_tour.js'):
        assert s in h, s
    data = json.loads(re.search(r'<script type="application/json" id="tourData">(.*?)</script>', h, re.S).group(1))
    assert [c['code'] for c in data['courses']] == ['ITSUP', 'NETOPS', 'CLIENT']
    assert [c['title'] for c in data['courses']] == list(NEW_TITLES.values())
    assert set(data['content']) == set(NEW_TITLES)


def test_landing_budget_links_and_brand(anon):
    h = anon.get('/landing').get_data(as_text=True)
    assert 'Every Mind Learns Differently.<br>Now the Course Does Too.' in h
    assert h.count('class="btn-gold"') == 1
    for href in ('/terms', '/security', '/privacy', '/specs', '/roi', '/consult', '/demo/tour', '/register'):
        assert f'href="{href}"' in h, href
    low = h.lower()
    assert 'soc 2' not in low and 'hecvat' not in low and 'not built yet' not in low
    assert '© 2026 Novak LMS™' in h


def test_student_lesson_reader_has_one_ways_bar_and_prefs(student, app, mod):
    with app.app_context():
        c = mod.Course.query.filter_by(code='ITSUP').first()
        sec = mod.ClassSection.query.filter_by(course_id=c.id).order_by(mod.ClassSection.id).first()
        m1 = mod.Module.query.filter_by(course_id=c.id, order=1).first()
        l1 = mod.Lesson.query.filter_by(module_id=m1.id, order=1).first()
    h = student.get(f'/student/module/{sec.id}/{m1.id}/lesson/{l1.id}').get_data(as_text=True)
    assert h.count('id="novakStepStyleBar"') == 1 and '5 Ways to Learn:' in h
    for k in ('fs', 'lh', 'contrast', 'dys', 'reset'):
        assert f'data-rp="{k}"' in h, k
    js = (ROOT / 'static/js/novak-ui.js').read_text()
    assert 'localStorage' in js and 'reader-dys' in js
    # Right rail on desktop / bottom sheet on mobile; the old header no longer sticks
    for s in ('id="lessonRail"', 'id="lessonRailToggle"', 'id="lessonRailSteps"', 'id="lessonRailLab"',
              'id="lessonSheetBtn"', 'id="lessonTopLine"'):
        assert s in h, s
    assert h.count('data-rail-rung=') == 5
    assert "novak.lessonRail.v1" in js and 'novak:lesson-step' in js
    css = (ROOT / 'static/css/novak-ui.css').read_text()
    assert '.novak-lesson-progress-bar { position: static !important;' in css


def test_cmdk_command_card(student):
    j = student.get('/api/search?q=chmod').get_json()
    card = j.get('command_card')
    assert card and card['command'].startswith('chmod') and card.get('syntax')
    j2 = student.get('/api/search?q=').get_json()
    assert j2.get('command_card') is None
    import command_cards as CC
    assert CC.card_for('show vlan brief') is not None
    assert CC.card_for('zzzz-not-a-command') is None


def test_instructor_tabs_roster_and_csv(instructor, student):
    h = instructor.get('/instructor').get_data(as_text=True)
    for s in ('id="classPassRate"', 'Students Needing Help', 'id="rosterTable"', 'id="rosterFilter"',
              '/instructor/roster.csv', 'Labs &amp; Assignments', 'Students &amp; Grades'):
        assert s in h, s
    r = instructor.get('/instructor/roster.csv')
    assert r.status_code == 200 and r.mimetype == 'text/csv'
    assert r.get_data(as_text=True).splitlines()[0].startswith('student,email,course,class,progress_percent')
    assert student.get('/instructor/roster.csv').status_code in (302, 403)


def test_admin_overview_cards_exports_and_tools(admin, instructor):
    h = admin.get('/admin').get_data(as_text=True)
    for s in ('admin-kpi-4', 'Active seats', 'Instructors', 'Exam Readiness', 'Estimated lab savings',
              'Users &amp; Sections', 'Exports'):
        assert s in h, s
    e = admin.get('/admin/exports').get_data(as_text=True)
    assert 'SCORM' in e and 'xAPI' in e and 'CSV' in e
    assert admin.get('/admin/tools').status_code == 200
    assert admin.get('/api/xapi/statements').get_json()['sample_only'] is False
    assert instructor.get('/admin/exports').status_code in (302, 403)


def test_no_unbacked_cmi5_or_ieee_claims(anon):
    """Novak LMS exports xAPI 1.0.3 statements; it is not a cmi5 LMS/LRS yet, so public copy must not say so."""
    for path in ('/landing', '/compliance', '/security', '/specs', '/gaps', '/consult', '/llms.txt', '/llms-full.txt'):
        body = anon.get(path).get_data(as_text=True).lower()
        for bad in ('cmi5 compliant', 'cmi5 conformant', 'cmi5)', '9274'):
            assert bad not in body, (path, bad)
