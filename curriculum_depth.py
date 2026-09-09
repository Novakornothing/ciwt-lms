"""Long-form teach sections appended to every ITSUP lesson.
Original CIWT schoolhouse prose. Applied after raised_bar.
"""

def _box(title, body):
    return f'<section class="sublesson depth"><h3>{title}</h3>\n{body}\n</section>\n'


DEPTH = {}


def add(ch, les, title, body):
    DEPTH.setdefault((ch, les), []).append(_box(title, body))


# ----- Chapter 1 -----
add(1, 1, "What this job actually is", """
<p>You are paid to restore a required outcome, not to look busy on a PC. The outcome is whatever the user must do again: send the report, badge the door, print the watchbill. Hardware, software, and networks are tools you use when they sit on the path to that outcome.</p>
<p>Three kinds of work show up in the same queue and they are not interchangeable. A <strong>service request</strong> is something the user never had (a share, a mailbox, a software title). <strong>Break/fix</strong> is something that used to work and does not. An <strong>incident</strong> is impact beyond one desk — many users, safety, security, or a service the shop has already labeled critical. If you treat a first-time access ask as a broken NIC you will waste an hour and still leave them without the share.</p>
<p>Impact is a count plus a consequence, not a feeling. “High” with no number is not a ticket. “Fourteen users in Bldg 3 cannot badge, mid-watch turnover in 20 minutes” is a ticket.</p>
""")
add(1, 1, "Worked contacts", """
<p><strong>A.</strong> “I need the budget folder. I never had it.” Service request. Check entitlement. Do not reset a password to “make the share appear.”</p>
<p><strong>B.</strong> “Outlook loops my password since 0700. Next desk is fine.” Break/fix, impact one, stay with it unless you lack account tools.</p>
<p><strong>C.</strong> “Half the quarterdeck badges failed after lunch. Reader is warm.” Incident, impact many, escalate. Heat plus access control is not a solo swap.</p>
<p><strong>D.</strong> Unknown caller wants a reset “right now” and cannot complete the shop identity script. Stop. Urgency is not identity.</p>
""")
add(1, 1, "Identity before any reset", """
<p>Every shop has a script: employee number, last four, callback on a listed number, badge in hand, manager on the line. You use the script even when the voice is friendly. A password reset is a privileged change. If you skip identity you have just handed an account to a stranger and written that fact into the ticket history.</p>
<p>Write what you used to verify, not the secret itself. “Verified via callback to listed desk 555-0142” is enough. Never write the new password.</p>
""")
add(1, 2, "Why the wall unplug matters", """
<p>The rocker on the PSU is not the same as the wall. Power supplies can keep capacitors charged after the rocker is off. You unplug the cord from the <em>wall</em>, wait, then open. The ESD strap goes on bare skin and clips to the same ground as the mat or chassis. A strap over a fleece sleeve is jewelry.</p>
<p>You never open a PSU in this course. A swollen capacitor, a burn smell, or a shock from a strip is an incident: stop, keep people away, escalate. That is the same label as a building-wide badge failure — safety first, parts second.</p>
""")
add(1, 2, "Lift, path, and the bench", """
<p>Towers and monitors have edges and cords that catch boots. Clear the path before you pick anything up. Two people on a full tower if it is awkward. Do not rest a chassis on a chair that rolls. The bench is for open work; the floor is for boxes. If you cannot name where the wall cord is before you lift, you are not ready to lift.</p>
""")
add(1, 3, "Ticket B versus Ticket A", """
<p>Ticket A: “VPN broken.” The next watch learns nothing. Ticket B: client version, error 809, LAN ping OK, gateway ping fails, started after the weekend update, user is on hotel Wi-Fi. Ticket B lets someone else continue at 0200 without calling you.</p>
<p>Every test is a pair: action → result. “Pinged 10.20.30.1 — 4/4 1 ms.” “Opened cached mode — still loops.” A test without a result is a slogan.</p>
<p>A <strong>repair</strong> puts a known-good state back. A <strong>change</strong> introduces something new: a DNS record, an image, a firmware setting, an AP password. Changes use the shop process even when they take two minutes. “I just added it” is how production mail dies after 1500.</p>
""")
add(1, 4, "Two audiences", """
<p>The user needs the outcome, the time, and what you need from them. They do not need DHCP or APIPA. The ticket needs facts. The lead on the phone needs a judgment call, not a novel. If those three channels get mixed, someone will paste a password into chat “so the next guy can log in.”</p>
<p>Refuse unsafe access without becoming the enemy. “I cannot reset that from this call. Here is the approved path” is a complete sentence. Document the refusal as a fact, not a fight.</p>
""")
add(1, 5, "How the live lab is scored", """
<p>The card is half the badges down after lunch and a warm reader. Commands the lab accepts, in order: <code>show ticket</code>, <code>classify incident</code>, <code>impact many</code>, <code>escalate yes</code>, a <code>note</code> that names heat and does not open the panel, then <code>submit</code>. <code>classify break-fix</code> or <code>impact 1</code> fails. Opening the reader in the note fails. That is the same judgment you will use on a real quarterdeck.</p>
""")

