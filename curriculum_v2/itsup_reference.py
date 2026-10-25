"""IT Support Technician Fundamentals — reference/depth sections and objective revisions (pass 8).

Each REFERENCE entry is appended to a lesson as a clearly headed "Reference" section so the original
teaching flow is untouched. Facts were checked against the issuing bodies' current publications
(listed in SOURCES and in CURRICULUM_AUDIT.md). Dates are stated so instructors can re-check them.
"""
from .netops_core import table, check

SOURCES = {
    'win-lifecycle': 'Microsoft Learn — Windows 11 release information / Supported versions of Windows client (checked Oct 2026)',
    'win10-eos': 'Microsoft Support — “Windows 10 support has ended on October 14, 2025”; Windows 10 ESU program page (consumer ESU through 12 Oct 2027)',
    'win11-req': 'Microsoft — Windows 11 specifications and system requirements',
    'nist-63b4': 'NIST SP 800-63B-4, Digital Identity Guidelines: Authentication and Authenticator Management (final, July 2025)',
    'wifi': 'IEEE 802.11ax/802.11be; Wi-Fi Alliance certification requirements as summarised in vendor design guides (WPA3 required on 6 GHz)',
    'usb': 'USB-IF Data Performance Language Usage Guidelines (Jan 2024); Intel Thunderbolt 5 technology brief',
    'ddr5': 'JEDEC DDR5 standards (JESD79-5 family; DDR5 UDIMM JESD308) as summarised by module vendors',
    'pcie': 'PCI-SIG PCIe base specifications (per-lane transfer rates)',
    'iana-ports': 'IANA Service Name and Transport Protocol Port Number Registry',
    'vmware': 'Broadcom/VMware — Workstation Pro free for all users (Nov 2024); Workstation Player discontinued',
}

