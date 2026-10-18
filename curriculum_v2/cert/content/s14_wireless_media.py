"""Network+ 2.3 (wireless devices and technologies) and 1.5 (transmission media and transceivers) — NETOPS 3.3 and 2.3."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-wlan', 'Choosing channels for a multi-AP floor (2.4 GHz)',
    ['AP-1\nchannel 1', 'AP-2\nchannel 6', 'AP-3\nchannel 11', 'AP-4\nchannel 1\n(far from AP-1)'],
    'Four access points in a row along a floor. In the 2.4 GHz band only channels 1, 6 and 11 do not overlap (in North '
    'America), so neighbouring access points use 1, 6 and 11 in turn, and the fourth access point reuses channel 1 because it '
    'is far enough from the first that their cells barely overlap. In 5 and 6 GHz there are many more non-overlapping 20 MHz '
    'channels, and wider channels (40, 80, 160 MHz) trade channel count for speed.',
    'Adjacent cells never share a channel; reuse a channel only where cells do not overlap.', cols=4)

HTML_WLAN = f'''
<h4>Channels and frequencies</h4>
<ul>
<li><strong>2.4 GHz</strong> — longest range and best wall penetration, but only three <strong>non-overlapping channels</strong>
(1, 6 and 11 in North America) and the most interference. <strong>5 GHz</strong> — many more channels, shorter range.
<strong>6 GHz</strong> (Wi-Fi 6E and 7) — the most clean spectrum; the Wi-Fi Alliance requires WPA3 (or Enhanced Open) there.</li>
<li><strong>Channel width</strong> — 20 MHz is the most robust; 40/80/160 MHz bonding increases speed but leaves fewer
non-overlapping channels, so dense deployments use narrower channels.</li>
<li><strong>Regulatory impacts / 802.11h</strong> — in parts of the 5 GHz band, APs must use <strong>DFS</strong> (dynamic frequency
selection, moving off a channel when radar is detected) and <strong>TPC</strong> (transmit power control).</li>
<li><strong>Band steering</strong> — the AP nudges dual-band clients from 2.4 GHz to 5 or 6 GHz.</li>
</ul>
{_FIG}
<h4>Identifiers, network types and hardware</h4>
<ul>
<li><strong>SSID</strong> is the network name; the <strong>BSSID</strong> is the MAC address of one AP radio; the <strong>ESSID</strong>
is one SSID served by many APs so clients can roam.</li>
<li><strong>Infrastructure</strong> mode (clients talk through an AP), <strong>ad hoc</strong> (devices talk directly),
<strong>mesh</strong> (APs relay to each other wirelessly) and <strong>point to point</strong> (a wireless bridge between buildings).</li>
<li><strong>Antennas</strong> — <strong>omnidirectional</strong> radiate all around (ceiling APs); <strong>directional</strong> antennas
(patch, Yagi, dish) focus energy for long links or corridors.</li>
<li><strong>Autonomous</strong> APs are configured one by one; <strong>lightweight</strong> APs are managed by a wireless LAN controller
(often over CAPWAP), which pushes the same configuration to all of them.</li>
<li><strong>Security</strong> — WPA2 or, better, <strong>WPA3</strong>; <strong>PSK</strong> (one shared passphrase) suits homes and small offices,
<strong>Enterprise</strong> (802.1X with a RADIUS server) gives each user their own credentials; <strong>guest networks</strong>
are isolated and often use a <strong>captive portal</strong> for terms or sign-in.</li>
</ul>
{worked('a conference room that drops calls', '''<ol>
<li>Wi-Fi analyzer in the room: three APs audible on 2.4 GHz, two on channel 6; the 5 GHz radios use 80 MHz channels and two overlap.</li>
<li>Re-plan: 2.4 GHz neighbours on 1/6/11; 5 GHz to 40 MHz width so neighbouring APs get separate channels; enable band steering.</li>
<li>Retest during a meeting: retries drop and calls hold. Record the channel plan in the network documentation.</li></ol>''')}
{scenario('the warehouse aisles', '''<p>A warehouse has long aisles between tall metal racks. Ceiling-mounted access points with omnidirectional
antennas give strong signal in the open areas but weak signal halfway down each aisle, where the racks absorb and reflect it.
The wireless survey recommends directional antennas aimed along the aisles, a 2.4 GHz plan that uses only channels 1, 6 and
11, and a re-survey after the change instead of simply raising transmit power.</p>''')}
{cfu(('Which 2.4 GHz channels do not overlap in North America?', '1, 6 and 11.'),
     ('What does a BSSID identify?', 'One AP radio (its MAC address); the ESSID is the network name across many APs.'),
     ('Lightweight or autonomous: which AP is managed by a controller?', 'Lightweight.'))}
'''

HTML_MEDIA = f'''
<h4>Transmission media and transceivers (Network+ 1.5)</h4>
<ul>
<li><strong>Wireless:</strong> the 802.11 family (Wi-Fi 4 = 802.11n, Wi-Fi 5 = 802.11ac, Wi-Fi 6/6E = 802.11ax, Wi-Fi 7 = 802.11be),
<strong>cellular</strong> (4G/LTE, 5G) and <strong>satellite</strong> links for remote sites (geostationary satellites add
noticeable latency; low-earth-orbit services far less).</li>
<li><strong>Wired (802.3):</strong> twisted-pair copper (1000BASE-T, 10GBASE-T), <strong>single-mode</strong> fibre (narrow core,
long distances, laser optics) versus <strong>multimode</strong> fibre (wider core, shorter runs, cheaper optics);
<strong>direct attach copper (DAC) / twinax</strong> cables for short rack-to-rack links; <strong>coaxial</strong> cable for cable
broadband. <strong>Plenum</strong>-rated jacket is required in air-handling spaces because it produces less toxic smoke.</li>
<li><strong>Transceivers</strong> carry Ethernet or Fibre Channel; form factors <strong>SFP</strong>/SFP+ (1/10/25 Gb/s) and
<strong>QSFP</strong> (four lanes: 40/100 Gb/s and up). Both ends must match: fibre type, wavelength and speed.</li>
<li><strong>Connectors:</strong> <strong>LC</strong> (small, duplex fibre — most SFPs), <strong>SC</strong> (square push-pull fibre),
<strong>ST</strong> (round bayonet fibre), <strong>MPO</strong> (multi-fibre for 40/100G), <strong>RJ45</strong> (Ethernet),
<strong>RJ11</strong> (telephone/DSL), <strong>F-type</strong> (coax broadband) and <strong>BNC</strong> (coax, older or video).</li>
</ul>
{figure('fig-c-fibrelink', 'A 10 Gb/s fibre link between two switches',
    ['Switch A\nSFP+ port', 'Transceiver\n10GBASE-LR', 'Single-mode fibre\nLC to LC duplex', 'Transceiver\n10GBASE-LR', 'Switch B\nSFP+ port'],
    'Five boxes in a chain. Switch A has an SFP+ port holding a 10GBASE-LR transceiver, which is designed for single-mode fibre. '
    'A duplex single-mode patch lead with LC connectors runs to an identical 10GBASE-LR transceiver in an SFP+ port on switch B. '
    'Each part must match the others: the same speed, the same fibre type and wavelength, and connectors that fit the transceiver.',
    'A fibre link only comes up when transceivers, fibre type and connectors match at both ends.', cols=5)}
{worked('picking media for three links', '''<ol>
<li>Server to top-of-rack switch, 2 m: a direct attach copper (DAC) cable — cheap, no separate optics.</li>
<li>Office floor to wiring closet, 60 m: twisted-pair copper, which Ethernet supports up to 100 m per channel.</li>
<li>Between two buildings, several hundred metres: beyond copper’s 100 m, so fibre. Check the transceiver datasheet for the rated distance on the chosen fibre type; for long runs that means single-mode.</li>
<li>Outdoors or between buildings, fibre also avoids the ground-potential and lightning problems of copper.</li></ol>''')}
{scenario('the link that would not come up', '''<p>A new fibre run between two closets shows no link. Both ends have LC connectors, but one switch holds a
short-range multimode transceiver and the other a long-range single-mode one. Swapping in a matching pair brings the link up.
The change record now lists the transceiver part numbers at both ends.</p>''')}
{cfu(('Why is single-mode fibre used between buildings 5 km apart?', 'Its narrow core and laser optics support long distances; multimode is for shorter runs.'),
     ('Which connector do most SFP fibre transceivers use?', 'LC (duplex).'),
     ('Why must cable in a ceiling air-return space be plenum-rated?', 'Plenum jackets produce less toxic smoke in a fire, and building codes require them there.'))}
'''

SUPPLEMENTS = [
    {'course': 'NETOPS', 'chapter': 3, 'lesson': 3, 'id': 'cert-wlan', 'title': 'Wireless channels, identifiers, antennas and AP types',
     'cert': ['N:2.3'], 'html': sme_note('Wireless device and technology selection (Network+ 2.3).') + HTML_WLAN, 'sources': ['ieee-80211', 'wfa-wpa3']},
    {'course': 'NETOPS', 'chapter': 2, 'lesson': 3, 'id': 'cert-media', 'title': 'Transmission media, transceivers and connectors',
     'cert': ['N:1.5'], 'html': sme_note('Transmission media and transceivers (Network+ 1.5).') + HTML_MEDIA, 'sources': ['ieee-80211']},
]

GLOSSARY = [
    ('BSSID', 'Basic service set identifier: the MAC address of one access-point radio.'),
    ('Band steering', 'AP feature that encourages dual-band clients onto the 5 or 6 GHz band.'),
    ('DFS', 'Dynamic frequency selection (802.11h): 5 GHz APs leave a channel when radar is detected.'),
    ('Lightweight AP', 'An access point managed by a wireless LAN controller rather than configured individually.'),
    ('DAC (twinax)', 'Direct attach copper cable with transceivers built on, for short high-speed links.'),
    ('QSFP', 'Quad small form-factor pluggable transceiver: four lanes for 40 Gb/s and faster links.'),
]

ITEMS = [
    single('N:2.3', 'NO-3.3', 1, 'Three APs cover adjacent areas on 2.4 GHz. Which channel plan avoids co-channel and adjacent-channel interference?',
           'Channels 1, 6 and 11',
           ['Channels 1, 2 and 3', 'Channels 6, 6 and 6', 'Channels 3, 7 and 9'],
           'Only 1, 6 and 11 are non-overlapping in the 2.4 GHz band (North America).'),
    match('N:2.3', 'NO-3.3', 2, 'Match each wireless term to its meaning.',
          [('BSSID', 'MAC address of one AP radio'), ('ESSID', 'One network name served by many APs'),
           ('Band steering', 'Moving dual-band clients to 5/6 GHz'), ('Captive portal', 'Web page guests must accept before access')],
          'Identifiers and features from Network+ 2.3.',
          decoys=['Spanning tree']),
    multi('N:2.3', 'NO-3.3', 3, 'A company wants each employee to authenticate to Wi-Fi with their own directory credentials. Which TWO are required? (Choose two.)',
          ['WPA2/WPA3-Enterprise (802.1X)', 'A RADIUS server'],
          ['A pre-shared key printed on the wall', 'An ad hoc network', 'A directional Yagi antenna'],
          'Enterprise mode uses 802.1X with RADIUS so each user has individual credentials.'),
    single('N:2.3', 'NO-3.3', 4, 'A 5 GHz AP keeps changing channel near an airport. Logs show radar detection events. Which standard explains this?',
           '802.11h (DFS and TPC)',
           ['802.1Q tagging', '802.3bt PoE', '802.11e (WMM quality of service)'],
           'DFS, defined in 802.11h, requires APs to vacate channels where radar is detected.'),
    single('N:2.3', 'NO-3.3', 5, 'Two buildings 300 m apart need a wireless link between them. Which antenna type is most appropriate?',
           'A pair of directional antennas',
           ['Omnidirectional ceiling antennas', 'Ad hoc laptop radios', 'A single mesh AP'],
           'Point-to-point links use directional antennas to focus energy on the remote end.'),
    match('N:1.5', 'NO-2.3', 1, 'Match each connector to its typical use.',
          [('LC', 'Duplex fibre on SFP transceivers'), ('F-type', 'Coax broadband to a cable modem'),
           ('RJ11', 'Telephone line / DSL'), ('MPO', 'Multi-fibre trunk for 40/100G')],
          'Recognise the connectors listed in Network+ 1.5.',
          decoys=['RJ45 on fibre']),
    single('N:1.5', 'NO-2.3', 2, 'A new 10 Gb/s link between two switches in the same rack needs the cheapest option with low latency. Which is most suitable?',
           'A DAC (twinax) cable',
           ['Single-mode fibre with long-reach optics', 'Category 5e copper', 'A satellite link'],
           'DAC cables suit short in-rack runs at 10G and above.'),
    single('N:1.5', 'NO-2.3', 3, 'A fibre link will not come up. One end has a single-mode transceiver; the other has a multimode transceiver. What is the problem?',
           'Transceiver and fibre type mismatch',
           ['The cable is not plenum-rated', 'The link needs PoE', 'Both ends need RJ45 copper connectors instead'],
           'Both ends must match fibre type, wavelength and speed.'),
    multi('N:1.5', 'NO-2.3', 4, 'Which TWO statements about fibre are correct? (Choose two.)',
          ['Single-mode supports longer distances than multimode', 'Multimode has a wider core than single-mode'],
          ['Multimode is required for runs over 10 km', 'Single-mode uses RJ45 connectors', 'Fibre is affected by EMI like copper'],
          'Single-mode: narrow core, long distance. Multimode: wider core, shorter runs. Fibre is immune to EMI.'),
]