# ----- Chapter 2 -----
add(2, 1, "What a motherboard is for", """
<p>The board is the backplane that lets CPU, memory, storage, and expansion work as one system. Form factor is the size and mounting pattern, not the brand painted on the box. ATX, microATX, and Mini-ITX trade expansion slots, RAM slots, and case clearance. A “small office tower” that is 9.6 × 9.6 in is microATX on this course card — measure the board, do not trust the Amazon title.</p>
<p>Chipset and socket decide which CPU family fits. You do not force a chip. A cocked CPU in an LGA socket is a destroyed CPU and sometimes a destroyed socket. Seat, then latch. If it does not drop, you have the wrong orientation or the wrong socket.</p>
""")
add(2, 2, "Firmware is not Windows", """
<p>UEFI runs before the operating system. It checks hardware (POST) and then starts a bootloader. A wrong boot order looks like a “dead Windows.” Secure Boot means firmware will start only a signed bootloader. That is good against some malware and also a reason a shop USB installer will not start until you temporarily allow it — which is a change, with a rollback.</p>
<p>You change one firmware setting, save, watch the next boot, write action → result. You do not toggle six options because a forum said so.</p>
""")
add(2, 3, "CPU, cooler, header", """
<p>The cooler must sit flat on the heat spreader with a thin film of paste — not a glob, not bare metal. The fan cable goes on the CPU_FAN header (or whatever this board’s firmware uses for the CPU cooler). Zero RPM in firmware after a “successful” install is often the wrong header, not a dead fan. Airflow in the case is intake/exhaust, not a sticker on the side panel.</p>
""")
add(2, 4, "Memory generation and channels", """
<p>DDR4 and DDR5 are not interchangeable. The notch is in a different place on purpose. Filing a notch is how you kill a board. Dual-channel needs the pair in the slots the manual paints as a channel — usually the second and fourth, not “whatever is empty.” If About shows less RAM than the DIMM count, reseat and check firmware before you image.</p>
""")
add(2, 5, "POST order", """
<p>POST is firmware talking about hardware before Windows exists. A memory LED plus long beeps plus no video is a memory problem even if the monitor cable is loose in your imagination. Display isolation starts only after POST is OK. Power isolation starts when there is no twitch and no LED. Learn those three neighborhoods so you do not replace a GPU because RAM is unseated.</p>
<p>On the hw-board lab this course card is microATX, LGA1700, DDR5, NVMe in the short slot, POST memory. Type those words. Do not invent a 2011 socket.</p>
""")
add(2, 6, "Inventory before you change the box", """
<p>Name, edition, build, RAM the OS sees, disk list. <code>list disk</code> only — never <code>clean</code> in this course. If About and the chassis disagree, you have a seating or firmware problem, not an image problem. Write the inventory in the ticket so the next person does not guess which handle is the OS disk.</p>
""")

# ----- Chapter 3 -----
add(3, 1, "M.2 is the slot, NVMe is the protocol", """
<p>An M.2 stick can be SATA or NVMe. Calling every short card “NVMe” is how you order the wrong part. SATA SSD uses the SATA path; NVMe typically uses PCIe and is faster on that path. An HDD is still a spinning disk with different failure modes (click, not-ready) than a NAND device that dies silent.</p>
<p><code>list disk</code> shows handles and sizes. That is how you know which disk is which. Destructive diskpart verbs are out of scope on purpose.</p>
""")
add(3, 2, "RAID is not backup", """
<p>RAID 0 stripes for speed and dies completely if one disk dies. RAID 1 mirrors. RAID 5 needs three disks and pays a rebuild tax when a disk fails. None of them undo a user delete or ransomware. Backup is a second copy you can restore. If the only copy lives on the same array, you do not have a backup.</p>
""")
add(3, 3, "Power isolation", """
<p>No fan twitch, no LED: wall outlet, PSU switch, 24-pin, CPU 8-pin. A known-good cord is a cheaper test than a new PSU. The PSU is a sealed FRU. You do not go inside it. Hot receptacle or burn smell while you swap is an incident — same stop rule as Chapter 1.2.</p>
""")
add(3, 4, "Display path after POST OK", """
<p>Cable, input on the panel (HDMI vs DisplayPort), brightness, then GPU seating. A dark panel during MEM beeps is still POST memory. Do not start the display order until firmware has said the machine is trying to boot.</p>
""")
add(3, 5, "Unstable workstation capstone", """
<p>Pick one domain. Change one thing. Write the result. If you reseat RAM, swap a PSU, and reimage in the same hour you will never know what worked. The capstone note should read like Ticket B from 1.3.</p>
""")

