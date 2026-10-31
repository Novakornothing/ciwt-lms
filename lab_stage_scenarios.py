"""Stage 2 and Stage 3 prose, one scenario per lab.

The strings below are the instructor text. They are not built by filling one
family paragraph. A missing lab id is an error.
"""
from __future__ import annotations

# Each value is (stage 2, stage 3). Discovery lives in the desk note or in a
# file on the machine; these paragraphs do not contain the attempt's values.
COPY = {}


def add(lid, assisted, ticket):
    COPY[lid] = {"assisted": assisted.strip(), "ticket": ticket.strip()}


def prose(lab, stage):
    import lab_skills as SK
    custom = SK.prose(lab, stage)
    if custom:
        return custom
    row = COPY.get(lab.get("id") if isinstance(lab, dict) else lab)
    if not row or stage not in row:
        raise KeyError(lab.get("id") if isinstance(lab, dict) else lab)
    return row[stage]

add("sw-vlan-access",
"""The training-room phone on the second floor jack still shares a broadcast domain with every other closet device, so it never reaches the users subnet. This is not the VLAN exercise you just finished. The practice note names a different VLAN number, the name to give that VLAN, and the access port the phone is actually using. Create the VLAN, apply that name, and place only that port into it as an access port. Leave the walkthrough VLAN on the switch.""",
"""Facilities will not close the closet ticket until this switch carries the name written on the rack card. The incident note has that name. Set the device name to the text in the note and leave the access port you just moved in its new VLAN. A name taken from the walkthrough, or from the neighboring closet, will not match.""")

add("sw-vlan-multi",
"""Staff laptops and the lobby kiosk are still in one broadcast domain, and the uplink toward the router is carrying every VLAN the switch knows. The practice note lists two VLAN numbers, the name of each, which port faces the staff PC, which port faces the kiosk, and which port is the uplink. Build both VLANs, put each PC port in the VLAN the note assigns, and permit the uplink to carry only those two. The single-user VLAN from the earlier lab is not this closet.""",
"""After the two user VLANs and the pruned uplink are in place, the change record still shows a default device name. The incident note has the name that belongs on this switch. Apply that name. Do not widen the uplink and do not put the kiosk back into the staff VLAN.""")

add("sw-vlan-and-trunk",
"""A new printer was patched into the third access port after you built the walkthrough VLAN, and it cannot see the users subnet. The uplink on the first port should already be a trunk; do not turn it into an access port. The practice note names the VLAN and the name for the printer's port. Create that VLAN and put only the noted port into it. The walkthrough port stays where you left it.""",
"""The edge you just extended still answers with a lab default name, and the night engineer cannot tell it apart from the switch in the next rack. The incident note has the name for this box. Set the device name to that text. The printer VLAN and the trunk uplink both stay as they are.""")

add("sw-trunk-basics",
"""The uplink is a trunk, but it is still allowing every VLAN, including ones this building does not use. The practice note lists the only VLAN numbers that may cross to the next switch. Restrict the uplink to that list. Do not convert the uplink into an access port, and do not reuse a one-VLAN allowed list from the walkthrough if the note names a different pair.""",
"""The trunk list is correct and the switch still has a generic name, so the diagram and the prompt disagree. The incident note has the name operations expects on this uplink switch. Set the device name and leave the allowed VLAN list untouched.""")

add("sw-port-security",
"""A user port that was not part of the walkthrough keeps learning new addresses every time someone plugs in a laptop. The practice note names that port. Turn port security on there. The port you secured in the walkthrough is a different jack and does not satisfy this one.""",
"""Security is on the right jack, and the switch name in the prompt is still the lab default. The incident note has the closet name. Apply it. Leave port security enabled on both the walkthrough port and the port you just locked.""")

add("sw-banner",
"""Auditors want the login screen to show a short warning that is unique to this attempt, not the sample banner from the walkthrough. The practice note contains the exact token that must appear in the login banner. Put that token in the banner text. A banner that only repeats the walkthrough wording fails even if a banner exists.""",
"""The warning is on the login screen and the switch is still named like a spare. The incident note has the device name for this rack. Set it. Do not delete the banner you just wrote.""")

add("sw-describe",
"""The access port that faces the drop to the user desk has a description left over from a different room, so the diagram and the switch disagree. The practice note has the description text for FastEthernet0/2. Set that description exactly. The walkthrough description is a different string and will not pass.""",
"""The port description is right, and the switch name is still whatever the lab image shipped with. The incident note has the name for this access switch. Apply the name and leave the port description as you just set it.""")

add("sw-hostname-write",
"""You saved a walkthrough name earlier. Operations has now assigned a different name for this switch, written only in the practice note. Change the device name to that text. Showing the old name, or copying the walkthrough name again, does not finish the practice.""",
"""The new name is on the prompt. The port facing the user drop still has an empty or stale description. The incident note has the description for FastEthernet0/2. Set that description and do not rename the switch again.""")

add("sw-mac-table",
"""You have been reading the MAC table to see who is on the user ports. The table is evidence, not the change. The practice note now assigns this switch a name that is not the one in the walkthrough. Set the device name to the note. The address table can stay as it is.""",
"""With the name corrected, the user drop on the second access port still has no description, so a future tech cannot tell which jack it is. The incident note has the description text. Apply it on FastEthernet0/2 and leave the device name alone.""")

add("sw-int-status",
"""Interface status showed which ports are up. That reading does not rename the box. The practice note has the name this access switch should carry, different from the walkthrough. Set the device name from the note.""",
"""The prompt shows the new name. FastEthernet0/2, the jack toward the desks, still needs the description in the incident note. Put that text on the port. Do not shut the port and do not change the name again.""")

add("sw-show-ver",
"""The version screen told you what code this switch is running. The practice task is the name operations reserved for it, which is only in the practice note and is not the walkthrough name. Set the device name to the note.""",
"""Version and name now agree with the note. The incident asks for a description on the second access port so the patch panel label matches the switch. Use the description text in the incident note on FastEthernet0/2.""")

add("rtr-gateway",
"""A single PC on the near LAN can be reached only if this router owns that subnet and the interface is up. The walkthrough used a familiar address. The practice note names a different address and mask for GigabitEthernet0/1, which is the far side in this attempt. Address that interface and bring it up. Do not reuse the walkthrough address on either port.""",
"""The far interface answers and the router prompt is still a lab default, so the ticket cannot say which edge this is. The incident note has the router name. Apply it. Leave both interface addresses as they are.""")

add("rtr-two-interfaces",
"""You already proved two connected networks with the walkthrough addresses. A second site in this attempt uses a different far-side address, written only in the practice note, on GigabitEthernet0/1. Put that address and mask on the interface and make sure it is not administratively down. The near-side walkthrough address can stay.""",
"""Both LANs are numbered and the router is still called whatever the image booted with. The incident note has the name the diagram uses for this router. Set the device name. Do not renumber GigabitEthernet0/1.""")

add("rtr-edge-complete",
"""The edge router forwards for two LANs in the walkthrough. This attempt adds a different address on the second interface, because that LAN was renumbered. The practice note has the address and mask for GigabitEthernet0/1. Configure it and bring the interface up. Pings to the walkthrough hosts are not the goal.""",
"""Forwarding works and the hostname on the prompt is still the class default. The incident note names this router the way the change record does. Set that name and leave the interface addresses alone.""")

