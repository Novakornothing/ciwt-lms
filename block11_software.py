"""CIWT Chapter 11 — Software troubleshooting.
Proprietary schoolhouse material.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER11 = {
    "title": "Chapter 11 — Software Troubleshooting",
    "order": 11,
    "minutes": 160,
    "overview": (
        "One app vs whole PC vs whole floor. Repair before rebuild. Slow logon is not automatically diskpart."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 40,
            "title": "11.1 Symptom Patterns",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Sort: one app, one user profile, one PC, many PCs</li>
<li>Write the exact error text</li>
<li>Do not start at rebuild</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Same impact trick as print path (4.3). Three tickets on the board.</p></div>
<div class="build-on"><strong>Builds on:</strong> 4.3 one vs many and 7.2 domains.</div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Outlook only, Word fine, next desk fine.</summary><p>One app on one PC. Profile or Office repair — not a clean image.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "11.2 Isolation Techniques",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Use another app, another profile, another PC as controls</li>
<li>If the symptom is “no network in the app,” run Chapter 5 first</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>If they claim the NIC, make them run win-full-triage before any app rebuild.</p></div>
<div class="live-demo"><h4>Lab</h4>
<p><strong>win-full-triage</strong> when the app failure might be name or lease.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Browser fails, ping IP works, ping name fails.</summary><p>DNS domain. Not an Office repair.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 40,
            "title": "11.3 Repair vs Rebuild",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Repair / in-place before clean image</li>
<li>Rebuild only with backup and a change ticket</li>
<li>List disk still required before any wipe (2.6)</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Tie to 8.1. No clean in class.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>gui-about</strong> and <strong>gui-update</strong> — know what you would be rebuilding.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Clean image because one app crashes?</summary><p>No. Isolate the app first.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "11.4 Capstone — Slow Logon",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Collect identity, Update, services, processes before you reboot-loop</li>
<li>Name the domain: profile, network home, disk, or GPO — then test one</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Inventory + processes + services. Reboot is a change. No diskpart.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>w11-inventory</strong>, <strong>w11-processes</strong>, <strong>gui-services</strong>.</p></div>
<div class="check-box"><h4>Pass bar</h4>
<p>Note has one theory and one next test. You did not image.</p>
</div>'''
        },
    ],
}
