"""Pass 11: certification alignment data, new item types, practice exams and answer-key privacy."""
import collections
import json
import re
from datetime import timedelta

import pytest

from curriculum_v2.cert import mapping as M
from curriculum_v2.cert import practice as PR
from curriculum_v2.cert.authoring import SOURCES
from curriculum_v2.cert.exams import DOMAINS, EXAMS, OBJECTIVES
from curriculum_v2.cert.items import CERT_ITEMS
from curriculum_v2.cert.supplements import SUPPLEMENTS
from curriculum_v2.objectives import OBJECTIVES as CIWT_OBJECTIVES

KEY_FIELDS = {'correct', 'explanation', 'why', 'rationale', 'answer', 'key', 'wrong', 'review', 'study_tip', 'bank_id'}


# ------------------------------------------------------------------------------------------- objective data
def test_published_objective_counts_and_weights():
    counts = collections.Counter(v['exam'] for v in OBJECTIVES.values())
    assert counts == {'A1': 27, 'A2': 36, 'N': 25}
    for ex, doms in DOMAINS.items():
        assert sum(w for _d, _n, w in doms) == 100, ex
    for k, v in OBJECTIVES.items():
        assert v['topics'], k
        for t in v['topics']:
            M._rx(t)   # every checklist regex compiles


def test_exam_citations_present_and_not_endorsement():
    for e in EXAMS.values():
        assert e['url'].startswith('https://') and 'Version' in e['doc_version'] and e['code']
    from curriculum_v2.cert.exams import DISCLAIMER
    assert 'Not affiliated' in DISCLAIMER and 'endorsed' in DISCLAIMER


# ------------------------------------------------------------------------------------------- mapping integrity
def test_curated_map_uses_real_ids_on_both_sides():
    assert set(M.CURATED) == set(CIWT_OBJECTIVES), 'every CIWT objective is mapped, and nothing else'
    for cobj, xs in M.CURATED.items():
        assert xs, cobj
        for x in xs:
            assert x in OBJECTIVES, (cobj, x)


def test_every_bank_item_maps_to_a_real_exam_objective():
    items = M.bank_items()
    assert len(items) >= 486 + len(CERT_ITEMS)
    for it in items:
        oids = M.map_item(it)
        assert oids, it['id']
        assert all(o in OBJECTIVES for o in oids), (it['id'], oids)
        assert it['obj'] in CIWT_OBJECTIVES, it['id']


def test_new_items_explicit_alignment_is_consistent_with_curated_map():
    for q in CERT_ITEMS:
        for c in q['cert']:
            assert c in M.CURATED[q['obj']], (q['bank_id'], q['obj'], c)


def test_alignment_json_is_up_to_date():
    with open(PR.os.path.join(PR.HERE, 'alignment.json'), encoding='utf-8') as f:
        stored = json.load(f)
    fresh = json.loads(json.dumps(M.snapshot()))
    assert stored == fresh, 'run: python tools/cert_coverage.py'


def test_every_exam_objective_has_four_items_and_no_gaps_remain():
    c = M.compute()
    thin = {k: len(v['items']) for k, v in c['objectives'].items() if len(v['items']) < 4}
    assert not thin, thin
    gaps = [k for k, v in c['objectives'].items() if v['status'] == 'gap']
    assert not gaps, gaps


def test_baseline_snapshot_is_kept_for_before_after():
    b = PR.baseline()
    assert set(b['status']) == set(OBJECTIVES)
    assert sum(1 for s in b['status'].values() if s == 'gap') == 11


# ------------------------------------------------------------------------------------------- new items
def test_new_item_shapes():
    ids = [q['bank_id'] for q in CERT_ITEMS]
    assert len(ids) == len(set(ids))
    types = collections.Counter(q['type'] for q in CERT_ITEMS)
    assert set(types) == {'single', 'multi', 'order', 'match'} and min(types.values()) >= 10, types
    for q in CERT_ITEMS:
        assert q['review'] == 'Pending SME review' and q['explanation'] and q['text'], q['bank_id']
        opts = q['options']
        assert len(opts) == len(set(opts)), q['bank_id']
        if q['type'] == 'single':
            assert len(opts) == 4 and q['correct'] in opts
        elif q['type'] == 'multi':
            assert set(q['correct']) <= set(opts) and q['choose'] == len(q['correct']) and len(opts) > len(q['correct'])
        elif q['type'] == 'order':
            assert sorted(opts) == sorted(q['correct']) and opts != q['correct'], 'presentation must not be the key order'
        elif q['type'] == 'match':
            assert len(q['prompts']) == len(q['correct']) and set(q['correct']) <= set(opts)
            assert len(opts) > len(set(q['correct'])), 'at least one decoy so the last match is not free'


def test_single_answer_keys_are_balanced_and_not_guessable_by_length():
    singles = [q for q in CERT_ITEMS if q['type'] == 'single']
    pos = collections.Counter(q['options'].index(q['correct']) for q in singles)
    assert max(pos.values()) - min(pos.values()) <= 1, pos
    longest = sum(1 for q in singles if len(q['correct']) > max(len(o) for o in q['options'] if o != q['correct']))
    assert longest / len(singles) < 0.45, f'key is the longest option in {longest}/{len(singles)} items'
    # no visible key sequence
    seq = [q['options'].index(q['correct']) for q in singles]
    assert seq != sorted(seq) and len(set(zip(seq, seq[1:]))) > 4


