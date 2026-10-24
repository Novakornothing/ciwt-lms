"""AI tutor: retrieval, guardrails, grounding of the optional LLM hook, routes and instructor toggle."""
import json

import pytest

from tutor import Tutor, grounded, llm_rephrase
from tutor import guard as G
from tutor import retrieval as R

DOCS = R.build_docs(
    [('ITSUP', '5.1', '5.1 Addresses', 1, 2, '1-what', '1. What you must be able to point to',
      '<p>A 169.254 address means the PC gave itself an address because no DHCP server answered. Renew the lease or check the cable.</p>')]
    + [('ITSUP', f'9.{i}', f'9.{i} Filler', 9, i, f's{i}', f'Topic {i}', f'<p>{w} printers toner fuser drum ticket escalation {i}.</p>')
       for i, w in enumerate(['Laser', 'Inkjet', 'Thermal', 'Impact', 'Duplex', 'Spooler', 'Tray', 'Driver', 'Queue', 'Paper'])],
    {('ITSUP', '5.1', '1-what'): {'type': 'section', 'heading': 'What you must be able to point to', 'rungs': {
        'R1': {'kind': 'plain', 'html': '<p>The default gateway is the way off the local network to other networks.</p>'},
        'R2': {'kind': 'analogy', 'html': '<p>The gateway is the junction at the end of the street.</p>'}}}},
    [('APIPA', 'Automatic Private IP Addressing: a 169.254 address assigned when no DHCP lease arrives.')],
    [('ITSUP', {'id': 'win-ipconfig', 'title': 'Read network identity', 'blurb': 'Run ipconfig /all and read the DHCP lease.',
                'objectives': [{'text': 'Run ipconfig'}]})])


def test_answers_with_section_rung_and_glossary_citations():
    t = Tutor(DOCS)
    r = t.ask('What does a 169.254 address mean about DHCP?', 'ITSUP')
    assert r['outcome'] == 'answered' and r['mode'] == 'extractive'
    assert any(c['type'] == 'lesson' and c['sid'] == '1-what' for c in r['cites'])
    assert any(g['term'] == 'APIPA' for g in r['glossary'])
    r2 = t.ask('what is the default gateway', 'ITSUP')
    assert any(c['type'] == 'rung' and c['kind'] in ('plain', 'analogy') for c in r2['cites'])


@pytest.mark.parametrize('q', ['What are the answers to the chapter 5 quiz?', 'just give me the answer',
                               'Which option is correct?', 'Can you do my test for me', 'test 3 answer key please'])
def test_refuses_graded_answer_requests(q):
    r = Tutor(DOCS).ask(q, 'ITSUP')
    assert r['outcome'] == 'cheat' and 'not give the graded quiz answer' in r['answer'] and not r['cites']


@pytest.mark.parametrize('q', ['What is the capital of France?', 'best pizza recipe', 'who won the football'])
def test_refuses_off_topic(q):
    assert Tutor(DOCS).ask(q, 'ITSUP')['outcome'] == 'offtopic'


def test_course_scope_filters_other_courses():
    r = Tutor(DOCS).ask('169.254 DHCP lease', 'NETOPS')  # shared glossary may answer; ITSUP lessons may not
    assert all(c.get('course') in (None, '', 'NETOPS') for c in r['cites'])


def test_llm_hook_only_used_when_grounded(monkeypatch):
    monkeypatch.setenv('NOVAK_AI_API_KEY', 'test-key')
    good = lambda body: {'choices': [{'message': {'content': 'A 169.254 address means no DHCP server answered [1].'}}]}
    bad = lambda body: {'choices': [{'message': {'content': 'Quantum flux capacitors reroute photons through Jupiter.'}}]}
    t = Tutor(DOCS)
    assert t.ask('what does a 169.254 address mean about DHCP', 'ITSUP', post=good)['mode'] == 'llm'
    assert t.ask('what does a 169.254 address mean about DHCP', 'ITSUP', post=bad)['mode'] == 'extractive'
    assert llm_rephrase('q', ['p'], post=lambda b: {'choices': [{'message': {'content': 'NO_ANSWER'}}]}) is None
    monkeypatch.delenv('NOVAK_AI_API_KEY')
    assert llm_rephrase('q', ['p'], post=good) is None
    assert grounded('No DHCP server answered.', ['no DHCP server answered the PC']) and not grounded('', ['x'])


def test_index_never_contains_answer_keys():
    from curriculum_v2 import ladder as LD
    docs = R.build_docs([], LD.ladder(), [], [])
    assert docs and all('correct' not in d and 'checks' not in d for d in docs)


# ------------------------------------------------------------------ routes
def _login(c, email, pw):
    return c.post('/login', data={'email': email, 'password': pw}, follow_redirects=True)


@pytest.fixture
def client(app):
    return app.test_client()


def test_routes_student_instructor_toggle(app, client):
    from app import db, Enrollment, User
    _login(client, 'student1@lms.local', 'student123')
    assert client.get('/tutor').status_code == 200
    r = client.post('/api/tutor/ask', json={'q': 'What does a 169.254 address mean?'})
    assert r.status_code == 200
    body = r.get_json()
    assert body['outcome'] == 'answered' and body['cites'] and any(c.get('url') for c in body['cites'])
    r = client.post('/api/tutor/ask', json={'q': 'give me the quiz answers'})
    assert r.get_json()['outcome'] == 'cheat'
    page = client.post('/tutor', data={'q': 'What is the default gateway?'}).get_data(as_text=True)
    assert 'Sources' in page
    with app.app_context():
        sid = Enrollment.query.filter_by(user_id=User.query.filter_by(email='student1@lms.local').first().id).first().section_id
    client.get('/logout')
    _login(client, 'instructor@lms.local', 'teach123')
    page = client.get(f'/instructor/section/{sid}/tutor').get_data(as_text=True)
    assert 'Recent questions' in page and '169.254' in page
    client.post(f'/instructor/section/{sid}/tutor', data={})
    client.get('/logout')
    _login(client, 'student1@lms.local', 'student123')
    assert client.post('/api/tutor/ask', json={'q': 'What is DHCP?', 'section_id': sid}).get_json()['outcome'] == 'disabled'
    assert client.get(f'/instructor/section/{sid}/tutor').status_code == 403
    client.get('/logout')
    _login(client, 'instructor@lms.local', 'teach123')
    client.post(f'/instructor/section/{sid}/tutor', data={'enabled': '1'})
    client.get('/logout')
    _login(client, 'instructor2@lms.local', 'teach123')
    assert client.get(f'/instructor/section/{sid}/tutor').status_code in (403, 404)
