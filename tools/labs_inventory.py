"""Print the live-lab inventory as a Markdown table (used for LABS_AUDIT.md).

usage: python tools/labs_inventory.py [--e2e e2e.json] [--baseline baseline.json]
e2e.json is tools/labs_e2e.py --json output; baseline.json maps lab id -> {view: completed?} from the pre-change probe.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import interactive_labs as IL  # noqa: E402
import lab_runtime as RT  # noqa: E402
import labs_catalog_new as N  # noqa: E402
import labs_vm as VM  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--e2e', default='')
ap.add_argument('--baseline', default='')
ap.add_argument('--env', action='store_true', help='print the real-environment vs simulated table instead')
a = ap.parse_args()
e2e = {}
if a.e2e:
    for r in json.load(open(a.e2e)):
        e2e.setdefault(r['lab'], {})[r['view']] = r
base = json.load(open(a.baseline)) if a.baseline else {}
chap = {}
for (c, ch), ids in IL.CHAPTER_LABS.items():
    for i in ids:
        chap.setdefault(i, []).append(f"{ {'ITSUP': 'IT', 'NETOPS': 'NO', 'CLIENT': 'CL'}.get(c, c)}{ch}")
new_ids = {l['id'] for l in N.NEW_LABS}


def mark(lab_id, view):
    r = e2e.get(lab_id, {}).get(view)
    if not r:
        return '–'
    return '✅' if r['ok'] else '❌'


def bmark(lab_id, view):
    if lab_id in new_ids or lab_id.startswith('CL-'):
        return 'new' if lab_id in new_ids else '–'
    b = base.get(lab_id, {})
    if view not in b:
        return '–'
    return 'ok' if b[view] else '**fail**'


TWIN = {}
for v in VM.VM_LABS:
    for f in v.get('fallback') or []:
        TWIN.setdefault(f, []).append(v['id'])


def env(lab):
    if lab['kind'] == 'vm':
        n = len(lab['vm']['machines'])
        net = ' + virtual network (DHCP/DNS host)' if lab['vm'].get('net', {}).get('services', {}).get('dhcp') else (' + virtual network' if lab['vm'].get('net') else '')
        return f"**Real** — {n} Linux VM{'s' if n > 1 else ''} in the browser{net}; fallback: " + ', '.join(f'`{f}`' for f in lab['fallback'])
    t = TWIN.get(lab['id'])
    return 'Simulated' + (' — real twin: ' + ', '.join(f'`{x}`' for x in t) if t else '')


if a.env:
    print('| # | Lab | Kind | Environment |')
    print('|---|---|---|---|')
    for n, lab in enumerate(IL.LABS, 1):
        print(f"| {n} | `{lab['id']}` — {lab['title'].replace('|', '/')} | {lab['kind']} | {env(lab)} |")
    for cl in RT.classroom_ids():
        print(f"| – | `{cl}` — {RT.classroom_lab(cl)['title']} | classroom | **In class** — real equipment or lab VMs, instructor sign-off |")
    sys.exit(0)

print('| # | Lab | Kind | Obj. | Course objectives | Chapters | Baseline D/P/T | Now D/P/T (e2e) |')
print('|---|---|---|---|---|---|---|---|')
for n, lab in enumerate(IL.LABS, 1):
    lid = lab['id']
    co = ', '.join(lab.get('course_objectives') or []) or '–'
    ch = ', '.join(sorted(set(chap.get(lid, [])))) or '–'
    b = '/'.join(bmark(lid, v) for v in ('desktop', 'phone', 'tablet'))
    now = ''.join(mark(lid, v) for v in ('desktop', 'phone', 'tablet'))
    title = lab['title'].replace('|', '/')
    print(f"| {n} | `{lid}`{' 🆕' if lid in new_ids else ''} — {title} | {lab['kind']} | {len(lab['objectives'])} | {co} | {ch} | {b} | {now} |")
for cl in RT.classroom_ids():
    c = RT.classroom_lab(cl)
    now = ''.join(mark(cl, v) for v in ('desktop', 'phone', 'tablet'))
    print(f"| – | `{cl}` — {c['title']} | classroom (sign-off) | rubric | – | – | not recorded | {now} |")
