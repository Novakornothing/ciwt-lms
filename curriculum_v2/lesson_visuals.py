"""Interactive Visual Architecture Blueprints & Technical Spec Reference Cards for all 115 Novak LMS™ lessons.

Provides curated per-lesson SVG topology/signal-flow diagrams (`viewBox="0 0 760 175"`),
4-6 row technical specification & CLI reference tables (`<table class="novak-spec-table">`),
and interactive field/exam watchout callouts (`<details class="novak-field-watchout">`).

Safe for Explanation Ladder (`curriculum_v2/ladder/sections.py`) and Cert Alignment:
- Never emits `<h2>`, `<h3>`, or `<section class="sublesson...">` inside the visual block.
- Appends the `<aside class="novak-visual-blueprint" ...>` cleanly at the end of `lesson.content`
  (or strips and replaces any prior `<aside class="novak-visual-blueprint"...>` idempotently).
"""
from __future__ import annotations

import re
from html import escape

_ASIDE_RE = re.compile(
    r'\n*<aside\s+class="novak-visual-blueprint"[^>]*>.*?</aside>\n*',
    re.DOTALL | re.IGNORECASE,
)

# Compact, compactly structured per-lesson blueprints keyed by label ("1.1", "N1.1", etc.)
# Format: (arch_title, [(stage_title, stage_sub, badge), ...], [(param, spec, cli_or_std, symptom), ...], watchout_title, watchout_body)
BLUEPRINTS_ITSUP = {
    "1.1": (
        "Support Intake & Ticket Classification Pipeline",
        [("1. User Contact", "Outcome Disrupted", "INTAKE"),
         ("2. Identity Check", "Verify Caller First", "AUTH GATE"),
         ("3. Classify Work", "Incident vs Request", "TRIAGE"),
         ("4. Scope & Impact", "1 User vs Floor/Site", "PRIORITY"),
         ("5. Action / Route", "Restore & Document", "CLOSURE")],
        [("Incident", "Unplanned loss or degradation of service", "Break/Fix Triage", "30 users lose shared drive at 09:10 -> High-impact incident"),
         ("Service Request", "Planned request for standard item/access", "Catalog / Approval", "New starter needs laptop & mailbox next Monday"),
         ("Change Record", "Planned modification to shared production", "CAB / Backout Plan", "Upgrading switch firmware or modifying GPO"),
         ("Identity Gate", "Verify caller before any account/data action", "Out-of-band / MFA Callback", "Urgent 'CFO' caller requesting immediate password read-out"),
         ("Ticket Handoff", "Symptom, scope, tests run, result, next step", "Structured Queue Note", "Vague 'VPN broken' forces Tier 2 to restart from zero")],
        "Incident vs. Service Request & Urgent Caller Trap",
        "Exam items frequently disguise a social-engineering password reset as an 'urgent executive incident.' Always verify identity through an approved channel before touching credentials, and classify unplanned outages by impact (users affected) + urgency.",
    ),
    "1.2": (
        "Bench Electrical & ESD Protection Path",
        [("1. De-Energize", "Unplug AC Mains", "ISOLATE"),
         ("2. Drain Flea Power", "Hold Power 5-10s", "DISCHARGE"),
         ("3. Bond Technician", "1 MOhm Wrist Strap", "ESD MAT"),
         ("4. Handle by Edges", "Zero Pin/Gold Contact", "TRANSFER"),
         ("5. Antistatic Bag", "Shielded Storage", "STAGE")],
        [("ESD Latent Threshold", "100 V - 300 V damages CMOS gates unseen", "ANSI/ESD S20.20 (< 3,000 V felt)", "Random BSODs weeks after bare-handed RAM upgrade"),
         ("Wrist Strap Resistor", "1 MOhm series current-limiting resistor", "Clip to bare chassis / ESD mat", "Direct low-ohm wire to AC ground creates shock hazard"),
         ("PSU Servicing Rule", "Sealed FRU — never open a power supply", "300 V+ primary bulk capacitors", "Lethal stored charge remains after AC cord removal"),
         ("Self-Grounding Rule", "Unplug AC cord before working inside PC", "ESD mat + chassis clip", "Leaving AC plugged in energizes +5VSB standby rail"),
         ("Laser Printer Hazard", "Fuser reaches ~200 C; HV corona wire", "Power off & cool 15+ min", "Toner vacuumed with standard shop vac creates static fire")],
        "Never Open a PSU & Never Use a Standard Vacuum on Toner",
        "Two classic safety traps: (1) Opening a PSU casing to replace a fuse exposes 300V+ primary capacitors; always replace the PSU as a sealed FRU. (2) Standard vacuums lack HEPA filtration and generate ESD sparks on fine toner.",
    ),
    "1.3": (
        "Repeatable Ticket Documentation & Change Boundary",
        [("1. Exact Symptom", "Verbatim Error / Time", "FACT"),
         ("2. Scope Matrix", "Who / Where / Since", "BOUNDARY"),
         ("3. One Test / Step", "Action -> Result Pair", "EVIDENCE"),
         ("4. Change Check", "Repair vs New State", "CONTROL"),
         ("5. Handoff / Close", "Verified + Next Step", "AUDIT")],
        [("Symptom Capture", "Exact error code, timestamp, affected app", "Event ID / Screenshot", "'It is slow' gives zero reproducible baseline"),
         ("Fact vs Hypothesis", "Separate measured outputs from theories", "Label 'Hypothesis:' explicitly", "Writing 'DNS is down' when only one URL failed"),
         ("One-Change Rule", "Modify one variable per test iteration", "Revert if test disproves theory", "Changing cable, IP, and driver at once hides root cause"),
         ("Change Escalation", "Shared infra edits require change approval", "Standard / Normal / Emergency", "Rebooting a classroom switch mid-exam without notice"),
         ("Closure Triad", "Root cause + action taken + user verification", "Searchable KB tags", "Closing 'Fixed' without recording what changed")],
        "Stating a Guess as a Confirmed Fact in Escalation Notes",
        "When escalating to Tier 2 or Network Ops, never write 'Firewall is blocking port 443' unless you proved it. Write the exact command and output (`Test-NetConnection 10.20.30.5 -Port 443 -> TcpTestSucceeded: False`) so the receiving team trusts your evidence.",
    ),
    "1.4": (
        "User Outcome Communication & Floor Privacy Gate",
        [("1. Listen Active", "No Interruption", "INTAKE"),
         ("2. Translate Tech", "Outcome Language", "CLARITY"),
         ("3. Privacy Shield", "Lock Screen / No PII", "COMPLIANCE"),
         ("4. Policy Boundary", "Polite Refusal + Path", "ETHICS"),
         ("5. Dual Notes", "User Summary vs Tech", "RECORD")],
        [("Outcome Framing", "Translate jargon into work impact & ETA", "Plain-language status update", "Telling an accountant 'Your Kerberos ticket expired'"),
         ("Credential Hygiene", "Never ask for or record a user's password", "Temporary reset / self-service", "Writing a user's password in a plain-text ticket field"),
         ("Shoulder Surfing", "Lock screen (Win+L) & close personal tabs", "Minimum necessary access", "Screenshotting a user's open banking tab in a bug report"),
         ("Policy Refusal", "Say what you CAN do via approved process", "Cite policy + offer request form", "Installing unlicensed software to 'be helpful'"),
         ("Regulated Data", "PII, PHI, PCI require strict need-to-know", "Escalate exposure to supervisor", "Discussing a student's accommodation record in the hallway")],
        "Never Record Passwords or Unrelated Personal Screen Data",
        "Technicians never need a user's current password to troubleshoot. If you must sign in as the user, use an approved administrative workflow or supervised session, and ask the user to close unrelated personal/financial windows before capturing screenshots.",
    ),
    "1.5": (
        "Safe Intake Capstone End-to-End Workflow",
        [("1. Safety Check", "Swollen Battery / AC?", "STOP GATE"),
         ("2. Verify & Scope", "Caller + Blast Radius", "CLASSIFY"),
         ("3. Classify Ticket", "Incident / Req / Chg", "QUEUE"),
         ("4. Baseline Tests", "Read-Only Evidence", "ISOLATE"),
         ("5. Structured Note", "Facts + Next Owner", "SUBMIT")],
        [("Safety Stop Gate", "Halt hands-on work for electrical/chemical risk", "Swollen Li-ion / burning smell", "Running software diagnostics on a smoking PSU"),
         ("High-Impact Incident", "Multi-user outage prioritizes escalation", "Notify lead + status board", "Working a 40-user switch outage silently for 2 hours"),
         ("Read-Only First", "Capture state before resetting or rebooting", "ipconfig /all, hostname, logs", "Rebooting before reading the error dialog"),
         ("Single Variable", "Test one change and verify outcome", "Document before/after state", "Stacking three registry edits without a checkpoint"),
         ("Handoff Completeness", "Who, what, scope, tests, results, next step", "Peer-ready ticket standard", "Escalating without attaching the IP/hostname tested")],
        "Skipping the Safety Stop Gate to 'Just Grab the Files First'",
        "If an intake involves a swollen lithium-ion pouch battery, liquid spill on live AC, or burning odor, the immediate correct action is a physical safety stop—never power on the unit to 'back up one quick folder.'",
    ),
}

BLUEPRINTS_ITSUP.update({
    "2.1": (
        "Motherboard Form Factors, Chipset & Bus Topology",
        [("1. CPU Socket", "LGA 1700 / AM5", "COMPUTE"),
         ("2. Direct Lanes", "PCIe x16 + Primary M.2", "CPU BUS"),
         ("3. DMI / Chipset", "High-Speed Interconnect", "PCH / FCH"),
         ("4. Expansion & I/O", "SATA / USB / PCIe x1", "SOUTHBRIDGE"),
         ("5. Chassis Mount", "ATX / mATX / Mini-ITX", "STANDOFFS")],
        [("ATX Standard", "305 x 244 mm (12 x 9.6 in), up to 7 slots", "Full tower / mid-tower", "Extra brass standoff under board shorts solder traces"),
         ("microATX (mATX)", "244 x 244 mm (9.6 x 9.6 in), up to 4 slots", "Fits ATX & mATX cases", "Mismatched rear I/O shield blocks RJ-45/USB seating"),
         ("Mini-ITX", "170 x 170 mm (6.7 x 6.7 in), 1 PCIe slot", "SFF / compact builds", "Limited VRM cooling and 2 DIMM slots max"),
         ("24-Pin + 8-Pin EPS", "Main board power + dedicated CPU VRM 12V", "ATX12V v2.x / ATX 3.0", "Forgetting 8-pin CPU power -> fans spin, no POST"),
         ("M.2 Key M Socket", "PCIe x4 NVMe / SATA bus lane routing", "2280 form factor (22x80mm)", "Some SATA ports disable when M.2 shares PCH lanes")],
        "Forgotten 8-Pin EPS CPU Power or Misplaced Brass Standoff",
        "When a newly built PC spins its fans for a second or powers on with a black screen and no POST, check the 8-pin (4+4) CPU power connector at the top corner of the board and verify no extra brass standoff is shorting the underside.",
    ),
    "2.2": (
        "UEFI Boot Pipeline, GPT & Secure Boot Trust Chain",
        [("1. Power-On / SEC", "CPU Reset Vector", "ROM"),
         ("2. UEFI DXE Phase", "Init Hardware & GOP", "FIRMWARE"),
         ("3. Secure Boot", "Verify EFI Signature", "PK / KEK / db"),
         ("4. GPT ESP Partition", "bootmgfw.efi Loader", "FAT32 EFI"),
         ("5. OS Kernel Init", "TPM 2.0 + BitLocker", "WINDOWS")],
        [("UEFI vs Legacy CSM", "64-bit firmware, GUI/mouse, >2.2 TB boot", "Requires GPT + FAT32 ESP", "Switching UEFI to Legacy/CSM -> 'No Bootable Device'"),
         ("Secure Boot", "Cryptographically checks signed bootloaders", "PK, KEK, db, dbx databases", "Unsigned Linux/driver USB blocked until signed or disabled"),
         ("TPM 2.0 (fTPM/dTPM)", "Hardware root of trust for keys & measurements", "Required by Windows 11", "Clearing TPM without BitLocker recovery key locks OS volume"),
         ("RTC / CMOS Battery", "CR2032 3V coin cell backs volatile NVRAM/clock", "3.0 V nominal DC", "Dead CR2032 resets clock & boot order on every AC unplug"),
         ("Admin vs User Pass", "Supervisor password gates UEFI setup edits", "Boot password gates startup", "Setting supervisor password without recording locks shop bench")],
        "Flipping UEFI/CSM Mode or Clearing TPM Without the BitLocker Key",
        "Never toggle UEFI to Legacy CSM or clear the TPM to 'fix a boot error' before checking drive partitioning and BitLocker status. Changing boot mode makes a GPT OS unbootable, and clearing TPM forces a 48-digit BitLocker recovery prompt.",
    ),
    "2.3": (
        "CPU Socket Seating, Thermal Interface & PWM Cooling Loop",
        [("1. Socket Match", "Pin 1 Triangle Align", "ZERO FORCE"),
         ("2. Retention Lock", "Load Plate Secured", "CLAMP"),
         ("3. TIM Application", "Pea-Sized Paste Layer", "CONDUCT"),
         ("4. Heatsink Mount", "Cross-Pattern Torque", "PRESSURE"),
         ("5. 4-Pin CPU_FAN", "Tach + PWM Control", "CLOSED LOOP")],
        [("LGA vs PGA", "Pads on CPU (LGA) vs pins on CPU (PGA)", "Align golden triangle Pin 1", "Forcing lever or dropping corner bends delicate socket pins"),
         ("Thermal Paste (TIM)", "Fills microscopic air gaps between IHS & base", "Pea-sized dot; peel plastic film!", "Leaving clear plastic protective film on cooler -> 100 C throttle"),
         ("CPU_FAN 4-Pin PWM", "GND, +12V, Sense (tach), Control (PWM)", "Motherboard CPU_FAN header", "Plugging into CHA_FAN triggers 'CPU Fan Error' on POST"),
         ("Thermal Throttling", "CPU lowers clock/voltage at TjMax (~95-100 C)", "Sudden FPS drop / power-off", "Dried paste, dead AIO pump, or dust-caked radiator fins"),
         ("ARM64 vs x86-64", "RISC fixed-length instructions vs CISC x64", "x64 emulates x86; ARM64 SoC", "32-bit x86 OS limited to 4 GB RAM address space")],
        "The Forgotten Cooler Plastic Peel & Wrong Fan Header",
        "If a newly serviced PC boots fine but shuts down after 90 seconds or throttles to 400 MHz under load, inspect the thermal path: peel-off film left on the heatsink base, uneven X-pattern mounting pressure, or AIO pump header unplugged.",
    ),
    "2.4": (
        "Multi-Channel Memory Architecture & DIMM Population",
        [("1. CPU IMC", "Integrated Controller", "DUAL CHANNEL"),
         ("2. Channel A (A2)", "64-bit Data Bus", "PRIMARY SLOT"),
         ("3. Channel B (B2)", "64-bit Data Bus", "PAIRED SLOT"),
         ("4. SPD / XMP Profile", "JEDEC Timings Init", "TRAINING"),
         ("5. ECC / Parity", "Single-Bit Correction", "SERVER / WS")],
        [("DDR4 vs DDR5", "288-pin DIMM (different notch position!)", "DDR4: 1.2V | DDR5: 1.1V PMIC", "Notches prevent cross-insertion; never force a DIMM"),
         ("SODIMM Form Factor", "Small Outline DIMM for laptops & Mini-PCs", "DDR4: 260-pin | DDR5: 262-pin", "Insert at 30-45 deg angle, then press down until side clips click"),
         ("Dual-Channel Pairing", "Populate A2 + B2 (slots 2 & 4 from CPU)", "128-bit combined bandwidth", "Populating A1 + A2 runs both sticks in single-channel mode"),
         ("ECC Memory", "Detects & corrects single-bit flips on the fly", "Requires ECC CPU + chipset", "Workstation/server stability; non-ECC boards reject UDIMM ECC"),
         ("Unseated RAM Symptom", "No video, diagnostic DRAM LED or repeating beeps", "Reseat until both latches click", "8 GB shown with two 8 GB sticks installed -> one stick unseated")],
        "Populating Adjacent Slots (A1+A2) Instead of Paired Channels (A2+B2)",
        "Most 4-slot motherboards wire Channel A to A1/A2 and Channel B to B1/B2, requiring two DIMMs in A2 and B2 first. Putting two sticks right next to each other cuts memory bandwidth in half.",
    ),
    "2.5": (
        "POST Hardware Isolation Order & Diagnostic Signalling",
        [("1. Wall & PSU", "AC + 24/8-Pin Rails", "POWER GOOD"),
         ("2. Board & CPU", "VRM + Clock + Reset", "HEARTBEAT"),
         ("3. DRAM Training", "SPD Read + Memory Test", "BEEP / LED"),
         ("4. VGA / Display", "PCIe GPU + Video Out", "POST SCREEN"),
         ("5. Boot Handoff", "NVMe/SATA -> EFI OS", "BOOTLOADER")],
        [("No Power / Dead", "Zero fans, zero board LEDs", "Wall outlet -> PSU switch -> 24-pin", "Swapping motherboard before checking PSU rear rocker switch"),
         ("Fans Spin, No POST", "Power rails up, halts before video init", "Check 8-pin EPS + reseat RAM", "Repeating short/long beeps or amber DRAM Q-LED lit"),
         ("POST OK, No Video", "Single beep / Boot LED green, blank monitor", "Check monitor input & GPU port", "Monitor plugged into motherboard HDMI when CPU has no iGPU"),
         ("No Bootable Device", "POST completes, firmware cannot find EFI/OS", "Verify M.2/SATA detection & UEFI", "Loose SATA cable, dead SSD, or UEFI switched to Legacy"),
         ("Minimum-to-POST", "Board + CPU/cooler + 1 RAM stick + PSU", "Breadboard isolation method", "Isolates shorted USB header, bad GPU, or faulty storage drive")],
        "Monitor Plugged into Motherboard I/O Instead of Discrete GPU",
        "After moving a desktop or installing a graphics card, users frequently plug the HDMI/DisplayPort cable into the vertical motherboard rear I/O instead of the horizontal discrete GPU ports—producing 'POSTs normal, black screen.'",
    ),
    "2.6": (
        "Live System Inventory & Pre-Touch Disk Verification",
        [("1. GUI Identity", "Settings > System > About", "READ-ONLY"),
         ("2. CLI Identity", "hostname & whoami", "AUDIT TRAIL"),
         ("3. Build & Hardware", "systeminfo / msinfo32", "BASELINE"),
         ("4. Disk Enumeration", "Get-Disk / diskpart", "VERIFY TARGET"),
         ("5. Ticket Snapshot", "Paste Exact Output", "CHANGE GATE")],
        [("hostname / whoami", "Confirms target machine & active security context", "cmd / PowerShell read-only", "Running repair scripts on the wrong remote workstation"),
         ("Settings > About", "Device name, RAM, CPU, Edition, OS Build", "ms-settings:about / winver", "Attempting GPedit.msc on Windows 11 Home edition"),
         ("systeminfo", "OS version, install date, boot time, hotfixes", "systeminfo | findstr /B /C:\"OS\"", "User says 'I just rebooted' -> Boot Time shows 28 days ago"),
         ("Disk Inventory", "Lists disk numbers, sizes, GPT/MBR style", "Get-Disk / list disk", "Wiping Disk 0 (OS) instead of Disk 1 (USB) by guessing"),
         ("Asset Tag Correlation", "Tie serial number (BIOS) to ticket record", "Get-CimInstance Win32_BIOS", "Swapping drives without recording serials breaks warranty")],
        "Never Run Disk Operations Without Listing Disks First",
        "Disk numbers (Disk 0, Disk 1) can shift depending on NVMe/SATA enumeration order. Always inspect size, model, and partition layout with `Get-Disk` or `list disk` before imaging, partitioning, or formatting.",
    ),
    "3.1": (
        "Storage Bus Stack: SATA III AHCI vs. PCIe NVMe M.2",
        [("1. Application I/O", "File System Read/Write", "NTFS / APFS"),
         ("2. Storage Driver", "NVMe Queue vs AHCI", "64K QUEUES"),
         ("3. Bus Interface", "PCIe x4 vs SATA 6Gb/s", "LANES"),
         ("4. Physical Media", "3D NAND vs Platter", "M.2 / 2.5\""),
         ("5. SMART Telemetry", "Get-PhysicalDisk", "HEALTH")],
        [("3.5\" / 2.5\" HDD", "Spinning magnetic platters (5400 / 7200 RPM)", "SATA III (up to ~150-220 MB/s)", "Audible clicking/grinding -> immediate backup before total head crash"),
         ("2.5\" SATA SSD", "NAND flash over AHCI/SATA controller", "SATA III 6 Gbps (~550 MB/s max)", "Drop-in upgrade for older laptops/desktops with 7-pin SATA"),
         ("M.2 NVMe SSD", "NAND flash directly on PCIe x4 lanes", "PCIe 3.0 (~3.5 GB/s) / 4.0 (~7 GB/s)", "Key M (5 pins); ordering SATA M.2 (B+M) for NVMe-only slot fails"),
         ("SMART Health Check", "Self-Monitoring, Analysis and Reporting Tech", "Get-PhysicalDisk / Wear indicator", "High reallocated sectors or 'Warning' -> image/backup immediately"),
         ("M.2 Length Codes", "2242, 2260, 2280 (22 mm wide x 80 mm long)", "Standoff screw secures tail", "Mounting M.2 directly to board without standoff bends PCB")],
        "M.2 Connector Shapes vs. Underlying Bus Protocol (NVMe vs. SATA)",
        "M.2 is only a physical form factor. An M.2 drive can speak PCIe NVMe (Key M) or legacy SATA AHCI (often Key B+M). Always verify the motherboard manual's M.2 slot support table before ordering a replacement drive.",
    ),
    "3.2": (
        "RAID Redundancy Math vs. 3-2-1 Backup Architecture",
        [("1. Live Volume", "Active OS & User Data", "PRODUCTION"),
         ("2. RAID Controller", "Stripe / Mirror / Parity", "UPTIME ONLY"),
         ("3. Copy #1 (Local)", "Fast NAS / USB Image", "MEDIA 1"),
         ("4. Copy #2 (Offsite)", "Immutable Cloud / Vault", "MEDIA 2 + OFFSITE"),
         ("5. Restore Drill", "Verify RPO & RTO", "PROVEN")],
        [("RAID 0 (Striping)", "2+ disks; Usable = N x Disk; 0 fault tolerance", "Max speed, zero redundancy", "Any 1 disk failure destroys 100% of array data"),
         ("RAID 1 (Mirroring)", "2 disks; Usable = 50% (1 disk); 1-disk fault ok", "Exact duplicate writes", "Survives 1 disk failure; does NOT stop ransomware or rm -rf"),
         ("RAID 5 (Parity)", "3+ disks; Usable = (N-1) x Disk; 1-disk fault ok", "Distributed parity blocks", "2nd disk failing during heavy parity rebuild loses array"),
         ("RAID 10 (1+0)", "4+ even disks; Usable = 50%; fast + redundant", "Mirrored pairs striped together", "Survives 1 disk per mirrored pair (up to 2 if in different mirrors)"),
         ("3-2-1 Backup Rule", "3 copies, 2 media types, 1 offsite/air-gapped", "Full / Incremental / Differential", "Incremental is fastest to back up; requires Full + every Inc to restore")],
        "RAID and Cloud File Sync Are Availability Tools, NOT Backups",
        "If a user deletes a critical database or ransomware encrypts a shared folder, RAID 1/5/10 and OneDrive/Dropbox sync replicate the deletion or encryption instantaneously. Only a versioned, offline/immutable 3-2-1 backup restores the prior state.",
    ),
    "3.3": (
        "ATX Power Supply Rails, Connector Keying & UPS Protection",
        [("1. AC Wall Mains", "115V / 230V 50-60Hz", "LINE INPUT"),
         ("2. UPS Battery", "AVR + Pure Sine Wave", "RIDE-THROUGH"),
         ("3. PSU Rectifier", "80 PLUS Switching", "DC RAILS"),
         ("4. +12V / +5V / +3.3V", "24-Pin + EPS + PCIe", "DISTRIBUTION"),
         ("5. +5VSB Standby", "Wake-on-LAN / USB", "ALWAYS ON")],
        [("24-Pin ATX Main", "+12V, +5V, +3.3V, +5VSB, PS_ON# control", "Motherboard right edge", "Unlatched 20+4 split connector causes intermittent reboots"),
         ("CPU 8-Pin (4+4 EPS)", "Dedicated +12V for CPU VRM phases", "Top-left of motherboard", "Do NOT force a 6+2 PCIe GPU cable into the 8-pin CPU socket!"),
         ("PCIe 6+2 / 12V-2x6", "+12V high-current auxiliary GPU power", "75W slot + 150W (8-pin) / 600W", "Daisy-chaining one pigtail cable on a 350W GPU melts connectors"),
         ("Modular PSU Cables", "Detachable PSU-side pinouts are NOT standardized", "Use ONLY cables from that exact PSU", "Reusing old modular SATA cables fries SSDs instantly (+12V on +5V)"),
         ("Surge vs UPS", "Surge clips voltage spikes (Joules); UPS has battery", "Online / Line-Interactive UPS", "Surge strip provides 0 seconds of runtime during brownout/blackout")],
        "Never Mix Modular PSU Cables Across Brands or Models",
        "While the device ends (24-pin, SATA, PCIe) are standardized, the pinout on the PSU housing end varies wildly between manufacturers. Reusing existing modular cables when swapping a PSU frequently sends +12V into +5V storage rails, destroying every connected SSD/HDD.",
    ),
    "3.4": (
        "USB-C Alt-Mode / Display Signal Isolation Pipeline",
        [("1. Monitor Power", "AC + Correct Input Src", "PHYSICAL"),
         ("2. Cable & Adapter", "Passive vs Active DP/HDMI", "LINK LAYER"),
         ("3. Known-Good Test", "Swap Monitor / Port", "ISOLATE"),
         ("4. GPU Port Check", "Discrete vs Board I/O", "HARDWARE"),
         ("5. OS & Driver", "Win+P / Win+Ctrl+Shift+B", "SOFTWARE")],
        [("USB-C Connector", "24-pin reversible shell — capabilities vary", "USB 2.0 (480M) to USB4/TB4 (40G)", "Charge-only USB-C cable carries zero data or DisplayPort video"),
         ("Thunderbolt 3 / 4", "40 Gbps PCIe + DP Alt Mode + Power Delivery", "Lightning icon next to port", "Supports dual 4K displays + daisy-chaining over active cables"),
         ("DisplayPort vs HDMI", "DP latches (press tab!) & supports MST daisy-chain", "DP 1.4 / 2.1 | HDMI 2.0 / 2.1", "Yanking a latched DisplayPort cable rips the socket off the GPU"),
         ("Active vs Passive", "DP->HDMI needs active level-shifter for 4K60/eyefinity", "Directional cables (Source->Display)", "Plugging a directional HDMI/DP adapter backwards gives black screen"),
         ("Driver Reset Shortcut", "Restarts Windows graphics subsystem live", "Win+Ctrl+Shift+B + Win+P", "Recovers black screen after dock sleep without killing open work")],
        "Assuming Every USB-C Port and Cable Supports DisplayPort Video",
        "USB-C is a physical shape, not a bandwidth or video guarantee. When an external USB-C monitor says 'No Signal,' check three things: (1) port markings for DP Alt Mode or Thunderbolt, (2) a full-featured USB-C cable (not a 2-wire charging cable), and (3) `Win+P` projection mode.",
    ),
    "3.5": (
        "Unstable Workstation Multi-Domain Isolation Order",
        [("1. Safety & Intake", "Smell / Heat / Scope", "TRIAGE"),
         ("2. POST & Thermals", "Cooler / PSU / RAM", "HARDWARE"),
         ("3. Storage Health", "SMART / Free Space", "DISK GATE"),
         ("4. Event & Reliab.", "perfmon /rel & WHEA", "EVIDENCE"),
         ("5. Single Change", "Verify & Document", "CLOSURE")],
        [("Thermal Shutdown", "Sudden power-off under heavy load after minutes", "Check CPU_FAN, dust, TIM paste", "Replacing OS image when CPU cooler pump is dead"),
         ("PSU Instability", "Random instant resets during GPU/CPU spikes", "Check wattage budget & 12V cables", "Kernel-Power Event ID 41 (unexpected loss of power)"),
         ("RAM Fault", "BSOD MEMORY_MANAGEMENT / amber DRAM LED", "Reseat A2/B2, run mdsched.exe", "Corrupts open files and OS updates if left unisolated"),
         ("Failing SSD/HDD", "Freeze bursts, Event ID 7/11/129 (stornvme/disk)", "Get-PhysicalDisk -> Backup first!", "Running heavy chkdsk /r on a dying drive kills its last hours"),
         ("Display-Only Fault", "PC stays on (Caps Lock toggles, audio plays)", "Win+Ctrl+Shift+B + swap cable", "Hard-holding power button when only the monitor lost sync")],
        "Back Up User Data BEFORE Stress-Testing a Failing Drive",
        "If `Get-PhysicalDisk` or SMART shows media wear warnings or bad blocks, do NOT run multi-hour surface scans or OS reinstalls first. Copy critical user data to safe storage while the drive is still spinning/responding.",
    ),
    "4.1": (
        "Laptop FRU Servicing & Li-Ion Battery Safe Sequence",
        [("1. Service Tag / Manual", "Verify FRU Part #", "LOOKUP"),
         ("2. Swell Inspection", "Flat Trackpad / Case?", "SAFETY STOP"),
         ("3. Disable Batt UEFI", "Unplug AC + Internal", "DE-ENERGIZE"),
         ("4. Flea Drain & ESD", "Hold Power + Strap", "ISOLATE"),
         ("5. Ordered Screw Map", "Replace FRU & Report", "VERIFY")],
        [("Li-Ion Swelling Stop", "Pouch cell off-gassing lifts trackpad/bottom cover", "STOP! Do not puncture or charge", "Prying a glued swollen battery with a metal screwdriver -> thermal runaway"),
         ("Power-Down Sequence", "Unplug AC -> UEFI Disable Battery -> Unplug cable", "Drain flea power before touching RAM", "Dropping a screw onto board with internal battery live blows backlight fuse"),
         ("Common Laptop FRUs", "SODIMM RAM, M.2 SSD, Wi-Fi card, battery, fan", "Check vendor Hardware Maint. Manual", "Soldered LPDDR5/eMMC cannot be upgraded without board swap"),
         ("Display Hinges/Cables", "eDP video cable & Wi-Fi antennas route through hinge", "White/Main + Black/Aux coax snaps", "Pinched eDP cable causes flicker when lid moves; swapped antenna kills 5GHz"),
         ("Battery Health CLI", "Compares Design Capacity vs Full Charge Capacity", "powercfg /batteryreport", "Full charge at 35% of design capacity explains 'dies in 40 minutes'")],
        "Never Pull the eDP LCD Cable Before Disconnecting the Internal Battery",
        "Laptop eDP screen connectors carry an always-on high-voltage backlight rail even when the laptop appears shut down. Unplugging or crookedly seating the LCD ribbon while the internal battery is connected instantly blows the motherboard backlight fuse.",
    ),
    "4.2": (
        "Mobile Radio Isolation & MDM Retire vs. Wipe Lifecycle",
        [("1. Radio Check", "Airplane / Wi-Fi / Cell", "LAYER 1-2"),
         ("2. Tunnel / VPN", "Per-App VPN / Proxy", "ROUTING"),
         ("3. Identity & Token", "SSO / MFA / Certs", "AUTH"),
         ("4. MDM Policy", "Compliance / Profile", "INTUNE / JAMF"),
         ("5. Lifecycle Action", "Retire vs Full Wipe", "DEPROVISION")],
        [("Wi-Fi vs Cellular", "Test on Wi-Fi then Wi-Fi off (cellular only)", "Isolates LAN/DNS vs carrier APN", "Blaming the phone when office Wi-Fi VLAN has an expired DHCP scope"),
         ("MDM Retire (Selective)", "Removes ONLY corporate apps, email & work data", "Keeps personal photos & contacts", "Best choice for BYOD employee leaving the company"),
         ("MDM Wipe (Factory)", "Erases 100% of device back to out-of-box state", "Destroys all personal + work data", "Used for lost/stolen corporate-owned (COPE/COD) devices"),
         ("Activation Lock / FRP", "Apple iCloud / Google Factory Reset Protection", "Managed via ABM / Zero-Touch", "Factory-resetting a turn-in phone without removing user Apple ID bricks it"),
         ("MFA Push Fatigue", "Unsolicited MFA prompts indicate credential theft", "Deny push + reset password", "Approving a 2 AM push prompt grants attacker an active session token")],
        "Wiping a BYOD Phone Instead of Retiring It (or Resetting Without ABM/FRP Release)",
        "On a BYOD device, a full MDM Wipe destroys the employee's personal family photos—always use **Retire** (selective corporate wipe) for BYOD offboarding. On corporate iPhones, verify Apple Business Manager (ABM) supervision before accepting a device return.",
    ),
    "4.3": (
        "Network Print Path & Laser Imaging 7-Step Process",
        [("1. App & GDI/XPS", "Print Job Generated", "CLIENT"),
         ("2. Print Spooler", "C:\\...\\spool\\PRINTERS", "SERVICE"),
         ("3. Driver & PDL", "PCL6 / PostScript / IPP", "RENDER"),
         ("4. Port / Network", "TCP 631 IPP / 9100 Raw", "TRANSPORT"),
         ("5. Laser Engine", "Charge->Expose->Fuse", "HARDWARE")],
        [("Stuck Print Queue", "Corrupt .SPL/.SHD file blocks all subsequent jobs", "net stop spooler -> del PRINTERS\\* -> start", "Restarting spooler without deleting stuck files in spool\\PRINTERS"),
         ("Network Print Ports", "IPP: TCP 631 (TLS) | Raw JetDirect: 9100 | LPD: 515", "Use static IP or DHCP reservation", "Printer on dynamic DHCP changes IP -> port points to dead address"),
         ("Garbled / ASCII Pages", "Reams of symbols/smiley faces printing endlessly", "Wrong PDL driver (PS vs PCL)", "Replace driver with matching model PCL6/PS or IPP Class Driver"),
         ("Laser 7-Step Order", "Processing, Charging, Exposing, Developing, Transferring, Fusing, Cleaning", "Fuser melts toner with heat+pressure", "Toner smudges off with finger -> Fuser assembly failing"),
         ("Ghosting / Streaks", "Faint repeat image down page or vertical black line", "Drum / cleaning blade / transfer belt", "Replacing toner cartridge when imaging drum or fuser is worn")],
        "Smudging Toner = Fuser Fault; Garbled Symbols = Driver/PDL Mismatch",
        "Exam items love matching print defects to laser stages: if toner rubs off on your fingers, the **fuser** isn't melting it into the paper. If pages print lines of random wingdings/symbols, the **driver** (PCL vs PostScript) doesn't match the printer.",
    ),
    "4.4": (
        "Portable & Print Capstone Triage Matrix",
        [("1. Safety Screen", "Battery / Fuser Heat", "GATE 1"),
         ("2. Scope & Owner", "1 User vs Shared Queue", "GATE 2"),
         ("3. Path Isolation", "Radio / Spool / Port", "GATE 3"),
         ("4. Policy Check", "BYOD Retire vs Wipe", "GATE 4"),
         ("5. Evidence Handoff", "FRU / IP / Queue Note", "SUBMIT")],
        [("Swollen Laptop Trackpad", "Immediate safety stop; unplug AC, do not charge", "Order battery FRU + ESD bag", "Forcing the bottom cover shut cracks the trackpad glass"),
         ("Shared Printer Down", "Check scope: can anyone print? Ping printer IP", "Check TCP 9100/631 & reservation", "Reinstalling drivers on 20 PCs when the printer changed its DHCP IP"),
         ("Single PC Can't Print", "Other PCs print fine to the same printer", "Clear local spool\\PRINTERS & driver", "Power-cycling the floor copier while 10 others are scanning"),
         ("Offboarding BYOD", "Remove company data while preserving personal", "Issue MDM Retire (not Full Wipe)", "Factory-wiping a contractor's personal smartphone"),
         ("Turn-In Corporate Phone", "Check ABM/MDM lock status before user leaves", "Sign out / release Activation Lock", "Discovering iCloud Activation Lock after employee leaves country")],
        "Scope First: One User's Spooler vs. Floor Printer's IP Address",
        "Before touching a shared network printer or resetting a print server, ask: 'Can a neighbor print to it?' If others print fine, the fault is on the single client (spooler/driver/VLAN). If nobody can print, check the printer's physical state and IP reservation.",
    ),
})

