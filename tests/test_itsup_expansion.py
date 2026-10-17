"""Pass 9: ITSUP chapters 7–13 expansion — content depth, accessibility of diagrams, item quality and tagging."""
import collections
import re

import pytest

import lessons
from curriculum_v2 import course_package as CP
from curriculum_v2 import documents as D
from curriculum_v2.itsup_core import EXPANDED_CHAPTERS, EXPANSION, GLOSSARY_ADD, ITSUP_CORE, LABS_ADD, PENDING, SOURCES
from curriculum_v2.objectives import OBJECTIVES


def _words(html):
    return len(re.sub(r'<[^>]+>', ' ', html).split())


def _chapter(n):
    return next(ch for ch in lessons.APLUS if ch['order'] == n)


STRONG_FLOOR = 3000   # chapter 2, one of the two strongest originals, has about 3,650 words


def test_expanded_chapters_exist():
    assert EXPANDED_CHAPTERS, 'no pass-9 chapters loaded'
    assert set(EXPANDED_CHAPTERS) <= set(range(7, 14))


@pytest.mark.parametrize('n', range(7, 14))
def test_chapter_depth_matches_strong_chapters(n):
    if n not in EXPANDED_CHAPTERS:
        pytest.skip(f'chapter {n} not expanded yet')
    ch = _chapter(n)
    assert sum(_words(l['html']) for l in ch['lessons']) >= STRONG_FLOOR
    for les in ch['lessons']:
        assert (n, int(les['order'])) in ITSUP_CORE, f'lesson {n}.{les["order"]} has no core content'


@pytest.mark.parametrize('key', sorted(ITSUP_CORE))
def test_every_core_lesson_has_required_parts(key):
    spec = ITSUP_CORE[key]
    html = spec['html']
    assert 3 <= len(spec['objectives']) <= 5
    verbs = ('Apply', 'Write', 'Justify', 'Record', 'Classify', 'Determine', 'Choose', 'Verify', 'Assemble', 'Resolve',
             'Decide', 'Communicate', 'Compare', 'Plan', 'Configure', 'Use', 'Interpret', 'Explain', 'Identify', 'Run',
             'Diagnose', 'Isolate', 'Select', 'Collect', 'Distinguish', 'Respond', 'Contain', 'Preserve', 'Evaluate',
             'Create', 'Navigate', 'Read', 'Set', 'Recover', 'Map', 'Describe', 'Calculate', 'Document', 'Prepare',
             'Test', 'Replace', 'Confirm', 'Reset', 'Locate', 'Draft', 'Perform', 'Protect', 'Analyze', 'Recognise',
             'Estimate', 'Troubleshoot', 'Restore', 'Move', 'Share', 'Back', 'Route', 'Connect', 'Manage')
    for o in spec['objectives']:
        assert o.split()[0] in verbs, f'{key}: objective does not start with a measurable verb: {o}'
    assert 'class="check-box cfu"' in html and html.count('<details>') >= 2, f'{key}: needs ≥ 2 check-for-understanding questions'
    assert PENDING in html, f'{key}: not tagged {PENDING}'
    assert _words(html) >= 300, f'{key}: core content too short'


@pytest.mark.parametrize('n', range(7, 14))
def test_each_chapter_has_worked_example_scenario_and_described_diagram(n):
    if n not in EXPANDED_CHAPTERS:
        pytest.skip()
    html = ''.join(v['html'] for (c, _l), v in ITSUP_CORE.items() if c == n)
    assert 'worked-example' in html and 'scenario-box' in html
    figs = re.findall(r'<figure class="lesson-figure" id="([^"]+)">(.*?)</figure>', html, re.S)
    assert figs, f'chapter {n}: no diagram'
    for fid, body in figs:
        assert f'role="img" aria-labelledby="{fid}-t {fid}-d"' in body
        assert re.search(rf'<title id="{fid}-t">[^<]+</title><desc id="{fid}-d">[^<]{{60,}}</desc>', body), fid
        assert '<figcaption>' in body and 'Text description of the diagram' in body


def test_figure_ids_are_unique():
    ids = re.findall(r'<figure class="lesson-figure" id="([^"]+)"', ''.join(v['html'] for v in ITSUP_CORE.values()))
    assert len(ids) == len(set(ids))


