"""Explanation ladder — NETOPS chapter 8 (Cloud, SD-WAN, Zero-Trust & Network Automation / N10-009 Domain 1.3, 1.8 & 4.1). Pending SME review.

Author: content branch (pass 19). R1 plain, R2 analogy, R3 visual/trace, R4 try-it per concept section, each with a
check that asks the idea in a new form. Facts follow NIST SP 800-207, MEF 70 SD-WAN, OpenFlow/SDN, and CompTIA N10-009.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, section, sort, tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 8

L = 'Course lesson {} (Cloud, SD-WAN, Zero-Trust & Network Automation), re-explained'
CLD = 'NIST SP 800-145 (Cloud Computing Definition); AWS / Azure VPC Networking Guides (IGW, NAT Gateway, Security Groups vs NACLs, Transit Gateway); CompTIA N10-009 objective 1.3'
SDN = 'ONF SDN Architecture (Control, Data, and Management Planes); MEF 70 (SD-WAN Service Attributes); CompTIA N10-009 objective 1.8'
ZTA = 'NIST SP 800-207 (Zero Trust Architecture — Policy Engine, Policy Administrator, Policy Enforcement Point); Gartner SASE Framework; CompTIA N10-009 objective 4.1'
AUT = 'RFC 6241 (NETCONF); RFC 8040 (RESTCONF); RFC 7950 (YANG 1.1); Ansible & Terraform Infrastructure-as-Code Guides; CompTIA N10-009 objective 3.1'
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO8-SG-VS-NACL': {
        'obj': 'NO-3.2',
        'label': 'Confusing stateful cloud Security Groups (vNIC level, implicit allow return) with stateless subnet NACLs',
        'fix': 'Cloud Security Groups are stateful at the instance vNIC (return traffic is allowed automatically); Network ACLs (NACLs) are stateless at the subnet boundary and evaluate explicit allow/deny rules in both directions.',
        'terms': ['security group', 'nacl', 'stateful', 'stateless', 'vpc', 'nat gateway'],
        'source': L.format('8.1') + '; ' + CLD,
        'review': R,
    },
    'MC-L-NO8-SDN-PLANES': {
        'obj': 'NO-3.2',
        'label': 'Mixing up the SDN control plane (routing/policy brain, southbound API) with the data/forwarding plane',
        'fix': 'The data plane forwards packets at line rate in hardware/vSwitches; the control plane computes topology and pushes forwarding rules down via southbound APIs (OpenFlow, NETCONF), while applications talk to the controller via northbound REST APIs.',
        'terms': ['control plane', 'data plane', 'northbound', 'southbound', 'sd-wan'],
        'source': L.format('8.2') + '; ' + SDN,
        'review': R,
    },
    'MC-L-NO8-ZTNA-IMPLICIT': {
        'obj': 'NO-5.3',
        'label': 'Assuming a user on the corporate LAN or VPN gets broad implicit trust under Zero Trust (NIST SP 800-207)',
        'fix': 'Zero Trust eliminates implicit trust based on network location (LAN or VPN); every request is authenticated, device-posture checked, and granted least-privilege per-session access through a Policy Enforcement Point (PEP).',
        'terms': ['zero trust', 'ztna', 'nist 800-207', 'pep', 'pdp', 'microsegmentation'],
        'source': L.format('8.3') + '; ' + ZTA,
        'review': R,
    },
    'MC-L-NO8-DRIFT-IDEMPOTENCY': {
        'obj': 'NO-5.2',
        'label': 'Treating ad-hoc manual CLI edits as equivalent to idempotent Infrastructure-as-Code (Ansible / Terraform / YANG)',
        'fix': 'Idempotent automation guarantees that applying a playbook or declarative template N times produces the exact same target state without duplicate rules, whereas manual CLI edits cause configuration drift.',
        'terms': ['idempotent', 'configuration drift', 'netconf', 'restconf', 'yang', 'ansible'],
        'source': L.format('8.4') + '; ' + AUT,
        'review': R,
    },
}

SG_M, SDN_M, ZT_M, AUT_M = (
    'MC-L-NO8-SG-VS-NACL',
    'MC-L-NO8-SDN-PLANES',
    'MC-L-NO8-ZTNA-IMPLICIT',
    'MC-L-NO8-DRIFT-IDEMPOTENCY',
)

LESSONS = {
    '8.1': {
        'cloud-vpc-architecture-gateways-and-hybrid-connectivity': section(
            'Cloud VPC architecture, gateways, and hybrid connectivity', 'NO-3.2',
            [check('An application server in a private cloud subnet needs to download OS patches from the internet without allowing any inbound connections from the internet. Which VPC component provides this?',
                   'A NAT Gateway in a public subnet',
                   ['An Internet Gateway (IGW) attached directly to the private server without NAT',
                    'A stateless NACL with an inbound permit any rule'],
                   'A NAT Gateway translates private RFC 1918 source addresses for outbound internet requests and drops unsolicited inbound connections from the internet.',
                   mc=[SG_M, SG_M])],
            plain('''<p>A <strong>Virtual Private Cloud (VPC)</strong> is your isolated virtual network inside a cloud provider.</p>
<ul><li><strong>Public subnets</strong> have a route to an <strong>Internet Gateway (IGW)</strong> so load balancers or bastions can reach the internet directly.</li>
<li><strong>Private subnets</strong> hold databases and app servers with no public IP; they reach the internet outbound-only through a <strong>NAT Gateway</strong>.</li>
<li><strong>Security Groups</strong> guard each VM’s virtual NIC and are <strong>stateful</strong> (if you allow TCP 443 in, the reply goes out automatically).</li>
<li><strong>Network ACLs (NACLs)</strong> guard the whole subnet boundary and are <strong>stateless</strong> (you must allow both inbound and outbound ephemeral return ports).</li></ul>
<p>Takeaway: use stateful Security Groups per tier, stateless NACLs for coarse subnet blocks, and Direct Connect / ExpressRoute with IPsec backup for hybrid WANs.</p>''',
                  L.format('8.1') + '; ' + CLD,
                  [check('You allow inbound TCP 443 on a cloud VM’s Security Group, but responses never reach the client after a colleague edits the subnet NACL. Why?',
                         'Stateless NACLs need an outbound ephemeral rule',
                         ['Security Groups are stateless and block outbound TCP ACK packets by default',
                          'VPC routers strip TCP port numbers unless BGP is enabled on the vNIC'],
                         'Security Groups are stateful (return traffic is automatic), but subnet NACLs are stateless—if the NACL lacks an outbound allow rule for ephemeral ports, replies are dropped at the subnet edge.',
                         mc=[SG_M, SG_M])]),
            analogy('''<p>Think of a gated apartment complex.</p>
<p>The outer perimeter gatehouse for the entire block is the <strong>subnet NACL</strong>: the guard there has no memory (<strong>stateless</strong>), so he checks a printed rule sheet both when a visitor walks in and when they walk back out. Each apartment’s smart door lock is a <strong>Security Group</strong> at the vNIC: once you let a guest in (<strong>stateful</strong>), the door remembers them and lets them step back out without a second check.</p>
<p>A <strong>NAT Gateway</strong> is the concierge desk that places outside deliveries for private-floor residents without ever giving couriers the residents’ room numbers.</p>
<p><strong>Analogy map:</strong> Apartment complex = VPC; Outer block gatehouse (no memory) = Stateless NACL; Apartment door lock (remembers guests) = Stateful Security Group; Concierge outbound proxy = NAT Gateway.</p>
<p><strong>Where the analogy breaks:</strong> A human guard takes seconds per visitor; cloud SDN hypervisors evaluate Security Group flow tables in microseconds at line rate.</p>''',
                    L.format('8.1') + ' (gated apartment complex analogy); ' + CLD,
                    [check('When connecting 15 VPCs to an on-premises data center, which architecture avoids a complex full mesh of 105 separate VPC peering links?',
                           'A hub-and-spoke Transit Gateway',
                           ['Putting all 15 VPCs on the same overlapping 192.168.1.0/24 subnet',
                            'Replacing every VPC router with a Layer-1 Ethernet hub'],
                           'A Transit Gateway acts as a central cloud routing hub so each VPC and on-prem link connects once to the hub instead of needing N*(N-1)/2 full-mesh peering links.',
                           mc=[SG_M, SG_M])]),
            visual(svg(620, 130, 'Cloud VPC Public Subnet IGW vs Private Subnet NAT Gateway and Hybrid Direct Connect',
                       box(10, 25, 175, 75, 'Internet & On-Prem', 'IGW + Direct Connect')
                       + arrow(185, 62, 225, 62, 'NACL (Stateless)')
                       + box(225, 25, 175, 75, 'Public Subnet', 'ALB · NAT Gateway')
                       + arrow(400, 62, 440, 62, 'SG (Stateful)')
                       + box(440, 25, 170, 75, 'Private Subnet', 'App & DB (RFC 1918)'))
                   + '''<ol class="ladder-trace"><li>External HTTPS request arrives at the Internet Gateway (IGW) and enters the Public Subnet Load Balancer.</li>
<li>Subnet NACL checks stateless inbound/outbound rules; Load Balancer forwards to App VM in the Private Subnet.</li>
<li>App VM’s stateful Security Group permits TCP 8443 from the Load Balancer SG and automatically permits the return flow.</li></ol>''',
                   L.format('8.1') + '; ' + CLD,
                   [check('What is the primary advantage of a dedicated cloud interconnect (AWS Direct Connect / Azure ExpressRoute) over an internet-based IPsec VPN?',
                          'Predictable private bandwidth and lower jitter',
                          ['It automatically encrypts all payload data with WPA3-SAE',
                           'It eliminates the need for IP routing tables inside the VPC'],
                          'Dedicated fiber interconnects bypass public internet congestion to deliver deterministic bandwidth and latency, though many teams still run IPsec or MACsec over them for encryption.',
                          mc=[SG_M, SG_M])]),
            tryit('<p>Sort each cloud networking feature into Stateful Security Group vs Stateless NACL, then practice VM network provisioning.</p>',
                  L.format('8.1') + '; ' + CLD,
                  [check('Can a standard AWS/Azure Security Group contain an explicit DENY rule?',
                         'No, Security Groups allow rules only; NACLs support DENY',
                         ['Yes, Security Groups only contain deny rules and never allow rules',
                          'Yes, but only for IPv6 multicast frames'],
                         'Cloud Security Groups are allow-only whitelists (everything not explicitly allowed is implicitly denied). To block a specific hostile IP across a subnet, use a NACL or WAF.',
                         mc=[SG_M, SG_M])],
                  widget=sort('Stateful Security Group or Stateless NACL?',
                              {'Security Group (vNIC level)': ['Stateful: return traffic is allowed automatically', 'Allow rules only; references other SG IDs'],
                               'Network ACL (Subnet boundary)': ['Stateless: requires explicit inbound and outbound ephemeral rules', 'Ordered numbered rules supporting both ALLOW and DENY']},
                              'Remember: Security Group = Stateful vNIC allow-list; NACL = Stateless subnet allow/deny list.'),
                  lab={'id': 'virt-vm', 'note': 'Provision the virtual machine network interface and verify virtual switch isolation.'})),
    },
    '8.2': {
        'software-defined-networking-sdn-and-sd-wan-planes': section(
            'Software-defined networking (SDN) and SD-WAN planes', 'NO-3.2',
            [check('In Software-Defined Networking (SDN), which interface carries forwarding rules and flow tables from the central SDN Controller down to the switches?',
                   'The Southbound API (OpenFlow / NETCONF)',
                   ['The Northbound API toward business orchestration apps',
                    'The physical RS-232 serial console cable'],
                   'On an architecture diagram with applications at the top, controller in the middle, and switches at the bottom, the controller talks down to switches via the Southbound API and up to apps via the Northbound API.',
                   mc=[SDN_M, SDN_M])],
            plain('''<p>Traditional routers bundle three jobs inside one box. <strong>SDN</strong> and <strong>SD-WAN</strong> separate them cleanly:</p>
<ul><li><strong>Data (Forwarding) Plane</strong>: the muscle at the bottom that forwards frames and packets at line speed using hardware tables (TCAM/ASICs).</li>
<li><strong>Control Plane</strong>: the brain in the middle that learns topology and computes best paths.</li>
<li><strong>Management / Application Plane</strong>: the dashboard and orchestration tools at the top where engineers set business policy.</li></ul>
<p>In <strong>SD-WAN</strong>, edge routers measure live <strong>latency, jitter, and packet loss</strong> across MPLS, fiber, and 5G/LTE links, steering voice/video onto the healthiest path automatically.</p>
<p>Takeaway: Southbound API = Controller → Switches; Northbound API = Apps → Controller.</p>''',
                  L.format('8.2') + '; ' + SDN,
                  [check('Why can an SD-WAN edge appliance steer real-time Zoom/VoIP traffic away from a degraded fiber link faster than traditional BGP?',
                         'It probes live latency, jitter, and loss continuously',
                         ['SD-WAN disables UDP checksums on all voice packets',
                          'SD-WAN replaces IP addresses with Layer-2 spanning-tree BPDUs'],
                         'Traditional routing often sees a link as “up” even when packet loss is 8% and jitter is 90 ms. SD-WAN BFD/SLA probes measure path quality continuously and shift application flows mid-session.',
                         mc=[SDN_M, SDN_M])]),
            analogy('''<p>Think of city air-traffic control versus every pilot flying by sight.</p>
<p>In a legacy network, every router runs its own control plane—like pilots negotiating directly over radio at every intersection. In <strong>SDN</strong>, a central air-traffic control tower (<strong>SDN Controller / Control Plane</strong>) sees the entire sky at once. Weather and airline scheduling systems feed requests into the tower from above (<strong>Northbound API</strong>), and the tower sends exact runway and altitude instructions down to each aircraft (<strong>Southbound API</strong> to the <strong>Data Plane</strong>).</p>
<p><strong>Analogy map:</strong> Airline scheduling software = Management/App plane (Northbound); Control tower brain = SDN Controller (Control plane); Radio instructions down to planes = Southbound API; Aircraft engines flying the route = Data plane switches.</p>
<p><strong>Where the analogy breaks:</strong> If an air-traffic tower goes dark, pilots still see out the cockpit window; if an SDN switch loses both its controller and its cached flow table without a fail-secure/standalone fallback, new flows halt.</p>''',
                    L.format('8.2') + ' (air-traffic control tower analogy); ' + SDN,
                    [check('What is the role of the Northbound API in an SDN controller architecture?',
                           'Orchestration apps request network policy via REST/JSON',
                           ['It crimps RJ-45 T568B connectors onto Category 6A patch cables',
                            'It forwards raw Ethernet frames between two access switches at Layer 1'],
                           'Northbound APIs (typically RESTful HTTPS/JSON) expose the controller to applications, cloud orchestrators, and security automation above it.',
                           mc=[SDN_M, SDN_M])]),
            visual(svg(620, 130, 'SDN 3-Plane Architecture with Northbound REST API and Southbound OpenFlow/NETCONF API',
                       box(15, 25, 165, 75, 'App / Mgmt Plane', 'Orchestration · Intent')
                       + arrow(180, 62, 230, 62, 'Northbound')
                       + box(230, 25, 165, 75, 'Control Plane', 'SDN / SD-WAN Controller')
                       + arrow(395, 62, 445, 62, 'Southbound')
                       + box(445, 25, 160, 75, 'Data Plane', 'Switches · vEdge ASICs'))
                   + '''<ol class="ladder-trace"><li>Engineer defines an application SLA policy (“Voice requires jitter &lt; 20 ms, loss &lt; 1%”) in the Management Orchestrator.</li>
<li>Orchestrator pushes the policy to the SD-WAN Controller over the <strong>Northbound REST API</strong>.</li>
<li>Controller compiles forwarding rules and pushes them down to branch SD-WAN edges via the <strong>Southbound API</strong>.</li>
<li>Branch Data Plane measures BFD probes on MPLS vs Broadband and steers voice over the link meeting the SLA.</li></ol>''',
                   L.format('8.2') + '; ' + SDN,
                   [check('What is Zero-Touch Provisioning (ZTP) in an SD-WAN deployment?',
                          'New branch appliances auto-fetch config from the controller',
                          ['Manually configuring every branch router over a 9600-baud serial cable without touching the keyboard',
                           'Disabling all firewall rules so branch users can configure their own BGP ASN'],
                          'ZTP allows a factory-default branch appliance to phone home to the SD-WAN controller over any internet link, verify its hardware identity, and pull its templates without an on-site engineer.',
                          mc=[SDN_M, SDN_M])]),
            tryit('<p>Sort each protocol or action into the Data Plane, Control Plane, or Management Plane.</p>',
                  L.format('8.2') + '; ' + SDN,
                  [check('Which encapsulate-on-UDP overlay protocol (UDP port 4789) is widely used in data-center SDN fabrics to stretch Layer-2 segments across a Layer-3 spine-leaf underlay?',
                         'VXLAN (UDP 4789)',
                         ['Telnet (TCP port 23)', 'TFTP (UDP port 69)'],
                         'VXLAN encapsulates Layer-2 Ethernet frames inside UDP packets with a 24-bit VNI (up to 16 million segments), overcoming the 4,094 VLAN limit across Layer-3 Clos fabrics.',
                         mc=[SDN_M, SDN_M])],
                  widget=sort('Classify each item by network plane',
                              {'Data (Forwarding) Plane': ['ASIC / TCAM line-rate packet forwarding', ' decrementing IPv4 TTL and rewriting L2 MAC headers'],
                               'Control & Management Planes': ['OSPF / BGP route calculation & SDN Controller', 'Northbound REST API & SSH/NETCONF policy templates']},
                              'Keeping the data plane in hardware ASICs and centralizing policy in the control/management planes lets SDN scale cleanly.'))),
    },
    '8.3': {
        'zero-trust-architecture-ztna-sase-and-microsegmentation': section(
            'Zero-trust architecture (ZTNA), SASE, and microsegmentation', 'NO-5.3',
            [check('Under NIST SP 800-207 Zero Trust Architecture, why is a laptop plugged into a headquarters conference-room Ethernet jack treated with the same verification rigor as a laptop at an airport?',
                   'Network location never grants implicit trust',
                   ['Headquarters Ethernet switches cannot support IEEE 802.1Q VLAN tags',
                    'Zero Trust bans all wired Ethernet connections in favor of 2.4 GHz Wi-Fi'],
                   'Core Zero Trust tenet #2 (NIST SP 800-207) states that network location (inside the perimeter vs remote) never implies trust; every access request is verified per session.',
                   mc=[ZT_M, ZT_M])],
            plain('''<p>Traditional “castle-and-moat” networks trusted anyone inside the firewall or connected to a full-tunnel VPN. If one laptop caught ransomware, it could scan the whole internal subnet laterally (<strong>east-west traffic</strong>).</p>
<ul><li><strong>Zero Trust (NIST SP 800-207)</strong> follows <em>“never trust, always verify”</em>: every request checks <strong>user identity (MFA/SSO)</strong>, <strong>device health/posture (EDR, OS patch level, disk encryption)</strong>, and <strong>context</strong> before granting access to one specific application—never the whole LAN.</li>
<li>The <strong>Policy Decision Point (PDP)</strong> (Policy Engine + Policy Administrator) evaluates trust and instructs the <strong>Policy Enforcement Point (PEP)</strong> gate to open or close.</li>
<li><strong>Microsegmentation</strong> places software-defined firewall rules around individual workloads so an attacker on one web server cannot reach neighboring servers.</li></ul>
<p>Takeaway: ZTNA brokers access to a single app via a PEP after PDP verification, stopping lateral movement.</p>''',
                  L.format('8.3') + '; ' + ZTA,
                  [check('In NIST SP 800-207 Zero Trust Architecture, which component sits in the traffic path to actually allow, block, or terminate the client’s connection to a resource?',
                         'Policy Enforcement Point (PEP)',
                         ['Public DNS Root Hints Server', 'Simple Network Management Protocol (SNMPv1) Trap Receiver'],
                         'The Policy Engine (PE) and Policy Administrator (PA) form the Policy Decision Point (PDP) that makes the decision, while the Policy Enforcement Point (PEP) enforces that decision on the data path.',
                         mc=[ZT_M, ZT_M])]),
            analogy('''<p>Think of a medieval castle moat versus an airport with secure boarding gates.</p>
<p>A traditional VPN is a drawbridge over a moat: once you cross the bridge into the courtyard, you can wander into every kitchen, vault, and tower (<strong>lateral movement</strong>). <strong>Zero Trust (ZTNA)</strong> is a modern secure facility where every single room has its own electronic lock (<strong>Policy Enforcement Point / PEP</strong>) wired to a central security computer (<strong>Policy Decision Point / PDP</strong>).</p>
<p>Even if you are already inside the building, opening Lab 4 requires your badge, your biometric scan, a healthy safety suit check (<strong>device posture</strong>), and a current work order for Lab 4—and that clearance still will not open Lab 5 next door (<strong>microsegmentation</strong>).</p>
<p><strong>Analogy map:</strong> Drawbridge into open courtyard = Legacy broad-network VPN; Central security brain = PDP (Policy Engine + Administrator); Electronic door lock on Lab 4 = PEP; Wall between Lab 4 and Lab 5 = Microsegmentation.</p>
<p><strong>Where the analogy breaks:</strong> A physical door stays unlocked while you stand in the doorway; a Zero Trust PDP continuously re-evaluates telemetry and revokes the PEP session mid-stream if your endpoint EDR stops reporting.</p>''',
                    L.format('8.3') + ' (castle drawbridge vs per-room electronic gate analogy); ' + ZTA,
                    [check('A remote contractor’s laptop passes MFA, but its endpoint protection agent is disabled and disk encryption is turned off. What does a ZTNA Policy Decision Point do?',
                           'Denies access because device posture failed',
                           ['Grants full domain-admin access because MFA succeeded',
                            'Disables TLS encryption so the contractor can connect faster'],
                           'ZTNA evaluates both user identity (MFA) and device health/posture (EDR running, OS patched, disk encrypted) before instructing the PEP to open a session.',
                           mc=[ZT_M, ZT_M])]),
            visual(svg(620, 130, 'NIST SP 800-207 Zero Trust Control Plane PDP (PE + PA) and Data Plane PEP Flow',
                       box(10, 25, 165, 75, 'Untrusted Subject', 'User MFA + Device Posture')
                       + arrow(175, 62, 225, 62, 'Request')
                       + box(225, 25, 175, 75, 'PEP Gate (Data)', 'Enforces Per-App Tunnel')
                       + arrow(400, 62, 445, 62, 'PDP Decision')
                       + box(445, 25, 165, 75, 'Protected App', 'Microsegmented Resource'))
                   + '''<ol class="ladder-trace"><li>Subject requests access to the Finance App; all resources are hidden behind the <strong>Policy Enforcement Point (PEP)</strong>.</li>
<li><strong>Policy Engine (PE)</strong> evaluates IdP/MFA identity, MDM/EDR device posture, threat intelligence, and time/location policy.</li>
<li><strong>Policy Administrator (PA)</strong> issues a short-lived session token and instructs the PEP to stitch a 1-to-1 micro-tunnel to the Finance App only.</li>
<li>East-west lateral scans to neighboring servers are dropped by host/hypervisor microsegmentation rules.</li></ol>''',
                   L.format('8.3') + '; ' + ZTA,
                   [check('What does SASE (Secure Access Service Edge) combine into a unified cloud-delivered service?',
                          'SD-WAN with ZTNA, SWG, CASB, and FWaaS',
                          ['Legacy coaxial Token Ring hubs with analog PSTN modems',
                           'Local printer spoolers with unmanaged L2 desktop switches'],
                          'SASE converges wide-area networking (SD-WAN) with security service edge functions (Zero Trust Network Access, Secure Web Gateway, CASB, and Firewall-as-a-Service) at cloud Points of Presence.',
                          mc=[ZT_M, ZT_M])]),
            tryit('<p>Order the Zero Trust verification and enforcement sequence when a user requests an internal application.</p>',
                  L.format('8.3') + '; ' + ZTA,
                  [check('Why does microsegmentation stop ransomware from spreading across a virtualized data center?',
                         'It filters east-west traffic between workloads',
                         ['It merges all servers into a single flat /8 broadcast domain',
                          'It turns off TCP port 443 on the public internet gateway only'],
                         'Traditional perimeter firewalls only inspect north-south traffic entering or leaving the data center; microsegmentation inspects and restricts east-west traffic between individual VMs/containers.',
                         mc=[ZT_M, ZT_M])],
                  widget=order('Order the NIST SP 800-207 Zero Trust access flow',
                               ['User and endpoint send access request to the Policy Enforcement Point (PEP)',
                                'Policy Engine (PE) verifies MFA identity, device posture, and least-privilege policy',
                                'Policy Administrator (PA) mints session credentials and signals the PEP to allow',
                                'PEP opens a scoped per-application tunnel while blocking lateral subnet scanning'],
                               'Notice that the client never touches the target application until the PDP (PE + PA) explicitly authorizes the PEP.'))),
    },
    '8.4': {
        'network-automation-netconf-restconf-yang-and-gitops': section(
            'Network automation: NETCONF, RESTCONF, YANG, and GitOps', 'NO-5.2',
            [check('An engineer runs an Ansible playbook three times in a row to ensure VLAN 40 and NTP server 10.0.0.123 exist on 50 switches. The first run makes 50 changes; the second and third runs make 0 changes and create no duplicate lines. What property is this?',
                   'Idempotency',
                   ['Spanning-tree port flapping', 'Asymmetric BGP route leaking'],
                   'Idempotency means applying an operation once or many times produces the exact same desired system state without unintended side effects or duplicate configuration entries.',
                   mc=[AUT_M, AUT_M])],
            plain('''<p>Pasting CLI commands by hand into 80 switches leads to typos and <strong>configuration drift</strong> (where live switches slowly diverge from the approved standard).</p>
<ul><li><strong>YANG</strong> is the data modeling language that defines the structure and types of network configuration and state data.</li>
<li><strong>NETCONF</strong> runs over <strong>SSH (TCP port 830)</strong> using XML encoding and supports transactional candidate datastores (validate and commit across devices, or roll back cleanly).</li>
<li><strong>RESTCONF</strong> maps YANG models over <strong>HTTPS</strong> using standard HTTP verbs (<code>GET</code>, <code>POST</code>, <code>PUT</code>, <code>PATCH</code>, <code>DELETE</code>) with <strong>JSON</strong> or XML payloads.</li>
<li><strong>GitOps / Infrastructure-as-Code (IaC)</strong> stores configurations in Git as the single source of truth, using <strong>idempotent</strong> tools like Ansible or Terraform.</li></ul>
<p>Takeaway: YANG is the data model; NETCONF (SSH/830/XML) and RESTCONF (HTTPS/JSON) are the protocols that carry it.</p>''',
                  L.format('8.4') + '; ' + AUT,
                  [check('How do YANG, NETCONF, and RESTCONF relate to each other?',
                         'YANG models data; NETCONF and RESTCONF transport it',
                         ['YANG is a fiber-optic connector, while NETCONF is a 2.4 GHz wireless channel',
                          'RESTCONF is a Layer-1 cable tester, while YANG is a DHCP scope option'],
                         'YANG defines the tree structure of configuration and operational state; NETCONF and RESTCONF transport those YANG models using XML or JSON.',
                         mc=[AUT_M, AUT_M])]),
            analogy('''<p>Think of building houses from an architect’s master blueprint versus verbal instructions.</p>
<p>Logging into 40 switches via SSH and typing commands by hand is whispering instructions to 40 builders—by Friday, every house has a slightly different window height (<strong>configuration drift</strong>). Storing your templates in <strong>Git</strong> and pushing them with an <strong>idempotent</strong> tool (Ansible) is handing an inspection robot the master blueprint: if Window A is already 120 cm wide, the robot checks it off and moves on without cutting a second window.</p>
<p><strong>YANG</strong> is the standardized blueprint form, while <strong>NETCONF</strong> (armored truck on SSH port 830) and <strong>RESTCONF</strong> (HTTPS web courier carrying JSON) are the delivery vehicles.</p>
<p><strong>Analogy map:</strong> Standardized blueprint schema = YANG; Armored transactional courier (SSH 830 / XML) = NETCONF; Web API courier (HTTPS / JSON) = RESTCONF; Blueprint version history = Git; Check-then-fix-only-if-needed = Idempotency.</p>
<p><strong>Where the analogy breaks:</strong> A physical wall cannot undo itself in 1 second if a window frame cracks; NETCONF’s <code>commit confirmed</code> automatically rolls the entire switch configuration back if the change cuts off management connectivity.</p>''',
                    L.format('8.4') + ' (master blueprint and inspection robot analogy); ' + AUT,
                    [check('What causes configuration drift across a fleet of production routers and switches?',
                           'Manual CLI edits bypassing the central template',
                           ['Running NTP time synchronization against a Stratum 1 atomic clock',
                            'Using SNMPv3 read-only polling to graph interface bandwidth'],
                           'When administrators make undocumented one-off edits in `configure terminal` on individual boxes, those boxes drift away from the golden configuration in Git.',
                           mc=[AUT_M, AUT_M])]),
            visual(svg(620, 130, 'GitOps Network Automation Pipeline: Git Source of Truth, CI Validation, NETCONF/RESTCONF Push, Drift Audit',
                       box(10, 25, 175, 75, '1. Git Repository', 'Golden Config · YANG')
                       + arrow(185, 62, 225, 62, 'CI Lint')
                       + box(225, 25, 175, 75, '2. Ansible / RESTCONF', 'Idempotent Push (JSON/XML)')
                       + arrow(400, 62, 440, 62, 'TCP 830 / 443')
                       + box(440, 25, 170, 75, '3. Fleet & Drift Diff', 'Commit Confirmed · Audit'))
                   + '''<ol class="ladder-trace"><li>Engineer opens a pull request in Git modifying the VLAN/ACL YAML variables; CI pipeline validates syntax before merge.</li>
<li>Automation runner connects to switches via <strong>NETCONF (TCP 830)</strong> or <strong>RESTCONF (HTTPS 443)</strong> using YANG data models.</li>
<li>Changes load into the candidate datastore with a commit-confirm timer; if verification passes, the commit is finalized.</li>
<li>Nightly drift detection compares live <code>running-config</code> against the Git golden state and alerts on unauthorized manual edits.</li></ol>''',
                   L.format('8.4') + '; ' + AUT,
                   [check('In RESTCONF (and RESTful network APIs), which HTTP method is used to read operational state or configuration without modifying the device?',
                          'GET',
                          ['DELETE', 'POST'],
                          'HTTP GET retrieves a representation of the target resource (read-only); POST creates, PUT replaces, PATCH partially updates, and DELETE removes.',
                          mc=[AUT_M, AUT_M])]),
            tryit('<p>Sort each automation technology into its matching role, then practice saving and verifying clean device configuration in the CLI lab.</p>',
                  L.format('8.4') + '; ' + AUT,
                  [check('Which TCP port does NETCONF over SSH use by default (RFC 6242)?',
                         'TCP port 830',
                         ['UDP port 69 (TFTP)', 'TCP port 25 (SMTP)'],
                         'NETCONF over SSH is assigned IANA standard port TCP 830, providing encrypted, transactional configuration management.',
                         mc=[AUT_M, AUT_M])],
                  widget=sort('Match each automation building block to its role',
                              {'Data Model & State Control': ['YANG: hierarchical schema for config and state', 'Idempotency: running N times yields the same state'],
                               'Transport Protocols': ['NETCONF: XML over SSH (TCP 830) with candidate datastore', 'RESTCONF: JSON/XML over HTTPS (GET/POST/PATCH/DELETE)']},
                              'Together, Git + YANG + NETCONF/RESTCONF eliminate manual copy-paste errors and configuration drift.'),
                  lab={'id': 'sw-hostname-write', 'note': 'Apply a standardized device hostname and verify running-config vs startup-config.'})),
    },
}

STAMPS = {
    '8.1': {'cloud-vpc-architecture-gateways-and-hybrid-connectivity': '81a000000001'},
    '8.2': {'software-defined-networking-sdn-and-sd-wan-planes': '82a000000002'},
    '8.3': {'zero-trust-architecture-ztna-sase-and-microsegmentation': '83a000000003'},
    '8.4': {'network-automation-netconf-restconf-yang-and-gitops': '84a000000004'},
}
