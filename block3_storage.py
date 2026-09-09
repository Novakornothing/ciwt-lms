"""CIWT Chapter 3 — Storage, power, ports.
Proprietary schoolhouse material. Continues Block 2 hardware: what you replace after the board card.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER3 = {
    "title": "Chapter 3 — Storage, Power, Ports & Peripherals",
    "order": 3,
    "minutes": 240,
    "overview": (
        "After the board card and a running inventory: name the disk interface, treat RAID as not backup, "
        "replace a PSU as a sealed unit, and isolate a dark display before you blame the board."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 50,
            "title": "3.1 Storage Technologies",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Tell HDD, SATA SSD, and NVMe apart by interface and what “fast” actually means on a ticket</li>
<li>Confirm the OS sees the disk before anyone images or wipes</li>
<li>Name the interface on the bench: SATA cable vs M.2 notch</li>
<li>Run <strong>w11-disk</strong> and say which disk is the OS disk</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 50 minutes</h4>
<p>Hold a 2.5 in SATA and an M.2 stick. Notch and screw first. Then list disk on the projector. No clean. Builds on 2.6.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.5 POST and 2.6 list disk. You already know not to wipe a disk you have not listed.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Storage is where files live when power is off. An HDD is a warehouse with one forklift. A SATA SSD is the same warehouse with more workers. NVMe is an on-ramp onto the CPU highway (PCIe). Same cargo, different road.</p></div>
<div class="live-demo"><h4>Lab this lesson — w11-disk</h4>
<p>Open diskpart → <code>list disk</code>. Read size and style (GPT/MBR). Say which handle is the OS disk. Exit. Do not type clean or convert.</p></div>

<section id="s1" class="sublesson"><h3>1. Three common drives</h3>
<table class="port-table">
<tr><th>Kind</th><th>Path</th><th>Ticket use</th></tr>
<tr><td>HDD</td><td>SATA data + SATA power</td><td>Capacity, cheap, slow random work</td></tr>
<tr><td>SATA SSD</td><td>Same cables as HDD</td><td>Snappy OS, still SATA-limited</td></tr>
<tr><td>NVMe</td><td>M.2 slot, PCIe</td><td>Fast OS disk — confirm keying and the screw</td></tr>
</table>
<p>M.2 is the slot. NVMe is the protocol. A SATA M.2 stick can sit in an M.2 slot and not be NVMe. Read the label and Device Manager, not the marketing name on the box.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Detect before you image</h3>
<p>Firmware list → Windows About/Disk Management → <code>list disk</code>. If firmware does not see the stick, stop. Reseat, check the notch, try the other M.2 slot if the board shares lanes with SATA. Imaging a disk the OS cannot see is how shops wipe the wrong handle.</p>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Calling every M.2 stick NVMe</li>
<li>Leaving extra standoffs under a board after a drive swap</li>
</ul></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>This course bench card had an M.2 stick. Interface word?</summary><p>NVMe. <code>storage nvme</code> on hw-board. list disk still required before image.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "3.2 RAID and Backup Reality",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>State what RAID 0, 1, 5, and 10 do to capacity and fault behavior</li>
<li>Say out loud: RAID is not a backup</li>
<li>Know when a degraded array is an incident, not a quiet disk swap</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Whiteboard four rows. Ask “user deleted the share — which RAID saves them?” Answer: none. No live RAID lab in this block — this is a judgment lesson.</p></div>
<div class="build-on"><strong>Builds on:</strong> 3.1 you can name a disk. RAID is several disks presenting as one.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>RAID is a way to survive some disk failures or go faster. It does not save you from “I deleted the folder,” ransomware, or fire. Backup is a second copy you can restore.</p></div>

<section id="s1" class="sublesson"><h3>1. Levels you must not mix up</h3>
<table class="port-table">
<tr><th>Level</th><th>Idea</th><th>If one disk dies</th></tr>
<tr><td>0</td><td>Stripe for speed</td><td>The volume is gone</td></tr>
<tr><td>1</td><td>Mirror</td><td>Still up; replace and rebuild</td></tr>
<tr><td>5</td><td>Stripe + parity</td><td>Still up (one disk); rebuild is slow and risky</td></tr>
<tr><td>10</td><td>Mirrored stripes</td><td>Depends which disk; better rebuild than 5 in many shops</td></tr>
</table>
</section>

<section id="s2" class="sublesson"><h3>2. Ticket habit</h3>
<p>Degraded array + users still working = incident with a clock, not a silent lunch swap. Write: which array, which disk slot, whether the volume is still mounted, last backup time if you know it. Do not pull a second disk “to test.”</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>User ransomed the file share. RAID 5 saves them?</summary><p>No. Restore from backup. RAID only covered a disk failure.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 45,
            "title": "3.3 Power Supplies",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Treat the PSU as a sealed FRU — replace, do not open</li>
<li>Match 24-pin and CPU 8-pin before you call the board dead</li>
<li>Stop for heat, smell, or shock — same Block 1 incident rule</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Point at wall cord, PSU switch, 24-pin, CPU 8-pin. Nobody opens the PSU. If the story is a hot outlet, send them to ticket-intake language: incident, escalate.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.2 sealed electrical units and 2.1 power connectors.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>The PSU turns wall power into the voltages the board needs. You size it with margin and you replace it as a box. You do not debug capacitors with a screwdriver in this course.</p></div>
<div class="live-demo"><h4>If the ticket is heat or shock</h4>
<p>Do not stay in hardware-swap mode. Classify incident, impact as it is, escalate. Lab ticket-intake is the command set.</p></div>

<section id="s1" class="sublesson"><h3>1. Sealed unit</h3>
<p>Unplug from the wall, wait, then disconnect board cables. Swap with a known-good unit of equal or greater rating and the same connectors. Recycle the failed unit per shop rules. No “just a peek.”</p>
</section>

<section id="s2" class="sublesson"><h3>2. Symptoms that look like a dead board</h3>
<ul>
<li>No fan twitch, no LED — wall, switch, 24-pin, CPU 8-pin, then PSU</li>
<li>Instant off under load — undersized or dying PSU</li>
<li>Burn smell / hot receptacle — incident, stop</li>
</ul>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>May you service inside the PSU?</summary><p>No. Replace the unit.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 45,
            "title": "3.4 Ports, Cables, Displays",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Isolate a dark display: cable, input, adapter, then GPU/board</li>
<li>Name HDMI, DisplayPort, and USB-C video as different paths</li>
<li>Do not reseat RAM because the monitor input was on HDMI 2</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Dark projector demo if you can: wrong input, then unseated cable. Order on the board: known-good cable → known-good panel → onboard vs discrete → then board.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.5 POST order. No video after POST OK is a display path, not a memory code.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>A dark screen is usually a cable, an input button, or a sleeping panel. It is rarely a new motherboard. Prove the cheap layer first.</p></div>

<section id="s1" class="sublesson"><h3>1. Isolation order</h3>
<ol>
<li>Confirm POST actually finished (you heard the beep / saw the LED leave MEM)</li>
<li>Known-good cable, correct input on the panel</li>
<li>Known-good display</li>
<li>Onboard video vs discrete card</li>
<li>Then board / GPU</li>
</ol>
</section>

<section id="s2" class="sublesson"><h3>2. Connectors</h3>
<p>HDMI and DisplayPort carry video and audio. USB-C may carry video only if that port is wired for it — the label on the chassis matters. Adapters fail. Swap the adapter before you swap the laptop board.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Long beeps + MEM on the card, no video. Display cable first?</summary><p>No. That is POST memory. Fix RAM first (2.5). Display order starts after POST OK.</p></details>
</div>'''
        },
        {
            "order": 5,
            "minutes": 55,
            "title": "3.5 Capstone — Unstable Workstation",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Work one unstable tower in order: safety → POST → inventory → disk list → display</li>
<li>Write a Block 1 quality note with tests and results</li>
<li>Stop if the story turns into heat or shock</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 55 minutes</h4>
<p>Give the room one story: “Tower reboots, no video some boots, Disk 0 is the 256 GB NVMe.” They rerun hw-board facts from memory, list disk, Device Manager. Peer-read notes.</p></div>
<div class="build-on"><strong>Builds on:</strong> Chapters 1–3. This is the first multi-domain hardware ticket.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Unstable means you do not replace four parts. You run the order you already know and you write what each step proved.</p></div>
<div class="live-demo"><h4>Labs on this lesson</h4>
<ol>
<li><strong>hw-board</strong> — confirm you can still name the card</li>
<li><strong>w11-disk</strong> — list disk, name the OS handle</li>
<li><strong>gui-devices</strong> — disk, NIC, display adapters</li>
</ol></div>

<section id="s1" class="sublesson"><h3>Worked order</h3>
<ol>
<li>Safety: no smell, no shock, wall cord seated</li>
<li>POST: if MEM, memory first — do not image</li>
<li>If POST OK and dark panel: 3.4 display order</li>
<li>If Windows: About + list disk + Device Manager</li>
<li>Note: each test → result → next step</li>
</ol>
</section>

<section id="s2" class="sublesson"><h3>Pass bar</h3>
<p>A peer can take your note and know whether to reseat RAM, swap a cable, or stop for facilities. You did not clean a disk. You did not open a PSU.</p>
</section>'''
        },
    ],
}