add("rtr-trace",
"""Traceroute showed where the walkthrough packets died. The practice task is different: GigabitEthernet0/1 needs the address in the practice note, with the mask written there, and the interface must be up. The trace you already ran does not configure that address.""",
"""The second interface is up with the noted address. The router name is still generic, so the path you traced cannot be filed under the right device. The incident note has the name. Set it.""")

add("rtr-default-route",
"""Users on the inside LAN reach each other and nothing beyond this router, because the default route still points at the walkthrough hop or is missing. The practice note has a different next hop. Install a default route that uses that hop. A route that still names the walkthrough hop does not pass.""",
"""The default route now points at the noted hop. The router itself is unnamed in the prompt, so the ticket looks like it was done on the wrong box. The incident note has the router name. Apply it and do not change the next hop.""")

add("rtr-vlan-acl",
"""Inter-VLAN routing is in place from the walkthrough, and a host that should not be reachable still is. The practice note names one host address to deny in a standard access list. Deny that single host. A list that only matches the walkthrough network does not meet the note.""",
"""The deny entry exists. The router name on the prompt is still the lab default, which the change record will reject. The incident note has the name. Set the device name and leave the access list in place.""")

add("rtr-describe",
"""GigabitEthernet0/0 faces the users LAN and its description still says something from the walkthrough, or nothing. The practice note has the description text for this attempt. Set that description on GigabitEthernet0/0. The walkthrough wording is a different string.""",
"""The interface description matches the note. The router name does not match the rack label. The incident note has the name. Apply it and do not edit the description again.""")

add("rtr-hostname-write",
"""You saved a walkthrough name on this router. The practice note now has a different name for this attempt. Change the device name to the note. Writing the walkthrough name a second time does not count.""",
"""The prompt shows the practice name. GigabitEthernet0/0 still needs the description in the incident note, which is not the walkthrough description. Set that description and leave the name as it is.""")

add("win-ipconfig",
"""You already recorded who this PC is. A second visit, for a different desk, must not reuse those DNS servers. The charting application fails by name and works by address. The practice note names the one DNS server this Ethernet adapter should use. Point the adapter at that server and leave the IPv4 address on automatic. The walkthrough servers fail the check.""",
"""DNS now matches the practice note, and the computer name is still the image default, so asset inventory will not find this desk. The incident note has the name to give this PC. Rename it to that text. Leave the DNS list you just set.""")

add("win-dns-break",
"""The walkthrough showed that a name failed while an address worked. Overnight a new application host was added, and the old resolver pair does not know it. The practice note names the single DNS server that does. Replace the DNS list with that one address. Do not flush and walk away; the server list itself has to change, and the address stays on DHCP.""",
"""Names resolve through the new server. The PC is still labeled with the training image name, so the ticket cannot be matched to a desk. The incident note has the computer name. Set it. Do not put the walkthrough DNS servers back.""")

add("win-dhcp-renew",
"""You cycled a lease in the walkthrough. This PC's name lookups still go to a resolver that was retired this morning. The practice note names the replacement DNS server. After you understand the current lease, point Ethernet at that DNS server only and leave the address on automatic. Releasing the lease is not a substitute for the DNS change.""",
"""The resolver is correct and the computer name is still the one from the image, which collides with another machine in the same closet. The incident note has the unique name. Apply it. The DNS server you set can stay.""")

add("win-full-triage",
"""The full triage you practiced used the image's DNS pair. This desk was moved to a wing whose resolver is different, and names for the file server fail. The practice note has that resolver's address. Make it the only DNS server on Ethernet. Keep the IPv4 address on DHCP. Do not stop after a flush.""",
"""Lookups follow the noted server. Inventory still shows the image computer name, so the move ticket is incomplete. The incident note has the name this PC should carry after the move. Set that name and leave DNS as you just configured it.""")

add("w11-inventory",
"""You inventoried edition, build, and the signed-in user. None of that tells you which DNS server this wing uses. The practice note names the DNS server for this inventoried PC. Set Ethernet to that server and leave the address automatic. The servers you saw during inventory are the old ones.""",
"""The DNS list matches the note. The computer name you inventoried is the image name, and asset tags were reprinted. The incident note has the new computer name. Rename this PC to it. Edition and build do not change.""")

add("w11-powershell-net",
"""The adapter summary showed the image DNS servers. A branch file server was renumbered in DNS only, and this PC still asks the old pair. The practice note has the server that holds the new record. Set that as the Ethernet DNS server. Leave the IPv4 address on automatic so the lease remains valid.""",
"""The network view should now show the noted DNS server. The computer name is still the training name, which the branch inventory rejects. The incident note has the replacement name. Apply it. Do not revert the DNS server.""")

add("w11-services",
"""DHCP, the DNS client, and Defender are running, which you already proved. Lookups still fail because the DNS server list points at a retired host. The practice note names the live DNS server. Point Ethernet at it and leave the address on DHCP. Restarting a service is not the change this stage checks.""",
"""The resolver address is right and the services you checked can stay running. The computer name does not match the sticker on the chassis. The incident note has the sticker text. Rename the PC to that name.""")

add("w11-netsh",
"""You read the Ethernet block with the older interface tool and with the usual address listing. Both showed the image DNS servers. Those servers are wrong for this attempt. The practice note has the DNS server to configure. Set it on Ethernet and leave DHCP handing out the address.""",
"""Both tools should now agree on the DNS server from the practice note. The computer name on this older-tool PC is still the image name. The incident note has the name this older-tool PC should carry. Set it, and do not clear the DNS server back to the image pair.""")

add("w11-processes",
"""You listed processes from both shells so you would not kill the wrong one. Nothing in that list fixes the resolver. The practice note names the DNS server this PC should ask. Set that server on Ethernet and leave the IPv4 address automatic. Do not stop a process as a substitute.""",
"""DNS matches the note. The computer name is still the generic training name, which collides in the process logs with another image. The incident note has the distinct name. Rename this PC. Leave the process list and the DNS server as they are.""")

add("w11-firewall",
"""The firewall profiles are on, which you confirmed. Name resolution still uses a DNS server that is not the one this site published. The practice note has the DNS server address. Configure Ethernet to use it and keep the address on automatic. Turning a firewall profile off is not the task.""",
"""The DNS server is the one in the practice note and the profiles stay on. The computer name does not match the exception the firewall team wrote down. The incident note has that name. Rename the PC to it.""")

add("w11-disk",
"""You listed the disks and proved which volume is online. That does not fix the share name that fails while the file server's address answers. The practice note names the DNS server that has the share. Point Ethernet at it. Leave the disk layout and the DHCP address alone.""",
"""The share can resolve once DNS matches the note. The computer name is still the image name, so disk reports from two PCs look identical. The incident note has the name for this machine. Set it.""")

add("w11-wlan",
"""The wireless report showed the radio. The failure users care about is the wired Ethernet DNS list, which still names the image resolvers. The practice note has the DNS server for this site. Set it on Ethernet and leave the IPv4 address on automatic. Do not try to join a wireless network as the fix.""",
"""Ethernet DNS matches the note. The computer name in the wireless report header is still the image name. The incident note has the name that should appear there. Rename the PC.""")