BLUEPRINTS_ITSUP.update({
    "5.1": (
        "IPv4 Prefix Math, RFC 1918 Private Ranges & APIPA Fallback",
        [("1. NIC Link Up", "MAC 48-bit burned-in", "LAYER 2"),
         ("2. DHCP or Static", "IP + Mask + Gateway", "LAYER 3"),
         ("3. APIPA Fallback", "169.254.x.x /16", "NO DHCP!"),
         ("4. Subnet Mask", "2^(32-p) - 2 Hosts", "LOCAL VS GW"),
         ("5. NAT Egress", "RFC 1918 -> Public IP", "WAN EDGE")],
        [("RFC 1918 Private", "10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16", "Requires NAT for Internet", "172.32.x.x is PUBLIC, not RFC 1918 private (ends at 172.31.255.255)"),
         ("APIPA / Link-Local", "169.254.0.1 - 169.254.255.254 (/16), no gateway", "DHCP Discover timed out", "Client cannot reach default gateway or Internet; check VLAN/DHCP"),
         ("Loopback Range", "127.0.0.0/8 (127.0.0.1) & IPv6 ::1/128", "Tests local OS TCP/IP stack", "Never appears on physical wire; verifies local NIC driver stack"),
         ("CIDR Host Math", "/24 = 254 hosts | /26 = 62 | /27 = 30 | /30 = 2", "Usable = 2^(32-prefix) - 2", "Subtract 2 for Network ID (all 0s) and Broadcast (all 1s)"),
         ("IPv6 Link-Local", "fe80::/10 auto-assigned on every active IPv6 NIC", "Global unicast: 2000::/3", "Seeing fe80:: is completely normal and does NOT mean DHCP failed")],
        "169.254.x.x (APIPA) Means DHCP Unreachable — fe80:: Is Normal IPv6",
        "When `ipconfig /all` shows `Autoconfiguration IPv4 Address: 169.254.x.x` with an empty Default Gateway, the NIC never heard a DHCP Offer (bad cable, wrong VLAN, dead DHCP scope). By contrast, `fe80::` is normal on every IPv6 interface.",
    ),
    "5.2": (
        "DHCP DORA Handshake & Well-Known Service Ports",
        [("1. DHCP Discover", "UDP 68 -> 67 Broadcast", "CLIENT"),
         ("2. DHCP Offer", "UDP 67 -> 68 Proposal", "SERVER"),
         ("3. DHCP Request", "UDP 68 -> 67 Accept", "CLIENT"),
         ("4. DHCP Ack + Opts", "IP, Mask, GW(3), DNS(6)", "LEASED"),
         ("5. Service Connect", "DNS 53 -> HTTPS 443", "APP FLOW")],
        [("DHCP (DORA)", "UDP 67 (Server) / UDP 68 (Client)", "T1=50% unicast, T2=87.5% bcast", "Blocked UDP 67/68 or missing IP helper drops client to 169.254.x.x"),
         ("DNS Lookup", "UDP 53 (standard queries) / TCP 53 (zone/large)", "nslookup / Resolve-DnsName", "Ping 8.8.8.8 works but ping example.com fails -> DNS port 53/config"),
         ("Web & Remote", "HTTP 80, HTTPS 443, SSH 22, RDP 3389", "Test-NetConnection -Port <N>", "ICMP ping succeeds even when Windows Firewall blocks TCP 3389 RDP"),
         ("File & Directory", "SMB 445, LDAP 389, LDAPS 636, Kerberos 88", "Domain join & UNC shares", "Blocking TCP 445 breaks `\\\\server\\share` file access"),
         ("Mail Protocols", "SMTP 25/587, IMAP 143/993, POP3 110/995", "TLS versions: 587, 993, 995", "Using legacy cleartext port 23 (Telnet) or 110 instead of SSH/TLS")],
        "Ping (ICMP) Does NOT Test a TCP Service Port",
        "A server can reply to `ping` (ICMP Echo) while its web server (TCP 443) or RDP service (TCP 3389) is stopped or blocked by a host firewall. Conversely, a server can block ICMP while serving HTTPS normally. Test the actual port with `Test-NetConnection`.",
    ),
    "5.3": (
        "Seven-Step Client Connectivity Isolation Ladder",
        [("1. Link / Media", "LEDs / SSID Connected", "LAYER 1-2"),
         ("2. Local Lease", "ipconfig /all (No 169.254)", "DHCP"),
         ("3. Default Gateway", "ping <Gateway_IP>", "LOCAL LAN"),
         ("4. Remote IP", "ping 1.1.1.1 / 8.8.8.8", "ROUTING/NAT"),
         ("5. Name & Port", "nslookup + TNC 443", "DNS / APP")],
        [("Step 1: Physical/Link", "Verify link lights or Wi-Fi association state", "Get-NetAdapter / ncpa.cpl", "Media Disconnected -> check patch cord, wall jack, or Wi-Fi switch"),
         ("Step 2: IP & Mask", "Confirm valid subnet IP, mask, and lease expiry", "ipconfig /all", "169.254.x.x -> Layer 2/VLAN/DHCP fault; stop pinging external hosts"),
         ("Step 3: Ping Gateway", "Proves Layer 2 switching & ARP to local router", "ping <Default_Gateway>", "Gateway ping fails -> wrong subnet mask, VLAN mismatch, or gateway down"),
         ("Step 4: Ping Remote IP", "Proves WAN routing and NAT past the gateway", "ping 8.8.8.8 / tracert -d", "Gateway replies, 8.8.8.8 fails -> ISP link, WAN route, or NAT fault"),
         ("Step 5: DNS & Service", "Compare IP reachability vs name resolution", "nslookup / Test-NetConnection", "8.8.8.8 replies, name fails -> wrong DNS server IP or DNS outage")],
        "Never Edit DNS or Browser Proxies Before Checking `ipconfig /all`",
        "If a client has `Media Disconnected` or `169.254.x.x`, flushing DNS (`ipconfig /flushdns`) or resetting Chrome cannot possibly help. Walk the ladder strictly from the wire/lease up to the application.",
    ),
    "5.4": (
        "SOHO Wireless Hardening, RF Bands & Channel Plan",
        [("1. Admin Plane", "Change Default Pass", "MGMT"),
         ("2. WPA3 / SAE", "Disable WPS & WEP/TKIP", "AUTH/CRYPT"),
         ("3. RF Band Plan", "2.4 (1,6,11) vs 5/6GHz", "SPECTRUM"),
         ("4. Guest Isolation", "Separate VLAN + Client Iso", "SEGMENT"),
         ("5. Client Verify", "netsh wlan show int", "EVIDENCE")],
        [("2.4 GHz Non-Overlap", "Channels 1, 6, and 11 only (20 MHz width)", "Longer range, high interference", "Picking channel 3 or 9 causes severe adjacent-channel interference"),
         ("5 GHz & 6 GHz (Wi-Fi 6E/7)", "More non-overlapping channels, 40/80/160 MHz", "Higher throughput, shorter range", "5 GHz DFS channels may radar-hop; 6 GHz requires WPA3/OWE"),
         ("WPA3-Personal (SAE)", "Simultaneous Authentication of Equals (128-bit+)", "Resists offline dictionary capture", "WPA2/WPA3 Transition Mode supports legacy IoT + modern clients"),
         ("WPS (Wi-Fi Protected Setup)", "8-digit PIN has only 11,000 effective combos", "DISABLE WPS in router settings", "Leaving WPS enabled lets brute-force tools crack WPA2 in hours"),
         ("SSID Broadcast & MAC", "Hiding SSID or MAC filtering is NOT encryption", "Probes reveal SSID; MACs spoofed", "Relying on hidden SSID with Open/WEP leaves all traffic readable")],
        "WPS Must Be Disabled & Channels 1, 6, 11 Are the Only 2.4 GHz Choices",
        "Even a 24-character WPA2/WPA3 passphrase is bypassed if Wi-Fi Protected Setup (WPS) PIN mode is left enabled. On 2.4 GHz, always assign channels **1, 6, or 11** at 20 MHz width.",
    ),
    "5.5": (
        "Client Network Ticket Capstone Triage Flow",
        [("1. Scope Outage", "1 PC vs Whole Floor", "BLAST RADIUS"),
         ("2. Read Lease", "ipconfig /all Snapshot", "FACT #1"),
         ("3. Gateway vs WAN", "Ping GW -> Ping 8.8.8.8", "FACT #2"),
         ("4. Name vs Port", "nslookup -> TNC Port", "FACT #3"),
         ("5. Escalate / Fix", "Action -> Result Note", "CLOSURE")],
        [("169.254.x.x on 1 PC", "Neighbors work; this PC has APIPA address", "Check patch cord, wall jack, renew", "Escalating to ISP when one cubicle patch cable is unplugged"),
         ("Gateway OK, WAN Dead", "All floor PCs ping 10.0.1.1; 8.8.8.8 times out", "Escalate to NetOps with hop trace", "Reinstalling NIC drivers on 30 workstations during a WAN cut"),
         ("WAN IP OK, Name Fails", "`ping 8.8.8.8` 4/4; `nslookup` times out", "Check DNS server IP / hosts file", "Static DNS pointing to decommissioned server 10.0.0.99"),
         ("Name OK, Port Blocked", "DNS resolves IP; `Test-NetConnection -Port 443` fails", "Check host/edge firewall & service", "Assuming 'network is down' when only the target web app crashed"),
         ("Escalation Boundary", "Never reconfigure shared switches/firewalls", "Attach exact CLI outputs to ticket", "Guessing VLAN IDs on a production closet switch without change approval")],
        "Distinguishing a Single-Drop Layer 1 Fault from a Floor-Wide Service Fault",
        "Two seconds of scoping ('Are your desk neighbors online?') saves an hour of wasted work. One user with APIPA points to the desk drop/port; twenty users losing DNS at 10:15 points to a shared infrastructure incident.",
    ),
    "6.1": (
        "Type 1 vs. Type 2 Hypervisor Stack & Host Readiness",
        [("1. Host CPU/BIOS", "VT-x / AMD-V + SLAT", "SILICON"),
         ("2. Hypervisor Layer", "Type 1 Bare vs Type 2 OS", "VMM SCHED"),
         ("3. Resource Pool", "vCPU, vRAM, VHDX Disk", "ALLOCATION"),
         ("4. Guest VM Isolation", "Independent OS Kernel", "SANDBOX"),
         ("5. Guest Additions", "Integration Drivers", "PARAVIRT")],
        [("Type 1 Hypervisor", "Runs directly on bare-metal server hardware", "Hyper-V, VMware ESXi, KVM/Proxmox", " Note: Enabling Hyper-V on Windows 11 turns the host into Type 1"),
         ("Type 2 Hypervisor", "Runs as an application inside a host OS", "VMware Workstation, VirtualBox", "Higher host OS overhead; ideal for local desktop lab sandboxes"),
         ("Firmware Virtualization", "Intel VT-x / VT-d or AMD-V / IOMMU in UEFI", "systeminfo -> Hyper-V Requirements", "'Virtualization Enabled in Firmware: No' blocks 64-bit VM startup"),
         ("Win 11 Hyper-V Edition", "Requires Windows 11 Pro, Enterprise, or Edu", "Windows 11 Home lacks Hyper-V", "Trying to enable Hyper-V feature on Windows 11 Home fails"),
         ("Containers vs VMs", "Containers share host OS kernel; VMs have full OS", "Docker / containerd vs Hyper-V VM", "Containers start in milliseconds but cannot run a different OS kernel natively")],
        "64-Bit VMs Refuse to Start When VT-x / AMD-V Is Disabled in UEFI",
        "If Hyper-V or VirtualBox throws an error that hardware virtualization is unavailable after a motherboard swap or BIOS reset, enter UEFI setup and enable **Intel VT-x (Virtualization Technology)** or **AMD SVM Mode**.",
    ),
    "6.2": (
        "Cloud Service Models (IaaS / PaaS / SaaS) Shared Responsibility",
        [("1. Physical DC", "Power, Cooling, Racks", "PROVIDER"),
         ("2. Compute & Net", "Hypervisor & Storage", "IAAS BOUNDARY"),
         ("3. Guest OS & Runtime", "Patching, Middleware", "PAAS BOUNDARY"),
         ("4. App & Config", "Tenant Admin Settings", "SAAS BOUNDARY"),
         ("5. Identity & Data", "Users, MFA, Access", "ALWAYS YOU")],
        [("IaaS (Infrastructure)", "Provider runs hardware/hypervisor; you patch OS", "AWS EC2, Azure VMs, Compute Engine", "Customer is responsible for Guest OS patching, firewall rules & AV"),
         ("PaaS (Platform)", "Provider patches OS & runtime; you deploy code", "Azure App Service, Cloud SQL, Heroku", "Developer manages app code & DB schema without patching Linux/Win"),
         ("SaaS (Software)", "Provider runs full app stack; you manage users/data", "Microsoft 365, Google Workspace, Salesforce", "Customer still owns user provisioning, MFA, and data classification"),
         ("NIST 5 Characteristics", "On-demand self-service, broad net access, pooling, rapid elasticity, measured service", "NIST SP 800-145 definition", "Confusing rapid elasticity (auto-scaling) with fixed hosting"),
         ("Deployment Models", "Public, Private, Hybrid, Community cloud", "Hybrid links on-prem + public via VPN", "Checking local NIC settings when vendor status page shows SaaS outage")],
        "The Customer Is ALWAYS Responsible for Identity, Accounts, and Data",
        "Even in 100% SaaS (like Microsoft 365), the cloud provider never decides which employees should have access or whether MFA is enforced. Account security, least privilege, and data governance always remain the customer's responsibility.",
    ),
    "6.3": (
        "Virtual Switch Modes (External / Internal / Private) & Checkpoints",
        [("1. Guest vNIC", "VM Virtual Adapter", "GUEST OS"),
         ("2. Virtual Switch", "Ext / Int / Private / NAT", "HYPERVISOR"),
         ("3. Host Physical NIC", "Bridged or NAT Uplinks", "HOST OS"),
         ("4. Differencing Disk", ".avhdx Checkpoint Tree", "SNAPSHOT"),
         ("5. Merge / Revert", "Delete Checkpoint Safely", "STORAGE")],
        [("External vSwitch (Bridged)", "Binds to physical NIC; VM gets LAN DHCP IP", "Reachable by other classroom PCs", "Binding to wrong host NIC (disconnected Wi-Fi vs Ethernet) drops VM"),
         ("Internal vSwitch / NAT", "VM <-> Host + VM <-> VM (Default Switch adds NAT)", "Isolated from direct LAN inbound", "VM can browse Internet via NAT but LAN peers cannot ping VM directly"),
         ("Private vSwitch", "VM <-> VM only; even Host OS cannot talk to VMs", "Isolated lab attack/AD segment", "Pinging from Host OS to a Private-switch VM always fails by design"),
         ("Checkpoints (Snapshots)", "Freezes base VHDX and writes changes to .avhdx", "Revert after risky patch/lab test", "Leaving 15 old checkpoints chains .avhdx files and fills host SSD"),
         ("Checkpoint != Backup", "Lives on same physical disk/volume as the VM", "Delete in Hyper-V Manager to merge", "Deleting .avhdx files manually in File Explorer corrupts the VM!")],
        "Never Delete `.avhdx` Files in File Explorer — Merge via Hypervisor Manager",
        "A checkpoint redirects new writes into a differencing disk (`.avhdx`). Deleting `.avhdx` files in Windows Explorer destroys every change written since the snapshot was taken. Always delete checkpoints inside Hyper-V Manager so changes merge cleanly.",
    ),
    "6.4": (
        "Slow or Unreachable VM Guest-vs-Host Isolation Pipeline",
        [("1. Guest State", "Running vs Paused-Critical", "HYPERVISOR"),
         ("2. Guest Metrics", "CPU / RAM / Disk Queue", "INSIDE VM"),
         ("3. vSwitch Binding", "Ext / Default / Private?", "VIRTUAL L2"),
         ("4. Host Contention", "Host RAM / SSD Space", "HOST OS"),
         ("5. Escalate Note", "Guest Facts vs Host Ask", "HANDOFF")],
        [("Paused-Critical State", "Hypervisor pauses VM when host disk hits 0 bytes", "Check host volume free space & .avhdx", "Rebooting guest OS when host SSD is 100% full of checkpoints"),
         ("Host RAM Overcommit", "Too many VMs fighting for physical host RAM", "Host swaps to disk -> all VMs crawl", "Adding more vCPUs to a VM when the host is starving for RAM"),
         ("vNIC Disconnected", "Virtual cable unchecked or bound to Private switch", "Check VM Settings > Network Adapter", "Reinstalling guest TCP/IP when vSwitch is set to 'Not connected'"),
         ("Missing Integration Svcs", "High CPU, laggy mouse, wrong clock after sleep", "Install Guest Additions / Integration", "Time drift breaks Kerberos domain authentication inside guest"),
         ("Guest-vs-Host Note", "Report measured guest metrics + suspected host limit", "Never reboot shared hypervisor host!", "Restarting a shared ESXi/Hyper-V server and crashing 20 other VMs")],
        "`Paused-Critical` Means the Host Storage Volume Is Full",
        "When a VM mysteriously enters `Paused-Critical` and refuses to resume, do not troubleshoot inside the guest OS—the physical host drive holding the `.vhdx`/`.avhdx` files has run out of free disk space.",
    ),
    "7.1": (
        "Seven-Step Troubleshooting Method & Cheapest-Test Ordering",
        [("1. Identify Problem", "Question User + Scope", "FACTS"),
         ("2. Probable Cause", "Top 3 Theories (Simple 1st)", "HYPOTHESIS"),
         ("3. Test Theory", "Cheapest / Lowest Risk", "PROVE / KILL"),
         ("4. Plan & Execute", "One Change + Backout", "ACTION"),
         ("5. Verify & Document", "User Outcome + Prevention", "CLOSURE")],
        [("Step 1: Identify", "Gather symptoms, question user, check recent changes", "Back up data before invasive work", "Jumping straight to registry edits before asking what changed"),
         ("Step 2: Theorize", "Question the obvious; list 2-3 likely causes", "Physical/simple causes before complex", "Theorizing 'corrupt kernel' before checking if monitor is plugged in"),
         ("Step 3: Test Theory", "Pick the fastest, non-destructive discriminating test", "If disproved -> form NEW theory", "Applying a fix after the test already disproved your theory"),
         ("Step 4-5: Plan & Act", "Plan action + rollback; change ONE thing at a time", "Escalate if out of scope/authority", "Changing 4 firewall rules and a driver simultaneously"),
         ("Step 6-7: Verify & Doc", "Confirm with user + document cause, fix, prevention", "Close ticket only after verification", "Closing ticket because 'my command succeeded' while user app still fails")],
        "When a Theory Is Disproved, Return to Step 2 (Establish a New Theory)",
        "On troubleshooting methodology questions, pay close attention to what just happened in the stem: if a technician tested a theory and the test failed, the next step is **establish a new theory of probable cause (or escalate)**—not 'implement the plan anyway.'",
    ),
    "7.2": (
        "Blast-Radius Scoping & Eight-Domain Fault Isolation Matrix",
        [("1. Scope Matrix", "1 User / 1 PC / 1 Site", "BLAST RADIUS"),
         ("2. Hardware / Boot", "Power -> POST -> WinRE", "DEVICE"),
         ("3. Identity / Profile", "User A vs User B Test", "ACCOUNT"),
         ("4. Network / DNS", "Lease -> GW -> Name", "PATH"),
         ("5. App / Permission", "ACL vs Service Health", "RESOURCE")],
        [("1 User on Any PC Fails", "User A fails on PC1 & PC2; User B works on PC1", "Account / AD / MFA / Entitlement", "Reimaging PC1 when the user's Active Directory account is locked"),
         ("Any User on 1 PC Fails", "User A & User B both fail on PC1; PC2 works", "Machine hardware / OS / local NIC", "Resetting user password when PC1's network cable is cut"),
         ("1 User, 1 PC Only", "User A fails on PC1; User B works on PC1", "Corrupt local user profile (`C:\\Users`)", "Reinstalling Windows when only one user's local profile cache is bad"),
         ("All Users, 1 Floor/VLAN", "Entire department loses network at once", "Closet switch / VLAN / DHCP scope", "Troubleshooting individual laptops during a closet power trip"),
         ("IP Works, Name Fails", "`ping 10.1.2.3` works; `\\\\filesrv` fails", "DNS / Name Resolution domain", "Replacing the switchport when the DNS A record is missing")],
        "The 'Swap User vs. Swap PC' 2x2 Matrix Immediately Isolates Account vs. Machine",
        "When a fault could be the account, the local profile, or the workstation: test the user on a second PC, or test a second user on the same PC. Follows the user everywhere = Account/Entitlement; stays on the PC for one user = Local Profile; hits everyone on that PC = Machine/OS.",
    ),
    "7.3": (
        "Customer Verification, Preventive Action & Escalation Handoff",
        [("1. Re-Run Failed Test", "Same CLI / Same Input", "TECH PROOF"),
         ("2. User Reproduction", "User Tests Real Workflow", "USER PROOF"),
         ("3. Regression Check", "Did Fix Break Neighbor?", "SAFETY"),
         ("4. Preventive Step", "Reservation / Label / KB", "PREVENTION"),
         ("5. Closure / Escalate", "Cause + Fix + Evidence", "RECORD")],
        [("Technical Verification", "Repeat the exact test that originally failed", "Before/after CLI output match", "Assuming `gpupdate` fixed a drive mapping without opening Explorer"),
         ("User Outcome Check", "Have the user perform their actual daily task", "User confirms print/sign-in works", "Closing a printer ticket after a test page when the ERP tray still jams"),
         ("Preventive Measure", "Remove the recurring trigger where authorized", "Convert printer dynamic IP to reservation", "Fixing an IP conflict today without reserving the IP for tomorrow"),
         ("Warm Escalation Note", "Symptom, scope, ruled-out domains, exact outputs", "Saves Tier 2 from repeating Step 1", "Escalating 'still broken' with zero command outputs attached"),
         ("Closure Formula", "Root cause + action taken + verification + prevention", "Searchable ticket history", "Writing 'Fixed issue' in resolution field")],
        "A Ticket Is Not Verified Until the User's Actual Workflow Succeeds",
        "`ping` replying or a service showing `Running` is technical evidence, not full system verification. Always verify the exact workflow the user reported and confirm no regression was introduced.",
    ),
    "7.4": (
        "Time-Boxed Capstone Troubleshooting Drills & Escalation Gate",
        [("1. Start Clock", "Read Intake & Scope", "T+0 MIN"),
         ("2. Cheap Proof #1", "Cut Fault Space in Half", "DISCRIMINATE"),
         ("3. Single Change", "Apply Fix or Revert", "CONTROL"),
         ("4. Time-Box Check", "Out of Theories / Auth?", "ESCALATE GATE"),
         ("5. Plain Status", "Outcome + Next Update", "COMMUNICATE")],
        [("Divide-and-Conquer", "Test the middle of the stack (e.g., ping IP)", "Splits L1-L3 from L4-L7 in 3 seconds", "Testing 12 browser extensions before checking if the PC has an IP"),
         ("Time-Box Discipline", "Set a strict 15-20 min cap per unproved theory", "Escalate when time-box expires", "Spending 3 hours guessing registry keys on a VIP workstation"),
         ("Revert Failed Tests", "Undo any test change that did not resolve the fault", "Leave system clean for Tier 2", "Leaving Windows Firewall disabled after proving it wasn't the cause"),
         ("Authority Boundary", "Stop at shared AD, firewall, or hypervisor changes", "Escalate with evidence packet", "Using a borrowed admin account to edit domain Group Policy"),
         ("User Status Cadence", "State what is known, impact, next step & ETA", "Plain language, no blame", "Going silent for 4 hours while researching a bug")],
        "Always Revert Unsuccessful Test Changes Before Escalating",
        "If you temporarily set a static IP or disabled an add-in to test a theory and the symptom persisted, **put the setting back** before moving on. Leaving failed test changes in place creates a multi-fault nightmare for the next technician.",
    ),
    "8.1": (
        "Windows 11 Servicing Paths & Pre-Install Gateways",
        [("1. Hardware Check", "TPM 2.0 + UEFI + 64GB", "COMPATIBILITY"),
         ("2. Pre-Flight Safety", "Backup + BitLocker Key", "DATA GATE"),
         ("3. Servicing Choice", "In-Place vs Clean Wipe", "STRATEGY"),
         ("4. Partition Layout", "GPT + EFI System Part", "STORAGE"),
         ("5. Post-Install", "Drivers + WU + Verify", "BASELINE")],
        [("Clean Install (USB)", "Wipes target partition(s); fresh OS + new SID", "Removes apps, settings & files", "Best for malware rebuild, disk replacement, or severe OS corruption"),
         ("In-Place Upgrade/Repair", "Runs `setup.exe` from mounted ISO inside Windows", "Keeps files, apps & settings", "Repairs broken OS components while preserving user environment"),
         ("Reset This PC", "Built-in recovery: 'Keep my files' vs 'Remove all'", "Reinstalls OS; removes desktop apps", "'Keep my files' still removes Win32 apps — document app list first!"),
         ("Win 11 Minimum Specs", "64-bit 1GHz 2+ cores, 4 GB RAM, 64 GB disk", "UEFI Secure Boot + TPM 2.0 + DX12", "Legacy MBR disk must convert via `mbr2gpt` before enabling UEFI"),
         ("BitLocker Pre-Check", "Suspend BitLocker or confirm 48-digit recovery key", "manage-bde -status / Entra escrow", "Repartitioning or updating BIOS without the BitLocker key locks data")],
        "`Reset This PC -> Keep My Files` Still Removes Installed Desktop Applications",
        "Users hear 'Keep my files' and assume their licensed accounting software, VPN clients, and Office plugins will remain. 'Keep my files' preserves `C:\\Users` personal documents but wipes installed Win32 applications—always inventory apps and license keys first.",
    ),
    "8.2": (
        "Windows Baseline, Least-Privilege Accounts & GPO Precedence (LSDOU)",
        [("1. Local Policy", "gpedit.msc (1st Applied)", "LOWEST"),
         ("2. Site Policy", "AD Site Links", "SITE"),
         ("3. Domain Policy", "Domain-Wide Baseline", "DOMAIN"),
         ("4. OU Policy", "Departmental OU (Wins!)", "HIGHEST"),
         ("5. Client Verify", "gpupdate -> gpresult /r", "EVIDENCE")],
        [("LSDOU Order", "Local -> Site -> Domain -> Organizational Unit", "Last applied (OU) wins conflicts", "Local policy edit gets overwritten on next domain `gpupdate`"),
         ("Daily vs Admin Account", "Standard user for email/web; separate Admin for UAC", "lusrmgr.msc / net localgroup", "Running daily browser as Local Admin lets malware own the OS silently"),
         ("gpupdate /force", "Reapplies all user & computer Group Policy now", "gpresult /r or /h report.html", "Checking GPO changes without running `gpupdate` or re-logging"),
         ("Domain Trust Lost", "'Trust relationship between workstation and domain failed'", "Test-ComputerSecureChannel -Repair", "Caused by reverting an old VM snapshot out of sync with AD machine password"),
         ("Baseline Snapshot", "OS build (`winver`), Defender status, BitLocker, accounts", "Compare broken PC against baseline", "Troubleshooting blind without knowing the shop's standard config")],
        "GPO Precedence Follows LSDOU — And Reverting a Domain VM Snapshot Breaks Machine Trust",
        "Group Policy evaluates in **Local -> Site -> Domain -> OU (LSDOU)** order, so the closest OU policy wins (unless Enforced/No Override is set). Also, reverting a domain-joined VM to a 60-day-old snapshot desynchronizes its machine account password with Active Directory.",
    ),
    "8.3": (
        "Windows Component Repair (DISM -> SFC) & WinRE Recovery Tree",
        [("1. Date the Fault", "Reliability Mon / EventVwr", "TIMELINE"),
         ("2. Fix Component Store", "DISM /RestoreHealth", "WIN-SXS"),
         ("3. Fix System Files", "sfc /scannow", "SYSTEM32"),
         ("4. WinRE Boot", "Safe Mode / Rollback", "OFFLINE"),
         ("5. Verify Services", "services.msc / sc query", "RUNTIME")],
        [("DISM /RestoreHealth", "Repairs the underlying WinSxS component store", "DISM /Online /Cleanup-Image /RestoreHealth", "Run DISM BEFORE `sfc /scannow` so SFC has known-good source files"),
         ("sfc /scannow", "Scans & replaces protected Windows system files", "Elevated admin cmd required", "Running SFC against a corrupted WinSxS store fails to repair files"),
         ("Reliability Monitor", "Day-by-day stability index & crash/install timeline", "perfmon /rel", "Quickest way to see 'App X started crashing the day Driver Y installed'"),
         ("WinRE Options", "Startup Repair, Uninstall Updates, System Restore, Safe Mode", "Shift+Restart or 2 failed boots", "System Restore rolls back system/registry/drivers without deleting user docs"),
         ("chkdsk /f /r", "Fixes file system metadata (/f) & bad sectors (/r)", "Locks volume -> schedules on reboot", "Never run `chkdsk /r` on a clicking drive before backing up user files")],
        "Always Run `DISM /RestoreHealth` Before (or When) `sfc /scannow` Reports Unrepairable Files",
        "`sfc /scannow` pulls replacement files from the local Windows Component Store (`WinSxS`). If that local cache is damaged, SFC fails—repair the component store first with `DISM /Online /Cleanup-Image /RestoreHealth`, then re-run `sfc /scannow`.",
    ),
    "8.4": (
        "Failed Windows Update Triage & Least-Disruptive Rollback",
        [("1. Read History", "KB Number + 0x Error", "IDENTIFY"),
         ("2. Check Disk & Time", "Free Space + NTP Sync", "PREREQS"),
         ("3. Reset WU Cache", "wuauserv + SoftwareDist", "REPAIR"),
         ("4. DISM + SFC", "Repair Component Store", "INTEGRITY"),
         ("5. Uninstall / Verify", "wusa /uninstall /kb:NNN", "VERIFY")],
        [("Update Error Capture", "Settings > Windows Update > Update history", "Record exact KB# & 0x8007xxxx code", "0x80070070 = insufficient disk space; check `C:` free GB first!"),
         ("Service & Cache Reset", "Stop `wuauserv` & `bits`, clear `SoftwareDistribution`", "net stop wuauserv -> rename folder", "Clears half-downloaded corrupt CAB packages without touching user data"),
         ("Component Store Fix", "Repair servicing stack before retrying cumulative KB", "DISM /RestoreHealth -> sfc /scannow", "Broken servicing metadata blocks every monthly cumulative update"),
         ("Rollback Bad Update", "WinRE > Uninstall Updates (Quality vs Feature)", "wusa /uninstall /kb:<ID>", "Recovers a machine that boot-loops immediately after Patch Tuesday"),
         ("Pattern Escalation", "If 5+ PCs fail on the same KB, pause & escalate", "Report KB#, OS build, hardware model", "Manually wiping 15 PCs when a vendor driver clashes with a new KB")],
        "Check Free Disk Space (`0x80070070`) and Date/Time Before Rebuilding the OS",
        "Many 'mysterious' Windows Update failures are caused by less than 15–20 GB of free space on `C:` (`0x80070070`), a clock skewed by hours (breaking TLS certificate checks), or a corrupt download in `C:\\Windows\\SoftwareDistribution`.",
    ),
    "9.1": (
        "Linux CLI Inventory, Octal/Symbolic Permissions & systemd",
        [("1. Identity & Host", "whoami, id, uname -a", "CONTEXT"),
         ("2. Network & Disk", "ip a, ip r, df -h, free -h", "RESOURCES"),
         ("3. Permission Bits", "-rwxr-x--- (u/g/o)", "OCTAL 750"),
         ("4. Ownership & Mode", "chmod / chown via sudo", "ACCESS"),
         ("5. Service & Logs", "systemctl & journalctl", "DAEMON")],
        [("Linux Inventory Map", "`ip a` (IPs), `ip r` (routes), `df -h` (disk), `free -h` (RAM)", "Replaces legacy `ifconfig`/`route`", "Running `df` without `-h` shows raw 1K blocks; `df -i` checks inode exhaustion"),
         ("Permission String", "Type (`-`/`d`/`l`) + User(rwx) + Group(rwx) + Other(rwx)", "r=4, w=2, x=1 (e.g., 750 = rwxr-x---)", "`chmod 640 file` -> `rw-r-----`; directories need `x` (1) to `cd` into them"),
         ("chown & chmod", "`chown user:group file` | `chmod u+x script.sh`", "Requires owner or `sudo`", "Using `chmod 777` to 'fix' a permission error exposes files to every local user"),
         ("systemd Service Mgmt", "`systemctl status|restart|enable|disable <svc>`", "`journalctl -u <svc> -n 50`", "`restart` starts it now; `enable` makes it start on boot"),
         ("Package & Process", "`apt`/`dnf` updates; `ps aux`, `top`, `kill <PID>`", "Use SIGTERM (15) before SIGKILL (-9)", "`kill -9` prevents database/service from flushing open files cleanly")],
        "Never Use `chmod 777` as a Quick Fix — And Directories Require Execute (`x`) to Traverse",
        "Setting `chmod 777` (`rwxrwxrwx`) is an instant security failure on exams and in production. Remember: read (`4`) + write (`2`) + execute (`1`), so standard private scripts use `750` or `700`, and config files use `640` or `600`.",
    ),
    "9.2": (
        "macOS Architecture, APFS / FileVault / Time Machine & MDM",
        [("1. About This Mac", "Apple Silicon vs Intel", "INVENTORY"),
         ("2. Activity & Disk", "Activity Mon + First Aid", "DIAGNOSE"),
         ("3. APFS & FileVault", "XTS-AES-128 + Recovery", "ENCRYPT"),
         ("4. Time Machine", "Local Snapshots + Ext", "BACKUP"),
         ("5. macOS Recovery", "Hold Power / Cmd+R", "RESTORE")],
        [("macOS File Layout", "`/Applications`, `/Users/<name>`, `/Library`, `~/Library`", "`Cmd+Shift+.` shows hidden dotfiles", "User app preferences live in `~/Library/Preferences` (.plist files)"),
         ("Diagnostic Triad", "Activity Monitor (CPU/RAM), Disk Utility (First Aid), Console", "`Cmd+Space` Spotlight launch", "Force Quit (`Cmd+Option+Esc`) closes a hung app without rebooting"),
         ("FileVault 2", "Full-disk encryption tied to user login + Recovery Key", "Escrow key in Jamf/MDM", "Without the user password or escrowed FileVault key, SSD data is unrecoverable"),
         ("macOS Recovery Entry", "Apple Silicon: Hold Power button | Intel: Hold `Cmd+R`", "Reinstall macOS, Disk Utility, Terminal", "Holding `Cmd+R` on M1/M2/M3/M4 Macs does not enter Recovery"),
         ("Gatekeeper & Keychain", "Gatekeeper verifies Apple notarization; Keychain stores secrets", "System Settings > Privacy & Security", "MDM Configuration Profiles (.mobileconfig) enforce Wi-Fi, VPN & FileVault")],
        "Apple Silicon Enters Recovery by Holding Power (Not `Cmd+R`)",
        "On Intel Macs you hold `Command+R` at chime, but on Apple Silicon (M-series) Macs you shut down and **press and hold the Power (Touch ID) button** until 'Loading startup options' appears.",
    ),
    "9.3": (
        "Cross-Platform Access: Fault vs. Entitlement & Identity Sources",
        [("1. User Report", "'Access Denied' vs Timeout", "SYMPTOM"),
         ("2. 2-Account Test", "Does Colleague Reach It?", "ISOLATE"),
         ("3. Identity Source", "Local / AD / Entra / IdP", "DIRECTORY"),
         ("4. Share vs NTFS/FS", "Most Restrictive Wins!", "EFFECTIVE ACL"),
         ("5. Owner Escalation", "Group Request + Evidence", "LEAST PRIV")],
        [("Fault vs Entitlement", "Timeout/Unreachable = Network Fault; 'Access Denied' = Auth/ACL", "Test same path from 2nd account/PC", "Troubleshooting DNS for an hour when the user simply isn't in the Finance group"),
         ("Share + File ACL Rule", "When accessing over SMB (`\\\\srv\\share`), BOTH apply", "Most restrictive permission wins!", "Share = Read, NTFS = Full Control -> Effective network access is Read-Only"),
         ("Explicit Deny Rule", "Explicit Deny overrides any Allow from group memberships", "Remove from Deny group; use groups", "Adding user to 'Allow' group while they remain in 'Contractors-Deny'"),
         ("Identity Authorities", "Local SAM/passwd vs Active Directory (Kerberos/LDAP) vs Cloud IdP", "whoami /groups or `id`", "Creating a local account on a workstation does not grant domain share access"),
         ("Remote Access Protocols", "RDP (TCP 3389), SSH (TCP 22), SMB (TCP 445), HTTPS VPN (443)", "Never expose RDP/SMB directly to WAN", "Exposing TCP 3389 or 445 on a public IP invites immediate ransomware brute-force")],
        "Combining SMB Share Permissions and NTFS/Filesystem Permissions: Most Restrictive Wins",
        "When a user connects over the network (`\\\\server\\share`), calculate their cumulative Share permission and their cumulative NTFS permission separately—then take the **more restrictive** of the two. (When logged in locally at the console, only NTFS applies.)",
    ),
    "9.4": (
        "Mixed-OS Environment File Systems, SMB Paths & Pitfalls",
        [("1. Pick File System", "NTFS / APFS / ext4 / exFAT", "MEDIA"),
         ("2. Network Share", "SMB (TCP 445) UNC/URI", "TRANSPORT"),
         ("3. Remote Shell", "OpenSSH (TCP 22)", "ADMIN CLI"),
         ("4. Case & Endings", "CRLF vs LF / Case-Sens.", "PITFALLS"),
         ("5. Verify Read/Write", "Test Create + Modify", "CLOSURE")],
        [("exFAT (Cross-OS USB)", "Native Read/Write on Windows, macOS, and modern Linux", "Supports files > 4 GB (unlike FAT32)", "Best choice for a shuttle USB drive moving a 12 GB VM image between Mac & PC"),
         ("FAT32 Limit Trap", "Universal compatibility, but max single file size = 4 GB - 1B", "Max volume size 32 GB in Win GUI", "Copying a 5.2 GB `.iso` to a FAT32 thumb drive fails with 'File too large' despite 20 GB free"),
         ("NTFS / APFS / ext4", "NTFS (Windows native), APFS (macOS native), ext4 (Linux)", "macOS reads NTFS natively (no write)", "Mac user can open files on an NTFS USB drive but cannot save edits"),
         ("SMB Syntax by OS", "Windows: `\\\\server\\share` | macOS/Linux: `smb://server/share`", "TCP Port 445 (CIFS/SMB3)", "Typing backslashes `\\\\server\\share` into macOS Finder `Cmd+K` fails"),
         ("Cross-OS Pitfalls", "Linux `ext4` is case-sensitive (`Report.txt` != `report.txt`); CRLF vs LF", "`dos2unix` fixes `^M` bash errors", "Bash script edited in Windows Notepad fails on Linux with `/bin/bash^M: bad interpreter`")],
        "4 GB File Failing on a 64 GB USB Drive = FAT32 Single-File Limit (Use exFAT)",
        "Whenever a ticket says 'User has 50 GB free on their USB drive, but copying a 4.5 GB video or ISO fails with disk full / file too large,' the drive is formatted as **FAT32** (4 GB max file size). Back up the drive and reformat as **exFAT**.",
    ),
})

