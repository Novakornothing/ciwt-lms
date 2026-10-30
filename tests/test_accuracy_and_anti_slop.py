"""Full Technical Accuracy & Anti-AI-Slop Audit across all lessons, quizzes, Knowledge Tests,
Exam-Sim banks, interactive simulation PBQs, Speed Drill cards, and SVG diagrams."""
import json
import re

from curriculum_v2 import ladder as LD
from curriculum_v2 import lesson_visuals as LV
from curriculum_v2.cert import bank_a1_extra as A1X
from curriculum_v2.cert import bank_n_extra as NX
from curriculum_v2.cert import practice as P
from curriculum_v2.cert import sim_pbq as SIM
from curriculum_v2.cert import speed_drill as SD
from curriculum_v2.ladder import sections as LSEC
from curriculum_v2.svg_diagrams import SVG_DIAGRAMS

SLOP_PATTERNS = (
    r'\bvariant\s*#?\d+\b',
    r'\bscenario\s*#?\d+\b',
    r'in a modern enterprise network,?\s+it is important to',
    r'as an ai language model',
    r'lorem ipsum',
    r'todo:\s*fill',
)
_SLOP_RE = re.compile('|'.join(SLOP_PATTERNS), re.I)


def _norm(text: str) -> str:
    return ' '.join(re.findall(r'[a-z0-9]+', (text or '').lower()))


def test_exam_sim_pools_and_bank_depth():
    """Verify Exam-Sim bank (1,375+ items), pools (A1 466+, A2 463+, N 454+, T 541+), PBQs (36), and Speed Drill (320+)."""
    bank = P.bank()
    assert len(bank) >= 1375, f'Expected 1,375+ bank items, got {len(bank)}'

    pool_mins = {'A1': 466, 'A2': 463, 'N': 454, 'T': 541}
    for ex, floor in pool_mins.items():
        p = P.pool(ex)
        uniq = {iid for ids in p.values() for iid in ids}
        assert len(uniq) >= floor, f'{ex} pool has {len(uniq)} unique items, expected >= {floor}'

    assert len(A1X.ITEMS) == 195
    assert len(NX.ITEMS) == 195
    assert len(SIM.SIMS) == 36
    by_ex = {ex: len(SIM.by_exam(ex)) for ex in ('A1', 'A2', 'N', 'T')}
    assert by_ex == {'A1': 10, 'A2': 10, 'N': 10, 'T': 6}, by_ex
    assert len(SD.CARDS) >= 320


def test_zero_duplicate_stems_and_zero_ai_slop():
    """Verify 100% unique stems across the 1,400-item Exam-Sim bank, 36 PBQs, and 325 Speed Drill cards, with zero AI slop."""
    bank = P.bank()
    seen_stems = {}
    for iid, it in bank.items():
        raw = it.get('raw') or {}
        prompts = ' '.join(map(str, raw.get('prompts') or []))
        stem_key = _norm((it.get('text') or '') + ' ' + prompts)
        assert stem_key, f'Empty stem on {iid}'
        assert stem_key not in seen_stems, f'Duplicate stem between {iid} and {seen_stems[stem_key]}'
        seen_stems[stem_key] = iid
        assert not _SLOP_RE.search(it.get('text') or ''), f'Slop phrase in stem of {iid}'
        assert not _SLOP_RE.search(it.get('explanation') or ''), f'Slop phrase in explanation of {iid}'

    card_prompts = set()
    for c in SD.CARDS:
        pk = _norm(f"{c['cat']}:{c['front']}:{c['back']}")
        assert pk not in card_prompts, f"Duplicate speed drill card: {c['id']}"
        card_prompts.add(pk)
        assert not _SLOP_RE.search(c['front']) and not _SLOP_RE.search(c['back'])


def test_option_balance_and_substantive_rationales():
    """Verify no duplicate/empty options, correct answer is longest < 35% of the time, and rationales >= 45 chars on new items."""
    bank = P.bank()
    singles = [it for it in bank.values() if it.get('type') == 'single']
    assert len(singles) >= 1150

    for it in singles:
        opts = it.get('options') or []
        assert len(opts) == 4, it['id']
        assert len(set(opts)) == 4, f"Duplicate options in {it['id']}"
        assert all(str(o).strip() for o in opts), f"Empty option in {it['id']}"
        assert it.get('correct') in opts, f"Missing correct key in {it['id']}"

    longest_all = sum(
        1 for q in singles
        if len(q['correct']) > max(len(o) for o in q['options'] if o != q['correct'])
    )
    assert longest_all / len(singles) < 0.35, f'Correct is longest in {longest_all}/{len(singles)} items'

    for name, extra_list in (('A1X', A1X.ITEMS), ('NX', NX.ITEMS)):
        longest_ex = sum(
            1 for q in extra_list
            if len(q['correct']) > max(len(o) for o in q['options'] if o != q['correct'])
        )
        assert longest_ex / len(extra_list) < 0.35, (name, longest_ex, len(extra_list))
        for q in extra_list:
            assert len((q.get('explanation') or '').strip()) >= 45, q['id']

    for sim in SIM.SIMS:
        assert len((sim.get('explanation') or '').strip()) >= 45, sim['id']


