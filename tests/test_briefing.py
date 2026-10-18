"""Pass 12: instructor co-pilot briefing (deterministic, from class data). Rows created here are throwaway test rows."""
import json
from datetime import datetime, timedelta

import pytest

from curriculum_v2 import misconceptions as MCS
from mastery import briefing as BR


@pytest.fixture(scope='module', autouse=True)
def objective_tagged_checks(app, mod):
    with app.app_context():
        mod.sync_pilot_slice()
        mod.db.session.commit()


def C(kind, score, title):
    return {'kind': kind, 'score': score, 'title': title, 'why': [], 'formula': ''}


def test_rank_todo_prefers_variety_then_score_and_is_deterministic():
    cands = [C('student', 10, 'b'), C('student', 9, 'a'), C('misconception', 6, 'x'), C('objective', 4, 'o'), C('section', 1, 's')]
    top = BR.rank_todo(cands)
    assert [t['kind'] for t in top] == ['student', 'misconception', 'objective']
    assert BR.rank_todo(list(reversed(cands))) == top
    only = [C('student', 5, 'b'), C('student', 5, 'a'), C('student', 1, 'c')]
    assert [t['title'] for t in BR.rank_todo(only)] == ['a', 'b', 'c']


def test_briefing_page_access_and_contents(instructor, instructor2, student):
    r = instructor.get('/instructor/section/1/briefing')
    h = r.data.decode()
    assert r.status_code == 200
    for part in ('to do today', 'Mix-ups to re-teach', 'Objectives most of the class has not mastered',
                 'Sections the class skimmed or skipped', 'Who to check in with', 'Recent results', 'Coming up',
                 'nothing is sent', 'No AI model writes any of it'):
        assert part in h, part
    assert instructor2.get('/instructor/section/1/briefing').status_code == 403
    assert student.get('/instructor/section/1/briefing').status_code == 403


def test_briefing_exports_text_and_csv(instructor):
    t = instructor.get('/instructor/section/1/briefing.txt')
    assert t.status_code == 200 and t.mimetype == 'text/plain' and 'TOP 3 TODAY' in t.data.decode()
    assert 'attachment' in t.headers['Content-Disposition']
    c = instructor.get('/instructor/section/1/briefing.csv')
    assert c.status_code == 200 and c.data.decode().splitlines()[0] == 'part,rank,item,detail,score,score_formula,demo_data'


@pytest.fixture
def mixups(app, mod):
    """Two students answer the chapter-1 check with tagged wrong answers."""
    with app.app_context():
        quiz = (mod.Quiz.query.join(mod.Module).filter(mod.Module.course_id == 1, mod.Module.order == 1).order_by(mod.Quiz.id).first())
        items = json.loads(quiz.questions)
        answers = {}
        for i, it in enumerate(items):
            tagged = [dd for (b, dd) in MCS.TAGS if b == it.get('bank_id')]
            answers[str(i)] = tagged[0] if tagged else next(o for o in it['options'] if o != it['correct'])
        users = [mod.User.query.filter_by(email=f'student{n}@lms.local').first() for n in (5, 6)]
        ids = []
        for u in users:
            a = mod.QuizAttempt(user_id=u.id, quiz_id=quiz.id, answers=json.dumps(answers), score=0,
                                completed_at=mod.utcnow() - timedelta(hours=2), section_id=1)
            mod.db.session.add(a); mod.db.session.flush(); ids.append(a.id)
        mod.db.session.commit()
        uids = [u.id for u in users]
    yield uids
    with app.app_context():
        for i in ids:
            mod.db.session.delete(mod.db.session.get(mod.QuizAttempt, i))
        M = app.extensions['ciwt_mastery'].models
        for u in uids:
            M.MasteryDecision.query.filter_by(user_id=u).delete()
            M.MasteryOverride.query.filter_by(user_id=u).delete()
        mod.db.session.commit()


