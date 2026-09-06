"""CIWT Block 2 / Chapter 2 — PC architecture.
Original CIWT schoolhouse material. Not official Navy courseware.
A trainee should identify the board on the bench card and run Lab hw-board.
"""

CHAPTER2 = {
    "title": "Chapter 2 — PC Architecture: Motherboard, CPU & Memory",
    "order": 2,
    "minutes": 200,
    "overview": (
        "Name the board, socket, memory generation, and storage interface on a real chassis "
        "before you unplug anything. Then isolate POST in order. Lab hw-board uses the same words."
    ),
    "lessons": [
        {
            "order": 1,
            "title": "2.1 Motherboards, Form Factors, and Chipsets",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Identify ATX, microATX, and Mini-ITX by screw pattern and size, not by guessing the box art</li>
<li>Explain what a chipset allows: which CPU family and which features the board will actually run</li>
<li>Point to 24-pin ATX, 8-pin CPU, RAM slots, and M.2 notch on a photo or chassis</li>
<li>Use lab command <code>form-factor</code> with the exact name of the board on the bench card</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> Chapter 1 safety. Power off, unplug, strap on, then look. You do not identify a board while it is running and the side panel is half off.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>The motherboard is the city map. Every other part is an address on that map. Wrong size board will not mount. Wrong chipset will not talk to the CPU you bought. Wrong slot will not take the drive.</p></div>
<div class="live-demo"><h4>Lab hw-board — this lesson</h4>
<p><code>show board</code> prints the bench card (what you would see after the side panel is off).<br>
<code>form-factor atx</code> or <code>microatx</code> or <code>mini-itx</code> — one word, no spaces in mini-itx.<br>
Do not submit yet. Later lessons add socket, memory, storage, and POST.</p></div>

<section id="s1" class="sublesson"><h3>1. Form factor is the hole pattern</h3>
<p>Measure and count mounts. Marketing names lie; screw holes do not.</p>
<table class="port-table">
<tr><th>Name</th><th>About</th><th>Where you see it</th></tr>
<tr><td><strong>ATX</strong></td><td>Largest common desktop, 12 × 9.6 in</td><td>Full tower / standard office tower</td></tr>
<tr><td><strong>microATX</strong></td><td>Shorter, 9.6 × 9.6 in, fewer slots</td><td>Small office towers</td></tr>
<tr><td><strong>Mini-ITX</strong></td><td>~6.7 in square, usually one expansion slot</td><td>Tiny / HTPC / some shipboard compact boxes</td></tr>
</table>
<p>If the case says ATX and the board is Mini-ITX, the board will mount on the ATX holes that exist, but I/O shield and standoffs must still match. Never leave extra metal standoffs under an unused hole — they short the back of the board.</p>
<div class="analogy-box"><div class="analogy-label">Analogy · Rack unit</div>
<p>A 1U server does not become 2U because you want more fans. Form factor is the same idea in a desktop: the case and board agreed on a grid before either was built.</p></div>
</section>

<section id="s2" class="sublesson"><h3>2. Chipset and sockets (names only for now)</h3>
<p>The socket is the CPU hole. Intel desktop for this course: <strong>LGA</strong> (pads on the CPU, pins in the socket). AMD AM4/AM5: pins on the CPU. You will type <code>socket lga1700</code> or <code>socket am5</code> in the lab when the card shows that family.</p>
<p>The chipset is the traffic cop between CPU, RAM, storage, and USB. A board whose chipset does not list your CPU will either not POST or will run with features cut. Read the board model printed between the RAM slots or near the I/O — that string is what you search, not “the black one.”</p>
</section>

<section id="s3" class="sublesson"><h3>3. Connectors you must be able to point to</h3>
<ul>
<li>24-pin ATX — main board power</li>
<li>4/8-pin EPS near the CPU — CPU power (missing this = no POST or instant off)</li>
<li>RAM slots — usually 2 or 4, color-paired for channels</li>
<li>M.2 slot — short stick, screw at the end; look at the notch before you force it</li>
<li>SATA ports — L-shaped data, separate power from the PSU</li>
<li>Front-panel header — power switch / LED; wrong pins = “dead” PC that is only wired wrong</li>
</ul>
<p>Desk drill: on any training tower, point to those six with the panel off and power unplugged. Then <code>show board</code> in the lab and compare.</p>
</section>'''
        },
        {
            "order": 2,
            "title": "2.2 Firmware: UEFI, Secure Boot, and Settings",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Enter firmware setup on a training PC and leave it without changing a setting you cannot name</li>
<li>State what UEFI is for versus what the operating system is for</li>
<li>Explain Secure Boot in one sentence a user will accept</li>
<li>Know that a “dead” PC can be a firmware setting, not a dead board</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> 2.1 — you already know the board. Firmware is software that lives on the board and runs before Windows.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Firmware is the first program the CPU runs. It checks RAM and storage, then hands off to Windows. If firmware is set to “ignore this disk” or “Legacy only,” Windows looks dead and the board is fine.</p></div>
<div class="live-demo"><h4>Live demo on the training tower</h4>
<p>Power on, tap Del or F2 (your bench note says which). Do not change anything. Read: CPU name, RAM size, boot order. Exit without saving. Write those three numbers in your ticket if you ever suspect firmware.</p></div>

<section id="s1" class="sublesson"><h3>1. UEFI versus “the BIOS screen”</h3>
<p>People still say BIOS. Modern boards run <strong>UEFI</strong> — same job, larger disks, mouse, Secure Boot. You still get there with a key at power-on. If Windows is already up, Settings → Recovery → Advanced → UEFI Firmware Settings is the supported path. Do not yank power to “force BIOS” on a production box.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Secure Boot</h3>
<p>Secure Boot asks the firmware to start only a signed bootloader. That blocks some bootkits. It also blocks a USB installer that was not signed. If a shop disk will not boot, check Secure Boot before you declare the disk bad.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Settings that fake hardware failure</h3>
<ul>
<li>Wrong boot order — “no OS” when the NVMe is healthy</li>
<li>CSM/Legacy on a UEFI-only disk</li>
<li>RAM XMP profile the stick cannot run — random POST fail</li>
<li>Internal video disabled on a CPU with no discrete GPU installed</li>
</ul>
<p>Change one thing, save, test, write it down. Firmware is a change (Chapter 1.3). It is not a casual click.</p>
</section>'''
        },
        {
            "order": 3,
            "title": "2.3 CPUs, Cooling, and Performance Basics",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Match a CPU to a socket before you open the lever</li>
<li>Seat a cooler so the board does not bow and the pump/fan actually spins</li>
<li>Read a thermal complaint as “cooler or paste or load,” not “buy a new CPU first”</li>
<li>Use <code>socket</code> in lab hw-board with the socket printed on the card</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> 2.1 socket names. 2.2 firmware will show the CPU string after POST.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>The CPU does the work. The cooler keeps it alive. The socket is the only hole it fits. Wrong socket does not “almost fit.” Pins bend and the board is done.</p></div>
<div class="live-demo"><h4>Lab command this lesson</h4>
<p><code>socket lga1700</code> or <code>socket am5</code> (or the exact string on <code>show board</code>). If you guess, submit will fail later.</p></div>

<section id="s1" class="sublesson"><h3>1. Socket first</h3>
<p>Read the board silkscreen and the CPU box. LGA: no pins on the chip; do not scrape the pads. AM4/AM5: pins on the chip; do not set it on a screw. Open the load lever fully, seat, close. If it does not drop in flat, it is not aligned — do not press.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Cooler is part of the CPU</h3>
<p>A CPU with no cooler will throttle or die. Check: cooler mounted to the backplate, paste a thin even layer (no smears onto the socket), fan or pump header on CPU_FAN so firmware can see RPM. A “fine CPU” that shuts down at 10 minutes is often a fan header on SYS_FAN and a zero-RPM reading in firmware.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Performance without myth</h3>
<p>Core count, cache, and generation matter. Clock-speed stickers from 2012 do not. For this course: identify the part, confirm firmware sees it, confirm cooler RPM. Tuning comes later. If firmware does not list the CPU, you have a support-list problem, not a “slow chip.”</p>
</section>'''
        },
        {
            "order": 4,
            "title": "2.4 Memory Technologies and Channels",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Tell DDR4 from DDR5 by the notch, not by the sticker if the sticker is missing</li>
<li>Populate the color-paired slots the board manual calls Channel A/B</li>
<li>Treat a no-POST after a RAM change as “reseated / wrong generation / dirty slot” before “dead CPU”</li>
<li>Type <code>memory ddr4</code> or <code>memory ddr5</code> in the lab</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> 2.1 RAM slots and 2.3 “if it does not drop in, stop.”</div>
<div class="plain-english"><h4>In plain English</h4>
<p>RAM is short-term work space. Wrong generation will not latch. One stick in the wrong slot can POST and run at half speed, or not POST at all.</p></div>
<div class="live-demo"><h4>Lab command this lesson</h4>
<p><code>memory ddr5</code> (or ddr4 if the card says so). Notch position is different. Do not file the notch. Do not stack a DDR4 stick in a DDR5 slot “to try.”</p></div>

<section id="s1" class="sublesson"><h3>1. Generation and notch</h3>
<p>DDR4 and DDR5 modules look similar from two feet away. The notch is offset differently. Voltage and controller are different. The slot will fight you if you are wrong — that fight is information. Stop.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Channels</h3>
<p>Two matched sticks in the paired slots (often 2 and 4, check the manual printed on the board) run dual channel. One stick works. Four unmatched kits can POST and then blue-screen. Match size and generation first; speed second.</p>
</section>

<section id="s3" class="sublesson"><h3>3. When RAM looks like a dead board</h3>
<p>No video after you “just added memory”: reseat both sticks, try one known-good stick in slot A2, clear firmware only if the shop procedure says so. Write each test. Chapter 2.5 will add beep codes. In the lab the POST answer for this bench card is memory — you will type it after you read the beep line.</p>
</section>'''
        },
        {
            "order": 5,
            "title": "2.5 POST Isolation and Hardware Order",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Use a fixed order: power → board lights → beep/POST → display → firmware → OS</li>
<li>Map a simple beep or debug-LED pattern to “memory / display / CPU” without inventing codes</li>
<li>Finish lab <strong>hw-board</strong>: form-factor, socket, memory, storage, post, submit</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> 2.1–2.4 names. This lesson is the order you work a dark tower.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>POST is the board checking parts before Windows. No POST means you do not reinstall Windows. You work hardware in order so you do not replace the CPU because a stick of RAM is half out.</p></div>
<div class="live-demo"><h4>Finish lab hw-board</h4>
<ol>
<li><code>show board</code></li>
<li><code>form-factor ...</code> <code>socket ...</code> <code>memory ...</code> <code>storage ...</code></li>
<li><code>post memory</code> (this card’s beep line is a memory fail — the lesson tells you that below)</li>
<li><code>submit</code></li>
</ol>
<p>Wrong guesses stay wrong until you change them. Submit lists what is still missing or incorrect.</p></div>

<section id="s1" class="sublesson"><h3>1. Order of work</h3>
<ol>
<li>Power present at the wall and PSU switch</li>
<li>Board LED / fan twitch on power button</li>
<li>Beep or debug code</li>
<li>Display</li>
<li>Firmware</li>
<li>Windows</li>
</ol>
<p>Skip a step and you will “fix” the OS on a box that never left POST.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Beeps on this course’s bench card</h3>
<p>Vendors do not share one universal codebook. For <strong>this lab</strong> use the card:</p>
<ul>
<li>1 short — POST OK, look at display/cables next</li>
<li>repeating short — display path</li>
<li>long beeps or “MEM” on a debug LED — memory</li>
<li>no beep, no fan — power or board</li>
</ul>
<p>The seeded card says long beeps / MEM. Command: <code>post memory</code>.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Storage word for the card</h3>
<p>If the card shows an M.2 stick in the short slot, that is <code>storage nvme</code>. If it shows a 2.5 in SATA tray, <code>storage sata</code>. You are naming the interface, not the brand.</p>
</section>'''
        },
    ],
}