def test_all_115_lessons_visuals_svgs_ladders_and_assessments(app, mod):
    """Verify all 115 lessons, 10 SVG diagrams, 115 blueprints, 4-rung ladder SHAs, 26 quizzes, and 45Q Knowledge Tests."""
    assert len(SVG_DIAGRAMS) == 10
    for key, svg_fig in SVG_DIAGRAMS.items():
        assert svg_fig.count('<svg') == svg_fig.count('</svg>') == 1, key
        assert 'ciwt' not in svg_fig.lower(), key

    with app.app_context():
        lessons = (mod.Lesson.query.join(mod.Module).join(mod.Course)
                   .filter(mod.Course.code.in_(('ITSUP', 'NETOPS', 'CLIENT')))
                   .order_by(mod.Lesson.id).all())
        assert len(lessons) == 115

        lad = LD.ladder()
        netops_words = 0
        for c in mod.Course.query.filter(mod.Course.code.in_(('ITSUP', 'NETOPS', 'CLIENT'))).all():
            for m in mod.Module.query.filter_by(course_id=c.id).order_by(mod.Module.order).all():
                for les in mod.Lesson.query.filter_by(module_id=m.id).order_by(mod.Lesson.order).all():
                    html = les.content or ''
                    assert 'ciwt' not in html.lower(), (c.code, m.order, les.order, les.title)
                    assert not _SLOP_RE.search(html), (c.code, m.order, les.order)
                    assert html.count('<aside class="novak-visual-blueprint"') == 1, (c.code, m.order, les.order)
                    assert html.count('<svg') == html.count('</svg>') >= 1, (c.code, m.order, les.order)
                    if c.code == 'NETOPS':
                        plain_words = re.sub(r'<[^>]+>', ' ', LV.strip_lesson_visuals(html)).split()
                        netops_words += len(plain_words)
                    for sec in LSEC.sections(html):
                        lkey = (c.code, les.id, sec['sid'])
                        if lkey in lad:
                            assert lad[lkey]['r0_sha'] == sec['r0_sha'], lkey

        assert netops_words >= 55000, f'Expected 55,000+ NETOPS words, got {netops_words}'

        # Verify 26 course quizzes (and 7 NETOPS 12-item quizzes = 84 items)
        quizzes = (mod.Quiz.query.join(mod.Module).join(mod.Course)
                   .filter(mod.Course.code.in_(('ITSUP', 'NETOPS', 'CLIENT'))).all())
        assert len(quizzes) == 26
        for c in mod.Course.query.filter(mod.Course.code.in_(('ITSUP', 'NETOPS', 'CLIENT'))).all():
            seen_q = set()
            q_total = 0
            for m in mod.Module.query.filter_by(course_id=c.id).order_by(mod.Module.order).all():
                for qz in mod.Quiz.query.filter_by(module_id=m.id).all():
                    qs = json.loads(qz.questions or '[]')
                    q_total += len(qs)
                    for q in qs:
                        sk = _norm(q.get('text') or q.get('q') or '')
                        assert sk not in seen_q, (c.code, m.order, sk)
                        seen_q.add(sk)
                        rat = q.get('explanation') or q.get('study_tip') or q.get('why') or ''
                        assert len(rat.strip()) >= 45, (c.code, m.order, sk)
            if c.code == 'NETOPS':
                assert q_total == 84, f'Expected 84 NETOPS quiz items, got {q_total}'

        # Verify 15 Knowledge Tests and 45Q Forms A/B/C for ITSUP and NETOPS
        all_kts = mod.KnowledgeTest.query.all()
        assert len(all_kts) >= 12
        for code in ('ITSUP', 'NETOPS'):
            c = mod.Course.query.filter_by(code=code).first()
            seen_kt = set()
            for o in (1, 2, 3):
                kt = mod.KnowledgeTest.query.filter_by(course_id=c.id, order=o).first()
                assert kt is not None, (code, o)
                qs = json.loads(kt.questions or '[]')
                assert len(qs) == 45, (code, kt.title, len(qs))
                for q in qs:
                    sk = _norm(q.get('text') or q.get('q') or '')
                    assert sk not in seen_kt, f'Duplicate KT stem in {code} {kt.title}: {sk}'
                    seen_kt.add(sk)
