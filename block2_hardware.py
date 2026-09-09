"""CIWT Block 2 / Chapter 2 — PC architecture and first inventory.
Proprietary schoolhouse material. Not official Navy courseware.
Teach from the screen: identify the board on the card (Lab hw-board), then inventory the running box.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER2 = {
    "title": "Chapter 2 — PC Architecture: Motherboard, CPU & Memory",
    "order": 2,
    "minutes": 280,
    "overview": (
        "Block 2 hardware slice. Name the board, socket, memory, and storage on a chassis before you "
        "unplug anything. Isolate POST in order. Finish Lab hw-board, then inventory a running Windows box "
        "(About, hostname, list disk) before anyone images it."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 45,
            "title": "2.1 Motherboards, Form Factors, and Chipsets",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Identify ATX, microATX, and Mini-ITX by screw pattern and size</li>
<li>Explain what a chipset allows: CPU family and features the board will actually run</li>
<li>Point to 24-pin ATX, 8-pin CPU, RAM slots, and M.2 notch on a chassis</li>
<li>Use <code>form-factor</code> with the exact name on the bench card</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Chapter 1 safety first: power off, wall unplug, strap. Side panel off. Point to six connectors as a group. Then <code>show board</code> only — do not submit hw-board until 2.5.</p></div>
<div class="build-on"><strong>Builds on:</strong> Chapter 1 safety. You do not identify a board while it is running and the panel is half off.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>The motherboard is the city map. Wrong size will not mount. Wrong chipset will not talk to the CPU you bought. Wrong slot will not take the drive.</p></div>
<div class="live-demo"><h4>Lab hw-board — this lesson</h4>
<p><code>show board</code> prints the bench card.<br>
<code>form-factor microatx</code> or <code>atx</code> or <code>mini-itx</code> — one token, <code>mini-itx</code> hyphenated.<br>
This card is a 9.6 × 9.6 in office tower → microATX. Later lessons add socket, memory, storage, POST.</p></div>

<section id="s1" class="sublesson"><h3>1. Form factor is the hole pattern</h3>
<table class="port-table">
<tr><th>Name</th><th>About</th><th>Where you see it</th></tr>
<tr><td><strong>ATX</strong></td><td>12 × 9.6 in</td><td>Full / standard office tower</td></tr>
<tr><td><strong>microATX</strong></td><td>9.6 × 9.6 in, fewer slots</td><td>Small office towers — this lab card</td></tr>
<tr><td><strong>Mini-ITX</strong></td><td>~6.7 in square</td><td>Tiny / compact boxes</td></tr>
</table>
<p>Never leave extra metal standoffs under an unused hole — they short the back of the board.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Chipset and sockets (names)</h3>
<p>Intel desktop in this course: <strong>LGA</strong> (pads on the CPU, pins in the socket). AMD AM4/AM5: pins on the CPU. The chipset is the traffic cop between CPU, RAM, storage, and USB. Read the board model printed between the RAM slots — search that string, not “the black one.”</p>
</section>

<section id="s3" class="sublesson"><h3>3. Connectors you must point to</h3>
<ul>
<li>24-pin ATX — main board power</li>
<li>4/8-pin EPS near the CPU — missing this = no POST or instant off</li>
<li>RAM slots — color-paired for channels</li>
<li>M.2 — short stick, screw at the end; look at the notch</li>
<li>SATA — L-shaped data, separate power from the PSU</li>
<li>Front-panel header — wrong pins = “dead” PC that is only wired wrong</li>
</ul>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Calling every small tower Mini-ITX</li>
<li>Measuring the case instead of the board</li>
</ul></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>9.6 × 9.6 in board in a small office tower?</summary><p>microATX. Lab: <code>form-factor microatx</code>.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "2.2 Firmware: UEFI, Secure Boot, and Settings",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Enter firmware setup on a training PC and leave without changing a setting you cannot name</li>
<li>State what UEFI does versus what Windows does</li>
<li>Explain Secure Boot in one sentence a user will accept</li>
<li>Know that a “dead” PC can be a firmware setting, not a dead board</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Live demo: power on, Del/F2, read CPU, RAM size, boot order, Exit without saving. Nobody changes XMP or Secure Boot on the shop image without a ticket.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.1 board names. Firmware is software that lives on the board and runs before Windows.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Firmware is the first program the CPU runs. It checks RAM and storage, then hands off to Windows. If firmware is set to ignore this disk, Windows looks dead and the board is fine.</p></div>
<div class="live-demo"><h4>Live demo on the training tower</h4>
<p>Power on, tap Del or F2 (bench note says which). Do not change anything. Read CPU name, RAM size, boot order. Exit without saving. Write those three into a ticket if you ever suspect firmware. Lab hw-board does not have a firmware command — you still need the habit before 2.5 POST.</p></div>

<section id="s1" class="sublesson"><h3>1. UEFI versus “the BIOS screen”</h3>
<p>People still say BIOS. Modern boards run <strong>UEFI</strong> — same job, larger disks, mouse, Secure Boot. If Windows is already up, Settings → Recovery → Advanced → UEFI Firmware Settings is the supported path. Do not yank power to “force BIOS” on a production box.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Secure Boot</h3>
<p>Firmware starts only a signed bootloader. That blocks some bootkits. It also blocks an unsigned USB installer. If a shop disk will not boot, check Secure Boot before you declare the disk bad.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Settings that fake hardware failure</h3>
<ul>
<li>Wrong boot order — “no OS” when the NVMe is healthy</li>
<li>CSM/Legacy on a UEFI-only disk</li>
<li>RAM XMP the stick cannot run — random POST fail</li>
<li>Internal video disabled and no discrete GPU</li>
</ul>
<p>Change one thing, save, test, write it down. Firmware is a change (1.3).</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Windows missing after a firmware click last week. First question?</summary><p>Boot order and the disk firmware still sees — not “reinstall Windows.”</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 40,
            "title": "2.3 CPUs, Cooling, and Performance Basics",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Match a CPU to a socket before you open the lever</li>
<li>Seat a cooler so the board does not bow and the fan header is CPU_FAN</li>
<li>Read a thermal complaint as cooler, paste, or load — not “buy a CPU first”</li>
<li>Type <code>socket</code> from the silkscreen on the card</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Show an LGA package vs an AM pin package if you have both. Nobody presses a cocked CPU. Lab command this hour: <code>socket lga1700</code> on this card.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.1 socket names. 2.2 firmware will show the CPU string after POST.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Wrong socket does not “almost fit.” Pins bend and the board is done.</p></div>
<div class="live-demo"><h4>Lab command this lesson</h4>
<p>Card silkscreen: LGA1700. <code>socket lga1700</code>. If you guess AM5, submit will fail in 2.5.</p></div>

<section id="s1" class="sublesson"><h3>1. Socket first</h3>
<p>Read the board silkscreen and the CPU box. LGA: no pins on the chip; do not scrape the pads. AM4/AM5: pins on the chip; do not set it on a screw. Open the load lever fully, seat, close. If it does not drop in flat, it is not aligned — do not press.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Cooler is part of the CPU</h3>
<p>No cooler → throttle or die. Check: backplate, thin even paste, fan or pump on <strong>CPU_FAN</strong> so firmware can see RPM. A “fine CPU” that shuts down at 10 minutes is often the header on SYS_FAN and a zero-RPM reading in firmware.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Performance without myth</h3>
<p>For this course: identify the part, confirm firmware sees it, confirm cooler RPM. If firmware does not list the CPU, you have a support-list problem, not a “slow chip.”</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>This lab card socket?</summary><p>LGA1700. <code>socket lga1700</code>.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "2.4 Memory Technologies and Channels",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Tell DDR4 from DDR5 by the notch</li>
<li>Populate the color-paired slots the board calls Channel A/B</li>
<li>Treat no-POST after a RAM change as reseat / wrong generation / dirty slot before “dead CPU”</li>
<li>Type <code>memory ddr4</code> or <code>memory ddr5</code></li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Hold a DDR4 and DDR5 stick if you have both. Notch offset is the lesson. This card: DIMM marking DDR5.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.1 RAM slots and 2.3 “if it does not drop in, stop.”</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Wrong generation will not latch. One stick in the wrong slot can POST at half speed, or not POST at all.</p></div>
<div class="live-demo"><h4>Lab command this lesson</h4>
<p>Card: DIMM marking DDR5. <code>memory ddr5</code>. Do not file the notch. Do not stack DDR4 in a DDR5 slot “to try.”</p></div>

<section id="s1" class="sublesson"><h3>1. Generation and notch</h3>
<p>DDR4 and DDR5 look similar from two feet. The notch is offset differently. The slot will fight you if you are wrong — that fight is information. Stop.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Channels</h3>
<p>Two matched sticks in the paired slots (often 2 and 4 — read the board) run dual channel. One stick works. Four unmatched kits can POST and then blue-screen. Match size and generation first; speed second.</p>
</section>

<section id="s3" class="sublesson"><h3>3. When RAM looks like a dead board</h3>
<p>No video after you “just added memory”: reseat both, try one known-good stick in slot A2, clear firmware only if shop procedure says so. Write each test. 2.5 adds beep codes. This card’s POST line is memory.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>This lab card memory?</summary><p>DDR5. <code>memory ddr5</code>.</p></details>
</div>'''
        },
        {
            "order": 5,
            "minutes": 50,
            "title": "2.5 POST Isolation and Hardware Order",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Use a fixed order: power → board lights → beep/POST → display → firmware → OS</li>
<li>Map this course’s beep/LED line to memory, display, power, or OK</li>
<li>Finish Lab hw-board: form-factor, socket, memory, storage, post, submit</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 50 minutes</h4>
<p>Write the six-step order on the board. Run hw-board to submit as a class on the projector once, then each trainee alone. Pass bar: correct five fields plus a note that they did not reseat RAM on a live chassis.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.1–2.4 names. This is the order you work a dark tower.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>No POST means you do not reinstall Windows. You work hardware in order so you do not replace the CPU because a stick of RAM is half out.</p></div>
<div class="live-demo"><h4>Finish lab hw-board</h4>
<ol>
<li><code>show board</code></li>
<li><code>form-factor microatx</code></li>
<li><code>socket lga1700</code></li>
<li><code>memory ddr5</code></li>
<li><code>storage nvme</code> (M.2 stick in the short slot)</li>
<li><code>post memory</code> (debug LED MEM, long beeps, no video)</li>
<li><code>submit</code></li>
</ol>
<p>Wrong guesses stay wrong until you change them. Submit lists what is still missing.</p></div>

<section id="s1" class="sublesson"><h3>1. Order of work</h3>
<ol>
<li>Power at the wall and PSU switch</li>
<li>Board LED / fan twitch on power button</li>
<li>Beep or debug code</li>
<li>Display</li>
<li>Firmware</li>
<li>Windows</li>
</ol>
<p>Skip a step and you will “fix” the OS on a box that never left POST.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Beeps on this course’s bench card</h3>
<p>Vendors do not share one codebook. For <strong>this lab</strong>:</p>
<ul>
<li>1 short — POST OK, look at display/cables next → <code>post ok</code></li>
<li>repeating short — display path → <code>post display</code></li>
<li>long beeps or “MEM” — memory → <code>post memory</code></li>
<li>no beep, no fan — power or board → <code>post power</code></li>
</ul>
<p>Seeded card: long beeps / MEM. <code>post memory</code>.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Storage word for the card</h3>
<p>M.2 stick in the short slot → <code>storage nvme</code>. 2.5 in SATA tray → <code>storage sata</code>. You are naming the interface, not the brand.</p>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>form-factor atx because the case is a “tower”</li>
<li>storage sata because “all disks are SATA”</li>
<li>post display because there is no video — the LED already said MEM</li>
</ul></div>
<div class="check-box"><h4>Pass bar</h4>
<p>Submit succeeds. You can point at the six connectors on a real chassis. You did not open a live box to reseat RAM during the lab.</p>
</div>'''
        },
        {
            "order": 6,
            "minutes": 55,
            "title": "2.6 Inventory the Running Box",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Read Windows identity: device name, edition, build — before you change anything</li>
<li>Collect hostname / whoami / systeminfo as ticket evidence</li>
<li>List disks before any wipe or image</li>
<li>Write those facts into the same note style as Block 1</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 55 minutes</h4>
<p>Hardware card is done. Now the box is running. Demo Settings → System → About, then a cmd window: hostname, whoami, systeminfo | more, diskpart → list disk. Nobody types clean or convert. Labs under this lesson: gui-about, w11-inventory, w11-disk, gui-devices.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.5 you can name the board. This lesson proves what the running OS thinks it is sitting on — required before imaging.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Replacing “the disk” without listing disks first is how you wipe the wrong one. Inventory is a ticket habit, not extra credit.</p></div>
<div class="live-demo"><h4>Labs on this lesson — run in this order</h4>
<ol>
<li><strong>gui-about</strong> — Settings → System → About. Read edition and device name.</li>
<li><strong>w11-inventory</strong> — hostname, whoami, systeminfo. Copy facts a night watch can use.</li>
<li><strong>w11-disk</strong> — list disk only. Say out loud which disk is the OS disk. Do not clean.</li>
<li><strong>gui-devices</strong> — Device Manager: Disk drives, Network adapters, Display adapters. Note a yellow bang if present.</li>
</ol>
<p>Then write a four-line note: name, edition/build, disk count and OS disk number, next step.</p></div>

<section id="s1" class="sublesson"><h3>1. About is the polite inventory</h3>
<p>Settings → System → About is what you can do with the user watching. Device name, edition, processor, RAM the OS sees. If About RAM and the DIMM count on the board disagree, you have a seating or firmware problem — go back to 2.4, do not image yet.</p>
</section>

<section id="s2" class="sublesson"><h3>2. CLI identity</h3>
<p><code>hostname</code> — the name on the wire.<br>
<code>whoami</code> — the account you are actually using.<br>
<code>systeminfo</code> — edition, build, install date, hotfixes. Pipe to more. Do not screenshot twenty pages into a ticket; pull the four lines that answer the question.</p>
</section>

<section id="s3" class="sublesson"><h3>3. List disk before any wipe</h3>
<p>diskpart → <code>list disk</code>. Size and whether it is GPT/MBR are enough to know which handle you are about to touch. <code>clean</code> and <code>convert</code> are not Block 2 commands. If the lab asks you only to list, you list and exit.</p>
</section>

<section id="s4" class="sublesson"><h3>4. Note that ties Block 1 to Block 2</h3>
<p>Example:</p>
<p><code>CIWT-W11-07, Windows 11 Education 23H2. systeminfo RAM 16 GB matches two DDR5 sticks. list disk: Disk 0 256 GB GPT (OS), Disk 1 0 GB empty. No wipe. Next: image only Disk 0 after backup confirm.</code></p>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Imaging before list disk</li>
<li>Trusting the sticker instead of About + systeminfo</li>
<li>Leaving diskpart open on a production box</li>
</ul></div>
<div class="check-box"><h4>Pass bar</h4>
<p>You can read name, edition, and disk list from the labs without a hint sheet, and your note would survive a 0200 handoff.</p>
</div>'''
        },
    ],
}