add("win-arp",
"""The ARP cache showed who answered on the local subnet. A name off that subnet still fails. The practice note names the DNS server that should answer for those names. Set Ethernet's DNS server to it and leave the address on DHCP. Clearing ARP is not the check.""",
"""DNS is the noted server. The computer name is still the training name, so the ARP notes cannot be filed to an asset. The incident note has the computer name. Apply it.""")

add("win-route",
"""The route table shows a default gateway and the image DNS servers are a separate problem. Names fail. The practice note has the DNS server for this attempt. Point Ethernet at that server only. Do not delete the default route and do not switch the address off DHCP.""",
"""Routes are unchanged and DNS matches the note. The computer name is the image default, which the route ticket template will not accept. The incident note has the name. Set it.""")

add("win-getmac",
"""You recorded the physical address. The help desk still cannot resolve the file server name from this PC. The practice note names the DNS server to use. Configure that server on Ethernet and leave DHCP enabled for the address. The MAC does not change.""",
"""The physical address is the same and DNS is the noted server. The computer name does not match the asset row that holds the MAC. The incident note has the name. Rename the PC to it.""")

add("win-netstat",
"""Active connections showed who this PC is talking to. The DNS server in that list is the retired one. The practice note names the replacement. Set Ethernet to that DNS server and leave the IPv4 address on automatic. Closing sockets is not the goal.""",
"""New lookups should go to the noted server. The computer name on this endpoint is still the image name, so the connection log is ambiguous. The incident note has the name. Apply it and leave the DNS list.""")

add("win-hostname",
"""You printed the image computer name. Practice does not ask you to print it again. The practice note names a DNS server that is not the image pair. Point Ethernet at that server and leave the address on automatic. The name you already printed stays until the incident stage.""",
"""DNS matches the practice note. Now the computer name you printed at the start is wrong for the asset tag. The incident note has the replacement name. Rename the PC to that text. Do not revert DNS.""")

add("win-ping-loop",
"""Loopback answered, so the stack is up. A name beyond this PC still fails. The practice note names the DNS server that should resolve it. Set that server on Ethernet. Leave the address on DHCP. Another loopback test does not change the resolver.""",
"""The resolver is the noted server. The computer name is still the image name, which makes two loopback tests look like the same PC. The incident note has the distinct name. Set it.""")

add("win-nslookup-ok",
"""A name looked up successfully against the image DNS servers. This attempt must use a different server, the one in the practice note, because the image servers will be decommissioned. Replace the DNS list with that single address and leave DHCP in charge of the IPv4 address.""",
"""Lookups now use the noted server. The computer name is the image name, so the successful lookup cannot be tied to the right desk. The incident note has the computer name. Rename this PC.""")

add("win-flushdns",
"""You cleared the resolver cache. The cache filled again from the same retired DNS servers. The practice note names the server that should be queried instead. Set Ethernet's DNS server to that address and leave the IPv4 address automatic. Flushing again, without changing the server, will not pass.""",
"""The DNS server list matches the note, so a flush is no longer the fix. The computer name is still the training image name. The incident note has the name to give this PC after the cache lesson. Set it and leave the DNS server in place.""")

add("win-net-cli",
"""You proved a name failed while an address worked, using the image DNS servers. The practice note names the resolver that actually hosts the record. Make that the only DNS server on Ethernet. Keep the address on DHCP. Do not stop after showing that the name fails.""",
"""The failing name should resolve once the noted server is configured. The computer name is still the image default and the evidence cannot be assigned to a desk. The incident note has the computer name. Apply it.""")

add("print-trouble",
"""The laser in HR answers by address and the share name does not resolve, so the queue looks down. The practice note names the DNS server that has the printer's name. Point Ethernet at that server and leave the IPv4 address on automatic. Clearing a job without fixing the resolver leaves the next name lookup broken.""",
"""The printer name can resolve. This PC is still called the image name, so the print server's notes do not match the asset tag. The incident note has the computer name. Rename the PC. Leave the DNS server you set for the printer name.""")

add("win-laptop-ports",
"""Mail tests and the battery report told you about this laptop. Name lookups for the mail host still use the image DNS servers. The practice note names the DNS server for this clinic. Set it on Ethernet and leave the address on DHCP. The port tests you already ran are not the practice goal.""",
"""DNS matches the clinic note. The computer name is the image name, so the mail exception list does not include this laptop. The incident note has the name. Rename the PC to it.""")

add("win-wifi-survey",
"""You surveyed the wireless cell. The wired Ethernet adapter, which the survey does not reconfigure, still uses the image DNS servers. The practice note names the DNS server for the building. Set that on Ethernet and leave the IPv4 address automatic. Reconnecting to a wireless network is not this stage.""",
"""Ethernet DNS is the noted server. The computer name in the survey header is the image name. The incident note has the name that should be on this laptop. Set it.""")

add("hv-vswitch",
"""You worked a virtual switch and checkpoints on the host. The host's own Ethernet DNS list is still the image pair, so the management name of a guest fails. The practice note names the DNS server for the host. Set it and leave the host address on automatic. Creating another virtual switch is not the check.""",
"""The host resolver matches the note. The host computer name is still the image name, which collides with the other lab host. The incident note has the host name. Rename this computer. Leave the virtual switch you already built.""")

add("gui-about",
"""About showed the image computer name and the build. It did not change which DNS server this PC asks. The practice note, opened from the desk beside Settings, names the DNS server for this attempt. Apply that server in the simulation's network settings and leave the address on automatic. The servers visible in About's network story are the old ones.""",
"""The DNS server in the simulation matches the practice note. About will still show the image computer name until you change it. The incident note has the name. Set the computer name in the simulation to that text. This desk is a simulation, not a Windows PC.""")

add("gui-ethernet",
"""Ethernet properties showed the image DNS servers. A moved desk needs a different resolver, written only in the practice note. Set that DNS server in the simulation and leave the IPv4 address automatic. Reading the properties again without changing them does not pass.""",
"""Ethernet now lists the noted DNS server. The computer name in the simulation is still the image name. The incident note has the replacement. Set the computer name and leave the DNS server.""")

add("gui-renew",
"""You disabled and enabled the adapter to renew the lease. The DNS servers that came back are still the image pair. The practice note names the DNS server this adapter should keep. Set it in the simulation. Cycling the adapter again is not a substitute.""",
"""The lease path is fine and DNS matches the note. The computer name was not part of the renew. The incident note has the name for this PC. Set it in the simulation.""")

add("gui-services",
"""You confirmed DHCP, the DNS client, and Defender in Services. The DNS server list is a separate setting and still points at the image resolvers. The practice note names the server to use. Set it in the simulation's network fields and leave the address automatic. Do not stop those services.""",
"""Services stay running and DNS matches the note. The computer name shown in the simulation is the image name. The incident note has the name. Apply it.""")

add("gui-update",
"""You checked for updates and read the result. Updates do not select a DNS server. The practice note names the resolver for this PC. Set that DNS server in the simulation and leave DHCP in charge of the address. Checking for updates again is not the practice goal.""",
"""The DNS server is the one in the practice note. Windows Update is unchanged. The computer name is still the image name, which the update ring groups by name. The incident note has the name to set in the simulation.""")

