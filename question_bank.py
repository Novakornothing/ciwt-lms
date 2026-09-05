"""Knowledge tests — original scenario items for CIWT LMS (not vendor exam content)."""


def _item(text, correct, w1, w2, w3, lo="LO-GEN", lo_text="Core technical knowledge", category="Core Knowledge"):
    return {
        "text": text,
        "options": [w1, w2, w3, correct],
        "correct": correct,
        "lo": lo,
        "lo_text": lo_text,
        "category": category,
    }


def _rotate(items):
    out = []
    for i, q in enumerate(items):
        opts = list(q["options"])
        shift = i % 4
        opts = opts[shift:] + opts[:shift]
        out.append({
            "text": q["text"],
            "options": opts,
            "correct": q["correct"],
            "lo": q.get("lo", "LO-GEN"),
            "lo_text": q.get("lo_text", "Core technical knowledge"),
            "to": q.get("to") or f"{q.get('lo', 'LO-GEN')}: {q.get('lo_text', 'Core technical knowledge')}",
            "category": q.get("category") or "Core Knowledge",
            "explanation": q.get("explanation", ""),
        })
    return out


def _tag(items, lo, lo_text, category=None):
    for q in items:
        q["lo"] = lo
        q["lo_text"] = lo_text
        if category:
            q["category"] = category
    return items


def _ensure_meta(pool):
    for q in pool:
        q.setdefault("category", "Core Knowledge")
        q.setdefault("lo", "LO-GEN")
        q.setdefault("lo_text", "Core technical knowledge")
    return pool


def _attach_lo_ranges(pool, ranges):
    pool = [dict(q) for q in pool]
    for start, end, lo, lo_text, category in ranges:
        for i in range(start, min(end, len(pool))):
            pool[i]["lo"] = lo
            pool[i]["lo_text"] = lo_text
            pool[i]["category"] = category
            pool[i]["to"] = f"{lo}: {lo_text}"
    return pool


