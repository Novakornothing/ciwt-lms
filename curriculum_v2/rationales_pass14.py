"""Pass 14: full rationales for ITSUP chapter-check items whose rationale was only a section reference (or a
section reference plus a few words). Each explains why the key is right and why the distractors fail, using the
facts already taught in the cited lessons; the original section pointer is kept at the end ("See …").
Keys and options are unchanged. Written by Grok Bot; pending SME review like the rest of the item review.
Merged into curriculum_v2.item_review.REVIEW only where an entry has no rationale of its own."""

RATIONALE = {
    # ---- chapter 3
    'Q3.1': 'list disk only shows the disks and their numbers, so it changes nothing. clean, delete partition and an unticketed convert on the OS disk all destroy data; in this block you list, read and exit. See 3.1 / 2.6.',
    'Q3.4': 'A PSU is a sealed field-replaceable unit: its capacitors can hold a dangerous charge after it is unplugged, so the fix is to replace the whole unit. Unplugging data cables or “discharging” it does not make opening it safe. See 3.3 / 1.2.',
    # ---- chapter 4
    'Q4.1': 'An adapter rated well below what the laptop expects cannot supply full power, so the laptop charges slowly or not at all under load and throttles the CPU. It does not improve thermals or boost clocks, and it does not damage files. Read both labels. See 4.1.',
    # ---- chapter 6
    'Q6.9': 'Deleting a snapshot changes (merges) the VM’s disk chain, so it is a change that belongs to the VM’s owner. Age, slowness or taking a new snapshot first do not give you that authority. See 6.4 / 1.3.',
    # ---- chapter 7
    'Q7.1': 'A user’s diagnosis is a clue, not evidence. Identify the problem and test the lease and IP path first; only if addresses work but names fail is DNS the domain. Urgency or a VM does not change the order. See 7.1 / 5.3.',
    'Q7.5': 'Pinging a public address proves the local network and Internet path work. If mail is down for the whole tenant, the shared factor is the SaaS service, so it goes to the vendor. Disks, batteries and PSUs would affect one device, not every user. See 7.2 / 6.2.',
    'Q7.6': 'Reaching the address proves routing works; failing by name points to name resolution (DNS). A display cable, RAID level or power fault would not let the IP ping succeed while the name fails. See 7.2 / 5.3.',
    'Q7.7': 'The last line of a handoff should name the next action: who owns it or the command to run next. A password never goes in a ticket, “look into it” gives no direction, and remarks about the user are not evidence. See 7.3.',
    'Q7.8': 'A note is evidence another technician will act on, so measured results and guesses must be kept apart: label a guess as a guess or leave it out. Writing guesses as results or as the root cause sends the next person the wrong way. See 7.3 / 1.3.',
    # ---- chapter 8
    'Q8.0': 'Inventory comes first: the device name, Windows edition and which disk is which. Without it you cannot plan any install. Typing clean, turning off the firewall or deleting someone else’s snapshots are destructive or unsafe changes. See 8.1 / 2.6.',
    'Q8.1': 'Long beeps or a MEM code with no video is a POST memory fault, which happens before Windows loads, so reinstalling Windows cannot fix it. Check and reseat memory first. See 8.1 / 2.5.',
    'Q8.2': 'A clean install wipes the OS volume and starts again. An in-place upgrade or repair reinstalls Windows while trying to keep apps, files and settings. Both are changes that need a ticket, and they are not the same process. See 8.1.',
    'Q8.3': 'A pending or failed update can restart the PC repeatedly, so Update history is evidence for a reboot loop and a reason to plan a change window. Updates do cause restarts, and none of this justifies turning Defender off or blaming the board. See 8.2.',
    'Q8.4': 'The accounts lab teaches you to check who is signed in, and with which account, before you change anything. Resetting phones, turning off MDM or wiping a work profile are changes made before you know whose account you are touching. See 8.2 / 4.2.',
    'Q8.7': 'The firewall profile stays on. Turning it off for a game launcher removes protection for the whole device; an approved rule or exception is the owner’s decision. Admin rights or a snapshot do not make it acceptable. See 8.3 / 5.2 / 1.4.',
    'Q8.9': 'The chapter 8 bar is evidence without damage: no image, no disabled Defender, and the next step written down. Turning the firewall off, deleting another host’s snapshot or imaging without list disk are the habits the chapter rules out. See 8.4.',
    # ---- chapter 9
    'Q9.0': 'On an unfamiliar Linux machine, start the same way as on Windows: who you are (whoami), where you are (hostname, pwd) and its address (ip a). Defender, diskpart and formatting a disk are Windows-only or destructive and come nowhere near first. See 9.1 / 2.6.',
    'Q9.2': 'ip a (ip address show) lists each interface with its addresses and state, much like ipconfig /all. ls lists files, notepad is a Windows editor, and diskpart clean is a destructive Windows disk command. See 9.1.',
    'Q9.3': 'A mail failure on a managed Mac could be the radio, the tenant or MDM, and a wipe destroys evidence and data without testing any of them. Isolate first. A swollen battery is a safety stop, and FileVault is not something to dodge. See 9.2 / 4.2.',
    'Q9.4': 'A swollen lithium-ion battery is a fire risk: stop using and charging the device and follow the battery-handling procedure. Charging, prying or reinstalling the OS all make the hazard worse or ignore it. See 9.2.',
    'Q9.5': 'Access the user has never had is new entitlement, so it is a service request. Nothing is broken, so it is not break/fix or a security incident, and a clean install would change nothing. See 9.3 / 1.1.',
    'Q9.6': 'A password never goes in a ticket on any platform: tickets are read by many people and kept for a long time. Linux or macOS makes no difference. See 9.3 / 1.4.',
    'Q9.7': 'About This Mac shows the model, chip, memory and macOS version, and Settings → System → About shows the same identity facts on Windows. Installed apps, Windows Update and Your info show other things. See 9.2.',
    'Q9.8': 'If another PC can open the share and this Mac has never had access, nothing is broken: the Mac’s user needs the access granted. Reinstalling macOS, disabling the firewall or replacing the NIC treat a request as a fault. See 9.4.',
    'Q9.9': 'The chapter 9 bar is a note that names the operating system, the signed-in user and whether this is a request or break/fix. Running mkfs, wiping in the hallway or recording the root password are the failures the chapter rules out. See 9.4.',
    # ---- chapter 10
    'Q10.0': 'Read the firewall profile as evidence (which profile is active and whether it is on), but do not turn it off. That holds for games, after malware and on every platform. See 10.1 / 8.3.',
    'Q10.1': 'A shared admin password on a monitor gives anyone in the room privileged access that cannot be traced to a person. A long password or a locked room does not fix that, and shared PCs use proper accounts instead. See 10.1.',
    'Q10.2': 'Mail sent as the user that they did not write suggests their account is compromised, so it is a security incident. A service request, an Outlook profile fault or a change request would all leave the attacker in the account. See 10.2 / 1.1.',
    'Q10.3': 'Defender stays on. Pausing it, even briefly or for a “known” cleaner, lets malware act and destroys evidence. Malware handling follows the shop’s incident process, not a third-party cleaner. See 10.2.',
    'Q10.4': 'Support contains the device per the shop’s process, records the facts and escalates to the incident team. Wiping the disk destroys evidence, investigating alone is not support’s role, and posting a password spreads the compromise. See 10.2.',
    'Q10.5': 'A user’s password is never recorded anywhere you control: not the ticket, chat, a screen or a note. If a reset is needed, use the approved reset path. See 10.3.',
    'Q10.6': 'Patch state is part of basic security hygiene, so read Windows Update as evidence on every ticket. It matters on clients as well as servers, and it is never a reason to turn off Defender. See 10.3 / 8.2.',
    'Q10.7': 'If the user did not open the phish, record the report and confirm they did not enter any credentials; then it can be reported and removed. Reimaging, turning off the firewall or scolding the user add risk and discourage reporting. See 10.4.',
    'Q10.8': 'A password typed into a phishing page means the account is compromised: treat it as an incident and reset through the approved path (with security), then revoke sessions and check MFA and mailbox rules. A lecture or doing nothing leaves the attacker in. See 10.4.',
    'Q10.9': 'The chapter 10 bar is a factual note with no password in it, and Defender left on. Recording a password, pausing Defender for a cleaner or leaving the firewall off are the failures the chapter rules out. See 10.4.',
    # ---- chapter 11
    'Q11.0': 'If only Outlook fails while Word on the same PC and the next desk both work, the scope is one app on one PC. That rules out a floor-wide incident and a power fault, and a reimage is far too big a change. See 11.1.',
    'Q11.1': 'Copy the exact error text into the ticket: it can be searched, matched to known issues and repeated by the next technician. Memory, paraphrase or leaving it out lose the detail that identifies the fault. See 11.1.',
    'Q11.2': 'Pinging the server’s IP proves the network path; failing by name points to DNS. A failing disk, the battery or the Office installation would not explain IP working while the name fails. See 11.2 / 5.3.',
    'Q11.4': 'Use the least disruptive fix first: an app repair or in-place upgrade keeps apps and data. A clean image, a factory reset or a new disk are bigger changes for when repair has failed and the user’s data is backed up. See 11.3 / 8.1.',
    'Q11.5': 'A rebuild destroys the OS volume, so it needs a tested backup, an approved change ticket and list disk to confirm the right disk. A verbal OK, turning the firewall off or a reboot do not protect the user’s data. See 11.3.',
    'Q11.6': 'One crashing app is isolated first: repair or reset it, or try another profile. A clean image throws away the evidence and the user’s setup for a problem that may be in one app, whatever the platform or delivery. See 11.3.',
    'Q11.7': 'Gather evidence before restarting: inventory, Update state, services and processes, then time the logon stages. Repeated reboots, a clean image or a disk wipe change things before you know the cause. See 11.4.',
    'Q11.8': 'A reboot changes the system state and clears volatile evidence (processes, memory, connections), so in this course it is a change: note it and why. It is not a backup and it is not harmless. See 11.4 / 8.3.',
    'Q11.9': 'The chapter 11 bar is one theory and one next test, with no reimage. Reimaging to save time, running diskpart on a SaaS problem or writing a password in the ticket are the failures the chapter rules out. See 11.4.',
    # ---- chapter 12
    'Q12.0': 'Adding a production DNS record outside the agreed window and against policy is a change: it needs a request, approval and a backout plan. It is not a repair, and policy says it is not optional or always allowed. See 12.1 / 1.3.',
    'Q12.1': 'Reseating RAM restores a part to working order, so it is a repair rather than a change that needs CAB approval. Still record it, because the next technician needs to know it was done. See 12.1.',
    'Q12.2': 'A password never goes in the ticket, even if the user agrees or the ticket is private: tickets are widely read and kept. The next technician uses the approved reset path. See 12.2.',
    'Q12.3': 'Refuse unsafe access politely and offer the approved path, so the user still gets help. Ignoring the request, disabling the firewall or sharing an admin account create the risks the policy is there to prevent. See 12.2 / 1.4.',
    'Q12.4': 'RAID keeps a volume running through a disk failure, and a snapshot is a point-in-time state on the same system; neither is a separate off-site copy. Only a backup kept elsewhere protects against site loss, deletion or ransomware. See 12.3 / 3.2 / 6.3.',
    'Q12.5': 'RAID 5 copies the encrypted files across the array, so it protects against a failed disk, not ransomware. A snapshot on the same box can be encrypted too. Restore from a backup taken before the attack. See 12.3.',
    'Q12.6': 'Ask when the last good backup was taken before any destructive step, while you can still stop. Asking after a wipe is too late, and it matters for every device, not just servers. See 12.3.',
    'Q12.7': 'A memory beep code is a hardware/POST memory fault, so the hw-board / memory lab family fits. SaaS reimaging, the print path and MDM wipes belong to other domains. See 12.4 / 2.5.',
    'Q12.8': 'A good ipconfig shows the local network works; if tenant mail is down, the fault is with the SaaS vendor or tenant. Reimaging, diskpart clean or opening the PSU change the local device and cannot fix a cloud service. See 12.4 / 6.2.',
    'Q12.9': 'The chapter 12 bar is a note from which a peer can tell the domain, with every safety stop held. A listed password, a firewall left off or unlabelled mixed domains are the failures the chapter rules out. See 12.4.',
    # ---- chapter 13
    'Q13.0': 'Chapter 13 is practice: lab repetitions of skills already taught in the earlier chapters. It introduces no new theory, it is required rather than optional, and it is not a vendor exam. See 13 overview.',
    'Q13.1': 'Inventory the lab VM (name, edition, disks, network) before changing anything, so you can tell what changed. Deleting host snapshots, clean and disabling Defender are destructive or unsafe. See 13.1 / 2.6.',
    'Q13.2': 'ipconfig /all output is evidence of what the PC thought its network settings were at that time, so paste it into the ticket with the command. Keeping it in private notes or leaving it out loses that record, and it never goes in a password field. See 13.2 / 5.1.',
    'Q13.3': 'ipconfig /release and /renew drop and re-request the DHCP lease. Use them when the lease is the fault domain, and record the result. They are not a reboot substitute, a clean install or a RAID rebuild. See 13.3.',
    'Q13.4': 'The broken-name-resolution capstone uses the DNS-break lab and the full-triage lab. diskpart clean is never practised, and the other pairs belong to different domains (settings views, hardware). See 13.4 / 5.5.',
    'Q13.5': 'The firewall stays on during the name-resolution labs, as in every chapter. DNS faults are found with lease, IP and name tests, not by removing protection. See 13.4.',
    'Q13.6': 'The settings-paths lab drills the Windows views used as evidence: About, Ethernet, Update, Accounts and Services. PSU internals, deleting Hyper-V snapshots and printer firmware are outside it, or unsafe. See 13.5.',
    'Q13.7': 'List processes before you reboot, because a reboot clears the running processes you are trying to see (8.3: a reboot is a change). After a reboot the evidence is gone, and this applies on Windows too. See 13.6 / 8.3.',
    'Q13.8': 'netsh interface ipv4 show config shows the same lease facts as ipconfig (address, gateway, DNS, DHCP state) in another format, which is useful for cross-checking. It does not show snapshots, the DHCP server’s scope or another PC. See 13.6.',
    'Q13.9': 'Chapter 13 is passed when the labs are submitted and the notes still meet the Block 1 standard: facts, tests and the next step. A recorded password, diskpart clean or a firewall left off fail it. See 13.6.',
}
