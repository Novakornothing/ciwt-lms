"""Measure misconception-tag coverage in the adaptive engine (content round 3).

An objective is *covered* when, among the single-answer items the engine can score for it (chapter checks and
Tests A/B/C in the seeded course DB, certification items aligned to it, the X-IT expansion bank and the exam
supplement), at least one real distractor carries a misconception tag that ``tag_for`` returns for that item, AND
that misconception yields a non-empty mix-up correction (``mastery.content.build_correction`` finds at least one
lesson section).

Also reported per objective: how many single-answer items the engine sees (the "traffic" proxy used to order
work), how many distractors exist and how many are tagged.

Run on a throwaway DB copy (never ciwt_lms.db):
    python tools/misconception_coverage.py [--json out.json]
"""
import json
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(tempfile.mkdtemp(prefix='ciwt-mccov-'), 'cov.db')
os.environ.setdefault('SECRET_KEY', 'coverage')


def _single(it):
    return ((it.get('type') or 'single') == 'single' and it.get('options') and it.get('correct') in it['options'])


def measure(app, mod):
    from mastery import content as C
    from mastery.engine import cert_items_for
    from curriculum_v2 import misconceptions as MCS
    from curriculum_v2.exam_supplement import SUPPLEMENT
    from curriculum_v2.itsup_core import EXPANSION
    out = {}
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        for code in ('ITSUP', 'NETOPS'):
            course = mod.Course.query.filter_by(code=code).first()
            sec = mod.ClassSection.query.filter_by(course_id=course.id).first()
            cmap = eng.course_map(sec)
            items = defaultdict(list)
            for it in cmap['check_items']:
                items[it['obj']].append(dict(it, _src='check'))
            for t in cmap['tests'].values():
                for q in t['qs'] if isinstance(t['qs'], list) else []:
                    if isinstance(q, dict) and q.get('obj') in cmap['objs']:
                        items[q['obj']].append(dict(q, _src='test'))
            for obj in cmap['objs']:
                items[obj] += [dict(it, _src='cert') for it in cert_items_for(obj)]
            for src, bank in (('bank', EXPANSION), ('supplement', SUPPLEMENT)):
                for it in bank:
                    if it.get('obj') in cmap['objs']:
                        items[it['obj']].append(dict(it, _src=src))
            for obj, o in cmap['objs'].items():
                info = cmap['obj_lesson'].get(obj)
                les = cmap['lesson_by_id'].get(info['lesson_id']) if info else None
                n_items = n_dis = n_tag = 0
                mcs, seen = set(), set()
                untagged, by_src = [], defaultdict(lambda: [0, 0])
                for it in items.get(obj, []):
                    if not _single(it):
                        continue
                    key = (it.get('bank_id'), ' '.join((it.get('text') or it.get('q') or '').lower().split()))
                    if key in seen:
                        continue
                    seen.add(key)
                    n_items += 1
                    hit = False
                    for d in it['options']:
                        if d == it['correct']:
                            continue
                        n_dis += 1
                        mc = MCS.tag_for(dict(it, obj=obj), d)
                        if mc:
                            n_tag += 1
                            mcs.add(mc)
                            hit = True
                    by_src[it['_src']][0] += 1
                    by_src[it['_src']][1] += int(hit)
                    if not hit:
                        untagged.append(it.get('bank_id') or it.get('ref'))
                corr = {}
                for mc in sorted(mcs):
                    r = C.build_correction(obj, o['text'], MCS.MISCONCEPTIONS[mc], les,
                                           chapter_lessons=cmap['by_ch'].get(o['chapter'], []))
                    corr[mc] = len(r['blocks'])
                with_corr = sorted(m for m, n in corr.items() if n)
                out[obj] = {'course': code, 'chapter': o['chapter'], 'text': o['text'], 'items': n_items,
                            'distractors': n_dis, 'tagged': n_tag, 'items_tagged': n_items - len(untagged),
                            'untagged_items': untagged, 'by_src': {k: v for k, v in by_src.items()}, 'misconceptions': sorted(mcs),
                            'with_correction': with_corr, 'covered': bool(with_corr)}
    return out


def summary(cov):
    objs = sorted(cov, key=lambda k: (k[:2], [int(x) for x in k.split('-')[1].split('.')]))
    tot = len(objs)
    covered = [o for o in objs if cov[o]['covered']]
    dis = sum(cov[o]['distractors'] for o in objs)
    tag = sum(cov[o]['tagged'] for o in objs)
    src = defaultdict(lambda: [0, 0])
    for o in objs:
        for k, (n, t) in cov[o]['by_src'].items():
            src[k][0] += n
            src[k][1] += t
    return {'objectives': tot, 'covered': len(covered), 'items': sum(cov[o]['items'] for o in objs),
            'items_tagged': sum(cov[o]['items_tagged'] for o in objs), 'items_by_source': dict(src),
            'one_misconception_only': [o for o in objs if len(cov[o]['with_correction']) == 1], 'uncovered': [o for o in objs if not cov[o]['covered']],
            'distractors': dis, 'tagged_distractors': tag,
            'by_course': {c: [sum(1 for o in objs if cov[o]['course'] == c and cov[o]['covered']),
                              sum(1 for o in objs if cov[o]['course'] == c)] for c in ('ITSUP', 'NETOPS')}}


def main(argv):
    import app as lms
    cov = measure(lms.app, lms)
    s = summary(cov)
    print(f"objectives covered: {s['covered']}/{s['objectives']}  (ITSUP {s['by_course']['ITSUP'][0]}/{s['by_course']['ITSUP'][1]}, "
          f"NETOPS {s['by_course']['NETOPS'][0]}/{s['by_course']['NETOPS'][1]})")
    print(f"tagged distractors: {s['tagged_distractors']}/{s['distractors']} scorable single-answer distractors")
    print(f"items with >=1 tagged distractor: {s['items_tagged']}/{s['items']}  by source (tagged/total): "
          + ', '.join(f"{k} {v[1]}/{v[0]}" for k, v in sorted(s['items_by_source'].items())))
    print('objectives with only one correctable misconception:', ', '.join(s['one_misconception_only']) or 'none')
    print('uncovered:', ', '.join(s['uncovered']) or 'none')
    for o in sorted(cov, key=lambda k: -cov[k]['items']):
        c = cov[o]
        print(f"  {o:8} items={c['items']:3} distractors={c['distractors']:3} tagged={c['tagged']:3} mcs={len(c['misconceptions']):2} "
              f"corr={len(c['with_correction']):2} items_tagged={c['items_tagged']:3} {'OK' if c['covered'] else '--'} "
              + ' '.join(f"{k}:{v[1]}/{v[0]}" for k, v in sorted(c['by_src'].items())))
    if '--json' in argv:
        Path(argv[argv.index('--json') + 1]).write_text(json.dumps({'summary': s, 'objectives': cov}, indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
