"""Validate the explanation ladder and report coverage (pass 19).

  python tools/ladder_check.py                       # validate every ladder file + coverage of every course
  python tools/ladder_check.py --course NETOPS       # one course (coverage); validation still covers all files
  python tools/ladder_check.py --course ITSUP --chapter 1 --sections   # list each section and its status
  python tools/ladder_check.py --scaffold ITSUP 7    # print a skeleton chNN.py for a chapter (sids, headings, r0_sha)
  python tools/ladder_check.py --json out.json --strict

Coverage reads the lessons from a throwaway COPY of ciwt_lms.db (or --db PATH, which must not be ciwt_lms.db), after
the app's start-up content sync, i.e. exactly the lesson HTML students get. Exit 1 on any error (or warning with
--strict). Two coverage numbers per course and chapter:
  * covered  = laddered (R1-R4 + checks) or same_as (a true duplicate of a laddered section in the same lesson).
               THE TARGET IS 100%: every element of every lesson gets a ladder, activity and reference sections too.
  * indexed  = covered + skip (a documented reason). Skips are counted and listed; the target is 0 skips.
--max-skips N exits 1 when more than N sections in scope are skips; --require-complete exits 1 on any missing or
stale section. Without --db, the lessons come from a copy of ciwt_lms.db, or (no ciwt_lms.db, e.g. a fresh
worktree) from a fresh database the app seeds itself; lesson HTML is synced from the python sources either way.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

ap = argparse.ArgumentParser()
ap.add_argument('--course'); ap.add_argument('--chapter', type=int)
ap.add_argument('--db', default=''); ap.add_argument('--json', default='')
ap.add_argument('--sections', action='store_true'); ap.add_argument('--strict', action='store_true')
ap.add_argument('--scaffold', nargs=2, metavar=('COURSE', 'CHAPTER'))
ap.add_argument('--stamp', nargs=2, metavar=('COURSE', 'CHAPTER'), help='print the STAMPS dict (r0_sha of each laddered section)')
ap.add_argument('--no-coverage', action='store_true', help='static validation only (no database needed)')
ap.add_argument('--require-complete', action='store_true', help='exit 1 if any section in scope is missing or stale')
ap.add_argument('--max-skips', type=int, default=None, help='exit 1 if more than N sections in scope are skips (target 0)')
a = ap.parse_args()

from curriculum_v2 import ladder as L                     # noqa: E402
from curriculum_v2.ladder import schema as S, sections as SEC  # noqa: E402
from curriculum_v2.misconceptions import MISCONCEPTIONS   # noqa: E402
from curriculum_v2.objectives import OBJECTIVES as _BASE_OBJECTIVES  # noqa: E402
from curriculum_sec.objectives import SEC_OBJECTIVES     # noqa: E402
OBJECTIVES = dict(_BASE_OBJECTIVES)
OBJECTIVES.update(SEC_OBJECTIVES)

errors, warnings = list(L.duplicates()), []
try:
    import interactive_labs as IL
    labs = {lab['id'] for lab in IL.LABS}
except Exception as e:                                    # labs catalogue unavailable: skip lab-id checks
    labs = None
    warnings.append(f'lab catalogue not loaded ({e!r}); lab ids not checked')
for mod in L.modules():
    e, w = S.validate_module(mod, OBJECTIVES, MISCONCEPTIONS, labs)
    errors += e; warnings += w

report = {'schema': S.SCHEMA, 'files': [m.__name__ for m in L.modules()], 'courses': {}}


def lessons_from_db():
    db = a.db
    if db and os.path.realpath(db).endswith('ciwt_lms.db'):
        sys.exit('--db must be a copy, not ciwt_lms.db')
    if not db:
        tmp = tempfile.mkdtemp(prefix='ladder-')
        db = os.path.join(tmp, 'copy.db')
        real = os.path.join(ROOT, 'ciwt_lms.db')
        if os.path.exists(real):
            shutil.copy2(real, db)       # else: a fresh DB, seeded and synced by the app on import
    os.environ['DATABASE_URL'] = 'sqlite:///' + db
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        import app as A
    out = []
    with A.app.app_context():
        for c in A.Course.query.order_by(A.Course.id):
            for m in A.Module.query.filter_by(course_id=c.id).order_by(A.Module.order):
                for les in A.Lesson.query.filter_by(module_id=m.id).order_by(A.Lesson.order):
                    out.append({'course': c.code, 'chapter': m.order, 'label': SEC.lesson_label(les.title),
                                'title': les.title, 'lesson_id': les.id, 'html': les.content or ''})
    return out


if a.scaffold:
    course, ch = a.scaffold[0].upper(), int(a.scaffold[1])
    ls = [x for x in lessons_from_db() if x['course'] == course and x['chapter'] == ch]
    print(f'"""Explanation ladder — {course} chapter {ch}. Pending SME review. See docs/EXPLANATION_LADDER.md."""')
    print('from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,\n'
          '                                         tryit, visual)\n\nSCHEMA = 1\nCOURSE = %r\nCHAPTER = %d\n\nMISCONCEPTIONS = {}\n\nLESSONS = {' % (course, ch))
    for x in ls:
        print(f'    {x["label"]!r}: {{   # {x["title"]}')
        for s in SEC.sections(x['html']):
            print(f'        {s["sid"]!r}: None,   # [{s["kind"]}] {s["heading"]!r}  r0_sha={s["r0_sha"]}  {len(SEC.text_of(s["html"]).split())} words')
        print('    },')
    print('}')
    sys.exit(0)

if a.stamp:
    course, ch = a.stamp[0].upper(), int(a.stamp[1])
    lad = L.ladder()
    print('STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)')
    for x in lessons_from_db():
        if x['course'] == course and x['chapter'] == ch:
            secs = [s for s in SEC.sections(x['html']) if (lad.get((course, x['label'], s['sid'])) or {}).get('type') == 'section']
            if secs:
                print(f'    {x["label"]!r}: {{' + ', '.join(f'{s["sid"]!r}: {s["r0_sha"]!r}' for s in secs) + '},')
    print('}')
    sys.exit(0)

if not a.no_coverage:
    lad = L.ladder()
    used = set()
    per = defaultdict(Counter)
    per_ch = defaultdict(Counter)
    rows = []
    for x in lessons_from_db():
        if a.course and x['course'] != a.course.upper():
            continue
        if a.chapter and x['chapter'] != a.chapter:
            continue
        for s in SEC.sections(x['html']):
            k = (x['course'], x['label'], s['sid'])
            ent = lad.get(k)
            used.add(k)
            st = 'missing'
            if ent:
                st = {'section': 'laddered', 'same_as': 'same_as', 'skip': 'skip'}.get(ent.get('type'), 'invalid')
                if (ent.get('heading') or '').strip() != s['heading']:
                    errors.append(f'{k}: heading {ent.get("heading")!r} does not match the lesson {s["heading"]!r}')
                tgt = L.entry(*k)
                if ent.get('type') == 'section':
                    S.validate_against_lesson(str(k), ent, s['html'], s['r0_sha'], errors, warnings)
                    if not ent.get('r0_sha'):
                        warnings.append(f'{k}: no r0 stamp (add it to STAMPS; see --stamp)')
                    elif ent['r0_sha'] != s['r0_sha']:
                        st = 'stale'
                elif ent.get('type') == 'same_as' and not tgt:
                    st = 'invalid'
                if st == 'invalid':
                    errors.append(f'{k}: invalid ladder entry')
            per[x['course']][st] += 1
            per[x['course']]['sections'] += 1
            per_ch[(x['course'], x['chapter'])][st] += 1
            per_ch[(x['course'], x['chapter'])]['sections'] += 1
            rows.append({'course': x['course'], 'chapter': x['chapter'], 'label': x['label'], 'sid': s['sid'],
                         'heading': s['heading'], 'kind': s['kind'], 'status': st, 'r0_sha': s['r0_sha']})
    for k in lad:
        if k not in used and (not a.course or k[0] == a.course.upper()) and not a.chapter:
            errors.append(f'{k}: ladder entry matches no section of the lesson (orphan; heading or lesson changed?)')
    skip_reasons = defaultdict(Counter)
    for r in rows:
        if r['status'] == 'skip':
            skip_reasons[r['course']][(lad.get((r['course'], r['label'], r['sid'])) or {}).get('reason', '?')] += 1
    for course, c in per.items():
        done = c['laddered'] + c['same_as'] + c['skip']
        cov = c['laddered'] + c['same_as']
        pct = (lambda n: round(100.0 * n / c['sections'], 1) if c['sections'] else 0.0)
        report['courses'][course] = dict(c, complete_pct=pct(done), indexed_pct=pct(done), covered_pct=pct(cov),
                                         skip_reasons=dict(skip_reasons[course]),
                                         chapters={ch: dict(v) for (cc, ch), v in sorted(per_ch.items()) if cc == course})
    report['sections'] = rows
    report['skips'] = [r for r in rows if r['status'] == 'skip']
    print('Coverage (concept sections). covered = laddered R1-R4 + checks or same_as (true duplicate); target 100%.')
    print('                             indexed = covered + skip; skips are counted and the target is 0.')
    for course, c in report['courses'].items():
        print(f"  {course}: {c['sections']} sections — laddered {c.get('laddered', 0)}, same_as {c.get('same_as', 0)}, "
              f"skip {c.get('skip', 0)}, missing {c.get('missing', 0)}, stale {c.get('stale', 0)} — "
              f"covered {c['covered_pct']}%, indexed {c['indexed_pct']}%")
        if c.get('skip'):
            print('      skips by reason (target 0): ' + ', '.join(f'{k} {n}' for k, n in sorted(c['skip_reasons'].items())))
        for ch, v in c['chapters'].items():
            cv = v.get('laddered', 0) + v.get('same_as', 0)
            note = [f"skip {v['skip']}" if v.get('skip') else '', f"missing {v['missing']}" if v.get('missing') else '',
                    f"stale {v['stale']}" if v.get('stale') else '']
            note = ', '.join(x for x in note if x)
            print(f"      ch{ch:>2}: covered {cv}/{v['sections']}" + (f"  ({note})" if note else ''))
    if a.sections:
        for r in rows:
            print(f"  {r['course']} {r['label']:>5} {r['status']:<9} {r['sid']}  [{r['kind']}]")

n_sec = sum(1 for e in L.ladder().values() if e.get('type') == 'section')
n_checks = sum(len(e['checks']) + sum(len(r['checks']) for r in e['rungs'].values()) for e in L.ladder().values() if e.get('type') == 'section')
print(f'Ladder files: {len(L.modules())}; laddered sections: {n_sec}; rungs: {4 * n_sec}; checks: {n_checks}; '
      f'new misconceptions: {len(L.misconceptions())}')
report.update(errors=errors, warnings=warnings, laddered_sections=n_sec, checks=n_checks)
for w in warnings:
    print('WARN ', w)
for e in errors:
    print('ERROR', e)
print(f'{len(errors)} errors, {len(warnings)} warnings')
if a.json:
    json.dump(report, open(a.json, 'w'), indent=1)
incomplete = a.require_complete and any(c.get('missing', 0) or c.get('stale', 0) for c in report['courses'].values())
if incomplete:
    print('INCOMPLETE: some concept sections in scope have no ladder (or a stale one)')
n_skips = len(report.get('skips') or [])
too_many_skips = a.max_skips is not None and n_skips > a.max_skips
if too_many_skips:
    print(f'TOO MANY SKIPS: {n_skips} skip entries in scope (allowed {a.max_skips}; target 0: give them ladders)')
sys.exit(1 if errors or incomplete or too_many_skips or (a.strict and warnings) else 0)