REFERENCE = {
    # (chapter, lesson): (heading, html, [source keys])
    (2, 4): ('Reference — memory generations and form factors', table(
        ['', 'DDR4', 'DDR5'], [
            ['Desktop module', '288-pin DIMM', '288-pin DIMM (notch in a different place — not interchangeable)'],
            ['Laptop module', '260-pin SO-DIMM', '262-pin SO-DIMM; some newer laptops use CAMM2 or soldered LPDDR5/5X'],
            ['Nominal voltage', '1.2 V', '1.1 V'],
            ['Power regulation', 'On the motherboard', 'On the module (PMIC)'],
            ['Channel layout', 'One 64-bit channel per module', 'Two independent 32-bit sub-channels per module'],
            ['Error correction', 'ECC only on ECC modules', 'On-die ECC inside every chip protects the DRAM cells; it is <em>not</em> the same as an ECC DIMM, which protects data on the way to the CPU'],
            ['Speed profiles', 'XMP', 'XMP 3.0 (Intel) or EXPO (AMD) — overclock profiles; disable to test instability'],
        ]) + '<p>Install matched modules in the slots the board manual names for dual-channel (often the second and fourth slots from the CPU). '
             'A system that reports less memory than is installed, or runs at single-channel bandwidth, usually has a module in the wrong slot or not fully seated.</p>', ['ddr5']),
    (3, 1): ('Reference — storage interfaces and real-world speeds', table(
        ['Interface', 'Link rate', 'Practical ceiling', 'Notes'], [
            ['SATA III', '6 Gb/s', '≈ 550–600 MB/s', 'HDDs and 2.5-inch SATA SSDs; also M.2 SATA (B+M key) sticks'],
            ['NVMe over PCIe 3.0 ×4', '8 GT/s per lane', '≈ 3.5 GB/s', 'M-key M.2'],
            ['NVMe over PCIe 4.0 ×4', '16 GT/s per lane', '≈ 7 GB/s', 'Common in current desktops and laptops'],
            ['NVMe over PCIe 5.0 ×4', '32 GT/s per lane', '≈ 14 GB/s', 'Needs a PCIe 5.0 slot; often needs a heatsink'],
        ]) + '<p>M.2 is the connector and card shape (sizes such as 2242, 2260 and 2280 give width and length in millimetres); SATA or NVMe is the protocol. '
             'A B+M-key stick is usually SATA; an M-key-only stick is usually NVMe — check the board manual, because some M.2 slots support only one protocol or disable SATA ports when used. '
             'Hard drives spin at 5,400 or 7,200 rpm (10k/15k in older servers); SSDs have a rated endurance (TBW) and rely on TRIM to stay fast.</p>', ['pcie']),
    (3, 4): ('Reference — USB, Thunderbolt and display links (current names)', table(
        ['Name customers see', 'Specification name', 'Signalling rate'], [
            ['Hi-Speed USB', 'USB 2.0', '480 Mb/s'],
            ['USB 5Gbps', 'USB 3.2 Gen 1 (formerly USB 3.0 / 3.1 Gen 1)', '5 Gb/s'],
            ['USB 10Gbps', 'USB 3.2 Gen 2', '10 Gb/s'],
            ['USB 20Gbps', 'USB 3.2 Gen 2×2 or USB4 20 Gbps', '20 Gb/s (Gen 2×2 needs USB-C)'],
            ['USB 40Gbps', 'USB4 (Version 1.0)', '40 Gb/s'],
            ['USB 80Gbps', 'USB4 Version 2.0', '80 Gb/s symmetric, or 120/40 Gb/s asymmetric'],
            ['Thunderbolt 4', '—', '40 Gb/s'],
            ['Thunderbolt 5', 'Built on USB4 Version 2.0', '80 Gb/s bidirectional; up to 120 Gb/s “Bandwidth Boost” for displays'],
        ]) + '<p><strong>USB-C is a connector, not a speed.</strong> The same plug can carry USB 2.0, 10 Gb/s, USB4, DisplayPort Alt Mode and USB Power Delivery (up to 240 W with PD 3.1 Extended Power Range and a 240 W-rated cable) — '
             'or only some of these. Check the port’s icon and the laptop’s spec sheet, and the cable’s rating, before blaming a dock. '
             'For displays, HDMI 2.1 carries up to 48 Gb/s and DisplayPort 2.1 up to 80 Gb/s (UHBR20); the slowest link in the chain (port, adapter, cable, monitor input) sets the maximum resolution and refresh rate.</p>', ['usb']),
    (5, 2): ('Reference — port numbers technicians use', table(
        ['Port', 'Protocol', 'Service'], [
            ['20/21', 'TCP', 'FTP (cleartext — prefer SFTP)'], ['22', 'TCP', 'SSH / SFTP'], ['23', 'TCP', 'Telnet (cleartext — avoid)'],
            ['25', 'TCP', 'SMTP relay between mail servers'], ['53', 'UDP/TCP', 'DNS'], ['67/68', 'UDP', 'DHCP'],
            ['80', 'TCP', 'HTTP'], ['110 / 995', 'TCP', 'POP3 / POP3 over TLS'], ['123', 'UDP', 'NTP'],
            ['137–139', 'UDP/TCP', 'NetBIOS (legacy Windows naming/sharing)'], ['143 / 993', 'TCP', 'IMAP / IMAP over TLS'],
            ['161/162', 'UDP', 'SNMP / SNMP traps'], ['389 / 636', 'TCP', 'LDAP / LDAPS'], ['443', 'TCP (UDP for HTTP/3)', 'HTTPS'],
            ['445', 'TCP', 'SMB file sharing'], ['587', 'TCP', 'Mail submission from clients'], ['3389', 'TCP/UDP', 'Remote Desktop'],
        ]) + '<p>Ports 0–1023 are “well-known”; client connections use a temporary high port as their source. A firewall rule or a stopped service shows up as “ping works but the app does not” — '
             'test the port itself with <code>Test-NetConnection server -Port 445</code>.</p>', ['iana-ports']),
    (5, 4): ('Reference — Wi-Fi generations and SOHO security baseline', table(
        ['Name', 'IEEE', 'Bands', 'What changed'], [
            ['Wi-Fi 4', '802.11n', '2.4 / 5 GHz', 'MIMO'],
            ['Wi-Fi 5', '802.11ac', '5 GHz', 'Wider channels, MU-MIMO downlink'],
            ['Wi-Fi 6', '802.11ax', '2.4 / 5 GHz', 'OFDMA: better with many devices'],
            ['Wi-Fi 6E', '802.11ax', '+ 6 GHz', 'New spectrum; WPA3 required on 6 GHz'],
            ['Wi-Fi 7', '802.11be', '2.4 / 5 / 6 GHz', '320 MHz channels in 6 GHz; multi-link operation'],
        ]) + '<h4>Baseline for a small office or home router</h4><ol>'
             '<li>Change the default admin password and, if offered, the admin username; disable remote (WAN-side) administration unless required.</li>'
             '<li>Use WPA3-Personal (or WPA2/WPA3 transition mode if older devices must connect). Never WEP or TKIP.</li>'
             '<li>Turn off WPS; its PIN method is a known weakness.</li>'
             '<li>Put visitors on a guest network with client isolation.</li>'
             '<li>Update firmware, and replace routers that no longer receive updates.</li>'
             '<li>Hiding the SSID and MAC filtering are not security controls — the radio and MAC addresses are still visible to anyone listening.</li></ol>', ['wifi']),
    (8, 1): ('Reference — Windows 11 requirements and servicing (checked Oct 2026)', table(
        ['Requirement', 'Minimum'], [
            ['Processor', '1 GHz or faster, 2 or more cores, on Microsoft’s supported 64-bit CPU list'],
            ['Memory / storage', '4 GB RAM / 64 GB storage'],
            ['Firmware', 'UEFI, Secure Boot capable'],
            ['Security processor', 'TPM 2.0'],
            ['Graphics / display', 'DirectX 12 compatible, WDDM 2.0 driver; 720p display larger than 9 inches'],
        ]) + '<p>Check a PC with the PC Health Check app or your management tool before promising an upgrade.</p>'
             + table(['Version', 'Released', 'Updates end — Home/Pro', 'Updates end — Enterprise/Education'], [
                ['24H2', 'Oct 2024', '13 Oct 2026 (ended)', '12 Oct 2027'],
                ['25H2', 'Sep 2025', '12 Oct 2027', '10 Oct 2028'],
                ['26H2', 'Sep 2026', '10 Oct 2028', '9 Oct 2029'],
            ]) + '<p>Feature updates arrive yearly; each is serviced for 24 months on Home/Pro and 36 months on Enterprise/Education. '
                 '<strong>Windows 10 reached end of support on 14 October 2025</strong>; enrolled personal devices can receive security-only Extended Security Updates through 12 October 2027, and organisations can buy commercial ESU. '
                 'Treat any Windows 10 device as a migration ticket. These dates change — confirm them on Microsoft’s release-information pages each term.</p>'
                 '<h4>Install and recovery options</h4><ul><li><strong>In-place upgrade</strong> keeps apps, settings and files.</li>'
                 '<li><strong>Clean install</strong> wipes the target volume — back up first and confirm the disk with <code>list disk</code>.</li>'
                 '<li><strong>Reset this PC</strong> reinstalls Windows with a choice to keep personal files (cloud download or local reinstall).</li>'
                 '<li><strong>Image/provisioning deployment</strong> (for example Windows Autopilot or an organisation’s imaging tool) for fleets.</li></ul>', ['win11-req', 'win-lifecycle', 'win10-eos']),
    (9, 1): ('Reference — Linux commands a support technician uses', table(
        ['Task', 'Command', 'Windows cousin'], [
            ['Where am I / who am I', '<code>pwd</code>, <code>whoami</code>, <code>hostname</code>', '<code>cd</code>, <code>whoami</code>, <code>hostname</code>'],
            ['List and read files', '<code>ls -l</code>, <code>cat</code>, <code>less</code>, <code>tail -f</code>', '<code>dir</code>, <code>type</code>'],
            ['Permissions', '<code>chmod</code>, <code>chown</code>, <code>ls -l</code> (rwx for owner/group/other)', 'icacls'],
            ['Run as administrator', '<code>sudo command</code>', 'Run as administrator / UAC'],
            ['Addresses and routes', '<code>ip a</code>, <code>ip route</code>', '<code>ipconfig /all</code>, <code>route print</code>'],
            ['Name lookup', '<code>dig</code>, <code>nslookup</code>, <code>resolvectl status</code>', '<code>nslookup</code>, <code>Resolve-DnsName</code>'],
            ['Listening ports', '<code>ss -tulpn</code>', '<code>netstat -ano</code>'],
            ['Services and logs', '<code>systemctl status name</code>, <code>journalctl -u name</code>', 'services.msc, Event Viewer'],
            ['Disk and memory', '<code>df -h</code>, <code>free -h</code>, <code>top</code>', 'Task Manager, <code>Get-Volume</code>'],
            ['Install software', '<code>apt</code> (Debian/Ubuntu), <code>dnf</code> (Fedora/RHEL)', 'winget, Microsoft Store'],
        ]) + '<p>“Permission denied” on a script that you can read usually means it lacks the execute bit: <code>chmod +x script.sh</code>, or run it through its interpreter (<code>bash script.sh</code>). '
             'Use <code>sudo</code> for the one command that needs it rather than staying in a root shell.</p>', []),
    (10, 1): ('Reference — authentication and passwords (current guidance)', '<ul>'
             '<li><strong>Factors:</strong> something you know (password, PIN), have (phone app, security key, smart card) or are (fingerprint, face). Multi-factor authentication (MFA) combines two or more <em>different</em> factors.</li>'
             '<li><strong>Phishing-resistant MFA</strong> — FIDO2 security keys, passkeys and smart cards — cannot be replayed on a fake site. Prefer them over SMS codes or push prompts, which can be phished or approved by mistake (“MFA fatigue”).</li>'
             '<li><strong>NIST SP 800-63B-4 (July 2025)</strong> requires passwords used on their own to be at least 15 characters (at least 8 when used only as part of MFA), and tells verifiers <em>not</em> to impose composition rules (such as “one symbol, one digit”) and <em>not</em> to force periodic changes — change a password when there is evidence it is compromised. Check new passwords against lists of breached and common passwords, allow at least 64 characters, and allow password managers to paste.</li>'
             '<li>Your organisation’s policy decides what you enforce; NIST guidance is what many policies are moving toward.</li>'
             '<li><strong>Support rules that do not change:</strong> verify identity before any reset, never ask for or record a user’s password, and use separate, MFA-protected admin accounts for privileged work.</li></ul>', ['nist-63b4']),
}