# ----- Chapter 4 -----
add(4, 1, "FRU identity and batteries", """
<p>Laptops use parts that look alike and are not. Service tag plus panel code beats “a 15-inch Dell screen.” A swollen pack lifts the trackpad or the chassis. Stop. Do not pry a sealed pack in class. Do not keep charging it. Shop battery procedure, then a ticket that says stop.</p>
<p>A 65 W brick on a chassis that expects 130 W looks like a slow, throttled mystery OS. Read both labels.</p>
""")
add(4, 2, "Radios and MDM", """
<p>Mail works on cellular and fails on building Wi-Fi: the radio works; the building path does not. Do not factory-reset a managed phone to “clear it.” MDM / work profile is shop property. Sidestepping it to install an app is a change you do not get to make in the hallway. gui-accounts on the Windows bench is the same question: whose account are you touching?</p>
""")
add(4, 3, "Print path", """
<p>Order: app → spooler / queue → driver / port → USB or network → device panel. One user, one app: start at the app. One PC, every app: spooler and driver; the next desk is the control. Whole floor queued: device panel and print server — do not rebuild the first PC’s driver. Panel says paper out or jam: device first.</p>
""")
add(4, 4, "Portable intake", """
<p>The note must tell the next person whether to stop for a battery, pull a driver, or work the panel. That is the same Block 1 standard on a laptop-shaped ticket.</p>
""")

# ----- Chapter 5 -----
add(5, 1, "Address, door, name", """
<p>IPv4 address is who this host is on the LAN. Mask says which bits are the network. Gateway is the door off this LAN. DNS turns names people type into addresses stacks route. APIPA (169.254.x.x) means no usable DHCP lease. Do not start a DNS lecture on an APIPA box.</p>
<p>ipconfig /all is the first evidence line on a client ticket: hostname, IPv4, mask, gateway, DNS, DHCP enabled or not.</p>
""")
add(5, 2, "Ports are doors on a host", """
<p>Port 53 is DNS. 80/443 web. 25/587 mail. 3389 RDP. The number changes the first test. Ping to an IP only proves ICMP to that host, not that the mail door is open. Outlook looping while ping to the mail server IP works is not a dead NIC.</p>
""")
add(5, 3, "Isolation order", """
<p>Identity → link lights / Ethernet status → ipconfig → ping gateway IP → ping a name → nslookup → only then flush or renew. Flushing DNS on APIPA skips a layer. Disabling the firewall “to test” is not a test in this course; it is a hole.</p>
""")
add(5, 4, "SOHO wireless", """
<p>Hiding the SSID does not hide the radio. Fix the admin password, guest isolation, and who is allowed on the LAN. Changing a shared AP password is a change. Write what you set and how to undo it.</p>
""")
add(5, 5, "Full triage lab", """
<p>win-full-triage wants identity, IP tests, name tests, and a written action → result. Skip ping-IP and jump to flushdns and you fail the habit even if the box “works.” Firewall stays on.</p>
""")

# ----- Chapter 6 -----
add(6, 1, "Host versus guest", """
<p>The Windows you type in on the training bench may already be a guest (CIWT-W11-07). The host is the machine or cluster that holds the files. If the host datastore is full or the host NIC is down, every guest looks sick. Inventory the guest first. If the guest looks healthy and five guests failed together, the next person is the host owner — not five NIC replacements.</p>
""")
add(6, 2, "What you may touch", """
<p>SaaS: account, license, client. You do not reimage a laptop because Outlook 365 is yellow for the whole tenant. IaaS: you still own the guest OS and use Chapters 2–5 inside it. PaaS: you own the app path, not the platform OS. Write the tenant name and whether other users fail.</p>
""")
add(6, 3, "Snapshots and virtual cables", """
<p>A snapshot is a bookmark next to the live disks. It is not a second copy in another building. Week-old snapshot chains fill the datastore and slow every guest. A virtual NIC can be disconnected in the hypervisor while the guest “has a NIC.” Isolate inside the guest first (ipconfig). If the guest has no adapter or APIPA and the host network is up, hand the host owner a vNIC / port-group / uplink question.</p>
""")
add(6, 4, "Slow VM note", """
<p>Guest facts (name, RAM the guest sees) go first. “Snapshot chain on host?” is labeled guess. You do not delete a snapshot you do not own.</p>
""")

