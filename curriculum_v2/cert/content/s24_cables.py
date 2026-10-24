"""A+ Core 1 3.2 (cable types and connectors) — ITSUP 3.4.  Round 2 of pass 11."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-cables', 'Cable families and their connectors',
    ['Twisted pair:\nRJ45 (RJ11 for phone)', 'Coaxial:\nF-type', 'Fibre:\nST, SC, LC', 'Peripheral:\nUSB, Lightning, serial DB9', 'Video:\nHDMI, DP, DVI, VGA', 'Internal:\nSATA, Molex'],
    'Six boxes. Twisted-pair copper Ethernet ends in an 8-position RJ45 plug; the smaller RJ11 is for telephone and DSL lines. '
    'Coaxial cable for cable modems and TV uses a screw-on F-type connector. Fibre uses ST (bayonet twist), SC (square push-pull) '
    'or LC (small latching, common in SFP modules). Peripheral cables are USB (Type-A, Type-B, Mini, Micro, USB-C), Apple '
    'Lightning and legacy RS-232 serial on a 9-pin DB9. Video cables are HDMI, DisplayPort, DVI and analogue VGA. Inside the PC, '
    'SATA carries drive data and power, and the 4-pin Molex connector carries peripheral power.',
    'Name the family first, then the connector, then the limit (speed or length) that matters for the job.', cols=3)

HTML = ('\n<p>A+ Core 1 3.2 asks you to name cables and connectors on sight and pick the right one for a job.</p>\n<h4>Network cables</h4>\n<table class="table table-sm"><caption>Twisted-pair copper categories (ANSI/TIA-568; 100 m channel unless stated)</caption>\n<thead><tr><th scope="col">Category</th><th scope="col">Typical Ethernet use</th></tr></thead><tbody>\n<tr><td>Cat 5e</td><td>1 Gbps (1000BASE-T) to 100 m</td></tr>\n<tr><td>Cat 6</td><td>1 Gbps to 100 m; 10 Gbps only on short runs (about 55 m)</td></tr>\n<tr><td>Cat 6a</td><td>10 Gbps (10GBASE-T) to the full 100 m</td></tr>\n<tr><td>Cat 8</td><td>25/40 Gbps over short data-centre runs (up to 30 m), shielded</td></tr>\n</tbody></table>\n<ul>\n<li><strong>UTP vs. STP</strong> — unshielded twisted pair is the office default; shielded twisted pair adds foil or braid for\nelectrically noisy places (motors, lifts, fluorescent ballasts) and must be grounded to work.</li>\n<li><strong>T568A and T568B</strong> — the two TIA-568 pin-outs. They swap the green and orange pairs. Use the same standard on\nboth ends for a straight-through cable; A on one end and B on the other makes a crossover.</li>\n<li><strong>Plenum-rated</strong> (CMP) jacket — required in air-handling spaces above drop ceilings or below raised floors,\nbecause it burns with less smoke and toxic fumes than ordinary PVC (NFPA 70). Riser (CMR) is for vertical runs between floors.</li>\n<li><strong>Direct burial</strong> — outdoor cable with a gel-filled or water-blocking, UV-resistant jacket that can go in the ground without conduit.</li>\n<li><strong>Coaxial</strong> — RG-6 with an F-type screw connector for cable modems and TV.</li>\n<li><strong>Fibre</strong> — single-mode (small core, laser, kilometres) or multimode (larger core, shorter in-building runs);\nconnectors ST (bayonet), SC (push-pull) and LC (small form factor). Fibre is immune to electrical interference.</li>\n<li><strong>RJ45</strong> (8P8C) for Ethernet; <strong>RJ11</strong> (smaller, 6-position) for phone lines and DSL.\nA <strong>punchdown block</strong> (for example a 110 block) terminates horizontal cable in the wiring closet using a punchdown tool.</li>\n</ul>\n<h4>Peripheral, video and internal cables</h4>\n<ul>\n<li><strong>USB 2.0</strong> — 480 Mbps. <strong>USB 3.x</strong> — 5, 10 or 20 Gbps (USB 3.2 Gen 1, Gen 2, Gen 2x2). <strong>USB-C</strong>\nis a reversible connector, not a speed: it can carry USB 2.0 up to USB4, power delivery, DisplayPort alternate mode or\n<strong>Thunderbolt</strong> (Thunderbolt 3/4 at 40 Gbps). <strong>MicroUSB and MiniUSB</strong> are older small connectors; Apple\n<strong>Lightning</strong> is Apple’s own 8-pin connector, replaced by USB-C from iPhone 15.</li>\n<li><strong>Serial</strong> — RS-232 on a 9-pin <strong>DB9</strong> (strictly DE-9) connector; still used for switch and router console ports\n(often through a USB-to-serial adapter).</li>\n<li><strong>HDMI</strong> — digital video and audio, TVs and projectors. <strong>DisplayPort</strong> — digital video and audio, can daisy-chain monitors.\n<strong>DVI</strong> — DVI-D digital, DVI-A analogue, DVI-I both. <strong>VGA</strong> — analogue, 15-pin DE-15, no audio.</li>\n<li><strong>SATA</strong> — 7-pin data and 15-pin power to internal drives; <strong>eSATA</strong> — external SATA (shielded, up to 2 m).\n<strong>Molex</strong> — 4-pin peripheral power (12 V and 5 V) for older drives and fans.</li>\n<li><strong>Adapters</strong> — DVI-D to HDMI is a simple passive adapter because both are digital; HDMI or DisplayPort to VGA needs an\nactive converter (digital to analogue). A dongle cannot add a speed the port does not have.</li>\n</ul>\n' + str(_FIG) + '\n' + str(worked('choosing cable for a new office', '''<ol>
<li>Desk drops run 70 m through the ceiling void that is also the air return: Cat 6a, plenum-rated, terminated T568B at both ends.</li>
<li>Runs end on a 110 punchdown block in the wiring closet, then patch to the switch with short patch cords.</li>
<li>The link to the building across the car park is 400 m: copper cannot reach, so multimode or single-mode fibre with LC connectors on SFP modules.</li>
<li>Conference room: HDMI to the screen, with a USB-C (DisplayPort alternate mode) adapter for laptops that have no HDMI port.</li></ol>''')) + '\n' + str(scenario('the crossover nobody meant to make', '''<p>A technician makes a replacement patch cord and the PC shows a link at only 100 Mbps, or none on an older switch.
Checking the plugs against the TIA-568 colour chart shows T568A on one end and T568B on the other: the green and orange pairs are
swapped. Most modern ports auto-sense (Auto-MDIX) and cope, but the cable is not standard. The technician re-terminates both ends
as T568B and tests the cable with a cable tester before it goes back into service.</p>''')) + '\n' + str(cfu(('What is the difference between T568A and T568B?', 'The green and orange pairs swap positions; use the same one on both ends of a straight-through cable.'),
     ('Where is plenum-rated cable required?', 'In air-handling spaces such as the void above a drop ceiling used for return air.'),
     ('Why can DVI-D to HDMI be a passive adapter but HDMI to VGA cannot?', 'DVI-D and HDMI are both digital; VGA is analogue, so a converter is needed.'))) + '\n')

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 3, 'lesson': 4, 'id': 'cert-cables', 'title': 'Cable types and connectors',
     'cert': ['A1:3.2'], 'html': sme_note('Cable types, connectors, features and purposes (A+ Core 1 3.2).') + HTML,
     'sources': ['tia568', 'nfpa70', 'usbif', 'vesa-dp', 'hdmi-la']},
]

GLOSSARY = [
    ('T568A / T568B', 'The two TIA-568 RJ45 pin-outs; they swap the green and orange pairs.'),
    ('Plenum-rated cable', 'Cable with a low-smoke, fire-resistant (CMP) jacket for air-handling spaces.'),
    ('Direct burial cable', 'Outdoor cable with a water-blocking, UV-resistant jacket that can be laid in the ground.'),
    ('Punchdown block', 'Termination block (such as a 110 block) where horizontal cable is punched down in the wiring closet.'),
    ('F-type connector', 'Screw-on coaxial connector used for cable modems and TV.'),
    ('DB9', 'Nine-pin D-subminiature connector (DE-9) used for RS-232 serial.'),
]

MISCONCEPTIONS = {
    'MC-C-IT3-USBC-IS-SPEED': {'obj': 'IT-3.4', 'label': 'Thinking USB-C (the connector) tells you the speed or protocol',
                               'fix': 'USB-C is a connector; it can carry USB 2.0 to USB4, Thunderbolt or DisplayPort.', 'terms': ['usb-c', 'thunderbolt', 'displayport', 'connector']},
    'MC-C-IT3-ANALOG-DIGITAL': {'obj': 'IT-3.4', 'label': 'Treating analogue VGA and digital HDMI/DVI-D/DisplayPort as passively interchangeable',
                                'fix': 'Digital-to-analogue needs an active converter; digital-to-digital can be passive.', 'terms': ['vga', 'analogue', 'hdmi', 'adapter']},
    'MC-C-IT3-CONNECTOR-MIX': {'obj': 'IT-3.4', 'label': 'Mixing up which connector belongs to which cable family',
                               'fix': 'RJ45 is Ethernet, RJ11 is phone/DSL, F-type is coax, ST/SC/LC are fibre.', 'terms': ['rj45', 'rj11', 'f-type', 'lc']},
    'MC-C-IT3-JACKET-ROLE': {'obj': 'IT-3.4', 'label': 'Confusing plenum, riser, direct burial and shielding by what they protect against',
                             'fix': 'Plenum is fire/smoke rating for air spaces; direct burial is for the ground; shielding is for interference.', 'terms': ['plenum', 'direct burial', 'shielded', 'riser']},
    'MC-C-IT3-PINOUT': {'obj': 'IT-3.4', 'label': 'Thinking mixing T568A and T568B on one cable still gives a standard straight-through cable',
                        'fix': 'Same standard both ends is straight-through; A to B is a crossover.', 'terms': ['t568a', 't568b', 'crossover', 'straight-through']},
    'MC-C-IT3-COPPER-REACH': {'obj': 'IT-3.4', 'label': 'Expecting a higher copper category to extend beyond the 100 m channel',
                              'fix': 'Copper Ethernet is limited to 100 m; longer runs need fibre.', 'terms': ['100 m', 'fibre', 'cat 6a', 'channel']},
}

ITEMS = [
    single('A1:3.2', 'IT-3.4', 11, 'A laptop’s only video output is USB-C. The projector has HDMI. What is needed?',
           'A USB-C to HDMI adapter that uses DisplayPort alternate mode',
           ['Nothing: every USB-C port outputs HDMI natively at any speed', 'A USB-C to RJ45 Ethernet dongle and a network projector cable',
            'A passive VGA to HDMI cable plugged into a USB-A port'],
           'USB-C can carry video through DisplayPort alternate mode; an adapter converts to HDMI. VGA is analogue and needs active conversion.',
           mc=['MC-C-IT3-USBC-IS-SPEED', None, 'MC-C-IT3-ANALOG-DIGITAL']),
    match('A1:3.2', 'IT-3.4', 12, 'Match each connector to the cable it terminates.',
          [('RJ45', 'Twisted-pair Ethernet'), ('RJ11', 'Telephone line or DSL'), ('F-type', 'Coaxial cable to a cable modem'),
           ('LC', 'Fibre to an SFP module'), ('DB9', 'RS-232 serial console')],
          'Connector families from A+ Core 1 3.2.', decoys=['15-pin SATA power']),
    single('A1:3.2', 'IT-3.4', 13, 'New network cable must run through the space above a drop ceiling that the building uses for return air. Which jacket rating is required?',
           'Plenum-rated (CMP)', ['Direct burial', 'Shielded twisted pair', 'Riser-rated (CMR)'],
           'Air-handling spaces need plenum-rated cable because it gives off less smoke and toxic gas in a fire (NFPA 70).',
           mc=['MC-C-IT3-JACKET-ROLE', 'MC-C-IT3-JACKET-ROLE', 'MC-C-IT3-JACKET-ROLE']),
    single('A1:3.2', 'IT-3.4', 14, 'A patch cord has T568A on one end and T568B on the other. What kind of cable is it?',
           'A crossover cable', ['A straight-through cable', 'A rollover (console) cable', 'A shielded cable'],
           'A-to-B swaps the green and orange pairs, which makes a crossover.',
           mc=['MC-C-IT3-PINOUT', None, None]),
    multi('A1:3.2', 'IT-3.4', 15, 'Which TWO connectors carry digital video? (Choose two.)',
          ['HDMI', 'DisplayPort'], ['VGA', 'RJ11', 'Molex'],
          'HDMI and DisplayPort are digital; VGA is analogue; RJ11 is phone and Molex is power.',
          mc=['MC-C-IT3-ANALOG-DIGITAL', 'MC-C-IT3-CONNECTOR-MIX', None]),
    single('A1:3.2', 'IT-3.4', 16, 'Two buildings are 350 m apart. Which cable should join their switches?',
           'Fibre optic cable', ['Cat 6a twisted pair', 'Cat 8 twisted pair', 'RG-6 coaxial cable'],
           'Copper Ethernet is limited to a 100 m channel; fibre reaches hundreds of metres or more.',
           mc=['MC-C-IT3-COPPER-REACH', 'MC-C-IT3-COPPER-REACH', None]),
]
