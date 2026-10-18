"""Network+ 1.3 (cloud), 1.6 (topologies and architectures) and 1.8 (modern network environments) — NETOPS 2.1 and 3.2."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG_TOPO = figure(
    'fig-c-topo', 'Three-tier hierarchy versus spine and leaf',
    ['Three-tier:\ncore', 'distribution', 'access\n(users)', 'Spine-leaf:\nspine layer', 'leaf layer\n(servers)'],
    'Left group, three boxes stacked as a chain: the core layer at the top, the distribution layer, then the access layer '
    'where users connect. Right group, two boxes: a spine layer and a leaf layer. In spine and leaf, every leaf switch connects '
    'to every spine switch, so any server reaches any other server in two hops (leaf to spine to leaf), which suits the '
    'east-west traffic between servers in a data centre. A collapsed core merges the core and distribution layers into one.',
    'Three-tier suits campus north-south traffic; spine and leaf gives equal, predictable paths for east-west data-centre traffic.', cols=5)

_FIG_VPC = figure(
    'fig-c-vpc', 'A simple cloud VPC',
    ['Internet', 'Internet\ngateway', 'Public subnet:\nweb server, NAT gw', 'Private subnet:\napp and database', 'On-premises via\nVPN / Direct Connect'],
    'Five boxes in a chain. The internet connects through an internet gateway to a public subnet holding the web server and a '
    'NAT gateway. Behind it is a private subnet with the application and database servers, which reach the internet only '
    'outbound through the NAT gateway. The organisation’s own network connects privately by a site-to-site VPN or a dedicated '
    'link such as AWS Direct Connect. Security groups filter traffic at each instance; network ACLs (security lists) filter '
    'at each subnet.',
    'Public subnet faces the internet gateway; private subnets reach out only through NAT; on-premises connects by VPN or a dedicated link.', cols=5)

HTML_TOPO = f'''
<p>Network+ 1.6 asks you to compare topologies and architectures and to describe traffic flows.</p>
<ul>
<li><strong>Star / hub and spoke</strong> — every node connects to a central device (a switch, or a hub site in a WAN). Simple;
the centre is a single point of failure.</li>
<li><strong>Mesh</strong> — nodes connect to many or all others (full or partial mesh). Resilient but costly in links.</li>
<li><strong>Point to point</strong> — one link between two endpoints (a WAN circuit or a wireless bridge).</li>
<li><strong>Hybrid</strong> — a mix of the above, which is what most real networks are.</li>
<li><strong>Three-tier hierarchical</strong> — <em>access</em> (user ports), <em>distribution</em> (policy, routing between
VLANs) and <em>core</em> (fast transport). A <strong>collapsed core</strong> merges core and distribution for smaller sites.</li>
<li><strong>Spine and leaf</strong> — the data-centre design: servers attach to leaf switches, and every leaf connects to every
spine, giving equal-cost paths and predictable latency.</li>
</ul>
<p><strong>Traffic flows:</strong> <strong>north-south</strong> traffic enters or leaves the data centre (users to servers,
servers to the internet); <strong>east-west</strong> traffic moves between servers inside it — the flow that spine and leaf is
designed for.</p>
{_FIG_TOPO}
{worked('choosing a design for a small data centre', '''<ol>
<li>Requirement: twelve racks of virtualised servers. Most traffic is virtual machine to virtual machine and application to database — east-west.</li>
<li>Three-tier: traffic between servers in different racks may climb to the distribution or core layer and back, so path length depends on where the two servers sit.</li>
<li>Spine and leaf: each rack’s top-of-rack leaf switch connects to every spine. Any two servers in different racks are leaf, spine, leaf — the same number of hops whichever pair you pick.</li>
<li>Growth: add spine switches for more bandwidth between racks; add leaf switches for more server ports.</li>
<li>Decision: spine and leaf for the data centre; the office floors keep a collapsed core because their traffic is mostly north-south.</li></ol>''')}
{scenario('the hub that took every branch down', '''<p>Six branch offices connect hub and spoke to head office. When the head-office WAN router failed, the branches lost
head-office applications <em>and</em> each other, because all branch-to-branch traffic passed through the hub. The options on the
review were a redundant hub (a second router and circuit at head office) or a partial mesh between the busiest branches. Both cost
more links; the question is which failures the business can tolerate.</p>''')}
{cfu(('Which topology connects every leaf switch to every spine switch?', 'Spine and leaf.'),
     ('What does a collapsed core combine?', 'The core and distribution layers of the three-tier model.'),
     ('Server-to-server traffic inside a data centre is called…?', 'East-west traffic.'))}
'''

HTML_CLOUD = f'''
<h4>Cloud networking (Network+ 1.3)</h4>
<p>NIST SP 800-145 defines the service models (IaaS, PaaS, SaaS) and deployment models (public, private, community and
hybrid); Network+ adds the building blocks a network technician configures in a provider’s cloud:</p>
<ul>
<li><strong>VPC</strong> (virtual private cloud) — an isolated virtual network in the provider’s cloud, divided into subnets.</li>
<li><strong>Network security groups</strong> filter traffic to individual instances; <strong>network security lists</strong>
(network ACLs) filter at the subnet boundary.</li>
<li><strong>Internet gateway</strong> — gives a public subnet a route to the internet. <strong>NAT gateway</strong> — lets
instances in a private subnet start outbound connections without being reachable from outside.</li>
<li><strong>Cloud connectivity</strong> — a site-to-site <strong>VPN</strong> over the internet, or a <strong>direct
connect</strong> dedicated private circuit (for example AWS Direct Connect) for predictable bandwidth.</li>
<li><strong>NFV</strong> (network functions virtualization) — firewalls, routers and load balancers run as software on standard servers.</li>
<li><strong>Scalability</strong> (capacity can be added), <strong>elasticity</strong> (it is added and removed automatically
with demand) and <strong>multitenancy</strong> (many customers share infrastructure, logically isolated).</li>
</ul>
{_FIG_VPC}
<h4>Modern network environments (Network+ 1.8)</h4>
<ul>
<li><strong>SDN and SD-WAN</strong> — the control plane is centralised in software. SD-WAN is <strong>application aware</strong>
(steers each application over the best link), supports <strong>zero-touch provisioning</strong> (a new branch device downloads
its configuration when plugged in), is <strong>transport agnostic</strong> (broadband, LTE/5G or MPLS) and uses
<strong>central policy management</strong>.</li>
<li><strong>VXLAN</strong> (RFC 7348) — carries Layer 2 frames inside UDP (port 4789), with a 24-bit segment ID (about 16
million segments, against 4,094 usable VLAN IDs). Uses: <strong>Layer 2 encapsulation</strong> over a routed fabric and
<strong>data centre interconnect (DCI)</strong>.</li>
<li><strong>Zero trust architecture</strong> (NIST SP 800-207) — no implicit trust from network location;
<strong>policy-based authentication</strong> and authorization for every request, with <strong>least privilege</strong>.</li>
<li><strong>SASE / SSE</strong> — secure access service edge combines SD-WAN with cloud-delivered security; security service
edge is the security part (secure web gateway, cloud access security broker, zero trust network access).</li>
<li><strong>Infrastructure as code (IaC)</strong> — configuration written as code: <strong>playbooks and templates</strong> for
reusable tasks, detection of <strong>configuration drift</strong> and compliance, automated upgrades and <strong>dynamic
inventories</strong>. Kept in <strong>source control</strong>: version history, a central repository, branching, and conflict
identification before changes merge.</li>
<li><strong>IPv6</strong> — mitigates IPv4 address exhaustion; transition uses <strong>dual stack</strong> (both protocols on
each interface), <strong>tunnelling</strong> (IPv6 carried over IPv4) and <strong>NAT64</strong> (IPv6-only clients reach IPv4 servers).</li>
</ul>
{worked('choosing cloud building blocks', '''<ol>
<li>Requirement: a public web front end, a database that must never be reachable from the internet, and patch downloads for both.</li>
<li>Web server in a public subnet with a route to the internet gateway; security group allows only TCP 443 inbound.</li>
<li>Database in a private subnet; its security group allows the database port only from the web tier’s security group.</li>
<li>Private subnet’s default route points at the NAT gateway, so it can download patches but accepts no inbound connections.</li>
<li>Head office connects by site-to-site VPN for administration — never by opening admin ports to the internet.</li></ol>''')}
{scenario('the new branch', '''<p>A retailer opens 30 small shops. Each gets a broadband line and an LTE backup. An SD-WAN edge device is
shipped to each shop; staff plug it in, it calls home (zero-touch provisioning) and downloads the central policy, which sends
card-payment traffic over the best-performing link and fails over to LTE automatically. Configuration templates live in
source control, so a change to all 30 shops is reviewed once and applied the same way everywhere.</p>''')}
{cfu(('What lets instances in a private subnet download updates without being reachable from the internet?', 'A NAT gateway.'),
     ('Name two SD-WAN characteristics from Network+ 1.8.', 'Any two of: application aware, zero-touch provisioning, transport agnostic, central policy management.'),
     ('Why does VXLAN scale further than VLANs?', 'Its 24-bit segment ID allows about 16 million segments versus 4,094 usable VLAN IDs.'))}
'''

SUPPLEMENTS = [
    {'course': 'NETOPS', 'chapter': 2, 'lesson': 1, 'id': 'cert-topologies',
     'title': 'Topologies, architectures and traffic flows', 'cert': ['N:1.6'],
     'html': sme_note('Network topologies and architectures (Network+ 1.6).') + HTML_TOPO, 'sources': ['cisco-spineleaf']},
    {'course': 'NETOPS', 'chapter': 3, 'lesson': 2, 'id': 'cert-cloud-modern',
     'title': 'Cloud networking and modern network environments', 'cert': ['N:1.3', 'N:1.8'],
     'html': sme_note('Cloud networking concepts and modern environments: SD-WAN, VXLAN, zero trust, SASE, IaC, IPv6 transition (Network+ 1.3 and 1.8).') + HTML_CLOUD,
     'sources': ['nist-800145', 'aws-vpc', 'rfc7348', 'nist-800207']},
]

GLOSSARY = [
    ('Spine and leaf', 'Data-centre topology in which every leaf (access) switch connects to every spine switch.'),
    ('East-west traffic', 'Traffic between servers inside a data centre; north-south traffic enters or leaves it.'),
    ('VPC', 'Virtual private cloud: an isolated virtual network in a cloud provider’s infrastructure.'),
    ('NAT gateway', 'Cloud service that lets private-subnet instances make outbound connections without accepting inbound ones.'),
    ('SD-WAN', 'Software-defined WAN: centrally managed, application-aware routing over any mix of transports.'),
    ('VXLAN', 'Virtual eXtensible LAN (RFC 7348): Layer 2 frames carried in UDP with a 24-bit segment ID.'),
    ('Zero trust', 'Security model with no implicit trust based on network location; every request is authenticated and authorized (NIST SP 800-207).'),
    ('Infrastructure as code', 'Managing network and system configuration as version-controlled code, applied by automation.'),
]

ITEMS = [
    match('N:1.6', 'NO-2.1', 1, 'Match each description to the topology or architecture.',
          [('Every leaf switch connects to every spine switch', 'Spine and leaf'),
           ('Branch sites all connect to one central hub site', 'Hub and spoke'),
           ('Core and distribution functions combined in one layer', 'Collapsed core'),
           ('Every router has a direct link to every other router', 'Full mesh')],
          'Recognise the Network+ 1.6 topologies from their defining feature.',
          decoys=['Point to point']),
    single('N:1.6', 'NO-2.1', 2, 'A data centre’s main traffic is between application and database servers. Which design best suits this east-west traffic?',
           'Spine and leaf',
           ['Hub and spoke', 'Three-tier campus', 'Point to point'],
           'Spine and leaf gives every server equal two-hop paths to every other server.'),
    single('N:1.6', 'NO-2.1', 3, 'Traffic from remote users to a web server in the data centre is described as which flow?',
           'North-south',
           ['East-west', 'Spine-to-leaf', 'Point-to-multipoint'],
           'Traffic entering or leaving the data centre is north-south.'),
    multi('N:1.6', 'NO-2.1', 4, 'Which TWO are layers of the three-tier hierarchical model? (Choose two.)',
          ['Distribution', 'Access'],
          ['Spine', 'Leaf', 'Edge cache'],
          'Three-tier: core, distribution and access. Spine and leaf is a different, two-layer design.'),
    single('N:1.3', 'NO-3.2', 1, 'Database servers in a cloud private subnet must download patches but must not accept connections from the internet. What should their default route use?',
           'A NAT gateway',
           ['An internet gateway', 'A public IP on each server', 'A security group rule allowing all inbound'],
           'A NAT gateway allows outbound-initiated connections only; an internet gateway route would make them public.'),
    match('N:1.3', 'NO-3.2', 2, 'Match each cloud component to its purpose.',
          [('Security group', 'Filters traffic to individual instances'), ('Network ACL / security list', 'Filters traffic at the subnet boundary'),
           ('Internet gateway', 'Routes a public subnet to the internet'), ('Direct connect', 'Dedicated private circuit to the provider')],
          'Know the VPC building blocks named in Network+ 1.3.',
          decoys=['Zero-touch provisioning']),
    single('N:1.3', 'NO-3.2', 3, 'A firewall that used to be a hardware appliance now runs as a virtual machine on standard servers. What is this an example of?',
           'Network functions virtualization (NFV)',
           ['Multitenancy', 'Infrastructure as code (IaC) deployment', 'A community cloud'],
           'NFV runs network functions as software on commodity hardware.'),
    multi('N:1.8', 'NO-3.2', 1, 'Which THREE are characteristics of SD-WAN listed in Network+ 1.8? (Choose three.)',
          ['Application aware', 'Zero-touch provisioning', 'Transport agnostic'],
          ['Requires MPLS at every site', 'Configured box by box at each branch', 'Limited to one ISP per site'],
          'SD-WAN is application aware, supports zero-touch provisioning, works over any transport and is centrally managed.'),
    single('N:1.8', 'NO-3.2', 2, 'An engineer needs more than 4,094 isolated Layer 2 segments across a routed data-centre fabric. Which technology fits?',
           'VXLAN',
           ['802.1Q VLAN trunking', 'Spanning Tree Protocol', 'NAT64'],
           'VXLAN’s 24-bit segment ID supports about 16 million segments (RFC 7348).'),
    single('N:1.8', 'NO-5.3', 3, 'A security design grants access per request based on identity, device health and policy, regardless of whether the user is on the office LAN. What is this?',
           'Zero trust architecture',
           ['A screened subnet (DMZ) design', 'Port security', 'A collapsed core'],
           'Zero trust removes implicit trust based on network location (NIST SP 800-207).'),
    order('N:1.8', 'NO-3.2', 4, 'Put an infrastructure-as-code change in the right order.',
          ['Create a branch in the repository', 'Edit the configuration template', 'Review and resolve any merge conflicts', 'Merge to the main branch', 'Run the playbook against the inventory'],
          'Source control: branch, change, review and resolve conflicts, merge, then automation applies the approved version.'),
]
