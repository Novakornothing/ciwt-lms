"""Pass 12 (content round 2): cert misconception tags reach the engine, and aligned cert items join the
engine's question pools (daily review, test-out, struggle/review offers, inline checks)."""
import json

import pytest

from curriculum_v2 import misconceptions as MCS
from curriculum_v2.cert import misconceptions as CERT_MC
from curriculum_v2.cert.items import CERT_ITEMS
from mastery import engine as E


def tagged_cert_item():
    for it in CERT_ITEMS:
        if (it.get('type') or 'single') == 'single' and it['obj'].startswith('IT-'):
            for d in it['options']:
                if (it['bank_id'], d) in CERT_MC.TAGS:
                    return it, d, CERT_MC.TAGS[(it['bank_id'], d)]
    raise AssertionError('no tagged single cert item')


def test_cert_tags_are_loaded_into_the_engine_vocabulary():
    assert set(CERT_MC.MISCONCEPTIONS) <= set(MCS.MISCONCEPTIONS) and all(k.startswith('MC-C-') for k in CERT_MC.MISCONCEPTIONS)
    assert set(CERT_MC.TAGS.items()) <= set(MCS.TAGS.items())
    it, d, mc = tagged_cert_item()
    assert MCS.tag_for(it, d) == mc and MCS.tag_for(it, it['correct']) is None
    assert MCS.tag_for(dict(it, obj='IT-99.9'), d) is None              # obj must match, as for refinement's tags
    for k, v in CERT_MC.MISCONCEPTIONS.items():
        assert {'obj', 'label', 'fix', 'terms'} <= set(v), k


def test_cert_items_join_pools_after_the_class_checks_single_answer_only(app, mod):
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        cmap = eng.course_map(mod.db.session.get(mod.ClassSection, 1))
        objs = [o for o in cmap['objs'] if E.cert_items_for(o)]
        assert objs
        for obj in objs:
            pool = eng.pool(cmap, obj)
            srcs = [it['src'] for it in pool]
            assert 'cert' in srcs and srcs == sorted(srcs, key=lambda s: E.SRC_RANK[s])
            for it in pool:
                assert it['obj'] == obj and it['correct'] in it['options']
            cert_ids = {it['bank_id'] for it in pool if it['src'] == 'cert'}
            assert all(next(c for c in CERT_ITEMS if c['bank_id'] == b)['type'] == 'single' for b in cert_ids)
        # NETOPS objectives never leak into an ITSUP class
        assert not any(o.startswith('NO-') for o in cmap['objs'])


def test_pick_items_serves_cert_items_once_checks_are_used(app, mod):
    class FakeCheck:
        def __init__(self, items):
            self.kind, self.items_json = 'review', json.dumps(items)
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        cmap = eng.course_map(mod.db.session.get(mod.ClassSection, 1))
        with_both = [o for o in cmap['objs'] if E.cert_items_for(o) and any(i.get('obj') == o for i in cmap['check_items'])]
        obj = (with_both or [o for o in cmap['objs'] if E.cert_items_for(o)])[0]
        first = eng.pick_items(cmap, [obj], 1, 1, [], False)[0]
        assert first['src'] == ('check' if with_both else 'cert')
        used = [FakeCheck([{'bank_id': it['bank_id']}]) for it in eng.pool(cmap, obj) if it['src'] == 'check']
        nxt = eng.pick_items(cmap, [obj], 1, 1, used, False)[0]
        assert nxt['src'] == 'cert'
        ch = cmap['objs'][obj]['chapter']
        testout = eng.pick_items(cmap, cmap['chapter_objs'][ch], E.TESTOUT_PER_OBJ, E.TESTOUT_MAX, used, False)
        assert any(it['src'] == 'cert' for it in testout)


@pytest.fixture
def cert_review(app, mod):
    it, d, mc = tagged_cert_item()
    with app.app_context():
        M = app.extensions['ciwt_mastery'].models
        u = mod.User.query.filter_by(email='student9@lms.local').first()
        served = {'bank_id': it['bank_id'], 'obj': it['obj'], 'src': 'cert', 'text': it['text'],
                  'options': it['options'], 'correct': it['correct']}
        c = M.MasteryCheck(section_id=1, user_id=u.id, kind='review', target=it['obj'], items_json=json.dumps([served]),
                           answers_json=json.dumps({'0': d}), correct=0, total=1, passed=False, completed_at=mod.utcnow())
        mod.db.session.add(c); mod.db.session.commit()
        cid, uid = c.id, u.id
    yield uid, it, mc
    with app.app_context():
        M = app.extensions['ciwt_mastery'].models
        mod.db.session.delete(mod.db.session.get(M.MasteryCheck, cid))
        M.MasteryDecision.query.filter_by(user_id=uid).delete()
        mod.db.session.commit()


def test_a_tagged_wrong_cert_answer_becomes_a_misconception(app, mod, cert_review):
    uid, it, mc = cert_review
    with app.test_request_context():
        eng = app.extensions['ciwt_mastery'].engine
        st = eng.student_state(mod.db.session.get(mod.ClassSection, 1), mod.db.session.get(mod.User, uid), log=False)
    assert mc in st['misconceptions'] and st['misconceptions'][mc]['obj'] == it['obj']


def test_cert_switch_defaults_on_and_turns_cert_items_off(app, mod, instructor):
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        assert eng.settings(1)['cert_items'] is True
    h = instructor.get('/instructor/section/1/mastery').data.decode()
    assert 'Include certification practice items (pending SME review)' in h and 'id="mxCert" checked' in h
    r = instructor.post('/instructor/section/1/mastery/settings', data={'enabled': '1', 'testout': '1'})
    assert r.status_code in (302, 303)
    try:
        with app.test_request_context():
            eng = app.extensions['ciwt_mastery'].engine
            sec = mod.db.session.get(mod.ClassSection, 1)
            assert eng.settings(1)['cert_items'] is False
            cmap = eng.course_map(sec)
            obj = next(o for o in cmap['objs'] if E.cert_items_for(o))
            assert not [i for i in eng.pool(cmap, obj, include_cert=False) if i['src'] == 'cert']
            u = mod.User.query.filter_by(email='student1@lms.local').first()
            st = eng.student_state(sec, u, log=False)
            items = eng.pick_items(cmap, list(cmap['objs']), 3, 999, st['checks'], False, include_cert=st['settings']['cert_items'])
            assert all(i['src'] != 'cert' for i in items)
            on = eng.pick_items(cmap, list(cmap['objs']), 3, 999, st['checks'], False, include_cert=True)
            assert any(i['src'] == 'cert' for i in on)
    finally:
        instructor.post('/instructor/section/1/mastery/settings', data={'enabled': '1', 'testout': '1', 'cert_items': '1'})
    with app.app_context():
        assert app.extensions['ciwt_mastery'].engine.settings(1)['cert_items'] is True


def test_cert_items_column_migration_on_an_old_table(tmp_path):
    import sqlite3
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from mastery.models import ensure_schema
    p = tmp_path / 'old.db'
    con = sqlite3.connect(p)
    con.execute('create table mastery_setting (id integer primary key, section_id integer, enabled boolean, testout boolean, testout_bank boolean)')
    con.execute('insert into mastery_setting (section_id, enabled, testout, testout_bank) values (1, 1, 1, 0)')
    con.commit(); con.close()
    a = Flask('m'); a.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{p}'
    db = SQLAlchemy(a)
    with a.app_context():
        ensure_schema(db); ensure_schema(db)            # idempotent
    con = sqlite3.connect(p)
    assert con.execute('select cert_items from mastery_setting').fetchall() == [(1,)]