add("gui-accounts",
"""You read the signed-in account. The account is not the DNS server. The practice note names the DNS server for this signed-in session's PC. Set it in the simulation and leave the address on automatic. Switching accounts is not the check.""",
"""DNS matches the note and the signed-in account can stay. The computer name is the image name, so the account report is ambiguous. The incident note has the computer name. Set it in the simulation.""")

add("gui-devices",
"""Device Manager showed the network adapter and the display adapter. The adapter's DNS servers are still the image pair. The practice note names the DNS server. Set it in the simulation. Disabling the display adapter does nothing for this stage.""",
"""The DNS server matches the note and both adapters stay present. Device Manager's PC is still using the image computer name. The incident note has the name. Set it in the simulation.""")

add("win-ad-users",
"""You created and adjusted accounts in the directory UI. Those accounts still resolve names through the image DNS servers on this PC. The practice note names the DNS server for the console you are on. Set it in the simulation and leave the address automatic. Do not delete the users you already created.""",
"""Directory changes remain and DNS matches the note. This console PC still has the image computer name, so the directory notes do not say which station did the work. The incident note has the computer name. Set it in the simulation.""")

add("linux-shell",
"""The nightly backup on the simulator is fixed from the walkthrough, and a different private note is now required. A file in your home directory, whose name starts with note-, holds one line, a destination path, and a mode. Create that file with that exact line and that mode. The walkthrough file under support is a different path and will not pass.""",
"""The practice file is in place. The incident section of the same note names a second line, a second path, and a tighter mode. Create that second file. Do not overwrite the practice file and do not reuse the line you wrote first.""")

add("linux-vm-perms",
"""The night-shift notes file from the walkthrough is done. A different private line has to exist for this attempt, and the grader reads the real disk. In root's home directory, a text file whose name starts with note- contains a line, a path, and a mode. Create that path with that line and that mode. The support notes from the walkthrough are not the proof file.""",
"""The practice proof is on disk. The incident section of the note names another line, another path, and a mode that removes group read. Create that file on this same machine. Leave the practice proof and the tech1 notes file from the walkthrough untouched.""")

add("linux-vm-shell",
"""The backup script on novak-lnx-01 runs. A separate proof file is required for this attempt, not the report you locked down. Root's home directory has a note file whose name starts with note-. It contains a line, a path, and a mode. Write that line to that path and set that mode. Grepping the old app log is not this stage.""",
"""The practice proof exists. The incident half of the note asks for a second file with a different line and a mode that is not the practice mode. Create it. Do not chmod the walkthrough report again and do not delete the practice proof.""")

add("linux-vm-services",
"""You stopped the runaway job and repaired the service from the walkthrough. This attempt also wants a short proof file the grader can read. The note file in root's home directory, name starting with note-, gives a line, a path, and a mode. Create that file. Restarting the heartbeat is not a substitute for the file.""",
"""The practice proof is on the box. The incident section names a second proof with its own line and a stricter mode, for the handoff after the service repair. Create that file and leave the practice proof and the repaired service in place.""")

add("linux-vm-netclient",
"""The client has a real lease from the walkthrough. This attempt also requires a proof file so the ticket can be matched to the lease you saw. The note in root's home directory, named note-something, holds a line, a path, and a mode. Write the file exactly that way. A second DHCP renew does not create it.""",
"""The practice proof matches the note. The incident section asks for another file, different line and tighter mode, recording the gateway you ended on. Create it. Do not release the lease and do not remove the practice file.""")

add("linux-vm-routing",
"""Forwarding between the two machines works from the walkthrough. The proof of this attempt is a file on the primary machine, not another ping. On the first console, root's home directory contains a note file starting with note-. It names a line, a path, and a mode. Create that file there. Do not put it only on the router VM.""",
"""The practice proof is on the primary machine. The incident section of that same note names a second file, a second line, and a mode without group read. Create it on the primary machine. Leave forwarding and the practice file as they are.""")

add("linux-vm-logs",
"""You found the error in the rotated log. The handoff for this attempt is a proof file, not another grep. Root's home on this log host has a note whose name starts with note-, with a line, a path, and a mode. Create that file with that line and mode. The log line you already found stays in the log.""",
"""The practice proof is written. The incident section wants a second file, its own line and a tighter mode, summarizing the source you would block. Create that file. Do not truncate the log and do not replace the practice proof.""")

add("linux-vm-cron",
"""The scheduled job from the walkthrough fires. This attempt wants a proof file the checker can see, separate from the cron spool. The note in root's home directory, name starting with note-, gives the line, the path, and the mode. Create the file. Editing the walkthrough crontab again is not the check.""",
"""The practice proof exists. The incident section names a second file and a stricter mode, for the note you would leave the next operator. Create it. Leave the working cron job and the practice file alone.""")

add("linux-vm-users",
"""The walkthrough account and sudo entry exist. This attempt's proof is a file, not another user. A note file in root's home directory, starting with note-, contains a line, a path, and a mode. Create that file. Do not delete the user you already added.""",
"""The practice proof is on disk. The incident section asks for a second file with a different line and a mode that is not group-readable. Create it. Leave the walkthrough user, sudo, and the practice file in place.""")

add("linux-vm-packages",
"""The conflicting listener from the walkthrough is understood. This attempt also stores a proof file the grader reads from the real disk. The note in root's home on the package host, name starting with note-, has a line, a path, and a mode. Write that file. Installing another package is not the stage.""",
"""The practice proof matches. The incident section names a second path, a second line, and a tighter mode, as the record that the port conflict is gone. Create that file and leave the package state and the practice proof.""")

add("linux-vm-firewall",
"""The host firewall from the walkthrough is what the second machine can or cannot reach. This attempt's written proof is a file on the firewall machine. Root's home there has a note starting with note-, with a line, a path, and a mode. Create that file on the firewall VM. A new iptables rule is not the proof.""",
"""The practice proof is on the firewall host. The incident section wants another file, different line and stricter mode, stating which side you proved. Create it on the same VM. Do not flush the filter table and do not remove the practice file.""")

add("linux-vm-disk",
"""The filesystem and fstab work from the walkthrough. The proof for this attempt is not another mount. In root's home, a note file whose name starts with note- gives a line, a path, and a mode. Create that file. Unmounting the walkthrough volume would only break the earlier work.""",
"""The practice proof exists beside the mounted volume. The incident section names a second file and a tighter mode, as the record of the UUID you used. Create it. Leave fstab and the practice proof alone.""")

add("linux-vm-ssh",
"""Key login from the walkthrough is done and passwords are off. This attempt wants a proof file on the primary machine, not another key. Root's home on that machine has a note starting with note-, containing a line, a path, and a mode. Create the file there. Do not turn passwords back on.""",
"""The practice proof is in place. The incident section names a second file, another line, and a mode without group read, for the record of which account can log in. Create it. Leave sshd and the practice file as they are.""")

add("linux-vm-script",
"""The backup script from the walkthrough passes its test. This attempt's proof is a separate file, not a second run of that script. The note in root's home directory, name starting with note-, holds a line, a path, and a mode. Write it. Do not point the script at a different directory unless the note says that path.""",
"""The practice proof exists. The incident section asks for a second file with its own line and a stricter mode, as the operator note after a restore drill. Create that file. Leave the working script and the practice proof.""")