def test_core_is_applied_and_hidden_tag_is_instructor_only():
    for (c, l), _spec in ITSUP_CORE.items():
        les = next(x for x in _chapter(c)['lessons'] if int(x['order']) == l)
        assert 'class="sublesson core-content"' in les['html']
        assert les['html'].count('class="lo-panel"') == 1
        # the SME tag lives in an instructor-note block, which render_lesson strips for students
        assert re.search(r'<div class="instructor-note"><h4>' + PENDING, les['html'])


def test_client_course_inherits_expanded_chapters():
    for n in EXPANDED_CHAPTERS:
        if n >= 8:
            client = lessons.CLIENT[n - 8]
            assert 'core-content' in client['lessons'][0]['html']


# ------------------------------------------------------------------------------------------- items
def _ratio(q):
    others = [o for o in q['options'] if o != q['correct']]
    return len(q['correct']) / (sum(map(len, others)) / 3)


def test_items_per_objective():
    counts = collections.Counter(q['obj'] for q in EXPANSION)
    for n in EXPANDED_CHAPTERS:
        for k, v in OBJECTIVES.items():
            if v['course'] == 'ITSUP' and v['chapter'] == n:
                assert counts[k] >= 2, f'{k}: {counts[k]} items'


def test_items_are_well_formed():
    ids = [q['bank_id'] for q in EXPANSION]
    assert len(ids) == len(set(ids))
    stems = [q['text'] for q in EXPANSION]
    assert len(stems) == len(set(stems))
    for q in EXPANSION:
        assert len(q['options']) == 4 and len(set(q['options'])) == 4 and q['correct'] in q['options'], q['bank_id']
        assert q['obj'] in OBJECTIVES and OBJECTIVES[q['obj']]['course'] == 'ITSUP', q['bank_id']
        assert len(q['explanation']) >= 40, q['bank_id']
        assert q['review'] == PENDING
        blob = ' '.join([q['text']] + q['options']).lower()
        assert 'comptia' not in blob and 'all of the above' not in blob and 'none of the above' not in blob, q['bank_id']


def test_distractors_are_similar_length():
    bad = {q['bank_id']: round(_ratio(q), 2) for q in EXPANSION if not 0.67 <= _ratio(q) <= 1.5}
    assert bad == {}
    longest = sum(1 for q in EXPANSION if len(q['correct']) == max(len(o) for o in q['options']))
    assert longest <= len(EXPANSION) * 0.4, f'key is the longest option in {longest}/{len(EXPANSION)} items'


def test_key_positions_are_balanced():
    pos = collections.Counter(q['options'].index(q['correct']) for q in EXPANSION)
    n = len(EXPANSION)
    assert all(abs(pos[i] - n / 4) <= 1 for i in range(4)), pos


# ------------------------------------------------------------------------------------------- package
def test_glossary_terms_added_and_tagged():
    terms = [t for t, _d in CP.GLOSSARY]
    assert len(terms) == len({t.lower() for t in terms})
    assert {t for t, _d in GLOSSARY_ADD} <= set(terms)
    doc = D.build('glossary', 'ITSUP')
    assert any(b[0] == 'note' and 'pending sme review' in b[1].lower() for b in doc['blocks'])


@pytest.mark.parametrize('code', ['ITSUP', 'CLIENT'])
def test_lesson_plans_and_labs_are_tagged(code):
    for n in EXPANDED_CHAPTERS:
        ch = n - 7 if code == 'CLIENT' else n
        if code == 'CLIENT' and n < 8:
            continue
        p = CP.lesson_plan(code, ch)
        assert p['review'] == PENDING and p['cfu'] and p['worked_example'], (code, ch)
    plans = D.build('lesson-plans', code)
    assert sum(1 for b in plans['blocks'] if b[0] == 'note' and PENDING in b[1]) >= len([n for n in EXPANDED_CHAPTERS if code == 'ITSUP' or n >= 8])
    for lab in LABS_ADD.values():
        assert lab['review'] == PENDING and lab['rubric'] in CP.RUBRICS
        assert set(lab['objectives']) <= set(OBJECTIVES)


def test_answer_key_has_tagged_item_bank():
    key = next(k for k in CP.answer_keys('ITSUP') if k.get('review'))
    assert len(key['rows']) == len(EXPANSION)
    doc = D.build('answer-key', 'ITSUP')
    assert any(b[0] == 'note' and 'pending SME review' in b[1] for b in doc['blocks'])


def test_sources_are_named_not_invented():
    for k, v in SOURCES.items():
        assert any(org in v for org in ('Microsoft', 'Apple', 'NIST', 'CISA', 'IETF', 'Linux', 'IEEE')), k
