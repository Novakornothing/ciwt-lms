"""Desktop and mobile screenshots of Try-It simulations inside real lessons.

Usage: python tools/sim_shots.py [base] [outdir]
"""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:5050'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/opt/cursor/artifacts/sims'

# Real lessons. section / module / lesson ids match the seeded catalog.
TARGETS = [
    ('subnet', 1, 5, 21, 'start-here-what-a-network-is'),
    ('osi', 2, 14, 60, 'core-content'),
    ('ports', 1, 5, 22, 'what-a-port-is-if-you-have-never-heard-it'),
    ('chmod', 1, 9, 38, 'linux-inventory-cousins'),
    ('raid', 1, 3, 12, 'storage-devices-interfaces-form-factors-raid-and-removable-m'),
    ('pcbuild', 1, 2, 6, 'start-here-the-parts-inside-the-box'),
    ('boot', 1, 2, 7, 'firmware-before-windows-from-zero'),
    ('phish', 1, 10, 43, 'teach-block-phish-and-malware-as-tickets'),
]


def show_all(page, width):
    if width < 1024:
        page.locator('#lessonSheetBtn').click()
        page.locator('#lessonRailAll').wait_for()
    btn = page.locator('#lessonRailAll')
    if 'Show all' in (btn.inner_text() or ''):
        btn.click()
        page.wait_for_timeout(200)
    if width < 1024:
        page.locator('#lessonSheetClose').click()


def open_sim(page, section, module, lesson, sid, width):
    url = f'{BASE}/student/module/{section}/{module}/lesson/{lesson}'
    page.goto(url, wait_until='domcontentloaded')
    page.wait_for_selector('#lessonBody')
    show_all(page, width)
    card = page.locator(f'#ladder-{sid}')
    card.wait_for()
    card.scroll_into_view_if_needed()
    page.evaluate(
        """(sid) => {
          const btn = document.querySelector('#ladder-' + sid + ' [data-rung-pick="R4"]');
          btn.form.requestSubmit(btn);
        }""",
        sid,
    )
    page.wait_for_selector(f'#ladder-{sid}[data-shown="R4"] [data-novak-sim] .novak-sim-stage > *', timeout=15000)
    page.wait_for_timeout(450)
    return page.locator(f'#ladder-{sid} .novak-sim')


def jump_check(page):
    """Desktop: the right-rail Try-It control is the visible switcher. It must not move the reader."""
    page.set_viewport_size({'width': 1280, 'height': 800})
    page.goto(f'{BASE}/student/module/1/1/lesson/1', wait_until='domcontentloaded')
    page.wait_for_selector('#lessonBody .ladder')
    box = page.locator('#lessonBody .ladder').first
    box.scroll_into_view_if_needed()
    sid = box.get_attribute('data-ladder-sid')
    before = box.bounding_box()['y']
    page.locator('[data-rail-rung="R4"]').click()
    page.wait_for_selector(f'#ladder-{sid}[data-shown="R4"] .novak-sim-stage > *', timeout=15000)
    page.wait_for_timeout(700)
    after = page.locator(f'#ladder-{sid}').bounding_box()['y']
    return sid, before, after, abs(after - before)


def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(f'{BASE}/demo/enter/student')
        page.wait_for_load_state('domcontentloaded')
        sid, before, after, delta = jump_check(page)
        open(os.path.join(OUT, 'jump-check.txt'), 'w').write(
            f'sid={sid} before={before:.1f} after={after:.1f} delta={delta:.1f}\n')
        if delta >= 40:
            errors.append(f'reader moved {delta:.1f}px')
        for kind, section, module, lesson, sec_sid in TARGETS:
            for name, size in (('desktop', {'width': 1280, 'height': 800}), ('mobile', {'width': 390, 'height': 844})):
                page.set_viewport_size(size)
                sim = open_sim(page, section, module, lesson, sec_sid, size['width'])
                path = os.path.join(OUT, f'{kind}-{name}.png')
                last = None
                for _ in range(4):
                    try:
                        sim.screenshot(path=path)
                        last = None
                        break
                    except Exception as exc:
                        last = exc
                        page.wait_for_timeout(400)
                        sim = page.locator(f'#ladder-{sec_sid} .novak-sim')
                if last:
                    raise last
                overflow = sim.evaluate('el => el.scrollWidth - el.clientWidth')
                if name == 'mobile' and overflow > 1:
                    errors.append(f'{kind} mobile overflow {overflow}px')
                print(path, 'overflow', overflow)
        browser.close()
    if errors:
        print('ERRORS')
        for e in errors:
            print(e)
        sys.exit(1)
    print('ok')


if __name__ == '__main__':
    main()