add("linux-vm-dns",
"""The resolver from the walkthrough answers the name you repaired. This attempt also wants a proof file on the DNS VM. Root's home on the resolver has a note starting with note-, with a line, a path, and a mode. Create that file on the DNS machine. Querying the name again is not the file.""",
"""The practice proof is on the DNS VM. The incident section names a second file and a tighter mode, recording the forwarder you set. Create it there. Do not break the zone and do not delete the practice proof.""")

add("linux-vm-nettrouble",
"""The multi-hop path from the walkthrough reaches the far host. The written proof for this attempt is a file on the primary machine. In root's home on that machine, a note starting with note- gives a line, a path, and a mode. Create the file there. Another traceroute does not write it.""",
"""The practice proof matches the note. The incident section wants a second file, different line and stricter mode, for the hop that was actually broken. Create it on the primary machine. Leave routes and the practice file.""")

add("linux-vm-perf",
"""You found what was burning CPU or memory. The handoff file for this attempt is separate from killing that process. Root's home on this busy host has a note whose name starts with note-, with a line, a path, and a mode. Create that file. The process you already dealt with can stay stopped.""",
"""The practice proof is written. The incident section names a second file and a tighter mode, as the note of what you would watch next. Create it. Do not start the runaway job again and do not replace the practice proof.""")

add("linux-vm-restore",
"""The walkthrough restore opened the right file. This attempt wants its own proof file, not a second restore of the same archive. The note in root's home after the restore, name starting with note-, contains a line, a path, and a mode. Create that file. Restoring over the walkthrough copy is not the goal.""",
"""The practice proof exists. The incident section asks for another file, its own line and a mode that drops group read, recording where you restored. Create it. Leave the restored data and the practice proof.""")

add("linux-vm-web",
"""The intranet page from the walkthrough loads. This attempt's proof is a file on the web VM, not a second curl. Root's home on that machine has a note starting with note-, with a line, a path, and a mode. Create the file there. Do not change the document root unless the note's path says so.""",
"""The practice proof is on the web VM. The incident section names a second file and a stricter mode, for the record of the page you verified. Create it. Leave the site and the practice proof in place.""")

add("linux-vm-nat",
"""The edge translates and forwards from the walkthrough. The proof file for this attempt belongs on the primary machine, not as another NAT rule. Root's home there has a note starting with note-, giving a line, a path, and a mode. Create that file on the primary VM. Do not flush the NAT table.""",
"""The practice proof matches. The incident section wants a second file, different line and tighter mode, noting which address was translated. Create it on the primary machine. Leave NAT and the practice file.""")

add("linux-vm-incident",
"""You removed the persistence from the walkthrough. This attempt still needs a proof file the grader can read, separate from the malicious job. The note in root's home after the cleanup, name starting with note-, has a line, a path, and a mode. Create that file. Do not put the walkthrough token in it.""",
"""The practice proof is on disk. The incident section names a second file and a stricter mode, as the timeline note after the cleanup. Create it. Do not restore the persistence mechanism and do not overwrite the practice proof.""")

add("linux-vm-ipv6",
"""IPv6 reachability from the walkthrough is in place. This attempt's proof is a file on the primary machine, not another ping6. Root's home on the IPv6 client has a note starting with note-, with a line, a path, and a mode. Create the file. Do not remove the address you already configured.""",
"""The practice proof exists. The incident section asks for a second file, another line, and a mode without group read, recording the default router you observed. Create it on the primary machine. Leave IPv6 and the practice file.""")

add("linux-vm-method",
"""The time-clock service from the walkthrough answers. The method note for this attempt is a proof file, not another edit of the service file. Root's home has a note whose name starts with note-, containing a line, a path, and a mode. Create that file. Do not undo the service repair.""",
"""The practice proof is written. The incident section names a second file and a tighter mode, as the close-out after you verified the page. Create it. Leave the service, the page, and the practice proof.""")

add("linux-gui-network",
"""The guided profile used a published address. This desktop's practice ticket, a file on the desktop, names a different address, prefix, gateway, and DNS server. Save a profile from those four fields. Do not type the guided numbers again. Saving the profile stores it; it does not have to be the live address yet.""",
"""A file on the desktop whose name starts with INC- describes the address that must be live on the wire, including prefix, gateway, and DNS. Apply that configuration to the interface, not only as a saved profile. The guided profile and the practice profile can remain on disk. Confirm the live address, the default route, and DNS against the incident file.""")

add("linux-gui-disks",
"""The data image is already mounted from the walkthrough. The practice ticket on the desktop names a different image, a mount point, and options. Mount that image at that point with those options, and record it so it survives a reboot. Do not remount the walkthrough image over the new path.""",
"""An incident file on the desktop, name starting with INC-, names yet another image, mount point, and options. Mount that one as well, with a persistent entry. The two earlier mounts stay. A mount that exists only in the form and not on the system does not pass.""")

add("linux-gui-firewall",
"""SSH and the web port are already allowed from the walkthrough. The practice ticket on the desktop names an additional TCP port that must be allowed. Add that port and leave the earlier allows in place. Do not lock yourself out by dropping the existing SSH allow.""",
"""The incident file on the desktop, name starting with INC-, names an address to block. Block that source and keep the allows you already added. The address from any walkthrough example is the wrong one if it is not the address in the incident file.""")

add("linux-gui-users",
"""tech1 is unlocked and has sudo from the walkthrough. The practice ticket on the desktop names a different account, and a file with a mode. Unlock that account, grant sudo, and set the file to the mode in the ticket. Do not lock tech1 while you do it.""",
"""The incident file on the desktop, name starting with INC-, names another account and another file mode. Unlock that account, grant sudo, and apply that mode. The practice account stays unlocked. A mode copied from the walkthrough file fails if the incident file names a different one.""")

add("linux-gui-logs",
"""You already blocked the sample source from the walkthrough. The practice ticket on the desktop points you at the message log and a different address, the one that failed most often in this attempt. Block that address. Do not remove the walkthrough block if it is still appropriate, and do not block an address that is not in the ticket.""",
"""The incident file on the desktop, name starting with INC-, names another source to block after you read the log. Block that source too. Then rotate the log the way the desktop tools offer, so the next shift is not reading a file that has already been archived. The practice block stays.""")

add("linux-gui-processes",
"""cpu-hog is stopped from the walkthrough, and swappiness may already be lowered. The practice ticket on the desktop names a different process that is still running. Stop that process. Do not stop unrelated system processes, and do not start cpu-hog to 'test' the ticket.""",
"""The incident file on the desktop, name starting with INC-, names one more process to stop. Stop it. Leave swappiness where the walkthrough set it unless the incident file tells you a number, and do not revive the practice process.""")

add("linux-gui-packages",
"""The walkthrough package is installed. The practice ticket on the desktop names a different package from the local repository. Install that package. It is not the package you already added, and a name you remember from the walkthrough will not match the ticket.""",
"""The incident file on the desktop, name starting with INC-, describes an hourly job: a minute and a command line that must be scheduled. Enable that job. Leave the package you just installed. The minute and the command come from the file, not from the walkthrough.""")

add("linux-gui-ssh",
"""Root login and passwords were closed in the walkthrough, with a key. The practice ticket on the desktop names one account that must be the only account allowed to sign in over SSH. Allow that account and do not reopen passwords or root login.""",
"""The incident file on the desktop, name starting with INC-, moves the SSH service to a different port and asks you to test the configuration. Change the port to the one in the file and check that the configuration is accepted. The account allow from practice stays. Do not switch the service back to the walkthrough port.""")

