"""Shared NETOPS ladder for the identical 'Network operations depth' signpost paragraph (same text, same r0 sha, in
several lessons). Written once here; each lesson file takes a fresh copy via _kit.shared(). Pending SME review."""
from curriculum_v2.ladder.netops._kit import C, lad
from curriculum_v2.ladder.schema import sort

_SRC = ('Course “Network operations depth” paragraph (the original section), re-explained; ISO/IEC 7498-1; RFC 1122; '
        'RFC 826 (ARP); IEEE Std 802.1Q; IEEE Std 802.3 (PoE)')
LAYER, NAME, ARP, MASK, VLAN = ('MC-C-NO1-OSI-LAYER', 'MC-NO1-NAME-FAIL-LOW-LAYER', 'MC-R3-NO1-ARP', 'MC-NO1-MASK-ONLINK',
                                'MC-NO1-ROUTER-REWRITES-IP')

NOD = lad('Network operations depth', 'NO-1.1', _SRC, {
    'r0': C('A user says “the network is down”, but other desks work and her PC has an address from the wrong subnet. Which idea from the paragraph fits first?',
            'A misassigned access VLAN on her port', ['A PoE budget problem on the switch', 'A NAT rule removing a path at the edge'],
            'One desk isolated, with an address from another subnet, is the misassigned access port the paragraph describes. PoE '
            'reboots powered devices, and a NAT change would hit many users.', [VLAN, LAYER]),
    'p': '''<p>This paragraph is a map of the whole course. Each idea is a tool for finding faults.</p>
<ul><li><strong>Layers</strong>: say which layer each test checks.</li>
<li><strong>Subnets</strong>: tell you if a host is local or must go through the router.</li>
<li><strong>ARP</strong> finds a local device. <strong>Routing</strong> finds a remote one.</li>
<li><strong>VLANs</strong>: one wrong port makes one desk look like “the network is down”.</li>
<li><strong>Wi-Fi</strong> adds logins, interference and roaming. <strong>PoE</strong> budgets make phones and APs reboot.</li>
<li><strong>Firewalls and NAT</strong> decide which paths exist.</li></ul>
<p>Always compare: does it work on the local network but not beyond? Is it blocked by a rule, or just unreachable?</p>''',
    'pc': C('Why does subnetting matter during a fault, according to the paragraph?', 'It tells you if a host is local or routed',
            ['It is mostly needed for passing exams', 'It sets the speed of the switch port'],
            'Address and mask decide whether a destination is on-link (ARP, deliver directly) or must go to the gateway. '
            'That changes which tests make sense; it has nothing to do with port speed.', [MASK, LAYER]),
    'a': '''<p>Think of a hospital’s floor plan and its staff badges.</p>
<p>The <strong>layers</strong> are the floors: you say which floor you are checking before you check it. The <strong>subnet</strong>
tells you whether the patient is on your ward (walk over: <strong>ARP</strong>) or in another building (go through reception:
<strong>routing</strong>). A nurse given a badge for the wrong ward (a <strong>misassigned VLAN</strong>) finds every door locked and
says “the hospital is closed”, while everyone else works. Wireless is the hospital radio system: it needs a login and suffers
interference. <strong>PoE</strong> is the power to the bedside monitors: plug in too many and some switch off. <strong>Firewalls and
NAT</strong> are the security desks that decide which corridors are open at all.</p>''',
    'ac': C('In the hospital story, a nurse with a badge for the wrong ward says “the hospital is closed”. What is the network equivalent?',
            'One port in the wrong VLAN', ['A failed core router for the whole site', 'A firewall rule for all users'],
            'Only that one person is locked out while everyone else works, which is the single misassigned access port. A core '
            'router or site-wide rule would affect many people.', [VLAN, LAYER]),
    'v': ['Name the layer of every test you run (e.g. “L3: ping 10.20.40.1”).',
          'Use address and mask to decide: is the target on-link (ARP) or routed (gateway)?',
          'On-link failing: check ARP, the access VLAN and the port.',
          'Routed failing: check the gateway, routes, NAT and firewall rules.',
          'Wireless or powered devices: add authentication, interference, roaming and PoE budget to the list.',
          'Compare on-net and off-net results, and write whether the failure is <strong>policy</strong> (a rule said no) or <strong>reachability</strong> (no path).'],
    'vc': C('Following the steps, a ping to a server on another subnet times out but the firewall log shows the packets denied. Policy or reachability?',
            'Policy: a rule refused it', ['Reachability: there is no path', 'Neither: it is a DNS failure'],
            'A logged deny means the packets arrived and a rule refused them, which is policy. A reachability fault would show no '
            'path at all, and the test used an IP, not a name.', [LAYER, NAME]),
    't': '<p>Sort each symptom by the idea from the paragraph that explains it best.</p>',
    'tc': C('A host reaches a server on its own subnet without the gateway. Which protocol found the server’s MAC address?', 'ARP',
            ['DNS', 'NAT'], 'On-link delivery needs the destination MAC, which ARP finds. DNS turns names into IPs, and NAT rewrites '
            'addresses at the edge.', [ARP, NAME]),
    'w': sort('Which idea explains it?',
              {'VLAN / access port': ['One desk isolated, wrong subnet', 'Green link light, no server reach'],
               'PoE budget': ['Phones reboot when more are added', 'New AP will not power on'],
               'Firewall / NAT': ['Works on-net, blocked off-net after a rule change', 'Inbound hosting fails behind PAT']},
              'Notice that each idea leaves its own fingerprint.'),
})