def test_class_mixup_becomes_a_reteach_with_lesson_content_and_a_question(app, mod, instructor, mixups):
    with app.test_request_context():
        b = app.extensions['ciwt_mastery'].briefing['build'](mod.db.session.get(mod.ClassSection, 1))
    mc_todo = [t for t in b['todo'] if t['kind'] == 'misconception']
    assert mc_todo and mc_todo[0]['score'] == 3 * len(mc_todo[0]['users']) and len(mc_todo[0]['users']) >= 2
    ours = {v for (bank, _), v in MCS.TAGS.items() if bank.startswith('Q1.')}
    mine = [a for a in b['misconceptions'] if a['mc'] in ours and set(mixups) <= {u.id for u in a['users']}]
    assert mine and all(a['active'] >= 2 for a in mine)
    with app.test_request_context():
        cmap = app.extensions['ciwt_mastery'].engine.course_map(mod.db.session.get(mod.ClassSection, 1))
        rt = BR.reteach_for(mine[0]['mc'], cmap, None)
    top = b['reteach'][0]
    assert rt['fix'] == MCS.MISCONCEPTIONS[rt['mc']]['fix']                    # course wording, not generated
    assert rt['blocks'] and sum(s['min'] for s in rt['steps']) == 5
    assert rt['question'] and rt['question']['distractor'] in rt['question']['options']
    assert any(r['kind'] == 'quiz' and r['attempts'] >= 2 and r['mean'] == 0 for r in b['results'])
    h = instructor.get('/instructor/section/1/briefing').data.decode()
    assert f'id="rt-{top["mc"]}"' in h and 'Ask the room' in h and 'The mix-up' in h


def test_assign_from_briefing_only_touches_enrolled_students(app, mod, instructor, mixups):
    with app.app_context():
        outsider = mod.User.query.filter_by(email='student25@lms.local').first().id
    r = instructor.post('/instructor/section/1/briefing/assign',
                        data={'obj': 'IT-1.1', 'user_ids': ','.join(map(str, mixups + [outsider])), 'note': 'From the briefing'})
    assert r.status_code == 303
    with app.app_context():
        M = app.extensions['ciwt_mastery'].models
        got = {o.user_id for o in M.MasteryOverride.query.filter_by(section_id=1, target='IT-1.1', kind='force_review', active=True)}
        assert set(mixups) <= got and outsider not in got
        M.MasteryOverride.query.filter_by(user_id=outsider).delete(); mod.db.session.commit()
    assert instructor.post('/instructor/section/1/briefing/assign', data={'obj': 'IT-1.1', 'user_ids': '1'}).status_code == 303


@pytest.fixture
def helix_rows(app, mod):
    """Two consented students read lesson 1, only its first section (test rows)."""
    hx = mod.HelixGazeSession
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        cmap = app.extensions['ciwt_mastery'].engine.course_map(sec)
        from mastery import content as Cn
        lid = next(iter(cmap['lesson_by_id']))
        heads = [s['heading'] for s in Cn.sections(cmap['lesson_by_id'][lid]['html'])]
        made = []
        users = [mod.User.query.filter_by(email=f'student{n}@lms.local').first() for n in (7, 8)]
        for u in users:
            c = mod.HelixConsent(user_id=u.id, policy_version=mod.HELIX_POLICY_VERSION)
            s = hx(user_id=u.id, section_id=1, lesson_id=lid, total_ms=120000, is_demo=False)
            mod.db.session.add_all([c, s]); mod.db.session.flush()
            b = mod.HelixAoiBucket(session_id=s.id, user_id=u.id, section_id=1, lesson_id=lid, aoi_key='h0',
                                   aoi_label=heads[0], aoi_kind='heading', dwell_ms=50000, visits=1)
            mod.db.session.add(b); made += [c, s, b]
        mod.db.session.commit()
        ids = [(type(x), x.id) for x in made]
    yield heads
    with app.app_context():
        for t, i in reversed(ids):
            mod.db.session.delete(mod.db.session.get(t, i))
        mod.db.session.commit()


def test_skipped_sections_come_from_consented_helix_reading_only(app, mod, helix_rows):
    with app.test_request_context():
        b = app.extensions['ciwt_mastery'].briefing['build'](mod.db.session.get(mod.ClassSection, 1))
    heads = {x['heading'] for x in b['skims']}
    assert helix_rows[0] not in heads and set(helix_rows[1:]) <= heads
    assert all(x['measured'] == 2 and x['skipped'] == 2 for x in b['skims'] if x['heading'] in helix_rows[1:])
    assert b['helix_n'] >= 2


def test_instructor_home_shows_the_briefing_card(instructor):
    h = instructor.get('/instructor').data.decode()
    assert 'Today’s briefing' in h and '/instructor/section/1/briefing' in h


def test_briefing_never_sends_anything():
    import inspect
    src = inspect.getsource(BR).lower()
    for word in ('smtplib', 'sendmail', 'send_message', 'requests.post', 'urlopen'):
        assert word not in src