# Vague "Know …" lesson objectives rewritten with observable verbs (originals remain in the block sources / git).
OBJECTIVE_REWRITES = {
    (1, 2): {'Know when a safety issue is an incident, not a “quick swap”':
             'Classify a safety issue (shock, heat, smoke, swollen battery) as an incident and stop work instead of performing a “quick swap”'},
    (1, 4): {'Know what belongs in the ticket versus what belongs on a phone to a lead':
             'Decide which information belongs in the ticket and which must go to a lead by phone (for example credentials or a suspected compromise)'},
    (2, 2): {'Know that a “dead” PC can be a firmware setting, not a dead board':
             'Identify firmware settings (boot order, CSM/legacy mode, Secure Boot, XMP/EXPO) that can make a working PC appear dead'},
    (3, 2): {'Know when a degraded array is an incident, not a quiet disk swap':
             'Explain why a degraded RAID array is an incident that requires a verified backup before any disk swap'},
    (6, 1): {'Know that this training PC may already be a guest (NOVAK-W11-07)':
             'Determine whether a Windows PC is a virtual machine guest (System Information, Task Manager, or the lab host name)'},
    (6, 2): {'Know when a “cloud outage” is a vendor ticket, not a local reimage':
             'Distinguish a SaaS/vendor outage from a local fault using scope and a provider status page, and route it to the vendor'},
    (6, 3): {'Know a guest can be on a virtual switch that is not the jack in the wall':
             'Trace a guest’s network path through its virtual NIC and virtual switch to the host uplink'},
}
