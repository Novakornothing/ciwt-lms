#!/usr/bin/env python3
"""Inventory the CIWT curriculum straight from the Python sources (no app import, no DB).

Writes a JSON report used by CURRICULUM_AUDIT.md and the content-integrity tests:
chapters, lessons, minutes, objectives, labs, quiz/test items, answer-key checks,
accessibility signals (img alt, media, heading order) and a reading-level estimate.

    ./venv/bin/python tools/curriculum_inventory.py out.json
"""
import json
import re
import sys
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lessons as L  # noqa: E402
import interactive_labs as IL  # noqa: E402
import pilot_slice as PS  # noqa: E402
import question_bank as QB  # noqa: E402
import skills_exams as SX  # noqa: E402
import alignment as AL  # noqa: E402
import aschool as AS  # noqa: E402

PACKS = {'ITSUP': L.APLUS, 'NETOPS': L.NETPLUS, 'CLIENT': L.CLIENT}
QUIZ_BANK_OF = {'ITSUP': lambda o: o, 'CLIENT': lambda o: o + 7}   # mirrors app.sync_pilot_slice


def text_of(html):
    html = re.sub(r'<(style|script)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', html))).strip()


def syllables(word):
    w = re.sub(r'[^a-z]', '', word.lower())
    if not w:
        return 0
    groups = re.findall(r'[aeiouy]+', w)
    n = len(groups) - (1 if w.endswith('e') and len(groups) > 1 and not w.endswith('le') else 0)
    return max(1, n)


def fk_grade(text):
    """Flesch-Kincaid grade estimate (heuristic syllable counter; prose only)."""
    sents = [s for s in re.split(r'[.!?]+\s', text) if len(s.split()) >= 3]
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", text)]
    if len(sents) < 3 or len(words) < 50:
        return None
    syl = sum(syllables(w) for w in words)
    return round(0.39 * len(words) / len(sents) + 11.8 * syl / len(words) - 15.59, 1)


def objectives(html):
    out = []
    for panel in re.findall(r'<div class="lo-panel">(.*?)</div>', html, flags=re.S):
        out += [text_of(li) for li in re.findall(r'<li>(.*?)</li>', panel, flags=re.S)]
    return out


BLOOM_MEASURABLE = set('''identify explain list name describe compare contrast classify configure install troubleshoot
diagnose verify document choose select map calculate convert apply demonstrate perform use run read write replace
differentiate distinguish summarize recognize interpret label locate point state recall determine assess evaluate
justify plan design build create implement test resolve isolate escalate record match order sequence measure set
recover restore remove disable enable assign capture analyze inspect check prioritize recommend avoid tell spot
open find follow pick give prove show compute translate'''.split())
VAGUE = ('understand', 'know', 'learn', 'appreciate', 'be aware', 'be familiar', 'get comfortable', 'feel')


def objective_quality(obj):
    first = re.sub(r'[^a-z ]', '', obj.lower()).split()
    verb = first[0] if first else ''
    if any(obj.lower().startswith(v) for v in VAGUE):
        return 'vague'
    return 'measurable' if verb in BLOOM_MEASURABLE else 'check'


def a11y(html):
    imgs = re.findall(r'<img\b[^>]*>', html, flags=re.I)
    no_alt = [i for i in imgs if not re.search(r'\balt\s*=', i, flags=re.I)]
    heads = [int(h) for h in re.findall(r'<h([1-6])\b', html, flags=re.I)]
    skips = sum(1 for a, b in zip(heads, heads[1:]) if b > a + 1)
    tables = re.findall(r'<table\b.*?</table>', html, flags=re.S | re.I)
    tables_no_th = sum(1 for t in tables if '<th' not in t.lower())
    media = len(re.findall(r'<(audio|video|iframe)\b', html, flags=re.I))
    narr = len(re.findall(r'data-narrat|speechSynthesis|narration', html, flags=re.I))
    return {'imgs': len(imgs), 'imgs_no_alt': len(no_alt), 'heading_skips': skips,
            'tables': len(tables), 'tables_no_th': tables_no_th, 'media': media, 'narration_refs': narr}