BLUEPRINTS_ITSUP.update({
    "10.1": (
        "Defense-in-Depth: Physical Controls, MFA Factors & Least Privilege",
        [("1. Physical Layer", "Mantrap / Badge / Lock", "PERIMETER"),
         ("2. Factor #1", "Something You Know", "PASSWORD"),
         ("3. Factor #2 (MFA)", "FIDO2 Key / Authenticator", "POSSESSION"),
         ("4. Factor #3", "Biometric (Touch/Face)", "INHERENCE"),
         ("5. Least Privilege", "Standard User + JIT UAC", "AUTHORIZATION")],
        [("Auth Factors (3 Types)", "Know (PIN/pass), Have (FIDO2 key/token), Are (biometric)", "True MFA requires 2 DIFFERENT types", "Password + Security Question = two 'Something You Know' (Single Factor!)"),
         ("MFA Phishing Resistance", "FIDO2 / WebAuthn Passkeys > App TOTP/Number Match > SMS", "FIDO2 binds cryptographically to domain", "SMS OTP is vulnerable to SIM-swapping and real-time reverse-proxy phishing"),
         ("Least Privilege", "Standard user account for daily work; separate Admin for elevation", "Run as administrator / sudo", "Logging in daily as Domain Admin turns one phishing click into total compromise"),
         ("Physical Deterrents", "Access control vestibule (mantrap), badge reader, privacy screen, cable lock", "Win+L screen lock on walk-away", "Mantrap (two interlocking doors) physically prevents tailgating/piggybacking"),
         ("AAA Framework", "Authentication (Who), Authorization (What allowed), Accounting (Audit log)", "Event ID 4624 (Logon) / 4625 (Failed)", "Shared generic admin accounts destroy Accounting non-repudiation")],
        "Two Passwords or a Password + PIN Is Two-Step, NOT Multi-Factor Authentication",
        "Multi-factor authentication requires at least two **different** categories of factors (Know, Have, Are, Somewhere). Asking for a password plus a mother's maiden name or PIN uses two 'Something You Know' factors.",
    ),
    "10.2": (
        "Malware Incident Response: Quarantine, Preserve & Remediate",
        [("1. Identify IoCs", "AV Alert / Strange Proc", "DETECT"),
         ("2. Quarantine Host", "Unplug Ethernet / Wi-Fi Off", "CONTAIN #1"),
         ("3. Preserve State", "Do NOT Power Off RAM!", "EVIDENCE"),
         ("4. Escalate / Scan", "Defender Offline / SOC", "ERADICATE"),
         ("5. Recover & Verify", "Clean Image + Rotate Creds", "RESTORE")],
        [("Step 1: Quarantine", "Disconnect network cable & disable Wi-Fi/Bluetooth immediately", "Stops lateral movement & C2 encryption", "Leaving an infected PC on the LAN while running a 2-hour scan spreads ransomware"),
         ("Preserve Volatile State", "Do NOT hard-power-off if security/forensics needs RAM/state", "Escalation to Security / SOC first", "Rebooting destroys volatile memory keys and triggers boot-sector lockers"),
         ("Defender Offline Scan", "Boots into trusted mini-OS before Windows kernel loads", "`Start-MpWDOScan` / Security UI", "Removes rootkits and locked kernel drivers that hide from live OS scans"),
         ("Ransomware Response", "Isolate host immediately -> notify Security -> restore from offline backup", "Never pay or delete shadow copies", "Signing into a ransom-locked PC with Domain Admin credentials exposes the domain hash"),
         ("Post-Remediation", "Verify protection re-enabled, update signatures, rotate user credentials", "Check Task Scheduler & Run keys", "Removing the dropper payload while leaving the attacker's scheduled persistence task")],
        "First Action on Suspected Malware/Ransomware: Isolate from Network (Unplug/Disable Wi-Fi)",
        "Before running scans, checking logs, or rebooting, **disconnect the machine from the network** (unplug Ethernet and turn off Wi-Fi) so ransomware cannot encrypt mapped SMB network shares or spread laterally.",
    ),
    "10.3": (
        "Data-at-Rest Encryption, Patch Hygiene & Media Sanitization (NIST 800-88)",
        [("1. Encrypt at Rest", "BitLocker + TPM 2.0", "PROTECT"),
         ("2. Escrow Key", "AD / Entra / Safe Vault", "RECOVERY"),
         ("3. Patch & USB", "Auto-Update + Block AutoRun", "HARDEN"),
         ("4. Sanitize Media", "Clear / Purge / Destroy", "NIST 800-88"),
         ("5. CoD Audit", "Serial # + Method Logged", "COMPLIANCE")],
        [("BitLocker + TPM 2.0", "Full volume encryption (`manage-bde -status`); binds to PCRs", "Escrow 48-digit key to AD / Entra ID", "Storing the BitLocker recovery `.txt` file on the encrypted `C:` drive itself"),
         ("NIST 800-88 Clear", "Single/multi-pass zero overwrite via standard read/write commands", "`format /p:1` or `dd if=/dev/zero`", "Resists keyboard recovery; suitable for internal reuse of functional HDDs"),
         ("NIST 800-88 Purge", "Cryptographic Erase (CE), NVMe Sanitize, ATA Secure Erase, Degauss", "Renders data unrecoverable in a lab", "NOTE: Degaussing works on magnetic HDDs/tape ONLY — does NOT erase NAND SSDs!"),
         ("NIST 800-88 Destroy", "Shredding, disintegrating, incinerating, pulverizing (<2mm for SSD)", "Certificate of Destruction required", "Required for failed drives holding regulated data or drives leaving high-security sites"),
         ("Removable Media Hygiene", "Disable AutoRun/AutoPlay; scan external USBs; block unknown HID", "Group Policy / Endpoint DLP", "Plugging in a 'found' parking-lot USB drive executes Rubber Ducky keystroke payloads")],
        "Degaussing Destroys Magnetic HDDs but Does NOTHING to Flash/SSD Media",
        "A degaosser uses a powerful magnetic field to scramble magnetic domains on spinning HDD platters and backup tapes. Because SSDs and USB flash drives store charges in silicon NAND gates (not magnetic media), degaussing leaves SSD data 100% intact—use **Cryptographic Erase / NVMe Sanitize** or **Physical Shredding**.",
    ),
    "10.4": (
        "Phishing Triage, Credential Compromise & Order of Volatility",
        [("1. Intake Report", "Forward Full Headers", "ANALYZE"),
         ("2. Scope Exposure", "Viewed vs Clicked vs Typed?", "BLAST RADIUS"),
         ("3. Revoke & Reset", "Kill Sessions + Reset MFA", "CONTAIN"),
         ("4. Audit Persistence", "Check Inbox Rules / OAuth", "ERADICATE"),
         ("5. Volatility Order", "CPU/RAM -> Net -> Disk", "FORENSICS")],
        [("Header Inspection", "Check `Return-Path`, `Received`, SPF (`pass`/`fail`), DKIM, DMARC", "View message source / headers", "Display name says 'IT Helpdesk' while envelope sender is `support@evil-domain.ru`"),
         ("Credentials Entered!", "Reset password from clean PC + **Revoke active session tokens**", "Revoke sessions in Entra/IdP!", "Resetting password alone leaves stolen session cookies/tokens valid for hours"),
         ("Mailbox Persistence", "Attackers create hidden Inbox forwarding/delete rules for 'invoice/wire'", "Audit Inbox Rules & Delegate access", "User still misses security alerts after password reset because an RSS/Inbox rule deletes them"),
         ("Order of Volatility", "1. CPU Reg/Cache -> 2. RAM -> 3. Network/ARP -> 4. Disk -> 5. Backups/Print", "RFC 3227 capture most volatile first", "Capturing disk image first while live RAM and active TCP sockets evaporate"),
         ("Chain of Custody", "Who handled evidence, when, where stored, SHA-256 hash, purpose", "Signed transfer log + tamper bag", "Unlogged evidence sitting on an unlocked tech bench is inadmissible")],
        "Password Reset Alone Does Not Kill Stolen Session Tokens or Malicious Inbox Rules",
        "When a user enters credentials AND approves an MFA prompt on a phishing site, the attacker steals a valid session token and immediately creates a hidden mailbox rule (e.g., auto-forward and delete emails containing 'password' or 'invoice'). Always **revoke active sessions**, **audit MFA devices**, and **check Inbox rules**.",
    ),
    "11.1": (
        "Software Symptom Classification, Scope & Event Log Correlation",
        [("1. Exact Symptom", "Crash / Hang / Error Code", "CLASSIFY"),
         ("2. Scope Boundary", "1 App / 1 Profile / Fleet", "ISOLATE"),
         ("3. Reliability Mon", "perfmon /rel Timeline", "CORRELATE"),
         ("4. Event Viewer", "ID 1000 Crash / 1002 Hang", "EVIDENCE"),
         ("5. Targeted Action", "Profile / App / Dependency", "RESOLVE")],
        [("App Crash (ID 1000)", "Process terminates abruptly; logs Faulting Module (`.dll`/`.exe`)", "Windows Logs > Application (ID 1000)", "Identifies whether the app itself or a third-party GPU/print DLL caused the crash"),
         ("App Hang (ID 1002)", "Window turns milky white ('Not Responding'); UI thread blocked", "Windows Logs > Application (ID 1002)", "Often caused by waiting on an unreachable network share or dead printer port"),
         ("Scope: 1 User Profile", "App works for User B on the same PC; fails only for User A", "`%LOCALAPPDATA%` / `%APPDATA%` cache", "Reinstalling the whole application in `Program Files` leaves corrupt `%APPDATA%` intact"),
         ("Scope: Fleet-Wide", "Same app fails for 50 users right after a morning update/cert expiry", "Check vendor status, KB, TLS cert", "Troubleshooting one user's mouse driver when an internal web cert expired"),
         ("Reliability Monitor", "Correlates application failures with Windows/driver installs by date", "`perfmon /rel`", "Shows exact day stability dropped from 10 to 2 after an agent update")],
        "Reinstalling in `Program Files` Never Fixes a Corrupt `%APPDATA%` User Profile Cache",
        "If an application crashes for User A on PC-01, test User B on PC-01. If User B works fine, the binaries in `C:\\Program Files` are healthy—the fault is inside User A's `%APPDATA%`, `%LOCALAPPDATA%`, or `HKCU` registry hive.",
    ),
    "11.2": (
        "Software Variable Elimination: Clean Boot, Safe Mode & App Repair",
        [("1. Baseline Control", "Known-Good User / File", "CONTROL"),
         ("2. App-Level Reset", "Settings > Apps > Repair", "NON-DESTRUCT"),
         ("3. Clean Boot", "msconfig (Hide MS Svcs)", "BINARY SEARCH"),
         ("4. Safe Mode Boot", "Minimal Drivers & Svcs", "KERNEL ISOLATE"),
         ("5. Restore Normal", "Re-Enable & Verify", "CLEANUP")],
        [("Clean Boot (`msconfig`)", "Check **'Hide all Microsoft services'** FIRST, then Disable all", "`msconfig` + Task Mgr Startup tab", "Forgetting 'Hide all Microsoft services' disables auth/boot services and locks you out!"),
         ("Binary Search (Halves)", "Re-enable top 50% of disabled third-party services, test, repeat", "Finds 1 bad service in 32 in 5 reboots", "Re-enabling all 30 services at once brings the bug back without naming the culprit"),
         ("Safe Mode (`bcdedit`)", "Loads only essential Microsoft drivers & services (no 3rd-party startup)", "WinRE > Startup Settings (4 or 5)", "If crash stops in Safe Mode, a third-party driver or background service is guilty"),
         ("App Repair vs Reset", "**Repair** fixes app binaries & keeps data; **Reset** wipes app cache/prefs", "Settings > Apps > Installed apps", "Clicking 'Reset' on a local-only notes app wipes unsynced local settings"),
         ("Return to Normal Startup", "Verify `msconfig` is back on Normal/Selective startup before closing", "Confirm `bcdedit` `safeboot` cleared", "Handing PC back in Diagnostic Startup with antivirus and print spooler disabled")],
        "In `msconfig` Services Tab, ALWAYS Check 'Hide All Microsoft Services' Before Clicking Disable All",
        "Disabling Microsoft services in `msconfig` stops Windows Logon, RPC, and Cryptographic Services—leaving the PC unbootable or unable to validate PIN/password sign-ins.",
    ),
    "11.3": (
        "Time-Boxed Repair vs. Rebuild Decision Matrix",
        [("1. Assess Fault", "Single App vs Deep OS/Malware", "DIAGNOSE"),
         ("2. Set Time-Box", "e.g. 45-Min Repair Cap", "DISCIPLINE"),
         ("3. Pre-Rebuild Gate", "Data Backup + BitLocker + Keys", "PROTECT"),
         ("4. Execute Path", "In-Place Repair vs Clean Image", "BUILD"),
         ("5. Restore & Verify", "Apps + User Data + Sign-Off", "CLOSURE")],
        [("Targeted App Repair", "Single app corrupt; OS & other apps healthy", "10-20 min (`winget` / M365 Quick Repair)", "Wiping the entire OS for a single broken Outlook OST cache file"),
         ("In-Place OS Repair", "OS system files/servicing broken; user apps/data intact", "45-60 min (`setup.exe` / Fix via WU)", "Preserves complex custom engineering software while replacing Windows core"),
         ("Clean Rebuild / Image", "Confirmed rootkit/ransomware, multi-subsystem rot, or time-box expired", "Standard gold image / Autopilot", "Spending 6 hours chasing cascading registry errors when a clean image takes 40 min"),
         ("Pre-Rebuild Checklist", "Backup `C:\\Users` + export browser bookmarks + app/license list + BitLocker", "Verify backup opens BEFORE wiping!", "Formatting `C:` before realizing the user saved tax files in `C:\\Temp\\Tax2026`"),
         ("Rebuild Change Record", "Record old/new hostname, serial, MAC, OS build, and user sign-off", "Update CMDB / asset inventory", "Imaging a PC with a duplicate hostname breaks domain trust for another user")],
        "Always Check Non-Standard Folders (`C:\\Temp`, Root of `C:\\`, Local App Databases) Before Rebuilding",
        "Users frequently store critical files outside `Documents` and `Desktop`—such as `C:\\Temp`, `C:\\Scans`, or local QuickBooks/SQLite folders. Always inspect the root of `C:\\` and verify backups are readable before starting a clean image.",
    ),
    "11.4": (
        "Slow Logon & Temporary Profile Bottleneck Isolation",
        [("1. Time the Phases", "Pre-Desktop vs Post-Desktop", "MEASURE"),
         ("2. Check Profile", "`whoami` & `C:\\Users\\TEMP`", "PROFILE GATE"),
         ("3. Policy & Scripts", "GPO / Dead `\\\\srv` Map", "NETWORK WAIT"),
         ("4. Startup Impact", "Task Mgr > Startup Apps", "AUTOLAUNCH"),
         ("5. Resource Bottleneck", "CPU / RAM / 100% Disk", "HARDWARE")],
        [("Dead Mapped Drive / GPO", "`Please wait for User Profile / Group Policy` hangs 90+ seconds", "`gpresult /r` & `net use`", "Logon script trying to map `\\\\decommissioned-nas\\share` waits for SMB timeout"),
         ("Startup App Bloat", "Desktop appears fast, then freezes for 3 minutes as tray icons load", "Task Manager > Startup apps (High impact)", "14 updaters, cloud sync clients, and chat apps launching simultaneously at login"),
         ("100% Active Disk Queue", "Disk active time pinned at 100% with >50 ms response time", "Resource Monitor (`resmon`) > Disk tab", "Failing HDD, concurrent AV scan + Windows Update, or severe RAM paging (`pagefile.sys`)"),
         ("Temporary Profile Trap", "Desktop looks empty; files 'missing'; `C:\\Users\\TEMP` in `set userprofile`", "Event ID 1511 / `ProfileList` `.bak` key", "DO NOT save new work in a `TEMP` profile—Windows deletes `C:\\Users\\TEMP` on sign-out!"),
         ("Profile Fix Procedure", "Never delete `C:\\Users\\<name>`! Fix lock/AV/disk space & `.bak` registry key", "`HKLM\\...\\ProfileList`", "Copying files into `C:\\Users\\TEMP` and rebooting erases the copied files")],
        "Never Save Files in a `C:\\Users\\TEMP` Profile — They Vanish at Logoff!",
        "When Windows cannot lock a user's `NTUSER.DAT` (often due to stuck antivirus locks or zero disk space), it logs the user into `C:\\Users\\TEMP`. The user's real files are still safe in `C:\\Users\\<username>`, but **anything saved while in `TEMP` is deleted on sign-out**.",
    ),
    "12.1": (
        "ITIL Change Control Lifecycle: Standard, Normal & Emergency",
        [("1. Classify Change", "Standard / Normal / Emerg", "CATEGORY"),
         ("2. Build RFC Plan", "Scope, Risk, Test, Backout", "PROPOSAL"),
         ("3. CAB Approval", "Peer & Stakeholder Sign-Off", "AUTHORIZE"),
         ("4. Maintenance Win", "Checklist Execution", "IMPLEMENT"),
         ("5. Verify & PIR", "Rollback Gate + Review", "CLOSE")],
        [("Standard Change", "Pre-approved, low-risk, repeatable procedure with documented checklist", "e.g., New hire account or toner swap", "Does not require a full CAB meeting every time because risk & steps are pre-authorized"),
         ("Normal Change", "Non-trivial modification requiring full RFC, risk assessment & CAB approval", "e.g., Core switch VLAN or GPO edit", "Scheduled in an announced maintenance window with a tested backout plan"),
         ("Emergency Change", "Urgent fix to restore a critical outage or patch an actively exploited 0-day", "Expedited ECAB approval + retroactive doc", "'Emergency' is NOT an excuse to skip documentation or omit a backout plan"),
         ("Backout / Rollback Plan", "Exact, timed steps to restore prior working state if verification fails", "Snapshot revert / config restore", "If the change isn't working by T-15 min of maintenance window end, execute rollback"),
         ("Post-Implementation (PIR)", "Did it meet objectives? Any unexpected side effects? Update runbooks", "Blameless review after completion", "Skipping PIR means the next engineer hits the exact same undocumented gotcha")],
        "Every Change Request Requires a Tested Backout Plan BEFORE Touching Production",
        "On exam questions asking what is missing from a technician's change proposal (or what to do first before applying a production firewall/switch update), look for the **backout / rollback plan** and **config backup**.",
    ),
    "12.2": (
        "Regulated Data (PII/PHI/PCI), Acceptable Use & AI Data Governance",
        [("1. Classify Data", "PII / PHI / FERPA / PCI", "SENSITIVITY"),
         ("2. Minimum Access", "Need-to-Know Only", "PRIVACY"),
         ("3. Policy Check", "AUP / Licensing / BYOD", "GOVERNANCE"),
         ("4. AI Redaction Gate", "Never Paste Secrets/PII", "GEN-AI RULE"),
         ("5. Escalate Incident", "Stop & Report Exposure", "COMPLIANCE")],
        [("Regulated Data Types", "PII (SSN/names), PHI/HIPAA (health), PCI-DSS (cardholder), FERPA (student)", "Encrypt in transit & at rest", "Attaching an unredacted CSV of customer credit cards to a general support ticket"),
         ("Public vs Enterprise AI", "Public GenAI tools may retain/train on prompts; never paste PII, keys, or code", "Sanitize hostnames/tokens/PII first", "Pasting a production `.env` file or customer medical ticket into a public chatbot"),
         ("Acceptable Use (AUP)", "Defines permitted use of company hardware/network & monitoring notice", "Signed at onboarding", "Installing unlicensed 'cracked' CAD software or crypto-miners on shop PCs"),
         ("Prohibited Content Stop", "If you encounter illegal content or HR/legal investigation material", "STOP immediately; preserve; notify lead", "Browsing folders, taking personal phone photos, or confronting the user directly"),
         ("Licensing Compliance", "Per-seat, per-device, concurrent, open-source (GPL/MIT) vs commercial", "Track in SAM / asset database", "Reusing a single-seat retail license key across 25 classroom workstations")],
        "Never Paste Customer PII, Live Credentials, or Private Source Code into Public AI Tools",
        "When using AI assistants to draft scripts or summarize logs, strip all PII, internal IP schemas, API tokens, and customer names unless using an approved, contractually isolated enterprise AI instance.",
    ),
    "12.3": (
        "Disaster Recovery Metrics (RPO vs. RTO) & Backup Restore Chains",
        [("1. RPO Target", "Max Data Age Lost (Past)", "FREQUENCY"),
         ("2.Backup Schedule", "Full / Diff / Incremental", "CAPTURE"),
         ("3. 3-2-1-1-0 Rule", "Immutable Offsite Copy", "SURVIVABILITY"),
         ("4. RTO Target", "Max Downtime Allowed (Future)", "SPEED"),
         ("5. Restore Drill", "Test Recovery & Measure", "VERIFIED")],
        [("RPO (Recovery Point)", "**How much data (time)** you can afford to lose looking backward", "Drives backup frequency (e.g. 15m vs 24h)", "RPO = 1 hour means backups/replication must capture changes at least every 60 minutes"),
         ("RTO (Recovery Time)", "**How long** the service can stay down after a disaster before business fails", "Drives restore speed (warm standby vs tape)", "RTO = 2 hours cannot be met if shipping physical tapes from a vault takes 24 hours"),
         ("Full + Incremental", "Incremental backs up only changes since **any** last backup (Full or Inc)", "Fastest backup; slowest restore chain", "Sun Full + Mon..Thu Inc -> Friday restore needs Sun Full + Mon + Tue + Wed + Thu"),
         ("Full + Differential", "Differential backs up all changes since the last **Full** backup", "Moderate backup; 2-set restore!", "Sun Full + Mon..Thu Diff -> Friday restore needs ONLY **Sun Full + Thu Diff**"),
         ("Untested Backup Trap", "Backup job 'Completed Successfully' does not prove files are restorable", "Schedule regular test restores", "Discovering during a ransomware outage that the backup service was backing up an empty folder")],
        "Restore Chain Math: Incremental Needs Full + Every Incremental; Differential Needs Full + Latest Differential Only",
        "Exam items love asking how many backup sets are required on Friday if Sunday is Full: **Incremental** requires Sunday Full + Mon + Tue + Wed + Thu (5 sets). **Differential** requires only Sunday Full + Thursday Differential (2 sets).",
    ),
    "12.4": (
        "Integrated Operations Capstone: KB Authoring, CMDB & End-to-End Closure",
        [("1. Triage & Scope", "Safety + Privacy + Impact", "INTAKE"),
         ("2. Change & Backup", "Verify Backup + Rollback", "CONTROL"),
         ("3. Execute & Verify", "1 Change + User Sign-Off", "RESOLVE"),
         ("4. Update CMDB", "Serial, Owner, Status, Loc", "ASSET DB"),
         ("5. Publish KB", "Symptom, Cause, Fix, Tags", "KNOWLEDGE")],
        [("KB Article Structure", "Exact symptom/error code, environment scope, root cause, step-by-step fix, verification", "Searchable tags for Tier 1", "Writing a KB article with no error code or verification step"),
         ("CMDB / Asset Update", "Update asset tag, serial number, MAC, assigned user, room/location, lifecycle state", "Update on every swap/move/retire", "Swapping a dead PC with spares stock without updating the asset database"),
         ("Chain of Custody / Wipe", "Link decommissioned drive serial # to NIST 800-88 Purge/Destroy record", "Audit trail for compliance", "Throwing a replaced SSD into a desk drawer with no sanitization log"),
         ("Integrated Ticket Flow", "Combines technical isolation + change control + privacy + documentation", "Complete peer-auditable record", "Fixing the technical fault quickly but violating change control and leaving no note"),
         ("Blameless Handoff", "Focus on system state, timeline, and preventive action—never personal blame", "Continuous shop improvement", "Hiding a mistake instead of documenting the exact state for recovery")],
        "A Hardware Swap Is Incomplete Until the Asset Inventory (CMDB) and Sanitization Log Are Updated",
        "Replacing a motherboard or workstation changes serial numbers, MAC addresses, and TPM keys. Always update the asset record, escrow the new BitLocker key, and log the old storage drive's sanitization status.",
    ),
    "13.1": (
        "Lab VM Sandbox Safety: Checkpoint Before Touch & Destructive Command Guard",
        [("1. Verify Guest", "Confirm VM Window / Hostname", "TARGET CHECK"),
         ("2. Take Checkpoint", "Pre-Lab Clean Snapshot", "SAFETY NET"),
         ("3. Baseline Audit", "winver, ipconfig /all", "EVIDENCE"),
         ("4. Safe Lab Action", "Read-Only / Scoped CLI", "EXECUTION"),
         ("5. Revert / Verify", "Restore Clean Lab State", "RESET")],
        [("Pre-Lab Checkpoint", "Create a Hyper-V / VM snapshot BEFORE running any system or network change", "`Checkpoint-VM` / VM Manager", "Making registry or partition changes without a snapshot forces a full VM rebuild"),
         ("Target Verification", "Run `hostname` and `whoami` before executing administrative commands", "Confirm lab guest vs physical host", "Running a network adapter disable command in the host's PowerShell instead of the VM"),
         ("Safe Inventory CLI", "`hostname`, `whoami`, `ipconfig /all`, `systeminfo`, `Get-Disk`", "100% non-destructive read-only", "Always capture baseline outputs into your lab worksheet before changing state"),
         ("Destructive Commands", "`diskpart clean`, `format`, `rm -rf /`, `del /s /q C:\\*`, `bcdedit /delete`", "NEVER run on unverified disks!", "`diskpart clean` wipes partition tables instantly with zero confirmation prompt"),
         ("Post-Lab Clean Reset", "Revert to pre-lab checkpoint or undo test changes as instructed", "Leaves lab ready for next module", "Leaving static bad DNS settings from Lab 3 so Lab 4 fails mysteriously")],
        "`diskpart clean` Has Zero Confirmation Prompt — Always Verify Context & Checkpoint First",
        "In a virtual lab, always confirm your command prompt is inside the **Guest VM** (check `hostname`) and that a fresh checkpoint exists before modifying network adapters, services, or disks.",
    ),
    "13.2": (
        "Windows CLI & PowerShell CIM Evidence Collection Pipeline",
        [("1. Identity Context", "hostname & whoami /all", "WHO & WHERE"),
         ("2. IP Configuration", "ipconfig /all vs NetTCPIP", "NETWORK"),
         ("3. CIM Hardware", "Get-CimInstance Win32_*", "REPLACES WMIC"),
         ("4. Lease Diagnosis", "DHCP Enabled + Server IP", "VALID VS APIPA"),
         ("5. Script Safety", ".ps1 ExecutionPolicy Gate", "AUTOMATION")],
        [("ipconfig /all vs bare", "`ipconfig /all` reveals MAC, DHCP Enabled, DHCP Server, Lease Times, DNS", "Bare `ipconfig` hides DNS & DHCP!", "Running bare `ipconfig` misses a rogue DHCP server or wrong DNS server IP"),
         ("WMIC -> PowerShell CIM", "`wmic` is removed in modern Win 11; use `Get-CimInstance` (`gcim`)", "`Get-CimInstance Win32_OperatingSystem`", "Legacy scripts calling `wmic bios get serialnumber` fail on current Windows 11 builds"),
         ("PowerShell NetTCPIP", "`Get-NetIPConfiguration`, `Get-NetAdapter`, `Resolve-DnsName`, `Test-NetConnection`", "Structured object output", "Can be piped to `Select-Object` or `Export-Csv` for clean ticket evidence"),
         ("Healthy vs APIPA Lease", "Healthy: `DHCP Enabled: Yes`, valid gateway & lease time | APIPA: `169.254.x.x`", "Check `DHCP Server` line", "Static IP (`DHCP Enabled: No`) typed on wrong subnet looks fine until gateway ping fails"),
         ("Script File Extensions", "`.ps1` (PowerShell), `.bat`/`.cmd` (CMD), `.sh` (Bash), `.py` (Python)", "`Get-ExecutionPolicy` guards `.ps1`", "Never run an untrusted `.ps1` with `-ExecutionPolicy Bypass` from an email attachment")],
        "Bare `ipconfig` Hides DNS Servers, MAC Addresses, and DHCP Server Identity — Use `ipconfig /all`",
        "In both live labs and exam scenarios, bare `ipconfig` only shows IPv4, Subnet Mask, and Default Gateway. You must run **`ipconfig /all`** (or `Get-NetIPConfiguration -Detailed`) to see whether DHCP is enabled, which DHCP server issued the lease, and which DNS servers are configured.",
    ),
    "13.3": (
        "Escalating Ladder of Windows Network Resets (Least to Most Disruptive)",
        [("1. Lease Refresh", "ipconfig /release & /renew", "STEP 1 (MILD)"),
         ("2. DNS Cache Flush", "ipconfig /flushdns", "STEP 2 (MILD)"),
         ("3. Adapter Bounce", "Restart-NetAdapter", "STEP 3 (LINK)"),
         ("4. Stack Reset", "netsh winsock / int ip reset", "STEP 4 (REBOOT)"),
         ("5. Full Net Reset", "Settings > Network Reset", "STEP 5 (LAST)")],
        [("1. DHCP Release/Renew", "`ipconfig /release` drops lease; `ipconfig /renew` runs DORA for fresh IP", "Brief 2-sec blip; keeps VPN/Wi-Fi", "Note: On a remote RDP/SSH session, `ipconfig /release` disconnects you immediately!"),
         ("2. Flush DNS Resolver", "`ipconfig /flushdns` clears stale positive/negative local DNS cache entries", "`Clear-DnsClientCache` (zero drop)", "Safe to run anytime after a DNS record update without dropping active connections"),
         ("3. Bounce NIC Adapter", "`Restart-NetAdapter -Name 'Ethernet'` (or `ncpa.cpl` Disable/Enable)", "Re-negotiates L1/L2 link & DHCP", "Fixes wedged USB Ethernet dongles or stuck 802.1X state without rebooting OS"),
         ("4. Winsock & IP Reset", "`netsh winsock reset` & `netsh int ip reset`", "Requires OS reboot to take effect", "Repairs corrupted layered service providers (LSP) after VPN/malware removal"),
         ("5. Windows Network Reset", "Settings > Network & internet > Advanced network settings > Network reset", "Wipes all NICs, Wi-Fi profiles, VPNs", "Nuclear option: removes saved Wi-Fi passwords, static IPs, and virtual switches")],
        "Never Start with 'Windows Network Reset' When `ipconfig /renew` or `/flushdns` Will Do",
        "Full Windows Network Reset deletes every saved Wi-Fi profile, VPN client binding, and Hyper-V virtual switch, forcing a 5-minute reboot and manual reconfiguration. Always climb the reset ladder from least disruptive (`ipconfig /flushdns` / `/renew`) to most disruptive.",
    ),
    "13.4": (
        "Broken Name Resolution Triage: IP Reachability vs. Hosts File vs. DNS",
        [("1. Test Raw IP", "ping 10.20.30.5 / 1.1.1.1", "IP PATH OK?"),
         ("2. Test Name", "ping portal.internal.lan", "NAME FAILS"),
         ("3. Inspect Local", "drivers\\etc\\hosts + cache", "LOCAL OVERRIDE"),
         ("4. Query DNS Server", "nslookup / Resolve-DnsName", "SERVER CHECK"),
         ("5. Fix & Flush", "Correct DNS/Hosts + flushdns", "VERIFY")],
        [("Step 1: IP vs Name Split", "If `ping <IP>` works and `ping <name>` fails, L1-L3 routing is 100% healthy", "Fault is strictly Name Resolution", "Never replace cables or change default gateway when raw IP pings succeed"),
         ("Resolution Order", "1. Local hostname -> 2. `hosts` file -> 3. Local DNS cache -> 4. Configured DNS server", "`C:\\Windows\\System32\\drivers\\etc\\hosts`", "`nslookup` bypasses the `hosts` file and queries the DNS server directly!"),
         ("The `hosts` File Trap", "Stale hard-coded line in `hosts` overrides DNS for browsers/ping, while `nslookup` looks fine!", "`Resolve-DnsName` vs `nslookup`", "If `nslookup app.local` returns the right IP but `ping app.local` hits an old IP, check `hosts`!"),
         ("Wrong DNS Server IP", "Static DNS pointing to dead IP (`10.0.0.99`) or public DNS (`8.8.8.8`) on an internal AD domain", "`ipconfig /all` -> DNS Servers", "Public DNS (`8.8.8.8`) cannot resolve private Active Directory names (`corp.local`)"),
         ("Verify Fix", "Correct DNS server / clean `hosts` -> `ipconfig /flushdns` -> test `Resolve-DnsName` & app", "Confirm both CLI and browser work", "Forgetting `ipconfig /flushdns` leaves the negative cache entry alive until TTL expires")],
        "`nslookup` Ignores the Local `hosts` File — So If `nslookup` Works but `ping <name>` Hits the Wrong IP, Check `hosts`!",
        "This is a classic technician trap: `nslookup` talks directly to the DNS server on port 53 and completely ignores `C:\\Windows\\System32\\drivers\\etc\\hosts`. If `nslookup` shows the new IP `10.1.1.50` but `ping` and the browser still connect to `10.1.1.9`, open `drivers\\etc\\hosts`.",
    ),
    "13.5": (
        "Windows 11 Settings Paths, MMC Consoles & CLI Equivalences",
        [("1. Settings GUI", "ms-settings:* URI Paths", "MODERN UI"),
         ("2. CLI Equivalent", "ipconfig / systeminfo", "CROSS-CHECK"),
         ("3. MMC Consoles", "services / eventvwr / devmgmt", "ADMIN TOOLS"),
         ("4. Legacy Applets", "ncpa.cpl / appwiz.cpl", "DIRECT LAUNCH"),
         ("5. Verify Match", "GUI Fact == CLI Output", "EVIDENCE")],
        [("System > About", "`ms-settings:about` -> Device name, Edition, OS build, RAM", "CLI: `hostname`, `winver`, `systeminfo`", "Quickest check for Windows Home vs Pro before attempting Domain Join or BitLocker"),
         ("Network Properties", "Settings > Network & internet > Ethernet/Wi-Fi (IP assignment, DNS)", "Applet: `ncpa.cpl` | CLI: `ipconfig /all`", "Settings shows 'Automatic (DHCP)' or 'Manual' next to DNS and IPv4"),
         ("Windows Update History", "Settings > Windows Update > Update history (`ms-settings:windowsupdate-history`)", "CLI: `Get-HotFix` / `wusa`", "Shows exact date and 0x8007xxxx failure code for failed quality/driver updates"),
         ("MMC Admin Consoles", "`services.msc` (Services), `eventvwr.msc` (Logs), `devmgmt.msc` (Drivers), `diskmgmt.msc`", "Win+X Power User Menu or Run (`Win+R`)", "Not everything lives in modern Settings; service dependencies require `services.msc`"),
         ("Control Panel Shortcuts", "`ncpa.cpl` (Adapters), `appwiz.cpl` (Programs), `sysdm.cpl` (Domain/System Props)", "Type directly in `Win+R` or Search", "`sysdm.cpl` -> Change button is still the fastest path to join an Active Directory domain")],
        "Know Your `.msc` and `.cpl` Fast-Launch Names for Both Live Labs and Exams",
        "Exam items and locked-down user sessions often require launching the exact tool without hunting through menus: `devmgmt.msc` (Device Manager), `diskmgmt.msc` (Disk Management), `services.msc` (Services), `eventvwr.msc` (Event Viewer), and `ncpa.cpl` (Network Connections).",
    ),
    "13.6": (
        "Process-to-Service Mapping (`tasklist /svc`), `netsh` & When NOT to Reboot",
        [("1. Observe Load", "Task Mgr / Get-Process", "INSPECT"),
         ("2. Map Services", "tasklist /svc (svchost)", "CORRELATE"),
         ("3. Inspect Socket", "netstat -ano / Get-NetTCP", "PORT -> PID"),
         ("4. Targeted Restart", "Restart-Service (No Reboot)", "SURGICAL"),
         ("5. Change Log", "Record Reason Before Reboot", "DISCIPLINE")],
        [("tasklist /svc", "Maps each `svchost.exe` PID to the exact Windows service names it hosts", "`tasklist /svc | findstr <PID>`", "Killing a random `svchost.exe` without `/svc` can crash RPC or DCOM and BSOD the PC"),
         ("Port-to-Process Map", "Finds which PID is listening on or holding a TCP/UDP port", "`netstat -ano` or `Get-NetTCPConnection`", "Join the PID column from `netstat -ano` to `tasklist /fi \"PID eq N\"`"),
         ("netsh Interface & WLAN", "`netsh interface ip show config`, `netsh wlan show interfaces`", "Matches `Get-NetIPConfiguration`", "`netsh wlan show wlanreport` generates a 3-day HTML wireless disconnect timeline"),
         ("Restart Service vs OS", "If Print Spooler (`Spooler`) or DNS Client (`Dnscache`) hangs, restart the service", "`Restart-Service -Name Spooler`", "Rebooting a workstation destroys unsaved user work and wipes volatile log state"),
         ("When Reboot IS Required", "Kernel/servicing updates (`PendingFileRenameOperations`), Winsock reset, hardware swap", "Schedule with user & save work first", "'Have you tried rebooting?' before reading logs erases the evidence of why it failed")],
        "Rebooting First Destroys Evidence — Inspect Processes (`tasklist /svc`) and Logs Before Restarting",
        "An unplanned reboot clears volatile network sockets (`netstat -ano`), resets hung process trees, and forces the user to wait until the fault randomly recurs. Always capture the offending PID/service and Event Viewer entry first, and prefer a surgical service restart over a blind OS reboot.",
    ),
})