# ----- Chapter 7 -----
add(7, 1, "The seven words", """
<p>Identify → probable cause → test → plan → change one thing → verify the user outcome → document. The user saying “it’s DNS” is not identify. Identify is who, what outcome, how many, safety stop. Then the cheapest test that can kill a theory.</p>
""")
add(7, 2, "Fault domains you already know", """
<p>Safety. Power / POST. Display after POST OK. OS / disk. Address. Name. Vendor / SaaS. Work inside one neighborhood until evidence moves you. Formatting a disk because tenant mail is down is crossing domains.</p>
""")
add(7, 3, "Handoff", """
<p>A handoff that omits tests sends the next person to zero. Last line is a person or a command, not “look into it.” Guesses stay labeled.</p>
""")
add(7, 4, "Two drills", """
<p>MEM beep: stay in POST (hw-board). Name fail after IP works: win-dns-break or full triage. diskpart on a SaaS outage fails the pass bar on purpose.</p>
""")

# ----- Chapter 8 -----
add(8, 1, "Clean versus in-place", """
<p>Clean wipes the OS volume. In-place tries to keep apps and files. Both are changes. Neither is step one on a box that never left POST. In-place when the OS boots and the component store or a feature update is the problem. Clean when the volume is trash and backup is confirmed.</p>
""")
add(8, 2, "Baseline is a description", """
<p>Who is signed in, whether Update is pending or failed, whether the box has a real address. Collect that before you “tune.” gui-update, gui-accounts, gui-ethernet are three views of the same PC.</p>
""")
add(8, 3, "Services are background jobs", """
<p>DHCP Client, DNS Client, Defender Running. If DHCP Client is stopped, ipconfig looks cursed. Listing processes before a reboot is how you know what you killed. Reboot is a change. Firewall profile is read-only in this course.</p>
""")
add(8, 4, "Failed update capstone", """
<p>OS still logs in. Collect About, Update error, three service states, next window (retry vs in-place vs escalate). No clean. No Defender off.</p>
""")

# ----- Chapter 9 -----
add(9, 1, "Linux inventory cousins", """
<p>whoami / hostnamectl, pwd, ls, ip a, lsblk. Same 2.6 habit, different spelling. sudo is a change with a ticket. mkfs is not a first command. This LMS has no Linux terminal — you learn the map so a real box does not scare you into destructive verbs.</p>
""")
add(9, 2, "A Mac is still a portable", """
<p>About This Mac is gui-about. FileVault and MDM are shop property. Swollen pack is still 4.1. Mail on a managed Mac is radio vs tenant vs enrollment — not a hallway wipe.</p>
""")
add(9, 3, "Shares and accounts", """
<p>Never had the share: request / entitlement, not a NIC. Password stays out of the ticket. Escalate the directory owner when entitlement is the block.</p>
""")
add(9, 4, "Mixed environment note", """
<p>Name the OS, who is signed in, request vs break/fix. Windows next door opening the share does not prove the Mac NIC is dead.</p>
""")

# ----- Chapter 10 -----
add(10, 1, "Daily controls", """
<p>Badge, screen lock, least privilege, who is signed in. Firewall profile stays on. A shared admin password on a monitor is unaccountable privilege.</p>
""")
add(10, 2, "Malware is an incident", """
<p>Contain per shop process. Do not run random cleaners. Do not disable Defender to let a “tool” run. Write facts. Escalate to the IR owner. You are support, not the whole IR team.</p>
""")
add(10, 3, "Hygiene", """
<p>Defender Running, Update read, no secrets in tickets. Patch state is part of the description of the box.</p>
""")
add(10, 4, "Phish follow-up", """
<p>Not opened: record, no shame, confirm no credentials. Password typed: incident plus approved reset. Never put that password in the ticket.</p>
""")

# ----- Chapter 11 -----
add(11, 1, "Scope first", """
<p>One app, one profile, one PC, many PCs. Write the exact error text. One-app crash is not a clean image.</p>
""")
add(11, 2, "Controls", """
<p>Another app, another profile, another PC. If the symptom is “no network in the app,” run Chapter 5 before any Office repair. Ping IP works and ping name fails: DNS domain.</p>
""")
add(11, 3, "Repair before rebuild", """
<p>In-place / repair first. Rebuild only with backup, a change ticket, and list disk first. A single crashing app does not earn a wipe.</p>
""")
add(11, 4, "Slow logon", """
<p>Inventory, Update, services, processes, then one theory. Reboot-loop is not identify. Profile vs network home vs disk vs GPO — pick one and test it.</p>
""")

