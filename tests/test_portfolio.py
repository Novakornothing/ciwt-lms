"""Skills portfolio: readiness maths, OpenBadges export, visibility and access control."""
from portfolio import build as B


def test_cert_readiness_and_levels():
    from curriculum_v2.cert.mapping import CURATED
    objs = list(CURATED)[:6]
    r = B.cert_readiness({o: {'p': 0.9 if i % 2 else 0.3} for i, o in enumerate(objs)})
    assert r and all(x['exam'] in B.EXAMS and 0 <= x['pct'] <= 100 and x['domains'] for x in r)
    assert B.cert_readiness({}) == []
    assert (B.level(0.9), B.level(0.7), B.level(0.1)) == ('Ready', 'Developing', 'Not yet')


def test_lab_badges_from_process_strengths():
    names = [b['label'] for b in B.lab_badges({'strengths': [{'id': 'diagnosed_first', 'label': 'Diagnosed before changing'},
                                                             {'id': 'verified_before_submit', 'label': 'Verified before submitting'}]})]
    assert 'Diagnosed before changing' in names and len(names) == 2
    assert B.lab_badges({}) == []


def test_openbadges_shape():
    pf = {'student': {'name': 'S One'}, 'generated': '2026-10-24', 'courses': [], 'certifications': [],
          'competencies': [{'id': 'o1', 'text': 'Read ipconfig', 'course': 'ITSUP'}],
          'labs': [{'id': 'l1', 'title': 'Lab', 'kind': 'vm', 'score': 100, 'badges': [{'label': 'Diagnosed before changing'}]}]}
    ob = B.openbadges(pf, 'http://x/', 'http://x/portfolio/u/t')
    assert len(ob['assertions']) == 2 and all(a['type'] == 'Assertion' for a in ob['assertions'])
    assert 'Diagnosed before changing' in ob['assertions'][1]['badge']['criteria']['narrative']


def test_visibility_public_link_and_instructor(app, student, anon, instructor, student2):
    from app import Enrollment, User
    assert student.get('/portfolio').status_code == 200
    r = student.get('/portfolio/export.json')
    assert r.status_code == 200 and r.is_json
    student.post('/portfolio/visibility', data={'visibility': 'link'})
    with app.app_context():
        PortfolioSetting = app.extensions['portfolio_api'].PortfolioSetting if 'portfolio_api' in app.extensions else __import__('app').portfolio_api.PortfolioSetting
        u = User.query.filter_by(email='student1@lms.local').first()
        tok = PortfolioSetting.query.get(u.id).token
        sid = Enrollment.query.filter_by(user_id=u.id).first().section_id
    page = anon.get(f'/portfolio/u/{tok}')
    assert page.status_code == 200 and b'noindex' in page.data
    assert anon.get('/portfolio/u/not-a-token').status_code == 404
    student.post('/portfolio/visibility', data={'visibility': 'private'})
    assert anon.get(f'/portfolio/u/{tok}').status_code == 404
    assert instructor.get(f'/instructor/section/{sid}/portfolio/{u.id}').status_code == 200
    assert student2.get(f'/instructor/section/{sid}/portfolio/{u.id}').status_code in (302, 403, 404)
