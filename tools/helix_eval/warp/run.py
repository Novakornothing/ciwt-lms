"""Run bench.html over one or more frame directories with headless Chromium.
usage: python run.py <mode features|landmarks> <suffix> <seq_dir> [<seq_dir> ...]
Each seq_dir must live under /workspace/ciwt (served as the web root) and contain frames.json.
Writes <seq_dir>/<mode><suffix>.json."""
import functools, http.server, json, os, socketserver, sys, threading
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

ROOT = '/workspace/ciwt'
mode, suffix, dirs = sys.argv[1], sys.argv[2], sys.argv[3:]


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, '.wasm': 'application/wasm', '.mjs': 'text/javascript'}


srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=ROOT))
srv.daemon_threads = True
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()


def one(d):
    rel = os.path.relpath(os.path.abspath(d), ROOT)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1440, 'height': 900})
        pg.goto(f'http://127.0.0.1:{port}/ciwt-lms/tools/helix_eval/warp/bench.html?mode={mode}&seq=/{rel}&nf={os.environ.get("BENCH_NF", "2")}')
        pg.wait_for_function('window.BENCH_DONE || window.BENCH_ERR', timeout=1_800_000, polling=1000)
        err = pg.evaluate('window.BENCH_ERR || null')
        if err:
            raise RuntimeError(f'{d}: {err}')
        out = pg.evaluate('window.BENCH_OUT')
        b.close()
    path = os.path.join(d, f'{mode}{suffix}.json')
    with open(path, 'w') as fh:
        json.dump(out, fh, separators=(',', ':'))
    found = sum(1 for f in out['frames'] if f and not f.get('none'))
    return f"{rel}: {out['n']} frames, face {found}, {out['ms']} ms, infer {out['inferMs']} ms"


with ThreadPoolExecutor(max_workers=int(os.environ.get('BENCH_JOBS', '4'))) as ex:
    for r in ex.map(one, dirs):
        print(r, flush=True)