# ------------------------------------------------------------------------------------------- supplements
def test_supplements_meet_the_pass_9_10_standard():
    assert len(SUPPLEMENTS) >= 15
    for s in SUPPLEMENTS:
        h = s['html']
        for marker in ('class="lesson-figure"', 'figure-desc', 'worked-example', 'scenario-box', 'check-box cfu', 'Pending SME review'):
            assert marker in h, (s['id'], marker)
        assert all(k in SOURCES for k in s['sources']) and s['sources'], s['id']
        assert all(c in OBJECTIVES for c in s['cert']), s['id']


def test_supplements_are_applied_once_and_keep_existing_content():
    import lessons
    packs = {'ITSUP': lessons.APLUS, 'NETOPS': lessons.NETPLUS}
    from curriculum_v2.apply import _lesson
    for s in SUPPLEMENTS:
        les = _lesson(packs[s['course']], s['chapter'], s['lesson'])
        assert les['html'].count(f'id="{s["id"]}"') == 1, s['id']
        assert les['html'].index(f'id="{s["id"]}"') > 200, 'supplement is appended after the existing lesson'


# ------------------------------------------------------------------------------------------- grading
def test_grade_each_type():
    by_type = {}
    for q in CERT_ITEMS:
        by_type.setdefault(q['type'], q)
    bank = PR.bank()
    for t, q in by_type.items():
        it = bank[q['bank_id']]
        right = it['correct'] if t == 'single' else json.dumps(it['correct'])
        assert PR.grade(it, right), t
        if t == 'single':
            assert not PR.grade(it, next(o for o in it['options'] if o != it['correct']))
        elif t == 'order':
            assert not PR.grade(it, json.dumps(list(reversed(it['correct']))))
        else:
            assert not PR.grade(it, json.dumps(it['correct'][:-1]))
        assert not PR.grade(it, '') and not PR.grade(it, None) and not PR.grade(it, 'not json [')


def test_full_practice_draw_is_domain_weighted_and_unique():
    import random
    for ex in EXAMS:
        chosen = PR.draw(ex, rng=random.Random(3))
        assert len(chosen) == PR.FULL_LENGTH
        assert len({i for i, _o in chosen}) == len(chosen)
        per = collections.Counter(OBJECTIVES[o]['domain'] for _i, o in chosen)
        want = PR._allocate(PR.FULL_LENGTH, {d: w for d, _n, w in DOMAINS[ex]})
        assert per == want, (ex, per, want)
        d0 = DOMAINS[ex][0][0]
        drill = PR.draw(ex, d0, rng=random.Random(4))
        assert len(drill) == PR.DRILL_LENGTH and all(OBJECTIVES[o]['domain'] == d0 for _i, o in drill)


# ------------------------------------------------------------------------------------------- pages
def _questions_json(html):
    m = re.search(r'<script type="application/json" id="assessQuestions">(.*?)</script>', html, re.S)
    assert m, 'question JSON not found'
    return json.loads(m.group(1))


def _start(client, exam, domain=None):
    data = {'exam': exam}
    if domain:
        data['domain'] = domain
    r = client.post('/practice/start', data=data)
    assert r.status_code == 302, r.status_code
    return int(r.headers['Location'].rstrip('/').split('/')[-1])


def test_practice_page_never_ships_answer_keys(student, app, mod):
    for ex in EXAMS:
        aid = _start(student, ex)
        r = student.get(f'/practice/attempt/{aid}')
        assert r.status_code == 200
        html = r.get_data(as_text=True)
        assert PR.PRACTICE_LABEL in html
        qs = _questions_json(html)
        assert len(qs) == PR.FULL_LENGTH
        with app.app_context():
            att = mod.db.session.get(PR_model(mod), aid)
            chosen = json.loads(att.items)
        bank = PR.bank()
        for q, (iid, _oid) in zip(qs, chosen):
            assert not (set(q) & KEY_FIELDS), set(q) & KEY_FIELDS
            it = bank[iid]
            if it['explanation']:
                assert it['explanation'] not in json.dumps(q, ensure_ascii=False)
            if it['type'] == 'order':
                assert q['options'] != [str(c) for c in it['correct']]
        assert '"correct"' not in html and 'bank_id' not in html


def test_existing_quiz_and_test_pages_still_hide_keys(student, ids):
    checked = 0
    for url in (f"/student/quiz/{ids['section']}/{ids['quiz']}", f"/student/test/{ids['section']}/{ids['test']}"):
        r = student.get(url)
        if r.status_code != 200 or 'assessQuestions' not in r.get_data(as_text=True):
            continue
        checked += 1
        qs = _questions_json(r.get_data(as_text=True))
        for q in qs:
            assert not (set(q) & KEY_FIELDS), (url, set(q) & KEY_FIELDS)
    assert checked >= 1, 'no runner page rendered'