# ----- Chapter 12 -----
add(12, 1, "Change control", """
<p>Firmware, DNS, image, AP password = changes. Reseat RAM = repair, still documented. A two-minute change that skips the process is still a change.</p>
""")
add(12, 2, "Privacy", """
<p>PII and passwords off hallway talk and tickets. Offer the approved path when you refuse unsafe access.</p>
""")
add(12, 3, "Recovery words", """
<p>Backup ≠ RAID ≠ snapshot. Ask last-backup time before any destructive step. Ransomware on the share is restore, not RAID 5 magic.</p>
""")
add(12, 4, "Integrated ticket", """
<p>MEM beep → hardware / POST. Tenant mail down + good ipconfig → SaaS. Name the domain in the first line of the note so a peer does not open the wrong lab.</p>
""")

# ----- Chapter 13 -----
add(13, 1, "This guest is shop property", """
<p>Inventory before you change the lab VM. No clean. Treat CIWT-W11-07 like a real bench PC that someone else also uses.</p>
""")
add(13, 2, "Evidence lines", """
<p>hostname and ipconfig /all go in the ticket. PowerShell Get-NetIPConfiguration is the same facts with different spelling.</p>
""")
add(13, 3, "Lease cycle", """
<p>Release/renew is for a lease problem, not a personality reboot. Confirm the new address and ping the gateway.</p>
""")
add(13, 4, "Broken name resolution", """
<p>Prove IP, fail name, nslookup, then flush. Same pass bar as 5.5. Firewall on.</p>
""")
add(13, 5, "Settings gym", """
<p>About, Ethernet, Update, Accounts, Services. You should be able to find each path without a screenshot from a forum.</p>
""")
add(13, 6, "Before you reboot", """
<p>List processes. netsh is another view of the same lease. Reboot is a change you can name.</p>
""")

add(3, 1, "When the disk is the ticket", """
<p>OS will not start, inaccessible boot device, Disk Management shows Unknown — those are disk or partition stories. A user who cannot find a file on a healthy volume is not. Write the handle, the size, and whether this is the OS disk before anyone talks about imaging.</p>
""")
add(3, 2, "Rebuild tax", """
<p>A degraded RAID 5 array still serves I/O and also rebuilds. Performance falls. A second disk dying during rebuild loses the volume. That is why RAID is not a place to skip backups.</p>
""")
add(5, 1, "Private ranges you will see", """
<p>10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16 are private. 169.254 is APIPA, not “a private range we use.” A public address on a staff laptop that should be NATed is an address-plan ticket, not a new NIC.</p>
""")
add(5, 3, "What each failed ping means", """
<p>Ping gateway fails plus APIPA: lease/link. Ping gateway fails plus a good address: local LAN or the gateway. Ping gateway works, ping 8.8.8.8 fails: upstream / NAT. Ping IP of the app works, ping the name fails: DNS.</p>
""")
add(7, 1, "Cheap tests first", """
<p>A cheap test kills a theory in one minute: ping, About, a second app, the next desk, a known-good cable. An expensive test takes an image or a part. Start cheap.</p>
""")
add(8, 2, "What pending update does to a ticket", """
<p>A pending feature update explains random reboots. It does not explain MEM beeps. If Update failed with a code, that code belongs in the ticket verbatim.</p>
""")
add(10, 2, "Containment without heroics", """
<p>Isolate on the wire if shop process says so. Do not treat a USB cleaner as IR. Your job is isolate, document, hand off.</p>
""")
add(11, 2, "Profile versus machine", """
<p>Works in another profile on this PC: profile. Fails every profile here, works next desk: machine. Fails every PC: server, license, or network path.</p>
""")
add(12, 1, "Rollback is part of the plan", """
<p>If you cannot say how you undo the change, you do not have a plan. Write the undo in the ticket before you click apply.</p>
""")


def apply_curriculum_depth(pack):
    for ch in pack:
        if not isinstance(ch, dict):
            continue
        ch_no = ch.get("order")
        for les in ch.get("lessons") or []:
            key = (ch_no, les.get("order"))
            extra = DEPTH.get(key) or []
            if extra:
                les["html"] = (les.get("html") or "") + "\n" + "\n".join(extra)
    return pack
