"""CIWT Chapter 9 — Linux, macOS, mixed environment.
Proprietary schoolhouse material. No Linux CLI simulator in this block — ticket habits + Windows labs we have.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER9 = {
    "title": "Chapter 9 — Linux, macOS & Cross-Platform Support",
    "order": 9,
    "minutes": 160,
    "overview": (
        "Same Block 1 ticket on a different OS. Read who owns the box, do not paste root passwords, "
        "and do not smash a Mac into a Windows image because mail is late."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 40,
            "title": "9.1 Linux CLI Essentials",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Name pwd, ls, cd, ip a / ip addr, and whoami as the inventory habit on Linux</li>
<li>Treat sudo as a change with a ticket, not a personality</li>
<li>Do not run destructive disk commands you cannot name</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>No Linux terminal in this LMS. Whiteboard the four inventory commands next to Windows hostname / ipconfig / whoami. Same 2.6 habit, different spelling.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.6 inventory and 7.1 process. You already know not to skip identify.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Linux is another guest or another bench PC. Inventory first. Root is not a shortcut around policy.</p></div>
<section id="s1" class="sublesson"><h3>1. Map to what you already type</h3>
<table class="port-table">
<tr><th>Windows habit</th><th>Linux cousin</th></tr>
<tr><td>hostname / whoami</td><td>hostnamectl / whoami</td></tr>
<tr><td>ipconfig /all</td><td>ip a</td></tr>
<tr><td>list disk</td><td>lsblk — still not wipe</td></tr>
</table>
</section>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>First command family on a strange Linux box?</summary><p>Who you are, where you are, address — not mkfs.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "9.2 macOS Support Patterns",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Collect model and OS version before ordering a part</li>
<li>Treat FileVault / MDM like shop property</li>
<li>Do not pry a sealed laptop battery (Chapter 4.1 still wins)</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>About This Mac = gui-about. MDM on a Mac is 4.2 again. Swollen pack is still stop-work.</p></div>
<div class="build-on"><strong>Builds on:</strong> 4.1 FRUs and 4.2 MDM.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>A Mac is a portable with a different Settings app. Identity, battery safety, and who owns the enrollment do not change.</p></div>
<div class="live-demo"><h4>Lab habit on the Windows bench</h4>
<p><strong>gui-accounts</strong> — read who is signed in. That is the question you take to a Mac: whose Apple ID vs whose work profile.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Mail fails on a managed Mac. Wipe it in the hallway?</summary><p>No. Isolate radio vs tenant vs MDM. Do not sidestep enrollment.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 40,
            "title": "9.3 Cross-Platform Access",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Separate account issues from file-share / protocol issues</li>
<li>Do not store the user’s password in the ticket</li>
<li>Escalate the directory owner when entitlement is the block</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Windows user cannot open a share the Mac team uses. Classify: request vs break/fix. gui-accounts first.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 request vs break/fix and 4.2 accounts.</div>
<div class="live-demo"><h4>Lab</h4>
<p><strong>gui-accounts</strong> — who is signed in on this bench before you talk about “the share.”</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Never had the share on this Mac.</summary><p>Service request. Entitlement. Not a NIC replacement.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "9.4 Capstone — Mixed Environment",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Write one intake that names the OS and the outcome</li>
<li>Stop for battery / shock the same as Chapter 4</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Story: “Designer Mac cannot open the budget share; Windows next door can.” ticket-intake language plus account check.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>ticket-intake</strong> for structure. <strong>gui-accounts</strong> for identity habit.</p></div>
<div class="check-box"><h4>Pass bar</h4>
<p>Note names OS, who is signed in, and whether this is request or break/fix. No hallway wipe.</p>
</div>'''
        },
    ],
}