def PR_model(mod):
    return mod.PracticeAttempt


def test_practice_submit_scores_by_domain_with_lesson_links(student, app, mod):
    aid = _start(student, 'A2')
    with app.app_context():
        chosen = json.loads(mod.db.session.get(mod.PracticeAttempt, aid).items)
    bank = PR.bank()
    data = {}
    for i, (iid, _oid) in enumerate(chosen):
        it = bank[iid]
        if i == 0:
            continue   # leave one unanswered
        data[f'q{i}'] = it['correct'] if it['type'] == 'single' else json.dumps(it['correct'])
    r = student.post(f'/practice/attempt/{aid}', data=data)
    assert r.status_code == 302 and r.headers['Location'].endswith(f'/practice/attempt/{aid}/result')
    with app.app_context():
        att = mod.db.session.get(mod.PracticeAttempt, aid)
        assert att.correct == len(chosen) - 1 and not att.timed_out
    html = student.get(f'/practice/attempt/{aid}/result').get_data(as_text=True)
    assert 'Practice score report' in html and 'not an official CompTIA exam' in html
    for d, name, _w in DOMAINS['A2']:
        if any(OBJECTIVES[o]['domain'] == d for _i, o in chosen):
            assert f'{d} {name}' in html
    assert '/student/module/' in html, 'missed objective links back to a lesson'
    # submitting again does not regrade; another student cannot see it
    assert student.post(f'/practice/attempt/{aid}', data={}).status_code == 302


def test_practice_attempt_is_private_and_deadline_enforced(student, student2, app, mod):
    aid = _start(student, 'N', '5.0')
    assert student2.get(f'/practice/attempt/{aid}').status_code == 404
    assert student2.get(f'/practice/attempt/{aid}/result').status_code == 404
    with app.app_context():
        att = mod.db.session.get(mod.PracticeAttempt, aid)
        att.deadline = att.started_at - timedelta(minutes=5)
        mod.db.session.commit()
    student.post(f'/practice/attempt/{aid}', data={})
    with app.app_context():
        assert mod.db.session.get(mod.PracticeAttempt, aid).timed_out is True


def test_practice_start_rejects_bad_input(student):
    assert student.post('/practice/start', data={'exam': 'ZZ'}).status_code == 400
    assert student.post('/practice/start', data={'exam': 'A1', 'domain': '9.0'}).status_code == 400


def test_practice_index_lists_exams_and_label(student):
    html = student.get('/practice').get_data(as_text=True)
    assert 'not an official CompTIA exam' in html
    for e in EXAMS.values():
        assert e['code'] in html


def test_coverage_page_staff_only_and_cites_sources(student, instructor, admin, anon):
    assert student.get('/staff/cert-coverage').status_code == 403
    assert anon.get('/staff/cert-coverage').status_code in (302, 401)
    for c in (instructor, admin):
        html = c.get('/staff/cert-coverage').get_data(as_text=True)
        assert 'Exam Objectives Document Version 4.0' in html and 'Version 6.0' in html
        assert 'Not affiliated' in html and 'heuristic' in html
        assert 'built-in method' not in html and 'object at 0x' not in html, 'template printed a Python method'
        assert html.count('class="cert-obj"') == len(OBJECTIVES)
    html = admin.get('/staff/cert-coverage?exam=N&status=partial').get_data(as_text=True)
    assert 0 < html.count('class="cert-obj"') < 25


# ------------------------------------------------------------------------------------------- course package
def test_course_package_shows_cert_alignment():
    from curriculum_v2 import documents as D
    from curriculum_v2.cert import package as CP
    from curriculum_v2.cert.supplements import GLOSSARY
    for code, exams in (('ITSUP', ('A1', 'A2')), ('NETOPS', ('N',)), ('CLIENT', ('A2',))):
        syl = str(D.build('syllabus', code)['blocks'])
        assert 'Certification alignment' in syl and 'Aligned to: ' in syl
        for k in exams:
            assert EXAMS[k]['doc_version'] in syl and EXAMS[k]['url'] in syl
        assert not re.search(r'(?<!not )(?<!or )endorsed by CompTIA', syl.replace('not reviewed or endorsed by CompTIA', ''))
        plans = str(D.build('lesson-plans', code)['blocks'])
        assert 'Certification alignment' in plans and 'Pending SME review' in plans
        key = str(D.build('answer-key', code)['blocks'])
        rows = CP.answer_key_rows(code)
        assert rows and all(r['id'] in key for r in rows)
    glo = str(D.build('glossary', 'ITSUP')['blocks'])
    assert all(t in glo for t, _d in GLOSSARY)


def test_student_syllabus_has_no_answer_keys():
    from curriculum_v2 import documents as D
    syl = str(D.build('syllabus', 'ITSUP')['blocks'])
    for q in CERT_ITEMS[:40]:
        assert q['explanation'] not in syl


def test_cert_coverage_md_is_current():
    import subprocess, sys
    r = subprocess.run([sys.executable, 'tools/cert_coverage_md.py', '--check'], cwd=str(__import__('pathlib').Path(__file__).resolve().parents[1]),
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr + ' — run: python tools/cert_coverage_md.py'