# ---------- IT Support banks (scenario-heavy) ----------
A1 = _rotate([
    _item("A new desktop fails POST with long continuous beep and no display. Reseating RAM and testing one stick at a time restores video. What was the most likely root cause?",
          "Faulty or improperly seated memory module", "Failed SATA data cable only", "Expired DHCP lease", "Corrupt hosts file",
          "LO-IS-1.2", "Troubleshoot memory and storage", "Hardware & Devices"),
    _item("You install an M.2 NVMe SSD but the OS installer only lists a SATA HDD. BIOS shows the NVMe under a PCIe slot. What should you check first?",
          "Whether the M.2 slot shares lanes with a disabled SATA port or needs UEFI storage mode set correctly", "Whether the HDD RPM is 5400 or 7200", "Whether Cat6 is T568A or T568B", "Whether the PSU is 80 Plus Bronze or Gold",
          "LO-IS-1.2", "Select and troubleshoot memory and storage", "Hardware & Devices"),
    _item("A workstation with dual-channel capable board shows half the expected memory bandwidth in diagnostics after a upgrade. Two identical DDR5 modules were installed in slots 1 and 2. What is the best next action?",
          "Move modules into the channel pair documented for dual-channel (often 2 and 4)", "Enable AHCI in the OS only", "Change the default gateway", "Disable Secure Boot permanently",
          "LO-IS-1.2", "Select and troubleshoot memory and storage", "Hardware & Devices"),
    _item("After adding a high-TDP GPU, random shutdowns occur only under 3D load while idle is stable. CPU and GPU temps are within spec. What is the most likely hardware limit?",
          "PSU wattage or 12V rail capacity insufficient under combined load", "DNS TTL too low", "Wrong VLAN on the management port", "Missing T568B pinout on HDMI",
          "LO-IS-1.3", "Configure power, cooling, and ports", "Hardware & Devices"),
    _item("A laptop charges only with the lid closed and shuts down when opened past 30 degrees. Which failure mode best matches?",
          "Damaged display hinge cable or connector intermittent under flex", "RAID 0 stripe failure", "APIPA addressing", "Expired Kerberos ticket only",
          "LO-IS-1.1", "Identify boards, sockets, and expansion", "Hardware & Devices"),
    _item("UEFI setup shows Secure Boot enabled but an unsigned legacy bootloader will not start. The training image requires that bootloader for a lab. What is the correct controlled approach?",
          "Temporarily allow the documented lab boot path per policy (e.g., disable Secure Boot or use signed media) then restore hardened settings", "Format the CMOS battery permanently", "Set the NIC to half duplex", "Disable the TPM by removing the CPU",
          "LO-IS-1.3", "Configure power, cooling, and ports", "Hardware & Devices"),
    _item("A PCIe 4.0 x16 GPU is installed in a mechanical x16 slot that is electrically only x4 on a small board. What performance outcome should you expect?",
          "Functionality with reduced bandwidth versus a full x16 electrical slot", "No POST until Resizable BAR is off", "Automatic upgrade to PCIe 5.0", "SATA speeds only",
          "LO-IS-1.1", "Identify boards, sockets, and expansion", "Hardware & Devices"),
    _item("ECC registered DIMMs from a server will not initialize in a consumer desktop that only lists unbuffered non-ECC support. Why?",
          "Memory controller and firmware do not support that module class", "Cat6 length exceeded", "Port 445 is blocked", "The PSU lacks a 24-pin connector",
          "LO-IS-1.2", "Select and troubleshoot memory and storage", "Hardware & Devices"),
    _item("A laser printer prints ghosted images of previous pages. Fuser temperature is normal. Which component is the primary suspect?",
          "Failing cleaning blade or drum unit retaining residual toner", "Wrong default gateway", "Disabled DHCP option 66", "Bad T568A patch only",
          "LO-IS-1.1", "Identify boards, sockets, and expansion", "Hardware & Devices"),
    _item("Thermal paste was applied in a thick blob covering the entire IHS. Idle temps are high. What is the correct remediation?",
          "Clean both surfaces and apply a thin appropriate amount, then reseat the cooler", "Increase pagefile size", "Switch to APIPA", "Enable port security on the printer",
          "LO-IS-1.3", "Configure power, cooling, and ports", "Hardware & Devices"),
    _item("RAID 5 array with four disks shows one disk failed. A rebuild starts then the array goes offline. What risk does RAID 5 have during rebuild that best explains urgency?",
          "A second disk failure during rebuild can destroy the array", "DHCP pools shrink automatically", "UEFI Secure Boot rotates keys", "SMB signing is disabled",
          "LO-IS-1.2", "Select and troubleshoot memory and storage", "Hardware & Devices"),
    _item("A mini-ITX build has no room for a full-height PCIe card. Which constraint is inherent to the form factor choice?",
          "Limited expansion slots and cooler clearance compared with ATX", "Inability to run 64-bit OS", "No support for RJ-45", "Mandatory ECC RAM",
          "LO-IS-1.1", "Identify boards, sockets, and expansion", "Hardware & Devices"),
    _item("A host can ping its gateway and LAN peers but cannot reach Internet hosts by name or IP. Traceroute dies at the gateway. What is the best first focus?",
          "Upstream routing/NAT/firewall policy beyond the gateway", "Local disk SMART status", "DisplayPort cable version", "Printer spooler service",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("A /27 network is required for 25 hosts. Which mask is appropriate without wasting a full /24 unnecessarily?",
          "255.255.255.224", "255.255.255.0", "255.255.0.0", "255.255.255.252",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("Two switches are connected with a single cable; both interfaces are access ports in different VLANs. Hosts on each switch cannot communicate. What is missing for inter-VLAN traffic?",
          "A router or L3 interface to route between VLANs", "APIPA on both sides", "RAID 1 on the switches", "WEP on the uplink",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("A technician changes a server IP but users still resolve the old address for 30 minutes. DNS A record was updated. What is the most likely delay source?",
          "Client or intermediate DNS cache TTL not yet expired", "Incorrect T568B on fiber", "PSU efficiency rating", "BitLocker recovery key rotation",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("Port 445 is blocked outbound from a user VLAN. Which common workflow breaks first?",
          "Access to SMB file shares", "DNS resolution of all names", "DHCP Discover broadcasts", "ARP on the local segment",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("A SOHO router was set to a static WAN IP but the ISP only provides DHCP. Symptom: WAN LED up, no Internet. Fix?",
          "Set WAN to obtain address automatically per ISP requirements", "Disable all LAN DHCP", "Force half duplex on WAN", "Enable port 25 only",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("A PC shows 169.254.x.x after move to a new desk. Cable tests OK to the wall. Switch port LED is off. Best next step?",
          "Verify switch port enabled/VLAN and link before blaming DHCP server", "Reinstall Office", "Disable UEFI", "Change the pagefile to D:",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("You need to confirm a remote host accepts HTTPS only. Which test is most appropriate?",
          "Connect to TCP 443 (e.g., browser or port check) and verify certificate/service response", "ping only", "chkdsk /r", "nslookup for MX only",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("After enabling a host firewall, RDP to a lab VM fails though ping works. What was likely overlooked?",
          "Allowing inbound TCP 3389 (or the configured RDP port) in the firewall", "Enabling SMB signing", "Setting a /30 on the loopback", "Disabling ARP",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("A dual-stack host reaches IPv4 sites but not IPv6-only services. ipconfig shows a link-local IPv6 only. What is missing?",
          "Global IPv6 address/RA or DHCPv6 configuration on the LAN path", "A second default gateway in IPv4", "WPA3 enterprise", "GPT conversion",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("Windows reports the boot volume is raw after a power loss mid-update. What is the most careful first recovery action?",
          "Boot installation/recovery media and attempt repair or offline volume recovery before destructive formats", "Immediate diskpart clean all", "Disable the NIC", "Delete System32",
          "LO-IS-3.1", "Install and maintain Windows storage and boot", "Operating Systems & Software"),
    _item("sfc /scannow fails repeatedly. Which tool is commonly used next to repair the Windows component store?",
          "DISM with restorehealth against a healthy source", "format c:", "nslookup", "tracert",
          "LO-IS-3.1", "Install and maintain Windows storage and boot", "Operating Systems & Software"),
    _item("A domain user can log on with cached credentials while offline but cannot access file shares when online. Password was recently reset. Best explanation?",
          "Kerberos/tickets or share authentication need a successful online logon path after password change", "APIPA is required for SMB", "RAID 0 must be rebuilt", "UEFI password equals domain password",
          "LO-IS-3.2", "Manage accounts, permissions, and tools", "Operating Systems & Software"),
    _item("A Linux lab VM cannot execute a script with permission denied though the file is readable. What is the typical fix?",
          "Add execute permission (e.g., chmod +x) or run via interpreter explicitly", "Convert disk to MBR", "Enable WEP", "Set metric 1 on all routes",
          "LO-IS-3.3", "Use Linux essentials and recovery practices", "Operating Systems & Software"),
    _item("Group Policy should apply a firewall baseline but gpresult shows the GPO denied. Computer is in the right OU. What should you verify?",
          "Security filtering, WMI filters, inheritance blocks, and computer vs user configuration scope", "Only the default gateway", "Only the pagefile size", "Only the HDMI cable",
          "LO-IS-3.2", "Manage accounts, permissions, and tools", "Operating Systems & Software"),
    _item("A Windows image must be deployed to mixed UEFI hardware. Which partition style is required for native UEFI boot?",
          "GPT", "MBR only", "FAT12 only", "NFS",
          "LO-IS-3.1", "Install and maintain Windows storage and boot", "Operating Systems & Software"),
    _item("Time skew of 10 minutes appears on a domain client; logons intermittently fail. Root cause class?",
          "Kerberos sensitivity to clock skew between client and domain controllers", "DNS using only LLMNR", "Cat5e length under 10m", "Missing thermal paste",
          "LO-IS-3.2", "Manage accounts, permissions, and tools", "Operating Systems & Software"),
    _item("You must map a drive only for members of a specific AD group at logon. Best mechanism?",
          "Group Policy preferences or login script scoped to that security group", "Static hosts file on every PC", "APIPA reservation", "Enabling Telnet",
          "LO-IS-3.2", "Manage accounts, permissions, and tools", "Operating Systems & Software"),
    _item("A user’s profile is corrupted; new files appear on desktop for a temporary profile only. Best remediation path?",
          "Rename/rebuild the profile folder and regenerate a clean profile per procedure", "Disable the CPU cache", "Set duplex to auto only", "Erase UEFI",
          "LO-IS-3.1", "Install and maintain Windows storage and boot", "Operating Systems & Software"),
    _item("Which principle best limits damage if a help-desk account is compromised?",
          "Least privilege with separate admin accounts and MFA for privileged roles", "Shared domain Admin password on a sticky note", "All users as local administrators", "Disable logging",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("Phishing email contains a link mimicking the SSO portal. User reports before clicking. What should you do first operationally?",
          "Record indicators, block/report per IR process, and verify no credentials were submitted", "Ignore because no click occurred so no risk exists ever", "Reimage the mail server immediately", "Disable all TLS",
          "LO-IS-4.2", "Follow malware and incident response steps", "Security"),
    _item("BitLocker is suspended for a firmware update then the device is lost. What residual risk remains?",
          "If suspension left the volume unprotected, data may be readable until protection is resumed", "APIPA will encrypt the disk", "RAID 1 encrypts automatically", "DNSSEC replaces BitLocker",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("A malware sample persists after reboot via a Run key and a scheduled task. After isolation, what is the correct high-level sequence?",
          "Identify/research, quarantine/remove persistence, remediate, verify, document", "Delete System32 first", "Only change the wallpaper", "Disable the switch uplink permanently",
          "LO-IS-4.2", "Follow malware and incident response steps", "Security"),
    _item("USB ports on kiosks should be restricted. Which control best matches the requirement?",
          "Endpoint policy to block unauthorized removable media plus physical port locks where needed", "Open guest SMB shares", "Disable all Ethernet", "Use WEP on kiosk Wi-Fi",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("A change to firewall rules was made during production without a ticket. Traffic drops. What process failure occurred?",
          "Missing change management approval and documentation", "Correct use of least privilege", "Proper tabletop IR exercise", "Successful capacity planning",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
    _item("While handling RAM modules, which practice reduces ESD risk most directly?",
          "Grounded wrist strap and ESD-safe work surface", "Working on carpet in socks", "Touching the CPU pins first", "Storing boards in plastic grocery bags",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
    _item("A ticket says “Internet is slow.” What is the best intake improvement?",
          "Gather scope, time started, wired/wireless, affected apps, and recent changes", "Close as user error immediately", "Only ask for the password", "Reimage without questions",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
    _item("Decommissioning drives from a finance PC requires which disposal standard mindset?",
          "Cryptographic erase or physical destruction per policy—not a single quick format", "Delete the desktop shortcuts only", "Unplug power and resell immediately", "Overwrite the hosts file",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("MFA challenge succeeds but the app still denies access. Logs show conditional access requiring compliant device. What is the issue class?",
          "Device compliance/conditional access policy not met", "Wrong subnet mask on the printer", "RAID rebuild percentage", "Expired DHCP option 150 only",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("A user insists on keeping local admin “to install printers.” What is the better control design?",
          "Delegated install rights or managed deployment without full local admin", "Give Domain Admins to all users", "Disable UAC and antivirus", "Share the built-in Administrator password",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
    _item("Which symptom most strongly suggests a duplex mismatch on a critical uplink?",
          "High late collisions/errors and poor throughput with link up", "Perfect symmetric throughput", "Only DNS failures", "Only POST beep codes",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("A new docking station provides DisplayPort but the laptop only drives one external monitor. BIOS and drivers are current. What should you verify next?",
          "Dock bandwidth limits, cable standards, and whether the port is USB-C DP-alt-mode capable", "Whether the HDD is 5400 RPM", "Whether the room has Cat3", "Whether port 25 is open",
          "LO-IS-1.1", "Identify boards, sockets, and expansion", "Hardware & Devices"),
    _item("Windows Event Viewer shows repeated failed logons from many internal IPs against one account. Best immediate action?",
          "Disable/reset the account per IR, preserve logs, and investigate lateral movement", "Ignore as noise", "Only reboot the PC", "Disable the firewall",
          "LO-IS-4.2", "Follow malware and incident response steps", "Security"),
    _item("A script uses plaintext credentials in a shared repo. What is the priority remediation?",
          "Rotate credentials, remove secrets from history where possible, and move to a secret store/managed identity", "Make the repo public", "Email the password to the team", "Store secrets in the hosts file",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("Which recovery option is most appropriate when a single file was deleted from a volume with previous-day backups but the volume is healthy?",
          "Restore the file from backup/previous versions rather than full bare-metal recovery", "Rebuild the RAID with different stripe size", "Disable the NIC team", "Reinstall the motherboard chipset only",
          "LO-IS-3.1", "Install and maintain Windows storage and boot", "Operating Systems & Software"),
    _item("A Linux host must allow user app to bind port 443 without running as root long-term. Which approach is more appropriate than continuous root?",
          "Capabilities, reverse proxy, or authbind-style controlled privilege—not permanent root shell", "chmod 777 /", "Disable SELinux and firewall always", "Telnet to localhost",
          "LO-IS-3.3", "Use Linux essentials and recovery practices", "Operating Systems & Software"),
    _item("After cloning a VM, both clones fight for the same IP and computer name on the LAN. What was omitted?",
          "Sysprep/generalize or regenerate identity and assign unique network identity", "Disabling DHCP on the LAN", "Setting both to APIPA intentionally", "Using identical MAC addresses on purpose",
          "LO-IS-3.1", "Install and maintain Windows storage and boot", "Operating Systems & Software"),
    _item("A help desk agent escalates without listing steps already tried. What professionalism issue does this create?",
          "Wasted tier-2 time and incomplete context for the next responder", "Faster MTTR always", "Automatic root cause", "Compliance with change control",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
])

A2 = _rotate([
    _item("SMART reports rising reallocated sectors on an OS SSD; backups are current. What is the prudent plan?",
          "Migrate data and replace the drive before hard failure", "Ignore until the OS fails to boot", "Only run disk cleanup", "Disable TRIM permanently",
          "LO-IS-1.2", "Select and troubleshoot memory and storage", "Hardware & Devices"),
    _item("A PCIe riser was added; GPU artifacts appear. The riser is unpowered for a power-hungry card. Likely issue?",
          "Insufficient PCIe power delivery through the riser path", "DNS cache poisoning", "Wrong NTP stratum only", "MBR vs GPT on the GPU",
          "LO-IS-1.3", "Configure power, cooling, and ports", "Hardware & Devices"),
    _item("Laptop battery swells the trackpad. Safety-first action?",
          "Power down, do not charge, isolate device, and handle swollen battery as hazardous", "Puncture to release gas", "Keep charging overnight", "Place under heavy books",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
    _item("Which IPv4 address is unusable as a host address on a /24 LAN?",
          "The network and broadcast addresses for that subnet", "Any address ending in .10", "Any RFC1918 address", "Any address with even last octet",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("A captive portal Wi-Fi network allows DNS but blocks general TCP until login. Users say “DNS works but web does not.” Explanation?",
          "Policy allows name resolution while redirecting/blocking web until authentication", "All packets are dropped including DNS", "RAID is rebuilding", "UEFI is offline",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("You must prove a file was not altered in transit for a forensic handoff. Which control is most relevant?",
          "Cryptographic hash comparison before and after transfer", "Ping time under 1ms", "Same filename length", "Identical file icon",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("Windows resource monitor shows a process locking a log file you need to truncate. Best approach?",
          "Stop the related service/process gracefully per procedure then manage the file", "Delete C:\\Windows", "Disable the firewall only", "Change the default gateway",
          "LO-IS-3.2", "Manage accounts, permissions, and tools", "Operating Systems & Software"),
    _item("A virtual NIC was set to promiscuous mode on a shared host without approval. Risk?",
          "Potential unauthorized capture of other tenants’ traffic depending on isolation", "Faster disk scrubbing", "Automatic BitLocker", "Lower CPU steal time only",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("Which metric best indicates a storage subsystem is the bottleneck under database load?",
          "High disk latency / queue length with modest CPU", "Low disk latency and 100% CPU", "Only high mouse DPI", "Only low fan RPM",
          "LO-IS-1.2", "Select and troubleshoot memory and storage", "Hardware & Devices"),
    _item("An access port is configured for VLAN 40; the user needs VLAN 40 but the wall jack is patched to a port still in VLAN 1. Result?",
          "Client will not reach VLAN 40 resources until the switchport VLAN matches design", "Automatic VLAN negotiation via DHCP option 3", "IPv6 fixes it", "DNSSEC assigns VLANs",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("A GPO installs software only when the computer is on the wired LAN. Laptops on VPN never get it. Design issue?",
          "Scope/filter assumes on-prem connectivity that VPN clients may not satisfy the same way", "VPN cannot carry SMB ever", "Laptops cannot be domain joined", "Group Policy requires APIPA",
          "LO-IS-3.2", "Manage accounts, permissions, and tools", "Operating Systems & Software"),
    _item("Which is the most appropriate evidence preservation step before reimaging a compromised endpoint?",
          "Capture volatile data/disk image per IR playbook when required", "Wipe immediately with no notes", "Post the disk image publicly", "Only change the hostname",
          "LO-IS-4.2", "Follow malware and incident response steps", "Security"),
    _item("A power user needs a local service account for a lab app. Least-privilege approach?",
          "Dedicated local account with only required rights and strong unique password/secret", "Use Domain Admin", "Use Guest with admin", "Hard-code root SSH keys in the app",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("Linux journalctl shows OOM killer terminating a service. Primary resource issue?",
          "Memory pressure exceeding available RAM + reclaimable cache under load", "DNS TTL", "Missing RJ-45 clip", "Wrong color laser cartridge",
          "LO-IS-3.3", "Use Linux essentials and recovery practices", "Operating Systems & Software"),
    _item("A change window is 02:00–04:00. At 03:50 a risky step remains. Best decision framework?",
          "Stop/rollback per plan rather than overrun into business hours without approval", "Continue until noon", "Skip testing", "Disable monitoring and proceed",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
    _item("Which cable fault is most likely if a cable certifier reports split pairs?",
          "Incorrect pairing of conductors despite continuity on pins", "Fiber polarity only", "Excessive PSU ripple", "Wrong NTP server",
          "LO-IS-1.1", "Identify boards, sockets, and expansion", "Hardware & Devices"),
    _item("A server NIC team is in switch-dependent mode but the switch is not configured for that teaming. Symptom?",
          "Unstable or suboptimal link aggregation behavior", "Automatic IPv6-only mode", "Forced WEP", "RAID 10 conversion",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("User cannot elevate with UAC while offline with cached creds for a domain account that requires online MFA for elevation. Explanation?",
          "Privileged elevation policy requires interactive online MFA path", "Cached logon always grants Domain Admin", "UAC is disabled offline always", "APIPA blocks UAC",
          "LO-IS-3.2", "Manage accounts, permissions, and tools", "Operating Systems & Software"),
    _item("Which backup test is the strongest validation?",
          "Periodic restore test of sample data to a non-production target", "Only checking backup job green status", "Only counting tape labels", "Only pinging the backup server",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
    _item("A mobile device management profile removes USB file transfer. User needs to export photos for an approved task. Correct process?",
          "Follow exception workflow or approved transfer method—not ad-hoc policy bypass", "Jailbreak the phone", "Disable MDM permanently", "Email the MDM admin password to the user",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
])

A3 = _rotate([
    _item("POST code indicates graphics initialization failure; onboard video works after removing the discrete GPU. Conclusion?",
          "Discrete GPU or its power/slot path is faulty", "DNS is misconfigured", "The hosts file blocks PCIe", "DHCP option 66 points to the GPU",
          "LO-IS-1.1", "Identify boards, sockets, and expansion", "Hardware & Devices"),
    _item("Which statement about RAID versus backup is accurate?",
          "RAID protects availability against drive failure; it is not a substitute for backups against deletion/malware/site loss", "RAID 0 is an offsite backup", "RAID 1 replaces versioning", "Backups require RAID 5",
          "LO-IS-1.2", "Select and troubleshoot memory and storage", "Hardware & Devices"),
    _item("A /30 is used on a point-to-point WAN link. How many usable host addresses exist?",
          "2", "30", "62", "254",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("Windows Hello for Business fails after TPM clear. What must be planned?",
          "Re-enrollment of TPM-bound credentials and possible recovery keys", "Only reinstalling the printer driver", "Only changing the subnet mask", "Only disabling IPv4",
          "LO-IS-3.2", "Manage accounts, permissions, and tools", "Operating Systems & Software"),
    _item("A ticket is marked resolved but the user never confirmed. Service quality issue?",
          "Lack of verification with the requester before closure", "Too much documentation", "Excessive follow-up", "Using change control",
          "LO-IS-4.3", "Practice safety, change control, and professionalism", "Operations & Professionalism"),
    _item("Which attack is best mitigated by application allow-listing on fixed-function kiosks?",
          "Execution of unauthorized binaries/ransomware payloads", "All DDoS on the ISP", "BGP hijacks on the Internet", "Undersea cable cuts",
          "LO-IS-4.1", "Apply physical and logical security controls", "Security"),
    _item("A Linux admin uses sudo -i for every task including reading logs. Better practice?",
          "Use least privilege sudo rules for specific commands", "Disable all auditing", "Share the root password via chat", "Run GUI as root over Telnet",
          "LO-IS-3.3", "Use Linux essentials and recovery practices", "Operating Systems & Software"),
    _item("Cable runs between buildings exceed copper Ethernet distance limits. Best media choice for the backbone?",
          "Fiber optic link", "Long Cat6 coiled in a loop", "USB-A extender", "Analog phone cable only",
          "LO-IS-1.1", "Identify boards, sockets, and expansion", "Hardware & Devices"),
    _item("A DHCP scope exhaustion causes intermittent APIPA. Sustainable fix?",
          "Expand capacity, reduce lease time appropriately, and remove stale reservations/rogue clients", "Disable DHCP forever", "Set all hosts to 1.1.1.1", "Use only public IPs on clients",
          "LO-IS-2.1", "Apply addressing, ports, and SOHO networking", "Networking"),
    _item("Which log source best helps prove who changed a privileged GPO?",
          "Directory service / auditing events for policy changes", "Printer toner levels", "Fan RPM history", "Display orientation logs",
          "LO-IS-4.2", "Follow malware and incident response steps", "Security"),
])

# ---------- Network Ops banks ----------
N1 = _rotate([
    _item("A packet is modified at each router hop for Layer 3 forwarding. Which header fields are typically rewritten?",
          "Layer 3 TTL/hop limit and Layer 2 addressing on each hop", "The original application payload checksum always", "The DNS query ID only", "The TLS certificate CN",
          "LO-NO-1.1", "Map OSI/TCP-IP layers to devices and protocols", "Networking"),
    _item("Which scenario correctly prefers UDP over TCP?",
          "Latency-sensitive streams where occasional loss is tolerable (e.g., many real-time media designs)", "Bank wire transfers requiring strict ordered delivery guarantees always via UDP", "RAID rebuild coordination", "UEFI firmware download requiring UDP only",
          "LO-NO-1.2", "Design addressing and compare TCP vs UDP", "Networking"),
    _item("Given network 192.168.10.0/23, which address is a valid host in the range?",
          "192.168.11.50", "192.168.12.10", "192.168.10.255 as usable host in /23 without checking", "192.168.9.1",
          "LO-NO-1.2", "Design addressing and compare TCP vs UDP", "Networking"),
    _item("STP places a port in blocking state. Primary purpose?",
          "Prevent Layer 2 loops while retaining redundancy", "Encrypt all frames", "Assign DHCP leases", "Terminate BGP",
          "LO-NO-1.3", "Explain topologies and common services", "Networking"),
    _item("An ACL is applied inbound on a router interface. A packet is denied. Where is it dropped relative to routing?",
          "According to ACL direction and interface placement—before or after routing depending on in/out design", "Only after NAT always", "Only on the client NIC", "Only in DNS",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("Which device is primarily a Layer 2 multiport bridge learning MAC addresses?",
          "Ethernet switch", "Router only", "Firewall specializing only in Layer 7 without switching", "Wireless controller without switching function",
          "LO-NO-2.1", "Place and describe network infrastructure devices", "Hardware & Devices"),
    _item("OSPF neighbors form but routes are missing. What should you verify beyond adjacency?",
          "Area mismatch, network statements, filtering, and LSDB contents", "Only the default gateway on a PC", "Only toner levels", "Only HDMI version",
          "LO-NO-1.1", "Map OSI/TCP-IP layers to devices and protocols", "Networking"),
    _item("A /64 is the common host subnet size for which protocol family?",
          "IPv6", "IPv4 only", "IPX", "AppleTalk",
          "LO-NO-1.2", "Design addressing and compare TCP vs UDP", "Networking"),
    _item("NAT hides internal addresses from the public Internet. Which tradeoff is most associated with basic many-to-one NAT?",
          "Inbound connections to internal hosts require additional mappings/ports", "Elimination of all ACLs", "Mandatory WEP", "Removal of ARP",
          "LO-NO-1.3", "Explain topologies and common services", "Networking"),
    _item("Which wireless security configuration is most appropriate for enterprise with per-user credentials?",
          "WPA2/WPA3-Enterprise with 802.1X", "Open system with MAC filter only", "WEP-128", "WPA-PSK shared by city-wide posters",
          "LO-NO-2.3", "Secure WLAN and describe cloud network constructs", "Security"),
    _item("A user VLAN cannot reach the Internet; the server VLAN can. Both use the same core. First isolation step?",
          "Compare routing, ACL/firewall policies, and NAT exemptions between VLANs", "Replace all copper with DAC only", "Disable STP globally", "Set all ports to trunk immediately",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("NetFlow/IPFIX is primarily used for?",
          "Traffic visibility and accounting metadata about flows", "Encrypting Layer 1", "Replacing DNSSEC", "Powering PoE devices",
          "LO-NO-3.1", "Monitor networks and apply segmentation", "Operations & Professionalism"),
    _item("A fiber link fails light levels on one side. Which tool confirms optical power?",
          "Optical power meter / light meter", "Toner probe only", "Punchdown tool only", "ESD wrist strap",
          "LO-NO-2.2", "Select copper, fiber, and wireless media", "Hardware & Devices"),
    _item("Which statement about TCP three-way handshake is correct?",
          "SYN, SYN-ACK, ACK establish a connection before data transfer", "FIN only is used to start connections", "UDP uses the same three-way handshake", "ARP completes TCP handshake",
          "LO-NO-1.1", "Map OSI/TCP-IP layers to devices and protocols", "Networking"),
    _item("A DMZ hosts public web servers. What is the design intent?",
          "Segment Internet-facing services from internal trust zones", "Place domain controllers on the Internet without firewalls", "Disable logging", "Require WEP on servers",
          "LO-NO-3.1", "Monitor networks and apply segmentation", "Operations & Professionalism"),
    _item("802.1Q tagging is used to?",
          "Carry VLAN identity on trunk links", "Encrypt passwords", "Assign IPv6 /48 automatically", "Measure optical loss",
          "LO-NO-1.3", "Explain topologies and common services", "Networking"),
    _item("A site-to-site VPN comes up but traffic does not pass interesting traffic selectors. Focus area?",
          "Crypto ACL/traffic selectors and routing into the tunnel", "Toner density", "Display resolution", "RAID stripe size",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("Which copper Ethernet issue is most associated with excessive NEXT?",
          "Poor pair twisting/termination quality", "Low optical dBm", "Missing default route only", "NTP stratum 16 only",
          "LO-NO-2.2", "Select copper, fiber, and wireless media", "Hardware & Devices"),
    _item("Anycast DNS is used so that?",
          "Multiple sites advertise the same service address and clients prefer topologically closer instances", "All clients share one unicast host only", "DHCP is disabled", "STP is replaced",
          "LO-NO-1.3", "Explain topologies and common services", "Networking"),
    _item("A zero-trust approach most strongly emphasizes?",
          "Continuous verification and least privilege regardless of network location", "Trusting all traffic inside the old perimeter", "Disabling MFA on VPN", "Using Telnet for management",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("Packet capture shows retransmissions and shrinking windows during a file copy. Likely class of issue?",
          "Congestion or loss on the path affecting TCP performance", "DNSSEC failure only", "Wrong printer driver", "UEFI Secure Boot",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("Which protocol resolves IPv4 addresses to MAC addresses on a LAN?",
          "ARP", "DNS", "TLS", "SMTP",
          "LO-NO-1.1", "Map OSI/TCP-IP layers to devices and protocols", "Networking"),
    _item("A wireless survey shows high channel utilization on 2.4 GHz. Best first design response?",
          "Prefer 5/6 GHz where clients support it and reduce co-channel interference", "Disable all security", "Force 802.11b only", "Use WEP to reduce overhead",
          "LO-NO-2.3", "Secure WLAN and describe cloud network constructs", "Security"),
    _item("HSRP/VRRP primarily provides?",
          "First-hop gateway redundancy for clients", "Certificate enrollment", "Optical multiplexing", "Disk striping",
          "LO-NO-2.1", "Place and describe network infrastructure devices", "Hardware & Devices"),
    _item("A traceroute shows * * * at a hop then continues. Interpretation?",
          "That hop may rate-limit or block ICMP TTL-exceeded while forwarding still works", "The path is definitively broken forever", "DNS is down globally", "The client lacks a NIC",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("Which control best reduces risk of unauthorized devices on access ports?",
          "802.1X port authentication", "Disabling all logging", "Using hubs only", "Static routes to 0.0.0.0/0 on clients",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("MTU mismatch causing PMTUD black hole typically shows up as?",
          "Connections that stall for large payloads while small packets succeed", "Always successful large transfers", "Only failed ARP", "Only failed STP",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("A cloud VPC peering link does not transit to on-prem by default in many designs. Implication?",
          "You may need explicit hybrid connectivity/routing rather than assuming transitive peering", "All VPCs automatically mesh globally", "BGP is illegal in cloud", "DNS cannot run in cloud",
          "LO-NO-2.3", "Secure WLAN and describe cloud network constructs", "Security"),
    _item("Syslog messages are critical for IR but are only stored on each device. Weakness?",
          "Lack of centralized immutable logging for correlation and retention", "Too much centralization", "Excessive MFA", "Too many fiber strands",
          "LO-NO-3.1", "Monitor networks and apply segmentation", "Operations & Professionalism"),
    _item("Which is a private IPv4 range?",
          "172.16.0.0/12", "8.8.8.0/24", "1.1.1.0/24", "9.9.9.0/24",
          "LO-NO-1.2", "Design addressing and compare TCP vs UDP", "Networking"),
])

N2 = _rotate([
    _item("A switchport is err-disabled after a host flaps. Likely feature?",
          "Link flap / errdisable recovery related security or physical protection features", "OSPF cost 1", "DNS TTL 0", "RAID alert",
          "LO-NO-2.1", "Place and describe network infrastructure devices", "Hardware & Devices"),
    _item("QoS classification should occur as close as possible to?",
          "The traffic source / trust boundary with consistent policy", "Only the far Internet core", "Only on printers", "Only during weekends",
          "LO-NO-3.1", "Monitor networks and apply segmentation", "Operations & Professionalism"),
    _item("Which DNS record type maps a name to an IPv6 address?",
          "AAAA", "A only", "MX", "PTR only for IPv4",
          "LO-NO-1.3", "Explain topologies and common services", "Networking"),
    _item("A rogue DHCP server hands out wrong gateways. Symptom pattern?",
          "Clients get addresses but cannot reach correct networks / intermittent blackholing", "All fiber goes dark", "STP root is stable and perfect", "Only HTTPS works",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("IPsec tunnel mode vs transport mode difference in typical site-to-site use?",
          "Tunnel mode protects original IP headers by encapsulating packets", "Transport mode is required for all site-to-site designs always", "Tunnel mode only encrypts ARP", "Transport mode requires hubs",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("Single-mode fiber is preferred over multimode when?",
          "Longer distance runs between campuses/buildings", "Runs under 3 meters only inside a desk", "USB peripheral links", "Analog POTS only",
          "LO-NO-2.2", "Select copper, fiber, and wireless media", "Hardware & Devices"),
    _item("BPDU Guard is enabled on access ports to?",
          "Shut down ports that receive unexpected STP BPDUs from edge devices", "Encrypt BGP", "Assign QoS DSCP 46 automatically", "Disable ARP",
          "LO-NO-2.1", "Place and describe network infrastructure devices", "Hardware & Devices"),
    _item("A dual-homed BGP edge loses one provider. Best outcome with proper design?",
          "Traffic shifts to remaining provider based on policy/routes", "All sessions die permanently", "OSPF becomes BGP", "VLANs collapse",
          "LO-NO-1.1", "Map OSI/TCP-IP layers to devices and protocols", "Networking"),
    _item("Which monitoring approach detects encrypted C2 least by payload signatures alone?",
          "Behavioral/flow/endpoint telemetry rather than only classic cleartext IDS signatures", "Only matching on HTTP GET strings always works for TLS", "Only ping monitoring", "Only toner SNMP",
          "LO-NO-3.1", "Monitor networks and apply segmentation", "Operations & Professionalism"),
    _item("A /28 provides how many usable IPv4 hosts (standard host addressing)?",
          "14", "16", "30", "28",
          "LO-NO-1.2", "Design addressing and compare TCP vs UDP", "Networking"),
    _item("Management plane protection on network devices should include?",
          "AAA, encrypted management (SSH/HTTPS), ACLs on management access, logging", "Telnet with shared passwords only", "SNMPv1 community public write", "No banners and no logs",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("Wi-Fi 6 (802.11ax) OFDMA primarily improves?",
          "Efficiency serving multiple clients in dense environments", "Copper cable category ratings", "OSPF hello timers", "Disk IOPS",
          "LO-NO-2.3", "Secure WLAN and describe cloud network constructs", "Security"),
    _item("A host sets a static /24 but the LAN is /22. Connectivity is partial. Why?",
          "Incorrect mask causes wrong assumption about on-link vs routed destinations", "TCP cannot use static IPs", "ARP is disabled by /22", "DNSSEC rejects /24",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("Which technology segments east-west traffic in a data center at scale more flexibly than only VLANs?",
          "Overlay segmentation (e.g., VXLAN with policy) as used in many modern fabrics", "A single hub", "Analog modems", "Token Ring only",
          "LO-NO-1.3", "Explain topologies and common services", "Networking"),
    _item("Certificate-based EAP-TLS for 802.1X is valued because?",
          "Strong mutual authentication without sharing a single PSK", "It uses WEP underneath", "It disables all encryption", "It requires Telnet",
          "LO-NO-2.3", "Secure WLAN and describe cloud network constructs", "Security"),
    _item("Latency is low but jitter is high on a voice VLAN. Impact?",
          "Voice quality degradation despite acceptable average delay", "Only email fails", "Only STP fails", "Only DHCP fails",
          "LO-NO-3.1", "Monitor networks and apply segmentation", "Operations & Professionalism"),
    _item("A copper run fails certification at 100m+ for 10GBASE-T. Likely factor?",
          "Category rating and installation quality limits for that speed/distance", "DNS TTL", "Missing MFA", "Wrong printer form type",
          "LO-NO-2.2", "Select copper, fiber, and wireless media", "Hardware & Devices"),
    _item("Control plane policing is intended to?",
          "Protect device CPU from excessive control/management traffic", "Accelerate RAID", "Replace fiber", "Disable QoS",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("Which command-line tool on many systems shows the path packets take?",
          "traceroute/tracert", "chkdsk", "diskpart", "sfc",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("Anycast vs unicast for a service IP: operational difference?",
          "Anycast can steer clients to nearest advertisement of the same address", "Anycast forbids DNS", "Unicast cannot be routed", "Anycast requires hubs",
          "LO-NO-1.3", "Explain topologies and common services", "Networking"),
])

N3 = _rotate([
    _item("A firewall rule allows established/related states. A new outbound HTTP connection still needs?",
          "A rule permitting the initial outbound flow (depending on policy model)", "Only inbound any any", "Only ARP allow", "Only spanning-tree allow",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("Split-horizon DNS is used so that?",
          "Internal and external resolvers return different answers for the same name", "All DNS is disabled internally", "DHCP assigns DNSSEC keys", "STP carries DNS",
          "LO-NO-1.3", "Explain topologies and common services", "Networking"),
    _item("Which metric is most useful to prove a WAN circuit is saturating?",
          "Interface utilization and drops over time", "Mouse polling rate", "Number of VLANs configured", "Number of DNS suffixes",
          "LO-NO-3.1", "Monitor networks and apply segmentation", "Operations & Professionalism"),
    _item("LACP is used to?",
          "Bundle multiple physical links into a logical aggregated link when peers agree", "Encrypt SNMP", "Assign VLANs via DHCP only", "Replace IP addresses with MACs globally",
          "LO-NO-2.1", "Place and describe network infrastructure devices", "Hardware & Devices"),
    _item("A user VPN authenticates but cannot reach internal HTTP. Split tunnel excludes the internal network. Fix class?",
          "Adjust tunnel policy/routes so internal destinations traverse the VPN", "Disable HTTP forever", "Force WEP on VPN", "Change the user’s display language",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("Which IPv6 feature reduces the need for NAT as commonly used in IPv4 SOHO?",
          "Abundant addressing with global uniques (still with firewalling)", "Mandatory WEP", "Removal of routers", "Only using /30 everywhere",
          "LO-NO-1.2", "Design addressing and compare TCP vs UDP", "Networking"),
    _item("A security baseline requires disabling unused switch ports. Primary benefit?",
          "Reduce opportunity for unauthorized network attachment", "Increase broadcast domain size", "Disable STP permanently", "Force half duplex",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
    _item("Optical time-domain reflectometer (OTDR) is used to?",
          "Characterize fiber spans and locate faults/reflections", "Crimp RJ-45", "Measure PSU wattage", "Test DDR timings",
          "LO-NO-2.2", "Select copper, fiber, and wireless media", "Hardware & Devices"),
    _item("In troubleshooting methodology, changing three variables at once primarily hurts?",
          "Ability to attribute which change fixed or broke the system", "Cable aesthetics", "Font choices on diagrams", "Color of patch panels only",
          "LO-NO-3.3", "Troubleshoot using methodology and tools", "Operations & Professionalism"),
    _item("Which protocol provides secure remote CLI management replacing Telnet?",
          "SSH", "HTTP cleartext", "FTP cleartext", "SNMPv1",
          "LO-NO-3.2", "Harden devices and apply zero-trust ideas", "Security"),
])


def _balance_select(pool, n=50, categories=None):
    if categories is None:
        categories = [
            "Hardware & Devices",
            "Networking",
            "Operating Systems & Software",
            "Security",
            "Operations & Professionalism",
            "Core Knowledge",
        ]
    pool = _ensure_meta([dict(q) for q in pool])
    by = {c: [] for c in categories}
    for q in pool:
        cat = q.get("category") or "Core Knowledge"
        if cat not in by:
            by[cat] = []
        by[cat].append(q)
    main = [c for c in categories if c != "Core Knowledge"]
    per = max(1, n // max(len(main), 1))
    selected = []
    used_ids = set()

    def qid(q):
        return q.get("text", "")

    for cat in main:
        take = by.get(cat, [])[:per]
        for q in take:
            if qid(q) not in used_ids:
                selected.append(q)
                used_ids.add(qid(q))
    leftovers = []
    for cat in main + ["Core Knowledge"]:
        for q in by.get(cat, []):
            if qid(q) not in used_ids:
                leftovers.append(q)
    i = 0
    while len(selected) < n and leftovers and i < len(leftovers) * 3:
        q = leftovers[i % len(leftovers)]
        i += 1
        if qid(q) in used_ids:
            continue
        selected.append(q)
        used_ids.add(qid(q))
    buckets = {c: [] for c in main}
    other = []
    for q in selected:
        c = q.get("category") or "Core Knowledge"
        if c in buckets:
            buckets[c].append(q)
        else:
            other.append(q)
    ordered = []
    max_len = max((len(v) for v in buckets.values()), default=0)
    for i in range(max_len):
        for c in main:
            if i < len(buckets[c]):
                ordered.append(buckets[c][i])
    ordered.extend(other)
    return _rotate(ordered[:n])


def tests_aplus():
    pool = list(A1) + list(A2) + list(A3)
    form1 = _balance_select(pool, 50)
    form2 = _balance_select(pool[20:] + pool[:20], 50)
    form3 = _balance_select(pool[40:] + pool[:40], 50)
    return [
        ("IT Support Knowledge Test A", "Scenario-based items across hardware, networking, OS, security, and operations. 50 questions. Passing score 80%.", 1, form1),
        ("IT Support Knowledge Test B", "Scenario-based items across hardware, networking, OS, security, and operations. 50 questions. Passing score 80%.", 2, form2),
        ("IT Support Knowledge Test C", "Scenario-based items across hardware, networking, OS, security, and operations. 50 questions. Passing score 80%.", 3, form3),
    ]


def tests_netplus():
    pool = list(N1) + list(N2) + list(N3)
    cats = ["Networking", "Hardware & Devices", "Security", "Operations & Professionalism", "Core Knowledge"]
    form1 = _balance_select(pool, 50, categories=cats)
    form2 = _balance_select(pool[15:] + pool[:15], 50, categories=cats)
    form3 = _balance_select(pool[30:] + pool[:30], 50, categories=cats)
    return [
        ("Network Operations Knowledge Test A", "Scenario-based networking, infrastructure, security, and operations. 50 questions. Passing score 80%.", 1, form1),
        ("Network Operations Knowledge Test B", "Scenario-based networking, infrastructure, security, and operations. 50 questions. Passing score 80%.", 2, form2),
        ("Network Operations Knowledge Test C", "Scenario-based networking, infrastructure, security, and operations. 50 questions. Passing score 80%.", 3, form3),
    ]
