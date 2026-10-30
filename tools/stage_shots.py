"""Screenshots of one lab of each kind, through all three stages, at two widths.

Usage: python tools/stage_shots.py <outdir>
"""
import os
import socket
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(prefix="stage-shots-"), "t.db")
os.environ.setdefault("SECRET_KEY", "shots")

import app as lms  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/cursor/artifacts/stage-labs")
OUT.mkdir(parents=True, exist_ok=True)
lms.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

LABS = [
    ("linux-vm", "linux-vm-shell"),
    ("windows-sim", "win-ipconfig"),
    ("cisco-sim", "sw-vlan-access"),
    ("network-canvas", "sec-acl"),
]
SIZES = {"desktop": (1440, 900), "mobile": (390, 844)}

sock = socket.socket()
sock.bind(("127.0.0.1", 0))
port = sock.getsockname()[1]
sock.close()
server = make_server("127.0.0.1", port, lms.app, threaded=True)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}"

with sync_playwright() as p:
    browser = p.chromium.launch()
    for size, (w, h) in SIZES.items():
        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                  is_mobile=(size == "mobile"), has_touch=(size == "mobile"))
        page = ctx.new_page()
        page.goto(base + "/login")
        page.fill('input[name=email]', "student1@lms.local")
        page.fill('input[name=password]', "student123")
        page.click('button[type=submit]')
        page.wait_for_load_state("networkidle")
        for name, lab_id in LABS:
            page.goto(base + f"/labs/{lab_id}", wait_until="networkidle")
            page.wait_for_selector("#labStages")
            for stage in ("guided", "assisted", "ticket"):
                page.click(f'#stageTab-{stage}')
                page.wait_for_selector(f'#stagePanel-{stage}:not([hidden])')
                path = OUT / f"{name}-{stage}-{size}.png"
                page.locator("#labStages").scroll_into_view_if_needed()
                page.screenshot(path=str(path), full_page=False)
                print(path)
            for sel, tag in (("#winSim", "win-panel"), ("#iosSim", "ios-panel"), ("#netCanvas", "net-panel")):
                loc = page.locator(sel)
                if loc.count():
                    loc.scroll_into_view_if_needed()
                    page.wait_for_timeout(200)
                    path = OUT / f"{name}-{tag}-{size}.png"
                    page.screenshot(path=str(path), full_page=False)
                    print(path)
        ctx.close()
    browser.close()
server.shutdown()
