"""Page-weight / first-paint probe.

Loads a few key pages in a fresh Chromium context with a throttled "slow 4G" profile
(Lighthouse mobile: 150 ms RTT, 1.6 Mbit/s down, 750 kbit/s up; no CPU throttling) and reports, per page:
  bytes over the wire (encoded) and decoded, request count, third-party requests,
  render-blocking requests (stylesheets/scripts in <head> before first paint), FCP, DOMContentLoaded.
Usage: perf_probe.py out.json [--base URL]
"""
import argparse, json, sys
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PAGES = [('anon', 'login', '/login'), ('student', 'home', '/student'), ('student', 'class', '/student/section/1'),
         ('student', 'lesson', None), ('admin', 'home', '/admin')]
CREDS = {'student': ('student1@lms.local', 'student123'), 'admin': ('admin@lms.local', 'admin123')}


def login(page, base, role):
    page.goto(base + '/login')
    page.fill('input[name=email]', CREDS[role][0]); page.fill('input[name=password]', CREDS[role][1])
    page.click('form button[type=submit]'); page.wait_for_load_state('networkidle')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--base', default='http://127.0.0.1:5077')
    a = ap.parse_args(); host = urlparse(a.base).netloc; rows = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for role, name, path in PAGES:
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
            pg = ctx.new_page()
            if role != 'anon':
                login(pg, a.base, role)
            if path is None:   # first lesson link on the class page
                pg.goto(a.base + '/student/section/1'); path = urlparse(pg.locator('a[href*="/lesson/"]').first.get_attribute('href')).path
            # cold cache, throttled
            cdp = ctx.new_cdp_session(pg)
            cdp.send('Network.enable'); cdp.send('Network.clearBrowserCache'); cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
            cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 150, 'downloadThroughput': 1.6e6 / 8, 'uploadThroughput': 750e3 / 8})
            enc = {}
            cdp.on('Network.loadingFinished', lambda e: enc.__setitem__(e['requestId'], e['encodedDataLength']))
            pg.goto(a.base + path, wait_until='load'); pg.wait_for_timeout(1500)
            m = pg.evaluate("""() => {
              const nav = performance.getEntriesByType('navigation')[0];
              const fcp = (performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime;
              const res = performance.getEntriesByType('resource');
              return {fcp, dcl: nav.domContentLoadedEventEnd, load: nav.loadEventEnd,
                      decoded: nav.decodedBodySize + res.reduce((s,r)=>s+r.decodedBodySize,0),
                      urls: res.map(r=>[r.name, r.renderBlockingStatus||'', r.initiatorType])};
            }""")
            third = [u for u, _, _ in m['urls'] if urlparse(u).netloc not in (host, '')]
            blocking = [u for u, st, _ in m['urls'] if st == 'blocking']
            row = dict(role=role, page=name, path=path, wire_kb=round(sum(enc.values()) / 1024, 1),
                       decoded_kb=round(m['decoded'] / 1024, 1), requests=len(m['urls']) + 1,
                       third_party=len(third), blocking=len(blocking), blocking_third_party=len([u for u in blocking if u in third]),
                       fcp_ms=round(m['fcp'] or 0), dcl_ms=round(m['dcl']), load_ms=round(m['load']), third_party_urls=third)
            rows.append(row)
            print(f"{role:8} {name:7} wire={row['wire_kb']:7}KB decoded={row['decoded_kb']:7}KB req={row['requests']:3} "
                  f"3p={row['third_party']:2} blocking={row['blocking']}({row['blocking_third_party']} 3p) FCP={row['fcp_ms']}ms load={row['load_ms']}ms")
            ctx.close()
        b.close()
    json.dump(rows, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    sys.exit(main())