def item_checks(item):
    text = item.get('text') or item.get('q') or ''
    opts = [str(o) for o in item.get('options') or []]
    corr = item.get('correct')
    issues = []
    if corr not in opts:
        issues.append('key-not-in-options')
    if len(set(o.strip().lower() for o in opts)) != len(opts):
        issues.append('duplicate-options')
    if len(opts) < 3:
        issues.append('too-few-options')
    low = ' '.join(opts).lower()
    if 'all of the above' in low or 'none of the above' in low:
        issues.append('all/none-of-above')
    if re.search(r'\b(NOT|EXCEPT)\b', text):
        issues.append('negative-stem')
    if opts and corr in opts:
        lens = sorted(len(o) for o in opts)
        if len(corr) == lens[-1] and len(opts) > 2 and lens[-1] > 1.8 * lens[-2]:
            issues.append('longest-answer-cue')
    return issues


def main(out):
    lab_ids = set(IL.LABS_BY_ID)
    report = {'courses': {}, 'labs': {}, 'tests': {}, 'skills_exams': {}, 'problems': []}
    for lab in IL.LABS:
        report['labs'][lab['id']] = {
            'title': lab['title'], 'kind': lab['kind'], 'objectives': len(lab.get('objectives') or []),
            'hints': len(lab.get('hints') or []), 'has_intro': bool(lab.get('intro')),
            'has_success': bool(lab.get('success_msg')), 'builds_on': lab.get('builds_on') or []}
    used_labs = Counter()
    for code, pack in PACKS.items():
        chapters = []
        for ch in pack:
            o = ch['order']
            lessons = []
            for les in ch['lessons']:
                h = les.get('html') or ''
                txt = text_of(h)
                objs = objectives(h)
                labs = IL.LESSON_LABS.get((code, o, les['order']), [])
                lessons.append({
                    'order': les['order'], 'title': les['title'], 'minutes': les.get('minutes'),
                    'words': len(txt.split()), 'fk_grade': fk_grade(txt), 'objectives': objs,
                    'objective_quality': dict(Counter(objective_quality(x) for x in objs)),
                    'labs': labs, 'instructor_note': 'instructor-note' in h, 'a11y': a11y(h),
                    'sublessons': h.count('class="sublesson"'),
                })
                for lid in labs:
                    used_labs[lid] += 1
                    if lid not in lab_ids:
                        report['problems'].append(f'{code} ch{o} L{les["order"]}: unknown lab {lid}')
            ch_labs = IL.CHAPTER_LABS.get((code, o), [])
            for lid in ch_labs:
                used_labs[lid] += 1
                if lid not in lab_ids:
                    report['problems'].append(f'{code} ch{o}: unknown chapter lab {lid}')
            bank = QUIZ_BANK_OF.get(code, lambda _o: None)(o)
            quiz = PS.PILOT_CHECKS.get(bank) or []
            qissues = [(i, item_checks(q)) for i, q in enumerate(quiz)]
            chapters.append({
                'order': o, 'title': ch['title'], 'minutes': ch.get('minutes'),
                'lesson_minutes': sum(int(x.get('minutes') or 0) for x in ch['lessons']),
                'lessons': lessons, 'chapter_labs': ch_labs,
                'all_labs': sorted(set(ch_labs) | {x for les in lessons for x in les['labs']}),
                'quiz_bank': bank if quiz else None, 'quiz_items': len(quiz),
                'quiz_item_issues': [(i, x) for i, x in qissues if x],
                'quiz_has_rationale': sum(1 for q in quiz if q.get('study_tip')),
            })
        report['courses'][code] = chapters
    for code, fn in (('ITSUP', QB.tests_aplus), ('NETOPS', QB.tests_netplus)):
        tests = []
        for title, desc, order, qs in fn():
            qs = list(qs)
            tests.append({
                'title': title, 'order': order, 'items': len(qs),
                'los': dict(Counter(q.get('lo') for q in qs)),
                'categories': dict(Counter(q.get('category') for q in qs)),
                'with_explanation': sum(1 for q in qs if (q.get('explanation') or '').strip()),
                'issues': [(i, item_checks(q), (q.get('text') or '')[:90]) for i, q in enumerate(qs) if item_checks(q)],
                'key_position': dict(Counter((q['options'].index(q['correct']) if q['correct'] in q['options'] else -1) for q in qs)),
            })
        report['tests'][code] = tests
    for code in ('ITSUP', 'NETOPS', 'CLIENT'):
        exams = []
        for title, desc, order, items, minutes, passing in SX.exams_for(code):
            st = SX.stations_of(items)
            for s in st:
                if s['lab_id'] not in lab_ids:
                    report['problems'].append(f'{code} skills exam {title}: unknown lab {s["lab_id"]}')
            exams.append({'title': title, 'order': order, 'minutes': minutes, 'passing': passing,
                          'stations': [(s['lab_id'], s['area']) for s in st]})
        report['skills_exams'][code] = exams
    for course_code, doms in (('ITSUP', AL.ITSUP_DOMAINS), ('NETOPS', AL.NETOPS_DOMAINS)):
        for d in doms:
            for lid in d.get('labs') or []:
                if lid not in lab_ids:
                    report['problems'].append(f'alignment {course_code} "{d["name"]}": unknown lab {lid}')
    for b in AS.BLOCKS:
        for eo in b['eos']:
            if eo.get('lab') and eo['lab'] not in lab_ids:
                report['problems'].append(f'aschool {eo["id"]}: unknown lab {eo["lab"]}')
    for lab in IL.LABS:
        for dep in lab.get('builds_on') or []:
            if dep not in lab_ids:
                report['problems'].append(f'lab {lab["id"]} builds_on unknown {dep}')
    report['labs_unused'] = sorted(lab_ids - set(used_labs))
    Path(out).write_text(json.dumps(report, indent=1, default=str))
    # console summary
    for code, chs in report['courses'].items():
        tot_min = sum(c['lesson_minutes'] for c in chs)
        n_les = sum(len(c['lessons']) for c in chs)
        n_obj = sum(len(les['objectives']) for c in chs for les in c['lessons'])
        print(f'{code}: {len(chs)} chapters, {n_les} lessons, {tot_min/60:.1f} h lesson time, {n_obj} objectives')
        for c in chs:
            q = Counter()
            for les in c['lessons']:
                q.update(les['objective_quality'])
            fks = [les['fk_grade'] for les in c['lessons'] if les['fk_grade']]
            words = sum(les['words'] for les in c['lessons'])
            alt = sum(les['a11y']['imgs_no_alt'] for les in c['lessons'])
            print(f"  ch{c['order']:>2} {c['title'][:58]:58} les={len(c['lessons']):2} min={c['lesson_minutes']:4} words={words:6} "
                  f"obj={dict(q)} labs={len(c['all_labs'])} quiz={c['quiz_items']} fk={(sum(fks)/len(fks)) if fks else 0:.1f} noalt={alt}"
                  f"{' ISSUES=' + str(len(c['quiz_item_issues'])) if c['quiz_item_issues'] else ''}")
    for code, tests in report['tests'].items():
        for t in tests:
            print(f"  TEST {code} {t['title'][:50]:50} items={t['items']} expl={t['with_explanation']} issues={len(t['issues'])} keypos={t['key_position']} los={len(t['los'])}")
    print('problems:', len(report['problems']))
    for p in report['problems'][:40]:
        print('  ', p)
    print('labs unused:', report['labs_unused'])


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'curriculum_inventory.json')