BLUEPRINTS_NETOPS = {
    "1.1": (
        "OSI 7-Layer Stack, TCP/IP Encapsulation PDUs & Layer Isolation",
        [("L7-L5 Application", "Data Payload (HTTP/DNS)", "DATA PDU"),
         ("L4 Transport", "TCP/UDP Port + Seq/Ack", "SEGMENT"),
         ("L3 Network", "Src/Dst IP + TTL Hop", "PACKET"),
         ("L2 Data Link", "Src/Dst MAC + FCS/VLAN", "FRAME"),
         ("L1 Physical", "Copper Volts / Fiber Light", "BITS")],
        [("L1 Physical", "Bits on wire/fiber/RF; cables, RJ-45, SFP, patch panels, hubs", "`show interfaces` (line/protocol)", "Unplugged cable, cut fiber, or EMI noise -> Layer 1 down"),
         ("L2 Data Link", "Frames; MAC addresses (48-bit), 802.1Q VLAN tags, switches, ARP", "`show mac address-table`, `arp -a`", "Wrong VLAN ID or STP port blocked -> same-subnet ARP fails"),
         ("L3 Network", "Packets; IPv4/IPv6 logical addressing, routers, L3 switches, ICMP", "`ip route`, `ping`, `traceroute`", "Each router hop rewrites L2 src/dst MAC and decrements L3 TTL"),
         ("L4 Transport", "Segments (TCP) / Datagrams (UDP); port numbers, flow control", "`ss -tulnp`, `Test-NetConnection`", "Host reachable by ICMP (L3) but firewall drops TCP port 443 (L4)"),
         ("L5-L7 Upper Layers", "Session, Presentation (TLS/encoding), Application (HTTP, DNS, SMB)", "`curl -v`, `nslookup`, logs", "TCP 443 handshake succeeds (L4) but HTTP returns 503 Service Unavailable (L7)")],
        "Routers Rewrite Layer-2 MAC Addresses at Every Hop While Keeping Layer-3 Source/Dest IPs Intact",
        "As an IP packet crosses multiple routers (without NAT), the **source and destination IP addresses remain unchanged**, TTL decrements by 1 at each router, and the **Layer-2 source and destination MAC addresses are rewritten on every link**.",
    ),
    "1.2": (
        "IPv4 CIDR Subnetting Math (`2^h - 2`) & IPv6 Address Types",
        [("1. Prefix / CIDR", "/24 to /30 Bit Boundary", "MASK"),
         ("2. Network ID", "All Host Bits = 0", "SUBNET BASE"),
         ("3. Usable Hosts", "2^(32-p) - 2 Range", "ASSIGNABLE"),
         ("4. Broadcast ID", "All Host Bits = 1", "DIRECTED BCAST"),
         ("5. IPv6 128-Bit", "2000::/3 & fe80::/10", "DUAL STACK")],
        [("CIDR Quick Table", "/24=254, /25=126, /26=62, /27=30, /28=14, /29=6, /30=2 hosts", "Usable = 2^(32 - prefix) - 2", "Point-to-point router links use /30 (2 hosts, 255.255.255.252) or /31"),
         ("Subnet Boundary Math", "Block size = 256 - last non-zero mask octet (e.g. .192 -> block 64)", "Multiples of block size = Net IDs", "For /26 (.192): subnets start at .0, .64, .128, .192; .63 is broadcast of first!"),
         ("RFC 1918 Private", "10.0.0.0/8, 172.16.0.0/12 (172.16-31), 192.168.0.0/16", "Not routed on public Internet", "CGNAT shared space is 100.64.0.0/10; Loopback is 127.0.0.0/8"),
         ("IPv6 Unicast Types", "Global (`2000::/3`), Unique Local (`fc00::/7`/`fd00::/8`), Link-Local (`fe80::/10`)", "SLAAC uses ICMPv6 Router Adv (RA)", "IPv6 has NO broadcast; uses Multicast (`ff00::/8`, e.g., `ff02::1` all-nodes)"),
         ("EUI-64 & Privacy", "64-bit network prefix + 64-bit interface ID", "Dual-stack runs IPv4 & IPv6 together", "Blocking ICMPv6 breaks IPv6 Neighbor Discovery (NDP) and SLAAC!")],
        "WatchSubnet Boundaries: In a `/26` (`255.255.255.192`), `.63` Is a Broadcast Address and `.64` Is a Network ID",
        "When an exam stem gives a host IP like `192.168.1.63/26` and asks why it cannot communicate, calculate the block size (`256 - 192 = 64`): Subnet 0 is `.0` to `.63` (where `.0` is Network ID and `.63` is Broadcast), so usable hosts are `.1` through `.62`!",
    ),
    "1.3": (
        "TCP 3-Way Handshake (SYN -> SYN-ACK -> ACK) vs. Connectionless UDP",
        [("1. Client SYN", "Seq=x, Syn Flag=1", "STEP 1"),
         ("2. Server SYN-ACK", "Seq=y, Ack=x+1", "STEP 2"),
         ("3. Client ACK", "Ack=y+1 (Established)", "STEP 3"),
         ("4. Windowed Flow", "Ordered + Retransmit", "RELIABLE TCP"),
         ("5. UDP Datagram", "Zero Handshake / Low Lag", "FAST UDP")],
        [("TCP (Connection-Oriented)", "3-way handshake, sequence/ack numbers, sliding window, retransmission", "20-byte header; guaranteed delivery", "HTTPS (443), SSH (22), SMB (445), RDP (3389), SMTP (25/587), BGP (179)"),
         ("UDP (Connectionless)", "No handshake, no retransmission, no ordering; 8-byte header", "Minimal latency & overhead", "DHCP (67/68), TFTP (69), SNMP (161/162), Syslog (514), NTP (123), VoIP RTP"),
         ("Dual-Transport Protocols", "DNS (53) uses UDP for standard queries & TCP for zone transfers/large replies", "Kerberos (88) also uses TCP & UDP", "Blocking TCP 53 breaks DNSSEC responses >512 bytes and AXFR zone transfers"),
         ("Port Scan States", "Open (SYN-ACK), Closed (RST), Filtered/Firewall Drop (Timeout/ICMP prohib)", "`Test-NetConnection` / `nc -zv`", "`Connection Refused` (RST) proves the host is reachable at L3, but the service isn't listening!"),
         ("Teardown States", "FIN -> ACK -> FIN -> ACK (graceful) vs RST (abrupt abort)", "`TIME_WAIT` holds socket briefly", "Thousands of `SYN_RECEIVED` half-open sockets indicate a SYN flood attack")],
        "`Connection Refused` (TCP RST) Proves Routing Works — The Target Host Simply Has No Service Listening on That Port",
        "Don't confuse **Connection Timed Out** (packet dropped silently by a firewall or dead route) with **Connection Refused** (the target host received your SYN and actively replied with a TCP `RST` because the daemon is stopped).",
    ),
    "1.4": (
        "OSI Layer Mapping Capstone: Bottom-Up vs. Divide-and-Conquer",
        [("1. Read Symptom", "Map to Lowest Layer", "CLASSIFY"),
         ("2. Pick Strategy", "Bottom-Up / Split @ L3", "METHOD"),
         ("3. Run L3 Probe", "ping IP (Splits L1-3 / L4-7)", "BISECT"),
         ("4. Narrow Layer", "ARP (L2) vs Port (L4)", "ISOLATE"),
         ("5. Peer Ticket", "Action -> Result + Layer", "DOCUMENT")],
        [("Bottom-Up Approach", "Start at L1 (cable/link LED) -> L2 (VLAN/MAC) -> L3 (IP/GW) -> L7", "Best when physical/local link is suspect", "Single desktop moved to a new cubicle has no link light -> start at L1"),
         ("Top-Down Approach", "Start at L7 application/auth -> L4 port -> L3 IP", "Best when other apps on same PC work", "User is on a Zoom call fine, but one internal web app throws HTTP 500 -> start at L7"),
         ("Divide-and-Conquer", "Test Layer 3 (`ping <target_IP>`) first to split stack in half", "Pass -> check L4-L7; Fail -> check L1-L3", "Fastest initial test when you have zero prior context on a remote ticket"),
         ("Layer 2 vs Layer 3", "Same-subnet ping tests L1+L2 (ARP/switch); cross-subnet tests L3 router", "`arp -a` vs `tracert -d`", "Host pings subnet peers (`.50`) but fails gateway (`.1`) -> check gateway IP/mask/ARP"),
         ("Evidence Standard", "Record exact command, output, and the OSI layer ruled in/out", "Peer-verifiable audit line", "'Checked network, looks fine' is rejected; write `ping 10.0.0.1 -> 4/4 (<1ms), L1-L3 local OK`")],
        "A Single Successful `ping <Remote_IP>` Simultaneously Proves Layers 1, 2, and 3 End-to-End",
        "If `ping 10.20.30.40` succeeds, stop checking patch cables (L1), VLAN tags (L2), subnet masks (L3), and routing tables (L3)—move immediately to Layer 4 (ports/firewalls) and Layer 7 (DNS/application).",
    ),
    "2.1": (
        "Layer-2 Switch Forwarding: Learn (Src MAC), Flood & Spanning Tree (STP)",
        [("1. Frame Arrives", "Read Source MAC + Port", "LEARN"),
         ("2. Update CAM", "MAC -> Port + VLAN Timer", "300S AGE"),
         ("3. Lookup Dst MAC", "Known Unicast vs Unknown", "DECISION"),
         ("4. Forward / Flood", "1 Port vs All VLAN Ports", "EGRESS"),
         ("5. STP Loop Guard", "802.1D/w Root + Block", "LOOP-FREE")],
        [("Source MAC Learning", "Switch populates CAM table by inspecting **Source MAC** of ingress frames", "`show mac address-table`", "A silent device that never transmits will not appear in the MAC table until it speaks"),
         ("Known Unicast", "Destination MAC is in CAM table -> forwarded out that **single** port only", "Each switch port = 1 collision domain", "Microsegmentation eliminates collisions (full-duplex links need no CSMA/CD)"),
         ("Flooding (Bcast/Unknown)", "`FF:FF:FF:FF:FF:FF` broadcast or unknown unicast floods all ports in **same VLAN**", "1 VLAN = 1 broadcast domain", "Routers (L3) stop broadcasts; switches (L2) flood broadcasts within the VLAN"),
         ("Spanning Tree (802.1D/w)", "Elects Root Bridge (lowest Bridge ID = Priority + MAC); blocks redundant paths", "802.1w RSTP converges in ~1-2 sec", "Unplugged STP/looped patch cord between two wall jacks causes a **Broadcast Storm**"),
         ("PortFast & BPDU Guard", "PortFast transitions access ports to Forwarding immediately; BPDU Guard shuts port on BPDU", "`spanning-tree portfast` / `bpduguard`", "Rogue switch plugged into a BPDU Guard access port puts port into `err-disabled`")],
        "Switches Learn from the SOURCE MAC and Forward/Flood Based on the DESTINATION MAC",
        "An exam classic: when Host A sends its very first frame to Host B through an empty switch, the switch **learns Host A's MAC on the ingress port**, then **floods the frame out all other ports in that VLAN** because Host B's MAC is not in the table yet.",
    ),
    "2.2": (
        "IEEE 802.1Q VLAN Tagging, Access vs. Trunk Ports & Inter-VLAN Routing",
        [("1. Access Port", "Untagged Host Frame", "VLAN 10"),
         ("2. Ingress Tag", "Insert 4-Byte 802.1Q Tag", "VID=10"),
         ("3. 802.1Q Trunk", "Carries Allowed VLANs", "SW <-> SW/RTR"),
         ("4. L3 SVI / ROAS", "Route VLAN 10 <-> VLAN 20", "DEFAULT GW"),
         ("5. Egress Strip", "Strip Tag -> Access Port", "VLAN 20")],
        [("Access Port", "Belongs to **one** VLAN; sends/receives untagged frames to end hosts", "`switchport mode access` + `vlan <ID>`", "+ Voice VLAN (`switchport voice vlan`) is the one exception for IP phone + PC"),
         ("802.1Q Trunk Port", "Inserts 4-byte tag into Ethernet header to carry multiple VLANs across 1 link", "`switchport mode trunk` + `allowed vlan`", "If VLAN 20 is missing from `trunk allowed vlan`, VLAN 20 is cut in half across switches"),
         ("Native VLAN", "Traffic sent **untagged** across an 802.1Q trunk (default VLAN 1)", "Must match on BOTH ends of trunk!", "Native VLAN mismatch logs `%CDP-4-NATIVE_VLAN_MISMATCH` and leaks frames between VLANs"),
         ("Wrong-VLAN Ticket", "Port assigned to VLAN 10 while PC has static IP for VLAN 20 (or gets VLAN 10 DHCP)", "`show vlan brief`", "PC cannot ping its default gateway because its port is in the wrong broadcast domain"),
         ("Inter-VLAN Routing", "VLANs cannot talk without Layer 3: **L3 Switch SVI** (`interface Vlan10`) or **Router-on-a-Stick**", "802.1Q subinterfaces (`Gi0/0.10`)", "Forgetting `encapsulation dot1Q 10` on router subinterface drops inter-VLAN traffic")],
        "Two Common Trunk Failures: Pruned Allowed-VLAN List and Native VLAN Mismatch",
        "When users on Switch B in VLAN 30 cannot reach their gateway on Switch A (while VLAN 10 users on Switch B work fine), check two commands first: `show vlan brief` (does VLAN 30 exist in Switch B's local VLAN database?) and `show interfaces trunk` (is VLAN 30 in the `Vlans allowed on trunk` list?).",
    ),
    "2.3": (
        "TIA-568 Structured Cabling, PoE Budgets (802.3af/at/bt) & Fiber Optics",
        [("1. Core Switch", "SFP+ / PoE+ PSE Port", "MDF / IDF"),
         ("2. Patch Panel", "110 Punchdown (T568B)", "CROSS-CONNECT"),
         ("3. Horizontal Run", "<= 90m Solid Copper", "PLENUM CMP"),
         ("4. Wall Keystone", "<= 10m Patch Cords", "100M MAX"),
         ("5. Fiber Uplink", "SMF (OS2) vs MMF (OM4)", "TX <-> RX")],
        [("Copper Categories", "Cat 5e: 1 Gbps (100m) | Cat 6: 10 Gbps (55m) | Cat 6A: 10 Gbps (100m)", "Max channel = **100m** (90m solid + 10m patch)", "Run beyond 100m suffers attenuation & late collisions; use fiber or an IDF switch"),
         ("T568A vs T568B Pinout", "Swaps green (pair 3) & orange (pair 2) on pins 1-2 and 3-6", "Use same standard on both ends (T568B)", "T568A on one end + T568B on the other creates a 100BASE-TX crossover cable"),
         ("Plenum (CMP) vs Riser", "**Plenum (CMP)** low-smoke fire-retardant jacket for air-handling drop ceilings", "PVC / Riser (CMR) emits toxic fumes", "Fire code requires Plenum-rated (CMP) cable in HVAC return-air plenum spaces"),
         ("PoE Standards (IEEE)", "**802.3af (PoE)**: 15.4W | **802.3at (PoE+)**: 30W | **802.3bt (PoE++)**: 60W/100W", "`show power inline` checks PoE budget", "Wi-Fi 6E/7 AP or PTZ camera rebooting under load -> switch port only supplying 15.4W 802.3af"),
         ("Fiber (SMF vs MMF)", "**SMF** (Yellow, 9um core, laser, 2-40km+, LX/LR) vs **MMF** (Aqua/Orange, 50um, LED/VCSEL, <=400m, SX/SR)", "LC (small square), SC, ST, MPO connectors", "Newly patched fiber link stays down -> **roll/swap the TX and RX strands** on one end!")],
        "Fiber Link Down After Patching? Check TX/RX Polarity & Wavelength/Mode Match (SMF vs. MMF)",
        "Because duplex fiber uses one strand to transmit (TX) and one to receive (RX), TX on Switch A must land on RX on Switch B. Also, never plug a Single-Mode (1310nm LR) transceiver into Multi-Mode (850nm SR) fiber.",
    ),
    "2.4": (
        "Isolated User Physical-to-VLAN Capstone Triage",
        [("1. Neighbor Check", "Does Cubicle Next Door Work?", "SCOPE = 1"),
         ("2. L1 Jack & Cord", "Swap Patch / Check LED", "PHYSICAL"),
         ("3. Switchport Status", "up/up vs err-disabled", "LINK STATE"),
         ("4. VLAN Membership", "show vlan brief (Access)", "LAYER 2"),
         ("5. Verify & Label", "ipconfig /renew + Ping GW", "CLOSURE")],
        [("up / up", "Layer 1 physical carrier present AND Layer 2 keepalives healthy", "`show interfaces status` (`connected`)", "Link is physically and logically up; check VLAN ID and DHCP next"),
         ("administratively down", "Someone issued `shutdown` on the switch interface", "Fix in `conf t`: `no shutdown`", "New wall drop patched into a switchport left `shutdown` by default"),
         ("down / down (`notconnect`)", "No Layer 1 electrical/optical carrier detected", "Check patch cord, punchdown, NIC", "Broken RJ-45 tab, wrong patch panel port, or dead TDR pair"),
         ("err-disabled", "Switch shut the port down due to a security/loop violation", "Port Security, BPDU Guard, DHCP Snooping", "Fix cause first, then bounce port: `shutdown` -> `no shutdown`"),
         ("Duplex / CRC Errors", "Half/Full duplex mismatch or damaged cable pair", "`show interfaces` -> CRC / Giants / Runts", "One side hardcoded `100/Full` while auto-negotiate side falls back to `100/Half` -> late collisions")],
        "Auto-Negotiation vs. Hardcoded Full Duplex Causes a Half-Duplex Fallback and Late Collisions",
        "If one end of an Ethernet link is hardcoded to `speed 100` / `duplex full` (which disables auto-negotiation pulses) and the other end is set to `auto`, the `auto` side senses 100 Mbps carrier but no negotiation pulses—and falls back to **100/Half-Duplex**, causing severe CRC errors and late collisions.",
    ),
    "3.1": (
        "IP Routing Table Lookup: Longest-Prefix Match, AD & FHRP (HSRP/VRRP)",
        [("1. Packet Ingress", "Inspect Dst IP Header", "L3 LOOKUP"),
         ("2. Longest Prefix", "/28 Beats /24 Beats /16", "RULE #1"),
         ("3. Admin Distance", "C(0) < S(1) < OSPF(110)", "TRUST TIE"),
         ("4. Next-Hop ARP", "Rewrite L2 MAC + TTL-1", "FORWARD"),
         ("5. FHRP Virtual IP", "HSRP / VRRP Active/Stby", "GATEWAY HA")],
        [("Longest-Prefix Match", "Router ALWAYS picks the route with the **most matching network bits** (highest `/N`)", "/27 beats /24 regardless of AD/metric!", "Packet for `10.1.1.5` matches `10.1.1.0/28` over `10.1.0.0/16` even if `/16` is static"),
         ("Administrative Distance", "Trustworthiness of route source (used only when prefixes are **identical**)", "Connected=0, Static=1, eBGP=20, OSPF=110", "Floating static backup route uses a higher AD (e.g., `ip route ... 200`)"),
         ("Route Table Codes", "`C` (Connected), `L` (Local /32), `S` (Static), `O` (OSPF), `B` (BGP), `*` (Candidate default)", "`show ip route`", "Gateway of last resort is `0.0.0.0/0` (IPv4) or `::/0` (IPv6); missing = drops unknown nets"),
         ("OSPF vs BGP", "**OSPF**: Link-state IGP (Dijkstra SPF, cost = bw, Areas/Area 0) | **BGP**: Path-vector EGP (AS-Path, TCP 179)", "Interior (IGP) vs Exterior (EGP)", "Enterprise campus uses OSPF internally; ISP/multi-homed WAN edge uses BGP"),
         ("FHRP (HSRP / VRRP)", "Two physical routers share one **Virtual IP (VIP)** and Virtual MAC as the hosts' default gateway", "HSRP (Cisco) / VRRP (Standards)", "If Router A dies, Router B takes over VIP `.1` transparently without changing host settings")],
        "Longest-Prefix Match ALWAYS Wins Before Administrative Distance Is Even Checked",
        "Do not fall for the Administrative Distance distractor when prefix lengths differ! If a routing table has a Static route (`AD 1`) for `10.0.0.0/16` and an OSPF route (`AD 110`) for `10.0.5.0/24`, traffic to `10.0.5.10` takes the **OSPF `/24` route** because `/24` is more specific than `/16`.",
    ),
    "3.2": (
        "WAN Demarcation Point, Access Media & Site-to-Site Overlays (VPN / SD-WAN)",
        [("1. Customer LAN", "Core Switch -> Firewall/CE", "CUSTOMER OWNS"),
         ("2. Demarc / NIU", "MPOE / Smartjack / ONT", "HANDOFF BOUNDARY"),
         ("3. Local Loop", "Fiber / Coax / 5G / Sat", "ISP LAST MILE"),
         ("4. WAN Core", "MPLS / MetroE / Internet", "PROVIDER BACKBONE"),
         ("5. Overlay Tunnel", "IPsec VPN / SD-WAN", "ENCRYPTED")],
        [("Demarcation Point (Demarc)", "Physical boundary where ISP responsibility ends and customer CPE wiring begins", "MPOE / Smartjack / Fiber ONT", "Test directly at the ONT/handoff port before calling the ISP to avoid a truck-roll fee"),
         ("WAN Access Media", "**Fiber/MetroE**: Symmetrical, low latency | **Cable (DOCSIS)**: Shared coax | **5G/LTE**: Cellular failover | **LEO/GEO Sat**: High latency", "Compare latency, symmetry & SLA", "Geostationary satellite has ~600 ms RTT (bad for VoIP); LEO satellite reduces RTT to ~30-50 ms"),
         ("MPLS vsLeased Line", "Private provider-managed label-switched WAN with QoS SLAs (not encrypted by default)", "Multi-site predictable voice/video", "High monthly cost and slow provisioning compared to broadband Internet"),
         ("Site-to-Site IPsec VPN", "Encrypts traffic across public Internet using IKE (UDP 500/4500) + ESP (Protocol 50)", "Confidentiality, Integrity, Auth", "Mismatched Phase 1/2 ciphers, PSK, or local/remote subnets prevents tunnel bring-up"),
         ("SD-WAN Architecture", "Decouples control plane; steers apps dynamically across Fiber + Broadband + 5G", "Application-aware path selection", "Automatically shifts voice/ERP from degraded broadband to 5G/MPLS based on jitter/loss")],
        "Before Opening an ISP Outage Ticket, Verify Power and Link at the Demarc (ONT / Modem)",
        "If an entire branch loses Internet, check whether the CPE router can ping the ISP gateway and whether the ISP ONT/modem has power and optical link (`PON`/`LOS` LED). Calling the ISP when the branch UPS tripped in the MPOE closet wastes hours.",
    ),
    "3.3": (
        "Enterprise WLAN: 802.11 Generations, Channel Reuse & 802.1X / RADIUS",
        [("1. Supplicant (Client)", "Wi-Fi 6/6E/7 Association", "RF CHANNEL"),
         ("2. Authenticator (AP)", "WLC CAPWAP + VLAN Map", "802.1X / EAP"),
         ("3. Auth Server", "RADIUS (UDP 1812/1813)", "VERIFY CERT/AD"),
         ("4. Dynamic Keys", "Per-Session PMK / PTK", "WPA3-ENT"),
         ("5. Roaming / RF", "RSSI -65dBm / SNR >25dB", "CAPACITY")],
        [("Wi-Fi Generations", "Wi-Fi 5 (`802.11ac`, 5GHz) | Wi-Fi 6 (`802.11ax`, 2.4/5GHz) | **Wi-Fi 6E** (+6GHz) | **Wi-Fi 7** (`802.11be`, MLO, 320MHz)", "OFDMA + MU-MIMO boost high-density", "Wi-Fi 6E and Wi-Fi 7 open the clean **6 GHz** band"),
         ("Channel Planning", "2.4 GHz: **1, 6, 11** (20 MHz) | 5 GHz: UNII-1/2(DFS)/3 (20/40 MHz in enterprise)", "Adjacent APs on different channels", "Setting 80/160 MHz channel width in a dense office causes severe co-channel contention"),
         ("WPA3-Enterprise (802.1X)", "**Supplicant** (Client) <-> **Authenticator** (AP/WLC) <-> **Authentication Server** (RADIUS)", "EAP-TLS (client+server certs) / PEAP", "Removing one departing employee's AD account revokes Wi-Fi without changing 500 devices' PSK!"),
         ("Open Guest Wi-Fi: OWE", "**Opportunistic Wireless Encryption (Enhanced Open)** encrypts air traffic without a password", "Captive portal handles guest T&Cs", "Legacy Open Wi-Fi sends unencrypted frames in cleartext to any sniffer in the cafe"),
         ("RF Health Metrics", "**RSSI**: `-30` to `-67 dBm` (good), `-80 dBm` (bad) | **SNR**: `>= 25 dB` | Channel Utilization `< 50%`", "Remember: `-55 dBm` is STRONGER than `-78 dBm`!", "High RSSI (`-50 dBm`) + terrible throughput = co-channel interference or over-subscribed AP")],
        "Negative dBm Math (`-50 dBm` Beats `-80 dBm`) & Why WPA3-Enterprise Uses 802.1X/RADIUS",
        "Because dBm is negative relative to 1 mW, **`-50 dBm` is 1,000x stronger than `-80 dBm`** (every 3 dB doubles/halves power; 10 dB = 10x). And whenever an enterprise needs individual user accountability or instant offboarding without changing a shared Wi-Fi password, choose **WPA2/WPA3-Enterprise (802.1X + RADIUS)**.",
    ),
    "3.4": (
        "Wireless Capacity & Roaming Capstone Triage",
        [("1. Measure RF", "RSSI, Noise, SNR, Util%", "SITE SURVEY"),
         ("2. Check Channel", "Overlap on 2/3/4/5/8?", "CO-CHANNEL"),
         ("3. Check Density", "65 Clients on 1 Radio?", "AIRTIME"),
         ("4. Band Steering", "Move Capable Clients -> 5/6GHz", "OPTIMIZE"),
         ("5. Verify Roam", "Packet Loss / Jitter Test", "CLOSURE")],
        [("Strong Signal, Slow Speed", "RSSI is `-52 dBm` (5 bars) in auditorium, but pages time out", "60+ clients sharing one 2.4 GHz channel", "Airtime saturation! Add 5/6 GHz AP capacity, narrow channel widths to 20 MHz, enable band steering"),
         ("Adjacent Channel Overlap", "APs set to Channels 1, 3, and 6 on 2.4 GHz", "Frames collide as corrupt noise/CRC", "Reassign strictly to **1, 6, and 11** so partially overlapping sidebands don't corrupt frames"),
         ("Sticky Client Roaming", "Laptop stays clung to distant lobby AP at `-82 dBm` while sitting under a `-50 dBm` AP", "2.4 GHz transmit power set too high", "Lower 2.4 GHz AP power and enable `802.11k/v/r` fast roaming"),
         ("DFS Channel Dropouts", "5 GHz AP on channel 52-144 suddenly changes channel when weather/airport radar is detected", "Dynamic Frequency Selection (DFS)", "Move critical voice/classroom APs to non-DFS UNII-1 (36-48) or UNII-3 (149-165)"),
         ("Evil Twin / Rogue AP", "Unauthorized BSSID broadcasting corporate SSID with stronger signal", "Enable WIPS / 802.11w PMF + 802.1X", "Mutual authentication (EAP-TLS) prevents client from trusting an unverified rogue RADIUS")],
        "'Full Bars' (`-50 dBm`) With Zero Throughput Means Airtime Contention or Backhaul Saturation",
        "Signal bars only measure the beacon strength from the AP to the laptop—they tell you nothing about whether 80 other laptops are contending for the same half-duplex RF channel or whether the AP's switch uplink is bottlenecked.",
    ),
    "4.1": (
        "DHCP Enterprise Architecture: DORA, Relay (`ip helper-address`) & Snooping",
        [("1. Client Broadcast", "Discover 255.255.255.255", "VLAN 20"),
         ("2. Router Relay", "ip helper-address Unicast", "GIADDR SET"),
         ("3. DHCP Server", "Matches GIADDR to Scope", "VLAN 10 SRV"),
         ("4. Offer & Ack", "IP + Opt 3 GW + Opt 6 DNS", "DORA COMPLETE"),
         ("5. DHCP Snooping", "Trusted Uplink vs Untrusted", "SECURITY")],
        [("DORA Packet Types", "Discover (Bcast) -> Offer -> Request (Bcast) -> ACK (UDP 67/68)", "Lease renews at T1 (50%) & T2 (87.5%)", "Request is broadcast so all other offering DHCP servers know their offer was declined"),
         ("DHCP Relay (`ip helper`)", "Configured on the **router interface/SVI facing the clients** (not the server VLAN!)", "`ip helper-address <DHCP_Srv_IP>`", "Router converts L2 broadcast into unicast to central DHCP server and stamps `GIADDR`"),
         ("Scope Exhaustion", "Pool is 100% leased out; new clients get `169.254.x.x` while existing clients still work", "Shorten lease time on guest Wi-Fi", "8-day lease time on a coffee-shop/visitor VLAN exhausts a `/24` pool by noon"),
         ("Reservations vs Exclusions", "**Reservation** binds 1 IP to 1 MAC via DHCP | **Exclusion** keeps DHCP from handing out static IPs", "Printers/servers use Reservations/Exclusions", "Assigning `.10` statically on a printer without excluding/reserving `.10` causes duplicate IP conflicts"),
         ("DHCP Snooping", "Blocks DHCP Offers/ACKs from **untrusted** access ports; builds binding table for DAI", "`ip dhcp snooping trust` on uplink", "Student plugging a home router LAN port into a wall jack hands out rogue `192.168.1.1` leases")],
        "`ip helper-address` Goes on the Client VLAN Interface, Pointing to the Central DHCP Server IP",
        "When clients in VLAN 20 (`10.20.0.0/24`) get `169.254.x.x` while the DHCP server lives in VLAN 10 (`10.10.0.50`), verify three things: (1) a `10.20.0.0/24` scope exists and is active on the server, (2) `ip helper-address 10.10.0.50` is set on `interface Vlan20`, and (3) UDP 67/68 is permitted.",
    ),
    "4.2": (
        "DNS Hierarchy (Root -> TLD -> Authoritative), Record Types & Split-Horizon",
        [("1. Stub Resolver", "OS Cache + hosts File", "CLIENT"),
         ("2. Recursive Srv", "Enterprise / ISP Resolver", "CACHE / ITERATE"),
         ("3. Root & TLD", "`.` -> `.com` NS Referral", "HIERARCHY"),
         ("4. Authoritative", "Holds Zone SOA + Records", "SOURCE OF TRUTH"),
         ("5. Answer + TTL", "Cached for TTL Seconds", "RESPONSE")],
        [("Address Records", "**A** -> IPv4 (`192.0.2.1`) | **AAAA** -> IPv6 (`2001:db8::1`) | **PTR** -> Reverse IP-to-Name (`in-addr.arpa`)", "`dig`, `nslookup`, `Resolve-DnsName`", "Missing PTR record causes outbound enterprise mail to be rejected by strict spam filters"),
         ("Alias & Service Records", "**CNAME** -> Canonical alias (`app` -> `lb.cloud.net`) | **MX** -> Mail server + priority | **SRV** -> `_ldap._tcp`", "Lower MX preference number = HIGHER priority", "MX priority 10 is tried BEFORE MX priority 20!"),
         ("Zone Authority & Text", "**SOA** -> Start of Authority (serial#, refresh, retry, negative TTL) | **NS** -> Name Servers | **TXT** -> SPF/DKIM/DMARC", "Increment SOA serial after manual edit", "TXT records hold **SPF** (allowed sender IPs), **DKIM** (public crypto key), and **DMARC** (policy)"),
         ("DNS Security", "**DNSSEC** signs records cryptographically (RRSIG/DNSKEY) for authenticity | **DoH (TCP 443) / DoT (TCP 853)** encrypt queries", "DNSSEC != confidentiality (doesn't encrypt)", "Exam trap: **DNSSEC** prevents cache poisoning/spoofing via digital signatures; **DoH/DoT** encrypts privacy"),
         ("Split-Horizon (Split-Brain)", "Internal DNS returns private IP (`10.1.2.5`); external DNS returns public IP (`203.0.113.5`) for same FQDN", "Internal vs External views", "VPN user missing internal DNS suffix/resolver gets public IP and fails internal firewall check")],
        "DNSSEC Authenticates Records (Does NOT Encrypt); DoH/DoT Encrypts Queries; Lower MX Number Wins",
        "Three high-frequency DNS exam traps: (1) **DNSSEC** digitally signs DNS answers to prevent spoofing, but queries are still cleartext; **DoT (853)** and **DoH (443)** encrypt the transport. (2) **MX 10** is preferred over **MX 50**. (3) **A** = IPv4, **AAAA** = IPv6.",
    ),
    "4.3": (
        "NAT/PAT Translation & Stateful Firewall First-Match Rule Processing",
        [("1. Inside Host", "Src 10.0.1.5:51422", "RFC 1918"),
         ("2. Zone Policy", "Inside -> Outside Inspect", "FIRST MATCH"),
         ("3. State Table", "Track Conn Tuple + Timer", "STATEFUL"),
         ("4. PAT Overload", "Src 203.0.113.9:61004", "WAN EGRESS"),
         ("5. Implicit Deny", "Unmatched Inbound Dropped", "DEFAULT DENY")],
        [("PAT / NAT Overload", "Many private Inside Local IPs share **one** Inside Global public IP using unique source ports", "Home/branch router standard", "Allows 200 office PCs to browse the Internet simultaneously using a single public IPv4"),
         ("Static NAT / Port Fwd", "1-to-1 permanent mapping (or single port DNAT) so external clients can initiate inbound connections", "Used for DMZ web/VPN endpoints", "Outbound PAT works automatically, but inbound public requests fail without DNAT/Port Forwarding"),
         ("Stateful vs Stateless", "**Stateful** tracks active flows in a state table and auto-allows return traffic; **Stateless ACL** checks each packet in isolation", "Stateful inspects connection state", "Stateless outbound ACL fails unless you manually add an inbound rule for ephemeral return ports"),
         ("First-Match Evaluation", "Firewall reads ACL/rules **top-to-bottom** and executes the **very first matching rule**", "Specific rules MUST go above broad rules!", "Putting `deny tcp any any` on Line 10 shadows `permit tcp any host 10.1.1.5 eq 443` on Line 20"),
         ("Implicit Deny All", "Invisible `deny ip any any` sits at the bottom of every ACL/firewall policy", "Log dropped packets when debugging", "An ACL with only one `deny` statement drops 100% of all other traffic because nothing was permitted!")],
        "Firewall Rules Execute Top-Down (First Match Wins) and End with an Implicit `Deny Any Any`",
        "If an administrator adds `permit tcp any host 10.0.0.10 eq 443` at the bottom of a firewall policy and traffic is still blocked, look higher in the list for a broader `deny ip 10.0.0.0/8 any` rule that matched first.",
    ),
    "4.4": (
        "'Internet Down' Core Services Capstone Isolation (DHCP -> Gateway -> NAT -> DNS)",
        [("1. Check Lease", "Valid IP vs 169.254?", "DHCP (L7/UDP)"),
         ("2. Ping Gateway", "Reach Local Router?", "LAN (L2/L3)"),
         ("3. Ping Public IP", "ping 1.1.1.1 / 8.8.8.8", "WAN / NAT"),
         ("4. Test DNS", "nslookup example.com", "DNS (UDP 53)"),
         ("5. Test TCP 443", "curl / TNC Port 443", "FIREWALL")],
        [("Symptom A: 169.254.x.x", "Client has APIPA; cannot ping gateway or anything else", "DHCP server down, scope full, or relay missing", "Fix DHCP scope or `ip helper-address`; NAT and DNS are innocent"),
         ("Symptom B: GW OK, 8.8.8.8 Fails", "Clients have valid leases and ping `10.1.1.1`, but `ping 8.8.8.8` fails", "Default route (`0.0.0.0/0`), ISP link, or PAT", "Check router `show ip route`, `show ip nat translations`, and WAN interface status"),
         ("Symptom C: 8.8.8.8 OK, Name Fails", "`ping 8.8.8.8` succeeds, but `nslookup` and web URLs fail", "DNS forwarder down or UDP/TCP 53 blocked", "Verify DHCP Option 6 (DNS Server IP) and firewall rule permitting port 53 to resolver"),
         ("Symptom D: DNS OK, HTTPS Fails", "`nslookup` returns IP and `ping` works, but browsers time out on HTTPS", "Firewall ACL blocking TCP 443 or bad proxy", "Inspect firewall rule order for accidental block of outbound TCP 80/443"),
         ("Escalation Packet", "Attach outputs of `ipconfig /all`, `ping <GW>`, `ping 8.8.8.8`, `nslookup`, `tracert -d`", "Proves exact failing hop/service", "Saves 45 minutes of finger-pointing between Server Admin and Network Ops")],
        "'The Internet Is Down' Is a User Symptom, Never a Technical Diagnosis",
        "Users say 'the Internet is down' for five completely different faults: an unplugged patch cable, an exhausted DHCP scope, a dead WAN circuit, a broken DNS forwarder, or a firewall rule blocking TCP 443. Isolate in order: Lease -> Gateway -> Public IP -> DNS -> Port 443.",
    ),
}

