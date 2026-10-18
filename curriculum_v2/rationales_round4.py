"""Content round 4 (Oct 18 2026): full rationales for the last 23 ITSUP chapter-check items whose served rationale was
still a one-line "section + slogan" (for example "1.1 — new access is a request, not a repair."), and one NETOPS item
(NQ5.5) whose distractors gained a misconception tag this round.

Spot-check round 3 measured them: rationale under 90 characters that starts with a section pointer. Pass 15 did not
reach them because they carry their study tip as their rationale. Each rationale below says why the key is right and
why each distractor is wrong, using what the cited lesson teaches; ``SOURCE`` names the primary source (standard,
vendor documentation, NIST/CISA, or the course lesson where the item tests the course's own lab or procedure) and is
appended to the served rationale. The original section pointer is kept ("See …"). Keys, options and stems are
unchanged. Written by Grok Bot, not an SME: every item that takes one is marked Pending SME review.

Applied by curriculum_v2.item_review.review_check (ITSUP, and CLIENT where it reuses ITSUP checks) and by
curriculum_v2.netops_checks.netops_quiz_payload (NQ5.5), only where the item has no full review rationale."""

STATUS = 'Pending SME review'
FIX = 'rationale rewritten in content round 4 (why the key is right and each distractor wrong); Pending SME review'

