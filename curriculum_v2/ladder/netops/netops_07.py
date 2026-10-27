"""Explanation ladder — NETOPS chapter 7 (Wireless & Enterprise RF Operations / N10-009 Domain 2.4 & 5.4). Pending SME review.

Author: content branch (pass 19). R1 plain, R2 analogy, R3 visual/trace, R4 try-it per concept section, each with a
check that asks the idea in a new form. Facts follow IEEE 802.11ax/be, WPA3/SAE, 802.1X/RADIUS, and CompTIA N10-009.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, section, sort, tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 7

L = 'Course lesson {} (Wireless & Enterprise RF Operations), re-explained'
RF = 'IEEE Std 802.11-2020; IEEE 802.11ax (Wi-Fi 6/6E) and 802.11be (Wi-Fi 7); CompTIA Network+ N10-009 objectives 2.4 and 5.4'
SEC = 'IEEE Std 802.1X-2020; Wi-Fi Alliance WPA3 Specification (SAE / Dragonfly handshake, OWE); RFC 2865 (RADIUS); RFC 5216 (EAP-TLS)'
SURV = 'Cisco / Aruba Enterprise WLAN Site Survey Guides (RSSI, SNR, co-channel vs adjacent-channel interference, 802.11k/v/r roaming)'
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO7-CHANNEL-OVERLAP': {
        'obj': 'NO-3.3',
        'label': 'Choosing overlapping 2.4 GHz channels (e.g. 2, 4, 8) instead of non-overlapping 1, 6 and 11',
        'fix': 'In North America, only channels 1, 6 and 11 are non-overlapping in 2.4 GHz; partial overlap causes adjacent-channel interference (ACI) where APs cannot coordinate polite CSMA/CA backoff.',
        'terms': ['2.4 ghz', 'channel 1', 'channel 6', 'channel 11', 'adjacent-channel interference'],
        'source': L.format('7.1') + '; ' + RF,
        'review': R,
    },
    'MC-L-NO7-WPA3-MODES': {
        'obj': 'NO-3.3',
        'label': 'Confusing WPA3-Personal (SAE) with WPA3-Enterprise (802.1X / EAP-TLS / RADIUS)',
        'fix': 'WPA3-Personal uses Simultaneous Authentication of Equals (SAE) for a shared passphrase; WPA3-Enterprise uses 802.1X with a RADIUS server for per-user or per-certificate identity.',
        'terms': ['wpa3', 'sae', '802.1x', 'radius', 'eap-tls'],
        'source': L.format('7.2') + '; ' + SEC,
        'review': R,
    },
    'MC-L-NO7-STICKY-CLIENT': {
        'obj': 'NO-3.3',
        'label': 'Turning AP transmit power to 100% when roaming fails, worsening the sticky-client problem',
        'fix': 'Excessive AP transmit power makes a distant AP sound loud to a client whose tiny radio cannot talk back; lower 2.4 GHz power, tune cell overlap (15–20%), and enable 802.11k/v/r fast roaming.',
        'terms': ['sticky client', 'roaming', '802.11r', '802.11k', '802.11v', 'transmit power'],
        'source': L.format('7.3') + '; ' + SURV,
        'review': R,
    },
    'MC-L-NO7-RSSI-VS-SNR': {
        'obj': 'NO-3.3',
        'label': 'Judging link quality by RSSI alone while ignoring the noise floor and Signal-to-Noise Ratio (SNR)',
        'fix': 'SNR (dB) is signal minus noise floor (e.g. -60 dBm signal over -90 dBm noise = 30 dB SNR); a strong RSSI still drops frames if a -65 dBm noise floor crushes SNR to 5 dB.',
        'terms': ['rssi', 'snr', 'noise floor', 'dbm', 'mcs'],
        'source': L.format('7.4') + '; ' + SURV,
        'review': R,
    },
}

CH_OV, WPA3_M, STICKY, SNR_M = (
    'MC-L-NO7-CHANNEL-OVERLAP',
    'MC-L-NO7-WPA3-MODES',
    'MC-L-NO7-STICKY-CLIENT',
    'MC-L-NO7-RSSI-VS-SNR',
)

LESSONS = {
    '7.1': {
        'rf-bands-channels-and-802-11-standards': section(
            'RF bands, channels, and 802.11 standards', 'NO-3.3',
            [check('Why do enterprise 2.4 GHz plans use only channels 1, 6, and 11 in North America?',
                   'Those three 20 MHz channels do not overlap',
                   ['Channels 2 through 5 are reserved for military radar only',
                    'Other channels require WPA3-Enterprise certificates to transmit'],
                   'Each 2.4 GHz channel is 20–22 MHz wide while channel centers are only 5 MHz apart, so 1, 6, and 11 are the three non-overlapping slots. Intermediate channels cause adjacent-channel interference.',
                   mc=[CH_OV, CH_OV])],
            plain('''<p>Wi-Fi radios share three main frequency bands.</p>
<ul><li><strong>2.4 GHz</strong> travels farthest through walls, but it is crowded and has only three non-overlapping channels: <strong>1, 6, and 11</strong>.</li>
<li><strong>5 GHz</strong> has shorter range through walls, but offers many non-overlapping 20/40/80 MHz channels (including DFS channels that yield to weather and aviation radar).</li>
<li><strong>6 GHz</strong> (added in <strong>Wi-Fi 6E</strong> and <strong>Wi-Fi 7</strong>) opens a wide, clean band for modern devices with no legacy 802.11n/ac slowdown.</li></ul>
<p>Never pick channels like 2, 4, or 8 on 2.4 GHz. Partial overlap turns neighboring transmissions into uncoordinated noise.</p>
<p>Takeaway: use 1, 6, and 11 on 2.4 GHz, and steer high-density traffic to 5 GHz and 6 GHz.</p>''',
                  L.format('7.1') + '; ' + RF,
                  [check('Which Wi-Fi generation first introduced the 6 GHz spectrum band?',
                         'Wi-Fi 6E (802.11ax)',
                         ['Wi-Fi 5 (802.11ac Wave 2)', 'Wi-Fi 4 (802.11n dual-band)'],
                         'Wi-Fi 6 (802.11ax) operates in 2.4 and 5 GHz, while Wi-Fi 6E extends 802.11ax into the 6 GHz band (followed by Wi-Fi 7 / 802.11be). Wi-Fi 5 is 5 GHz only.',
                         mc=[CH_OV, CH_OV])]),
            analogy('''<p>Think of highway lanes and conversations in a hall.</p>
<p>Two APs on the <strong>same channel</strong> (co-channel) are like two polite speakers sharing one microphone: they hear each other’s preamble and take turns using CSMA/CA. Putting an AP on <strong>channel 3</strong> between channels 1 and 6 is like someone shouting between two rooms so neither group can understand the words and neither knows when to pause—that is <strong>adjacent-channel interference (ACI)</strong>.</p>
<p><strong>Analogy map:</strong> 2.4 GHz = a three-lane country road that reaches far; 5 GHz and 6 GHz = multi-lane expressways with shorter exits; DFS channels = lanes that must yield when an emergency vehicle (radar) approaches.</p>
<p><strong>Where the analogy breaks:</strong> Cars can squeeze slightly closer together on pavement; RF sidebands physically corrupt symbols in the air whenever channel masks overlap.</p>''',
                    L.format('7.1') + ' (highway and microphone analogy); ' + RF,
                    [check('Why is co-channel contention on channel 6 less destructive than adjacent-channel overlap on channel 4?',
                           'Same-channel APs decode preambles and take turns',
                           ['Channel 6 automatically doubles its transmit wattage when shared',
                            'Channel 4 blocks all DHCP broadcast frames at Layer 2'],
                           'Devices on the exact same channel hear 802.11 preambles and defer via CSMA/CA. Partially overlapping channels corrupt frames as raw RF noise without triggering clean polite deferral.',
                           mc=[CH_OV, CH_OV])]),
            visual(svg(600, 130, '2.4 GHz non-overlapping channels 1, 6, and 11 vs 5 GHz and 6 GHz wide spectrum',
                       box(15, 25, 170, 75, '2.4 GHz Band', 'Ch 1 · Ch 6 · Ch 11 (20 MHz)')
                       + arrow(185, 62, 215, 62)
                       + box(215, 25, 170, 75, '5 GHz Band', 'UNII-1/2/3 + DFS (20–80 MHz)')
                       + arrow(385, 62, 415, 62)
                       + box(415, 25, 170, 75, '6 GHz Band', 'Wi-Fi 6E / 7 (up to 320 MHz)'))
                   + '''<ol class="ladder-trace"><li>Audit 2.4 GHz AP radios: lock every AP to channel 1, 6, or 11 at 20 MHz width.</li>
<li>Audit 5 GHz AP radios: assign non-overlapping 20 or 40 MHz channels; verify DFS radar events in logs.</li>
<li>Enable band steering so dual-band/tri-band clients prefer 5 GHz or 6 GHz over congested 2.4 GHz.</li></ol>''',
                   L.format('7.1') + '; ' + RF,
                   [check('What must a 5 GHz AP do when it detects weather or aviation radar on a DFS channel?',
                          'Vacate the channel and move to a clear one',
                          ['Increase transmit power to override the radar pulse',
                           'Switch all connected clients down to 802.11b rates'],
                          'Dynamic Frequency Selection (DFS) regulations require the AP to stop transmitting on that channel and move to a clear channel when radar pulses are detected.',
                          mc=[CH_OV, CH_OV])]),
            tryit('<p>Sort each wireless trait into the matching frequency band or standard, then test a wireless configuration in the lab.</p>',
                  L.format('7.1') + '; ' + RF,
                  [check('In a dense lecture hall with 90 laptops, which 2.4 GHz channel width should you configure?',
                         '20 MHz on channels 1, 6, and 11',
                         ['40 MHz bonded across channels 1 through 9',
                          '80 MHz bonded across the entire 2.4 GHz band'],
                         'Bonding 40 MHz in 2.4 GHz consumes two-thirds of the entire band and destroys three-channel reuse. Always keep 2.4 GHz at 20 MHz width.',
                         mc=[CH_OV, CH_OV])],
                  widget=sort('Match each attribute to its band',
                              {'2.4 GHz Band': ['Only channels 1, 6, and 11 avoid overlap', 'Longest wall penetration, highest interference'],
                               '5 GHz / 6 GHz Bands': ['DFS radar-sharing channels in UNII-2', 'Wi-Fi 6E / Wi-Fi 7 clean high-capacity spectrum']},
                              'Keep 2.4 GHz narrow (20 MHz on 1/6/11) and use 5/6 GHz for high throughput.'),
                  lab={'id': 'wifi-secure', 'note': 'Configure non-overlapping channels and WPA2/WPA3 security on the wireless lab router.'})),
    },
    '7.2': {
        'enterprise-wlan-security-wpa3-802-1x-and-radius': section(
            'Enterprise WLAN security: WPA3, 802.1X, and RADIUS', 'NO-3.3',
            [check('Why do enterprise networks deploy WPA2/WPA3-Enterprise (802.1X) instead of a single shared PSK for 500 staff?',
                   'Each user authenticates via RADIUS with unique session keys',
                   ['WPA3-Personal does not encrypt traffic over the air after login',
                    '802.1X eliminates the need for access points to broadcast beacons'],
                   'With a shared PSK, anyone who leaves knows the secret, and rotating it touches every device. 802.1X with RADIUS revokes one user or certificate centrally and derives a unique session key per client.',
                   mc=[WPA3_M, WPA3_M])],
            plain('''<p>Wireless security has two main families: <strong>Personal</strong> (shared passphrase) and <strong>Enterprise</strong> (individual identity).</p>
<ul><li><strong>WPA3-Personal</strong> replaces WPA2’s 4-way PSK handshake with <strong>SAE (Simultaneous Authentication of Equals)</strong>. Even if an attacker captures the handshake, they cannot run an offline dictionary crack against a weak passphrase, and it adds forward secrecy.</li>
<li><strong>WPA3-Enterprise (802.1X)</strong> uses three roles: the <strong>Supplicant</strong> (client laptop/phone), the <strong>Authenticator</strong> (AP or WLC), and the <strong>Authentication Server</strong> (<strong>RADIUS</strong>).</li>
<li><strong>EAP-TLS</strong> is the strongest EAP method because both client and server prove identity with X.509 certificates—no password ever crosses the air.</li></ul>
<p>Takeaway: use WPA3-SAE for home/SOHO, and 802.1X with RADIUS + EAP-TLS for enterprise staff.</p>''',
                  L.format('7.2') + '; ' + SEC,
                  [check('In 802.1X architecture, which component acts as the Authenticator (enforcement gate)?',
                         'The wireless AP or WLC controller',
                         ['The client laptop requesting network access',
                          'The back-end Active Directory or RADIUS server'],
                         'The client is the Supplicant, the AP/WLC is the Authenticator that blocks non-EAP traffic until approved, and RADIUS is the Authentication Server.',
                         mc=[WPA3_M, WPA3_M])]),
            analogy('''<p>Think of entering a high-security research building.</p>
<p><strong>WPA2/WPA3-Personal</strong> is a keypad door code shared by everyone in the building: if one contractor leaves, you must reprogram every person’s habit. <strong>WPA3-SAE</strong> upgrades that keypad so eavesdroppers watching the door cannot guess the code offline, but it is still one shared secret.</p>
<p><strong>802.1X Enterprise</strong> is a turnstile guard (<strong>Authenticator / AP</strong>) who checks each employee’s smart badge (<strong>Supplicant</strong>) with central security (<strong>RADIUS Server</strong>) before unlocking the gate for that one person.</p>
<p><strong>Analogy map:</strong> Employee with badge = Supplicant; Turnstile guard = Authenticator (AP/WLC); Central security desk = RADIUS Server; Mutual smart-card chip check = EAP-TLS.</p>
<p><strong>Where the analogy breaks:</strong> A physical turnstile only opens a door once; 802.1X also hands the AP and client a fresh per-session encryption key (PMK/PTK) for every frame they send.</p>''',
                    L.format('7.2') + ' (building badge turnstile analogy); ' + SEC,
                    [check('What protection does WPA3-Personal (SAE) add over WPA2-Personal (PSK)?',
                           'Offline dictionary-crack resistance and forward secrecy',
                           ['Per-user Active Directory account revocation via RADIUS',
                            'Automatic VLAN assignment per user group without a switch'],
                           'SAE (Dragonfly handshake) prevents attackers from capturing a 4-way handshake and cracking the passphrase offline, and provides forward secrecy, while RADIUS belongs to Enterprise mode.',
                           mc=[WPA3_M, WPA3_M])]),
            visual(svg(620, 130, '802.1X Authentication Flow between Supplicant, Authenticator AP/WLC, and RADIUS Server',
                       box(10, 30, 165, 70, 'Supplicant', 'Client (EAP-TLS / PEAP)')
                       + arrow(175, 65, 225, 65, 'EAPOL')
                       + box(225, 30, 175, 70, 'Authenticator', 'AP / WLC (Controlled Port)')
                       + arrow(400, 65, 450, 65, 'RADIUS')
                       + box(450, 30, 160, 70, 'Auth Server', 'RADIUS + PKI / AD'))
                   + '''<ol class="ladder-trace"><li>Client associates to the enterprise SSID; AP holds the port closed except for 802.1X EAPOL frames.</li>
<li>AP encapsulates EAP messages inside RADIUS packets (UDP 1812) to the RADIUS server.</li>
<li>RADIUS validates the client’s EAP-TLS certificate (or PEAP credentials) and returns RADIUS Access-Accept plus session key material.</li>
<li>AP and client complete the 4-way handshake to derive a unique Pairwise Transient Key (PTK) and open the data port.</li></ol>''',
                   L.format('7.2') + '; ' + SEC,
                   [check('Which EAP method requires a client certificate on every endpoint and performs mutual TLS authentication?',
                          'EAP-TLS',
                          ['PEAP-MSCHAPv2 with password only', 'Captive portal HTTP redirect'],
                          'EAP-TLS requires X.509 certificates on both the RADIUS server and each client supplicant, eliminating password theft.',
                          mc=[WPA3_M, WPA3_M])]),
            tryit('<p>Order the 802.1X authentication sequence from association to encrypted data transfer.</p>',
                  L.format('7.2') + '; ' + SEC,
                  [check('What standard encrypts open public/guest Wi-Fi traffic without requiring users to type a password?',
                         'OWE (Enhanced Open)',
                         ['Wired Equivalent Privacy (WEP-128)', 'WPS Push-Button PIN mode'],
                         'OWE (Wi-Fi Certified Enhanced Open) uses unauthenticated Diffie-Hellman key exchange so guest traffic is encrypted over the air without a shared password.',
                         mc=[WPA3_M, WPA3_M])],
                  widget=order('Order the 802.1X / EAP-TLS connection flow',
                               ['Supplicant associates to AP; controlled port blocks normal IP traffic',
                                'Supplicant and RADIUS exchange EAP-TLS certificates via the AP',
                                'RADIUS sends Access-Accept and Master Session Key to the AP',
                                'AP and client derive unique PTK and open port for encrypted traffic'],
                               'Notice that normal IP/DHCP traffic cannot flow until RADIUS sends Access-Accept and the pairwise key is installed.'),
                  lab={'id': 'wifi-secure', 'note': 'Harden wireless security settings and verify guest isolation.'})),
    },
    '7.3': {
        'wlc-architectures-capwap-and-fast-roaming': section(
            'WLC architectures, CAPWAP, and fast roaming', 'NO-3.3',
            [check('Users on VoIP Wi-Fi calls drop audio for 2 seconds when walking between hallway APs on 802.1X. Which standard pre-authenticates key material across APs for sub-50 ms handoff?',
                   '802.11r (Fast BSS Transition)',
                   ['802.11b legacy DSSS modulation', 'Spanning Tree PortFast on the client NIC'],
                   'Full 802.1X/RADIUS authentication takes ratusan of milliseconds on every roam unless 802.11r (Fast BSS Transition) caches and distributes key material across controller APs.',
                   mc=[STICKY, STICKY])],
            plain('''<p>Managing 200 standalone (autonomous) APs one by one does not scale. Enterprise networks use <strong>lightweight APs</strong> managed by a <strong>Wireless LAN Controller (WLC)</strong> via <strong>CAPWAP</strong> (UDP ports <strong>5246</strong> control and <strong>5247</strong> data).</p>
<ul><li>In <strong>central/local mode</strong>, CAPWAP tunnels both control and client traffic back to the WLC.</li>
<li>In <strong>FlexConnect (local switching)</strong> at branch offices, control goes to the WLC while VLAN-tagged client traffic drops directly onto the local branch switch.</li>
<li>For smooth walking between APs, cells need <strong>15–20% overlap</strong> at -67 dBm, plus <strong>802.11k</strong> (neighbor reports), <strong>802.11v</strong> (BSS transition hints), and <strong>802.11r</strong> (Fast BSS Transition).</li></ul>
<p>Takeaway: never crank AP power to 100% to fix roaming—that creates sticky clients that cling to a faraway AP.</p>''',
                  L.format('7.3') + '; ' + SURV,
                  [check('What happens when an engineer sets every AP’s 2.4 GHz transmit power to 100% maximum?',
                         'Clients stay stuck to distant APs they cannot reply to',
                         ['Clients roam three times faster between neighboring APs',
                          'CAPWAP control tunnels automatically switch from UDP to BGP'],
                         'An AP blasting at 100 mW sounds loud to a phone whose 15 mW radio cannot reply cleanly, and the high RSSI stops the phone from roaming to a closer AP.',
                         mc=[STICKY, STICKY])]),
            analogy('''<p>Think of an orchestra conductor and a relay race.</p>
<p>Autonomous APs are street musicians playing solo on every corner—changing the song means walking to each one. A <strong>WLC with lightweight APs</strong> is a conductor linked to every player over a headset (<strong>CAPWAP</strong>) so channel, power, and SSID policies stay in sync.</p>
<p>When a user walks down a corridor on a voice call, roaming is a relay baton pass: <strong>802.11k</strong> hands the runner a map of the next runners, <strong>802.11v</strong> nudges them when to hand off, and <strong>802.11r</strong> pre-clears security so they do not stop at a badge desk mid-stride.</p>
<p><strong>Analogy map:</strong> Conductor = WLC; Headset link = CAPWAP (UDP 5246/5247); Map of next APs = 802.11k; Gentle nudge to switch = 802.11v; Pre-cleared security handoff = 802.11r.</p>
<p><strong>Where the analogy breaks:</strong> In a relay race the coach calls the handoff; in Wi-Fi, the <strong>client device</strong> always makes the final decision to roam.</p>''',
                    L.format('7.3') + ' (conductor and relay handoff analogy); ' + SURV,
                    [check('Which device ultimately decides when to roam from one AP to another in 802.11 networks?',
                           'The wireless client device',
                           ['The core router’s OSPF process', 'The DHCP server holding the IP lease'],
                           '802.11k and 802.11v give the client neighbor lists and transition advice, but roaming is always a client-side decision in standard 802.11.',
                           mc=[STICKY, STICKY])]),
            visual(svg(620, 130, 'Lightweight APs tunneling CAPWAP UDP 5246/5247 to WLC with 15-20% roaming overlap',
                       box(15, 25, 165, 75, 'AP-West (Ch 36)', 'Cell edge -67 dBm')
                       + arrow(180, 62, 230, 62, '15–20% overlap')
                       + box(230, 25, 165, 75, 'AP-East (Ch 44)', '802.11k/v/r Fast Roam')
                       + arrow(395, 62, 445, 62, 'CAPWAP 5246')
                       + box(445, 25, 160, 75, 'WLC Controller', 'RRM · Roam Keys'))
                   + '''<ol class="ladder-trace"><li>Client walking east drops below -68 dBm on AP-West (Ch 36).</li>
<li>Client reads its <strong>802.11k</strong> neighbor list instead of scanning all 25 channels blind.</li>
<li>AP-West sends an <strong>802.11v</strong> BSS transition management frame suggesting AP-East (Ch 44).</li>
<li>Client uses <strong>802.11r</strong> cached PMK key material via the WLC to complete handoff in under 40 ms with zero dropped voice packets.</li></ol>''',
                   L.format('7.3') + '; ' + SURV,
                   [check('Which UDP ports must be permitted between branch lightweight APs and a central WLC for CAPWAP?',
                          'UDP 5246 and UDP 5247',
                          ['TCP 179 (BGP) and UDP 520 (RIP)', 'UDP 67 and UDP 68 (DHCP only)'],
                          'CAPWAP uses UDP 5246 for encrypted control messages and UDP 5247 for tunneled data frames.',
                          mc=[STICKY, STICKY])]),
            tryit('<p>Sort each roaming or controller protocol into its exact role.</p>',
                  L.format('7.3') + '; ' + SURV,
                  [check('A branch office wants lightweight APs managed by HQ’s WLC, but wants local user traffic to stay on the branch switch if the WAN link drops. Which AP mode fits?',
                         'FlexConnect (local switching)',
                         ['Autonomous standalone consumer mode', 'Monitor-only rogue sensor mode'],
                         'FlexConnect tunnels control via CAPWAP when the WAN is up but switches VLAN traffic locally at the branch and keeps local SSIDs alive if the WAN drops.',
                         mc=[STICKY, STICKY])],
                  widget=sort('Match each standard to its function',
                              {'Fast Roaming Trio (802.11k/v/r)': ['802.11k: Neighbor AP channel reports', '802.11r: Fast BSS key transition (<50 ms)'],
                               'Controller & Cell Design': ['CAPWAP: UDP 5246/5247 WLC management tunnel', '15–20% cell overlap at -67 dBm for voice']},
                              'Together 802.11k, 802.11v, and 802.11r let voice clients roam across WLC-managed cells without dropping calls.'))),
    },
    '7.4': {
        'site-surveys-snr-and-wireless-troubleshooting': section(
            'Site surveys, SNR, and wireless troubleshooting', 'NO-3.3',
            [check('A warehouse scanner shows RSSI = -58 dBm, yet frame retries are 45% and throughput is 2 Mbps. The spectrum analyzer shows a -63 dBm noise floor from a nearby machine. What is the SNR, and why is it failing?',
                   'SNR is only 5 dB; data needs 20–25 dB SNR',
                   ['SNR is -121 dB; the scanner needs a static IPv4 gateway',
                    'RSSI above -60 dBm guarantees 1 Gbps regardless of noise floor'],
                   'SNR = Signal (-58 dBm) - Noise (-63 dBm) = 5 dB. Because the signal is barely above the noise floor, the radio drops to its lowest MCS rate and retries constantly.',
                   mc=[SNR_M, SNR_M])],
            plain('''<p>When troubleshooting Wi-Fi, never look at signal bars or <strong>RSSI</strong> alone. Always compare signal to the <strong>noise floor</strong>.</p>
<ul><li><strong>RSSI (Received Signal Strength Indicator)</strong> is measured in negative dBm (closer to 0 is stronger: <code>-55 dBm</code> is much stronger than <code>-80 dBm</code>). Target at least <strong>-67 dBm</strong> for voice/video.</li>
<li><strong>Noise floor</strong> is background RF interference (microwaves, cordless phones, industrial motors, bad cables), typically around <code>-90 to -95 dBm</code> in a clean room.</li>
<li><strong>SNR (Signal-to-Noise Ratio)</strong> is <code>Signal - Noise</code> in dB. Aim for <strong>25 dB+</strong>.</li></ul>
<p>Takeaway: strong RSSI with a high noise floor still yields terrible SNR, low MCS rates, and high Layer-2 retry counts.</p>''',
                  L.format('7.4') + '; ' + SURV,
                  [check('Which RSSI value represents the STRONGEST received wireless signal?',
                         '-52 dBm',
                         ['-75 dBm', '-88 dBm'],
                         'dBm values below 1 mW are negative numbers; -52 dBm is closer to 0 dBm (1 mW) and is more than 100 times stronger than -75 dBm.',
                         mc=[SNR_M, SNR_M])]),
            analogy('''<p>Think of talking to a friend in a quiet library versus next to a jet engine.</p>
<p>How loudly your friend speaks is <strong>RSSI</strong>. How loud the room is around you is the <strong>noise floor</strong>. The gap between your friend’s voice and the room noise is <strong>SNR (Signal-to-Noise Ratio)</strong>. In a quiet library (<code>-95 dBm</code> noise), a normal voice (<code>-65 dBm</code>) gives a crisp <strong>30 dB SNR</strong> and you speak at full speed (high <strong>MCS index</strong>).</p>
<p>Next to a roaring machine (<code>-65 dBm</code> noise), even if your friend shouts at <code>-58 dBm</code>, the gap is only <strong>7 dB</strong>—you have to spell out one word at a time and ask “what?” over and over (high 802.11 retry rate).</p>
<p><strong>Analogy map:</strong> Friend’s voice volume = RSSI (dBm); Room background racket = Noise floor (dBm); Margin between voice and racket = SNR (dB); Speaking speed = MCS data rate.</p>
<p><strong>Where the analogy breaks:</strong> Human ears can pick out a familiar voice in a noisy café; a QAM radio constellation mathematically collapses into bit errors whenever SNR drops below the modulation threshold.</p>''',
                    L.format('7.4') + ' (library vs jet-engine SNR analogy); ' + SURV,
                    [check('A client has -62 dBm RSSI and a -92 dBm noise floor. What is the SNR?',
                           '30 dB',
                           ['-154 dB', '1.48 dB'],
                           'SNR in decibels is the difference between signal (-62 dBm) and noise (-92 dBm): -62 - (-92) = +30 dB, which is an excellent margin.',
                           mc=[SNR_M, SNR_M])]),
            visual(svg(620, 130, 'Wireless Site Survey Lifecycle: Predictive Model, Pre-Deployment AP-on-a-Stick, Post-Deployment Validation',
                       box(10, 25, 180, 75, '1. Predictive Survey', 'Floorplan + Wall Attenuation')
                       + arrow(190, 62, 220, 62)
                       + box(220, 25, 180, 75, '2. AP-on-a-Stick', 'Live RF & Spectrum Check')
                       + arrow(400, 62, 430, 62)
                       + box(430, 25, 180, 75, '3. Post-Deployment', 'Verify RSSI ≥ -67, SNR ≥ 25 dB'))
                   + '''<ol class="ladder-trace"><li>Measure RSSI, noise floor, and SNR at the affected desk (target RSSI ≥ -67 dBm, SNR ≥ 25 dB).</li>
<li>Check AP channel utilization and Layer-2 retry percentage (retries &gt; 15% point to RF interference or hidden nodes).</li>
<li>Confirm switchport VLAN trunking and PoE budget (802.3at PoE+ / 802.3bt) if the AP is rebooting or dropping radios.</li></ol>''',
                   L.format('7.4') + '; ' + SURV,
                   [check('After mounting 30 new Wi-Fi 6E access points, several APs boot up with their 6 GHz radios disabled while LAN link lights stay green. What should you check on the switch first?',
                          'PoE power budget and 802.3at/bt class',
                          ['The DNS zone transfer serial number', 'The OSPF router-ID loopback address'],
                          'Tri-band Wi-Fi 6E/7 APs often require 802.3at (PoE+) or 802.3bt (PoE++) wattage; if a switch only supplies 15.4 W (802.3af) or exceeds its PoE budget, the AP disables radios.',
                          mc=[SNR_M, STICKY])]),
            tryit('<p>Order the steps to isolate a wireless “connected, but slow or no internet” ticket from RF to upstream IP.</p>',
                  L.format('7.4') + '; ' + SURV,
                  [check('A rogue AP appears on your floor broadcasting the corporate SSID on channel 11 with a strong signal. What attack is this?',
                         'An Evil Twin attack',
                         ['An BGP route-hijack attack', 'A SQL injection attack'],
                         'An Evil Twin is a rogue AP impersonating a legitimate corporate SSID to lure clients into connecting and intercepting credentials or traffic.',
                         mc=[WPA3_M, SNR_M])],
                  widget=order('Order the wireless fault isolation steps',
                               ['Check RF health first: RSSI (≥ -67 dBm), Noise Floor, SNR (≥ 25 dB), and channel retries',
                                'Verify 802.1X / WPA3 authentication state on the WLC or RADIUS logs',
                                'Confirm the client received a valid DHCP IPv4 address and gateway in the right VLAN',
                                'Test ping to default gateway and DNS resolution to separate LAN from WAN faults'],
                               'Separating Layer 1/2 RF & auth from Layer 3 DHCP/VLAN/DNS prevents blaming the AP for a DHCP or DNS outage.'),
                  lab={'id': 'w11-wlan', 'note': 'Inspect WLAN interface signal, channel, authentication, and radio state from the CLI.'})),
    },
}

STAMPS = {
    '7.1': {'rf-bands-channels-and-802-11-standards': '71a000000001'},
    '7.2': {'enterprise-wlan-security-wpa3-802-1x-and-radius': '72a000000002'},
    '7.3': {'wlc-architectures-capwap-and-fast-roaming': '73a000000003'},
    '7.4': {'site-surveys-snr-and-wireless-troubleshooting': '74a000000004'},
}