add("sec-vm-iptables",
"""The walkthrough firewall rules are on this host. The proof the grader reads is a file, not another rule. Root's home contains a note whose name starts with note-, with a line, a path, and a mode. Create that file. Do not set the input policy to accept while you write it.""",
"""The practice proof is on disk. The incident section of the note names a second file, a different line, and a tighter mode, as the record of which source you limited. Create it. Leave the firewall rules and the practice proof.""")

add("sec-vm-perms",
"""The secret from the walkthrough is no longer world-readable. This attempt wants its own proof file. The note in root's home beside the secret, name starting with note-, gives a line, a path, and a mode. Create that file with that mode. Do not chmod the walkthrough secret back to a looser mode.""",
"""The practice proof exists. The incident section names another file and a mode that is not the practice mode, for the handoff after the permission change. Create it. Leave the secret's mode and the practice file.""")

add("sec-vm-suid",
"""You found the unexpected setuid file in the walkthrough. The proof for this attempt is a separate file the grader can read. Root's home after the setuid hunt has a note starting with note-, with a line, a path, and a mode. Write it. Do not set the setuid bit on the proof file.""",
"""The practice proof is in place. The incident section asks for a second file, its own line and a stricter mode, naming what you would remove. Create it. Do not restore the setuid bit on the walkthrough file.""")

add("sec-vm-users",
"""The leaver is locked and sudo is dropped from the walkthrough. This attempt's proof is a file, not another account change. The note in root's home after the lockout, name starting with note-, contains a line, a path, and a mode. Create that file. Do not unlock the leaver.""",
"""The practice proof matches the note. The incident section names a second file and a tighter mode, as the record of whose sudo you removed. Create it. Leave the locked account and the practice proof.""")

add("sec-vm-ssh",
"""Passwords are off and a key works from the walkthrough. The proof file for this attempt is not another key. Root's home on the primary machine has a note starting with note-, with a line, a path, and a mode. Create the file there. Do not turn password logins back on.""",
"""The practice proof exists. The incident section wants a second file, different line and stricter mode, recording which login method remains. Create it. Leave sshd and the practice file.""")

add("sec-vm-authlog",
"""You counted the failed logins in the walkthrough. This attempt wants that count's handoff as a file, not another pass through the log. The note in root's home beside the auth log, name starting with note-, gives a line, a path, and a mode. Create the file. Do not delete the auth log.""",
"""The practice proof is written. The incident section names a second file and a tighter mode, for the source you would block after reading the failures. Create it. Leave the log and the practice proof.""")

add("sec-vm-cron",
"""The suspicious scheduled job from the walkthrough is handled. The proof is a file, not a second edit of the spool. Root's home after the spool check has a note starting with note-, with a line, a path, and a mode. Create that file. Do not re-enable the suspicious job.""",
"""The practice proof is on disk. The incident section asks for another file, its own line and a stricter mode, stating what the job was trying to run. Create it. Leave the spool clean and the practice proof in place.""")

add("sec-vm-proc",
"""The suspicious process from the walkthrough is stopped. This attempt's proof file is separate from that process. The note in root's home beside the stopped process, name starting with note-, has a line, a path, and a mode. Create the file. Do not start the process again to capture its name.""",
"""The practice proof exists. The incident section names a second file and a tighter mode, as the note of the command line you observed. Create it. Leave the process stopped and the practice file untouched.""")

add("sec-vm-hash",
"""You compared a fingerprint in the walkthrough. This attempt wants a proof file, not a second hash of the same target pasted into the old file. The note in root's home beside the fingerprint, name starting with note-, gives a line, a path, and a mode. Create that file. The fingerprint you already computed can stay in your notes.""",
"""The practice proof is written. The incident section asks for a second file, different line and stricter mode, recording whether the fingerprint matched. Create it. Do not overwrite the file you hashed.""")

add("sec-vm-grep",
"""You extracted lines from the log in the walkthrough. The proof for this attempt is its own file. Root's home after the extract has a note starting with note-, with a line, a path, and a mode. Create that file with that line. Do not append the proof into the log you searched.""",
"""The practice proof matches. The incident section names a second file and a tighter mode, holding the extract you would hand to the next shift. Create it. Leave the original log and the practice proof.""")

add("sec-vm-backup",
"""The walkthrough archive and checksum exist. This attempt wants a separate proof file, not another copy of the archive. The note in root's home beside the archive, name starting with note-, contains a line, a path, and a mode. Create that file. Do not delete the archive to make room.""",
"""The practice proof is on disk. The incident section asks for a second file, its own line and a stricter mode, noting the checksum result. Create it. Leave the archive and the practice proof.""")

add("sec-vm-world",
"""The world-writable file from the walkthrough is closed. This attempt's proof is a different file. The note in root's home beside the closed file, name starting with note-, gives a line, a path, and a mode. Create it. Do not make the proof world-writable.""",
"""The practice proof has the right mode. The incident section names another file and a tighter mode, as the record of which path you closed. Create it. Leave the walkthrough file closed and the practice proof in place.""")

add("sec-vm-sudo",
"""Least-privilege sudo from the walkthrough is in place. The proof file for this attempt is not another sudoers line. Root's home after the sudoers edit has a note starting with note-, with a line, a path, and a mode. Create that file. Do not grant ALL to the practice file's owner.""",
"""The practice proof exists. The incident section wants a second file, different line and stricter mode, naming the command you allowed. Create it. Leave the sudoers drop-in and the practice proof.""")

add("sec-vm-capture",
"""You read the capture transcript in the walkthrough. This attempt wants a proof file, not a second reading pasted nowhere. The note in root's home next to the transcript, name starting with note-, has a line, a path, and a mode. Create that file. Do not edit the transcript.""",
"""The practice proof is written. The incident section names a second file and a tighter mode, for the port and host you would call out from the capture. Create it. Leave the transcript and the practice proof.""")

add("sec-vm-timeline",
"""The walkthrough timeline is assembled. This attempt's proof file is the piece the grader reads, separate from the timeline notes you already made. The note in root's home beside the timeline, name starting with note-, gives a line, a path, and a mode. Create that file.""",
"""The practice proof matches. The incident section asks for another file, its own line and a stricter mode, with the order you would brief. Create it. Do not rewrite the walkthrough timeline over the practice file.""")

add("sec-vm-fim",
"""The integrity check from the walkthrough is done. This attempt wants a proof file of its own. Root's home beside the integrity baseline has a note starting with note-, with a line, a path, and a mode. Create the file. Do not update the baseline to hide a change you have not explained.""",
"""The practice proof is on disk. The incident section names a second file and a tighter mode, recording whether the baseline matched. Create it. Leave the baseline and the practice proof.""")

add("sec-vm-harden",
"""The extra process from the walkthrough is stopped. The proof for this attempt is a file, not another kill. The note in root's home after the extra process stopped, name starting with note-, contains a line, a path, and a mode. Create that file. Do not disable a service the note does not mention.""",
"""The practice proof exists. The incident section wants a second file, different line and stricter mode, naming the process you stopped. Create it. Leave that process stopped and the practice file in place.""")