RATIONALE = {
    # ---- chapter 1 (ticket classes: lesson 1.1 table "break/fix / service request / incident"; change: lesson 1.3)
    'Q1.0': 'The user never had the budget share, so nothing broke: they are asking for something new, which is a service request (check entitlement and approval, then fulfil). It is not an incident, because no service is interrupted and only one person is asking, and not break/fix, because break/fix means something that used to work. A firmware change has nothing to do with folder access. See 1.1.',
    'Q1.1': 'Half the building locked out of access control is impact beyond one desk on a security system, so the first label is incident: stop, scope and escalate. Break/fix for one reader understates the scope, a service request for new badges asks for something new when the badges worked before, and a paint change ticket has nothing to do with the outage. See 1.1.',
    'Q1.5': 'A shock from a metal strip is a safety event, and the course rule is that shock, heat and burning smells are incidents: stop, keep people away from the equipment and escalate. Ignoring it because the PC boots leaves a live hazard in place, swapping the strip as break/fix treats an electrical fault as a parts job you do alone, and opening the PSU is never done in this course. See 1.2 / 1.5.',
    'Q1.6': 'Adding a production DNS record introduces something new on shared infrastructure, so it is a change and goes through the shop’s change process, which here forbids it after 1500. A repair only restores a known-good state (reseat RAM, replace a failed disk), nothing has broken yet so it is not an incident, and documentation is never optional for work that can affect other people. See 1.3.',
    'Q1.8': 'Half the quarterdeck badges failed and the reader is warm: many people are affected and there is heat on access-control hardware, so the lab answer is classify incident, impact many, escalate yes. “Request, impact 1” treats a failure as a new ask, “break-fix, impact 1” understates both the scope and the heat, and opening the reader panel is the unsafe move the lab fails on. See 1.5.',
    # ---- chapter 2 (hw-board bench card; lessons 2.1–2.5)
    'Q2.0': 'A 9.6 × 9.6 in board is microATX: ATX is 12 × 9.6 in and Mini-ITX is about 6.7 in (170 mm) square, so the board’s size, not the case’s marketing, names the form factor. 1U is not a board form factor at all; it is a rack height (1.75 in) for servers. See 2.1 / hw-board card.',
    'Q2.1': 'The lab command names the socket printed on the board, and this card’s silkscreen says LGA1700, so the command is socket lga1700. AM5 is AMD’s socket and LGA2011 an older Intel workstation/server socket, so either would be a guess that contradicts the card; form-factor takes a board size (microatx, atx, mini-itx), not a socket name. See 2.3.',
    'Q2.2': 'The DIMM label says DDR5, and memory generation is typed with the memory command: memory ddr5. memory ddr4 names the other generation, whose key notch is in a different place so it would not even fit the slot; storage takes the drive interface (nvme or sata) and post takes the POST result, so neither accepts a memory type. See 2.4.',
    'Q2.4': 'The debug LED reads MEM and the board gives long beeps, and both point at memory during POST, so the lab command is post memory. No video is a consequence: the board stops before it ever sends a picture, so post display chases the screen the LED has already ruled out. post power fits a board with no fans and no LEDs, which is not this one, and post ok would mean POST passed. See 2.5.',
    'Q2.5': 'UEFI firmware runs first, before any operating system: it runs POST to check the CPU, memory and disks, then starts the bootloader that loads Windows. Device drivers are loaded by Windows itself after firmware has handed over, Safe Mode is a Windows startup option, and background services run inside Windows. That is why a wrong boot order in firmware can look like a dead Windows. See 2.2.',
    'Q2.6': 'Secure Boot means the firmware will start only a bootloader whose signature it trusts. That blocks some bootkits, and it is also why an unsigned shop USB stick will not start. It does not make the disk faster, it does not replace antivirus once Windows is running, and it does not encrypt anything: drive encryption is BitLocker’s job. See 2.2.',
    'Q2.8': 'The CPU cooler’s fan goes on CPU_FAN, because that is the header the firmware monitors (and often warns or shuts down on) for CPU cooling. On SYS_FAN the fan may spin, but the CPU reading shows zero RPM, which is the classic “dead fan” that is really the wrong header. The USB 2.0 and front-panel LED headers are not fan headers at all. See 2.3.',
    # ---- chapter 4
    'Q4.0': 'A raised trackpad on a hot laptop is the sign of a swollen lithium-ion battery, which is a safety incident: stop, do not charge, press or pry it, move it away from anything flammable and follow the battery procedure. Prying the pack out risks puncturing it and starting a fire, charging adds energy to a damaged cell, and reimaging Windows is software work on a physical hazard. See 4.1.',
    'Q4.2': 'Mail works on cellular, so the phone, its radio and the mail account all work; only the building Wi-Fi path fails, so isolate that path (WLAN, captive portal, proxy). A factory reset, “always” or otherwise, wipes the device and still would not fix the building network. Removing the work profile is the MDM owner’s decision, not a hallway fix, and having MDM installed is a reason not to reset, not a reason to. See 4.2.',
    'Q4.3': 'A work profile or MDM enrolment puts the phone under the organisation’s policy: only the policy owner retires, wipes or changes it, so you do not sidestep it. It is not the user’s personal Apple ID or a personal backup app; those belong to the user. Removing it to install an app breaks compliance and removes company data, which is exactly the change you do not get to make. See 4.2.',
    'Q4.6': 'A print job travels application → Windows print system (spooler and queue) → driver and port → link (USB or network) → device, and you isolate along that path by scope. Starting at the printer panel, or jumping from device and cable back to the app, scrambles the order so you cannot tell which box failed, and “reinstall the driver every time” is a reflex that tests only one box. See 4.3.',
    # ---- chapter 5
    'Q5.7': 'No: a hidden SSID still appears in client probe requests, so it hides nothing from anyone who listens. The controls that matter are a changed admin password, WPA2/WPA3 encryption, a guest network with client isolation and current firmware. MAC filtering does not stop anyone joining, because MAC addresses travel unencrypted and can be copied. Hiding the SSID cannot replace encryption, and disabling DHCP does not stop someone typing a static address. See 5.4.',
    # ---- chapter 6
    'Q6.0': 'A virtual machine is a guest computer made of files (virtual disks and configuration) that runs on a host’s hypervisor, so the Windows on this bench may itself be a guest. A remote desktop session is only a remote view of some computer, physical or virtual. A rack server is physical hardware that may host VMs, and a backup copy of a disk does not run. See 6.1.',
    'Q6.1': 'Five guests on the same host losing the network together share one thing: the host’s virtual switch or its physical uplink, so start there. Replacing five NICs, reinstalling five copies of Windows or changing Secure Boot on each guest treats one shared fault as five separate local ones, and none of those touch the virtual network all five depend on. See 6.1.',
    'Q6.6': 'Each snapshot (checkpoint) starts a differencing disk that keeps growing while the VM runs, so week-old chains fill the datastore and slow every guest on it. They do not add free space or speed, they do nothing for RAID performance, and they are not off-site backups: they live on the same storage as the VM and depend on it. Delete or consolidate them through the hypervisor once the change is done. See 6.3.',
    'Q6.7': 'You ran the network checks inside the guest, the guest shows no adapter or an APIPA address and the host network is up, so the fault is in the virtual layer between them: a disconnected vNIC, the wrong port group or the host uplink. That belongs to the hypervisor owner. The printer vendor and “whoever has a screwdriver” have no access to it, and reinstalling the guest OS does not reconnect a virtual adapter. See 6.3.',
    # ---- chapter 7
    'Q7.0': 'The process starts with identify: who is affected, what outcome is missing, how many people and whether there is a safety stop. Without that you cannot form a theory worth testing. Reimaging, flushing DNS and disabling Defender are changes made before anyone knows what the problem is, and closing the ticket after a flush skips verification. The user saying “it’s DNS” is not identification. See 7.1.',
    'Q7.3': 'Verified means the outcome the user called about works again, confirmed by re-running the test that failed, with the user. A voicemail is a message, not a confirmation. A calm Task Manager is supporting evidence about one machine, not the user’s outcome, and an expired SLA timer measures time, not whether anything was fixed. Closing a ticket is not the same as fixing it. See 7.3 / 1.1.',
    # ---- NETOPS (rationale extended because its distractors are now tagged, see misconceptions_round4.py)
    'NQ5.5': 'Accurate, synchronised timestamps let you line up events from many devices in the order they happened during an incident; without NTP every device’s clock drifts and the sequence is guesswork. Central logging does not encrypt the routing table and does nothing for boot time after a power cut. It does not replace SNMP either: syslog carries event messages, while SNMP answers polls for counters and status and sends traps, so the two are used together.',
}

