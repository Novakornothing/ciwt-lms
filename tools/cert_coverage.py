"""Regenerate the committed certification-alignment data.

    python tools/cert_coverage.py            # writes curriculum_v2/cert/alignment.json
    python tools/cert_coverage.py --baseline # also (re)writes coverage_baseline.json (before-content snapshot)
    python tools/cert_coverage.py --check    # exit 1 if alignment.json is stale
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from curriculum_v2.cert import mapping  # noqa: E402

OUT = os.path.join(ROOT, 'curriculum_v2', 'cert', 'alignment.json')
BASE = os.path.join(ROOT, 'curriculum_v2', 'cert', 'coverage_baseline.json')


def dump(obj):
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + '\n'


def main(argv):
    snap = dump(mapping.snapshot())
    if '--check' in argv:
        cur = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
        if cur != snap:
            print('alignment.json is stale: run python tools/cert_coverage.py')
            return 1
        print('alignment.json up to date')
        return 0
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(snap)
    if '--baseline' in argv:
        c = mapping.compute()
        base = {'note': 'Coverage before the content pass (branch content, from refinement bc19ca8).',
                'summary': c['summary'],
                'status': {oid: v['status'] for oid, v in c['objectives'].items()},
                'items': {oid: len(v['items']) for oid, v in c['objectives'].items()}}
        with open(BASE, 'w', encoding='utf-8') as f:
            f.write(dump(base))
    for ex, s in mapping.compute()['summary'].items():
        print(ex, s)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