BLUEPRINTS_NETOPS.update({
    "5.1": (
        "Network Telemetry: SNMPv3 (161/162), Syslog Severities (0-7) & Interface Counters",
        [("1. Device Agent", "MIB Counters + Events", "ROUTER / SW"),
         ("2. SNMPv3 Poll", "UDP 161 Get/Walk (authPriv)", "PULL METRICS"),
         ("3. SNMP Trap/Syslog", "UDP 162 Trap / 514 Syslog", "PUSH ALERTS"),
         ("4. NTP Clock Sync", "UDP 123 Stratum Hierarchy", "TIMESTAMPS"),
         ("5. Baseline Alert", "CRC / Drops / Util >80%", "SIEM / NMS")],
        [("SNMP Polling vs Traps", "**UDP 161**: NMS polls agent (`Get`/`Walk`) | **UDP 162**: Agent pushes unsolicited **Trap/Inform**", "**SNMPv3** adds `authPriv` (SHA + AES)", "SNMPv1/v2c send `public`/`private` community strings in cleartext!"),
         ("Syslog Severities (0-7)", "0 Emerg, 1 Alert, 2 Crit, 3 Error, 4 Warn, 5 Notice, 6 Info, 7 Debug", "Lower number = HIGHER severity!", "`logging trap warning` (4) forwards levels **0, 1, 2, 3, and 4** to SIEM"),
         ("Interface Error Counters", "**CRC / FCS**: Bad cable/EMI/duplex | **Runts** (<64B): Collisions | **Giants** (>1518B): MTU/baby-giant", "`show interfaces`", "Rising Input Errors + CRC on a copper port -> swap patch cable & check duplex"),
         ("Output Drops / Discards", "Interface outbound queue full due to burst congestion or rate-limiting", "QoS (DSCP EF=46 for Voice)", "Output drops with 0 CRC errors means bandwidth oversubscription, not a bad cable"),
         ("NTP Time Sync (UDP 123)", "Synchronizes device clocks to Stratum 1/2 reference before forwarding logs", "`ntp server <IP>`", "Unsynchronized switch clocks make multi-hop incident correlation impossible")],
        "Syslog Level 0 (`Emergency`) Is Highest Severity; SNMP Polls on UDP 161 and Traps on UDP 162",
        "Mnemonic for Syslog 0–7: **E**very **A**lleys **C**at **E**ats **W**atery **N**oodles **I**n **D**itches (0=Emergency, 1=Alert, 2=Critical, 3=Error, 4=Warning, 5=Notice, 6=Informational, 7=Debugging). Also never confuse SNMP Poll (`UDP 161`) with SNMP Trap (`UDP 162`).",
    ),
    "5.2": (
        "Management Plane Hardening: SSHv2, AAA (TACACS+ vs. RADIUS) & Out-of-Band",
        [("1. Admin Source", "Jump Host / Mgmt VLAN 99", "VTY ACL"),
         ("2. Encrypted Transport", "SSHv2 (22) / HTTPS (443)", "NO TELNET!"),
         ("3. AAA Check", "TACACS+ (TCP 49) / RADIUS", "CENTRAL AUTH"),
         ("4. Break-Glass Local", "local secret (If AAA Down)", "FALLBACK"),
         ("5. Command Audit", "Accounting Log to SIEM", "COMPLIANCE")],
        [("Cleartext -> Secure Map", "Telnet (23) -> **SSH (22)** | HTTP (80) -> **HTTPS (443)** | SNMPv2c -> **SNMPv3** | TFTP (69) -> **SFTP/SCP**", "`transport input ssh` on `line vty`", "Leaving `transport input all` allows a single Telnet login to expose admin credentials"),
         ("TACACS+ vs RADIUS", "**TACACS+** (TCP 49): Encrypts full body, separates AAA, logs every CLI command | **RADIUS** (UDP 1812/1813): Network/802.1X", "Device CLI Admin -> TACACS+; Wi-Fi/VPN -> RADIUS", "TACACS+ authorizes individual `conf t` router commands; RADIUS combines Auth+Authz"),
         ("Local Break-Glass Account", "`aaa authentication login default group tacacs+ local`", "`username admin secret <strong_hash>`", "If the WAN link to TACACS+ dies and `local` fallback is missing, admins are locked out!"),
         ("Management Plane ACL", "Restrict VTY/HTTPS logins to the dedicated **Management VLAN / Jump Box** (`access-class`)", "Out-of-Band (OOB) console server", "Allowing SSH from the Guest Wi-Fi VLAN exposes core switches to brute-force scans"),
         ("Config Hygiene", "`service password-encryption`, `enable secret` (Type 8/9 scrypt/SHA), login banner (`banner motd`), idle `exec-timeout`", "Disable CDP/LLDP on untrusted WAN ports", "Leaving an unattended console session with `exec-timeout 0 0` lets anyone walk up in `enable` mode")],
        "TACACS+ (TCP 49) for Device CLI Command Authorization; RADIUS (UDP 1812/1813) for 802.1X/VPN Network Access",
        "When an exam scenario asks for centralized AAA that **authorizes and logs each individual CLI command** an engineer types on routers and switches, pick **TACACS+**. When it asks for **802.1X wireless/switchport authentication**, pick **RADIUS**.",
    ),
    "5.3": (
        "Zero-Trust Network Segmentation, Zones (DMZ / IoT / Mgmt) & 802.1X NAC",
        [("1. Untrusted Edge", "Internet -> Screened DMZ", "PERIMETER"),
         ("2. Internal Zones", "Users / Servers / Mgmt", "VLAN + ACL"),
         ("3. High-Risk Iso", "IoT / HVAC / Guest VLAN", "BLAST RADIUS"),
         ("4. 802.1X / NAC", "Posture + Dynamic VLAN", "IDENTITY PORT"),
         ("5. East-West Guard", "Microsegmentation Policy", "ZERO TRUST")],
        [("Screened Subnet (DMZ)", "Holds public-facing web/mail/reverse-proxy servers between External and Internal firewall rules", "Allow Internet -> DMZ:443; BLOCK DMZ -> LAN", "If a public web server in the DMZ is compromised, the firewall blocks it from initiating SMB/RDP into the internal LAN"),
         ("IoT & Building Systems", "Badge readers, IP cameras, smart TVs, HVAC controllers go in a dedicated **IoT VLAN**", "Deny IoT -> Corporate LAN; allow only required controller", "Compromised smart thermostat on the flat corporate VLAN used to pivot into Finance file servers"),
         ("Guest Network Isolation", "Separate Guest VLAN + **Client Isolation** (Private VLAN / AP isolation) + Internet-only ACL", "Blocks peer-to-peer L2 sniffing", "Without client isolation, one guest laptop can ARP-spoof another guest on the same AP"),
         ("802.1X & NAC Posture", "Authenticates device certificate before opening switchport; checks AV/patch posture; assigns dynamic VLAN", "Unhealthy host -> Quarantine/Remediation VLAN", "Plugging a rogue laptop into a conference room wall jack lands in a dead/quarantine VLAN"),
         ("Microsegmentation", "Host/hypervisor-level east-west policies between workloads even inside the same subnet", "Stops lateral movement inside Data Center", "Traditional perimeter firewalls never see east-west traffic between two VMs on the same VLAN")],
        "DMZ Servers Must Never Be Allowed to Initiate Unsolicited Connections into the Internal LAN",
        "In a properly segmented Screened Subnet (DMZ), internal servers or admins may initiate connections toward the DMZ (or the DMZ talks only to a tightly scoped backend port), while arbitrary **DMZ -> Internal LAN** initiation is denied to contain public web compromises.",
    ),
    "5.4": (
        "Switch & Router Hardening Audit Capstone Workflow",
        [("1. Audit Config", "show run / show int status", "DISCOVER"),
         ("2. Rank Risk", "Telnet/Default Pass = High", "PRIORITIZE"),
         ("3. Unused Ports", "shutdown + VLAN 999 Blackhole", "L2 HARDEN"),
         ("4. Guard Features", "BPDU Guard + DHCP Snoop", "EDGE PROTECT"),
         ("5. Change Request", "Backout + Save Startup", "CONTROL")],
        [("Critical Finding #1", "`transport input telnet` or `enable password` (cleartext/Type 7) on VTY lines", "Switch to `transport input ssh` + `enable secret`", "Anyone running Wireshark on the path captures the admin password in plain text"),
         ("Critical Finding #2", "SNMP `rw` community set to `private` or `public` with no ACL", "Disable SNMPv1/v2c; deploy SNMPv3 `authPriv`", "Read-Write (`rw`) SNMPv2c lets an attacker modify the device's running configuration remotely!"),
         ("Unused Access Ports", "20 empty switchports left `no shutdown` in Default VLAN 1", "`shutdown` + `switchport access vlan <unused>`", "Visitor plugs into an active lobby jack and lands directly on VLAN 1"),
         ("L2 Edge Protections", "Enable **PortFast + BPDU Guard**, **DHCP Snooping**, and **Dynamic ARP Inspection (DAI)** on user ports", "Leave trunk uplinks `trusted`", "Enabling DHCP Snooping globally without trusting the uplink port breaks DHCP for everyone!"),
         ("Default VLAN 1 Hygiene", "Move user ports off VLAN 1; change trunk Native VLAN to an unused VLAN ID", "`switchport trunk native vlan 999`", "Mitigates double-tagging VLAN hopping attacks that exploit default Native VLAN 1")],
        "Enabling DHCP Snooping Without Setting `ip dhcp snooping trust` on the Uplink Drops All DHCP Leases!",
        "By default, DHCP Snooping marks **every** port on the switch as `untrusted` (blocking incoming DHCP Offers and ACKs). You must explicitly configure `ip dhcp snooping trust` on the trunk/uplink port leading to the legitimate DHCP server.",
    ),
    "6.1": (
        "Network Fault Pattern Library: Scope First & Look-Alike Discrimination",
        [("1. Map Scope", "1 Host / 1 VLAN / 1 Site", "BLAST RADIUS"),
         ("2. Compare Peer", "Working Neighbor Output", "BASELINE"),
         ("3. Split Look-Alike", "DNS vs Route / VLAN vs DHCP", "DISCRIMINATE"),
         ("4. Inspect Counters", "CRC / STP / NAT Table", "TELEMETRY"),
         ("5. First Proof Test", "1 Command Kills Theory", "ISOLATE")],
        [("DNS vs Routing Look-Alike", "Both look like 'websites won't load' -> Run **`ping 8.8.8.8`** vs **`nslookup`**", "8.8.8.8 OK = DNS fault; 8.8.8.8 Fail = Route/NAT", "Restarting the DNS server when the ISP fiber circuit is dark"),
         ("Wrong VLAN vs Dead DHCP", "Static IP works in Neither if wrong VLAN; Static IP works if only DHCP service is down", "`show vlan brief` + `ipconfig /all`", "Client getting a valid `10.30.x.x` lease on a port meant for `10.20.x.x` is on the wrong access VLAN"),
         ("Duplex Mismatch vs Congestion", "Both cause slow transfers -> Check **`show interfaces`** for **Late Collisions / CRC** vs **Output Drops**", "CRC/Late Collisions = Duplex/L1; Drops = Bandwidth", "Upgrading WAN bandwidth when a core switchport is stuck at 100/Half-Duplex"),
         ("Intermittent 30-50s Dropouts", "All users on a switch lose connectivity for 30-50 seconds whenever a desk PC reboots", "STP topology change / missing PortFast", "Enable `spanning-tree portfast` on edge access ports so workstation boots don't trigger TCNs"),
         ("Asymmetric / Blackhole Route", "`traceroute` reaches hop 3 and loops (`A -> B -> A`) or dies at one subnet", "`show ip route` on both routers", "Return route missing on remote router (packet arrives at server, reply has no route back)")],
        "One-Way Routing Trap: Packets Reach the Destination, Yet `ping` Fails Because the Return Route Is Missing",
        "Remember that `ping` requires a round trip! If Router A has a static route to Subnet B, but Router B has no route back to Subnet A, pings will time out even though Router A's routing table looks 100% correct.",
    ),
    "6.2": (
        "Incident Execution Under Pressure: 7-Step Method, Time-Boxes & Rollback vs. Push Forward",
        [("1. Stabilize & Scope", "Who / Since When / What Chg?", "T+0 TRIAGE"),
         ("2. Recent Change?", "Correlate Change Log", "PRIME SUSPECT"),
         ("3. Time-Box Theory", "15-Min Cap per Test", "DISCIPLINE"),
         ("4. Rollback Decision", "Revert Change vs Fix Fwd", "GATE"),
         ("5. Cadence Update", "Facts + Impact + Next ETA", "STAKEHOLDERS")],
        [("Recent Change Correlation", "80% of sudden multi-user outages follow a recent config change, patch, or cable move", "`show archive log config` / ticket log", "Spending 2 hours debugging OSPF from scratch when an engineer edited an ACL 10 minutes ago"),
         ("Rollback vs Push Forward", "If a maintenance change causes unplanned outage and cannot be fixed within the time-box -> **ROLL BACK**", "Restore pre-change config backup", "'Just one more tweak' at 5:45 AM extends a maintenance window into a Monday morning outage"),
         ("Time-Box Escalation", "If your top theories fail within 15-20 minutes or require higher privilege, escalate immediately", "Hand over clean command transcript", "Holding a critical outage ticket for 90 minutes out of pride before paging Senior NetOps"),
         ("Predictable Status Cadence", "Send concise status every 15-30 min: **Impact, Known Facts, Current Action, Next Update Time**", "No speculation or finger-pointing", "Silence during a Sev-1 outage causes executives and users to flood the help desk"),
         ("Single-Change Discipline", "Even in an outage, apply and test **one** change at a time (and undo it if it doesn't help)", "Prevents compounding secondary faults", "Flipping 6 switchports and 3 firewall rules in a panic makes rollback impossible")],
        "When an Outage Starts Right After a Change and the Fix Isn't Immediate, Roll Back First!",
        "During a live Sev-1 incident caused by a recent change, the priority is **restoring service** via the documented backout plan—not debugging the new configuration live on the production floor.",
    ),
    "6.3": (
        "Network Verification, Living Documentation (L1/L2/L3 Diagrams) & Blameless PIR",
        [("1. End-to-End Verify", "CLI Counters + User App", "PROVEN"),
         ("2. Save Config", "copy run start + Backup", "PERSIST"),
         ("3. Update Diagrams", "Physical / Logical / IPAM", "TRUTH"),
         ("4. Publish Runbook", "Symptom -> Proof -> Fix", "KB ARTICLE"),
         ("5. Blameless PIR", "Timeline + Systemic Guard", "PREVENT")],
        [("Before/After Verification", "Compare `show ip route`, `show int status`, `ping`, and real user application workflow", "Zero rising CRC/drop counters", "Closing ticket after `ping` works while VoIP phones still fail to register on Voice VLAN"),
         ("Save Running Config", "Copy volatile RAM (`running-config`) to NVRAM (`startup-config`) and central Git/TFTP backup", "`copy running-config startup-config` (`wr`)", "Fixing a VLAN at 2 PM without saving -> 8 PM power blip reverts the switch to the broken config!"),
         ("Network Documentation Set", "**Physical diagram** (racks/patch panels/ports), **Logical diagram** (VLANs/subnets/OSPF), **IPAM**", "Update within change closure", "Stale wiring/VLAN diagrams cause the next technician to unplug the wrong production trunk"),
         ("IDF / Rack Hygiene", "Label both ends of every patch cord; use cable management; document MDF/IDF patch table", "TIA-606 labeling standard", "Unlabeled 'spaghetti' closet wiring turns a 2-minute port trace into a 2-hour outage"),
         ("Blameless Post-Incident (PIR)", "Chronological timeline, root cause, what went well, and **automated guardrails** to prevent recurrence", "Fix the process, not blame the person", "Punishing an engineer for a typo instead of adding pre-commit config validation")],
        "Fixing `running-config` Without Saving to `startup-config` Turns the Next Power Blip into a Repeat Outage",
        "Every configuration change in RAM (`running-config`) vanishes on reload unless committed to NVRAM with `copy running-config startup-config` (or `write memory`) after verification.",
    ),
    "6.4": (
        "Full Multi-Fault Network Capstone: Layered Triage & Evidence Packet",
        [("1. Intake & Scope", "Map Affected Subnets/Users", "BLAST RADIUS"),
         ("2. L1/L2 Check", "Link / Trunk / VLAN / PoE", "SWITCHING"),
         ("3. L3 Routing/DHCP", "SVI / Helper / Route Table", "ROUTING"),
         ("4. L4/L7 Edge", "NAT / Firewall ACL / DNS", "SERVICES"),
         ("5. Verify & Save", "User Test + wr mem + PIR", "COMPLETE")],
        [("Multi-Fault Trap", "Fixing Fault #1 (e.g., `no shutdown` on port) reveals Fault #2 (e.g., wrong VLAN or missing DNS)", "Re-run full verification ladder after fix!", "Stopping after the link light turns green without checking if the PC actually gets a DHCP lease"),
         ("Layer-by-Layer Audit", "L1 (`show int status`) -> L2 (`show vlan brief`, `show int trunk`) -> L3 (`show ip route`) -> L4/7 (ACL/DNS)", "Systematic elimination", "Jumping between router ACLs and client browsers randomly"),
         ("Evidence Packet Standard", "Every hypothesis paired with exact CLI command, output excerpt, and conclusion", "Reproducible by any peer", "Submitting a capstone summary with 'Fixed router' and no `show` command evidence"),
         ("Status & Escalation", "Clear interim status message + clean escalation boundary for ISP/Security-owned gear", "Professional operations habit", "Modifying out-of-scope firewall policies without authorization"),
         ("Final Persistence Check", "Confirm `running-config` matches `startup-config` and IPAM/diagrams reflect final state", "`show startup-config`", "Leaving temporary debug commands or unsaved changes on lab/production gear")],
        "In Multi-Fault Scenarios, Fixing Layer 1/2 Only Uncovers Layer 3/7 — Always Verify All the Way to the Application",
        "In both real closets and capstone labs, a port might be `shutdown` AND assigned to the wrong VLAN, or a router interface might need `no shutdown` AND `ip helper-address`. Never stop at 'link light is green'—verify lease, gateway ping, DNS, and application access.",
    ),
    "9.1": (
        "Cisco IOS CLI Modes, Console Serial Parameters & Hostname Identity",
        [("1. Physical Console", "Rollover / USB-Serial", "9600-8-N-1"),
         ("2. User EXEC", "Switch> (Read-Only Basic)", "PROMPT >"),
         ("3. Privileged EXEC", "enable -> Switch#", "PROMPT #"),
         ("4. Global Config", "conf t -> Switch(config)#", "PROMPT (config)#"),
         ("5. Sub-Mode & Exit", "int / line -> end -> wr", "VERIFY")],
        [("Serial Console Settings", "**9600 baud**, **8** data bits, **No** parity, **1** stop bit, **No** flow control (`9600-8-N-1`)", "PuTTY / screen / minicom", "Wrong baud rate (e.g., 115200 on a 9600 console) prints garbage characters on screen"),
         ("User EXEC (`>`)", "Limited non-destructive inspection (`ping`, basic `show`); cannot view full config or reboot", "`Switch>` or `Router>`", "Typing `configure terminal` at `Switch>` fails—must enter `enable` first"),
         ("Privileged EXEC (`#`)", "Full inspection (`show running-config`), debug, file copy, reload", "`enable` -> `Switch#`", "Typing `show run` inside `(config)#` fails on older IOS unless prefixed with `do show run`"),
         ("Global Config (`(config)#`)", "Changes device state live in RAM immediately as each line is entered", "`configure terminal` (`conf t`)", "Every command in `(config)#` takes effect in `running-config` immediately!"),
         ("Interface / Line Submodes", "`interface Gi0/1` -> `(config-if)#` | `line console 0` / `line vty 0 15` -> `(config-line)#`", "`exit` steps back 1 level; `end` / `Ctrl+Z` -> `#`", "Setting `hostname SW-IDF1` in `(config)#` changes prompt immediately to match rack label")],
        "CLI Prompt Literacy: `>` (User), `#` (Privileged), `(config)#` (Global), `(config-if)#` (Interface)",
        "Always read the CLI prompt before typing a command! `show running-config` and `write memory` live at Privileged EXEC (`#`), `hostname` lives at Global Config (`(config)#`), and `ip address` / `no shutdown` live inside Interface Config (`(config-if)#`).",
    ),
    "9.2": (
        "Switch CLI: Creating VLANs, Assigning Access Ports & Verification",
        [("1. Create VLAN DB", "vlan 10 -> name USERS", "(config-vlan)#"),
         ("2. Select Port", "interface Gi0/1", "(config-if)#"),
         ("3. Set Access Mode", "switchport mode access", "UNTAGGED"),
         ("4. Bind VLAN ID", "switchport access vlan 10", "ASSIGN"),
         ("5. Verify State", "show vlan brief & status", "SW# CHECK")],
        [("Step 1: Create & Name VLAN", "`vlan 10` then `name SALES` in global configuration mode", "`show vlan brief` confirms active", "Creating `interface Vlan10` (L3 SVI) does NOT create the Layer-2 VLAN in the VLAN database on all platforms!"),
         ("Step 2: Access Port Config", "`interface FastEthernet0/1` -> `switchport mode access` -> `switchport access vlan 10`", "Add `spanning-tree portfast`", "Leaving port in dynamic auto/desirable mode delays link startup and risks unauthorized trunking"),
         ("Assigning Non-Existent VLAN", "If you type `switchport access vlan 20` before `vlan 20` exists, modern IOS auto-creates VLAN 0020", "Always verify name in `show vlan brief`", "If a VLAN is in `act/lshut` or missing from `show vlan brief`, ports in that VLAN go amber/inactive"),
         ("Deleting a VLAN Trap", "If you run `no vlan 20` while ports are still assigned to VLAN 20, those ports become **orphaned/inactive**!", "Move ports to another VLAN first!", "Orphaned ports disappear from `show vlan brief` and drop all host traffic until reassigned"),
         ("Verification Triad", "`show vlan brief` (port-to-VLAN map), `show interfaces status` (up/VLAN/speed), `show mac address-table vlan 10`", "Run at `Switch#` prompt", "Never assume a port moved to VLAN 10 without checking `show vlan brief`")],
        "Deleting a VLAN (`no vlan 20`) Orphans Every Port Still Assigned to It!",
        "If you delete a VLAN from the switch database without first moving its access ports to a valid VLAN, those ports become inactive 'phantom' ports that cannot pass traffic even though their cables are plugged in.",
    ),
    "9.3": (
        "Router CLI: Addressing Interfaces, `no shutdown` & Connected Routes (`C` / `L`)",
        [("1. Enter Interface", "interface Gi0/0", "(config-if)#"),
         ("2. Add Description", "description LAN_VLAN10_GW", "DOCUMENT"),
         ("3. Assign IPv4/Mask", "ip address 10.10.10.1 255...", "LAYER 3"),
         ("4. Enable Carrier", "no shutdown (CRITICAL!)", "BRING UP"),
         ("5. Verify Table", "show ip int brief & route", "C + L ROUTES")],
        [("Router Port Default State", "Unlike switch ports (which default to `no shutdown`), **router interfaces default to `administratively down`!**", "MUST run `no shutdown`!", "Configuring `ip address` and exiting without `no shutdown` leaves the port `administratively down / down`"),
         ("show ip interface brief", "Displays Interface, IP-Address, OK?, Method, **Status (L1)**, and **Protocol (L2)**", "Target state: `up` / `up`", "`administratively down / down` = needs `no shutdown`; `down / down` = bad cable/unplugged peer"),
         ("Connected (`C`) & Local (`L`)", "As soon as an interface has an IP and goes `up/up`, IOS injects **`C` (subnet)** and **`L` (/32 host IP)** routes", "`show ip route`", "If an interface is `down/down`, its `C` and `L` routes vanish from the routing table automatically!"),
         ("Subnet Overlap Error", "IOS rejects configuring two router interfaces in overlapping IP subnets", "`% 10.1.1.0 overlaps with Gi0/0`", "A router connects **different** subnets/VLANs; two routed ports cannot share the same `/24`"),
         ("End-to-End Ping Test", "Router pings host (`ping 10.10.10.50`); host pings default gateway (`ping 10.10.10.1`)", "First ping may drop 1 packet for ARP!", "`! ! ! !` (80% success on first ping: `. ! ! ! !`) is completely normal while ARP resolves the MAC")],
        "Router Interfaces Default to `shutdown` — And First Ping Often Drops One Packet (`.!!!!`) Due to ARP",
        "Two essential router CLI facts: (1) Router ports ship `administratively down`, so you must type **`no shutdown`** for the `C` (Connected) route to appear in `show ip route`. (2) Seeing `.!!!!` (80% success) on the very first ping to a new subnet host is normal while ARP resolves the L2 MAC; re-running `ping` immediately yields `!!!!!` (100%).",
    ),
    "9.4": (
        "Inter-VLAN Routing Lab: Router-on-a-Stick (802.1Q Subinterfaces) vs. L3 Switch SVIs",
        [("1. Switch Access", "PC1 (VLAN 10) / PC2 (VLAN 20)", "ACCESS PORTS"),
         ("2. Switch Trunk", "Gi0/24 switchport mode trunk", "802.1Q UPLINK"),
         ("3. Physical Parent", "Router Gi0/0: no ip + no shut", "CARRIER UP"),
         ("4. 802.1Q Sub-Int", "Gi0/0.10: encap dot1Q 10 + IP", "GATEWAY .1"),
         ("5. Cross-VLAN Ping", "PC1 -> .10.1 -> .20.1 -> PC2", "ROUTED")],
        [("Parent Interface Setup", "`interface Gi0/0` -> `no ip address` -> **`no shutdown`**", "Parent physical port MUST be `no shut`", "Configuring `Gi0/0.10` and `Gi0/0.20` while parent `Gi0/0` is still `shutdown` leaves all subinterfaces dead!"),
         ("Subinterface Order", "`interface Gi0/0.10` -> **`encapsulation dot1Q 10`** FIRST -> THEN `ip address 10.0.10.1 255.255.255.0`", "Must set `dot1Q <VLAN>` before IP!", "IOS rejects `ip address` on a subinterface until `encapsulation dot1Q <vlan-id>` is configured"),
         ("Switch Uplink Port", "The switch port connected to the router MUST be an **802.1Q Trunk** (`switchport mode trunk`)", "`show interfaces trunk`", "Leaving the switch uplink as an access port in VLAN 1 drops all tagged `.10` and `.20` frames!"),
         ("L3 Switch SVI Alternative", "Create L2 VLAN (`vlan 10`), then `interface Vlan10` -> `ip address ...` -> `no shutdown` + global `ip routing`", "Wire-speed hardware routing", "An SVI (`interface Vlan10`) stays `down/down` unless VLAN 10 exists AND has at least 1 active up port/trunk"),
         ("Host Gateway Mistake", "PC in VLAN 10 (`10.0.10.50`) must set Default Gateway = `10.0.10.1` (its own VLAN subinterface)", "`ipconfig` on PC", "Setting PC1's gateway to `10.0.20.1` fails because a host's gateway MUST be in its own subnet")],
        "Three Classic Router-on-a-Stick Bugs: Parent Port `shutdown`, Switch Uplink Not a Trunk, or `encapsulation dot1Q` Missing",
        "When inter-VLAN routing fails in Lab 9.4, check in this exact order: (1) Is the switch-to-router port in `show interfaces trunk`? (2) Is the router parent `Gi0/0` `up/up` (`no shutdown`)? (3) Does each subinterface have the matching `encapsulation dot1Q <VLAN_ID>`?",
    ),
    "9.5": (
        "New Closet Drop Capstone: Ordered Switch + Router + Host Verification",
        [("1. Patch & L1 Check", "show interfaces status", "CONNECTED?"),
         ("2. L2 VLAN & Trunk", "show vlan brief / trunk", "VLAN MATCH"),
         ("3. L3 Gateway SVI", "show ip int brief / route", "GW UP/UP"),
         ("4. Host Lease/Ping", "ipconfig /all -> ping GW", "END-TO-END"),
         ("5. Ticket & Save", "CLI Evidence + write mem", "CLOSURE")],
        [("Check 1: Switch Port L1", "`show interfaces status` -> verify new drop port is `connected` (`up/up`), not `disabled` or `notconnect`", "Fix: `no shutdown` / check cable", "Testing DHCP on the PC while the closet switchport is still `administratively down`"),
         ("Check 2: Access VLAN ID", "`show vlan brief` -> verify port is assigned to the department's VLAN (e.g., VLAN 20), not default VLAN 1", "`switchport access vlan 20`", "Port is `up/up` in VLAN 1 while the PC has a static IP for VLAN 20"),
         ("Check 3: Trunk to Router", "`show interfaces trunk` -> confirm the new VLAN is allowed and forwarding on the uplink trunk", "`switchport trunk allowed vlan add 20`", "Access port is in VLAN 20, but VLAN 20 was pruned from the uplink trunk to the router"),
         ("Check 4: Gateway & DHCP", "`show ip interface brief` on router -> confirm `.20` subinterface/SVI is `up/up` with right IP/mask", "Ping gateway from PC, then remote VLAN", "Typo in router subinterface subnet mask (`255.255.255.252` instead of `.0`) blocks `.50` host"),
         ("Check 5: Escalation Scope", "Document exact switch, port (`Gi0/14`), patch panel jack (`B-14`), VLAN ID, and CLI verification outputs", "Escalate core firewall/WAN if blocked", "Closing a closet drop ticket without recording which switchport jack B-14 is patched into")],
        "Trace the Frame Path from Wall Jack -> Access Port -> VLAN DB -> Trunk Uplink -> Router Subinterface",
        "Every new closet drop follows one physical-to-logical chain: Wall Jack -> Patch Panel -> Switch Access Port (`up/up` + right `access vlan`) -> Active VLAN in `show vlan brief` -> Allowed on 802.1Q Trunk -> Router Subinterface/SVI (`up/up` + right `dot1Q` tag and IP).",
    ),
    "9.6": (
        "Device Identity (`hostname`) & Configuration Persistence (`running-config` -> `startup-config`)",
        [("1. Identify Rack/Role", "Closet Label (e.g. IDF2-SW1)", "STANDARD"),
         ("2. Set Hostname", "conf t -> hostname IDF2-SW1", "RAM (LIVE)"),
         ("3. Verify Running", "show running-config", "VOLATILE RAM"),
         ("4. Commit to NVRAM", "copy run start / write mem", "PERSIST"),
         ("5. Verify Startup", "show startup-config", "SURVIVES RELOAD")],
        [("running-config (DRAM)", "Active configuration in volatile RAM; changes in `(config)#` take effect here immediately", "`show running-config` (`sh run`)", "**Lost completely** on power loss or `reload` if not saved to NVRAM!"),
         ("startup-config (NVRAM)", "Non-volatile configuration loaded at boot time after IOS image decompresses from Flash", "`show startup-config` (`sh start`)", "If `startup-config` is missing or stale, device boots into initial setup dialog or old state"),
         ("Save Commands", "`copy running-config startup-config` or `write memory` (`wr`) at the Privileged EXEC `#` prompt", "Confirm `[OK]` / `Building configuration...`", "Typing `write memory` inside `(config)#` fails unless you exit to `#` or type `do write memory`"),
         ("Naming Standard", "`hostname <SITE>-<CLOSET>-<ROLE><NUM>` (e.g., `NYC-IDF3-SW01`)", "Matches physical label & NMS/Syslog", "Leaving 12 switches named `Switch` makes Syslog alerts and SSH tabs impossible to distinguish"),
         ("Accidental Lockout Recovery", "If an unsaved ACL/change locks you out remotely (and wasn't saved), a scheduled `reload in 10` reverts to `startup-config`", "`reload cancel` once verified", "Saving a broken VTY ACL to `startup-config` before testing a second SSH session makes the lockout permanent!")],
        "Test Your New SSH/ACL Session BEFORE Running `copy running-config startup-config` — Then Always Save!",
        "When modifying management access or trunk uplinks, open a second verification session to prove everything works, and **immediately run `copy running-config startup-config` (`write memory`)** so a power blip six weeks later doesn't wipe out your work.",
    ),
})

