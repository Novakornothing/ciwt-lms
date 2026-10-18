"""Chapter checks for Network Operations (pass 8).

Before pass 8 the seeder gave the seven NETOPS chapters three generic 10-item sets in rotation
(chapters 4 and 9 repeated chapter 1, 5 repeated 2, 6 repeated 3) with joke distractors. These
checks follow each chapter's core content (curriculum_v2.netops_core) and objectives. Each item:
stem, four options, key, assessed objective, rationale. Ungraded practice; they feed study tips.
The old seed text is still in app.py seed_database() and in git.
"""


def c(q, options, correct, obj, why):
    assert correct in options and len(options) == 4 and len(set(options)) == 4, q
    return {'q': q, 'options': options, 'correct': correct, 'obj': obj, 'why': why}


NETOPS_CHECKS = {
    1: [
        c('A user can ping 10.1.1.1 but not www.example.com. At which layer does the evidence point first?',
          ['Physical cabling', 'Data link (switching)', 'Name resolution at the application layer', 'Transport (TCP ports)'],
          'Name resolution at the application layer', 'NO-1.1', 'IP reachability works, so layers 1–3 are fine; failing by name points to DNS, an application-layer service.'),
        # spot-check round 2 (Oct 18): "frame" -> "packet"; a router ends each frame and builds a new one. Pending SME review
        c('As a packet crosses routers on its way to the destination, which value stays the same end to end (without NAT)?',
          ['Source MAC address', 'Destination MAC address', 'Destination IP address', 'IP TTL value'],
          'Destination IP address', 'NO-1.1', 'Routers rewrite layer-2 addresses and decrement TTL at every hop; IP addresses are unchanged unless NAT is used.'),
        c('How many usable host addresses does 10.0.0.0/26 provide?', ['64', '62', '30', '126'], '62', 'NO-1.2',
          '/26 leaves 6 host bits: 2^6 = 64 addresses minus network and broadcast = 62.'),
        c('What is the broadcast address of 172.16.5.64/27?', ['172.16.5.95', '172.16.5.127', '172.16.5.63', '172.16.5.96'], '172.16.5.95', 'NO-1.2',
          'A /27 block is 32 addresses: 172.16.5.64–172.16.5.95, so .95 is the broadcast.'),
        c('A host shows fe80::1c2b:3aff:fe4d:1 on its interface. What kind of address is it?',
          ['Global unicast', 'Unique local', 'Link-local', 'Multicast'], 'Link-local', 'NO-1.2',
          'fe80::/10 is link-local; every IPv6 interface has one, and it is never routed.'),
        c('Which service uses TCP 443 by default?', ['SSH', 'HTTPS', 'RDP', 'DNS'], 'HTTPS', 'NO-1.3',
          'HTTPS is TCP 443 (HTTP/3 uses UDP 443). SSH is 22, RDP is 3389, DNS is 53.'),
        c('Why does DNS normally use UDP for queries?', ['Queries are small and a lost one is simply retried', 'UDP encrypts the query', 'TCP cannot carry names', 'UDP guarantees ordered delivery'],
          'Queries are small and a lost one is simply retried', 'NO-1.3', 'One request and one reply fit in single datagrams; the client retries on loss. Large responses and zone transfers use TCP.'),
        c('Which port and transport does SNMP polling use by default?', ['UDP 161', 'TCP 161', 'UDP 514', 'TCP 22'], 'UDP 161', 'NO-1.3',
          'Agents listen on UDP 161; traps go to UDP 162. UDP 514 is syslog.'),
    ],
    2: [
        c('A switch receives a frame for a MAC address not in its table. What does it do?',
          ['Drops the frame', 'Floods it out all ports in that VLAN except the source', 'Sends it to the default gateway', 'Asks the router with ARP'],
          'Floods it out all ports in that VLAN except the source', 'NO-2.1', 'Unknown unicast is flooded within the VLAN; the switch learns the destination when it replies.'),
        c('Users report the whole floor slowed to a halt after someone patched a cable between two wall jacks. Most likely cause?',
          ['A layer-2 loop causing a broadcast storm', 'A duplex mismatch on one port', 'A DHCP scope running out', 'A DNS server failure'],
          'A layer-2 loop causing a broadcast storm', 'NO-2.1', 'Two jacks on the same switch form a loop; without STP edge protection (BPDU Guard) broadcasts multiply.'),
        c('A PC on access port VLAN 20 cannot reach its gateway; other VLAN 20 PCs can. The port shows VLAN 1. What is the fix?',
          ['Assign the port to VLAN 20', 'Enable trunking on the port', 'Change the PC to a static IP', 'Restart the DHCP server'],
          'Assign the port to VLAN 20', 'NO-2.2', 'The port is in the wrong VLAN, so the PC sits in a different broadcast domain from its gateway.'),
        c('Two switches are trunked, but VLAN 30 hosts on each switch cannot reach each other. Other VLANs work. What do you check first?',
          ['Whether VLAN 30 is allowed on the trunk', 'The spanning-tree root bridge', 'The PoE budget on both switches', 'The DNS records for VLAN 30'],
          'Whether VLAN 30 is allowed on the trunk', 'NO-2.2', 'If one VLAN fails across a working trunk, it is usually missing from the allowed list (or not created on one switch).'),
        c('What happens to frames in the native VLAN on an 802.1Q trunk?', ['They are sent untagged', 'They are encrypted', 'They are dropped', 'They get a double tag'],
          'They are sent untagged', 'NO-2.2', 'The native VLAN is the one VLAN carried without a tag; mismatched native VLANs leak traffic between VLANs.'),
        c('What is the maximum channel length for a standard twisted-pair Ethernet run?', ['55 m', '100 m', '185 m', '300 m'], '100 m', 'NO-2.3',
          'TIA/IEEE copper channels are 100 m (90 m permanent link plus patch cords). 10GBASE-T on Cat6 is limited to about 55 m.'),
        c('A run of 400 m between two buildings needs 10 Gb/s. Which medium fits?',
          ['Cat6A copper', 'Multimode or single-mode fibre', 'Cat5e with a repeater', 'Coaxial cable'], 'Multimode or single-mode fibre', 'NO-2.3',
          'Copper Ethernet stops at 100 m; 10GBASE-SR (OM3/OM4 multimode) reaches about 300–400 m and single-mode goes further.'),
        c('Which tool finds which switch port a wall jack is patched to, without a live network?',
          ['Toner and probe', 'Optical power meter', 'Loopback plug', 'Spectrum analyser'], 'Toner and probe', 'NO-2.3',
          'A tone generator on the jack and a probe at the patch panel identify the cable without powering anything.'),
    ],
    3: [
        c('A router has routes to 10.0.0.0/8 and 10.1.0.0/16. Which route does a packet for 10.1.2.3 use?',
          ['10.0.0.0/8', '10.1.0.0/16', 'The default route', 'Both, load-balanced'], '10.1.0.0/16', 'NO-3.1',
          'Routers choose the longest matching prefix; /16 is more specific than /8.'),
        c('A static route and an OSPF route both reach the same prefix with the same mask. Which is installed by default?',
          ['The OSPF route (dynamic wins)', 'The static route (lower AD)', 'Neither — they conflict', 'Whichever was learned first'],
          'The static route (lower AD)', 'NO-3.1', 'For equal prefixes, the source with the lower administrative distance wins; static (1) beats OSPF (110).'),
        c('What does a default route 0.0.0.0/0 match?', ['Only private addresses', 'Any destination with no more specific route', 'Only the local subnet', 'Only multicast'],
          'Any destination with no more specific route', 'NO-3.1', 'A /0 matches everything but is the least specific, so it is used only when nothing else matches.'),
        c('A branch circuit drops every afternoon. What should you collect before calling the provider?',
          ['Timestamps, interface errors and your test results', 'The provider’s list of other customers', 'A screenshot of the speed test site', 'The router’s serial number only'],
          'Timestamps, interface errors and your test results', 'NO-3.2', 'Providers act on evidence: when it happened, what the interface counters showed, and tests that isolate your side.'),
        c('Which option connects two sites securely over the public Internet?',
          ['An IPsec site-to-site VPN', 'A VLAN trunk between sites', 'A DHCP relay', 'An SNMP trap'], 'An IPsec site-to-site VPN', 'NO-3.2',
          'IPsec tunnels encrypt traffic between gateways over an untrusted network. Trunks and relays are LAN features.'),
        c('Which 2.4 GHz channels do not overlap in most regions?', ['1, 6 and 11', '1, 2 and 3', '1, 4, 8 and 11', '3, 8 and 13'],
          '1, 6 and 11', 'NO-3.3', 'In 20 MHz widths, channels 1, 6 and 11 are the non-overlapping set used in North America and most designs.'),
        c('A signal reads −65 dBm with a noise floor of −95 dBm. What is the SNR?', ['30 dB', '−30 dB', '160 dB', '65 dB'], '30 dB', 'NO-3.3',
          'SNR = signal − noise = −65 − (−95) = 30 dB, a good value for data and voice.'),
        c('Which wireless security option suits a staff network where each user signs in with their own account?',
          ['WPA3-Enterprise with 802.1X', 'WPA3-Personal with one passphrase', 'An open SSID with a captive portal', 'WPA2-Personal with MAC filtering'],
          'WPA3-Enterprise with 802.1X', 'NO-3.3', 'Enterprise mode authenticates each user against RADIUS, so access can be revoked per person.'),
    ],
    4: [
        c('In what order do the DHCP DORA messages occur?', ['Discover, Offer, Request, Acknowledge', 'Discover, Request, Offer, Acknowledge', 'Offer, Discover, Acknowledge, Request', 'Request, Offer, Discover, Acknowledge'],
          'Discover, Offer, Request, Acknowledge', 'NO-4.1', 'The client discovers, servers offer, the client requests one offer and that server acknowledges.'),
        c('Clients on a new VLAN get 169.254 addresses. The DHCP server is on another subnet. What is most likely missing?',
          ['A DHCP relay (helper address) on the VLAN gateway', 'A DNS A record for the server', 'A NAT rule for the VLAN', 'A static route on each client'],
          'A DHCP relay (helper address) on the VLAN gateway', 'NO-4.1', 'Discover is a broadcast and does not cross routers; the gateway must relay it to the server.'),
        c('Which DHCP option gives clients their default gateway?', ['Option 3 (router)', 'Option 6 (DNS servers)', 'Option 15 (domain name)', 'Option 51 (lease time)'],
          'Option 3 (router)', 'NO-4.1', 'Option 3 lists routers (default gateway); option 6 lists DNS servers.'),
        c('nslookup returns NXDOMAIN for intranet.example.com. What does that mean?',
          ['The name does not exist in the zone', 'The DNS server is unreachable', 'The record exists but the server timed out', 'The client has no IP address'],
          'The name does not exist in the zone', 'NO-4.2', 'NXDOMAIN is an authoritative “no such name”. A timeout or SERVFAIL would mean a server problem.'),
        c('A web server’s address changed, but some users still reach the old IP. What explains it?',
          ['Cached records that have not reached their TTL', 'A missing MX record', 'An expired DHCP lease', 'A wrong subnet mask on the server'],
          'Cached records that have not reached their TTL', 'NO-4.2', 'Resolvers and clients cache answers for the record’s TTL; lower the TTL before planned changes.'),
        # spot-check round 2 (Oct 18): PTR and SRV records also carry a name in their data, so "points one name to
        # another name" did not single out CNAME; the stem now asks for an alias (RFC 1035 3.3.1, RFC 2782). Pending SME review
        c('Which DNS record type makes one name an alias for another name?', ['CNAME', 'PTR', 'AAAA', 'SRV'], 'CNAME', 'NO-4.2',
          'A CNAME makes a name an alias for another (canonical) name. PTR and SRV records also hold a name, but a PTR maps an address (its reverse-lookup name) to a host name and an SRV gives the host and port for a service; AAAA maps a name to an IPv6 address.'),
        c('Many inside hosts share one public IPv4 address using different source ports. What is this called?',
          ['Port address translation (PAT)', 'Static one-to-one NAT', 'Inbound port forwarding', 'Split-horizon DNS'],
          'Port address translation (PAT)', 'NO-4.3', 'PAT tracks each inside flow by source port so many hosts share one address.'),
        c('A firewall rule list has “deny any any” at line 5 and “permit tcp to web server 443” at line 9. What happens to HTTPS traffic to the web server?',
          ['It is denied, because rules are processed top-down and line 5 matches first', 'It is permitted, because specific rules win', 'It is permitted only for established sessions', 'It is logged but allowed'],
          'It is denied, because rules are processed top-down and line 5 matches first', 'NO-4.3', 'Most firewalls and ACLs stop at the first match; put specific permits above broad denies.'),
    ],
    5: [
        c('Which syslog severity level is more severe: 2 or 5?', ['2 (critical)', '5 (notice)', 'They are equal', 'It depends on the vendor'], '2 (critical)', 'NO-5.1',
          'Syslog severities run 0 (emergency) to 7 (debug); lower numbers are more severe.'),
        c('An interface shows rising CRC errors but low utilisation. What does that suggest?',
          ['A bad cable, connector or optic', 'The link is saturated by traffic', 'A routing loop upstream', 'A DNS failure on the network'],
          'A bad cable, connector or optic', 'NO-5.1', 'CRC errors mean corrupted frames, which point to cabling, connectors, optics or interference, not load.'),
        c('Why record a baseline of normal traffic?', ['So you can tell when current readings are abnormal', 'So the switch runs faster', 'So SNMP does not need a password', 'So logs are deleted sooner'],
          'So you can tell when current readings are abnormal', 'NO-5.1', 'Without a baseline, “high” has no reference; baselines turn readings into evidence.'),
        c('Which SNMP version adds authentication and encryption?', ['SNMPv3', 'SNMPv2c', 'SNMPv1', 'All versions'], 'SNMPv3', 'NO-5.2',
          'SNMPv1 and v2c send community strings in clear text; SNMPv3 adds user authentication and privacy (encryption).'),
        c('Which change best hardens remote management of a switch?',
          ['Allow SSH only from the management subnet, with AAA', 'Enable Telnet with a longer password', 'Allow HTTP management from any network', 'Share one local admin account'],
          'Allow SSH only from the management subnet, with AAA', 'NO-5.2', 'Encrypted access, restricted sources and individual accountable accounts reduce exposure.'),
        c('Why send device logs to a central server with synchronised time (NTP)?',
          ['Events from many devices can be correlated in order', 'It makes the devices boot faster', 'It removes the need for SNMP', 'It encrypts the routing table'],
          'Events from many devices can be correlated in order', 'NO-5.2', 'Accurate timestamps let you line up events across devices during an incident.'),
        c('Guest Wi-Fi users should reach the Internet but nothing internal. Which design does that?',
          ['A separate guest VLAN/zone with a policy allowing only Internet', 'Putting guests on the staff VLAN with a different SSID name', 'Giving guests static IPs', 'Hiding the guest SSID'],
          'A separate guest VLAN/zone with a policy allowing only Internet', 'NO-5.3', 'Segmentation plus a deny-internal policy enforces least privilege; SSID names and hiding do not.'),
        c('Which principle grants each user or system only the access needed for its job?', ['Least privilege', 'Defence in depth', 'Separation of duties', 'Implicit trust'], 'Least privilege', 'NO-5.3',
          'Least privilege limits access to what is required; zero-trust designs apply it to every request.'),
    ],
    6: [
        c('Only users in one building cannot reach any server; other buildings are fine. Where do you look first?',
          ['The building’s shared uplink and gateway', 'The application servers themselves', 'Each affected user’s PC in turn', 'The Internet provider’s circuit'],
          'The building’s shared uplink and gateway', 'NO-6.1', 'Scope narrows the fault: what those users share and others do not is the likeliest place.'),
        c('One user cannot reach a single website; everyone else can. Most likely scope?', ['The user’s device or account', 'The core switch', 'The ISP circuit', 'The data-centre firewall'],
          'The user’s device or account', 'NO-6.1', 'A single user and single destination failing while others succeed points to the client (proxy, DNS cache, hosts file, browser).'),
        c('During an outage you have two theories. What is the disciplined next step?',
          ['Test the most likely, least disruptive theory first and record the result', 'Apply both fixes at once to save time', 'Wait for the problem to clear by itself', 'Reboot the core to rule everything out'],
          'Test the most likely, least disruptive theory first and record the result', 'NO-6.2', 'One change at a time keeps cause and effect clear; order tests by likelihood and risk.'),
        c('Why time-box each troubleshooting step during a major incident?',
          ['To decide when to escalate or roll back instead of drifting', 'To make the ticket shorter', 'To avoid writing status updates', 'To give users fewer updates'],
          'To decide when to escalate or roll back instead of drifting', 'NO-6.2', 'Time boxes force a decision point: escalate, roll back or try the next theory.'),
        c('A change caused an outage and the fix is unclear. What does a good change plan already contain?',
          ['A tested rollback procedure', 'A list of users to blame', 'Only the new configuration', 'The vendor’s support phone number only'],
          'A tested rollback procedure', 'NO-6.2', 'Rollback is planned before the change so service can be restored quickly.'),
        c('Which status update is most useful to stakeholders?',
          ['Impact, current action, next update time', 'Technical details of every command run', '“Working on it” every few minutes', 'A promise of when it will be fixed'],
          'Impact, current action, next update time', 'NO-6.2', 'Stakeholders need impact, what is being done and when they will hear next; avoid promises you cannot keep.'),
        c('A fix appears to work. How do you verify it?',
          ['Re-run the original failing test and confirm with affected users', 'Close the ticket when the alert clears', 'Ask one technician if it looks fine', 'Wait a week and see if anyone complains'],
          'Re-run the original failing test and confirm with affected users', 'NO-6.3', 'Verification repeats the test that failed and confirms the user outcome; an alert clearing is not proof.'),
        c('After the incident, what should be updated?',
          ['Diagrams, configs and the runbook to match the change', 'Only the ticket status', 'Nothing, if service is restored', 'The user’s password'],
          'Diagrams, configs and the runbook to match the change', 'NO-6.3', 'Documentation that matches reality is what makes the next incident faster.'),
    ],
    9: [
        c('Which command shows which VLAN each switch access port belongs to on Cisco IOS-style switches?',
          ['show vlan brief', 'show ip route', 'show running-config | include hostname', 'show clock'], 'show vlan brief', 'NO-9.1',
          'show vlan brief lists VLANs with their member access ports. Trunks appear in show interfaces trunk.'),
        c('Which interface commands make a port an access port in VLAN 20?',
          ['switchport mode access, then switchport access vlan 20', 'switchport mode trunk, then switchport trunk native vlan 20', 'ip address 20.0.0.1 255.0.0.0', 'vlan 20, then name ACCESS'],
          'switchport mode access, then switchport access vlan 20', 'NO-9.1', 'Access mode plus the access VLAN assigns the port; the vlan command alone only creates the VLAN.'),
        c('Which command verifies which VLANs are allowed and active on a trunk?', ['show interfaces trunk', 'show vlan brief', 'show arp', 'show version'], 'show interfaces trunk', 'NO-9.1',
          'show interfaces trunk lists trunk ports, native VLAN, and allowed/active VLANs.'),
        c('Hosts in VLAN 10 and VLAN 20 must talk through one router interface. What is that design called?',
          ['Router-on-a-stick with 802.1Q subinterfaces', 'A routed access port per VLAN', 'A VLAN-free flat network', 'Static NAT between VLANs'],
          'Router-on-a-stick with 802.1Q subinterfaces', 'NO-9.2', 'One trunk to the router with a tagged subinterface per VLAN, each with the VLAN’s gateway address.'),
        c('Which command adds a default route to next hop 203.0.113.1?', ['ip route 0.0.0.0 0.0.0.0 203.0.113.1', 'ip default-network 203.0.113.0', 'route add default 203.0.113.1', 'ip route 203.0.113.1 0.0.0.0'],
          'ip route 0.0.0.0 0.0.0.0 203.0.113.1', 'NO-9.2', 'A static route to 0.0.0.0/0 via the next hop is the IOS default route. route add is a host OS command.'),
        c('An interface shows “administratively down”. What fixes it?', ['no shutdown on the interface', 'Replacing the cable', 'Changing the VLAN', 'Reloading the router'],
          'no shutdown on the interface', 'NO-9.2', '“Administratively down” means it was shut in the configuration; no shutdown enables it.'),
        c('Which command saves the running configuration so it survives a reload?', ['copy running-config startup-config', 'show running-config', 'erase startup-config', 'reload'],
          'copy running-config startup-config', 'NO-9.2', 'Changes live in running-config until copied to startup-config (write memory does the same).'),
        c('Which output confirms the router has a connected route for its VLAN 10 subinterface?',
          ['A “C” entry for the VLAN 10 subnet in show ip route', 'The VLAN listed in show vlan brief', 'An ARP entry for the router itself', 'The hostname in the prompt'],
          'A “C” entry for the VLAN 10 subnet in show ip route', 'NO-9.2', 'Connected routes (code C) appear once the subinterface has an address and is up.'),
    ],
}


def netops_quiz_payload(order):
    """Quiz JSON for a NETOPS chapter (same shape as pilot_slice.quiz_payload)."""
    from curriculum_v2.objectives import OBJECTIVES
    from curriculum_v2 import parity_pass15
    out = []
    for i, it in enumerate(NETOPS_CHECKS.get(order) or []):
        wrong = [o for o in it['options'] if o != it['correct']]
        opts = wrong + [it['correct']]
        s = (i + order) % 4
        opts = opts[s:] + opts[:s]
        o = OBJECTIVES.get(it['obj']) or {}
        opts, key = parity_pass15.apply(f'NQ{order}.{i}', opts, it['correct'])  # pass 15: option-length parity
        out.append({
            'text': it['q'], 'options': opts, 'correct': key,
            'lo': f'LO-NET-{order}', 'lo_text': o.get('text', f'Network chapter {order}'),
            'focus': o.get('text', f'Network chapter {order}'), 'keywords': [],
            'study_tip': it['why'], 'explanation': it['why'],
            'obj': it['obj'], 'obj_text': o.get('text', ''), 'bank_id': f'NQ{order}.{i}',
        })
    return out