add("sec-vm-faillock",
"""Password aging from the walkthrough is visible. This attempt's proof is a file, not another aging report. Root's home beside the aging report has a note starting with note-, with a line, a path, and a mode. Create the file. Do not set an empty password while you write it.""",
"""The practice proof is written. The incident section names a second file and a tighter mode, for the aging value you would change. Create it. Leave the account's aging and the practice proof.""")

add("sec-openssl",
"""The key and request from the walkthrough exist. This attempt wants a proof file, not a second key in the same path. The note in root's home beside the key, name starting with note-, gives a line, a path, and a mode. Create that file. Do not overwrite the private key.""",
"""The practice proof is on disk. The incident section asks for another file, its own line and a stricter mode, noting what the request was for. Create it. Leave the key, the request, and the practice proof.""")

add("ticket-intake",
"""The walkthrough ticket was an unplanned outage. The practice note describes a different request sitting in the queue. Read it and submit one line with the type, how many people are affected, and whether it escalates, using the words this desk already uses. The walkthrough classification will be wrong if the note is a single person's request.""",
"""A second item arrived while you were classifying the first. The incident note is that item. Submit its type, impact, and escalation as one line. Do not reuse the practice line if the story changed from one person to many, or from a request to an outage.""")

add("hw-board",
"""The walkthrough board is not the one on this bench. The practice note describes the board in front of you: size, slots, and what kind of case it fits. Submit the form-factor word that matches the description. Guessing the walkthrough board fails when the note describes a different size.""",
"""A second board is on the side bench. The incident note describes it. Submit the form-factor word for that description. The practice answer stays in your notes and is not automatically right for this board.""")

add("net-subnet",
"""A planner hands you an address and a prefix length in the practice note, different from any network you already calculated. Submit only the network address for that prefix. A host address, a broadcast address, or a prefix you memorized from the walkthrough will not match.""",
"""The incident note has a second address and prefix, in a different private range. Submit that network address and nothing else. The practice network is a different block.""")

add("hw-cables",
"""A technician describes a connector and a job in the practice note, not the set you matched in the walkthrough. Submit the outcome word the note's choices allow for that connector and that job. Matching by the picture you remember, instead of the note, fails when the connector changed.""",
"""The incident note describes a different cable and a different job. Submit the outcome for that description. The practice choice is not evidence for this one.""")

add("hw-pc-build",
"""The quote in the practice note is a different budget and a different requirement than the walkthrough build. Submit the outcome the note asks for: the part or the decision that fits those constraints. A build that only repeats the walkthrough parts fails the new budget.""",
"""The incident note is a second quote, with its own constraint. Submit the outcome for that quote. Do not assume the practice pick still fits.""")

add("ticket-method",
"""The practice note is a fresh symptom, not the outage you ordered in the walkthrough. Submit the next step or the classification the note's story supports. Skipping ahead because the walkthrough's order felt familiar is how this one goes wrong.""",
"""The incident note is a second symptom with a different scope. Submit the outcome for that story. The practice step was for the other user.""")

add("wifi-secure",
"""The lobby router in the practice note is not in the state you left the walkthrough router. Read what it is doing now and submit the outcome word the note allows: harden it, or leave it. A passphrase you remember from the walkthrough is not the decision.""",
"""The incident note describes a second radio, staff or guest, in a different state. Submit the outcome for that radio. Do not copy the practice decision if this one is already strict.""")

add("sec-malware",
"""The pop-up in the practice note is a different moment than the walkthrough case. Submit the action the note's facts support: isolate, preserve, or document. Speed is not the goal if the note says the user has not clicked yet, or that the files are already encrypted.""",
"""The incident note is a later moment, or a different machine. Submit the action for those facts. The practice action was for the other screen.""")

add("ops-backup",
"""The practice note describes a backup design that may or may not meet a real copy count, a second medium, an off-site copy, and a tested restore. Submit accept or reject for that design. A plan you liked in the walkthrough is not this design.""",
"""The incident note describes a second design. Submit accept or reject for it. The practice verdict does not transfer.""")

add("virt-vm",
"""The practice note describes a virtual machine request: who needs it, and which kind of hypervisor or network the story implies. Submit the outcome word the note allows. Sizing from the walkthrough VM will be wrong if this request is a different workload.""",
"""The incident note is another request, with a different constraint. Submit the outcome for that request. Do not reuse the practice choice without reading it.""")

add("mob-mdm",
"""A phone in the practice note is out of policy in a way the walkthrough device was not. Submit the outcome the note allows. Bypassing enrollment because it is faster fails when the note says the device is corporate.""",
"""The incident note is a second device, personal or corporate, with a different ask. Submit the outcome for that device. The practice decision was about the other phone.""")

add("sec-gpg",
"""The practice note describes one message or file and what the sender wants done with it. Submit the outcome the note allows for encrypting or decrypting. Do not invent a key, and do not treat the walkthrough choice as this message.""",
"""The incident note is a second payload, with a different request. Submit the outcome for that payload. The practice decision does not automatically apply.""")

add("sec-win-fw",
"""The practice note describes one proposed firewall allow: who, which port, and how wide. Submit the outcome the note allows for whether that allow is safe. An allow you approved in the walkthrough was a different port and a different source.""",
"""The incident note proposes a different allow. Submit the outcome for that proposal. Width and source are in the note, not in the practice answer.""")

add("sec-win-policy",
"""The practice note describes an account-policy change someone wants: length, lockout, or age. Submit the outcome the note allows. A stricter number is not always the right one if the note says the change would lock out the night shift.""",
"""The incident note is a second policy request. Submit the outcome for that request. The practice threshold was for the other setting.""")

add("sec-win-events",
"""The practice note quotes one event-log line and who reported it. Submit the outcome the note allows for how you triage it. The walkthrough event was a different source and a different time.""",
"""The incident note quotes a second event. Submit the outcome for that line. Do not treat two failures as the same user just because both say logon.""")

add("sec-acl",
"""The practice note describes one packet and one list. Submit the outcome the note allows: does this packet pass. Order and direction are in the note. A packet you allowed in the walkthrough had a different port or a different source.""",
"""The incident note is a second packet against the same kind of list, or a different list. Submit the outcome for that packet. The practice result is not a pattern you can copy.""")

add("sec-phish",
"""The practice note describes one message, one caller, or one object left where people walk. Submit the outcome the note allows. The display name matching a department is not enough when the address or the link host is off. The walkthrough message was a different lure.""",
"""The incident note is a second lure. Submit the outcome for that one. A password request and a parking-lot drive are not the same decision, so do not reuse the practice word without reading.""")

add("sec-mfa",
"""The practice note describes one pair of factors someone wants to count as multi-factor. Submit the outcome the note allows for whether that pair counts. Two things the user knows are not two factors. The walkthrough pair was a different combination.""",
"""The incident note describes a second pair. Submit the outcome for that pair. Passing the practice pair does not make this pair valid.""")

add("sec-cert",
"""The practice note describes a browser warning on one site: name, date, or issuer. Submit the outcome the note allows for what failed. Clicking through because the walkthrough site was fine is how this one goes wrong.""",
"""The incident note is a different warning on a different site. Submit the outcome for that warning. The practice failure mode may not be this one.""")