SOURCE = {
    'Q1.0': 'ITIL 4 Service request management practice guide (requests for something new or standard, including access); course 1.1',
    'Q1.1': 'ITIL 4 Incident management practice guide (unplanned interruption of a service; prioritise by impact); course 1.1',
    'Q1.5': 'CompTIA A+ Core 2 (220-1202) operational procedures, electrical safety; course 1.2 / 1.5 stop rule',
    'Q1.6': 'ITIL 4 Change enablement practice guide (a change is any addition, modification or removal that could affect services); course 1.3',
    'Q1.8': 'Course lab ticket-intake (lesson 1.5 command list); ITIL 4 Incident management (impact and escalation)',
    'Q2.0': 'Intel ATX specification v2.2 (12 × 9.6 in) and microATX Motherboard Interface Specification v1.2 (up to 9.6 × 9.6 in); VIA Mini-ITX (170 × 170 mm); EIA-310 rack unit (1U = 1.75 in)',
    'Q2.1': 'Course hw-board bench card (lesson 2.3 lab command list); AMD Socket AM5 quick reference guide (1718-pin LGA)',
    'Q2.2': 'Course hw-board bench card (lesson 2.4 lab command list); JEDEC DDR4 and DDR5 DIMM standards (different key-notch positions)',
    'Q2.4': 'Course hw-board bench card (lesson 2.5 POST table); motherboard vendor manuals (DRAM/MEM debug LED marks a memory fault during POST)',
    'Q2.5': 'UEFI Specification 2.10 (boot services and boot manager run before the OS loader calls ExitBootServices)',
    'Q2.6': 'UEFI Specification 2.10, Secure Boot and Driver Signing; Microsoft Learn, "Secure boot" and "BitLocker overview"',
    'Q2.8': 'Motherboard vendor manuals (connect the CPU cooler fan to CPU_FAN; firmware monitors it and may warn or halt at 0 RPM)',
    'Q4.0': 'U.S. EPA, "Used Lithium-Ion Batteries"; laptop vendor swollen-battery guidance (stop using and charging, do not puncture); course 4.1',
    'Q4.2': 'Microsoft Learn, Intune "Remove devices by using wipe, retire, or manually unenrolling the device"; course 4.2 isolation table',
    'Q4.3': 'Microsoft Learn, Intune device enrolment and compliance policies; Apple Platform Deployment guide (device management and User Enrollment)',
    'Q4.6': 'Microsoft Support, "Fix printer connection and printing problems in Windows"; Microsoft Learn, Print Spooler service; course 4.3',
    'Q5.7': 'CISA, "Home Network Security" guidance (change default admin password, WPA2/WPA3, guest network, updates); Wi-Fi Alliance WPA3 specification',
    'Q6.0': 'NIST SP 800-125, Guide to Security for Full Virtualization Technologies (host, hypervisor, guest OS)',
    'Q6.1': 'Microsoft Learn, Hyper-V virtual switch types (external, internal, private); course 6.1 / 6.3',
    'Q6.6': 'Microsoft Learn, Hyper-V checkpoints (differencing .avhdx disks); Broadcom/VMware KB 1025279, "Best practices for using VMware snapshots" (not backups; do not keep one more than 72 hours)',
    'Q6.7': 'Microsoft Learn, Hyper-V virtual switch and network adapter settings; VMware vSphere networking (port groups, uplinks); course 6.3',
    'Q7.0': 'CompTIA A+ 220-1201 exam objectives, troubleshooting methodology section, step 1 (identify the problem) (a competency standard, not a tested objective in the 220-1200 series)',
    'Q7.3': 'CompTIA A+ 220-1201 exam objectives, troubleshooting methodology section, step 5 (verify full system functionality) (a competency standard, not a tested objective in the 220-1200 series); ITIL 4 Incident management (closure confirmed with the user)',
    'NQ5.5': 'IETF RFC 5905 (NTPv4); RFC 5424 (syslog protocol, timestamps); RFC 3411 (SNMP architecture)',
}


def served(key, base=''):
    """The served rationale for ``key``: the round-4 rationale plus its source, or ``base`` if there is none."""
    r = RATIONALE.get(key)
    if not r:
        return base
    return f'{r} Source: {SOURCE[key]}.'