# Build the complete 115-lesson index keyed by (course_code, chapter_order, lesson_order)
LESSON_VISUALS: dict[tuple[str, int, int], tuple] = {}

for _lbl, _spec in BLUEPRINTS_ITSUP.items():
    _ch_s, _les_s = _lbl.split(".")
    _ch_i, _les_i = int(_ch_s), int(_les_s)
    LESSON_VISUALS[("ITSUP", _ch_i, _les_i)] = _spec
    # CLIENT chapters 1..6 correspond to lessons 8.1 .. 13.6
    if 8 <= _ch_i <= 13:
        _c_ch = _ch_i - 7
        _c_title = f"{_spec[0]} (Operating Systems Track)"
        LESSON_VISUALS[("CLIENT", _c_ch, _les_i)] = (
            _c_title,
            _spec[1],
            _spec[2],
            _spec[3],
            _spec[4],
        )

for _lbl, _spec in BLUEPRINTS_NETOPS.items():
    _ch_s, _les_s = _lbl.split(".")
    LESSON_VISUALS[("NETOPS", int(_ch_s), int(_les_s))] = _spec

_LABEL_PREFIX_RE = re.compile(r"^\s*(\d+\.\d+)\b")


# User-facing course names; internal codes stay in ids and keys.
COURSE_DISPLAY = {"ITSUP": "IT Support", "NETOPS": "Basic Networking", "CLIENT": "Operating Systems"}


