"""CIWT Chapter 8 — Windows client configuration.
Proprietary schoolhouse material. Aschool Block 3 slice: Settings and CLI as two views of one PC.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER8 = {
    "title": "Chapter 8 — Windows Installation & Client Configuration",
    "order": 8,
    "minutes": 180,
    "overview": (
        "Know what is on the box before you image it. Read Update, accounts, and services from Settings "
        "and from CLI. Repair tools come after inventory. This is not a license to clean Disk 0."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 45,
            "title": "8.1 Clean vs In-Place",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Inventory name, edition, and disks before any install talk</li>
<li>Say when an in-place repair is safer than a clean image</li>
<li>Never image until list disk has a named OS handle</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>No live image in class unless shop says so. Demo gui-about + w11-inventory. Clean vs in-place on the board: data risk vs time.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.6 inventory and 3.1 list disk.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Clean install wipes the OS volume. In-place tries to keep apps and files. Both are changes (1.3). Neither is step one on a dark screen that never left POST.</p></div>
<div class="live-demo"><h4>Labs this lesson</h4>
<p><strong>gui-about</strong> and <strong>w11-inventory</strong>. Write edition and build. If you also list disk, you still do not type clean.</p></div>

<section id="s1" class="sublesson"><h3>1. Choose with evidence</h3>
<p>In-place when the OS boots and the problem is a broken component store or a failed feature update. Clean when the volume is trash and backup is confirmed. POST memory fail is still Chapter 2.5 — not setup.exe.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>MEM beep, no video. Clean install?</summary><p>No. Memory domain first.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 45,
            "title": "8.2 Baseline Configuration",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Read Update state from Settings</li>
<li>Read the signed-in account</li>
<li>Confirm a lease from Settings Ethernet and from CLI</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>This is A-school Block 3 time: Settings and CLI as two views. Run gui-update, gui-accounts, gui-ethernet, optional win-dhcp-renew if the lab VM allows a cycle.</p></div>
<div class="build-on"><strong>Builds on:</strong> 4.2 accounts and 5.1 ipconfig.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Baseline means you can describe the box: who is signed in, whether updates are pending, whether it has a real address. You collect that before you “tune” anything.</p></div>
<div class="live-demo"><h4>Labs this lesson</h4>
<ol>
<li><strong>gui-update</strong> — patch state</li>
<li><strong>gui-accounts</strong> — who is signed in</li>
<li><strong>gui-ethernet</strong> / <strong>win-dhcp-renew</strong> — address path</li>
</ol></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Why read Update before a mystery reboot loop?</summary><p>A pending feature update is a change window, not a dead board.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 45,
            "title": "8.3 Repair Tools",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Confirm DHCP Client, DNS Client, and Defender are Running</li>
<li>Do the same from PowerShell / Services</li>
<li>List processes before you reboot “to clear it”</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>gui-services and w11-services side by side. w11-processes before any reboot drill. Firewall read-only if time (w11-firewall) — do not turn it off.</p></div>
<div class="build-on"><strong>Builds on:</strong> 5.2 firewall stays on, 7.1 change one thing.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Services are the background jobs that make lease, names, and Defender work. If DHCP Client is stopped, ipconfig will look cursed. Reboot is a change, not a personality.</p></div>
<div class="live-demo"><h4>Labs this lesson</h4>
<ol>
<li><strong>gui-services</strong> and <strong>w11-services</strong> — Dhcp, Dnscache, Defender</li>
<li><strong>w11-processes</strong> — look before you reboot</li>
<li><strong>w11-firewall</strong> — read profile only</li>
</ol></div>
<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Stopping Defender to make an installer quiet</li>
<li>Reboot without listing what was running</li>
</ul></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>May you turn the firewall profile off for a game launcher?</summary><p>No. Chapter 1.4 / 5.2.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 45,
            "title": "8.4 Capstone — Failed Update",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Collect About, Update state, services, and a short note</li>
<li>Choose in-place vs escalate vs hardware domain with evidence</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Story: “PC rebooted three times, Update says failed, users can still log in.” Inventory + Update + services. No clean install in class.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>gui-about</strong>, <strong>gui-update</strong>, <strong>gui-services</strong>. Note: edition/build, Update error if shown, three service states, next step (retry window vs in-place vs escalate).</p></div>
<div class="check-box"><h4>Pass bar</h4>
<p>You did not image. You did not disable Defender. A peer knows the next window from your note.</p>
</div>'''
        },
    ],
}
