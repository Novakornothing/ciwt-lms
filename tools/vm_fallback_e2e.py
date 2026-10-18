"""Round 5: real-VM labs when the VM cannot run — at 390×844 with touch, through the real UI.

For each real-VM lab page (or --only):
  nowasm   the browser has no WebAssembly: the weak-device notice appears before Start, and every simulated fallback
           link opens a working simulator page that links back to the real twin
  lowmem   navigator.deviceMemory = 1: the notice appears
  libfail  the emulator script fails to load: a clear error, Start is enabled again, the notice appears
  slow     the emulator never finishes loading: after 60 s (fake clock) the notice says the device is taking a while
usage: python tools/vm_fallback_e2e.py [--base URL] [--only regex] [--json out.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import interactive_labs as IL  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--base', default='http://127.0.0.1:5191')
ap.add_argument('--only', default='')
ap.add_argument('--user', default='student3@lms.local')
ap.add_argument('--json', default='')
a = ap.parse_args()
OVERFLOW = "()=>document.documentElement.scrollWidth-document.documentElement.clientWidth"


def new_page(b, init=None):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
    if init:
        ctx.add_init_script(init)
    pg = ctx.new_page()
    pg.goto(a.base + '/login')
    pg.fill('input[name=email]', a.user)
    pg.fill('input[name=password]', 'student123')
    pg.click('button[type=submit]')
    pg.wait_for_load_state()
    return ctx, pg


def weak_text(pg):
    pg.wait_for_selector('#vmWeak:not([hidden])', timeout=8000)
    return pg.inner_text('#vmWeak')


def main():
    labs = [l for l in IL.LABS if l['kind'] == 'vm' and (not a.only or re.search(a.only, l['id']))]
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        # nowasm: weak notice + every fallback link works and links back
        ctx, pg = new_page(b, 'delete window.WebAssembly;')
        for lab in labs:
            r = {'lab': lab['id'], 'case': 'nowasm', 'ok': True, 'notes': []}
            try:
                pg.goto(f"{a.base}/labs/{lab['id']}")
                t = weak_text(pg)
                assert 'WebAssembly' in t, t
                links = pg.eval_on_selector_all('.vm-fallback a', 'ns=>ns.map(n=>n.getAttribute("href"))')
                want = ['/labs/' + f for f in lab['fallback']]
                assert sorted(links) == sorted(want), (links, want)
                for f in lab['fallback']:
                    pg.goto(f"{a.base}/labs/{lab['id']}")
                    pg.locator(f'.vm-fallback a[href="/labs/{f}"]').tap()
                    pg.wait_for_url(f'**/labs/{f}')
                    pg.wait_for_selector('#labObjectives')
                    back = pg.eval_on_selector_all('.lab-real-link a', 'ns=>ns.map(n=>n.getAttribute("href"))')
                    if f"/labs/{lab['id']}" not in back:
                        r['notes'].append(f'{f} does not link back')
                    ov = pg.evaluate(OVERFLOW)
                    if ov > 1:
                        r['notes'].append(f'{f} page scrolls sideways {ov}px')
                r['ok'] = not r['notes']
            except Exception as e:
                r.update(ok=False, error=str(e)[:200])
            out.append(r)
            print('PASS' if r['ok'] else 'FAIL', r['case'], lab['id'], r.get('error', ''), '; '.join(r['notes']), flush=True)
        ctx.close()
        # lowmem
        ctx, pg = new_page(b, "Object.defineProperty(navigator,'deviceMemory',{get:()=>1});")
        for lab in labs:
            r = {'lab': lab['id'], 'case': 'lowmem', 'ok': True, 'notes': []}
            try:
                pg.goto(f"{a.base}/labs/{lab['id']}")
                assert 'little memory' in weak_text(pg)
            except Exception as e:
                r.update(ok=False, error=str(e)[:200])
            out.append(r)
            print('PASS' if r['ok'] else 'FAIL', r['case'], lab['id'], r.get('error', ''), flush=True)
        ctx.close()
        # libfail + slow: one single-VM and one network lab are enough (same code path for every lab)
        sample = [l for l in labs if len(l['vm']['machines']) == 1][:1] + [l for l in labs if l['vm'].get('net')][:1]
        for lab in sample:
            r = {'lab': lab['id'], 'case': 'libfail', 'ok': True, 'notes': []}
            ctx, pg = new_page(b)
            try:
                pg.route(re.compile(r'libv86\.js'), lambda route: route.abort())
                pg.goto(f"{a.base}/labs/{lab['id']}")
                pg.tap('#vmBoot')
                pg.wait_for_function("()=>/Could not start/.test(document.getElementById('vmStatus').textContent)", timeout=10000)
                assert pg.is_enabled('#vmBoot'), 'Start stays disabled after the failure'
                assert 'could not start' in weak_text(pg).lower()
                assert pg.evaluate(OVERFLOW) <= 1
            except Exception as e:
                r.update(ok=False, error=str(e)[:200])
            ctx.close()
            out.append(r)
            print('PASS' if r['ok'] else 'FAIL', r['case'], lab['id'], r.get('error', ''), flush=True)
            r = {'lab': lab['id'], 'case': 'slow', 'ok': True, 'notes': []}
            ctx, pg = new_page(b)
            try:
                held = []
                pg.route(re.compile(r'libv86\.js'), lambda route: held.append(route))   # never answered: a stalled download
                pg.clock.install()
                pg.goto(f"{a.base}/labs/{lab['id']}")
                pg.tap('#vmBoot')
                pg.clock.fast_forward(61000)
                assert 'taking a while' in weak_text(pg)
                for h in held:
                    h.abort()
            except Exception as e:
                r.update(ok=False, error=str(e)[:200])
            ctx.close()
            out.append(r)
            print('PASS' if r['ok'] else 'FAIL', r['case'], lab['id'], r.get('error', ''), flush=True)
        b.close()
    bad = [r for r in out if not r['ok']]
    print(f'\n{len(out) - len(bad)}/{len(out)} passed')
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