def course_display(code: str) -> str:
    c = (code or "").upper()
    return COURSE_DISPLAY.get(c, c)


def get_lesson_blueprint(course_code: str, ch_order: int, les_order: int, lesson_title: str = "") -> tuple:
    """Return (arch_title, stages, spec_rows, watchout_title, watchout_body) for any lesson."""
    code = (course_code or "ITSUP").upper()
    key = (code, int(ch_order), int(les_order))
    if key in LESSON_VISUALS:
        return LESSON_VISUALS[key]
    m = _LABEL_PREFIX_RE.match(lesson_title or "")
    if m:
        lbl = m.group(1)
        if code == "NETOPS" and lbl in BLUEPRINTS_NETOPS:
            return BLUEPRINTS_NETOPS[lbl]
        if lbl in BLUEPRINTS_ITSUP:
            return BLUEPRINTS_ITSUP[lbl]
    # Fallback generator by title/topic if a custom lesson is ever added
    clean_title = (lesson_title or f"{course_display(code)} {ch_order}.{les_order}").strip()
    return (
        f"{clean_title} — Architecture & Signal Path",
        [("1. Intake & Scope", "Verify Context", "STAGE 1"),
         ("2. Baseline Check", "Read-Only Audit", "STAGE 2"),
         ("3. Isolate Layer", "Single Variable", "STAGE 3"),
         ("4. Controlled Fix", "Apply & Test", "STAGE 4"),
         ("5. Verify & Log", "User Outcome", "STAGE 5")],
        [("Scope & Identity", "Confirm affected asset, user, and blast radius", "hostname / whoami", "Skipping scope wastes time on wrong fault domain"),
         ("Baseline Capture", "Record pre-change state before modifying settings", "ipconfig /all / logs", "Unrecorded changes prevent clean rollback"),
         ("Isolation Method", "Test cheapest discriminating hypothesis first", "Divide-and-Conquer", "Changing multiple variables hides root cause"),
         ("Verification Gate", "Re-run failed test and confirm with end user", "Before/After proof", "Closing ticket before user workflow is verified")],
        "Verify Scope and Baseline Evidence Before Changing System State",
        "Always capture read-only evidence first, change one variable at a time, and verify the fix with the user before closing the ticket.",
    )