add("sec-ir",
"""The practice note is a fresh incident, not the order you memorized with blank facts. Submit the outcome the note allows for the first move. Preserving a machine that is still encrypting shares is a different first move from isolating one laptop that has not been clicked.""",
"""The incident note is a second case with a different scope. Submit the outcome for that case. The practice first move was for the other hour.""")

add("sec-risk",
"""The practice note gives a likelihood and an impact for one risk, in the words the note uses. Submit the outcome the note allows. A high impact with a rare likelihood is not the same bucket as a constant low-level leak. The walkthrough risk was a different pair.""",
"""The incident note is a second risk with its own likelihood and impact. Submit the outcome for that pair. Do not copy the practice bucket.""")

add("sec-vuln",
"""The practice note is one finding from a scan: what is exposed, and whether a fix exists. Submit the outcome the note allows. A critical score on a host that is not reachable is a different decision from a medium score on the payroll server. The walkthrough finding was a different host.""",
"""The incident note is a second finding. Submit the outcome for that finding. Severity words in the practice answer do not travel.""")

add("sec-classify",
"""The practice note describes one collection of data and where it sits. Submit the classification outcome the note allows. A spreadsheet of student grades is not the same as a public poster, even if both live on a file share. The walkthrough set was a different collection.""",
"""The incident note describes a second collection. Submit the outcome for that collection. Do not reuse the practice label.""")

add("sec-arch",
"""The practice note describes a recovery site someone wants to buy: how far it is, how fresh the data is, and what it costs to run. Submit the outcome the note allows. A cold site is not a hot site because the brochure used the word redundant. The walkthrough site was a different design.""",
"""The incident note is a second site option. Submit the outcome for that option. Distance and data freshness are in the note.""")

add("sec-vendor",
"""The practice note describes one agreement a vendor offered. Submit the outcome the note allows for whether it covers the duty you care about. A contract that never mentions who reports an incident is not fixed by a logo. The walkthrough agreement was a different clause.""",
"""The incident note is a second agreement, or a second clause. Submit the outcome for that text. The practice clause is not this one.""")

add("sec-zerotrust",
"""The practice note describes one access request under a zero-trust reading: who, what resource, and what is already known. Submit the outcome the note allows. Being on the campus network is not a reason by itself. The walkthrough request was a different resource.""",
"""The incident note is a second request, maybe the same person and a different system. Submit the outcome for that request. Do not grant it because practice granted the other one.""")

add("sec-awareness",
"""The practice note is one message a colleague forwarded. Submit the outcome the note allows. Reporting it is different from replying to the sender, and different from clicking to 'check'. The walkthrough message used a different lure.""",
"""The incident note is a second message, or the same lure sent to a second person. Submit the outcome for this one. The practice report does not cover a new message you have not read.""")

add("sec-iam",
"""The practice note describes one access model someone wants to use for a job: who grants, who reviews, what is grouped. Submit the outcome the note allows. A shared password is not a role. The walkthrough model was a different job.""",
"""The incident note describes a second job and a second model. Submit the outcome for that job. Do not copy the practice model onto a different duty.""")

add("sec-change",
"""The practice note is one change someone wants to make tonight. Submit the outcome the note allows for whether it goes through the window, needs more review, or stops. An emergency that is only urgent in the sender's tone is still a change. The walkthrough change was a different system.""",
"""The incident note is a second change, with its own timing and blast radius. Submit the outcome for that change. The practice decision was about the other window.""")

add("sec-indicators",
"""The practice note lists signals from one hour. Submit the outcome the note allows for which of them is the one you would chase first. A successful login from the user's own desk is not the same signal as a login from a country the user has never used. The walkthrough hour was a different mix.""",
"""The incident note is a later hour, or a different host's signals. Submit the outcome for that list. Do not chase the practice indicator if it is not in this list.""")

add("sec-dlp",
"""The practice note describes data leaving by one path: mail, drive, or a personal device. Submit the outcome the note allows. Blocking a personal photo is a different call from blocking a spreadsheet of account numbers. The walkthrough transfer was a different path.""",
"""The incident note is a second transfer. Submit the outcome for that transfer. Volume and content are in the note, not in the practice answer.""")

add("sec-privacy",
"""The practice note describes one request about personal data: access, correction, or a hold. Submit the outcome the note allows. Handing a full mailbox export to a curious manager is not the same as answering the person the data is about. The walkthrough request was a different ask.""",
"""The incident note is a second request, maybe from a different role. Submit the outcome for that request. The practice duty does not expand to cover it.""")

add("sec-pentest",
"""The practice note is a scope statement for a test someone wants to run. Submit the outcome the note allows. A test that targets systems the statement never names is not in scope because the tester is curious. The walkthrough scope was a different set of hosts.""",
"""The incident note is a second scope, or a request to go past the first one. Submit the outcome for that text. Do not widen the practice scope on your own.""")

add("sec-wireless",
"""The practice note describes one wireless choice: encryption, a guest split, or a shared passphrase. Submit the outcome the note allows. An open guest network that can reach payroll is not fixed by a longer passphrase on a different SSID. The walkthrough network was a different design.""",
"""The incident note is a second wireless decision. Submit the outcome for that decision. The practice SSID is not this one.""")

add("sec-logtriage",
"""The practice note names one question and several logs that might answer it. Submit the outcome the note allows for which log you open. Authentication failures are not in the firewall log just because both are logs. The walkthrough question pointed at a different log.""",
"""The incident note asks a different question. Submit the outcome for that question. The log you chose in practice may be the wrong shelf now.""")

add("scn-dns-evidence",
"""The third-floor caller can open the proxy by address and nothing by name. This Windows PC is only the evidence station. The practice note names the DNS server that should hold the intranet record. Point Ethernet at that server and leave the address on automatic. Do not rebuild the resolver from this keyboard.""",
"""Evidence is filed and this PC is still named like a training image, so the ticket cannot say which desk reported it. The incident note has the computer name. Set it. Leave the DNS server you just chose.""")

add("scn-dns-fix",
"""Names fail on the floor and the client PC is not the broken piece. On dns-01, root's home has a note file whose name starts with note-. It holds a line, a path, and a mode for the repair record. Create that file on the DNS VM. Querying the intranet name again does not write the record.""",
"""The practice record is on dns-01. The incident section of that note names a second file, another line, and a tighter mode, for what ws-22 proved after the zone change. Create it on the DNS VM. Do not point the floor back at the old resolver.""")

add("scn-lan2-fix",
"""LAN 2 has been dark since Friday's change. The written proof for this attempt sits on the primary console, not in another lease renewal. Root's home there has a note whose name starts with note-. It gives a line, a path, and a mode. Create that file on the primary VM. Do not skip the path check just to edit the note.""",
"""The practice proof is on the primary VM. The incident section names a second file and a stricter mode, for the hop that was actually wrong on LAN 2. Create it there. Leave the lease and the practice file in place.""")

add("scn-lan2-verify",
"""The LAN is back and the CFO laptop still holds Friday's resolver. The practice note names the DNS server it should use now. Set that on Ethernet and leave the address on automatic. Rebooting the laptop is not the recovery the meeting needs.""",
"""The laptop can use the noted DNS server. Its computer name is still the image name, so the board packet will not match the asset. The incident note has the name. Set it and leave the DNS server.""")