def render_visual_blueprint(course_code: str, ch_order: int, les_order: int, lesson_title: str = "") -> str:
    """Render the complete `<aside class="novak-visual-blueprint">` HTML block for a lesson."""
    code = (course_code or "ITSUP").upper()
    ch_i, les_i = int(ch_order), int(les_order)
    arch_title, stages, spec_rows, watch_title, watch_body = get_lesson_blueprint(
        code, ch_i, les_i, lesson_title
    )
    aside_id = f"novak-visual-{code.lower()}-{ch_i}-{les_i}"
    grad_id = f"nvg-{code.lower()}-{ch_i}-{les_i}"
    arrow_id = f"nva-{code.lower()}-{ch_i}-{les_i}"

    # Render 5 stage nodes across viewBox="0 0 760 175"
    # Each box is 132px wide with 16px gap: 5*132 + 4*16 = 660 + 64 = 724 (margin 18px left/right)
    svg_nodes = []
    accents = ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f472b6"]
    for idx, (st_title, st_sub, st_badge) in enumerate(stages[:5]):
        x = 18 + idx * 148
        y = 42
        w, h = 132, 108
        color = accents[idx % len(accents)]
        svg_nodes.append(
            f'<g class="novak-svg-node" transform="translate({x},{y})">'
            f'<rect width="{w}" height="{h}" rx="8" fill="#0f172a" stroke="{color}" stroke-width="1.6"/>'
            f'<rect x="8" y="8" width="{w - 16}" height="20" rx="4" fill="{color}" fill-opacity="0.16"/>'
            f'<text x="{w // 2}" y="22" text-anchor="middle" fill="{color}" font-family="ui-monospace,Consolas,monospace" font-size="9.5" font-weight="700">{escape(st_badge)}</text>'
            f'<text x="{w // 2}" y="54" text-anchor="middle" fill="#f8fafc" font-family="system-ui,-apple-system,sans-serif" font-size="11" font-weight="700">{escape(st_title)}</text>'
            f'<text x="{w // 2}" y="76" text-anchor="middle" fill="#cbd5e1" font-family="system-ui,-apple-system,sans-serif" font-size="9.8">{escape(st_sub)}</text>'
            f'<line x1="14" y1="92" x2="{w - 14}" y2="92" stroke="{color}" stroke-opacity="0.35" stroke-width="1"/>'
            f'<text x="{w // 2}" y="103" text-anchor="middle" fill="#94a3b8" font-family="ui-monospace,Consolas,monospace" font-size="8.5">{ch_i}.{les_i} · S{idx + 1}</text>'
            f'</g>'
        )
        if idx < len(stages[:5]) - 1:
            ax1 = x + w + 2
            ax2 = x + w + 14
            ay = y + h // 2
            svg_nodes.append(
                f'<line x1="{ax1}" y1="{ay}" x2="{ax2}" y2="{ay}" stroke="#38bdf8" stroke-width="2" marker-end="url(#{arrow_id})"/>'
            )

    svg_html = (
        f'<svg viewBox="0 0 760 175" width="100%" role="img" '
        f'aria-label="{escape(arch_title)}" class="novak-arch-svg" '
        f'style="display:block;height:auto;max-width:100%;background:linear-gradient(180deg,#0b1120 0%,#111827 100%);border:1px solid rgba(56,189,248,0.28);border-radius:10px;margin:0.35rem 0 0.45rem 0">'
        f'<defs>'
        f'<linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="#38bdf8" stop-opacity="0.22"/>'
        f'<stop offset="100%" stop-color="#818cf8" stop-opacity="0.08"/>'
        f'</linearGradient>'
        f'<marker id="{arrow_id}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 1 L 9 5 L 0 9 z" fill="#38bdf8"/>'
        f'</marker>'
        f'</defs>'
        f'<rect x="0" y="0" width="760" height="30" rx="10" fill="url(#{grad_id})"/>'
        f'<text x="18" y="20" fill="#e2e8f0" font-family="system-ui,-apple-system,sans-serif" font-size="11.5" font-weight="700">'
        f'NOVAK LMS™ VISUAL ARCHITECTURE · {escape(course_display(code))} {ch_i}.{les_i} — {escape(arch_title)}</text>'
        f'<text x="742" y="20" text-anchor="end" fill="#38bdf8" font-family="ui-monospace,Consolas,monospace" font-size="9.5" font-weight="600">SIGNAL &amp; WORKFLOW MAP</text>'
        + "".join(svg_nodes)
        + f'<text x="18" y="166" fill="#94a3b8" font-family="ui-monospace,Consolas,monospace" font-size="9">'
          f'Flow: {escape(" -> ".join(s[0] for s in stages[:5]))}</text>'
        f'</svg>'
    )

    rows_html = []
    for param, spec, cli, symptom in spec_rows:
        rows_html.append(
            f'<tr>'
            f'<td style="padding:0.45rem 0.6rem;border-bottom:1px solid rgba(148,163,184,0.18);font-weight:600">{escape(param)}</td>'
            f'<td style="padding:0.45rem 0.6rem;border-bottom:1px solid rgba(148,163,184,0.18)">{escape(spec)}</td>'
            f'<td style="padding:0.45rem 0.6rem;border-bottom:1px solid rgba(148,163,184,0.18);font-family:ui-monospace,Consolas,monospace;font-size:0.84rem"><code>{escape(cli)}</code></td>'
            f'<td style="padding:0.45rem 0.6rem;border-bottom:1px solid rgba(148,163,184,0.18)">{escape(symptom)}</td>'
            f'</tr>'
        )

    table_html = (
        f'<div class="novak-spec-table-wrap" style="overflow-x:auto;margin:0.65rem 0">'
        f'<table class="novak-spec-table" style="width:100%;border-collapse:collapse;font-size:0.88rem">'
        f'<thead>'
        f'<tr style="background:rgba(56,189,248,0.1);text-align:left">'
        f'<th style="padding:0.5rem 0.6rem;border-bottom:2px solid rgba(56,189,248,0.35)">Component / Parameter</th>'
        f'<th style="padding:0.5rem 0.6rem;border-bottom:2px solid rgba(56,189,248,0.35)">Technical Specification</th>'
        f'<th style="padding:0.5rem 0.6rem;border-bottom:2px solid rgba(56,189,248,0.35)">Standard / CLI / Path</th>'
        f'<th style="padding:0.5rem 0.6rem;border-bottom:2px solid rgba(56,189,248,0.35)">Failure Symptom &amp; Field Action</th>'
        f'</tr>'
        f'</thead>'
        f'<tbody>{"".join(rows_html)}</tbody>'
        f'</table>'
        f'</div>'
    )

    watchout_html = (
        f'<details class="novak-field-watchout" open style="margin-top:0.65rem;padding:0.6rem 0.85rem;background:rgba(251,191,36,0.09);border-left:4px solid #fbbf24;border-radius:0 8px 8px 0">'
        f'<summary style="cursor:pointer;font-weight:700;font-size:0.9rem">'
        f'Exam &amp; Field Watchout — {escape(watch_title)}</summary>'
        f'<p style="margin:0.45rem 0 0 0;font-size:0.88rem;line-height:1.5">{escape(watch_body)}</p>'
        f'</details>'
    )

    return (
        f'\n<aside class="novak-visual-blueprint" id="{aside_id}" '
        f'aria-label="Visual Architecture &amp; Technical Reference" '
        f'style="margin:0.65rem 0 0.85rem 0;padding:0.75rem 1rem;border:1px solid rgba(56,189,248,0.3);border-radius:12px;background:rgba(15,23,42,0.03)">'
        f'<div class="novak-visual-header" style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.25rem">'
        f'<h4 style="margin:0;font-size:0.95rem;font-weight:700">Visual Architecture &amp; Technical Spec Reference — {escape(arch_title)}</h4>'
        f'<span class="badge" style="font-family:ui-monospace,Consolas,monospace;font-size:0.72rem;padding:0.18rem 0.48rem;border-radius:6px;background:rgba(56,189,248,0.15);color:#0284c7">{escape(course_display(code))} · Ch {ch_i} · Lesson {les_i}</span>'
        f'</div>'
        f'{svg_html}'
        f'<details class="novak-spec-drawer">'
        f'<summary class="novak-spec-drawer-summary"><i class="bi bi-table me-1" aria-hidden="true"></i><strong>Technical Specification Table &amp; Field Watchout</strong> <span class="novak-spec-drawer-hint">Expand 5-row spec reference &amp; field watchout ▾</span></summary>'
        f'<div class="novak-spec-drawer-body pt-2">'
        f'{table_html}'
        f'{watchout_html}'
        f'</div>'
        f'</details>'
        f'</aside>\n'
    )


_ASIDE_EXACT_RE = re.compile(
    r'<aside\s+class="novak-visual-blueprint"[^>]*>.*?</aside>',
    re.DOTALL | re.IGNORECASE,
)
_FIG_EXACT_RE = re.compile(
    r'<figure\s+class="novak-inline-visual"[^>]*>.*?</figure>',
    re.DOTALL | re.IGNORECASE,
)
_BOOT_EXACT_RE = re.compile(
    r'<article\s+class="novak-boot-deep-dive"[^>]*>.*?</article>',
    re.DOTALL | re.IGNORECASE,
)


def strip_lesson_visuals(html: str) -> str:
    """Remove any existing `<aside class="novak-visual-blueprint">`, `<figure class="novak-inline-visual">`, or `<article class="novak-boot-deep-dive">` blocks."""
    if not html:
        return ""
    s = _ASIDE_EXACT_RE.sub("", html)
    s = _FIG_EXACT_RE.sub("", s)
    s = _BOOT_EXACT_RE.sub("", s)
    return s.rstrip()


def inject_lesson_visual(html: str, course_code: str, ch_order: int, les_order: int, lesson_title: str = "") -> str:
    """Idempotently strip any prior visual blocks and inject top blueprint + 3 inline SVG schematics + boot deep dive."""
    from .inline_section_diagrams import (
        render_inline_spec_schematic_svg,
        render_inline_sequence_flow_svg,
        render_inline_triage_tree_svg,
    )
    from .boot_architecture_depth import (
        WINDOWS_BOOT_DEEP_DIVE_HTML,
        LINUX_BOOT_DEEP_DIVE_HTML,
    )

    cleaned = strip_lesson_visuals(html or "")
    code = (course_code or "ITSUP").upper()
    ch_i, les_i = int(ch_order), int(les_order)
    arch_title, stages, spec_rows, watch_title, _watch_body = get_lesson_blueprint(
        code, ch_i, les_i, lesson_title
    )
    aside = render_visual_blueprint(code, ch_i, les_i, lesson_title).strip()
    fig1 = render_inline_spec_schematic_svg(code, ch_i, les_i, arch_title, spec_rows).strip()
    fig2 = render_inline_sequence_flow_svg(code, ch_i, les_i, arch_title, stages, spec_rows).strip()
    fig3 = render_inline_triage_tree_svg(code, ch_i, les_i, arch_title, spec_rows, watch_title).strip()

    boot_blocks = []
    if (code == "ITSUP" and (ch_i, les_i) in ((2, 2), (8, 1), (8, 2), (8, 3))) or (
        code == "CLIENT" and (ch_i, les_i) in ((1, 1), (1, 2), (1, 3))
    ):
        boot_blocks.append(WINDOWS_BOOT_DEEP_DIVE_HTML.strip())
        if (code == "ITSUP" and (ch_i, les_i) in ((2, 2), (8, 1))) or (
            code == "CLIENT" and (ch_i, les_i) == (1, 1)
        ):
            boot_blocks.append(LINUX_BOOT_DEEP_DIVE_HTML.strip())
    elif (code == "ITSUP" and (ch_i, les_i) == (9, 1)) or (
        code == "CLIENT" and (ch_i, les_i) == (2, 1)
    ):
        boot_blocks.append(LINUX_BOOT_DEEP_DIVE_HTML.strip())
        boot_blocks.append(WINDOWS_BOOT_DEEP_DIVE_HTML.strip())
    boot_str = "".join(boot_blocks)

    closes = [m.end() for m in re.finditer(r"</section>", cleaned, flags=re.I)]
    if len(closes) >= 6:
        idx1 = closes[1]
        idx2 = closes[len(closes) // 2]
        idx3 = closes[min(len(closes) - 2, (len(closes) * 3) // 4)]
        out = (
            cleaned[:idx1]
            + fig1
            + boot_str
            + cleaned[idx1:idx2]
            + fig2
            + cleaned[idx2:idx3]
            + fig3
            + cleaned[idx3:]
        )
    else:
        out = cleaned + fig1 + boot_str + fig2 + fig3

    first_sec = re.search(r"<section\b", out, flags=re.I)
    if first_sec:
        s_pos = first_sec.start()
        out = out[:s_pos] + aside + out[s_pos:]
    else:
        out = aside + out
    return out + "\n"


def apply_lesson_visuals(db, Course, Chapter, Lesson) -> int:
    """Idempotently inject visual architecture blueprints & spec tables into all 115 lessons.

    Works with SQLAlchemy `db` session and models (`Course`, `Chapter`/`Module`, `Lesson`).
    Returns the total number of lessons updated (115 across ITSUP, NETOPS, CLIENT).
    """
    count = 0
    courses = Course.query.filter(Course.code.in_(("ITSUP", "NETOPS", "CLIENT"))).order_by(Course.id).all()
    ch_order_attr = getattr(Chapter, "order", None) or getattr(Chapter, "order_index", None)
    les_order_attr = getattr(Lesson, "order", None) or getattr(Lesson, "order_index", None)

    for course in courses:
        q_ch = Chapter.query.filter_by(course_id=course.id)
        if ch_order_attr is not None:
            q_ch = q_ch.order_by(ch_order_attr)
        chapters = q_ch.all()
        for ch in chapters:
            ch_num = getattr(ch, "order", None)
            if ch_num is None:
                ch_num = getattr(ch, "order_index", 1)
            fk_field = "module_id" if hasattr(Lesson, "module_id") else "chapter_id"
            q_les = Lesson.query.filter_by(**{fk_field: ch.id})
            if les_order_attr is not None:
                q_les = q_les.order_by(les_order_attr)
            lessons = q_les.all()
            for les in lessons:
                les_num = getattr(les, "order", None)
                if les_num is None:
                    les_num = getattr(les, "order_index", 1)
                les.content = inject_lesson_visual(
                    les.content or "",
                    course.code,
                    int(ch_num),
                    int(les_num),
                    les.title or "",
                )
                count += 1
    db.session.commit()
    return count


def apply_lesson_visuals_to_packs(pack, course: str = "ITSUP") -> int:
    """Idempotently inject visual architecture blueprints & spec tables into an assembled course pack list."""
    count = 0
    for ch in pack:
        ch_order = int(ch.get("order") or 1)
        for idx, les in enumerate(ch.get("lessons", []), start=1):
            les_order = int(les.get("order") or idx)
            les["html"] = inject_lesson_visual(
                les.get("html") or "",
                course,
                ch_order,
                les_order,
                les.get("title") or "",
            )
            count += 1
    return count
