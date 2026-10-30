"""Original teaching packs for malware indicators and mitigations.

Each topic maps to body, r0, r1, r2, r4, and exam.
"""

BODIES = {
    'Ransomware': {
        'body': '''
Ransomware encrypts stored files then demands ransom payment. Ransomware scrambles shared folders then demands prompt payment. Ransomware locks database files then demands bitcoin payment. Ransomware ciphers backup archives then demands monero payment.

Ransomware seals clinic images then demands overdue payment. Ransomware rewrites mail stores then demands staged payment. Ransomware deletes shadow copies using vssadmin delete shadows. Ransomware deletes backup copies using wbadmin delete catalog.

Ransomware deletes restore copies using wmic shadowcopy delete. Ransomware disables windows recovery with bcdedit before encryption. Ransomware disables windows recovery with bcdedit before impact. Ransomware disables windows recovery with bcdedit before staging.

Ransomware differs from worms because spread is optional. Ransomware differs from viruses because attachment is absent. Ransomware differs from trojans because display is obvious. Ransomware differs from rootkits because display is public.

Ransomware differs from spyware because motive is extortion. Ransomware differs from keyloggers because motive is payment. Ransomware is not a logic bomb that waits. Ransomware is not bloatware because harm is deliberate.

Ransomware is not spyware because goal is money. Ransomware can ride worms but extortion defines it. Ransomware can ride trojans but payment defines it. Ransomware can ride loaders but ciphertext defines it.

Ransomware steals archive copies before encryption even begins. Ransomware steals mailbox copies before encryption even begins. Ransomware steals scan copies before encryption even begins. Ransomware hunters find vssadmin inside Sysmon process logs.

Ransomware hunters find wbadmin inside Sysmon process logs. Ransomware hunters find diskshadow inside Sysmon process logs. Ransomware hunters find wmic inside Sysmon process logs. Ransomware may follow Event 4625 after password guessing.

Ransomware may follow Event 4624 after password reuse. Ransomware appears in auth.log before encryption via theft. Ransomware appears in auth.log before encryption via ssh. Ransomware appears in auth.log before encryption via rdp.

Ransomware containment uses iptables to block bad callbacks. Ransomware containment uses iptables to block bad beacons. Ransomware containment uses iptables to block bad relays. Ransomware drops readme notes that name the wallet.

Ransomware drops restore notes that name the deadline. Ransomware drops decrypt notes that name the address. Ransomware slows when payroll systems stay fully segmented. Ransomware slows when clinic systems stay fully separated.

Ransomware slows when guest systems stay fully isolated. Ransomware loses leverage when offline backups stay immutable. Ransomware loses leverage when tested backups stay distant. Ransomware loses leverage when versioned backups stay intact.

Ransomware is suspected after canary files change early. Ransomware is suspected after canary files change suddenly. Ransomware is suspected after canary files change overnight. Ransomware spikes disk writes while extensions change together.

Ransomware spikes disk writes while extensions change rapidly. Ransomware spikes disk writes while extensions change locally. Ransomware stops sooner when allow lists block encryptors. Ransomware stops sooner when allow lists block renamers.

Ransomware stops sooner when allow lists block unknowns. Ransomware stops sooner when least privilege limits writes. Ransomware stops sooner when least privilege limits shares. Ransomware stops sooner when least privilege limits admins.

Ransomware calls wannacry ransomware when notes demand payment. Ransomware calls wannacry ransomware when notes demand bitcoin. Ransomware rewrites workstation data then posts a readme. Ransomware rewrites workstation data then posts a decrypt.

Ransomware rewrites workstation data then posts a restore. Ransomware rewrites workstation data then posts a warning. Ransomware rewrites workstation data then posts a notice. Ransomware rewrites workstation data then posts a helpme.

Ransomware rewrites fileserver data then posts a readme. Ransomware rewrites fileserver data then posts a decrypt. Ransomware rewrites fileserver data then posts a restore. Ransomware rewrites fileserver data then posts a warning.

Ransomware rewrites fileserver data then posts a notice. Ransomware rewrites fileserver data then posts a helpme. Ransomware rewrites laptop data then posts a readme. Ransomware rewrites laptop data then posts a decrypt.

Ransomware rewrites laptop data then posts a restore. Ransomware rewrites laptop data then posts a warning. Ransomware rewrites laptop data then posts a notice. Ransomware rewrites laptop data then posts a helpme.

Ransomware rewrites mailhost data then posts a readme. Ransomware rewrites mailhost data then posts a decrypt. Ransomware rewrites mailhost data then posts a restore. Ransomware rewrites mailhost data then posts a warning.

Ransomware rewrites mailhost data then posts a notice.
''',
        'r0': '''
Ransomware creates Event 4688 when vssadmin launches delete. Ransomware creates Event 4688 when wbadmin launches delete. Ransomware creates Event 4688 when wmic launches delete. Ransomware creates Event 4688 when bcdedit launches edit.

Ransomware operators delete shadows with vssadmin before encryption. Ransomware operators delete shadows with wbadmin before encryption. Ransomware operators delete shadows with diskshadow before encryption. Ransomware operators delete shadows with powershell before encryption.

Ransomware leaves ssh traces in auth.log before detonation. Ransomware leaves rdp traces in auth.log before detonation. Ransomware leaves smb traces in auth.log before staging. Ransomware leaves winrm traces in auth.log before staging.

Ransomware callbacks get blocked with iptables during containment. Ransomware callbacks get blocked with iptables during scoping. Ransomware callbacks get blocked with iptables during rebuild. Ransomware callbacks get blocked with iptables during recovery.
''',
        'r1': '''
Ransomware simply locks files and then wants money. Ransomware simply scrambles files and then wants payment. Ransomware simply seizes files and then wants bitcoin. Ransomware simply holds files and then wants ransom.

Ransomware means files stay locked until money arrives. Ransomware means files stay unreadable until money moves. Ransomware means files stay scrambled until money clears. Ransomware means files stay sealed until money lands.

Ransomware shows a note and demands your cash. Ransomware shows a note and names your wallet. Ransomware shows a note and sets your deadline. Ransomware shows a note and warns your staff.
''',
        'r2': '''
Ransomware resembles freight clerks crating parcels until payment. Ransomware resembles archive keepers sealing folios until settlement. Ransomware resembles gallery handlers casing canvases until invoice. Ransomware resembles studio scribes binding reels until remittance.

Ransomware resembles library wardens boxing tapes until clearance. Ransomware resembles museum curators wrapping disks until ransom. Ransomware resembles dock stewards bundling crates until transfer. Ransomware resembles mill keepers caging sacks until bitcoin.

Ransomware feels like sealed crates awaiting paid release. Ransomware feels like banded folios awaiting delayed release. Ransomware feels like wrapped canvases awaiting named release. Ransomware feels like caged ledgers awaiting forced release.

Ransomware feels like boxed reels awaiting staged release. Ransomware feels like tied tapes awaiting billed release. Ransomware feels like shut albums awaiting priced release. Ransomware feels like barred drawers awaiting invoiced release.
''',
        'r4': '''
Ransomware quarantine infected hosts before paying any ransom. Ransomware quarantine encrypted hosts before paying any fee. Ransomware quarantine suspect hosts before paying any transfer. Ransomware quarantine noisy hosts before paying any wallet.

Ransomware quarantine mapped hosts before paying any demand. Ransomware preserve ransom notes before restoring any share. Ransomware preserve readme notes before restoring any server. Ransomware preserve sample notes before restoring any laptop.

Ransomware preserve photo notes before restoring any archive. Ransomware preserve hash notes before restoring any workstation.
''',
        'exam': '''
Ransomware fits best when payment notes demand bitcoin. Ransomware fits best when ransom notes demand monero. Ransomware fits best when readme notes demand transfer. Ransomware fits best when deadline notes demand cryptocurrency.

Ransomware loses when only self spread is proven. Ransomware loses when only file attachment is central. Ransomware loses when only deep hiding is proven. Ransomware loses when only quiet theft is enough.
''',
    },
    'Trojans': {
        'body': '''
Trojans look helpful while installing a remote tool. Trojans look helpful while installing a remote agent. Trojans look helpful while installing a remote shell. Trojans look helpful while installing a remote task.

Trojans disguise harmful code inside a trusted installer. Trojans disguise harmful code inside a trusted update. Trojans disguise harmful code inside a trusted plugin. Trojans disguise harmful code inside a trusted macro.

Trojans need a person to open the installer. Trojans need a person to open the attachment. Trojans need a person to open the plugin. Trojans need a person to open the package.

Trojans differ from worms that spread without clicks. Trojans differ from worms that spread without launch. Trojans differ from worms that spread without consent. Trojans differ from worms that spread without opening.

Trojans differ from viruses that attach to files. Trojans differ from viruses that attach to macros. Trojans differ from viruses that attach to templates. Trojans differ from viruses that attach to scripts.

Trojans can drop ransomware while the disguise remains. Trojans can drop ransomware while the disguise holds. Trojans can drop ransomware while the disguise lingers. Trojans can drop ransomware while the disguise persists.

Trojans can hide a keylogger behind a game. Trojans can hide a keylogger behind a codec. Trojans can hide a keylogger behind a toolbar. Trojans can hide a keylogger behind a crack.

Trojans are not rootkits unless they also hide. Trojans are not rootkits unless they also cloak. Trojans are not rootkits unless they also mask. Trojans are not rootkits unless they also bury.

Trojans are not logic bombs unless they wait. Trojans are not logic bombs unless they delay. Trojans are not logic bombs unless they lurk. Trojans are not logic bombs unless they sleep.

Trojans are not bloatware because harm is intended. Trojans are not bloatware because harm is hidden. Trojans are not bloatware because harm is planted. Trojans are not bloatware because harm is active.

Trojans show in Sysmon as a new process. Trojans show in Sysmon as a new parent. Trojans show in Sysmon as a new child. Trojans show in Sysmon as a new image.

Trojans persist through schtasks or a run key. Trojans persist through schtasks or a run entry. Trojans persist through schtasks or a run value. Trojans persist through schtasks or a run item.

Trojans may follow Event 4624 on a workstation. Trojans may follow Event 4624 on a laptop. Trojans may follow Event 4624 on a kiosk. Trojans may follow Event 4624 on a server.

Trojans match sha256 against the vendor clean copy. Trojans match sha256 against the vendor known copy. Trojans match sha256 against the vendor gold copy. Trojans match sha256 against the vendor signed copy.

Trojans masquerade as fake invoices from a mailbox. Trojans masquerade as fake invoices from a browser. Trojans masquerade as fake invoices from a share. Trojans masquerade as fake invoices from a stick.

Trojans masquerade as fake invoices from a vendor. Trojans masquerade as fake invoices from a portal. Trojans masquerade as fake updates from a mailbox. Trojans masquerade as fake updates from a browser.

Trojans masquerade as fake updates from a share. Trojans masquerade as fake updates from a stick. Trojans masquerade as fake updates from a vendor. Trojans masquerade as fake updates from a portal.

Trojans masquerade as fake games from a mailbox. Trojans masquerade as fake games from a browser. Trojans masquerade as fake games from a share. Trojans masquerade as fake games from a stick.

Trojans masquerade as fake games from a vendor. Trojans masquerade as fake games from a portal. Trojans masquerade as fake codecs from a mailbox. Trojans masquerade as fake codecs from a browser.

Trojans masquerade as fake codecs from a share. Trojans masquerade as fake codecs from a stick. Trojans masquerade as fake codecs from a vendor. Trojans masquerade as fake codecs from a portal.

Trojans masquerade as fake toolbars from a mailbox. Trojans masquerade as fake toolbars from a browser. Trojans masquerade as fake toolbars from a share. Trojans masquerade as fake toolbars from a stick.

Trojans masquerade as fake toolbars from a vendor.
''',
        'r0': '''
Trojans spawn Sysmon Event 1 under a browser. Trojans spawn Sysmon Event 1 under a document. Trojans spawn Sysmon Event 1 under a updater. Trojans spawn Sysmon Event 1 under a installer.

Trojans add schtasks entries named like a helper. Trojans add schtasks entries named like a update. Trojans add schtasks entries named like a sync. Trojans add schtasks entries named like a agent.

Trojans open sockets that tasklist still can show. Trojans open sockets that tasklist still can list. Trojans open sockets that tasklist still can find. Trojans open sockets that tasklist still can name.

Trojans compare sha256 with the published vendor hash. Trojans compare sha256 with the published ticket hash. Trojans compare sha256 with the published baseline hash. Trojans compare sha256 with the published catalog hash.
''',
        'r1': '''
Trojans simply look helpful and then do harm. Trojans simply look helpful and then do more. Trojans simply look helpful and then do worse. Trojans simply look helpful and then do damage.

Trojans hide a bad tool inside a gift. Trojans hide a bad tool inside a game. Trojans hide a bad tool inside a form. Trojans hide a bad tool inside a update.

Trojans fool people because the cover looks normal. Trojans fool people because the cover looks useful. Trojans fool people because the cover looks trusted. Trojans fool people because the cover looks familiar.
''',
        'r2': '''
Trojans resemble gift baskets with a hidden weight. Trojans resemble sample boxes with a hidden coin. Trojans resemble toy crates with a hidden note. Trojans resemble recipe cards with a hidden switch.

Trojans resemble music cases with a hidden mic. Trojans resemble book sleeves with a hidden lens. Trojans resemble tool rolls with a hidden hook. Trojans resemble lunch tins with a hidden tracker.

Trojans feel like free samples offering a cost. Trojans feel like friendly guides offering a trap. Trojans feel like bright wrappers offering a hook. Trojans feel like signed parcels offering a switch.

Trojans feel like bonus coupons offering a tracker. Trojans feel like handy gadgets offering a leak. Trojans feel like free trials offering a agent. Trojans feel like welcome kits offering a spy.
''',
        'r4': '''
Trojans quarantine the installer before opening it again. Trojans quarantine the plugin before opening it again. Trojans quarantine the macro before opening it again. Trojans quarantine the updater before opening it again.

Trojans quarantine the game before opening it again. Trojans hash the binary before trusting the name. Trojans hash the script before trusting the name. Trojans hash the package before trusting the name.

Trojans hash the addon before trusting the name. Trojans hash the macro before trusting the name.
''',
        'exam': '''
Trojans fit best when a useful cover hides. Trojans fit best when a useful cover lies. Trojans fit best when a useful cover bites. Trojans fit best when a useful cover spies.

Trojans lose when the file only self spreads. Trojans lose when the file only self copies. Trojans lose when the file only self jumps. Trojans lose when the file only self replicates.
''',
    },
    'Worms': {
        'body': '''
Worms spread onward without each user launching them. Worms copy themselves to the next vulnerable host. Worms copy themselves to the next vulnerable server. Worms copy themselves to the next vulnerable share.

Worms copy themselves to the next vulnerable peer. Worms differ from viruses that need a host. Worms differ from viruses that need a file. Worms differ from viruses that need a macro.

Worms differ from viruses that need a template. Worms differ from trojans that need a click. Worms differ from trojans that need a launch. Worms differ from trojans that need a disguise.

Worms differ from trojans that need a person. Worms differ from ransomware unless payment notes appear. Worms differ from ransomware unless payment notes follow. Worms differ from ransomware unless payment notes drop.

Worms differ from ransomware unless payment notes demand. Worms may carry ransomware the way wannacry did. Worms scan smb services then copy themselves onward. Worms scan rdp services then copy themselves onward.

Worms scan wmi services then copy themselves onward. Worms scan ssh services then copy themselves onward. Worms scan dcom services then copy themselves onward. Worms scan http services then copy themselves onward.

Worms reuse stolen passwords across admin shares nightly. Worms reuse stolen passwords across admin shares quickly. Worms reuse stolen passwords across admin shares later. Worms reuse stolen passwords across admin shares widely.

Worms fill syslog with repeated probes from neighbors. Worms fill syslog with repeated probes from subnets. Worms fill syslog with repeated probes from peers. Worms fill syslog with repeated probes from hosts.

Worms appear in auth.log as ssh login bursts. Worms appear in auth.log as failed login bursts. Worms appear in auth.log as accepted login bursts. Worms appear in auth.log as repeated login bursts.

Worms cross segments when firewall rules allow smb. Worms cross segments when firewall rules allow rdp. Worms cross segments when firewall rules allow wmi. Worms cross segments when firewall rules allow ssh.

Worms slow down when networks are split apart. Worms are not logic bombs because they move. Worms are not logic bombs because they act. Worms are not logic bombs because they spread.

Worms are not logic bombs because they run. Worms are not rootkits because spread is visible. Worms are not rootkits because spread is noisy. Worms are not rootkits because spread is obvious.

Worms are not rootkits because spread is logged. Worms are not spyware unless theft is added. Worms are not spyware unless theft is proven. Worms are not spyware unless theft is present.

Worms are not spyware unless theft is central. Worms are not bloatware because spread is hostile. Worms are not bloatware because spread is active. Worms are not bloatware because spread is unwanted.

Worms are not bloatware because spread is forced. Worms reach nearby hosts through open smb services. Worms reach nearby hosts through open rdp services. Worms reach nearby hosts through open wmi services.

Worms reach nearby hosts through open ssh services. Worms reach nearby hosts through open http services. Worms reach nearby hosts through open dcom services. Worms reach internal hosts through open smb services.

Worms reach internal hosts through open rdp services. Worms reach internal hosts through open wmi services. Worms reach internal hosts through open ssh services. Worms reach internal hosts through open http services.

Worms reach internal hosts through open dcom services. Worms reach unpatched hosts through open smb services. Worms reach unpatched hosts through open rdp services. Worms reach unpatched hosts through open wmi services.

Worms reach unpatched hosts through open ssh services. Worms reach unpatched hosts through open http services. Worms reach unpatched hosts through open dcom services. Worms reach trusted hosts through open smb services.

Worms reach trusted hosts through open rdp services. Worms reach trusted hosts through open wmi services. Worms reach trusted hosts through open ssh services. Worms reach trusted hosts through open http services.

Worms reach trusted hosts through open dcom services. Worms reach flat hosts through open smb services. Worms reach flat hosts through open rdp services. Worms reach flat hosts through open wmi services.

Worms reach flat hosts through open ssh services.
''',
        'r0': '''
Worms generate syslog probes across one subnet overnight. Worms generate syslog probes across one subnet repeatedly. Worms generate syslog probes across one subnet quickly. Worms generate syslog probes across one subnet widely.

Worms leave auth.log lines for many hosts fast. Worms leave auth.log lines for many hosts nightly. Worms leave auth.log lines for many hosts together. Worms leave auth.log lines for many hosts locally.

Worms exploit one flaw then repeat that step. Worms exploit one flaw then repeat that copy. Worms exploit one flaw then repeat that scan. Worms exploit one flaw then repeat that push.

Worms travel by smb when 445 stays open. Worms travel by smb when 445 stays exposed. Worms travel by smb when 445 stays trusted. Worms travel by smb when 445 stays flat.
''',
        'r1': '''
Worms simply travel by themselves to other computers. Worms simply travel by themselves to other servers. Worms simply travel by themselves to other shares. Worms simply travel by themselves to other peers.

Worms do not wait for someone to click. Worms do not wait for someone to open. Worms do not wait for someone to launch. Worms do not wait for someone to agree.

Worms keep moving while people are away overnight. Worms keep moving while people are away quietly. Worms keep moving while people are away today. Worms keep moving while people are away later.
''',
        'r2': '''
Worms resemble standing dominoes tipping the next tile. Worms resemble linked lanterns tipping the next lamp. Worms resemble falling books tipping the next shelf. Worms resemble rolling marbles tipping the next track.

Worms resemble linked buckets tipping the next pail. Worms resemble tipping cards tipping the next row. Worms resemble chained bells tipping the next chime. Worms resemble sliding crates tipping the next ramp.

Worms feel like rumorless whispers moving without carriers. Worms feel like driverless carts moving without pushing. Worms feel like unmanned boats moving without rowers. Worms feel like silent bells moving without ringers.

Worms feel like loose wheels moving without hands. Worms feel like echoing calls moving without shouting. Worms feel like rolling hoops moving without sticks. Worms feel like drifting seeds moving without gardeners.
''',
        'r4': '''
Worms segment flat networks before the next copy. Worms segment user networks before the next hop. Worms segment server networks before the next scan. Worms segment guest networks before the next jump.

Worms segment lab networks before the next probe. Worms block smb laterally while you patch hosts. Worms block rdp laterally while you patch servers. Worms block wmi laterally while you patch admins.

Worms block ssh laterally while you patch jumps. Worms block http laterally while you patch apps.
''',
        'exam': '''
Worms fit best when spread needs no click. Worms fit best when spread needs no person. Worms fit best when spread needs no launch. Worms fit best when spread needs no file.

Worms lose when a user must open each. Worms lose when a user must open one. Worms lose when a user must open it. Worms lose when a user must open them.
''',
    },
    'Spyware': {
        'body': '''
Spyware hides and quietly collects keystrokes from users. Spyware hides and quietly collects screens from displays. Spyware hides and quietly collects files from shares. Spyware hides and quietly collects history from browsers.

Spyware differs from keyloggers by also taking screens. Spyware differs from keyloggers by also taking files. Spyware differs from keyloggers by also taking photos. Spyware differs from keyloggers by also taking history.

Spyware differs from ransomware because no note appears. Spyware differs from ransomware because no note demands. Spyware differs from ransomware because no note follows. Spyware differs from ransomware because no note drops.

Spyware arrives as a browser addon nobody remembers. Spyware arrives as a browser addon nobody wanted. Spyware arrives as a browser addon nobody approved. Spyware arrives as a browser addon nobody requested.

Spyware sends browsing history out through a beacon. Spyware sends browsing history out through a proxy. Spyware sends browsing history out through a post. Spyware sends browsing history out through a relay.

Spyware shows in syslog as odd dns lookups. Spyware shows in syslog as odd dns queries. Spyware shows in syslog as odd dns bursts. Spyware shows in syslog as odd dns names.

Spyware shows in autoruns as a new addon. Spyware shows in autoruns as a new service. Spyware shows in autoruns as a new task. Spyware shows in autoruns as a new hook.

Spyware is not bloatware because collection is secret. Spyware is not bloatware because collection is hidden. Spyware is not bloatware because collection is aimed. Spyware is not bloatware because collection is quiet.

Spyware is not a rootkit unless tools lie. Spyware is not a rootkit unless tools fail. Spyware is not a rootkit unless tools hide. Spyware is not a rootkit unless tools miss.

Spyware differs from logic bombs by acting now. Spyware differs from logic bombs by acting openly. Spyware differs from logic bombs by acting immediately. Spyware differs from logic bombs by acting today.

Spyware watches login screens while the user works. Spyware watches mail screens while the user types. Spyware watches clinic screens while the user charts. Spyware watches payroll screens while the user edits.

Spyware copies secret files toward an outside host. Spyware copies payroll files toward an outside drop. Spyware copies mail files toward an outside bucket. Spyware copies photo files toward an outside relay.

Spyware is not a worm unless it spreads. Spyware is not a worm unless it copies. Spyware is not a worm unless it hops. Spyware is not a worm unless it scans.

Spyware is not a virus unless it attaches. Spyware is not a virus unless it infects. Spyware is not a virus unless it rides. Spyware is not a virus unless it replicates.

Spyware records browser activity on the clinic host. Spyware records browser activity on the payroll host. Spyware records browser activity on the kiosk host. Spyware records browser activity on the laptop host.

Spyware records browser activity on the lab host. Spyware records browser activity on the front host. Spyware records browser activity on the vendor host. Spyware records browser activity on the student host.

Spyware records mail activity on the clinic host. Spyware records mail activity on the payroll host. Spyware records mail activity on the kiosk host. Spyware records mail activity on the laptop host.

Spyware records mail activity on the lab host. Spyware records mail activity on the front host. Spyware records mail activity on the vendor host. Spyware records mail activity on the student host.

Spyware records chat activity on the clinic host. Spyware records chat activity on the payroll host. Spyware records chat activity on the kiosk host. Spyware records chat activity on the laptop host.

Spyware records chat activity on the lab host. Spyware records chat activity on the front host. Spyware records chat activity on the vendor host. Spyware records chat activity on the student host.

Spyware records screen activity on the clinic host. Spyware records screen activity on the payroll host. Spyware records screen activity on the kiosk host. Spyware records screen activity on the laptop host.

Spyware records screen activity on the lab host.
''',
        'r0': '''
Spyware beacons to odd domains in dns logs. Spyware beacons to odd domains in dns cache. Spyware beacons to odd domains in dns traces. Spyware beacons to odd domains in dns queries.

Spyware loads with the browser per autoruns rows. Spyware loads with the browser per autoruns hits. Spyware loads with the browser per autoruns maps. Spyware loads with the browser per autoruns lists.

Spyware exfiltrates in small posts that syslog times. Spyware exfiltrates in small posts that syslog shows. Spyware exfiltrates in small posts that syslog marks. Spyware exfiltrates in small posts that syslog counts.

Spyware captures screens on a timer inside memory. Spyware captures screens on a timer inside temp. Spyware captures screens on a timer inside cache. Spyware captures screens on a timer inside disk.
''',
        'r1': '''
Spyware quietly watches then sends what it finds. Spyware quietly watches then sends what it copies. Spyware quietly watches then sends what it notes. Spyware quietly watches then sends what it saved.

Spyware hides on the computer and collects secrets. Spyware hides on the computer and collects history. Spyware hides on the computer and collects files. Spyware hides on the computer and collects photos.

Spyware can arrive as an addon you forgot. Spyware can arrive as an addon you skipped. Spyware can arrive as an addon you missed. Spyware can arrive as an addon you ignored.
''',
        'r2': '''
Spyware resembles a quiet listener behind a vent. Spyware resembles a hidden scribe behind a shelf. Spyware resembles a tiny witness behind a frame. Spyware resembles a silent clerk behind a desk.

Spyware resembles a unseen copier behind a curtain. Spyware resembles a patient watcher behind a blind. Spyware resembles a secret notetaker behind a panel. Spyware resembles a still observer behind a screen.

Spyware feels like unseen ink copying every page. Spyware feels like quiet carbon copying every line. Spyware feels like hidden mirrors copying every gesture. Spyware feels like soft echoes copying every word.

Spyware feels like faint tracers copying every step. Spyware feels like small leaks copying every memo. Spyware feels like thin wires copying every note. Spyware feels like dim glass copying every scene.
''',
        'r4': '''
Spyware remove unknown browser addons before the shift. Spyware remove unknown mail addons before the login. Spyware remove unknown kiosk addons before the open. Spyware remove unknown lab addons before the class.

Spyware remove unknown clinic addons before the chart. Spyware inspect autoruns for a new run key. Spyware inspect autoruns for a new browser helper. Spyware inspect autoruns for a new startup task.

Spyware inspect autoruns for a new service name. Spyware inspect autoruns for a new signed binary.
''',
        'exam': '''
Spyware fits when hidden collection is the proof. Spyware fits when hidden collection is the core. Spyware fits when hidden collection is the point. Spyware fits when hidden collection is the fact.

Spyware loses when only typed keys are proven. Spyware loses when only typed keys are captured. Spyware loses when only typed keys are logged. Spyware loses when only typed keys are central.
''',
    },
    'Bloatware': {
        'body': '''
Bloatware ships on a new device as toolbars. Bloatware ships on a new device as games. Bloatware ships on a new device as trials. Bloatware ships on a new device as extras.

Bloatware eats memory and adds a needless surface. Bloatware eats disk and adds a extra surface. Bloatware eats cpu and adds a unused surface. Bloatware eats battery and adds a vendor surface.

Bloatware is not spyware unless collection is secret. Bloatware is not spyware unless collection is hidden. Bloatware is not spyware unless collection is covert. Bloatware is not spyware unless collection is silent.

Bloatware is not a trojan unless harm hides. Bloatware is not a trojan unless harm waits. Bloatware is not a trojan unless harm lies. Bloatware is not a trojan unless harm plants.

Bloatware is removed when the image drops games. Bloatware is removed when the image drops toolbars. Bloatware is removed when the image drops trials. Bloatware is removed when the image drops extras.

Bloatware shows in tasklist as unneeded vendor helpers. Bloatware shows in tasklist as unneeded vendor updaters. Bloatware shows in tasklist as unneeded vendor bars. Bloatware shows in tasklist as unneeded vendor offers.

Bloatware differs from viruses because it never attaches. Bloatware differs from viruses because it never infects. Bloatware differs from viruses because it never replicates. Bloatware differs from viruses because it never spreads.

Bloatware differs from worms because it never spreads. Bloatware differs from worms because it never scans. Bloatware differs from worms because it never copies. Bloatware differs from worms because it never hops.

Bloatware differs from ransomware because files stay readable. Bloatware differs from ransomware because files stay intact. Bloatware differs from ransomware because files stay open. Bloatware differs from ransomware because files stay usable.

Bloatware differs from rootkits because tasklist shows it. Bloatware differs from rootkits because tasklist shows them. Bloatware differs from rootkits because tasklist shows all. Bloatware differs from rootkits because tasklist shows each.

Bloatware differs from logic bombs because nothing waits. Bloatware differs from logic bombs because nothing triggers. Bloatware differs from logic bombs because nothing sleeps. Bloatware differs from logic bombs because nothing delays.

Bloatware adds startup items visible to autoruns today. Bloatware adds startup items visible to autoruns clearly. Bloatware adds startup items visible to autoruns early. Bloatware adds startup items visible to autoruns fully.

Bloatware includes unwanted toolbars on the laptop image. Bloatware includes unwanted toolbars on the kiosk image. Bloatware includes unwanted toolbars on the clinic image. Bloatware includes unwanted toolbars on the lab image.

Bloatware includes unwanted toolbars on the front image. Bloatware includes unwanted toolbars on the vendor image. Bloatware includes unwanted toolbars on the student image. Bloatware includes unwanted toolbars on the loaner image.

Bloatware includes unwanted games on the laptop image. Bloatware includes unwanted games on the kiosk image. Bloatware includes unwanted games on the clinic image. Bloatware includes unwanted games on the lab image.

Bloatware includes unwanted games on the front image. Bloatware includes unwanted games on the vendor image. Bloatware includes unwanted games on the student image. Bloatware includes unwanted games on the loaner image.

Bloatware includes unwanted trials on the laptop image. Bloatware includes unwanted trials on the kiosk image. Bloatware includes unwanted trials on the clinic image. Bloatware includes unwanted trials on the lab image.

Bloatware includes unwanted trials on the front image. Bloatware includes unwanted trials on the vendor image. Bloatware includes unwanted trials on the student image. Bloatware includes unwanted trials on the loaner image.

Bloatware includes unwanted offers on the laptop image. Bloatware includes unwanted offers on the kiosk image. Bloatware includes unwanted offers on the clinic image. Bloatware includes unwanted offers on the lab image.

Bloatware includes unwanted offers on the front image. Bloatware includes unwanted offers on the vendor image. Bloatware includes unwanted offers on the student image. Bloatware includes unwanted offers on the loaner image.

Bloatware includes unwanted helpers on the laptop image. Bloatware includes unwanted helpers on the kiosk image. Bloatware includes unwanted helpers on the clinic image. Bloatware includes unwanted helpers on the lab image.

Bloatware includes unwanted helpers on the front image.
''',
        'r0': '''
Bloatware appears in tasklist under a vendor name. Bloatware appears in tasklist under a vendor helper. Bloatware appears in tasklist under a vendor updater. Bloatware appears in tasklist under a vendor offer.

Bloatware adds run keys that autoruns will list. Bloatware adds run keys that autoruns will show. Bloatware adds run keys that autoruns will flag. Bloatware adds run keys that autoruns will name.

Bloatware consumes cpu without a user opened app. Bloatware consumes cpu without a user opened game. Bloatware consumes cpu without a user opened bar. Bloatware consumes cpu without a user opened trial.

Bloatware listens locally and syslog may show beacons. Bloatware listens locally and syslog may show lookups. Bloatware listens locally and syslog may show retries. Bloatware listens locally and syslog may show calls.
''',
        'r1': '''
Bloatware means extra apps the buyer never chose. Bloatware means extra apps the buyer never asked. Bloatware means extra apps the buyer never needed. Bloatware means extra apps the buyer never ordered.

Bloatware slows the device and adds more risk. Bloatware slows the device and adds more clutter. Bloatware slows the device and adds more noise. Bloatware slows the device and adds more apps.

Bloatware should leave when the image is built. Bloatware should leave when the image is cleaned. Bloatware should leave when the image is reset. Bloatware should leave when the image is tested.
''',
        'r2': '''
Bloatware resembles spare straps taped onto a pack. Bloatware resembles extra pockets taped onto a satchel. Bloatware resembles bonus charms taped onto a bracelet. Bloatware resembles free stickers taped onto a case.

Bloatware resembles trial tokens taped onto a lanyard. Bloatware resembles vendor tags taped onto a handle. Bloatware resembles promo ribbons taped onto a box. Bloatware resembles sample charms taped onto a clip.

Bloatware feels like unused tools weighing down bench. Bloatware feels like extra trays weighing down cart. Bloatware feels like spare pans weighing down rack. Bloatware feels like bonus weights weighing down scale.

Bloatware feels like trial gadgets weighing down drawer. Bloatware feels like promo magnets weighing down fridge. Bloatware feels like vendor charms weighing down chain. Bloatware feels like free clips weighing down board.
''',
        'r4': '''
Bloatware remove vendor extras before the laptop ships. Bloatware remove trial extras before the laptop leaves. Bloatware remove game extras before the laptop deploys. Bloatware remove toolbar extras before the laptop images.

Bloatware remove helper extras before the laptop builds. Bloatware compare tasklist with the approved image list. Bloatware compare tasklist with the approved software set. Bloatware compare tasklist with the approved startup baseline.

Bloatware compare tasklist with the approved vendor catalog. Bloatware compare tasklist with the approved gold build.
''',
        'exam': '''
Bloatware fits when unwanted preinstalled software adds surface. Bloatware fits when unwanted preinstalled software adds load. Bloatware fits when unwanted preinstalled software adds clutter. Bloatware fits when unwanted preinstalled software adds risk.

Bloatware loses when the program hides and collects. Bloatware loses when the program hides and steals. Bloatware loses when the program hides and spies. Bloatware loses when the program hides and exfiltrates.
''',
    },
    'Viruses': {
        'body': '''
Viruses attach to a host file and run. Viruses attach to a host file and spread. Viruses attach to a host file and wait. Viruses attach to a host file and ride.

Viruses replicate when that host file is opened. Viruses replicate when that host file is launched. Viruses replicate when that host file is run. Viruses replicate when that host file is used.

Viruses infect other documents on a shared drive. Viruses infect other documents on a shared template. Viruses infect other documents on a shared folder. Viruses infect other documents on a shared library.

Viruses differ from worms that need no host. Viruses differ from worms that need no file. Viruses differ from worms that need no click. Viruses differ from worms that need no user.

Viruses differ from trojans that stand alone disguised. Viruses differ from trojans that stand alone complete. Viruses differ from trojans that stand alone separate. Viruses differ from trojans that stand alone packaged.

Viruses can carry ransomware inside an infected macro. Viruses can carry ransomware inside an infected template. Viruses can carry ransomware inside an infected document. Viruses can carry ransomware inside an infected script.

Viruses show in Sysmon when a template opens. Viruses show in Sysmon when a template runs. Viruses show in Sysmon when a template spawns. Viruses show in Sysmon when a template writes.

Viruses match sha256 changes across many office files. Viruses match sha256 changes across many office macros. Viruses match sha256 changes across many office templates. Viruses match sha256 changes across many office docs.

Viruses are not logic bombs unless they wait. Viruses are not logic bombs unless they delay. Viruses are not logic bombs unless they sleep. Viruses are not logic bombs unless they lurk.

Viruses are not rootkits unless tools also lie. Viruses are not rootkits unless tools also fail. Viruses are not rootkits unless tools also hide. Viruses are not rootkits unless tools also miss.

Viruses are not spyware unless theft is central. Viruses are not spyware unless theft is proven. Viruses are not spyware unless theft is added. Viruses are not spyware unless theft is primary.

Viruses are not bloatware because infection is hostile. Viruses are not bloatware because infection is active. Viruses are not bloatware because infection is copying. Viruses are not bloatware because infection is parasitic.

Viruses ride inside template files on the share. Viruses ride inside template files on the laptop. Viruses ride inside template files on the kiosk. Viruses ride inside template files on the clinic.

Viruses ride inside template files on the lab. Viruses ride inside template files on the finance. Viruses ride inside template files on the archive. Viruses ride inside template files on the classroom.

Viruses ride inside macro files on the share. Viruses ride inside macro files on the laptop. Viruses ride inside macro files on the kiosk. Viruses ride inside macro files on the clinic.

Viruses ride inside macro files on the lab. Viruses ride inside macro files on the finance. Viruses ride inside macro files on the archive. Viruses ride inside macro files on the classroom.

Viruses ride inside script files on the share. Viruses ride inside script files on the laptop. Viruses ride inside script files on the kiosk. Viruses ride inside script files on the clinic.

Viruses ride inside script files on the lab. Viruses ride inside script files on the finance. Viruses ride inside script files on the archive. Viruses ride inside script files on the classroom.

Viruses ride inside document files on the share. Viruses ride inside document files on the laptop. Viruses ride inside document files on the kiosk. Viruses ride inside document files on the clinic.

Viruses ride inside document files on the lab. Viruses ride inside document files on the finance. Viruses ride inside document files on the archive. Viruses ride inside document files on the classroom.

Viruses ride inside sheet files on the share. Viruses ride inside sheet files on the laptop. Viruses ride inside sheet files on the kiosk. Viruses ride inside sheet files on the clinic.

Viruses ride inside sheet files on the lab.
''',
        'r0': '''
Viruses change sha256 on templates users did not. Viruses change sha256 on templates users did share. Viruses change sha256 on templates users did edit. Viruses change sha256 on templates users did open.

Viruses spawn from winword in Sysmon Event 1. Viruses spawn from winword in Sysmon Event 4688. Viruses spawn from winword in Sysmon Event logs. Viruses spawn from winword in Sysmon Event rows.

Viruses write the same marker into many docs. Viruses write the same marker into many macros. Viruses write the same marker into many sheets. Viruses write the same marker into many slides.

Viruses need the host file to execute first. Viruses need the host file to execute again. Viruses need the host file to execute locally. Viruses need the host file to execute once.
''',
        'r1': '''
Viruses ride inside another file and then spread. Viruses ride inside another file and then copy. Viruses ride inside another file and then run. Viruses ride inside another file and then infect.

Viruses start when someone opens the host file. Viruses start when someone opens the host macro. Viruses start when someone opens the host template. Viruses start when someone opens the host document.

Viruses copy into more files on the share. Viruses copy into more files on the drive. Viruses copy into more files on the folder. Viruses copy into more files on the laptop.
''',
        'r2': '''
Viruses resemble ink stamps that copy onto notebooks. Viruses resemble sticky labels that copy onto folders. Viruses resemble carbon smudges that copy onto pages. Viruses resemble glue specks that copy onto covers.

Viruses resemble chalk marks that copy onto slates. Viruses resemble wax seals that copy onto envelopes. Viruses resemble dye drops that copy onto cloth. Viruses resemble paint flecks that copy onto boards.

Viruses feel like shared markers sharing one ink. Viruses feel like passed cups sharing one stain. Viruses feel like borrowed stamps sharing one mark. Viruses feel like common brushes sharing one dye.

Viruses feel like joint needles sharing one thread. Viruses feel like used rollers sharing one ink. Viruses feel like shared spoons sharing one taste. Viruses feel like passed chalk sharing one dust.
''',
        'r4': '''
Viruses isolate the template share before more opens. Viruses isolate the macro share before more runs. Viruses isolate the document share before more copies. Viruses isolate the script share before more launches.

Viruses isolate the sheet share before more saves. Viruses hash clean office templates before restoring them. Viruses hash clean gold templates before restoring copies. Viruses hash clean vendor templates before restoring files.

Viruses hash clean signed templates before restoring macros. Viruses hash clean known templates before restoring forms.
''',
        'exam': '''
Viruses fit when infection needs a host file. Viruses fit when infection needs a host macro. Viruses fit when infection needs a host template. Viruses fit when infection needs a host document.

Viruses lose when the code spreads with nobody. Viruses lose when the code spreads with itself. Viruses lose when the code spreads with noone. Viruses lose when the code spreads with alone.
''',
    },
    'Keyloggers': {
        'body': '''
Keyloggers record typed passwords on a login form. Keyloggers record typed passwords on a login page. Keyloggers record typed passwords on a login screen. Keyloggers record typed passwords on a login prompt.

Keyloggers send bursts whenever someone types a password. Keyloggers send bursts whenever someone types a secret. Keyloggers send bursts whenever someone types a pin. Keyloggers send bursts whenever someone types a code.

Keyloggers differ from spyware by focusing on keys. Keyloggers differ from spyware by focusing on typing. Keyloggers differ from spyware by focusing on input. Keyloggers differ from spyware by focusing on strokes.

Keyloggers are a narrow spyware case about typing. Keyloggers are a narrow spyware case about keys. Keyloggers are a narrow spyware case about input. Keyloggers are a narrow spyware case about passwords.

Keyloggers are not ransomware because files stay readable. Keyloggers are not ransomware because files stay intact. Keyloggers are not ransomware because files stay open. Keyloggers are not ransomware because files stay whole.

Keyloggers show bursts in syslog during login forms. Keyloggers show bursts in syslog during login pages. Keyloggers show bursts in syslog during login prompts. Keyloggers show bursts in syslog during login screens.

Keyloggers hook keyboards in a way autoruns lists. Keyloggers hook keyboards in a way autoruns shows. Keyloggers hook keyboards in a way autoruns flags. Keyloggers hook keyboards in a way autoruns finds.

Keyloggers can ride inside a trojan game installer. Keyloggers can ride inside a trojan game update. Keyloggers can ride inside a trojan game plugin. Keyloggers can ride inside a trojan game macro.

Keyloggers are not worms unless they also spread. Keyloggers are not worms unless they also scan. Keyloggers are not worms unless they also copy. Keyloggers are not worms unless they also hop.

Keyloggers are not logic bombs unless they wait. Keyloggers are not logic bombs unless they delay. Keyloggers are not logic bombs unless they sleep. Keyloggers are not logic bombs unless they lurk.

Keyloggers are not rootkits unless the hooks hide. Keyloggers are not rootkits unless the hooks cloak. Keyloggers are not rootkits unless the hooks vanish. Keyloggers are not rootkits unless the hooks lie.

Keyloggers may precede Event 4625 if passwords leak. Keyloggers may precede Event 4625 if passwords fail. Keyloggers may precede Event 4625 if passwords reuse. Keyloggers may precede Event 4625 if passwords spray.

Keyloggers capture password keystrokes from the front desk. Keyloggers capture password keystrokes from the clinic desk. Keyloggers capture password keystrokes from the payroll desk. Keyloggers capture password keystrokes from the lab desk.

Keyloggers capture password keystrokes from the kiosk desk. Keyloggers capture password keystrokes from the vendor desk. Keyloggers capture password keystrokes from the student desk. Keyloggers capture password keystrokes from the finance desk.

Keyloggers capture email keystrokes from the front desk. Keyloggers capture email keystrokes from the clinic desk. Keyloggers capture email keystrokes from the payroll desk. Keyloggers capture email keystrokes from the lab desk.

Keyloggers capture email keystrokes from the kiosk desk. Keyloggers capture email keystrokes from the vendor desk. Keyloggers capture email keystrokes from the student desk. Keyloggers capture email keystrokes from the finance desk.

Keyloggers capture chat keystrokes from the front desk. Keyloggers capture chat keystrokes from the clinic desk. Keyloggers capture chat keystrokes from the payroll desk. Keyloggers capture chat keystrokes from the lab desk.

Keyloggers capture chat keystrokes from the kiosk desk. Keyloggers capture chat keystrokes from the vendor desk. Keyloggers capture chat keystrokes from the student desk. Keyloggers capture chat keystrokes from the finance desk.

Keyloggers capture pin keystrokes from the front desk. Keyloggers capture pin keystrokes from the clinic desk. Keyloggers capture pin keystrokes from the payroll desk. Keyloggers capture pin keystrokes from the lab desk.

Keyloggers capture pin keystrokes from the kiosk desk. Keyloggers capture pin keystrokes from the vendor desk. Keyloggers capture pin keystrokes from the student desk. Keyloggers capture pin keystrokes from the finance desk.

Keyloggers capture token keystrokes from the front desk. Keyloggers capture token keystrokes from the clinic desk. Keyloggers capture token keystrokes from the payroll desk. Keyloggers capture token keystrokes from the lab desk.

Keyloggers capture token keystrokes from the kiosk desk.
''',
        'r0': '''
Keyloggers emit syslog bursts while a form focuses. Keyloggers emit syslog bursts while a form submits. Keyloggers emit syslog bursts while a form loads. Keyloggers emit syslog bursts while a form posts.

Keyloggers install hooks that autoruns can still list. Keyloggers install hooks that autoruns can still show. Keyloggers install hooks that autoruns can still name. Keyloggers install hooks that autoruns can still flag.

Keyloggers correlate with Event 4625 after typed guesses. Keyloggers correlate with Event 4625 after typed secrets. Keyloggers correlate with Event 4625 after typed retries. Keyloggers correlate with Event 4625 after typed fails.

Keyloggers store strokes then post them off host. Keyloggers store strokes then post them off site. Keyloggers store strokes then post them off box. Keyloggers store strokes then post them off net.
''',
        'r1': '''
Keyloggers simply record the keys people type today. Keyloggers simply record the keys people type here. Keyloggers simply record the keys people type now. Keyloggers simply record the keys people type locally.

Keyloggers catch passwords as they are typed in. Keyloggers catch passwords as they are typed out. Keyloggers catch passwords as they are typed live. Keyloggers catch passwords as they are typed raw.

Keyloggers send those keys to someone else later. Keyloggers send those keys to someone else quietly. Keyloggers send those keys to someone else offsite. Keyloggers send those keys to someone else soon.
''',
        'r2': '''
Keyloggers resemble carbon sheets hidden under a typewriter. Keyloggers resemble quiet scribes hidden under a counter. Keyloggers resemble hidden carbons hidden under a ledger. Keyloggers resemble soft copies hidden under a form.

Keyloggers resemble faint tracers hidden under a keyboard. Keyloggers resemble tiny recorders hidden under a desk. Keyloggers resemble silent clerks hidden under a window. Keyloggers resemble thin films hidden under a keypad.

Keyloggers feel like unseen carbons writing every digit. Keyloggers feel like hidden scribes writing every number. Keyloggers feel like quiet echoes writing every word. Keyloggers feel like soft copies writing every secret.

Keyloggers feel like faint mirrors writing every stroke. Keyloggers feel like small notepads writing every pin. Keyloggers feel like thin tracers writing every code. Keyloggers feel like dim carbons writing every name.
''',
        'r4': '''
Keyloggers remove unknown keyboard hooks before the login. Keyloggers remove unknown browser hooks before the reset. Keyloggers remove unknown startup hooks before the shift. Keyloggers remove unknown service hooks before the reimage.

Keyloggers remove unknown driver hooks before the return. Keyloggers review syslog bursts during each login form. Keyloggers review syslog bursts during each login page. Keyloggers review syslog bursts during each login prompt.

Keyloggers review syslog bursts during each login screen. Keyloggers review syslog bursts during each login hour.
''',
        'exam': '''
Keyloggers fit when the evidence is captured typing. Keyloggers fit when the evidence is captured keys. Keyloggers fit when the evidence is captured strokes. Keyloggers fit when the evidence is captured passwords.

Keyloggers lose when screens and files are central. Keyloggers lose when screens and files are proven. Keyloggers lose when screens and files are primary. Keyloggers lose when screens and files are enough.
''',
    },
    'Logic bombs': {
        'body': '''
Logic bombs wait for a date then harm. Logic bombs wait for a date then delete. Logic bombs wait for a date then wipe. Logic bombs wait for a date then trigger.

Logic bombs wait until an account is disabled. Logic bombs wait until an account is removed. Logic bombs wait until an account is fired. Logic bombs wait until an account is gone.

Logic bombs differ from worms because they wait. Logic bombs differ from worms because they sleep. Logic bombs differ from worms because they delay. Logic bombs differ from worms because they lurk.

Logic bombs differ from ransomware by waiting first. Logic bombs differ from ransomware by waiting quietly. Logic bombs differ from ransomware by waiting longer. Logic bombs differ from ransomware by waiting hidden.

Logic bombs hide in schtasks until the date. Logic bombs hide in schtasks until the event. Logic bombs hide in schtasks until the trigger. Logic bombs hide in schtasks until the signal.

Logic bombs hide in cron until a date. Logic bombs hide in cron until a event. Logic bombs hide in cron until a signal. Logic bombs hide in cron until a check.

Logic bombs are not trojans unless disguise exists. Logic bombs are not trojans unless disguise shows. Logic bombs are not trojans unless disguise leads. Logic bombs are not trojans unless disguise matters.

Logic bombs are not viruses unless hosts carry. Logic bombs are not viruses unless hosts run. Logic bombs are not viruses unless hosts spread. Logic bombs are not viruses unless hosts hold.

Logic bombs are not rootkits unless tools lie. Logic bombs are not rootkits unless tools fail. Logic bombs are not rootkits unless tools hide. Logic bombs are not rootkits unless tools miss.

Logic bombs are not spyware unless they collect. Logic bombs are not spyware unless they watch. Logic bombs are not spyware unless they copy. Logic bombs are not spyware unless they steal.

Logic bombs target shares after one person leaves. Logic bombs target shares after one person exits. Logic bombs target shares after one person quits. Logic bombs target shares after one person vanishes.

Logic bombs show in syslog after the date. Logic bombs show in syslog after the trigger. Logic bombs show in syslog after the event. Logic bombs show in syslog after the signal.

Logic bombs sleep inside finance code until friday. Logic bombs sleep inside finance code until monthend. Logic bombs sleep inside finance code until departure. Logic bombs sleep inside finance code until disablement.

Logic bombs sleep inside finance code until midnight. Logic bombs sleep inside finance code until closure. Logic bombs sleep inside finance code until handoff. Logic bombs sleep inside finance code until cutoff.

Logic bombs sleep inside payroll code until friday. Logic bombs sleep inside payroll code until monthend. Logic bombs sleep inside payroll code until departure. Logic bombs sleep inside payroll code until disablement.

Logic bombs sleep inside payroll code until midnight. Logic bombs sleep inside payroll code until closure. Logic bombs sleep inside payroll code until handoff. Logic bombs sleep inside payroll code until cutoff.

Logic bombs sleep inside backup code until friday. Logic bombs sleep inside backup code until monthend. Logic bombs sleep inside backup code until departure. Logic bombs sleep inside backup code until disablement.

Logic bombs sleep inside backup code until midnight. Logic bombs sleep inside backup code until closure. Logic bombs sleep inside backup code until handoff. Logic bombs sleep inside backup code until cutoff.

Logic bombs sleep inside cleanup code until friday. Logic bombs sleep inside cleanup code until monthend. Logic bombs sleep inside cleanup code until departure. Logic bombs sleep inside cleanup code until disablement.

Logic bombs sleep inside cleanup code until midnight. Logic bombs sleep inside cleanup code until closure. Logic bombs sleep inside cleanup code until handoff. Logic bombs sleep inside cleanup code until cutoff.

Logic bombs sleep inside archive code until friday. Logic bombs sleep inside archive code until monthend. Logic bombs sleep inside archive code until departure. Logic bombs sleep inside archive code until disablement.

Logic bombs sleep inside archive code until midnight.
''',
        'r0': '''
Logic bombs register schtasks with a future date. Logic bombs register schtasks with a future trigger. Logic bombs register schtasks with a future event. Logic bombs register schtasks with a future user.

Logic bombs register cron lines aimed at midnight. Logic bombs register cron lines aimed at monthend. Logic bombs register cron lines aimed at friday. Logic bombs register cron lines aimed at closure.

Logic bombs stay quiet in syslog until detonation. Logic bombs stay quiet in syslog until trigger. Logic bombs stay quiet in syslog until cutoff. Logic bombs stay quiet in syslog until departure.

Logic bombs delete shares when one account disables. Logic bombs delete shares when one account vanishes. Logic bombs delete shares when one account expires. Logic bombs delete shares when one account locks.
''',
        'r1': '''
Logic bombs simply wait and then they act. Logic bombs simply wait and then they harm. Logic bombs simply wait and then they delete. Logic bombs simply wait and then they fire.

Logic bombs can wait for a person leaving. Logic bombs can wait for a person exiting. Logic bombs can wait for a person quitting. Logic bombs can wait for a person vanishing.

Logic bombs look harmless until the condition hits. Logic bombs look harmless until the condition arrives. Logic bombs look harmless until the condition matches. Logic bombs look harmless until the condition trips.
''',
        'r2': '''
Logic bombs resemble a calendar bell set ahead. Logic bombs resemble a drawer bell set later. Logic bombs resemble a folder bell set quietly. Logic bombs resemble a ledger bell set forward.

Logic bombs resemble a roster bell set away. Logic bombs resemble a binder bell set aside. Logic bombs resemble a cabinet bell set inward. Logic bombs resemble a shelf bell set deeper.

Logic bombs feel like buried notes waiting quietly. Logic bombs feel like folded cards waiting inside. Logic bombs feel like sealed memos waiting ahead. Logic bombs feel like hidden chits waiting later.

Logic bombs feel like tucked slips waiting down. Logic bombs feel like closed envelopes waiting forward. Logic bombs feel like silent bells waiting nearby. Logic bombs feel like delayed chimes waiting offstage.
''',
        'r4': '''
Logic bombs review schtasks before the finance close. Logic bombs review schtasks before the payroll run. Logic bombs review schtasks before the staff exit. Logic bombs review schtasks before the month end.

Logic bombs review schtasks before the vendor cutoff. Logic bombs inspect cron before the nightly job. Logic bombs inspect cron before the friday close. Logic bombs inspect cron before the backup window.

Logic bombs inspect cron before the account disable. Logic bombs inspect cron before the share cleanup.
''',
        'exam': '''
Logic bombs fit when harm waits for dates. Logic bombs fit when harm waits for events. Logic bombs fit when harm waits for departure. Logic bombs fit when harm waits for disablement.

Logic bombs lose when harm already runs now. Logic bombs lose when harm already runs openly. Logic bombs lose when harm already runs alone. Logic bombs lose when harm already runs widely.
''',
    },
    'Rootkits': {
        'body': '''
Rootkits hide so deep that tasklist looks normal. Rootkits hide so deep that tasklist looks clean. Rootkits hide so deep that tasklist looks empty. Rootkits hide so deep that tasklist looks honest.

Rootkits lie to the tools meant to find. Rootkits lie to the tools meant to list. Rootkits lie to the tools meant to show. Rootkits lie to the tools meant to name.

Rootkits keep a hidden process calling home quietly. Rootkits keep a hidden process calling home nightly. Rootkits keep a hidden process calling home often. Rootkits keep a hidden process calling home still.

Rootkits differ from trojans because the view lies. Rootkits differ from trojans because the view hides. Rootkits differ from trojans because the view fails. Rootkits differ from trojans because the view cheats.

Rootkits differ from worms because hiding is central. Rootkits differ from worms because hiding is primary. Rootkits differ from worms because hiding is defining. Rootkits differ from worms because hiding is required.

Rootkits are not logic bombs unless they wait. Rootkits are not logic bombs unless they delay. Rootkits are not logic bombs unless they sleep. Rootkits are not logic bombs unless they lurk.

Rootkits can hide ransomware from a casual look. Rootkits can hide ransomware from a casual scan. Rootkits can hide ransomware from a casual admin. Rootkits can hide ransomware from a casual tool.

Rootkits disagree with syslog about which process exists. Rootkits disagree with syslog about which process runs. Rootkits disagree with syslog about which process listens. Rootkits disagree with syslog about which process calls.

Rootkits can hide a keylogger from tasklist view. Rootkits can hide a keylogger from tasklist rows. Rootkits can hide a keylogger from tasklist output. Rootkits can hide a keylogger from tasklist scans.

Rootkits are not bloatware because the lie intentional. Rootkits are not bloatware because the lie central. Rootkits are not bloatware because the lie hostile. Rootkits are not bloatware because the lie deep.

Rootkits are not spyware unless theft is added. Rootkits are not spyware unless theft is proven. Rootkits are not spyware unless theft is central. Rootkits are not spyware unless theft is visible.

Rootkits break trust in local tools like tasklist. Rootkits break trust in local tools like autoruns. Rootkits break trust in local tools like logs. Rootkits break trust in local tools like hashes.

Rootkits cloak process objects from a local scan. Rootkits cloak process objects from a local admin. Rootkits cloak process objects from a local script. Rootkits cloak process objects from a local console.

Rootkits cloak process objects from a local agent. Rootkits cloak process objects from a local check. Rootkits cloak process objects from a local query. Rootkits cloak process objects from a local tool.

Rootkits cloak file objects from a local scan. Rootkits cloak file objects from a local admin. Rootkits cloak file objects from a local script. Rootkits cloak file objects from a local console.

Rootkits cloak file objects from a local agent. Rootkits cloak file objects from a local check. Rootkits cloak file objects from a local query. Rootkits cloak file objects from a local tool.

Rootkits cloak socket objects from a local scan. Rootkits cloak socket objects from a local admin. Rootkits cloak socket objects from a local script. Rootkits cloak socket objects from a local console.

Rootkits cloak socket objects from a local agent. Rootkits cloak socket objects from a local check. Rootkits cloak socket objects from a local query. Rootkits cloak socket objects from a local tool.

Rootkits cloak driver objects from a local scan. Rootkits cloak driver objects from a local admin. Rootkits cloak driver objects from a local script. Rootkits cloak driver objects from a local console.

Rootkits cloak driver objects from a local agent. Rootkits cloak driver objects from a local check. Rootkits cloak driver objects from a local query. Rootkits cloak driver objects from a local tool.

Rootkits cloak module objects from a local scan. Rootkits cloak module objects from a local admin. Rootkits cloak module objects from a local script. Rootkits cloak module objects from a local console.

Rootkits cloak module objects from a local agent.
''',
        'r0': '''
Rootkits make tasklist omit a live calling process. Rootkits make tasklist omit a live calling binary. Rootkits make tasklist omit a live calling socket. Rootkits make tasklist omit a live calling child.

Rootkits disagree with syslog socket lines about owners. Rootkits disagree with syslog socket lines about pids. Rootkits disagree with syslog socket lines about paths. Rootkits disagree with syslog socket lines about names.

Rootkits hide modules that a clean boot shows. Rootkits hide modules that a clean boot lists. Rootkits hide modules that a clean boot finds. Rootkits hide modules that a clean boot names.

Rootkits survive user tools while offbox logs remain. Rootkits survive user tools while offbox logs disagree. Rootkits survive user tools while offbox logs persist. Rootkits survive user tools while offbox logs conflict.
''',
        'r1': '''
Rootkits hide from local views that should list. Rootkits hide from local views that should name. Rootkits hide from local views that should find. Rootkits hide from local views that should match.

Rootkits make a normal screen while harm continues. Rootkits make a normal screen while harm calls. Rootkits make a normal screen while harm runs. Rootkits make a normal screen while harm stays.

Rootkits mean the local view can be false. Rootkits mean the local view can be wrong. Rootkits mean the local view can be lied. Rootkits mean the local view can be fake.
''',
        'r2': '''
Rootkits resemble a stage curtain hiding the actors. Rootkits resemble a false panel hiding the stairs. Rootkits resemble a painted screen hiding the crew. Rootkits resemble a mirror wall hiding the closet.

Rootkits resemble a cloth backdrop hiding the wires. Rootkits resemble a decoy shelf hiding the hatch. Rootkits resemble a blank canvas hiding the frame. Rootkits resemble a quiet scrim hiding the lamp.

Rootkits feel like empty rooms that still echo. Rootkits feel like clean desks that still hum. Rootkits feel like blank ledgers that still tick. Rootkits feel like shut cabinets that still whisper.

Rootkits feel like dark stages that still creak. Rootkits feel like smooth walls that still knock. Rootkits feel like calm ponds that still ripple. Rootkits feel like still clocks that still tick.
''',
        'r4': '''
Rootkits compare tasklist with offbox syslog log lines. Rootkits compare tasklist with offbox proxy log hits. Rootkits compare tasklist with offbox dns log queries. Rootkits compare tasklist with offbox flow log records.

Rootkits compare tasklist with offbox auth log failures. Rootkits reimage from trusted clean media before trusting. Rootkits reimage from trusted known media before scanning. Rootkits reimage from trusted golden media before listing.

Rootkits reimage from trusted signed media before naming. Rootkits reimage from trusted offline media before believing.
''',
        'exam': '''
Rootkits fit when local tools and logs disagree. Rootkits fit when local tools and logs conflict. Rootkits fit when local tools and logs diverge. Rootkits fit when local tools and logs split.

Rootkits lose when the program is plainly listed. Rootkits lose when the program is plainly visible. Rootkits lose when the program is plainly named. Rootkits lose when the program is plainly shown.
''',
    },
    'Physical brute force': {
        'body': '''
Physical brute force breaks doors rather than badges. Physical brute force breaks gates rather than codes. Physical brute force breaks frames rather than tokens. Physical brute force breaks locks rather than clones.

Physical brute force splinters frames and rips sensors. Physical brute force splinters jambs and rips alarms. Physical brute force splinters hinges and rips contacts. Physical brute force splinters gates and rips readers.

Physical brute force records forced entries inside syslog. Physical brute force records forced entries inside alarms. Physical brute force records forced entries inside cameras. Physical brute force records forced entries inside sensors.

Physical brute force differs from cloning by damage. Physical brute force differs from cloning by force. Physical brute force differs from cloning by noise. Physical brute force differs from cloning by marks.

Physical brute force differs from weather by impact. Physical brute force differs from weather by marks. Physical brute force differs from weather by force. Physical brute force differs from weather by tools.

Physical brute force leaves bent metal not logs. Physical brute force leaves bent metal not badges. Physical brute force leaves bent metal not codes. Physical brute force leaves bent metal not tokens.

Physical brute force rams doors at the loading. Physical brute force rams doors at the rear. Physical brute force rams doors at the dock. Physical brute force rams doors at the cage.

Physical brute force rams doors at the lab. Physical brute force rams doors at the clinic. Physical brute force rams doors at the archive. Physical brute force rams doors at the roof.

Physical brute force rams doors at the annex. Physical brute force rams gates at the loading. Physical brute force rams gates at the rear. Physical brute force rams gates at the dock.

Physical brute force rams gates at the cage. Physical brute force rams gates at the lab. Physical brute force rams gates at the clinic. Physical brute force rams gates at the archive.

Physical brute force rams gates at the roof. Physical brute force rams gates at the annex. Physical brute force rams frames at the loading. Physical brute force rams frames at the rear.

Physical brute force rams frames at the dock. Physical brute force rams frames at the cage. Physical brute force rams frames at the lab. Physical brute force rams frames at the clinic.

Physical brute force rams frames at the archive. Physical brute force rams frames at the roof. Physical brute force rams frames at the annex. Physical brute force rams locks at the loading.

Physical brute force rams locks at the rear. Physical brute force rams locks at the dock. Physical brute force rams locks at the cage. Physical brute force rams locks at the lab.

Physical brute force rams locks at the clinic. Physical brute force rams locks at the archive. Physical brute force rams locks at the roof. Physical brute force rams locks at the annex.

Physical brute force rams hatches at the loading. Physical brute force rams hatches at the rear. Physical brute force rams hatches at the dock. Physical brute force rams hatches at the cage.

Physical brute force rams hatches at the lab. Physical brute force rams hatches at the clinic. Physical brute force rams hatches at the archive. Physical brute force rams hatches at the roof.

Physical brute force rams hatches at the annex. Physical brute force rams shutters at the loading. Physical brute force rams shutters at the rear. Physical brute force rams shutters at the dock.

Physical brute force rams shutters at the cage. Physical brute force rams shutters at the lab. Physical brute force rams shutters at the clinic. Physical brute force rams shutters at the archive.

Physical brute force rams shutters at the roof. Physical brute force rams shutters at the annex. Physical brute force rams cages at the loading. Physical brute force rams cages at the rear.

Physical brute force rams cages at the dock. Physical brute force rams cages at the cage. Physical brute force rams cages at the lab. Physical brute force rams cages at the clinic.

Physical brute force rams cages at the archive.
''',
        'r0': '''
Physical brute force trips door contacts into syslog. Physical brute force trips door contacts into alarms. Physical brute force trips door contacts into panels. Physical brute force trips door contacts into video.

Physical brute force shows pried sensor on camera. Physical brute force shows pried sensor on video. Physical brute force shows pried sensor on site. Physical brute force shows pried sensor on frame.

Physical brute force lacks valid badge read nearby. Physical brute force lacks valid badge read then. Physical brute force lacks valid badge read first. Physical brute force lacks valid badge read after.

Physical brute force pairs alarm time with video. Physical brute force pairs alarm time with syslog. Physical brute force pairs alarm time with damage. Physical brute force pairs alarm time with photos.
''',
        'r1': '''
Physical brute force means they broke the door. Physical brute force means they broke the lock. Physical brute force means they broke the gate. Physical brute force means they broke the frame.

Physical brute force shows damage instead of trickery. Physical brute force shows damage instead of codes. Physical brute force shows damage instead of badges. Physical brute force shows damage instead of clones.

Physical brute force is force you can see. Physical brute force is force you can photo. Physical brute force is force you can touch. Physical brute force is force you can film.
''',
        'r2': '''
Physical brute force resembles a ram against timber. Physical brute force resembles a hammer against hinges. Physical brute force resembles a bar against shutters. Physical brute force resembles a wedge against frames.

Physical brute force feels like splinters left behind. Physical brute force feels like bent left metal. Physical brute force feels like torn left seals. Physical brute force feels like cracked left glassless.

Physical brute force mirrors shutters forced inward today. Physical brute force mirrors gates forced aside today. Physical brute force mirrors cages forced open today. Physical brute force mirrors hatches forced up today.

Physical brute force acts as impact not finesse. Physical brute force acts as force not copies. Physical brute force acts as shock not stealth. Physical brute force acts as blows not badges.
''',
        'r4': '''
Physical brute force photograph frames before repairs start. Physical brute force photograph sensors before repairs begin. Physical brute force photograph hinges before repairs hide. Physical brute force photograph gates before repairs close.

Physical brute force photograph locks before repairs change. Physical brute force review syslog door alarms first. Physical brute force review syslog door alarms tonight. Physical brute force review syslog door alarms early.

Physical brute force review syslog door alarms fully. Physical brute force review syslog door alarms again.
''',
        'exam': '''
Physical brute force fits when damage shows force. Physical brute force fits when damage shows impact. Physical brute force fits when damage shows prying. Physical brute force fits when damage shows marks.

Physical brute force loses when only a clone. Physical brute force loses when only a badge. Physical brute force loses when only a code. Physical brute force loses when only a token.
''',
    },
    'RFID cloning': {
        'body': '''
RFID cloning copies a badge into a clone. RFID cloning copies a badge into a second. RFID cloning copies a badge into a duplicate. RFID cloning copies a badge into a spare.

RFID cloning shows one badge at two doors. RFID cloning shows one badge at two readers. RFID cloning shows one badge at two gates. RFID cloning shows one badge at two times.

RFID cloning differs from force by leaving none. RFID cloning differs from force by leaving zero. RFID cloning differs from force by leaving nothing. RFID cloning differs from force by leaving marks.

RFID cloning reads near a real badge briefly. RFID cloning reads near a real badge quietly. RFID cloning reads near a real badge closely. RFID cloning reads near a real badge once.

RFID cloning logs duplicate reads inside syslog today. RFID cloning logs duplicate reads inside panels today. RFID cloning logs duplicate reads inside badges today. RFID cloning logs duplicate reads inside doors today.

RFID cloning is not a stolen card itself. RFID cloning is not a stolen card only. RFID cloning is not a stolen card always. RFID cloning is not a stolen card alone.

RFID cloning mirrors staff badges at once today. RFID cloning mirrors staff badges at night today. RFID cloning mirrors staff badges at dawn today. RFID cloning mirrors staff badges at lunch today.

RFID cloning mirrors staff badges at shift today. RFID cloning mirrors staff badges at close today. RFID cloning mirrors staff badges at entry today. RFID cloning mirrors staff badges at exit today.

RFID cloning mirrors staff badges at annex today. RFID cloning mirrors vendor badges at once today. RFID cloning mirrors vendor badges at night today. RFID cloning mirrors vendor badges at dawn today.

RFID cloning mirrors vendor badges at lunch today. RFID cloning mirrors vendor badges at shift today. RFID cloning mirrors vendor badges at close today. RFID cloning mirrors vendor badges at entry today.

RFID cloning mirrors vendor badges at exit today. RFID cloning mirrors vendor badges at annex today. RFID cloning mirrors clinic badges at once today. RFID cloning mirrors clinic badges at night today.

RFID cloning mirrors clinic badges at dawn today. RFID cloning mirrors clinic badges at lunch today. RFID cloning mirrors clinic badges at shift today. RFID cloning mirrors clinic badges at close today.

RFID cloning mirrors clinic badges at entry today. RFID cloning mirrors clinic badges at exit today. RFID cloning mirrors clinic badges at annex today. RFID cloning mirrors lab badges at once today.

RFID cloning mirrors lab badges at night today. RFID cloning mirrors lab badges at dawn today. RFID cloning mirrors lab badges at lunch today. RFID cloning mirrors lab badges at shift today.

RFID cloning mirrors lab badges at close today. RFID cloning mirrors lab badges at entry today. RFID cloning mirrors lab badges at exit today. RFID cloning mirrors lab badges at annex today.

RFID cloning mirrors night badges at once today. RFID cloning mirrors night badges at night today. RFID cloning mirrors night badges at dawn today. RFID cloning mirrors night badges at lunch today.

RFID cloning mirrors night badges at shift today. RFID cloning mirrors night badges at close today. RFID cloning mirrors night badges at entry today. RFID cloning mirrors night badges at exit today.

RFID cloning mirrors night badges at annex today. RFID cloning mirrors loading badges at once today. RFID cloning mirrors loading badges at night today. RFID cloning mirrors loading badges at dawn today.

RFID cloning mirrors loading badges at lunch today. RFID cloning mirrors loading badges at shift today. RFID cloning mirrors loading badges at close today. RFID cloning mirrors loading badges at entry today.

RFID cloning mirrors loading badges at exit today. RFID cloning mirrors loading badges at annex today. RFID cloning mirrors front badges at once today. RFID cloning mirrors front badges at night today.

RFID cloning mirrors front badges at dawn today. RFID cloning mirrors front badges at lunch today. RFID cloning mirrors front badges at shift today. RFID cloning mirrors front badges at close today.

RFID cloning mirrors front badges at entry today.
''',
        'r0': '''
RFID cloning flags one id at two readers. RFID cloning flags one id at two doors. RFID cloning flags one id at two sites. RFID cloning flags one id at two times.

RFID cloning stores reads in panel syslog today. RFID cloning stores reads in panel buffers today. RFID cloning stores reads in panel exports today. RFID cloning stores reads in panel journals today.

RFID cloning lacks tailgating video of entry today. RFID cloning lacks tailgating video of force today. RFID cloning lacks tailgating video of damage today. RFID cloning lacks tailgating video of prying today.

RFID cloning matches facility codes on both today. RFID cloning matches facility codes on clones today. RFID cloning matches facility codes on reads today. RFID cloning matches facility codes on hits today.
''',
        'r1': '''
RFID cloning means a copied badge still works. RFID cloning means a copied badge still opens. RFID cloning means a copied badge still scans. RFID cloning means a copied badge still passes.

RFID cloning can happen without broken doors today. RFID cloning can happen without broken locks today. RFID cloning can happen without broken frames today. RFID cloning can happen without broken glass today.

RFID cloning shows the same badge twice once. RFID cloning shows the same badge twice fast. RFID cloning shows the same badge twice apart. RFID cloning shows the same badge twice today.
''',
        'r2': '''
RFID cloning resembles a second stamp made quietly. RFID cloning resembles a spare stamp made nearby. RFID cloning resembles a twin stamp made later. RFID cloning resembles a copy stamp made close.

RFID cloning feels like borrowed ink on paper. RFID cloning feels like traced ink on cards. RFID cloning feels like pressed ink on slips. RFID cloning feels like echoed ink on seals.

RFID cloning mirrors twin passes used apart today. RFID cloning mirrors spare passes used twice today. RFID cloning mirrors copied passes used elsewhere today. RFID cloning mirrors silent passes used again today.

RFID cloning acts as echoes without damage today. RFID cloning acts as twins without force today. RFID cloning acts as copies without marks today. RFID cloning acts as shadows without noise today.
''',
        'r4': '''
RFID cloning compare badge reads at once today. RFID cloning compare badge reads at doors today. RFID cloning compare badge reads at times today. RFID cloning compare badge reads at sites today.

RFID cloning compare badge reads at dawn today. RFID cloning disable the cloned badge immediately today. RFID cloning disable the duplicated badge immediately now. RFID cloning disable the shared badge immediately fully.

RFID cloning disable the suspect badge immediately fast. RFID cloning disable the night badge immediately first.
''',
        'exam': '''
RFID cloning fits when one badge is twice. RFID cloning fits when one badge is cloned. RFID cloning fits when one badge is duplicated. RFID cloning fits when one badge is echoed.

RFID cloning loses when the frame is splintered. RFID cloning loses when the frame is forced. RFID cloning loses when the frame is pried. RFID cloning loses when the frame is bent.
''',
    },
    'Environmental attacks': {
        'body': '''
Environmental attacks use heat against rack inlet sensors. Environmental attacks use water against rack inlet gear. Environmental attacks use cold against rack inlet alerts. Environmental attacks use power against rack inlet rooms.

Environmental attacks log temperature spikes inside the syslog. Environmental attacks log temperature spikes inside the bms. Environmental attacks log temperature spikes inside the alarm. Environmental attacks log temperature spikes inside the trace.

Environmental attacks differ from force by using climate. Environmental attacks differ from force by using power. Environmental attacks differ from force by using water. Environmental attacks differ from force by using heat.

Environmental attacks aim at sensors so gear stops. Environmental attacks aim at sensors so gear shuts. Environmental attacks aim at sensors so gear trips. Environmental attacks aim at sensors so gear fails.

Environmental attacks are not badge copies or clones. Environmental attacks are not badge copies or tokens. Environmental attacks are not badge copies or reads. Environmental attacks are not badge copies or codes.

Environmental attacks can force a bad shutdown choice. Environmental attacks can force a bad shutdown call. Environmental attacks can force a bad shutdown path. Environmental attacks can force a bad shutdown step.

Environmental attacks stress closet rooms using heat today. Environmental attacks stress closet rooms using cold today. Environmental attacks stress closet rooms using water today. Environmental attacks stress closet rooms using dust today.

Environmental attacks stress closet rooms using power today. Environmental attacks stress closet rooms using humidity today. Environmental attacks stress closet rooms using smoke today. Environmental attacks stress closet rooms using vibration today.

Environmental attacks stress closet rooms using annex today. Environmental attacks stress rack rooms using heat today. Environmental attacks stress rack rooms using cold today. Environmental attacks stress rack rooms using water today.

Environmental attacks stress rack rooms using dust today. Environmental attacks stress rack rooms using power today. Environmental attacks stress rack rooms using humidity today. Environmental attacks stress rack rooms using smoke today.

Environmental attacks stress rack rooms using vibration today. Environmental attacks stress rack rooms using annex today. Environmental attacks stress lab rooms using heat today. Environmental attacks stress lab rooms using cold today.

Environmental attacks stress lab rooms using water today. Environmental attacks stress lab rooms using dust today. Environmental attacks stress lab rooms using power today. Environmental attacks stress lab rooms using humidity today.

Environmental attacks stress lab rooms using smoke today. Environmental attacks stress lab rooms using vibration today. Environmental attacks stress lab rooms using annex today. Environmental attacks stress clinic rooms using heat today.

Environmental attacks stress clinic rooms using cold today. Environmental attacks stress clinic rooms using water today. Environmental attacks stress clinic rooms using dust today. Environmental attacks stress clinic rooms using power today.

Environmental attacks stress clinic rooms using humidity today. Environmental attacks stress clinic rooms using smoke today. Environmental attacks stress clinic rooms using vibration today. Environmental attacks stress clinic rooms using annex today.

Environmental attacks stress archive rooms using heat today. Environmental attacks stress archive rooms using cold today. Environmental attacks stress archive rooms using water today. Environmental attacks stress archive rooms using dust today.

Environmental attacks stress archive rooms using power today. Environmental attacks stress archive rooms using humidity today. Environmental attacks stress archive rooms using smoke today. Environmental attacks stress archive rooms using vibration today.

Environmental attacks stress archive rooms using annex today. Environmental attacks stress roof rooms using heat today. Environmental attacks stress roof rooms using cold today. Environmental attacks stress roof rooms using water today.

Environmental attacks stress roof rooms using dust today. Environmental attacks stress roof rooms using power today. Environmental attacks stress roof rooms using humidity today. Environmental attacks stress roof rooms using smoke today.

Environmental attacks stress roof rooms using vibration today. Environmental attacks stress roof rooms using annex today. Environmental attacks stress battery rooms using heat today. Environmental attacks stress battery rooms using cold today.

Environmental attacks stress battery rooms using water today. Environmental attacks stress battery rooms using dust today. Environmental attacks stress battery rooms using power today. Environmental attacks stress battery rooms using humidity today.

Environmental attacks stress battery rooms using smoke today.
''',
        'r0': '''
Environmental attacks raise inlet temps in bms syslog. Environmental attacks raise inlet temps in bms trends. Environmental attacks raise inlet temps in bms alarms. Environmental attacks raise inlet temps in bms graphs.

Environmental attacks trip power feeds without a login. Environmental attacks trip power feeds without a badge. Environmental attacks trip power feeds without a exploit. Environmental attacks trip power feeds without a payload.

Environmental attacks leave water sensors wet in logs. Environmental attacks leave water sensors wet in photos. Environmental attacks leave water sensors wet in trays. Environmental attacks leave water sensors wet in pans.

Environmental attacks skew thermostats until hosts halt today. Environmental attacks skew thermostats until hosts throttle today. Environmental attacks skew thermostats until hosts alarm today. Environmental attacks skew thermostats until hosts stop today.
''',
        'r1': '''
Environmental attacks means the room is the target. Environmental attacks means the room is the weapon. Environmental attacks means the room is the path. Environmental attacks means the room is the problem.

Environmental attacks bring heat cold water or power. Environmental attacks bring heat cold water or dust. Environmental attacks bring heat cold water or smoke. Environmental attacks bring heat cold water or ice.

Environmental attacks can shut gear without a password. Environmental attacks can shut gear without a badge. Environmental attacks can shut gear without a login. Environmental attacks can shut gear without a code.
''',
        'r2': '''
Environmental attacks resemble heaters aimed at sensors today. Environmental attacks resemble buckets aimed at floors today. Environmental attacks resemble fans aimed at inlets today. Environmental attacks resemble ice aimed at racks today.

Environmental attacks feel like weather against cabinets today. Environmental attacks feel like steam against shelves today. Environmental attacks feel like dust against vents today. Environmental attacks feel like drips against trays today.

Environmental attacks mirror climate turned into harm today. Environmental attacks mirror power turned into noise today. Environmental attacks mirror water turned into trouble today. Environmental attacks mirror cold turned into halts today.

Environmental attacks act as weather on purpose today. Environmental attacks act as climate on demand today. Environmental attacks act as heat on schedule today. Environmental attacks act as leaks on purpose today.
''',
        'r4': '''
Environmental attacks review bms temps before blame today. Environmental attacks review bms temps before reboot today. Environmental attacks review bms temps before restore today. Environmental attacks review bms temps before patch today.

Environmental attacks review bms temps before guess today. Environmental attacks photograph wet rooms before cleanup today. Environmental attacks photograph hot rooms before cooldown today. Environmental attacks photograph dusty rooms before filters today.

Environmental attacks photograph dark rooms before power today. Environmental attacks photograph cold rooms before restart today.
''',
        'exam': '''
Environmental attacks fit when the room causes harm. Environmental attacks fit when the room causes shutdown. Environmental attacks fit when the room causes heat. Environmental attacks fit when the room causes loss.

Environmental attacks lose when a door was kicked. Environmental attacks lose when a door was pried. Environmental attacks lose when a door was rammed. Environmental attacks lose when a door was forced.
''',
    },
    'Distributed denial of service': {
        'body': '''
Distributed denial of service abuses amplification and reflection. Distributed denial of service abuses volume and spoofing. Distributed denial of service abuses reflectors and noise. Distributed denial of service abuses queries and size.

Distributed denial of service spoofs queries toward amplifiers. Distributed denial of service spoofs sources toward resolvers. Distributed denial of service spoofs packets toward reflectors. Distributed denial of service spoofs names toward monitors.

Distributed denial of service saturates links while healthy. Distributed denial of service saturates pipes while up. Distributed denial of service saturates edges while fine. Distributed denial of service saturates paths while idle.

Distributed denial of service gathers numerous origins together. Distributed denial of service gathers numerous hosts atonce. Distributed denial of service gathers numerous nets wide. Distributed denial of service gathers numerous bots briefly.

Distributed denial of service shows in netflow spikes. Distributed denial of service shows in syslog drops. Distributed denial of service shows in graphs flat. Distributed denial of service shows in edges full.

Distributed denial of service differs from theft goals. Distributed denial of service differs from logins noise. Distributed denial of service differs from crashes floods. Distributed denial of service differs from malware volume.

Distributed denial of service floods dns via reflection. Distributed denial of service floods dns via amplification. Distributed denial of service floods dns via spoofing. Distributed denial of service floods dns via volume.

Distributed denial of service floods dns via noise. Distributed denial of service floods dns via bursts. Distributed denial of service floods dns via edges. Distributed denial of service floods dns via paths.

Distributed denial of service floods dns via annex. Distributed denial of service floods ntp via reflection. Distributed denial of service floods ntp via amplification. Distributed denial of service floods ntp via spoofing.

Distributed denial of service floods ntp via volume. Distributed denial of service floods ntp via noise. Distributed denial of service floods ntp via bursts. Distributed denial of service floods ntp via edges.

Distributed denial of service floods ntp via paths. Distributed denial of service floods ntp via annex. Distributed denial of service floods ssdp via reflection. Distributed denial of service floods ssdp via amplification.

Distributed denial of service floods ssdp via spoofing. Distributed denial of service floods ssdp via volume. Distributed denial of service floods ssdp via noise. Distributed denial of service floods ssdp via bursts.

Distributed denial of service floods ssdp via edges. Distributed denial of service floods ssdp via paths. Distributed denial of service floods ssdp via annex. Distributed denial of service floods memcached via reflection.

Distributed denial of service floods memcached via amplification. Distributed denial of service floods memcached via spoofing. Distributed denial of service floods memcached via volume. Distributed denial of service floods memcached via noise.

Distributed denial of service floods memcached via bursts. Distributed denial of service floods memcached via edges. Distributed denial of service floods memcached via paths. Distributed denial of service floods memcached via annex.

Distributed denial of service floods chargen via reflection. Distributed denial of service floods chargen via amplification. Distributed denial of service floods chargen via spoofing. Distributed denial of service floods chargen via volume.

Distributed denial of service floods chargen via noise. Distributed denial of service floods chargen via bursts. Distributed denial of service floods chargen via edges. Distributed denial of service floods chargen via paths.

Distributed denial of service floods chargen via annex. Distributed denial of service floods ldap via reflection. Distributed denial of service floods ldap via amplification. Distributed denial of service floods ldap via spoofing.

Distributed denial of service floods ldap via volume. Distributed denial of service floods ldap via noise. Distributed denial of service floods ldap via bursts. Distributed denial of service floods ldap via edges.

Distributed denial of service floods ldap via paths. Distributed denial of service floods ldap via annex. Distributed denial of service floods snmp via reflection. Distributed denial of service floods snmp via amplification.

Distributed denial of service floods snmp via spoofing. Distributed denial of service floods snmp via volume. Distributed denial of service floods snmp via noise. Distributed denial of service floods snmp via bursts.

Distributed denial of service floods snmp via edges.
''',
        'r0': '''
Distributed denial of service compares query size replies. Distributed denial of service compares query rate bytes. Distributed denial of service compares query src spoof. Distributed denial of service compares query ttl hops.

Distributed denial of service reads netflow spikes inbound. Distributed denial of service reads netflow pairs reflect. Distributed denial of service reads netflow tops talkers. Distributed denial of service reads netflow maps edges.

Distributed denial of service keeps servers healthy anyway. Distributed denial of service keeps servers up still. Distributed denial of service keeps servers idle inside. Distributed denial of service keeps servers fine locally.

Distributed denial of service rates limit dns replies. Distributed denial of service rates limit udp bursts. Distributed denial of service rates limit edges first. Distributed denial of service rates limit queries hard.
''',
        'r1': '''
Distributed denial of service means many sources flood. Distributed denial of service means many callers block. Distributed denial of service means many noises crowd. Distributed denial of service means many hits pile.

Distributed denial of service can amplify small queries. Distributed denial of service can amplify tiny asks. Distributed denial of service can amplify short packets. Distributed denial of service can amplify fake sources.

Distributed denial of service leaves servers up anyway. Distributed denial of service leaves servers fine inside. Distributed denial of service leaves servers healthy still. Distributed denial of service leaves servers idle locally.
''',
        'r2': '''
Distributed denial of service resembles empty carts today. Distributed denial of service resembles fake queues today. Distributed denial of service resembles loud crowds today. Distributed denial of service resembles jammed lanes today.

Distributed denial of service feels like echo canyons. Distributed denial of service feels like megaphone yards. Distributed denial of service feels like stampedes doors. Distributed denial of service feels like confetti storms.

Distributed denial of service mirrors shouted questions today. Distributed denial of service mirrors huge answers today. Distributed denial of service mirrors tiny whistles today. Distributed denial of service mirrors vast roars today.

Distributed denial of service acts as noise walls. Distributed denial of service acts as crowd blocks. Distributed denial of service acts as echo traps. Distributed denial of service acts as flood gates.
''',
        'r4': '''
Distributed denial of service rate limit udp replies. Distributed denial of service rate limit dns queries. Distributed denial of service rate limit edges first. Distributed denial of service rate limit reflectors hard.

Distributed denial of service rate limit inbound bursts. Distributed denial of service read netflow before blame. Distributed denial of service read netflow for talkers. Distributed denial of service read netflow at edges.

Distributed denial of service read netflow during spikes. Distributed denial of service read netflow after alerts.
''',
        'exam': '''
Distributed denial of service fits many sources flooding. Distributed denial of service fits many reflectors answering. Distributed denial of service fits many links full. Distributed denial of service fits many edges saturated.

Distributed denial of service loses if one host. Distributed denial of service loses if servers crashed. Distributed denial of service loses if files encrypted. Distributed denial of service loses if logs empty.
''',
    },
    'DNS attacks': {
        'body': '''
DNS attacks corrupt lookups so staff reach fakes. DNS attacks corrupt lookups so staff reach clones. DNS attacks corrupt lookups so staff reach decoys. DNS attacks corrupt lookups so staff reach traps.

DNS attacks poison resolvers toward a lookalike host. DNS attacks poison resolvers toward a lookalike site. DNS attacks poison resolvers toward a lookalike name. DNS attacks poison resolvers toward a lookalike page.

DNS attacks differ from floods because names lie. DNS attacks differ from floods because names shift. DNS attacks differ from floods because names redirect. DNS attacks differ from floods because names mislead.

DNS attacks show odd answers in dns logs. DNS attacks show odd answers in dns cache. DNS attacks show odd answers in dns traces. DNS attacks show odd answers in dns debug.

DNS attacks can feed amplification when open resolvers. DNS attacks can feed amplification when open recursion. DNS attacks can feed amplification when open replies. DNS attacks can feed amplification when open servers.

DNS attacks are not wireless evil twins themselves. DNS attacks are not wireless evil twins alone. DNS attacks are not wireless evil twins only. DNS attacks are not wireless evil twins purely.

DNS attacks redirect payroll names toward fakes today. DNS attacks redirect payroll names toward clones today. DNS attacks redirect payroll names toward sinks today. DNS attacks redirect payroll names toward traps today.

DNS attacks redirect payroll names toward decoys today. DNS attacks redirect payroll names toward lookalikes today. DNS attacks redirect payroll names toward staging today. DNS attacks redirect payroll names toward collectors today.

DNS attacks redirect payroll names toward annex today. DNS attacks redirect mail names toward fakes today. DNS attacks redirect mail names toward clones today. DNS attacks redirect mail names toward sinks today.

DNS attacks redirect mail names toward traps today. DNS attacks redirect mail names toward decoys today. DNS attacks redirect mail names toward lookalikes today. DNS attacks redirect mail names toward staging today.

DNS attacks redirect mail names toward collectors today. DNS attacks redirect mail names toward annex today. DNS attacks redirect vpn names toward fakes today. DNS attacks redirect vpn names toward clones today.

DNS attacks redirect vpn names toward sinks today. DNS attacks redirect vpn names toward traps today. DNS attacks redirect vpn names toward decoys today. DNS attacks redirect vpn names toward lookalikes today.

DNS attacks redirect vpn names toward staging today. DNS attacks redirect vpn names toward collectors today. DNS attacks redirect vpn names toward annex today. DNS attacks redirect clinic names toward fakes today.

DNS attacks redirect clinic names toward clones today. DNS attacks redirect clinic names toward sinks today. DNS attacks redirect clinic names toward traps today. DNS attacks redirect clinic names toward decoys today.

DNS attacks redirect clinic names toward lookalikes today. DNS attacks redirect clinic names toward staging today. DNS attacks redirect clinic names toward collectors today. DNS attacks redirect clinic names toward annex today.

DNS attacks redirect sso names toward fakes today. DNS attacks redirect sso names toward clones today. DNS attacks redirect sso names toward sinks today. DNS attacks redirect sso names toward traps today.

DNS attacks redirect sso names toward decoys today. DNS attacks redirect sso names toward lookalikes today. DNS attacks redirect sso names toward staging today. DNS attacks redirect sso names toward collectors today.

DNS attacks redirect sso names toward annex today. DNS attacks redirect files names toward fakes today. DNS attacks redirect files names toward clones today. DNS attacks redirect files names toward sinks today.

DNS attacks redirect files names toward traps today. DNS attacks redirect files names toward decoys today. DNS attacks redirect files names toward lookalikes today. DNS attacks redirect files names toward staging today.

DNS attacks redirect files names toward collectors today. DNS attacks redirect files names toward annex today. DNS attacks redirect updates names toward fakes today. DNS attacks redirect updates names toward clones today.

DNS attacks redirect updates names toward sinks today. DNS attacks redirect updates names toward traps today. DNS attacks redirect updates names toward decoys today. DNS attacks redirect updates names toward lookalikes today.

DNS attacks redirect updates names toward staging today.
''',
        'r0': '''
DNS attacks compare resolver answers with authority today. DNS attacks compare resolver answers with dnssec today. DNS attacks compare resolver answers with expected today. DNS attacks compare resolver answers with baseline today.

DNS attacks read dns debug logs for poison. DNS attacks read dns debug logs for mismatch. DNS attacks read dns debug logs for ttl. DNS attacks read dns debug logs for oddity.

DNS attacks disable open recursion on edges today. DNS attacks disable open recursion on caches today. DNS attacks disable open recursion on resolvers today. DNS attacks disable open recursion on forwards today.

DNS attacks alert when ttl drops without change. DNS attacks alert when ttl drops without ticket. DNS attacks alert when ttl drops without owner. DNS attacks alert when ttl drops without plan.
''',
        'r1': '''
DNS attacks mean the name book is lying. DNS attacks mean the name book is wrong. DNS attacks mean the name book is shifted. DNS attacks mean the name book is fake.

DNS attacks send people to a lookalike site. DNS attacks send people to a lookalike host. DNS attacks send people to a lookalike page. DNS attacks send people to a lookalike name.

DNS attacks are about names not just noise. DNS attacks are about names not just volume. DNS attacks are about names not just floods. DNS attacks are about names not just load.
''',
        'r2': '''
DNS attacks resemble swapped signs on trails today. DNS attacks resemble moved signs on markers today. DNS attacks resemble false signs on mileposts today. DNS attacks resemble turned signs on arrows today.

DNS attacks feel like relabeled maps with roads. DNS attacks feel like edited maps with indexes. DNS attacks feel like wrong maps with captions. DNS attacks feel like shifted maps with labels.

DNS attacks mirror lobby directories pointing elsewhere today. DNS attacks mirror desk directories pointing aside today. DNS attacks mirror index directories pointing away today. DNS attacks mirror catalog directories pointing wrong today.

DNS attacks act as false guides toward houses. DNS attacks act as bad guides toward rooms. DNS attacks act as wrong guides toward desks. DNS attacks act as decoy guides toward counters.
''',
        'r4': '''
DNS attacks compare answers with the authority today. DNS attacks compare answers with the baseline today. DNS attacks compare answers with the owner today. DNS attacks compare answers with the ticket today.

DNS attacks compare answers with the plan today. DNS attacks disable open recursion at edges today. DNS attacks disable open recursion at caches today. DNS attacks disable open recursion at branches today.

DNS attacks disable open recursion at resolvers today. DNS attacks disable open recursion at forwards today.
''',
        'exam': '''
DNS attacks fit when a trusted name lies. DNS attacks fit when a trusted name shifts. DNS attacks fit when a trusted name redirects. DNS attacks fit when a trusted name misleads.

DNS attacks lose when only volume is high. DNS attacks lose when only volume is huge. DNS attacks lose when only volume is noisy. DNS attacks lose when only volume is full.
''',
    },
    'Wireless attacks': {
        'body': '''
Wireless attacks include rogue radios and evil twins. Wireless attacks include rogue radios and evil clones. Wireless attacks include rogue radios and evil names. Wireless attacks include rogue radios and evil traps.

Wireless attacks crack a weak passphrase from nearby. Wireless attacks crack a weak passphrase from hallway. Wireless attacks crack a weak passphrase from clinic. Wireless attacks crack a weak passphrase from lobby.

Wireless attacks differ from dns lies using radio. Wireless attacks differ from dns lies using signal. Wireless attacks differ from dns lies using air. Wireless attacks differ from dns lies using ssid.

Wireless attacks show a second name in scans. Wireless attacks show a second name in surveys. Wireless attacks show a second name in logs. Wireless attacks show a second name in alerts.

Wireless attacks lure laptops that autojoin known names. Wireless attacks lure laptops that autojoin known ssids. Wireless attacks lure laptops that autojoin known labels. Wireless attacks lure laptops that autojoin known titles.

Wireless attacks are not badge clones or doors. Wireless attacks are not badge clones or force. Wireless attacks are not badge clones or heat. Wireless attacks are not badge clones or floods.

Wireless attacks log rogue names inside the syslog. Wireless attacks log rogue names inside the survey. Wireless attacks log rogue names inside the wids. Wireless attacks log rogue names inside the controller.

Wireless attacks spoof clinic names from nearby today. Wireless attacks spoof clinic names from hallway today. Wireless attacks spoof clinic names from parkinglot today. Wireless attacks spoof clinic names from cafe today.

Wireless attacks spoof clinic names from atrium today. Wireless attacks spoof clinic names from garage today. Wireless attacks spoof clinic names from courtyard today. Wireless attacks spoof clinic names from stair today.

Wireless attacks spoof guest names from nearby today. Wireless attacks spoof guest names from hallway today. Wireless attacks spoof guest names from parkinglot today. Wireless attacks spoof guest names from cafe today.

Wireless attacks spoof guest names from atrium today. Wireless attacks spoof guest names from garage today. Wireless attacks spoof guest names from courtyard today. Wireless attacks spoof guest names from stair today.

Wireless attacks spoof staff names from nearby today. Wireless attacks spoof staff names from hallway today. Wireless attacks spoof staff names from parkinglot today. Wireless attacks spoof staff names from cafe today.

Wireless attacks spoof staff names from atrium today. Wireless attacks spoof staff names from garage today. Wireless attacks spoof staff names from courtyard today. Wireless attacks spoof staff names from stair today.

Wireless attacks spoof lab names from nearby today. Wireless attacks spoof lab names from hallway today. Wireless attacks spoof lab names from parkinglot today. Wireless attacks spoof lab names from cafe today.

Wireless attacks spoof lab names from atrium today. Wireless attacks spoof lab names from garage today. Wireless attacks spoof lab names from courtyard today. Wireless attacks spoof lab names from stair today.

Wireless attacks spoof lobby names from nearby today. Wireless attacks spoof lobby names from hallway today. Wireless attacks spoof lobby names from parkinglot today. Wireless attacks spoof lobby names from cafe today.

Wireless attacks spoof lobby names from atrium today. Wireless attacks spoof lobby names from garage today. Wireless attacks spoof lobby names from courtyard today. Wireless attacks spoof lobby names from stair today.

Wireless attacks spoof vendor names from nearby today. Wireless attacks spoof vendor names from hallway today. Wireless attacks spoof vendor names from parkinglot today. Wireless attacks spoof vendor names from cafe today.

Wireless attacks spoof vendor names from atrium today. Wireless attacks spoof vendor names from garage today. Wireless attacks spoof vendor names from courtyard today. Wireless attacks spoof vendor names from stair today.

Wireless attacks spoof classroom names from nearby today. Wireless attacks spoof classroom names from hallway today. Wireless attacks spoof classroom names from parkinglot today. Wireless attacks spoof classroom names from cafe today.

Wireless attacks spoof classroom names from atrium today. Wireless attacks spoof classroom names from garage today. Wireless attacks spoof classroom names from courtyard today. Wireless attacks spoof classroom names from stair today.

Wireless attacks spoof warehouse names from nearby today.
''',
        'r0': '''
Wireless attacks log rogue ssids in the survey. Wireless attacks log rogue ssids in the wids. Wireless attacks log rogue ssids in the controller. Wireless attacks log rogue ssids in the syslog.

Wireless attacks capture handshakes when passphrases weak today. Wireless attacks capture handshakes when passphrases short today. Wireless attacks capture handshakes when passphrases shared today. Wireless attacks capture handshakes when passphrases reused today.

Wireless attacks alert on a second bssid nearby. Wireless attacks alert on a second bssid today. Wireless attacks alert on a second bssid inside. Wireless attacks alert on a second bssid fast.

Wireless attacks prefer wpa3 or long unique secrets. Wireless attacks prefer wpa3 or long unique phrases. Wireless attacks prefer wpa3 or long unique keys. Wireless attacks prefer wpa3 or long unique codes.
''',
        'r1': '''
Wireless attacks mean a fake or weak radio. Wireless attacks mean a fake or weak signal. Wireless attacks mean a fake or weak name. Wireless attacks mean a fake or weak network.

Wireless attacks copy a familiar name over air. Wireless attacks copy a familiar name over radio. Wireless attacks copy a familiar name over wifi. Wireless attacks copy a familiar name over signal.

Wireless attacks can sit near the building quietly. Wireless attacks can sit near the building briefly. Wireless attacks can sit near the building outside. Wireless attacks can sit near the building today.
''',
        'r2': '''
Wireless attacks resemble copied banners on carts today. Wireless attacks resemble twin banners on stalls today. Wireless attacks resemble false banners on awnings today. Wireless attacks resemble second banners on booths today.

Wireless attacks feel like familiar voices using names. Wireless attacks feel like borrowed voices using titles. Wireless attacks feel like echoed voices using calls. Wireless attacks feel like twin voices using labels.

Wireless attacks mirror decoy shops across aisles today. Wireless attacks mirror pop shops across lanes today. Wireless attacks mirror shadow shops across counters today. Wireless attacks mirror copy shops across windows today.

Wireless attacks act as twin radios with names. Wireless attacks act as weak radios with locks. Wireless attacks act as rogue radios with signs. Wireless attacks act as nearby radios with traps.
''',
        'r4': '''
Wireless attacks survey ssids before staff join today. Wireless attacks survey ssids before staff trust today. Wireless attacks survey ssids before staff roam today. Wireless attacks survey ssids before staff save today.

Wireless attacks survey ssids before staff auto today. Wireless attacks rotate weak passphrases this week today. Wireless attacks rotate weak passphrases this month today. Wireless attacks rotate weak passphrases this night today.

Wireless attacks rotate weak passphrases this cycle today. Wireless attacks rotate weak passphrases this window today.
''',
        'exam': '''
Wireless attacks fit when a second radio copies. Wireless attacks fit when a second radio appears. Wireless attacks fit when a second radio traps. Wireless attacks fit when a second radio lures.

Wireless attacks lose when only a name lookup. Wireless attacks lose when only a name lies. Wireless attacks lose when only a name shifts. Wireless attacks lose when only a name redirects.
''',
    },
    'On-path attacks': {
        'body': '''
On-path attacks sit between parties and alter bytes. On-path attacks sit between parties and alter traffic. On-path attacks sit between parties and alter logins. On-path attacks sit between parties and alter tokens.

On-path attacks differ from replay of captured bytes. On-path attacks differ from replay of captured tokens. On-path attacks differ from replay of captured logins. On-path attacks differ from replay of captured cookies.

On-path attacks relay logins that lack tls protection. On-path attacks relay logins that lack tls checks. On-path attacks relay logins that lack tls seals. On-path attacks relay logins that lack tls privacy.

On-path attacks show arp changes on a lan. On-path attacks show arp changes on a cafe. On-path attacks show arp changes on a vlan. On-path attacks show arp changes on a segment.

On-path attacks can edit live traffic not later. On-path attacks can edit live traffic not stored. On-path attacks can edit live traffic not old. On-path attacks can edit live traffic not saved.

On-path attacks are not application payment repeats alone. On-path attacks are not application payment repeats only. On-path attacks are not application payment repeats purely. On-path attacks are not application payment repeats merely.

On-path attacks relay cafe sessions on lan today. On-path attacks relay cafe sessions on wifi today. On-path attacks relay cafe sessions on vlan today. On-path attacks relay cafe sessions on segment today.

On-path attacks relay cafe sessions on switch today. On-path attacks relay cafe sessions on bridge today. On-path attacks relay cafe sessions on hub today. On-path attacks relay cafe sessions on path today.

On-path attacks relay cafe sessions on annex today. On-path attacks relay guest sessions on lan today. On-path attacks relay guest sessions on wifi today. On-path attacks relay guest sessions on vlan today.

On-path attacks relay guest sessions on segment today. On-path attacks relay guest sessions on switch today. On-path attacks relay guest sessions on bridge today. On-path attacks relay guest sessions on hub today.

On-path attacks relay guest sessions on path today. On-path attacks relay guest sessions on annex today. On-path attacks relay lobby sessions on lan today. On-path attacks relay lobby sessions on wifi today.

On-path attacks relay lobby sessions on vlan today. On-path attacks relay lobby sessions on segment today. On-path attacks relay lobby sessions on switch today. On-path attacks relay lobby sessions on bridge today.

On-path attacks relay lobby sessions on hub today. On-path attacks relay lobby sessions on path today. On-path attacks relay lobby sessions on annex today. On-path attacks relay lab sessions on lan today.

On-path attacks relay lab sessions on wifi today. On-path attacks relay lab sessions on vlan today. On-path attacks relay lab sessions on segment today. On-path attacks relay lab sessions on switch today.

On-path attacks relay lab sessions on bridge today. On-path attacks relay lab sessions on hub today. On-path attacks relay lab sessions on path today. On-path attacks relay lab sessions on annex today.

On-path attacks relay clinic sessions on lan today. On-path attacks relay clinic sessions on wifi today. On-path attacks relay clinic sessions on vlan today. On-path attacks relay clinic sessions on segment today.

On-path attacks relay clinic sessions on switch today. On-path attacks relay clinic sessions on bridge today. On-path attacks relay clinic sessions on hub today. On-path attacks relay clinic sessions on path today.

On-path attacks relay clinic sessions on annex today. On-path attacks relay vendor sessions on lan today. On-path attacks relay vendor sessions on wifi today. On-path attacks relay vendor sessions on vlan today.

On-path attacks relay vendor sessions on segment today. On-path attacks relay vendor sessions on switch today. On-path attacks relay vendor sessions on bridge today. On-path attacks relay vendor sessions on hub today.

On-path attacks relay vendor sessions on path today. On-path attacks relay vendor sessions on annex today. On-path attacks relay classroom sessions on lan today. On-path attacks relay classroom sessions on wifi today.

On-path attacks relay classroom sessions on vlan today. On-path attacks relay classroom sessions on segment today. On-path attacks relay classroom sessions on switch today. On-path attacks relay classroom sessions on bridge today.

On-path attacks relay classroom sessions on hub today.
''',
        'r0': '''
On-path attacks watch arp tables for a flip. On-path attacks watch arp tables for a fight. On-path attacks watch arp tables for a move. On-path attacks watch arp tables for a clash.

On-path attacks require tls so relays cannot read. On-path attacks require tls so relays cannot edit. On-path attacks require tls so relays cannot forge. On-path attacks require tls so relays cannot steal.

On-path attacks log cert warnings users click through. On-path attacks log cert warnings users click past. On-path attacks log cert warnings users click anyway. On-path attacks log cert warnings users click aside.

On-path attacks pin expected keys on admin tools. On-path attacks pin expected keys on admin jumps. On-path attacks pin expected keys on admin shells. On-path attacks pin expected keys on admin apps.
''',
        'r1': '''
On-path attacks mean someone stands in the middle. On-path attacks mean someone stands in the path. On-path attacks mean someone stands in the gap. On-path attacks mean someone stands in the line.

On-path attacks can read or change live talk. On-path attacks can read or change live traffic. On-path attacks can read or change live words. On-path attacks can read or change live bytes.

On-path attacks need the attacker present right now. On-path attacks need the attacker present right then. On-path attacks need the attacker present right there. On-path attacks need the attacker present right live.
''',
        'r2': '''
On-path attacks resemble mid translators changing words today. On-path attacks resemble live translators changing letters today. On-path attacks resemble path translators changing notes today. On-path attacks resemble desk translators changing slips today.

On-path attacks feel like live couriers rewriting notes. On-path attacks feel like hallway couriers rewriting slips. On-path attacks feel like desk couriers rewriting memos. On-path attacks feel like counter couriers rewriting forms.

On-path attacks mirror switchboard operators on calls today. On-path attacks mirror headset operators on lines today. On-path attacks mirror relay operators on messages today. On-path attacks mirror bridge operators on talk today.

On-path attacks act as live middles that edit. On-path attacks act as present middles that rewrite. On-path attacks act as active middles that relay. On-path attacks act as open middles that alter.
''',
        'r4': '''
On-path attacks require tls before any login today. On-path attacks require tls before any relay today. On-path attacks require tls before any cafe today. On-path attacks require tls before any guest today.

On-path attacks require tls before any jump today. On-path attacks inspect arp tables after roams today. On-path attacks inspect arp tables after joins today. On-path attacks inspect arp tables after moves today.

On-path attacks inspect arp tables after alerts today. On-path attacks inspect arp tables after flips today.
''',
        'exam': '''
On-path attacks fit when someone can alter live. On-path attacks fit when someone can alter now. On-path attacks fit when someone can alter bytes. On-path attacks fit when someone can alter traffic.

On-path attacks lose when only an old capture. On-path attacks lose when only an old token. On-path attacks lose when only an old cookie. On-path attacks lose when only an old replay.
''',
    },
    'Credential replay': {
        'body': '''
Credential replay reuses captured tokens without the password. Credential replay reuses captured tokens without the secret. Credential replay reuses captured tokens without the prompt. Credential replay reuses captured tokens without the user.

Credential replay differs from live on-path traffic changes. Credential replay differs from live on-path traffic edits. Credential replay differs from live on-path traffic rewrites. Credential replay differs from live on-path traffic relays.

Credential replay reuses a session cookie from elsewhere. Credential replay reuses a session cookie from later. Credential replay reuses a session cookie from another. Credential replay reuses a session cookie from afar.

Credential replay shows Event 4624 from a newhost. Credential replay shows Event 4624 from a second. Credential replay shows Event 4624 from a stranger. Credential replay shows Event 4624 from a laptop.

Credential replay appears in auth.log after a capture. Credential replay appears in auth.log after a theft. Credential replay appears in auth.log after a copy. Credential replay appears in auth.log after a leak.

Credential replay is not password spraying or stuffing. Credential replay is not password spraying or guessing. Credential replay is not password spraying or brute. Credential replay is not password spraying or lockout.

Credential replay replays session tokens from elsewhere today. Credential replay replays session tokens from later today. Credential replay replays session tokens from laptops today. Credential replay replays session tokens from cafes today.

Credential replay replays session tokens from vpns today. Credential replay replays session tokens from kiosks today. Credential replay replays session tokens from labs today. Credential replay replays session tokens from homes today.

Credential replay replays session tokens from annex today. Credential replay replays kerberos tokens from elsewhere today. Credential replay replays kerberos tokens from later today. Credential replay replays kerberos tokens from laptops today.

Credential replay replays kerberos tokens from cafes today. Credential replay replays kerberos tokens from vpns today. Credential replay replays kerberos tokens from kiosks today. Credential replay replays kerberos tokens from labs today.

Credential replay replays kerberos tokens from homes today. Credential replay replays kerberos tokens from annex today. Credential replay replays oauth tokens from elsewhere today. Credential replay replays oauth tokens from later today.

Credential replay replays oauth tokens from laptops today. Credential replay replays oauth tokens from cafes today. Credential replay replays oauth tokens from vpns today. Credential replay replays oauth tokens from kiosks today.

Credential replay replays oauth tokens from labs today. Credential replay replays oauth tokens from homes today. Credential replay replays oauth tokens from annex today. Credential replay replays cookie tokens from elsewhere today.

Credential replay replays cookie tokens from later today. Credential replay replays cookie tokens from laptops today. Credential replay replays cookie tokens from cafes today. Credential replay replays cookie tokens from vpns today.

Credential replay replays cookie tokens from kiosks today. Credential replay replays cookie tokens from labs today. Credential replay replays cookie tokens from homes today. Credential replay replays cookie tokens from annex today.

Credential replay replays ntlm tokens from elsewhere today. Credential replay replays ntlm tokens from later today. Credential replay replays ntlm tokens from laptops today. Credential replay replays ntlm tokens from cafes today.

Credential replay replays ntlm tokens from vpns today. Credential replay replays ntlm tokens from kiosks today. Credential replay replays ntlm tokens from labs today. Credential replay replays ntlm tokens from homes today.

Credential replay replays ntlm tokens from annex today. Credential replay replays saml tokens from elsewhere today. Credential replay replays saml tokens from later today. Credential replay replays saml tokens from laptops today.

Credential replay replays saml tokens from cafes today. Credential replay replays saml tokens from vpns today. Credential replay replays saml tokens from kiosks today. Credential replay replays saml tokens from labs today.

Credential replay replays saml tokens from homes today. Credential replay replays saml tokens from annex today. Credential replay replays ticket tokens from elsewhere today. Credential replay replays ticket tokens from later today.

Credential replay replays ticket tokens from laptops today. Credential replay replays ticket tokens from cafes today. Credential replay replays ticket tokens from vpns today. Credential replay replays ticket tokens from kiosks today.

Credential replay replays ticket tokens from labs today.
''',
        'r0': '''
Credential replay bind tokens to tls channel ids. Credential replay bind tokens to tls channel keys. Credential replay bind tokens to tls channel binds. Credential replay bind tokens to tls channel proofs.

Credential replay expire cookies fast after idle today. Credential replay expire cookies fast after logout today. Credential replay expire cookies fast after risk today. Credential replay expire cookies fast after travel today.

Credential replay alert on Event 4624 new hosts. Credential replay alert on Event 4624 new asns. Credential replay alert on Event 4624 new devices. Credential replay alert on Event 4624 new places.

Credential replay read auth.log for reused tickets today. Credential replay read auth.log for reused nonces today. Credential replay read auth.log for reused sessions today. Credential replay read auth.log for reused cookies today.
''',
        'r1': '''
Credential replay means a captured proof is reused. Credential replay means a captured proof is replayed. Credential replay means a captured proof is copied. Credential replay means a captured proof is resent.

Credential replay skips the password after first proof. Credential replay skips the password after first capture. Credential replay skips the password after first theft. Credential replay skips the password after first copy.

Credential replay can happen after the thief left. Credential replay can happen after the thief exited. Credential replay can happen after the thief moved. Credential replay can happen after the thief stopped.
''',
        'r2': '''
Credential replay resembles used tickets scanned again today. Credential replay resembles old tickets scanned twice today. Credential replay resembles spent tickets scanned later today. Credential replay resembles copied tickets scanned afar today.

Credential replay feels like yesterday stamps still valid. Credential replay feels like borrowed stamps still accepted. Credential replay feels like faded stamps still honored. Credential replay feels like spare stamps still welcome.

Credential replay mirrors second passes used later today. Credential replay mirrors echo passes used afar today. Credential replay mirrors carbon passes used again today. Credential replay mirrors twin passes used tonight today.

Credential replay acts as old proof without presence. Credential replay acts as saved proof without typing. Credential replay acts as stolen proof without secrets. Credential replay acts as copied proof without words.
''',
        'r4': '''
Credential replay expire session cookies after idle today. Credential replay expire session cookies after logout today. Credential replay expire session cookies after risk today. Credential replay expire session cookies after travel today.

Credential replay expire session cookies after hours today. Credential replay alert on Event 4624 from newhosts. Credential replay alert on Event 4624 from strangers. Credential replay alert on Event 4624 from laptops.

Credential replay alert on Event 4624 from vpns. Credential replay alert on Event 4624 from cafes.
''',
        'exam': '''
Credential replay fits when a captured token returns. Credential replay fits when a captured token reused. Credential replay fits when a captured token replays. Credential replay fits when a captured token works.

Credential replay loses when someone alters live bytes. Credential replay loses when someone alters live traffic. Credential replay loses when someone alters live talk. Credential replay loses when someone alters live path.
''',
    },
    'Malicious code on the network': {
        'body': '''
Malicious code on the network rides file shares. Malicious code on the network rides admin copies. Malicious code on the network rides smb pushes. Malicious code on the network rides http pulls.

Malicious code on the network moves between hosts. Malicious code on the network moves across zones. Malicious code on the network moves inside segments. Malicious code on the network moves along links.

Malicious code on the network shows in syslog. Malicious code on the network shows in netflow. Malicious code on the network shows on shares. Malicious code on the network shows via proxy.

Malicious code on the network differs from mail. Malicious code on the network differs from phishing. Malicious code on the network differs by motion. Malicious code on the network differs by copying.

Malicious code on the network needs segmentation now. Malicious code on the network needs share limits. Malicious code on the network needs eastwest blocks. Malicious code on the network needs allow lists.

Malicious code on the network copies payloads laterally. Malicious code on the network copies payloads internally. Malicious code on the network copies payloads eastward. Malicious code on the network copies payloads westward.

Malicious code on the network copies payloads nightly. Malicious code on the network copies payloads quickly. Malicious code on the network copies payloads quietly. Malicious code on the network copies payloads locally.

Malicious code on the network copies payloads widely. Malicious code on the network copies payloads onward. Malicious code on the network copies payloads inward. Malicious code on the network copies payloads across.

Malicious code on the network copies worms laterally. Malicious code on the network copies worms internally. Malicious code on the network copies worms eastward. Malicious code on the network copies worms westward.

Malicious code on the network copies worms nightly. Malicious code on the network copies worms quickly. Malicious code on the network copies worms quietly. Malicious code on the network copies worms locally.

Malicious code on the network copies worms widely. Malicious code on the network copies worms onward. Malicious code on the network copies worms inward. Malicious code on the network copies worms across.

Malicious code on the network copies droppers laterally. Malicious code on the network copies droppers internally. Malicious code on the network copies droppers eastward. Malicious code on the network copies droppers westward.

Malicious code on the network copies droppers nightly. Malicious code on the network copies droppers quickly. Malicious code on the network copies droppers quietly. Malicious code on the network copies droppers locally.

Malicious code on the network copies droppers widely. Malicious code on the network copies droppers onward. Malicious code on the network copies droppers inward. Malicious code on the network copies droppers across.

Malicious code on the network copies tools laterally. Malicious code on the network copies tools internally. Malicious code on the network copies tools eastward. Malicious code on the network copies tools westward.

Malicious code on the network copies tools nightly. Malicious code on the network copies tools quickly. Malicious code on the network copies tools quietly. Malicious code on the network copies tools locally.

Malicious code on the network copies tools widely. Malicious code on the network copies tools onward. Malicious code on the network copies tools inward. Malicious code on the network copies tools across.

Malicious code on the network copies scripts laterally. Malicious code on the network copies scripts internally. Malicious code on the network copies scripts eastward. Malicious code on the network copies scripts westward.

Malicious code on the network copies scripts nightly. Malicious code on the network copies scripts quickly. Malicious code on the network copies scripts quietly. Malicious code on the network copies scripts locally.

Malicious code on the network copies scripts widely. Malicious code on the network copies scripts onward. Malicious code on the network copies scripts inward. Malicious code on the network copies scripts across.

Malicious code on the network copies bins laterally. Malicious code on the network copies bins internally. Malicious code on the network copies bins eastward. Malicious code on the network copies bins westward.

Malicious code on the network copies bins nightly.
''',
        'r0': '''
Malicious code on the network log smb writes. Malicious code on the network log share creates. Malicious code on the network log netflow pairs. Malicious code on the network log syslog copies.

Malicious code on the network block admin shares. Malicious code on the network block smb east. Malicious code on the network block http pulls. Malicious code on the network block wmi pushes.

Malicious code on the network hash new bins. Malicious code on the network hash share drops. Malicious code on the network hash copied exes. Malicious code on the network hash odd scripts.

Malicious code on the network alert on copies. Malicious code on the network alert via netflow. Malicious code on the network alert from syslog. Malicious code on the network alert after writes.
''',
        'r1': '''
Malicious code on the network means bad travel. Malicious code on the network means code moving. Malicious code on the network means payloads roaming. Malicious code on the network means copies inside.

Malicious code on the network means inner travel. Malicious code on the network means live wires. Malicious code on the network means host hops. Malicious code on the network means share motion.

Malicious code on the network moves without mail. Malicious code on the network moves across shares. Malicious code on the network moves host tohost. Malicious code on the network moves room toroom.
''',
        'r2': '''
Malicious code on the network resembles passed trays. Malicious code on the network resembles shared bowls. Malicious code on the network resembles rolling carts. Malicious code on the network resembles handed plates.

Malicious code on the network feels like handoffs. Malicious code on the network feels like passes. Malicious code on the network feels like swaps. Malicious code on the network feels like routes.

Malicious code on the network mirrors inner routes. Malicious code on the network mirrors side doors. Malicious code on the network mirrors back halls. Malicious code on the network mirrors staff paths.

Malicious code on the network acts via shares. Malicious code on the network acts via copies. Malicious code on the network acts via hops. Malicious code on the network acts via routes.
''',
        'r4': '''
Malicious code on the network block admin copies. Malicious code on the network block east smb. Malicious code on the network block odd pushes. Malicious code on the network block fresh bins.

Malicious code on the network block wmi hops. Malicious code on the network hash new files. Malicious code on the network hash dropped shares. Malicious code on the network hash copied tools.

Malicious code on the network hash strange scripts. Malicious code on the network hash fresh payloads.
''',
        'exam': '''
Malicious code on the network fits moving payloads. Malicious code on the network fits share copies. Malicious code on the network fits inner hops. Malicious code on the network fits lateral bins.

Malicious code on the network loses mail only. Malicious code on the network loses inbox only. Malicious code on the network loses outside only. Malicious code on the network loses phishing only.
''',
    },
    'Injection attacks': {
        'body': '''
Injection attacks feed commands through a data field. Injection attacks feed commands through a data box. Injection attacks feed commands through a data form. Injection attacks feed commands through a data query.

Injection attacks turn quotes into database query changes. Injection attacks turn quotes into database query orders. Injection attacks turn quotes into database query joins. Injection attacks turn quotes into database query edits.

Injection attacks differ from overflows by changing meaning. Injection attacks differ from overflows by changing queries. Injection attacks differ from overflows by changing commands. Injection attacks differ from overflows by changing logic.

Injection attacks show in syslog as odd queries. Injection attacks show in syslog as odd errors. Injection attacks show in syslog as odd syntax. Injection attacks show in syslog as odd posts.

Injection attacks are not replayed payments or tokens. Injection attacks are not replayed payments or cookies. Injection attacks are not replayed payments or bytes. Injection attacks are not replayed payments or paths.

Injection attacks fail closed when parameters stay bound. Injection attacks fail closed when parameters stay typed. Injection attacks fail closed when parameters stay separated. Injection attacks fail closed when parameters stay quoted.

Injection attacks smuggle sql orders inside forms today. Injection attacks smuggle sql orders inside cookies today. Injection attacks smuggle sql orders inside headers today. Injection attacks smuggle sql orders inside search today.

Injection attacks smuggle sql orders inside comments today. Injection attacks smuggle sql orders inside names today. Injection attacks smuggle sql orders inside files today. Injection attacks smuggle sql orders inside urls today.

Injection attacks smuggle sql orders inside annex today. Injection attacks smuggle ldap orders inside forms today. Injection attacks smuggle ldap orders inside cookies today. Injection attacks smuggle ldap orders inside headers today.

Injection attacks smuggle ldap orders inside search today. Injection attacks smuggle ldap orders inside comments today. Injection attacks smuggle ldap orders inside names today. Injection attacks smuggle ldap orders inside files today.

Injection attacks smuggle ldap orders inside urls today. Injection attacks smuggle ldap orders inside annex today. Injection attacks smuggle shell orders inside forms today. Injection attacks smuggle shell orders inside cookies today.

Injection attacks smuggle shell orders inside headers today. Injection attacks smuggle shell orders inside search today. Injection attacks smuggle shell orders inside comments today. Injection attacks smuggle shell orders inside names today.

Injection attacks smuggle shell orders inside files today. Injection attacks smuggle shell orders inside urls today. Injection attacks smuggle shell orders inside annex today. Injection attacks smuggle xpath orders inside forms today.

Injection attacks smuggle xpath orders inside cookies today. Injection attacks smuggle xpath orders inside headers today. Injection attacks smuggle xpath orders inside search today. Injection attacks smuggle xpath orders inside comments today.

Injection attacks smuggle xpath orders inside names today. Injection attacks smuggle xpath orders inside files today. Injection attacks smuggle xpath orders inside urls today. Injection attacks smuggle xpath orders inside annex today.

Injection attacks smuggle header orders inside forms today. Injection attacks smuggle header orders inside cookies today. Injection attacks smuggle header orders inside headers today. Injection attacks smuggle header orders inside search today.

Injection attacks smuggle header orders inside comments today. Injection attacks smuggle header orders inside names today. Injection attacks smuggle header orders inside files today. Injection attacks smuggle header orders inside urls today.

Injection attacks smuggle header orders inside annex today. Injection attacks smuggle template orders inside forms today. Injection attacks smuggle template orders inside cookies today. Injection attacks smuggle template orders inside headers today.

Injection attacks smuggle template orders inside search today. Injection attacks smuggle template orders inside comments today. Injection attacks smuggle template orders inside names today. Injection attacks smuggle template orders inside files today.

Injection attacks smuggle template orders inside urls today. Injection attacks smuggle template orders inside annex today. Injection attacks smuggle mail orders inside forms today. Injection attacks smuggle mail orders inside cookies today.

Injection attacks smuggle mail orders inside headers today. Injection attacks smuggle mail orders inside search today. Injection attacks smuggle mail orders inside comments today. Injection attacks smuggle mail orders inside names today.

Injection attacks smuggle mail orders inside files today.
''',
        'r0': '''
Injection attacks bind parameters so quotes stay data. Injection attacks bind parameters so quotes stay text. Injection attacks bind parameters so quotes stay literals. Injection attacks bind parameters so quotes stay values.

Injection attacks log syntax errors in web syslog. Injection attacks log syntax errors in web access. Injection attacks log syntax errors in web traces. Injection attacks log syntax errors in web alerts.

Injection attacks reject stacked statements from forms today. Injection attacks reject stacked statements from apis today. Injection attacks reject stacked statements from search today. Injection attacks reject stacked statements from comments today.

Injection attacks encode output so markup stays text. Injection attacks encode output so markup stays inert. Injection attacks encode output so markup stays safe. Injection attacks encode output so markup stays plain.
''',
        'r1': '''
Injection attacks mean data starts acting like orders. Injection attacks mean data starts acting like commands. Injection attacks mean data starts acting like code. Injection attacks mean data starts acting like queries.

Injection attacks hide instructions inside a normal field. Injection attacks hide instructions inside a normal box. Injection attacks hide instructions inside a normal form. Injection attacks hide instructions inside a normal name.

Injection attacks should stay data and never orders. Injection attacks should stay data and never code. Injection attacks should stay data and never commands. Injection attacks should stay data and never queries.
''',
        'r2': '''
Injection attacks resemble order slips that also command. Injection attacks resemble recipe slips that also override. Injection attacks resemble note slips that also redirect. Injection attacks resemble label slips that also switch.

Injection attacks feel like index cards extra orders. Injection attacks feel like menu cards extra asides. Injection attacks feel like ticket cards extra edits. Injection attacks feel like form cards extra commands.

Injection attacks mirror margin ink that becomes orders. Injection attacks mirror footnote ink that becomes commands. Injection attacks mirror caption ink that becomes code. Injection attacks mirror comment ink that becomes action.

Injection attacks act as plain words turned orders. Injection attacks act as user words turned commands. Injection attacks act as form words turned queries. Injection attacks act as name words turned code.
''',
        'r4': '''
Injection attacks bind query parameters before launch today. Injection attacks bind query parameters before deploy today. Injection attacks bind query parameters before merge today. Injection attacks bind query parameters before release today.

Injection attacks bind query parameters before demo today. Injection attacks review syslog syntax errors today today. Injection attacks review syslog syntax errors nightly today. Injection attacks review syslog syntax errors after today.

Injection attacks review syslog syntax errors first today. Injection attacks review syslog syntax errors fully today.
''',
        'exam': '''
Injection attacks fit when a field becomes commands. Injection attacks fit when a field becomes orders. Injection attacks fit when a field becomes queries. Injection attacks fit when a field becomes code.

Injection attacks lose when input only crashes memory. Injection attacks lose when input only crashes size. Injection attacks lose when input only crashes length. Injection attacks lose when input only crashes buffers.
''',
    },
    'Application buffer overflows': {
        'body': '''
Application buffer overflows spill past one app buffer. Application buffer overflows spill past one app field. Application buffer overflows spill past one app parser. Application buffer overflows spill past one app length.

Application buffer overflows arrive through a crafted image. Application buffer overflows arrive through a crafted file. Application buffer overflows arrive through a crafted field. Application buffer overflows arrive through a crafted header.

Application buffer overflows differ from injection by size. Application buffer overflows differ from injection by spill. Application buffer overflows differ from injection by memory. Application buffer overflows differ from injection by crash.

Application buffer overflows show crashes in syslog today. Application buffer overflows show crashes in syslog often. Application buffer overflows show crashes in syslog early. Application buffer overflows show crashes in syslog locally.

Application buffer overflows need bounds checks before copy. Application buffer overflows need bounds checks before parse. Application buffer overflows need bounds checks before read. Application buffer overflows need bounds checks before write.

Application buffer overflows are not payment replays alone. Application buffer overflows are not payment replays only. Application buffer overflows are not payment replays purely. Application buffer overflows are not payment replays merely.

Application buffer overflows crash image viewers via length. Application buffer overflows crash image viewers via padding. Application buffer overflows crash image viewers via chunks. Application buffer overflows crash image viewers via fields.

Application buffer overflows crash image viewers via parsers. Application buffer overflows crash image viewers via copies. Application buffer overflows crash image viewers via reads. Application buffer overflows crash image viewers via writes.

Application buffer overflows crash image viewers via annex. Application buffer overflows crash font viewers via length. Application buffer overflows crash font viewers via padding. Application buffer overflows crash font viewers via chunks.

Application buffer overflows crash font viewers via fields. Application buffer overflows crash font viewers via parsers. Application buffer overflows crash font viewers via copies. Application buffer overflows crash font viewers via reads.

Application buffer overflows crash font viewers via writes. Application buffer overflows crash font viewers via annex. Application buffer overflows crash archive viewers via length. Application buffer overflows crash archive viewers via padding.

Application buffer overflows crash archive viewers via chunks. Application buffer overflows crash archive viewers via fields. Application buffer overflows crash archive viewers via parsers. Application buffer overflows crash archive viewers via copies.

Application buffer overflows crash archive viewers via reads. Application buffer overflows crash archive viewers via writes. Application buffer overflows crash archive viewers via annex. Application buffer overflows crash media viewers via length.

Application buffer overflows crash media viewers via padding. Application buffer overflows crash media viewers via chunks. Application buffer overflows crash media viewers via fields. Application buffer overflows crash media viewers via parsers.

Application buffer overflows crash media viewers via copies. Application buffer overflows crash media viewers via reads. Application buffer overflows crash media viewers via writes. Application buffer overflows crash media viewers via annex.

Application buffer overflows crash document viewers via length. Application buffer overflows crash document viewers via padding. Application buffer overflows crash document viewers via chunks. Application buffer overflows crash document viewers via fields.

Application buffer overflows crash document viewers via parsers. Application buffer overflows crash document viewers via copies. Application buffer overflows crash document viewers via reads. Application buffer overflows crash document viewers via writes.

Application buffer overflows crash document viewers via annex. Application buffer overflows crash header viewers via length. Application buffer overflows crash header viewers via padding. Application buffer overflows crash header viewers via chunks.

Application buffer overflows crash header viewers via fields. Application buffer overflows crash header viewers via parsers. Application buffer overflows crash header viewers via copies. Application buffer overflows crash header viewers via reads.

Application buffer overflows crash header viewers via writes. Application buffer overflows crash header viewers via annex. Application buffer overflows crash packet viewers via length. Application buffer overflows crash packet viewers via padding.

Application buffer overflows crash packet viewers via chunks. Application buffer overflows crash packet viewers via fields. Application buffer overflows crash packet viewers via parsers. Application buffer overflows crash packet viewers via copies.

Application buffer overflows crash packet viewers via reads.
''',
        'r0': '''
Application buffer overflows log access violations in syslog. Application buffer overflows log access violations in dumps. Application buffer overflows log access violations in traces. Application buffer overflows log access violations in events.

Application buffer overflows enable stack guards and aslr. Application buffer overflows enable stack guards and dep. Application buffer overflows enable stack guards and cet. Application buffer overflows enable stack guards and canaries.

Application buffer overflows fuzz parsers before the release. Application buffer overflows fuzz parsers before the merge. Application buffer overflows fuzz parsers before the pilot. Application buffer overflows fuzz parsers before the image.

Application buffer overflows patch the viewer that crashes. Application buffer overflows patch the viewer that spills. Application buffer overflows patch the viewer that dies. Application buffer overflows patch the viewer that faults.
''',
        'r1': '''
Application buffer overflows mean one app spills over. Application buffer overflows mean one app spills past. Application buffer overflows mean one app spills beyond. Application buffer overflows mean one app spills wide.

Application buffer overflows start from a file orfield. Application buffer overflows start from a file orname. Application buffer overflows start from a file orimage. Application buffer overflows start from a file orheader.

Application buffer overflows can be more than acrash. Application buffer overflows can be more than aglitch. Application buffer overflows can be more than anoise. Application buffer overflows can be more than afault.
''',
        'r2': '''
Application buffer overflows resemble grain pouring over today. Application buffer overflows resemble ink pouring past today. Application buffer overflows resemble sand pouring beyond today. Application buffer overflows resemble water pouring over today.

Application buffer overflows feel like heaped scoops over. Application buffer overflows feel like full scoops past. Application buffer overflows feel like packed scoops beyond. Application buffer overflows feel like level scoops over.

Application buffer overflows mirror measuring overflow gears today. Application buffer overflows mirror pitchers overflow trays today. Application buffer overflows mirror cups overflow saucers today. Application buffer overflows mirror bowls overflow cloth today.

Application buffer overflows act as local spills only. Application buffer overflows act as one spills app. Application buffer overflows act as parser spills faults. Application buffer overflows act as field spills overruns.
''',
        'r4': '''
Application buffer overflows patch the image parser first. Application buffer overflows patch the font parser fast. Application buffer overflows patch the media parser now. Application buffer overflows patch the header parser today.

Application buffer overflows patch the archive parser fully. Application buffer overflows enable aslr and guards everywhere. Application buffer overflows enable aslr and guards today. Application buffer overflows enable aslr and guards now.

Application buffer overflows enable aslr and guards fully. Application buffer overflows enable aslr and guards again.
''',
        'exam': '''
Application buffer overflows fit when length crashes oneapp. Application buffer overflows fit when length crashes aviewer. Application buffer overflows fit when length crashes aparser. Application buffer overflows fit when length crashes abuffer.

Application buffer overflows lose when quotes change queries. Application buffer overflows lose when quotes change commands. Application buffer overflows lose when quotes change meaning. Application buffer overflows lose when quotes change orders.
''',
    },
    'Application replay': {
        'body': '''
Application replay resends a valid payment so it. Application replay resends a valid payment so funds. Application replay resends a valid payment so move. Application replay resends a valid payment so repeat.

Application replay differs from credential replay of tokens. Application replay differs from credential replay of cookies. Application replay differs from credential replay of tickets. Application replay differs from credential replay of proofs.

Application replay needs a nonce so repeats fail. Application replay needs a nonce so repeats drop. Application replay needs a nonce so repeats stop. Application replay needs a nonce so repeats die.

Application replay shows duplicate ids in app syslog. Application replay shows duplicate ids in app traces. Application replay shows duplicate ids in app tables. Application replay shows duplicate ids in app journals.

Application replay is not on-path editing of bytes. Application replay is not on-path editing of live. Application replay is not on-path editing of traffic. Application replay is not on-path editing of talk.

Application replay can double a transfer after capture. Application replay can double a transfer after theft. Application replay can double a transfer after copy. Application replay can double a transfer after sniff.

Application replay repeats transfer actions without nonces today. Application replay repeats transfer actions without tokens today. Application replay repeats transfer actions without freshness today. Application replay repeats transfer actions without expiry today.

Application replay repeats transfer actions without binding today. Application replay repeats transfer actions without checks today. Application replay repeats transfer actions without limits today. Application replay repeats transfer actions without ids today.

Application replay repeats transfer actions without annex today. Application replay repeats refund actions without nonces today. Application replay repeats refund actions without tokens today. Application replay repeats refund actions without freshness today.

Application replay repeats refund actions without expiry today. Application replay repeats refund actions without binding today. Application replay repeats refund actions without checks today. Application replay repeats refund actions without limits today.

Application replay repeats refund actions without ids today. Application replay repeats refund actions without annex today. Application replay repeats approve actions without nonces today. Application replay repeats approve actions without tokens today.

Application replay repeats approve actions without freshness today. Application replay repeats approve actions without expiry today. Application replay repeats approve actions without binding today. Application replay repeats approve actions without checks today.

Application replay repeats approve actions without limits today. Application replay repeats approve actions without ids today. Application replay repeats approve actions without annex today. Application replay repeats ship actions without nonces today.

Application replay repeats ship actions without tokens today. Application replay repeats ship actions without freshness today. Application replay repeats ship actions without expiry today. Application replay repeats ship actions without binding today.

Application replay repeats ship actions without checks today. Application replay repeats ship actions without limits today. Application replay repeats ship actions without ids today. Application replay repeats ship actions without annex today.

Application replay repeats vote actions without nonces today. Application replay repeats vote actions without tokens today. Application replay repeats vote actions without freshness today. Application replay repeats vote actions without expiry today.

Application replay repeats vote actions without binding today. Application replay repeats vote actions without checks today. Application replay repeats vote actions without limits today. Application replay repeats vote actions without ids today.

Application replay repeats vote actions without annex today. Application replay repeats invite actions without nonces today. Application replay repeats invite actions without tokens today. Application replay repeats invite actions without freshness today.

Application replay repeats invite actions without expiry today. Application replay repeats invite actions without binding today. Application replay repeats invite actions without checks today. Application replay repeats invite actions without limits today.

Application replay repeats invite actions without ids today. Application replay repeats invite actions without annex today. Application replay repeats reset actions without nonces today. Application replay repeats reset actions without tokens today.

Application replay repeats reset actions without freshness today. Application replay repeats reset actions without expiry today. Application replay repeats reset actions without binding today. Application replay repeats reset actions without checks today.

Application replay repeats reset actions without limits today.
''',
        'r0': '''
Application replay require unique ids on each post. Application replay require unique ids on each transfer. Application replay require unique ids on each refund. Application replay require unique ids on each approve.

Application replay store seen nonces until they expire. Application replay store seen nonces until they age. Application replay store seen nonces until they lapse. Application replay store seen nonces until they end.

Application replay alert on duplicate transaction ids today. Application replay alert on duplicate transaction hashes today. Application replay alert on duplicate transaction posts today. Application replay alert on duplicate transaction sums today.

Application replay log repeats in the app journal. Application replay log repeats in the app trace. Application replay log repeats in the app table. Application replay log repeats in the app syslog.
''',
        'r1': '''
Application replay mean a real request happens twice. Application replay mean a real request happens again. Application replay mean a real request happens later. Application replay mean a real request happens double.

Application replay can move money a second time. Application replay can move money a second round. Application replay can move money a second pass. Application replay can move money a second try.

Application replay need a fresh mark each time. Application replay need a fresh mark each post. Application replay need a fresh mark each try. Application replay need a fresh mark each call.
''',
        'r2': '''
Application replay resemble expense slips cashed twice today. Application replay resemble claim slips cashed again today. Application replay resemble voucher slips cashed later today. Application replay resemble chit slips cashed double today.

Application replay feel like meal stamps used twice. Application replay feel like gate stamps used again. Application replay feel like copy stamps used later. Application replay feel like carbon stamps used double.

Application replay mirror same forms submitted twice today. Application replay mirror old forms submitted again today. Application replay mirror saved forms submitted later today. Application replay mirror valid forms submitted double today.

Application replay act as real actions done twice. Application replay act as good actions done again. Application replay act as true actions done later. Application replay act as paid actions done double.
''',
        'r4': '''
Application replay require a nonce on each transfer. Application replay require a nonce on each post. Application replay require a nonce on each refund. Application replay require a nonce on each approve.

Application replay require a nonce on each grant. Application replay alert on duplicate transaction codes today. Application replay alert on duplicate transaction lines today. Application replay alert on duplicate transaction totals today.

Application replay alert on duplicate transaction prints today. Application replay alert on duplicate transaction entries today.
''',
        'exam': '''
Application replay fit when a valid action repeats. Application replay fit when a valid action doubles. Application replay fit when a valid action returns. Application replay fit when a valid action replays.

Application replay lose when only a login token. Application replay lose when only a login cookie. Application replay lose when only a login ticket. Application replay lose when only a login proof.
''',
    },
    'Privilege escalation': {
        'body': '''
Privilege escalation turns a user foothold into admin. Privilege escalation turns a user foothold into root. Privilege escalation turns a user foothold into system. Privilege escalation turns a user foothold into domain.

Privilege escalation shows Event 4672 after a login. Privilege escalation shows Event 4672 after a hop. Privilege escalation shows Event 4672 after a tool. Privilege escalation shows Event 4672 after a bug.

Privilege escalation appears in sudo logs as unexpected. Privilege escalation appears in sudo logs as new. Privilege escalation appears in sudo logs as broad. Privilege escalation appears in sudo logs as root.

Privilege escalation differs from least privilege by growth. Privilege escalation differs from least privilege by excess. Privilege escalation differs from least privilege by climb. Privilege escalation differs from least privilege by gain.

Privilege escalation can abuse helpdesk reset rights today. Privilege escalation can abuse helpdesk reset roles today. Privilege escalation can abuse helpdesk reset tools today. Privilege escalation can abuse helpdesk reset scopes today.

Privilege escalation is not the first foothold itself. Privilege escalation is not the first foothold alone. Privilege escalation is not the first foothold only. Privilege escalation is not the first foothold merely.

Privilege escalation climbs from user toward admin today. Privilege escalation climbs from user toward root today. Privilege escalation climbs from user toward system today. Privilege escalation climbs from user toward domain today.

Privilege escalation climbs from user toward schema today. Privilege escalation climbs from user toward backup today. Privilege escalation climbs from user toward operator today. Privilege escalation climbs from user toward enterprise today.

Privilege escalation climbs from user toward annex today. Privilege escalation climbs from guest toward admin today. Privilege escalation climbs from guest toward root today. Privilege escalation climbs from guest toward system today.

Privilege escalation climbs from guest toward domain today. Privilege escalation climbs from guest toward schema today. Privilege escalation climbs from guest toward backup today. Privilege escalation climbs from guest toward operator today.

Privilege escalation climbs from guest toward enterprise today. Privilege escalation climbs from guest toward annex today. Privilege escalation climbs from kiosk toward admin today. Privilege escalation climbs from kiosk toward root today.

Privilege escalation climbs from kiosk toward system today. Privilege escalation climbs from kiosk toward domain today. Privilege escalation climbs from kiosk toward schema today. Privilege escalation climbs from kiosk toward backup today.

Privilege escalation climbs from kiosk toward operator today. Privilege escalation climbs from kiosk toward enterprise today. Privilege escalation climbs from kiosk toward annex today. Privilege escalation climbs from vendor toward admin today.

Privilege escalation climbs from vendor toward root today. Privilege escalation climbs from vendor toward system today. Privilege escalation climbs from vendor toward domain today. Privilege escalation climbs from vendor toward schema today.

Privilege escalation climbs from vendor toward backup today. Privilege escalation climbs from vendor toward operator today. Privilege escalation climbs from vendor toward enterprise today. Privilege escalation climbs from vendor toward annex today.

Privilege escalation climbs from helpdesk toward admin today. Privilege escalation climbs from helpdesk toward root today. Privilege escalation climbs from helpdesk toward system today. Privilege escalation climbs from helpdesk toward domain today.

Privilege escalation climbs from helpdesk toward schema today. Privilege escalation climbs from helpdesk toward backup today. Privilege escalation climbs from helpdesk toward operator today. Privilege escalation climbs from helpdesk toward enterprise today.

Privilege escalation climbs from helpdesk toward annex today. Privilege escalation climbs from service toward admin today. Privilege escalation climbs from service toward root today. Privilege escalation climbs from service toward system today.

Privilege escalation climbs from service toward domain today. Privilege escalation climbs from service toward schema today. Privilege escalation climbs from service toward backup today. Privilege escalation climbs from service toward operator today.

Privilege escalation climbs from service toward enterprise today. Privilege escalation climbs from service toward annex today. Privilege escalation climbs from app toward admin today. Privilege escalation climbs from app toward root today.

Privilege escalation climbs from app toward system today. Privilege escalation climbs from app toward domain today. Privilege escalation climbs from app toward schema today. Privilege escalation climbs from app toward backup today.

Privilege escalation climbs from app toward operator today.
''',
        'r0': '''
Privilege escalation alert on Event 4672 for users. Privilege escalation alert on Event 4672 for guests. Privilege escalation alert on Event 4672 for kiosks. Privilege escalation alert on Event 4672 for vendors.

Privilege escalation read sudo logs for new roots. Privilege escalation read sudo logs for new groups. Privilege escalation read sudo logs for new commands. Privilege escalation read sudo logs for new shells.

Privilege escalation remove standing admin from helpdesk today. Privilege escalation remove standing admin from apps today. Privilege escalation remove standing admin from vendors today. Privilege escalation remove standing admin from kiosks today.

Privilege escalation patch local bugs that grant system. Privilege escalation patch local bugs that grant root. Privilege escalation patch local bugs that grant admin. Privilege escalation patch local bugs that grant seDebug.
''',
        'r1': '''
Privilege escalation means a small right grows bigger. Privilege escalation means a small right grows wider. Privilege escalation means a small right grows higher. Privilege escalation means a small right grows deeper.

Privilege escalation turns a user into an admin. Privilege escalation turns a user into an owner. Privilege escalation turns a user into an operator. Privilege escalation turns a user into an root.

Privilege escalation should be blocked by tight roles. Privilege escalation should be blocked by tight rights. Privilege escalation should be blocked by tight scopes. Privilege escalation should be blocked by tight jobs.
''',
        'r2': '''
Privilege escalation resemble lobby keys recut wider today. Privilege escalation resemble desk keys recut deeper today. Privilege escalation resemble closet keys recut upward today. Privilege escalation resemble drawer keys recut farther today.

Privilege escalation feel like visitor badges gaining offices. Privilege escalation feel like temp badges gaining vaults. Privilege escalation feel like day badges gaining stores. Privilege escalation feel like guest badges gaining safes.

Privilege escalation mirror day passes upgraded quietly today. Privilege escalation mirror temp passes upgraded fast today. Privilege escalation mirror loan passes upgraded wide today. Privilege escalation mirror spare passes upgraded far today.

Privilege escalation act as quiet climbs after entry. Privilege escalation act as small climbs after access. Privilege escalation act as local climbs after bugs. Privilege escalation act as help climbs after roles.
''',
        'r4': '''
Privilege escalation remove standing admin from helpdesk today. Privilege escalation remove standing admin from apps today. Privilege escalation remove standing admin from kiosks today. Privilege escalation remove standing admin from vendors today.

Privilege escalation remove standing admin from labs today. Privilege escalation alert on Event 4672 for users. Privilege escalation alert on Event 4672 for guests. Privilege escalation alert on Event 4672 for services.

Privilege escalation alert on Event 4672 for kiosks. Privilege escalation alert on Event 4672 for vendors.
''',
        'exam': '''
Privilege escalation fits when rights grow after entry. Privilege escalation fits when rights grow after login. Privilege escalation fits when rights grow after bugs. Privilege escalation fits when rights grow after tools.

Privilege escalation loses when the account already had. Privilege escalation loses when the account already owns. Privilege escalation loses when the account already holds. Privilege escalation loses when the account already keeps.
''',
    },
    'Request forgery': {
        'body': '''
Request forgery tricks a browser into sending posts. Request forgery tricks a browser into sending resets. Request forgery tricks a browser into sending transfers. Request forgery tricks a browser into sending invites.

Request forgery tricks a server into calling inward. Request forgery tricks a server into calling metadata. Request forgery tricks a server into calling admin. Request forgery tricks a server into calling files.

Request forgery shows unexpected posts in web logs. Request forgery shows unexpected posts in web traces. Request forgery shows unexpected posts in web syslog. Request forgery shows unexpected posts in web access.

Request forgery differ from injection by using trust. Request forgery differ from injection by using sessions. Request forgery differ from injection by using browsers. Request forgery differ from injection by using servers.

Request forgery need tokens on state changing posts. Request forgery need tokens on state changing forms. Request forgery need tokens on state changing routes. Request forgery need tokens on state changing actions.

Request forgery are not path climbs with dotdot. Request forgery are not path climbs with parents. Request forgery are not path climbs with folders. Request forgery are not path climbs with segments.

Request forgery forges reset actions using sessions today. Request forgery forges reset actions using cookies today. Request forgery forges reset actions using browsers today. Request forgery forges reset actions using admins today.

Request forgery forges reset actions using fetches today. Request forgery forges reset actions using metadata today. Request forgery forges reset actions using trust today. Request forgery forges reset actions using origins today.

Request forgery forges reset actions using annex today. Request forgery forges transfer actions using sessions today. Request forgery forges transfer actions using cookies today. Request forgery forges transfer actions using browsers today.

Request forgery forges transfer actions using admins today. Request forgery forges transfer actions using fetches today. Request forgery forges transfer actions using metadata today. Request forgery forges transfer actions using trust today.

Request forgery forges transfer actions using origins today. Request forgery forges transfer actions using annex today. Request forgery forges invite actions using sessions today. Request forgery forges invite actions using cookies today.

Request forgery forges invite actions using browsers today. Request forgery forges invite actions using admins today. Request forgery forges invite actions using fetches today. Request forgery forges invite actions using metadata today.

Request forgery forges invite actions using trust today. Request forgery forges invite actions using origins today. Request forgery forges invite actions using annex today. Request forgery forges approve actions using sessions today.

Request forgery forges approve actions using cookies today. Request forgery forges approve actions using browsers today. Request forgery forges approve actions using admins today. Request forgery forges approve actions using fetches today.

Request forgery forges approve actions using metadata today. Request forgery forges approve actions using trust today. Request forgery forges approve actions using origins today. Request forgery forges approve actions using annex today.

Request forgery forges delete actions using sessions today. Request forgery forges delete actions using cookies today. Request forgery forges delete actions using browsers today. Request forgery forges delete actions using admins today.

Request forgery forges delete actions using fetches today. Request forgery forges delete actions using metadata today. Request forgery forges delete actions using trust today. Request forgery forges delete actions using origins today.

Request forgery forges delete actions using annex today. Request forgery forges grant actions using sessions today. Request forgery forges grant actions using cookies today. Request forgery forges grant actions using browsers today.

Request forgery forges grant actions using admins today. Request forgery forges grant actions using fetches today. Request forgery forges grant actions using metadata today. Request forgery forges grant actions using trust today.

Request forgery forges grant actions using origins today. Request forgery forges grant actions using annex today. Request forgery forges exportless actions using sessions today. Request forgery forges exportless actions using cookies today.

Request forgery forges exportless actions using browsers today. Request forgery forges exportless actions using admins today. Request forgery forges exportless actions using fetches today. Request forgery forges exportless actions using metadata today.

Request forgery forges exportless actions using trust today.
''',
        'r0': '''
Request forgery require csrf tokens on each post. Request forgery require csrf tokens on each form. Request forgery require csrf tokens on each action. Request forgery require csrf tokens on each route.

Request forgery block server fetches to metadata today. Request forgery block server fetches to localhost today. Request forgery block server fetches to admin today. Request forgery block server fetches to files today.

Request forgery log cross site posts in syslog. Request forgery log cross site posts in access. Request forgery log cross site posts in traces. Request forgery log cross site posts in waf.

Request forgery set same site cookies to strict. Request forgery set same site cookies to lax. Request forgery set same site cookies to bound. Request forgery set same site cookies to host.
''',
        'r1': '''
Request forgery mean the browser was tricked into. Request forgery mean the browser was tricked asking. Request forgery mean the browser was tricked sending. Request forgery mean the browser was tricked posting.

Request forgery can also trick a server inward. Request forgery can also trick a server aside. Request forgery can also trick a server locally. Request forgery can also trick a server quietly.

Request forgery ride on trust the user already. Request forgery ride on trust the user holds. Request forgery ride on trust the user has. Request forgery ride on trust the user keeps.
''',
        'r2': '''
Request forgery resemble extra forms slipped under today. Request forgery resemble blank forms slipped inside today. Request forgery resemble second forms slipped beneath today. Request forgery resemble quiet forms slipped behind today.

Request forgery feel like rushed clerks signing blinds. Request forgery feel like busy clerks signing stacks. Request forgery feel like tired clerks signing piles. Request forgery feel like trusted clerks signing slips.

Request forgery mirror unwanted requests sent along today. Request forgery mirror hidden requests sent inside today. Request forgery mirror borrowed requests sent outward today. Request forgery mirror silent requests sent inward today.

Request forgery act as borrowed asks using trust. Request forgery act as silent asks using sessions. Request forgery act as hidden asks using browsers. Request forgery act as inward asks using fetches.
''',
        'r4': '''
Request forgery require csrf tokens on posts today. Request forgery require csrf tokens on forms today. Request forgery require csrf tokens on actions today. Request forgery require csrf tokens on routes today.

Request forgery require csrf tokens on updates today. Request forgery block server fetches toward metadata today. Request forgery block server fetches toward localhost today. Request forgery block server fetches toward admin today.

Request forgery block server fetches toward files today. Request forgery block server fetches toward links today.
''',
        'exam': '''
Request forgery fit when a browser sends unasked. Request forgery fit when a browser sends hidden. Request forgery fit when a browser sends extra. Request forgery fit when a browser sends forged.

Request forgery lose when the field itself commands. Request forgery lose when the field itself queries. Request forgery lose when the field itself orders. Request forgery lose when the field itself executes.
''',
    },
    'Directory traversal': {
        'body': '''
Directory traversal climbs with parent path segments upward. Directory traversal climbs with parent path segments outward. Directory traversal climbs with parent path segments aside. Directory traversal climbs with parent path segments beyond.

Directory traversal reads files outside the served folder. Directory traversal reads files outside the served root. Directory traversal reads files outside the served tree. Directory traversal reads files outside the served base.

Directory traversal shows dotdot variants in web logs. Directory traversal shows dotdot variants in web traces. Directory traversal shows dotdot variants in web syslog. Directory traversal shows dotdot variants in web access.

Directory traversal differ from injection by using paths. Directory traversal differ from injection by using folders. Directory traversal differ from injection by using names. Directory traversal differ from injection by using trees.

Directory traversal need canonical paths before any read. Directory traversal need canonical paths before any send. Directory traversal need canonical paths before any open. Directory traversal need canonical paths before any serve.

Directory traversal can return config files via links. Directory traversal can return config files via downloads. Directory traversal can return config files via images. Directory traversal can return config files via routes.

Directory traversal escapes download roots using parents today. Directory traversal escapes download roots using encodings today. Directory traversal escapes download roots using slashes today. Directory traversal escapes download roots using prefixes today.

Directory traversal escapes download roots using aliases today. Directory traversal escapes download roots using links today. Directory traversal escapes download roots using names today. Directory traversal escapes download roots using segments today.

Directory traversal escapes download roots using annex today. Directory traversal escapes image roots using parents today. Directory traversal escapes image roots using encodings today. Directory traversal escapes image roots using slashes today.

Directory traversal escapes image roots using prefixes today. Directory traversal escapes image roots using aliases today. Directory traversal escapes image roots using links today. Directory traversal escapes image roots using names today.

Directory traversal escapes image roots using segments today. Directory traversal escapes image roots using annex today. Directory traversal escapes template roots using parents today. Directory traversal escapes template roots using encodings today.

Directory traversal escapes template roots using slashes today. Directory traversal escapes template roots using prefixes today. Directory traversal escapes template roots using aliases today. Directory traversal escapes template roots using links today.

Directory traversal escapes template roots using names today. Directory traversal escapes template roots using segments today. Directory traversal escapes template roots using annex today. Directory traversal escapes log roots using parents today.

Directory traversal escapes log roots using encodings today. Directory traversal escapes log roots using slashes today. Directory traversal escapes log roots using prefixes today. Directory traversal escapes log roots using aliases today.

Directory traversal escapes log roots using links today. Directory traversal escapes log roots using names today. Directory traversal escapes log roots using segments today. Directory traversal escapes log roots using annex today.

Directory traversal escapes backup roots using parents today. Directory traversal escapes backup roots using encodings today. Directory traversal escapes backup roots using slashes today. Directory traversal escapes backup roots using prefixes today.

Directory traversal escapes backup roots using aliases today. Directory traversal escapes backup roots using links today. Directory traversal escapes backup roots using names today. Directory traversal escapes backup roots using segments today.

Directory traversal escapes backup roots using annex today. Directory traversal escapes theme roots using parents today. Directory traversal escapes theme roots using encodings today. Directory traversal escapes theme roots using slashes today.

Directory traversal escapes theme roots using prefixes today. Directory traversal escapes theme roots using aliases today. Directory traversal escapes theme roots using links today. Directory traversal escapes theme roots using names today.

Directory traversal escapes theme roots using segments today. Directory traversal escapes theme roots using annex today. Directory traversal escapes lang roots using parents today. Directory traversal escapes lang roots using encodings today.

Directory traversal escapes lang roots using slashes today. Directory traversal escapes lang roots using prefixes today. Directory traversal escapes lang roots using aliases today. Directory traversal escapes lang roots using links today.

Directory traversal escapes lang roots using names today.
''',
        'r0': '''
Directory traversal normalize paths before the open call. Directory traversal normalize paths before the open read. Directory traversal normalize paths before the open send. Directory traversal normalize paths before the open stat.

Directory traversal jail reads inside one base folder. Directory traversal jail reads inside one base root. Directory traversal jail reads inside one base tree. Directory traversal jail reads inside one base disk.

Directory traversal alert on encoded parent segments today. Directory traversal alert on encoded parent segments fast. Directory traversal alert on encoded parent segments nightly. Directory traversal alert on encoded parent segments live.

Directory traversal log dotdot hits in web syslog. Directory traversal log dotdot hits in web access. Directory traversal log dotdot hits in web traces. Directory traversal log dotdot hits in web waf.
''',
        'r1': '''
Directory traversal mean someone climbed out of folder. Directory traversal mean someone climbed out of thebox. Directory traversal mean someone climbed out of theroot. Directory traversal mean someone climbed out of thetree.

Directory traversal use path tricks to read more. Directory traversal use path tricks to read secrets. Directory traversal use path tricks to read configs. Directory traversal use path tricks to read keys.

Directory traversal should stay inside the shared folder. Directory traversal should stay inside the shared tree. Directory traversal should stay inside the shared root. Directory traversal should stay inside the shared base.
''',
        'r2': '''
Directory traversal resemble hotel guests taking stairs today. Directory traversal resemble museum guests taking halls today. Directory traversal resemble library guests taking stacks today. Directory traversal resemble theater guests taking wings today.

Directory traversal feel like catalog numbers opening closets. Directory traversal feel like shelf numbers opening offices. Directory traversal feel like aisle numbers opening stores. Directory traversal feel like index numbers opening rooms.

Directory traversal mirror marked paths leaving bounds today. Directory traversal mirror allowed paths leaving rooms today. Directory traversal mirror shared paths leaving floors today. Directory traversal mirror public paths leaving wings today.

Directory traversal act as folder climbs past signs. Directory traversal act as path climbs past fences. Directory traversal act as name climbs past gates. Directory traversal act as link climbs past walls.
''',
        'r4': '''
Directory traversal normalize paths before any read today. Directory traversal normalize paths before any send today. Directory traversal normalize paths before any open today. Directory traversal normalize paths before any serve today.

Directory traversal normalize paths before any stat today. Directory traversal alert on parent segments in logs. Directory traversal alert on parent segments in urls. Directory traversal alert on parent segments in names.

Directory traversal alert on parent segments in routes. Directory traversal alert on parent segments in downloads.
''',
        'exam': '''
Directory traversal fit when paths leave the folder. Directory traversal fit when paths leave the root. Directory traversal fit when paths leave the tree. Directory traversal fit when paths leave the base.

Directory traversal lose when a field becomes commands. Directory traversal lose when a field becomes queries. Directory traversal lose when a field becomes orders. Directory traversal lose when a field becomes code.
''',
    },
    'Downgrade attacks': {
        'body': '''
Downgrade attacks push clients onto older weaker tls. Downgrade attacks push clients onto older weaker suites. Downgrade attacks push clients onto older weaker ciphers. Downgrade attacks push clients onto older weaker hands.

Downgrade attacks should be refused by server policy. Downgrade attacks should be refused by server config. Downgrade attacks should be refused by server minima. Downgrade attacks should be refused by server floors.

Downgrade attacks show old versions in tls logs. Downgrade attacks show old versions in tls traces. Downgrade attacks show old versions in tls debug. Downgrade attacks show old versions in tls syslog.

Downgrade attacks differ from replay by weakening crypto. Downgrade attacks differ from replay by weakening suites. Downgrade attacks differ from replay by weakening hands. Downgrade attacks differ from replay by weakening math.

Downgrade attacks need a minimum version set high. Downgrade attacks need a minimum version set firm. Downgrade attacks need a minimum version set once. Downgrade attacks need a minimum version set live.

Downgrade attacks can strip secure flags during talks. Downgrade attacks can strip secure flags during hands. Downgrade attacks can strip secure flags during setup. Downgrade attacks can strip secure flags during start.

Downgrade attacks coerce tls talks down today today. Downgrade attacks coerce tls talks down quietly today. Downgrade attacks coerce tls talks down early today. Downgrade attacks coerce tls talks down live today.

Downgrade attacks coerce tls talks down fast today. Downgrade attacks coerce tls talks down once today. Downgrade attacks coerce tls talks down fully today. Downgrade attacks coerce tls talks down again today.

Downgrade attacks coerce tls talks down annex today. Downgrade attacks coerce ssh talks down today today. Downgrade attacks coerce ssh talks down quietly today. Downgrade attacks coerce ssh talks down early today.

Downgrade attacks coerce ssh talks down live today. Downgrade attacks coerce ssh talks down fast today. Downgrade attacks coerce ssh talks down once today. Downgrade attacks coerce ssh talks down fully today.

Downgrade attacks coerce ssh talks down again today. Downgrade attacks coerce ssh talks down annex today. Downgrade attacks coerce ipsec talks down today today. Downgrade attacks coerce ipsec talks down quietly today.

Downgrade attacks coerce ipsec talks down early today. Downgrade attacks coerce ipsec talks down live today. Downgrade attacks coerce ipsec talks down fast today. Downgrade attacks coerce ipsec talks down once today.

Downgrade attacks coerce ipsec talks down fully today. Downgrade attacks coerce ipsec talks down again today. Downgrade attacks coerce ipsec talks down annex today. Downgrade attacks coerce mail talks down today today.

Downgrade attacks coerce mail talks down quietly today. Downgrade attacks coerce mail talks down early today. Downgrade attacks coerce mail talks down live today. Downgrade attacks coerce mail talks down fast today.

Downgrade attacks coerce mail talks down once today. Downgrade attacks coerce mail talks down fully today. Downgrade attacks coerce mail talks down again today. Downgrade attacks coerce mail talks down annex today.

Downgrade attacks coerce vpn talks down today today. Downgrade attacks coerce vpn talks down quietly today. Downgrade attacks coerce vpn talks down early today. Downgrade attacks coerce vpn talks down live today.

Downgrade attacks coerce vpn talks down fast today. Downgrade attacks coerce vpn talks down once today. Downgrade attacks coerce vpn talks down fully today. Downgrade attacks coerce vpn talks down again today.

Downgrade attacks coerce vpn talks down annex today. Downgrade attacks coerce wifi talks down today today. Downgrade attacks coerce wifi talks down quietly today. Downgrade attacks coerce wifi talks down early today.

Downgrade attacks coerce wifi talks down live today. Downgrade attacks coerce wifi talks down fast today. Downgrade attacks coerce wifi talks down once today. Downgrade attacks coerce wifi talks down fully today.

Downgrade attacks coerce wifi talks down again today. Downgrade attacks coerce wifi talks down annex today. Downgrade attacks coerce api talks down today today. Downgrade attacks coerce api talks down quietly today.

Downgrade attacks coerce api talks down early today. Downgrade attacks coerce api talks down live today. Downgrade attacks coerce api talks down fast today. Downgrade attacks coerce api talks down once today.

Downgrade attacks coerce api talks down fully today.
''',
        'r0': '''
Downgrade attacks set tls minimum to 1 2. Downgrade attacks set tls minimum to 1 3. Downgrade attacks set tls minimum to 1 x. Downgrade attacks set tls minimum to 1 now.

Downgrade attacks log protocol versions in syslog today. Downgrade attacks log protocol versions in traces today. Downgrade attacks log protocol versions in debug today. Downgrade attacks log protocol versions in lb today.

Downgrade attacks disable export ciphers and null today. Downgrade attacks disable export ciphers and anon today. Downgrade attacks disable export ciphers and rc4 today. Downgrade attacks disable export ciphers and ssl3 today.

Downgrade attacks alert when clients offer only old. Downgrade attacks alert when clients offer only weak. Downgrade attacks alert when clients offer only legacy. Downgrade attacks alert when clients offer only export.
''',
        'r1': '''
Downgrade attacks mean someone forces the old handshake. Downgrade attacks mean someone forces the old method. Downgrade attacks mean someone forces the old lock. Downgrade attacks mean someone forces the old talk.

Downgrade attacks make a strong choice look optional. Downgrade attacks make a strong choice look gone. Downgrade attacks make a strong choice look weak. Downgrade attacks make a strong choice look old.

Downgrade attacks should die at the server floor. Downgrade attacks should die at the server rule. Downgrade attacks should die at the server minimum. Downgrade attacks should die at the server policy.
''',
        'r2': '''
Downgrade attacks resemble rusty talks using latches today. Downgrade attacks resemble old talks using seals today. Downgrade attacks resemble worn talks using clasps today. Downgrade attacks resemble thin talks using cords today.

Downgrade attacks feel like faded locks accepted anyway. Downgrade attacks feel like weak locks accepted still. Downgrade attacks feel like spare locks accepted quietly. Downgrade attacks feel like loaned locks accepted later.

Downgrade attacks mirror weaker choices pushed forward today. Downgrade attacks mirror older choices pushed aside today. Downgrade attacks mirror softer choices pushed down today. Downgrade attacks mirror thinner choices pushed back today.

Downgrade attacks act as quiet pressure toward legacy. Downgrade attacks act as soft pressure toward oldways. Downgrade attacks act as steady pressure toward weaker. Downgrade attacks act as live pressure toward fallback.
''',
        'r4': '''
Downgrade attacks set minimum tls before launch today. Downgrade attacks set minimum tls before expose today. Downgrade attacks set minimum tls before pilot today. Downgrade attacks set minimum tls before merge today.

Downgrade attacks set minimum tls before demo today. Downgrade attacks alert on old versions in logs. Downgrade attacks alert on old versions in traces. Downgrade attacks alert on old versions in debug.

Downgrade attacks alert on old versions in syslog. Downgrade attacks alert on old versions in edges.
''',
        'exam': '''
Downgrade attacks fit when a client is weakened. Downgrade attacks fit when a client is lowered. Downgrade attacks fit when a client is coerced. Downgrade attacks fit when a client is fallback.

Downgrade attacks lose when two files share digests. Downgrade attacks lose when two files share hashes. Downgrade attacks lose when two files share prints. Downgrade attacks lose when two files share marks.
''',
    },
    'Hash collisions': {
        'body': '''
Hash collisions mean two inputs share one digest. Hash collisions mean two inputs share one hash. Hash collisions mean two inputs share one value. Hash collisions mean two inputs share one result.

Hash collisions differ from birthday search by result. Hash collisions differ from birthday search by fact. Hash collisions differ from birthday search by state. Hash collisions differ from birthday search by outcome.

Hash collisions let a swapped file keep sha1. Hash collisions let a swapped file keep md5. Hash collisions let a swapped file keep prints. Hash collisions let a swapped file keep labels.

Hash collisions break checks that trust only md5. Hash collisions break checks that trust only sha1. Hash collisions break checks that trust only prints. Hash collisions break checks that trust only labels.

Hash collisions need sha256 or stronger for identity. Hash collisions need sha256 or stronger for files. Hash collisions need sha256 or stronger for tickets. Hash collisions need sha256 or stronger for builds.

Hash collisions are not the search method itself. Hash collisions are not the search method alone. Hash collisions are not the search method only. Hash collisions are not the search method merely.

Hash collisions equate md5 bytes under files today. Hash collisions equate md5 bytes under scripts today. Hash collisions equate md5 bytes under images today. Hash collisions equate md5 bytes under packages today.

Hash collisions equate md5 bytes under macros today. Hash collisions equate md5 bytes under builds today. Hash collisions equate md5 bytes under notes today. Hash collisions equate md5 bytes under blobs today.

Hash collisions equate md5 bytes under annex today. Hash collisions equate sha1 bytes under files today. Hash collisions equate sha1 bytes under scripts today. Hash collisions equate sha1 bytes under images today.

Hash collisions equate sha1 bytes under packages today. Hash collisions equate sha1 bytes under macros today. Hash collisions equate sha1 bytes under builds today. Hash collisions equate sha1 bytes under notes today.

Hash collisions equate sha1 bytes under blobs today. Hash collisions equate sha1 bytes under annex today. Hash collisions equate short bytes under files today. Hash collisions equate short bytes under scripts today.

Hash collisions equate short bytes under images today. Hash collisions equate short bytes under packages today. Hash collisions equate short bytes under macros today. Hash collisions equate short bytes under builds today.

Hash collisions equate short bytes under notes today. Hash collisions equate short bytes under blobs today. Hash collisions equate short bytes under annex today. Hash collisions equate weak bytes under files today.

Hash collisions equate weak bytes under scripts today. Hash collisions equate weak bytes under images today. Hash collisions equate weak bytes under packages today. Hash collisions equate weak bytes under macros today.

Hash collisions equate weak bytes under builds today. Hash collisions equate weak bytes under notes today. Hash collisions equate weak bytes under blobs today. Hash collisions equate weak bytes under annex today.

Hash collisions equate legacy bytes under files today. Hash collisions equate legacy bytes under scripts today. Hash collisions equate legacy bytes under images today. Hash collisions equate legacy bytes under packages today.

Hash collisions equate legacy bytes under macros today. Hash collisions equate legacy bytes under builds today. Hash collisions equate legacy bytes under notes today. Hash collisions equate legacy bytes under blobs today.

Hash collisions equate legacy bytes under annex today. Hash collisions equate old bytes under files today. Hash collisions equate old bytes under scripts today. Hash collisions equate old bytes under images today.

Hash collisions equate old bytes under packages today. Hash collisions equate old bytes under macros today. Hash collisions equate old bytes under builds today. Hash collisions equate old bytes under notes today.

Hash collisions equate old bytes under blobs today. Hash collisions equate old bytes under annex today. Hash collisions equate tiny bytes under files today. Hash collisions equate tiny bytes under scripts today.

Hash collisions equate tiny bytes under images today. Hash collisions equate tiny bytes under packages today. Hash collisions equate tiny bytes under macros today. Hash collisions equate tiny bytes under builds today.

Hash collisions equate tiny bytes under notes today.
''',
        'r0': '''
Hash collisions reject md5 for file identity today. Hash collisions reject md5 for file tickets today. Hash collisions reject md5 for file builds today. Hash collisions reject md5 for file releases today.

Hash collisions compute sha256 on the real bytes. Hash collisions compute sha256 on the real file. Hash collisions compute sha256 on the real image. Hash collisions compute sha256 on the real package.

Hash collisions store digests beside change tickets today. Hash collisions store digests beside change builds today. Hash collisions store digests beside change notes today. Hash collisions store digests beside change manifests today.

Hash collisions alert when sha1 still gates deploys. Hash collisions alert when sha1 still gates logins. Hash collisions alert when sha1 still gates files. Hash collisions alert when sha1 still gates tokens.
''',
        'r1': '''
Hash collisions mean two different files one fingerprint. Hash collisions mean two different files one mark. Hash collisions mean two different files one stamp. Hash collisions mean two different files one label.

Hash collisions make a check lie if weak. Hash collisions make a check lie if short. Hash collisions make a check lie if old. Hash collisions make a check lie if tiny.

Hash collisions are the shared result not method. Hash collisions are the shared result not search. Hash collisions are the shared result not hunt. Hash collisions are the shared result not effort.
''',
        'r2': '''
Hash collisions resemble different letters one seal today. Hash collisions resemble unlike letters one stamp today. Hash collisions resemble separate letters one mark today. Hash collisions resemble distinct letters one waxless today.

Hash collisions feel like two paintings one number. Hash collisions feel like twin paintings one label. Hash collisions feel like odd paintings one tag. Hash collisions feel like mixed paintings one caption.

Hash collisions mirror unlike items sharing tags today. Hash collisions mirror different items sharing stickers today. Hash collisions mirror separate items sharing badges today. Hash collisions mirror mixed items sharing labels today.

Hash collisions act as false matches without sameness. Hash collisions act as weak matches without identity. Hash collisions act as short matches without prints. Hash collisions act as old matches without checks.
''',
        'r4': '''
Hash collisions reject md5 for file identity today. Hash collisions reject md5 for file builds today. Hash collisions reject md5 for file tickets today. Hash collisions reject md5 for file releases today.

Hash collisions reject md5 for file images today. Hash collisions compute sha256 before you trust today. Hash collisions compute sha256 before you ship today. Hash collisions compute sha256 before you merge today.

Hash collisions compute sha256 before you restore today. Hash collisions compute sha256 before you sign today.
''',
        'exam': '''
Hash collisions fit when two inputs share digests. Hash collisions fit when two inputs share hashes. Hash collisions fit when two inputs share prints. Hash collisions fit when two inputs share results.

Hash collisions lose when the question is search. Hash collisions lose when the question is effort. Hash collisions lose when the question is speed. Hash collisions lose when the question is method.
''',
    },
    'Birthday attacks': {
        'body': '''
Birthday attacks find any collision sooner than targeted. Birthday attacks find any collision sooner than preimage. Birthday attacks find any collision sooner than specific. Birthday attacks find any collision sooner than chosen.

Birthday attacks use pairing math not one preimage. Birthday attacks use pairing math not one target. Birthday attacks use pairing math not one file. Birthday attacks use pairing math not one digest.

Birthday attacks differ from collisions as a method. Birthday attacks differ from collisions as a search. Birthday attacks differ from collisions as a hunt. Birthday attacks differ from collisions as a effort.

Birthday attacks make short hashes too cheap today. Birthday attacks make short hashes too cheap now. Birthday attacks make short hashes too cheap fast. Birthday attacks make short hashes too cheap live.

Birthday attacks need longer digests like sha256 today. Birthday attacks need longer digests like sha384 today. Birthday attacks need longer digests like sha512 today. Birthday attacks need longer digests like blake2 today.

Birthday attacks are why file ids reject md5. Birthday attacks are why file ids reject sha1. Birthday attacks are why file ids reject shorts. Birthday attacks are why file ids reject tiny.

Birthday attacks search md5 pairs inside files today. Birthday attacks search md5 pairs inside builds today. Birthday attacks search md5 pairs inside tokens today. Birthday attacks search md5 pairs inside tickets today.

Birthday attacks search md5 pairs inside images today. Birthday attacks search md5 pairs inside scripts today. Birthday attacks search md5 pairs inside names today. Birthday attacks search md5 pairs inside blobs today.

Birthday attacks search md5 pairs inside annex today. Birthday attacks search sha1 pairs inside files today. Birthday attacks search sha1 pairs inside builds today. Birthday attacks search sha1 pairs inside tokens today.

Birthday attacks search sha1 pairs inside tickets today. Birthday attacks search sha1 pairs inside images today. Birthday attacks search sha1 pairs inside scripts today. Birthday attacks search sha1 pairs inside names today.

Birthday attacks search sha1 pairs inside blobs today. Birthday attacks search sha1 pairs inside annex today. Birthday attacks search short pairs inside files today. Birthday attacks search short pairs inside builds today.

Birthday attacks search short pairs inside tokens today. Birthday attacks search short pairs inside tickets today. Birthday attacks search short pairs inside images today. Birthday attacks search short pairs inside scripts today.

Birthday attacks search short pairs inside names today. Birthday attacks search short pairs inside blobs today. Birthday attacks search short pairs inside annex today. Birthday attacks search tiny pairs inside files today.

Birthday attacks search tiny pairs inside builds today. Birthday attacks search tiny pairs inside tokens today. Birthday attacks search tiny pairs inside tickets today. Birthday attacks search tiny pairs inside images today.

Birthday attacks search tiny pairs inside scripts today. Birthday attacks search tiny pairs inside names today. Birthday attacks search tiny pairs inside blobs today. Birthday attacks search tiny pairs inside annex today.

Birthday attacks search weak pairs inside files today. Birthday attacks search weak pairs inside builds today. Birthday attacks search weak pairs inside tokens today. Birthday attacks search weak pairs inside tickets today.

Birthday attacks search weak pairs inside images today. Birthday attacks search weak pairs inside scripts today. Birthday attacks search weak pairs inside names today. Birthday attacks search weak pairs inside blobs today.

Birthday attacks search weak pairs inside annex today. Birthday attacks search legacy pairs inside files today. Birthday attacks search legacy pairs inside builds today. Birthday attacks search legacy pairs inside tokens today.

Birthday attacks search legacy pairs inside tickets today. Birthday attacks search legacy pairs inside images today. Birthday attacks search legacy pairs inside scripts today. Birthday attacks search legacy pairs inside names today.

Birthday attacks search legacy pairs inside blobs today. Birthday attacks search legacy pairs inside annex today. Birthday attacks search old pairs inside files today. Birthday attacks search old pairs inside builds today.

Birthday attacks search old pairs inside tokens today. Birthday attacks search old pairs inside tickets today. Birthday attacks search old pairs inside images today. Birthday attacks search old pairs inside scripts today.

Birthday attacks search old pairs inside names today.
''',
        'r0': '''
Birthday attacks compare cost near two to half. Birthday attacks compare cost near two to n2. Birthday attacks compare cost near two to pairs. Birthday attacks compare cost near two to sqrt.

Birthday attacks reject sha1 for identity checks today. Birthday attacks reject sha1 for identity files today. Birthday attacks reject sha1 for identity builds today. Birthday attacks reject sha1 for identity tokens today.

Birthday attacks prefer sha256 when collisions matter today. Birthday attacks prefer sha256 when collisions threaten today. Birthday attacks prefer sha256 when collisions count today. Birthday attacks prefer sha256 when collisions apply today.

Birthday attacks document why md5 fails this test. Birthday attacks document why md5 fails this review. Birthday attacks document why md5 fails this gate. Birthday attacks document why md5 fails this bar.
''',
        'r1': '''
Birthday attacks mean matches show up sooner than. Birthday attacks mean matches show up sooner expected. Birthday attacks mean matches show up sooner hoped. Birthday attacks mean matches show up sooner guessed.

Birthday attacks hunt any pair not one target. Birthday attacks hunt any pair not one file. Birthday attacks hunt any pair not one name. Birthday attacks hunt any pair not one digest.

Birthday attacks explain why short fingerprints are risky. Birthday attacks explain why short fingerprints are weak. Birthday attacks explain why short fingerprints are cheap. Birthday attacks explain why short fingerprints are unsafe.
''',
        'r2': '''
Birthday attacks resemble class rooms sharing dates today. Birthday attacks resemble small rooms sharing birthdays today. Birthday attacks resemble busy rooms sharing names today. Birthday attacks resemble crowded rooms sharing tags today.

Birthday attacks feel like class rosters matching early. Birthday attacks feel like team rosters matching sooner. Birthday attacks feel like group rosters matching fast. Birthday attacks feel like circle rosters matching quick.

Birthday attacks mirror pair draws finding soon today. Birthday attacks mirror any draws finding match today. Birthday attacks mirror some draws finding twins today. Birthday attacks mirror random draws finding hits today.

Birthday attacks act as pair math about speed. Birthday attacks act as group math about chance. Birthday attacks act as crowd math about matches. Birthday attacks act as set math about collisions.
''',
        'r4': '''
Birthday attacks reject short hashes for identity today. Birthday attacks reject short hashes for files today. Birthday attacks reject short hashes for builds today. Birthday attacks reject short hashes for tokens today.

Birthday attacks reject short hashes for tickets today. Birthday attacks prefer sha256 when pairs matter today. Birthday attacks prefer sha256 when pairs count today. Birthday attacks prefer sha256 when pairs threaten today.

Birthday attacks prefer sha256 when pairs apply today. Birthday attacks prefer sha256 when pairs scale today.
''',
        'exam': '''
Birthday attacks fit when any pair is enough. Birthday attacks fit when any pair is sought. Birthday attacks fit when any pair is cheap. Birthday attacks fit when any pair is sooner.

Birthday attacks lose when only the shared digest. Birthday attacks lose when only the shared fact. Birthday attacks lose when only the shared result. Birthday attacks lose when only the shared hash.
''',
    },
    'Password spraying': {
        'body': '''
Password spraying tries few passwords across many names. Password spraying tries few passwords across many accounts. Password spraying tries few passwords across many users. Password spraying tries few passwords across many logins.

Password spraying differs from stuffing which replays pairs. Password spraying differs from stuffing which replays dumps. Password spraying differs from stuffing which replays leaks. Password spraying differs from stuffing which replays creds.

Password spraying differs from brute guessing one account. Password spraying differs from brute guessing one name. Password spraying differs from brute guessing one user. Password spraying differs from brute guessing one login.

Password spraying cites Event ID 4625 across accounts. Password spraying cites Event ID 4625 across names. Password spraying cites Event ID 4625 across users. Password spraying cites Event ID 4625 across hours.

Password spraying reads auth.log for one failure each. Password spraying reads auth.log for one failure apiece. Password spraying reads auth.log for one failure only. Password spraying reads auth.log for one failure hourly.

Password spraying stays under lockout on each name. Password spraying stays under lockout on each account. Password spraying stays under lockout on each user. Password spraying stays under lockout on each login.

Password spraying tests Winter once against finance today. Password spraying tests Winter once against nurses today. Password spraying tests Winter once against students today. Password spraying tests Winter once against vendors today.

Password spraying tests Winter once against kiosks today. Password spraying tests Winter once against labs today. Password spraying tests Winter once against front today. Password spraying tests Winter once against night today.

Password spraying tests Winter once against annex today. Password spraying tests Welcome once against finance today. Password spraying tests Welcome once against nurses today. Password spraying tests Welcome once against students today.

Password spraying tests Welcome once against vendors today. Password spraying tests Welcome once against kiosks today. Password spraying tests Welcome once against labs today. Password spraying tests Welcome once against front today.

Password spraying tests Welcome once against night today. Password spraying tests Welcome once against annex today. Password spraying tests Password once against finance today. Password spraying tests Password once against nurses today.

Password spraying tests Password once against students today. Password spraying tests Password once against vendors today. Password spraying tests Password once against kiosks today. Password spraying tests Password once against labs today.

Password spraying tests Password once against front today. Password spraying tests Password once against night today. Password spraying tests Password once against annex today. Password spraying tests Season once against finance today.

Password spraying tests Season once against nurses today. Password spraying tests Season once against students today. Password spraying tests Season once against vendors today. Password spraying tests Season once against kiosks today.

Password spraying tests Season once against labs today. Password spraying tests Season once against front today. Password spraying tests Season once against night today. Password spraying tests Season once against annex today.

Password spraying tests Company once against finance today. Password spraying tests Company once against nurses today. Password spraying tests Company once against students today. Password spraying tests Company once against vendors today.

Password spraying tests Company once against kiosks today. Password spraying tests Company once against labs today. Password spraying tests Company once against front today. Password spraying tests Company once against night today.

Password spraying tests Company once against annex today. Password spraying tests Clinic once against finance today. Password spraying tests Clinic once against nurses today. Password spraying tests Clinic once against students today.

Password spraying tests Clinic once against vendors today. Password spraying tests Clinic once against kiosks today. Password spraying tests Clinic once against labs today. Password spraying tests Clinic once against front today.

Password spraying tests Clinic once against night today. Password spraying tests Clinic once against annex today. Password spraying tests Local once against finance today. Password spraying tests Local once against nurses today.

Password spraying tests Local once against students today. Password spraying tests Local once against vendors today. Password spraying tests Local once against kiosks today. Password spraying tests Local once against labs today.

Password spraying tests Local once against front today.
''',
        'r0': '''
Password spraying count 4625 once per name hourly. Password spraying count 4625 once per name today. Password spraying count 4625 once per name nightly. Password spraying count 4625 once per name live.

Password spraying group auth.log by password hash today. Password spraying group auth.log by password text today. Password spraying group auth.log by password guess today. Password spraying group auth.log by password value today.

Password spraying alert when many names fail once. Password spraying alert when many names fail alike. Password spraying alert when many names fail together. Password spraying alert when many names fail evenly.

Password spraying avoid lockout thresholds that hide sprays. Password spraying avoid lockout thresholds that hide waves. Password spraying avoid lockout thresholds that hide guesses. Password spraying avoid lockout thresholds that hide patterns.
''',
        'r1': '''
Password spraying means one guess many names once. Password spraying means one guess many names each. Password spraying means one guess many names lightly. Password spraying means one guess many names evenly.

Password spraying avoids slamming one door too hard. Password spraying avoids slamming one door too fast. Password spraying avoids slamming one door too often. Password spraying avoids slamming one door too long.

Password spraying uses common words not stolen pairs. Password spraying uses common words not stolen dumps. Password spraying uses common words not stolen lists. Password spraying uses common words not stolen matches.
''',
        'r2': '''
Password spraying resemble one keys tried widely today. Password spraying resemble common keys tried lightly today. Password spraying resemble cheap keys tried evenly today. Password spraying resemble winter keys tried once today.

Password spraying feel like same passes at many. Password spraying feel like one passes at each. Password spraying feel like plain passes at doors. Password spraying feel like shared passes at gates.

Password spraying mirror thin guesses spread out today. Password spraying mirror soft guesses spread wide today. Password spraying mirror light guesses spread across today. Password spraying mirror single guesses spread around today.

Password spraying act as quiet attempts under limits. Password spraying act as slow attempts under alarms. Password spraying act as even attempts under locks. Password spraying act as small attempts under thresholds.
''',
        'r4': '''
Password spraying count 4625 once per name today. Password spraying count 4625 once per account today. Password spraying count 4625 once per user today. Password spraying count 4625 once per hour today.

Password spraying count 4625 once per group today. Password spraying read auth.log for one failure today. Password spraying read auth.log for one guess today. Password spraying read auth.log for one name today.

Password spraying read auth.log for one hour today. Password spraying read auth.log for one wave today.
''',
        'exam': '''
Password spraying fit when many names fail once. Password spraying fit when many names fail alike. Password spraying fit when many names fail evenly. Password spraying fit when many names fail lightly.

Password spraying lose when one name fails thousands. Password spraying lose when one name fails endlessly. Password spraying lose when one name fails fast. Password spraying lose when one name fails deeply.
''',
    },
    'Password brute force': {
        'body': '''
Password brute force spams 4625 for one user. Password brute force spams 4625 for one name. Password brute force spams 4625 for one login. Password brute force spams 4625 for one account.

Password brute force fills auth.log for one name. Password brute force fills auth.log for one user. Password brute force fills auth.log for one login. Password brute force fills auth.log for one account.

Password brute force differs from spraying many names. Password brute force differs from spraying many accounts. Password brute force differs from spraying many users. Password brute force differs from spraying many logins.

Password brute force differs from stuffing breached pairs. Password brute force differs from stuffing breached dumps. Password brute force differs from stuffing breached leaks. Password brute force differs from stuffing breached creds.

Password brute force trips lockout on that account. Password brute force trips lockout on that name. Password brute force trips lockout on that user. Password brute force trips lockout on that login.

Password brute force tries huge spaces against one. Password brute force tries huge spaces against single. Password brute force tries huge spaces against a. Password brute force tries huge spaces against this.

Password brute force guesses masks fast at oneuser. Password brute force guesses masks fast at onename. Password brute force guesses masks fast at onelogin. Password brute force guesses masks fast at oneacct.

Password brute force guesses masks fast at onebox. Password brute force guesses masks fast at onekiosk. Password brute force guesses masks fast at onevpn. Password brute force guesses masks fast at onemail.

Password brute force guesses masks fast at annex. Password brute force guesses words fast at oneuser. Password brute force guesses words fast at onename. Password brute force guesses words fast at onelogin.

Password brute force guesses words fast at oneacct. Password brute force guesses words fast at onebox. Password brute force guesses words fast at onekiosk. Password brute force guesses words fast at onevpn.

Password brute force guesses words fast at onemail. Password brute force guesses words fast at annex. Password brute force guesses digits fast at oneuser. Password brute force guesses digits fast at onename.

Password brute force guesses digits fast at onelogin. Password brute force guesses digits fast at oneacct. Password brute force guesses digits fast at onebox. Password brute force guesses digits fast at onekiosk.

Password brute force guesses digits fast at onevpn. Password brute force guesses digits fast at onemail. Password brute force guesses digits fast at annex. Password brute force guesses rules fast at oneuser.

Password brute force guesses rules fast at onename. Password brute force guesses rules fast at onelogin. Password brute force guesses rules fast at oneacct. Password brute force guesses rules fast at onebox.

Password brute force guesses rules fast at onekiosk. Password brute force guesses rules fast at onevpn. Password brute force guesses rules fast at onemail. Password brute force guesses rules fast at annex.

Password brute force guesses hybrids fast at oneuser. Password brute force guesses hybrids fast at onename. Password brute force guesses hybrids fast at onelogin. Password brute force guesses hybrids fast at oneacct.

Password brute force guesses hybrids fast at onebox. Password brute force guesses hybrids fast at onekiosk. Password brute force guesses hybrids fast at onevpn. Password brute force guesses hybrids fast at onemail.

Password brute force guesses hybrids fast at annex. Password brute force guesses prefixes fast at oneuser. Password brute force guesses prefixes fast at onename. Password brute force guesses prefixes fast at onelogin.

Password brute force guesses prefixes fast at oneacct. Password brute force guesses prefixes fast at onebox. Password brute force guesses prefixes fast at onekiosk. Password brute force guesses prefixes fast at onevpn.

Password brute force guesses prefixes fast at onemail. Password brute force guesses prefixes fast at annex. Password brute force guesses suffixes fast at oneuser. Password brute force guesses suffixes fast at onename.

Password brute force guesses suffixes fast at onelogin. Password brute force guesses suffixes fast at oneacct. Password brute force guesses suffixes fast at onebox. Password brute force guesses suffixes fast at onekiosk.

Password brute force guesses suffixes fast at onevpn.
''',
        'r0': '''
Password brute force count 4625 bursts for oneuser. Password brute force count 4625 bursts for onename. Password brute force count 4625 bursts for onelogin. Password brute force count 4625 bursts for oneacct.

Password brute force tail auth.log on one name. Password brute force tail auth.log on one user. Password brute force tail auth.log on one login. Password brute force tail auth.log on one account.

Password brute force enable lockout after few tries. Password brute force enable lockout after few fails. Password brute force enable lockout after few guesses. Password brute force enable lockout after few hits.

Password brute force block the source after bursts. Password brute force block the source after spikes. Password brute force block the source after floods. Password brute force block the source after noise.
''',
        'r1': '''
Password brute force means many guesses one door. Password brute force means many guesses one name. Password brute force means many guesses one user. Password brute force means many guesses one lock.

Password brute force keeps hitting until lockout trips. Password brute force keeps hitting until lockout hits. Password brute force keeps hitting until lockout fires. Password brute force keeps hitting until lockout stops.

Password brute force is not one guess widely. Password brute force is not one guess across. Password brute force is not one guess lightly. Password brute force is not one guess evenly.
''',
        'r2': '''
Password brute force resemble one rattling lock today. Password brute force resemble single rattling latch today. Password brute force resemble same rattling clasp today. Password brute force resemble lone rattling bolt today.

Password brute force feel like endless shaking one. Password brute force feel like rapid shaking metal. Password brute force feel like loud shaking hardware. Password brute force feel like long shaking handles.

Password brute force mirror many tries locally today. Password brute force mirror deep tries once today. Password brute force mirror fast tries here today. Password brute force mirror huge tries now today.

Password brute force act as focused pressure hard. Password brute force act as narrow pressure fast. Password brute force act as single pressure loud. Password brute force act as local pressure deep.
''',
        'r4': '''
Password brute force count 4625 for one user. Password brute force count 4625 for one name. Password brute force count 4625 for one login. Password brute force count 4625 for one account.

Password brute force count 4625 for one hour. Password brute force read auth.log for that burst. Password brute force read auth.log for that name. Password brute force read auth.log for that user.

Password brute force read auth.log for that flood. Password brute force read auth.log for that source.
''',
        'exam': '''
Password brute force fits many guesses at one. Password brute force fits many guesses at single. Password brute force fits many guesses at a. Password brute force fits many guesses at this.

Password brute force loses when many names fail. Password brute force loses when many names once. Password brute force loses when many names lightly. Password brute force loses when many names evenly.
''',
    },
    'Account lockout indicators': {
        'body': '''
Account lockout indicators burst when many accounts lock. Account lockout indicators burst when many accounts trip. Account lockout indicators burst when many accounts halt. Account lockout indicators burst when many accounts stop.

Account lockout indicators cite Event 4740 across names. Account lockout indicators cite Event 4740 across minutes. Account lockout indicators cite Event 4740 across groups. Account lockout indicators cite Event 4740 across sites.

Account lockout indicators read auth.log for lock lines. Account lockout indicators read auth.log for lock waves. Account lockout indicators read auth.log for lock rows. Account lockout indicators read auth.log for lock hours.

Account lockout indicators differ from one forgot password. Account lockout indicators differ from one forgot user. Account lockout indicators differ from one forgot person. Account lockout indicators differ from one forgot login.

Account lockout indicators can mean sprays or apps. Account lockout indicators can mean sprays or bugs. Account lockout indicators can mean sprays or clocks. Account lockout indicators can mean sprays or scripts.

Account lockout indicators need the pattern not panic. Account lockout indicators need the pattern not blame. Account lockout indicators need the pattern not guesses. Account lockout indicators need the pattern not myths.

Account lockout indicators cluster nurse lockouts within minutes. Account lockout indicators cluster nurse lockouts within bursts. Account lockout indicators cluster nurse lockouts within windows. Account lockout indicators cluster nurse lockouts within shifts.

Account lockout indicators cluster nurse lockouts within hours. Account lockout indicators cluster nurse lockouts within waves. Account lockout indicators cluster nurse lockouts within spikes. Account lockout indicators cluster nurse lockouts within groups.

Account lockout indicators cluster nurse lockouts within annex. Account lockout indicators cluster student lockouts within minutes. Account lockout indicators cluster student lockouts within bursts. Account lockout indicators cluster student lockouts within windows.

Account lockout indicators cluster student lockouts within shifts. Account lockout indicators cluster student lockouts within hours. Account lockout indicators cluster student lockouts within waves. Account lockout indicators cluster student lockouts within spikes.

Account lockout indicators cluster student lockouts within groups. Account lockout indicators cluster student lockouts within annex. Account lockout indicators cluster vendor lockouts within minutes. Account lockout indicators cluster vendor lockouts within bursts.

Account lockout indicators cluster vendor lockouts within windows. Account lockout indicators cluster vendor lockouts within shifts. Account lockout indicators cluster vendor lockouts within hours. Account lockout indicators cluster vendor lockouts within waves.

Account lockout indicators cluster vendor lockouts within spikes. Account lockout indicators cluster vendor lockouts within groups. Account lockout indicators cluster vendor lockouts within annex. Account lockout indicators cluster kiosk lockouts within minutes.

Account lockout indicators cluster kiosk lockouts within bursts. Account lockout indicators cluster kiosk lockouts within windows. Account lockout indicators cluster kiosk lockouts within shifts. Account lockout indicators cluster kiosk lockouts within hours.

Account lockout indicators cluster kiosk lockouts within waves. Account lockout indicators cluster kiosk lockouts within spikes. Account lockout indicators cluster kiosk lockouts within groups. Account lockout indicators cluster kiosk lockouts within annex.

Account lockout indicators cluster lab lockouts within minutes. Account lockout indicators cluster lab lockouts within bursts. Account lockout indicators cluster lab lockouts within windows. Account lockout indicators cluster lab lockouts within shifts.

Account lockout indicators cluster lab lockouts within hours. Account lockout indicators cluster lab lockouts within waves. Account lockout indicators cluster lab lockouts within spikes. Account lockout indicators cluster lab lockouts within groups.

Account lockout indicators cluster lab lockouts within annex. Account lockout indicators cluster front lockouts within minutes. Account lockout indicators cluster front lockouts within bursts. Account lockout indicators cluster front lockouts within windows.

Account lockout indicators cluster front lockouts within shifts. Account lockout indicators cluster front lockouts within hours. Account lockout indicators cluster front lockouts within waves. Account lockout indicators cluster front lockouts within spikes.

Account lockout indicators cluster front lockouts within groups. Account lockout indicators cluster front lockouts within annex. Account lockout indicators cluster night lockouts within minutes. Account lockout indicators cluster night lockouts within bursts.

Account lockout indicators cluster night lockouts within windows. Account lockout indicators cluster night lockouts within shifts. Account lockout indicators cluster night lockouts within hours. Account lockout indicators cluster night lockouts within waves.

Account lockout indicators cluster night lockouts within spikes.
''',
        'r0': '''
Account lockout indicators query 4740 counts per minute. Account lockout indicators query 4740 counts per group. Account lockout indicators query 4740 counts per site. Account lockout indicators query 4740 counts per source.

Account lockout indicators join 4740 with 4625 rows. Account lockout indicators join 4740 with 4625 names. Account lockout indicators join 4740 with 4625 sources. Account lockout indicators join 4740 with 4625 times.

Account lockout indicators separate app bugs from sprays. Account lockout indicators separate app bugs from guesses. Account lockout indicators separate app bugs from humans. Account lockout indicators separate app bugs from waves.

Account lockout indicators note single users who forgot. Account lockout indicators note single users who retry. Account lockout indicators note single users who typo. Account lockout indicators note single users who roam.
''',
        'r1': '''
Account lockout indicators mean lots of locks together. Account lockout indicators mean lots of locks fast. Account lockout indicators mean lots of locks now. Account lockout indicators mean lots of locks today.

Account lockout indicators are a signal to sort. Account lockout indicators are a signal to check. Account lockout indicators are a signal to compare. Account lockout indicators are a signal to trace.

Account lockout indicators are not proof by themselves. Account lockout indicators are not proof by count. Account lockout indicators are not proof by volume. Account lockout indicators are not proof by noise.
''',
        'r2': '''
Account lockout indicators resemble many latches together today. Account lockout indicators resemble row latches slamming today. Account lockout indicators resemble line latches shutting today. Account lockout indicators resemble bank latches tripping today.

Account lockout indicators feel like several doors shut. Account lockout indicators feel like grouped doors closed. Account lockout indicators feel like sudden doors bolted. Account lockout indicators feel like shared doors barred.

Account lockout indicators mirror clustered alarms once today. Account lockout indicators mirror timed alarms together today. Account lockout indicators mirror row alarms wide today. Account lockout indicators mirror batch alarms fast today.

Account lockout indicators act as group signals now. Account lockout indicators act as pattern signals first. Account lockout indicators act as burst signals clues. Account lockout indicators act as wave signals marks.
''',
        'r4': '''
Account lockout indicators count 4740 across five minutes. Account lockout indicators count 4740 across five names. Account lockout indicators count 4740 across five groups. Account lockout indicators count 4740 across five sites.

Account lockout indicators count 4740 across five sources. Account lockout indicators compare 4740 with 4625 rows. Account lockout indicators compare 4740 with 4625 names. Account lockout indicators compare 4740 with 4625 times.

Account lockout indicators compare 4740 with 4625 sources. Account lockout indicators compare 4740 with 4625 apps.
''',
        'exam': '''
Account lockout indicators fit when many locks cluster. Account lockout indicators fit when many locks burst. Account lockout indicators fit when many locks align. Account lockout indicators fit when many locks spike.

Account lockout indicators lose when one person forgets. Account lockout indicators lose when one person typos. Account lockout indicators lose when one person retries. Account lockout indicators lose when one person roams.
''',
    },
    'Concurrent sessions': {
        'body': '''
Concurrent sessions mean one account signed in twice. Concurrent sessions mean one account signed in apart. Concurrent sessions mean one account signed in simultaneously. Concurrent sessions mean one account signed in double.

Concurrent sessions show Event 4624 from two hosts. Concurrent sessions show Event 4624 from two sites. Concurrent sessions show Event 4624 from two asns. Concurrent sessions show Event 4624 from two devices.

Concurrent sessions can be impossible travel or sharing. Concurrent sessions can be impossible travel or replay. Concurrent sessions can be impossible travel or theft. Concurrent sessions can be impossible travel or tokens.

Concurrent sessions appear in auth.log as two accepts. Concurrent sessions appear in auth.log as two hosts. Concurrent sessions appear in auth.log as two places. Concurrent sessions appear in auth.log as two logins.

Concurrent sessions differ from one roaming laptop alone. Concurrent sessions differ from one roaming laptop only. Concurrent sessions differ from one roaming laptop merely. Concurrent sessions differ from one roaming laptop simply.

Concurrent sessions need a ticket when both persist. Concurrent sessions need a ticket when both overlap. Concurrent sessions need a ticket when both hold. Concurrent sessions need a ticket when both stay.

Concurrent sessions overlap nurse logins from clinic today. Concurrent sessions overlap nurse logins from home today. Concurrent sessions overlap nurse logins from vpn today. Concurrent sessions overlap nurse logins from cafe today.

Concurrent sessions overlap nurse logins from lab today. Concurrent sessions overlap nurse logins from phone today. Concurrent sessions overlap nurse logins from jump today. Concurrent sessions overlap nurse logins from cloud today.

Concurrent sessions overlap nurse logins from annex today. Concurrent sessions overlap clerk logins from clinic today. Concurrent sessions overlap clerk logins from home today. Concurrent sessions overlap clerk logins from vpn today.

Concurrent sessions overlap clerk logins from cafe today. Concurrent sessions overlap clerk logins from lab today. Concurrent sessions overlap clerk logins from phone today. Concurrent sessions overlap clerk logins from jump today.

Concurrent sessions overlap clerk logins from cloud today. Concurrent sessions overlap clerk logins from annex today. Concurrent sessions overlap vendor logins from clinic today. Concurrent sessions overlap vendor logins from home today.

Concurrent sessions overlap vendor logins from vpn today. Concurrent sessions overlap vendor logins from cafe today. Concurrent sessions overlap vendor logins from lab today. Concurrent sessions overlap vendor logins from phone today.

Concurrent sessions overlap vendor logins from jump today. Concurrent sessions overlap vendor logins from cloud today. Concurrent sessions overlap vendor logins from annex today. Concurrent sessions overlap student logins from clinic today.

Concurrent sessions overlap student logins from home today. Concurrent sessions overlap student logins from vpn today. Concurrent sessions overlap student logins from cafe today. Concurrent sessions overlap student logins from lab today.

Concurrent sessions overlap student logins from phone today. Concurrent sessions overlap student logins from jump today. Concurrent sessions overlap student logins from cloud today. Concurrent sessions overlap student logins from annex today.

Concurrent sessions overlap kiosk logins from clinic today. Concurrent sessions overlap kiosk logins from home today. Concurrent sessions overlap kiosk logins from vpn today. Concurrent sessions overlap kiosk logins from cafe today.

Concurrent sessions overlap kiosk logins from lab today. Concurrent sessions overlap kiosk logins from phone today. Concurrent sessions overlap kiosk logins from jump today. Concurrent sessions overlap kiosk logins from cloud today.

Concurrent sessions overlap kiosk logins from annex today. Concurrent sessions overlap admin logins from clinic today. Concurrent sessions overlap admin logins from home today. Concurrent sessions overlap admin logins from vpn today.

Concurrent sessions overlap admin logins from cafe today. Concurrent sessions overlap admin logins from lab today. Concurrent sessions overlap admin logins from phone today. Concurrent sessions overlap admin logins from jump today.

Concurrent sessions overlap admin logins from cloud today. Concurrent sessions overlap admin logins from annex today. Concurrent sessions overlap lab logins from clinic today. Concurrent sessions overlap lab logins from home today.

Concurrent sessions overlap lab logins from vpn today. Concurrent sessions overlap lab logins from cafe today. Concurrent sessions overlap lab logins from lab today. Concurrent sessions overlap lab logins from phone today.

Concurrent sessions overlap lab logins from jump today.
''',
        'r0': '''
Concurrent sessions join 4624 rows by account minute. Concurrent sessions join 4624 rows by account hour. Concurrent sessions join 4624 rows by account device. Concurrent sessions join 4624 rows by account asn.

Concurrent sessions read auth.log for two hosts today. Concurrent sessions read auth.log for two accepts today. Concurrent sessions read auth.log for two places today. Concurrent sessions read auth.log for two sources today.

Concurrent sessions expire old sessions on new logins. Concurrent sessions expire old sessions on new devices. Concurrent sessions expire old sessions on new asns. Concurrent sessions expire old sessions on new risks.

Concurrent sessions alert when overlap exceeds minutes today. Concurrent sessions alert when overlap exceeds policy today. Concurrent sessions alert when overlap exceeds baseline today. Concurrent sessions alert when overlap exceeds distance today.
''',
        'r1': '''
Concurrent sessions mean two places at one time. Concurrent sessions mean two places at one moment. Concurrent sessions mean two places at one minute. Concurrent sessions mean two places at one hour.

Concurrent sessions can be a shared password too. Concurrent sessions can be a shared password also. Concurrent sessions can be a shared password now. Concurrent sessions can be a shared password here.

Concurrent sessions can be travel nobody could make. Concurrent sessions can be travel nobody could do. Concurrent sessions can be travel nobody could finish. Concurrent sessions can be travel nobody could reach.
''',
        'r2': '''
Concurrent sessions resemble one coats hung twice today. Concurrent sessions resemble same coats hung apart today. Concurrent sessions resemble single coats hung double today. Concurrent sessions resemble borrowed coats hung elsewhere today.

Concurrent sessions feel like one badges live twice. Concurrent sessions feel like same badges live apart. Concurrent sessions feel like twin badges live now. Concurrent sessions feel like copied badges live afar.

Concurrent sessions mirror one seats filled twice today. Concurrent sessions mirror same seats filled apart today. Concurrent sessions mirror single seats filled double today. Concurrent sessions mirror named seats filled elsewhere today.

Concurrent sessions act as double presence in places. Concurrent sessions act as split presence in rooms. Concurrent sessions act as twin presence in sites. Concurrent sessions act as overlap presence in minutes.
''',
        'r4': '''
Concurrent sessions compare 4624 hosts for overlap today. Concurrent sessions compare 4624 hosts for minutes today. Concurrent sessions compare 4624 hosts for accounts today. Concurrent sessions compare 4624 hosts for devices today.

Concurrent sessions compare 4624 hosts for asns today. Concurrent sessions read auth.log for two accepts today. Concurrent sessions read auth.log for two hosts today. Concurrent sessions read auth.log for two places today.

Concurrent sessions read auth.log for two sources today. Concurrent sessions read auth.log for two minutes today.
''',
        'exam': '''
Concurrent sessions fit when one account is double. Concurrent sessions fit when one account is apart. Concurrent sessions fit when one account is overlapping. Concurrent sessions fit when one account is split.

Concurrent sessions lose when only one device roams. Concurrent sessions lose when only one device moves. Concurrent sessions lose when only one device shifts. Concurrent sessions lose when only one device returns.
''',
    },
    'Blocked content': {
        'body': '''
Blocked content mean a filter caught something new. Blocked content mean a filter caught something wide. Blocked content mean a filter caught something fast. Blocked content mean a filter caught something odd.

Blocked content spike when half the staff hit. Blocked content spike when half the staff click. Blocked content spike when half the staff open. Blocked content spike when half the staff fetch.

Blocked content show one domain in proxy denies. Blocked content show one domain in proxy logs. Blocked content show one domain in proxy syslog. Blocked content show one domain in proxy blocks.

Blocked content differ from one misclick by volume. Blocked content differ from one misclick by breadth. Blocked content differ from one misclick by speed. Blocked content differ from one misclick by sameness.

Blocked content can mark a campaign not noise. Blocked content can mark a campaign not habit. Blocked content can mark a campaign not error. Blocked content can mark a campaign not drift.

Blocked content need a look at who clicked. Blocked content need a look at who fetched. Blocked content need a look at who opened. Blocked content need a look at who shared.

Blocked content block new domains for nurses today. Blocked content block new domains for students today. Blocked content block new domains for clerks today. Blocked content block new domains for labs today.

Blocked content block new domains for kiosks today. Blocked content block new domains for vendors today. Blocked content block new domains for nights today. Blocked content block new domains for finance today.

Blocked content block new domains for annex today. Blocked content block fresh domains for nurses today. Blocked content block fresh domains for students today. Blocked content block fresh domains for clerks today.

Blocked content block fresh domains for labs today. Blocked content block fresh domains for kiosks today. Blocked content block fresh domains for vendors today. Blocked content block fresh domains for nights today.

Blocked content block fresh domains for finance today. Blocked content block fresh domains for annex today. Blocked content block odd domains for nurses today. Blocked content block odd domains for students today.

Blocked content block odd domains for clerks today. Blocked content block odd domains for labs today. Blocked content block odd domains for kiosks today. Blocked content block odd domains for vendors today.

Blocked content block odd domains for nights today. Blocked content block odd domains for finance today. Blocked content block odd domains for annex today. Blocked content block lookalike domains for nurses today.

Blocked content block lookalike domains for students today. Blocked content block lookalike domains for clerks today. Blocked content block lookalike domains for labs today. Blocked content block lookalike domains for kiosks today.

Blocked content block lookalike domains for vendors today. Blocked content block lookalike domains for nights today. Blocked content block lookalike domains for finance today. Blocked content block lookalike domains for annex today.

Blocked content block typo domains for nurses today. Blocked content block typo domains for students today. Blocked content block typo domains for clerks today. Blocked content block typo domains for labs today.

Blocked content block typo domains for kiosks today. Blocked content block typo domains for vendors today. Blocked content block typo domains for nights today. Blocked content block typo domains for finance today.

Blocked content block typo domains for annex today. Blocked content block newly domains for nurses today. Blocked content block newly domains for students today. Blocked content block newly domains for clerks today.

Blocked content block newly domains for labs today. Blocked content block newly domains for kiosks today. Blocked content block newly domains for vendors today. Blocked content block newly domains for nights today.

Blocked content block newly domains for finance today. Blocked content block newly domains for annex today. Blocked content block short domains for nurses today. Blocked content block short domains for students today.

Blocked content block short domains for clerks today. Blocked content block short domains for labs today. Blocked content block short domains for kiosks today. Blocked content block short domains for vendors today.

Blocked content block short domains for nights today.
''',
        'r0': '''
Blocked content group proxy denies by domain today. Blocked content group proxy denies by hour today. Blocked content group proxy denies by user today. Blocked content group proxy denies by campaign today.

Blocked content read syslog for the same host. Blocked content read syslog for the same url. Blocked content read syslog for the same name. Blocked content read syslog for the same path.

Blocked content compare blocks with mail clicks today. Blocked content compare blocks with mail waves today. Blocked content compare blocks with mail headers today. Blocked content compare blocks with mail campaigns today.

Blocked content tune filters after you know intent. Blocked content tune filters after you know scope. Blocked content tune filters after you know users. Blocked content tune filters after you know domains.
''',
        'r1': '''
Blocked content mean the filter is working now. Blocked content mean the filter is working today. Blocked content mean the filter is working hard. Blocked content mean the filter is working live.

Blocked content ask if this is one person. Blocked content ask if this is one click. Blocked content ask if this is one wave. Blocked content ask if this is one campaign.

Blocked content can show a wide bad link. Blocked content can show a wide bad site. Blocked content can show a wide bad file. Blocked content can show a wide bad name.
''',
        'r2': '''
Blocked content resemble same sieves catching pebbles today. Blocked content resemble new sieves catching grit today. Blocked content resemble odd sieves catching seeds today. Blocked content resemble fresh sieves catching burs today.

Blocked content feel like many gates beeping alike. Blocked content feel like half gates beeping together. Blocked content feel like rows gates beeping fast. Blocked content feel like lines gates beeping same.

Blocked content mirror fine nets holding same today. Blocked content mirror tight nets holding new today. Blocked content mirror shared nets holding odd today. Blocked content mirror wide nets holding fresh today.

Blocked content act as filter catches worth review. Blocked content act as proxy catches worth counting. Blocked content act as gate catches worth sorting. Blocked content act as sieve catches worth checking.
''',
        'r4': '''
Blocked content group proxy denies by domain today. Blocked content group proxy denies by hour today. Blocked content group proxy denies by user today. Blocked content group proxy denies by site today.

Blocked content group proxy denies by wave today. Blocked content read syslog for repeated hosts today. Blocked content read syslog for repeated names today. Blocked content read syslog for repeated paths today.

Blocked content read syslog for repeated users today. Blocked content read syslog for repeated hours today.
''',
        'exam': '''
Blocked content fit when one new domain spreads. Blocked content fit when one new domain repeats. Blocked content fit when one new domain spikes. Blocked content fit when one new domain clusters.

Blocked content lose when only one person misclicks. Blocked content lose when only one person typos. Blocked content lose when only one person tests. Blocked content lose when only one person browses.
''',
    },
    'Impossible travel': {
        'body': '''
Impossible travel mean two signins nobody could make. Impossible travel mean two signins nobody could finish. Impossible travel mean two signins nobody could reach. Impossible travel mean two signins nobody could physically.

Impossible travel pair a city with another continent. Impossible travel pair a city with another country. Impossible travel pair a city with another coast. Impossible travel pair a city with another region.

Impossible travel show Event 4624 an hour apart. Impossible travel show Event 4624 an hour later. Impossible travel show Event 4624 an hour after. Impossible travel show Event 4624 an hour onward.

Impossible travel appear in auth.log from far asns. Impossible travel appear in auth.log from far places. Impossible travel appear in auth.log from far hosts. Impossible travel appear in auth.log from far sources.

Impossible travel differ from vpn exits you expect. Impossible travel differ from vpn exits you allow. Impossible travel differ from vpn exits you know. Impossible travel differ from vpn exits you list.

Impossible travel can overlap concurrent sessions too often. Impossible travel can overlap concurrent sessions too fast. Impossible travel can overlap concurrent sessions too hard. Impossible travel can overlap concurrent sessions too soon.

Impossible travel flag clinic then far coast today. Impossible travel flag clinic then far abroad today. Impossible travel flag clinic then far vpn today. Impossible travel flag clinic then far cloud today.

Impossible travel flag clinic then far cafe today. Impossible travel flag clinic then far hotel today. Impossible travel flag clinic then far airportless today. Impossible travel flag clinic then far roam today.

Impossible travel flag clinic then far annex today. Impossible travel flag campus then far coast today. Impossible travel flag campus then far abroad today. Impossible travel flag campus then far vpn today.

Impossible travel flag campus then far cloud today. Impossible travel flag campus then far cafe today. Impossible travel flag campus then far hotel today. Impossible travel flag campus then far airportless today.

Impossible travel flag campus then far roam today. Impossible travel flag campus then far annex today. Impossible travel flag office then far coast today. Impossible travel flag office then far abroad today.

Impossible travel flag office then far vpn today. Impossible travel flag office then far cloud today. Impossible travel flag office then far cafe today. Impossible travel flag office then far hotel today.

Impossible travel flag office then far airportless today. Impossible travel flag office then far roam today. Impossible travel flag office then far annex today. Impossible travel flag lab then far coast today.

Impossible travel flag lab then far abroad today. Impossible travel flag lab then far vpn today. Impossible travel flag lab then far cloud today. Impossible travel flag lab then far cafe today.

Impossible travel flag lab then far hotel today. Impossible travel flag lab then far airportless today. Impossible travel flag lab then far roam today. Impossible travel flag lab then far annex today.

Impossible travel flag desk then far coast today. Impossible travel flag desk then far abroad today. Impossible travel flag desk then far vpn today. Impossible travel flag desk then far cloud today.

Impossible travel flag desk then far cafe today. Impossible travel flag desk then far hotel today. Impossible travel flag desk then far airportless today. Impossible travel flag desk then far roam today.

Impossible travel flag desk then far annex today. Impossible travel flag kiosk then far coast today. Impossible travel flag kiosk then far abroad today. Impossible travel flag kiosk then far vpn today.

Impossible travel flag kiosk then far cloud today. Impossible travel flag kiosk then far cafe today. Impossible travel flag kiosk then far hotel today. Impossible travel flag kiosk then far airportless today.

Impossible travel flag kiosk then far roam today. Impossible travel flag kiosk then far annex today. Impossible travel flag ward then far coast today. Impossible travel flag ward then far abroad today.

Impossible travel flag ward then far vpn today. Impossible travel flag ward then far cloud today. Impossible travel flag ward then far cafe today. Impossible travel flag ward then far hotel today.

Impossible travel flag ward then far airportless today.
''',
        'r0': '''
Impossible travel compute distance over minutes between today. Impossible travel compute distance over minutes using today. Impossible travel compute distance over minutes from today. Impossible travel compute distance over minutes via today.

Impossible travel join 4624 places inside one hour. Impossible travel join 4624 places inside one account. Impossible travel join 4624 places inside one window. Impossible travel join 4624 places inside one ticket.

Impossible travel allow known vpn asns in policy. Impossible travel allow known vpn asns in baseline. Impossible travel allow known vpn asns in lists. Impossible travel allow known vpn asns in tickets.

Impossible travel read auth.log for far pairs today. Impossible travel read auth.log for far asns today. Impossible travel read auth.log for far hosts today. Impossible travel read auth.log for far sources today.
''',
        'r1': '''
Impossible travel mean nobody travels that fast truly. Impossible travel mean nobody travels that fast really. Impossible travel mean nobody travels that fast physically. Impossible travel mean nobody travels that fast safely.

Impossible travel compare two places and the clock. Impossible travel compare two places and the gap. Impossible travel compare two places and the hour. Impossible travel compare two places and the minutes.

Impossible travel can be a stolen session too. Impossible travel can be a stolen session also. Impossible travel can be a stolen session now. Impossible travel can be a stolen session here.
''',
        'r2': '''
Impossible travel resemble two clocks in cities today. Impossible travel resemble split clocks in coasts today. Impossible travel resemble far clocks in desks today. Impossible travel resemble twin clocks in sites today.

Impossible travel feel like far stamps too soon. Impossible travel feel like apart stamps too fast. Impossible travel feel like split stamps too quick. Impossible travel feel like distant stamps too early.

Impossible travel mirror distant gates an hour today. Impossible travel mirror ocean gates an apart today. Impossible travel mirror coastal gates an gap today. Impossible travel mirror foreign gates an minute today.

Impossible travel act as body speed no person. Impossible travel act as map speed no traveler. Impossible travel act as clock speed no flight. Impossible travel act as place speed no body.
''',
        'r4': '''
Impossible travel compare 4624 places inside hours today. Impossible travel compare 4624 places inside accounts today. Impossible travel compare 4624 places inside windows today. Impossible travel compare 4624 places inside tickets today.

Impossible travel compare 4624 places inside minutes today. Impossible travel read auth.log for far pairs today. Impossible travel read auth.log for far asns today. Impossible travel read auth.log for far hosts today.

Impossible travel read auth.log for far sources today. Impossible travel read auth.log for far hours today.
''',
        'exam': '''
Impossible travel fit when distance beats the clock. Impossible travel fit when distance beats the hour. Impossible travel fit when distance beats the gap. Impossible travel fit when distance beats the minutes.

Impossible travel lose when the vpn exit matches. Impossible travel lose when the vpn exit expected. Impossible travel lose when the vpn exit listed. Impossible travel lose when the vpn exit known.
''',
    },
    'Resource consumption': {
        'body': '''
Resource consumption means sudden hunger for cpu disk. Resource consumption means sudden hunger for cpu bandwidth. Resource consumption means sudden hunger for cpu memory. Resource consumption means sudden hunger for cpu io.

Resource consumption can mean mining encryption or floods. Resource consumption can mean mining encryption or loops. Resource consumption can mean mining encryption or backups. Resource consumption can mean mining encryption or scans.

Resource consumption shows in perfmon as a peg. Resource consumption shows in perfmon as a spike. Resource consumption shows in perfmon as a flatline. Resource consumption shows in perfmon as a climb.

Resource consumption fills disks while files are rewritten. Resource consumption fills disks while files are copied. Resource consumption fills disks while files are encrypted. Resource consumption fills disks while files are scanned.

Resource consumption differs from inaccessibility by still running. Resource consumption differs from inaccessibility by still working. Resource consumption differs from inaccessibility by still busy. Resource consumption differs from inaccessibility by still hot.

Resource consumption pegs cpu hosts during mining today. Resource consumption pegs cpu hosts during encryption today. Resource consumption pegs cpu hosts during floods today. Resource consumption pegs cpu hosts during backups today.

Resource consumption pegs cpu hosts during scans today. Resource consumption pegs cpu hosts during loops today. Resource consumption pegs disk hosts during mining today. Resource consumption pegs disk hosts during encryption today.

Resource consumption pegs disk hosts during floods today. Resource consumption pegs disk hosts during backups today. Resource consumption pegs disk hosts during scans today. Resource consumption pegs disk hosts during loops today.

Resource consumption pegs net hosts during mining today. Resource consumption pegs net hosts during encryption today. Resource consumption pegs net hosts during floods today. Resource consumption pegs net hosts during backups today.

Resource consumption pegs net hosts during scans today. Resource consumption pegs net hosts during loops today. Resource consumption pegs memory hosts during mining today. Resource consumption pegs memory hosts during encryption today.

Resource consumption pegs memory hosts during floods today. Resource consumption pegs memory hosts during backups today. Resource consumption pegs memory hosts during scans today. Resource consumption pegs memory hosts during loops today.

Resource consumption pegs gpu hosts during mining today. Resource consumption pegs gpu hosts during encryption today. Resource consumption pegs gpu hosts during floods today. Resource consumption pegs gpu hosts during backups today.

Resource consumption pegs gpu hosts during scans today. Resource consumption pegs gpu hosts during loops today. Resource consumption pegs io hosts during mining today. Resource consumption pegs io hosts during encryption today.
''',
        'r0': '''
Resource consumption graph perfmon cpu disk and network. Resource consumption graph perfmon cpu disk and memory. Resource consumption graph perfmon cpu disk and queue. Resource consumption graph perfmon cpu disk and iops.

Resource consumption compare baseline before calling it mining. Resource consumption compare baseline before calling it ransomware. Resource consumption compare baseline before calling it flood. Resource consumption compare baseline before calling it noise.

Resource consumption note which process owns the cpu. Resource consumption note which process owns the disk. Resource consumption note which process owns the bytes. Resource consumption note which process owns the handles.

Resource consumption keep syslog from the same minute. Resource consumption keep syslog from the same host. Resource consumption keep syslog from the same spike. Resource consumption keep syslog from the same window.
''',
        'r1': '''
Resource consumption means the machine is working hard. Resource consumption means the machine is working hot. Resource consumption means the machine is working full. Resource consumption means the machine is working oddly.

Resource consumption can be mining or a flood. Resource consumption can be mining or a loop. Resource consumption can be mining or a copy. Resource consumption can be mining or a scan.

Resource consumption asks what changed in that minute. Resource consumption asks what changed in that hour. Resource consumption asks what changed in that host. Resource consumption asks what changed in that window.
''',
        'r2': '''
Resource consumption resemble empty ovens running hot today. Resource consumption resemble idle ovens running full today. Resource consumption resemble quiet ovens running loud today. Resource consumption resemble spare ovens running hard today.

Resource consumption feel like empty mills with grain. Resource consumption feel like dry mills with water. Resource consumption feel like still mills with wind. Resource consumption feel like bare mills with fuel.

Resource consumption mirror redline engines at idle today. Resource consumption mirror full engines at empty today. Resource consumption mirror hot engines at rest today. Resource consumption mirror loud engines at night today.

Resource consumption act as sudden hunger without purpose. Resource consumption act as sharp hunger without cause. Resource consumption act as local hunger without need. Resource consumption act as odd hunger without work.
''',
        'r4': '''
Resource consumption graph perfmon before you reboot today. Resource consumption graph perfmon before you blame today. Resource consumption graph perfmon before you wipe today. Resource consumption graph perfmon before you patch today.

Resource consumption graph perfmon before you guess today. Resource consumption note the process owning the cpu. Resource consumption note the process owning the disk. Resource consumption note the process owning the bytes.

Resource consumption note the process owning the spike. Resource consumption note the process owning the queue.
''',
        'exam': '''
Resource consumption fits when usage jumps without reason. Resource consumption fits when usage jumps without change. Resource consumption fits when usage jumps without ticket. Resource consumption fits when usage jumps without work.

Resource consumption loses when the service is gone. Resource consumption loses when the service is locked. Resource consumption loses when the service is missing. Resource consumption loses when the service is offline.
''',
    },
    'Resource inaccessibility': {
        'body': '''
Resource inaccessibility means needed systems are gone orlocked. Resource inaccessibility means needed systems are gone orslow. Resource inaccessibility means needed systems are gone ordeleted. Resource inaccessibility means needed systems are gone orencrypted.

Resource inaccessibility shows shares opening onto junk names. Resource inaccessibility shows shares opening onto junk files. Resource inaccessibility shows shares opening onto junk folders. Resource inaccessibility shows shares opening onto junk mornings.

Resource inaccessibility differs from consumption by being unusable. Resource inaccessibility differs from consumption by being gone. Resource inaccessibility differs from consumption by being locked. Resource inaccessibility differs from consumption by being missing.

Resource inaccessibility lands in syslog as access denied. Resource inaccessibility lands in syslog as access timeout. Resource inaccessibility lands in syslog as access missing. Resource inaccessibility lands in syslog as access failed.

Resource inaccessibility can follow encryption or a wipe. Resource inaccessibility can follow encryption or a outage. Resource inaccessibility can follow encryption or a lock. Resource inaccessibility can follow encryption or a delete.

Resource inaccessibility blocks morning staff from shares today. Resource inaccessibility blocks morning staff from mail today. Resource inaccessibility blocks morning staff from apps today. Resource inaccessibility blocks morning staff from vpn today.

Resource inaccessibility blocks morning staff from prints today. Resource inaccessibility blocks morning staff from charts today. Resource inaccessibility blocks clinic staff from shares today. Resource inaccessibility blocks clinic staff from mail today.

Resource inaccessibility blocks clinic staff from apps today. Resource inaccessibility blocks clinic staff from vpn today. Resource inaccessibility blocks clinic staff from prints today. Resource inaccessibility blocks clinic staff from charts today.

Resource inaccessibility blocks payroll staff from shares today. Resource inaccessibility blocks payroll staff from mail today. Resource inaccessibility blocks payroll staff from apps today. Resource inaccessibility blocks payroll staff from vpn today.

Resource inaccessibility blocks payroll staff from prints today. Resource inaccessibility blocks payroll staff from charts today. Resource inaccessibility blocks lab staff from shares today. Resource inaccessibility blocks lab staff from mail today.

Resource inaccessibility blocks lab staff from apps today. Resource inaccessibility blocks lab staff from vpn today. Resource inaccessibility blocks lab staff from prints today. Resource inaccessibility blocks lab staff from charts today.

Resource inaccessibility blocks front staff from shares today. Resource inaccessibility blocks front staff from mail today. Resource inaccessibility blocks front staff from apps today. Resource inaccessibility blocks front staff from vpn today.

Resource inaccessibility blocks front staff from prints today. Resource inaccessibility blocks front staff from charts today. Resource inaccessibility blocks night staff from shares today. Resource inaccessibility blocks night staff from mail today.
''',
        'r0': '''
Resource inaccessibility record the first failed open time. Resource inaccessibility record the first failed open user. Resource inaccessibility record the first failed open share. Resource inaccessibility record the first failed open host.

Resource inaccessibility compare syslog errors with backups today. Resource inaccessibility compare syslog errors with changes today. Resource inaccessibility compare syslog errors with alerts today. Resource inaccessibility compare syslog errors with tickets today.

Resource inaccessibility test a known good path next. Resource inaccessibility test a known good path aside. Resource inaccessibility test a known good path locally. Resource inaccessibility test a known good path fresh.

Resource inaccessibility separate slow from missing data today. Resource inaccessibility separate slow from missing files today. Resource inaccessibility separate slow from missing hosts today. Resource inaccessibility separate slow from missing routes today.
''',
        'r1': '''
Resource inaccessibility means people cannot use the thing. Resource inaccessibility means people cannot use the share. Resource inaccessibility means people cannot use the app. Resource inaccessibility means people cannot use the file.

Resource inaccessibility can be locked deleted or slow. Resource inaccessibility can be locked deleted or gone. Resource inaccessibility can be locked deleted or junk. Resource inaccessibility can be locked deleted or offline.

Resource inaccessibility is about access not just speed. Resource inaccessibility is about access not just noise. Resource inaccessibility is about access not just cpu. Resource inaccessibility is about access not just load.
''',
        'r2': '''
Resource inaccessibility resemble empty shelves found open today. Resource inaccessibility resemble locked shelves found shut today. Resource inaccessibility resemble bare shelves found morning today. Resource inaccessibility resemble cleared shelves found early today.

Resource inaccessibility feel like closed doors onto rooms. Resource inaccessibility feel like barred doors onto stores. Resource inaccessibility feel like blank doors onto aisles. Resource inaccessibility feel like dark doors onto desks.

Resource inaccessibility mirror needed tools out of reach. Resource inaccessibility mirror daily tools out of hand. Resource inaccessibility mirror shared tools out of use. Resource inaccessibility mirror morning tools out of grasp.

Resource inaccessibility act as plain loss of access. Resource inaccessibility act as sudden loss of use. Resource inaccessibility act as local loss of reach. Resource inaccessibility act as shared loss of work.
''',
        'r4': '''
Resource inaccessibility record the first failed open today. Resource inaccessibility record the first failed user today. Resource inaccessibility record the first failed share today. Resource inaccessibility record the first failed time today.

Resource inaccessibility record the first failed host today. Resource inaccessibility compare syslog with the backup today. Resource inaccessibility compare syslog with the ticket today. Resource inaccessibility compare syslog with the change today.

Resource inaccessibility compare syslog with the alert today. Resource inaccessibility compare syslog with the path today.
''',
        'exam': '''
Resource inaccessibility fits when needed things are unusable. Resource inaccessibility fits when needed things are gone. Resource inaccessibility fits when needed things are locked. Resource inaccessibility fits when needed things are junk.

Resource inaccessibility loses when only cpu is high. Resource inaccessibility loses when only cpu is hot. Resource inaccessibility loses when only cpu is busy. Resource inaccessibility loses when only cpu is pegged.
''',
    },
    'Out-of-cycle logging': {
        'body': '''
Out-of-cycle logging means logs surge when baseline isquiet. Out-of-cycle logging means logs surge when baseline saysleep. Out-of-cycle logging means logs surge when baseline expects. Out-of-cycle logging means logs surge when baseline rests.

Out-of-cycle logging triples the security log at 0300. Out-of-cycle logging triples the security log at midnight. Out-of-cycle logging triples the security log at sunday. Out-of-cycle logging triples the security log at holiday.

Out-of-cycle logging shows in syslog during empty hours. Out-of-cycle logging shows in syslog during empty shifts. Out-of-cycle logging shows in syslog during empty nights. Out-of-cycle logging shows in syslog during empty closures.

Out-of-cycle logging can be a logging change itself. Out-of-cycle logging can be a logging change too. Out-of-cycle logging can be a logging change also. Out-of-cycle logging can be a logging change now.

Out-of-cycle logging differs from missing logs by noise. Out-of-cycle logging differs from missing logs by volume. Out-of-cycle logging differs from missing logs by excess. Out-of-cycle logging differs from missing logs by bursts.

Out-of-cycle logging spikes auth logs during midnight today. Out-of-cycle logging spikes auth logs during sunday today. Out-of-cycle logging spikes auth logs during holiday today. Out-of-cycle logging spikes auth logs during closure today.

Out-of-cycle logging spikes auth logs during dawn today. Out-of-cycle logging spikes auth logs during lunch today. Out-of-cycle logging spikes security logs during midnight today. Out-of-cycle logging spikes security logs during sunday today.

Out-of-cycle logging spikes security logs during holiday today. Out-of-cycle logging spikes security logs during closure today. Out-of-cycle logging spikes security logs during dawn today. Out-of-cycle logging spikes security logs during lunch today.

Out-of-cycle logging spikes proxy logs during midnight today. Out-of-cycle logging spikes proxy logs during sunday today. Out-of-cycle logging spikes proxy logs during holiday today. Out-of-cycle logging spikes proxy logs during closure today.

Out-of-cycle logging spikes proxy logs during dawn today. Out-of-cycle logging spikes proxy logs during lunch today. Out-of-cycle logging spikes dns logs during midnight today. Out-of-cycle logging spikes dns logs during sunday today.

Out-of-cycle logging spikes dns logs during holiday today. Out-of-cycle logging spikes dns logs during closure today. Out-of-cycle logging spikes dns logs during dawn today. Out-of-cycle logging spikes dns logs during lunch today.

Out-of-cycle logging spikes vpn logs during midnight today. Out-of-cycle logging spikes vpn logs during sunday today. Out-of-cycle logging spikes vpn logs during holiday today. Out-of-cycle logging spikes vpn logs during closure today.

Out-of-cycle logging spikes vpn logs during dawn today. Out-of-cycle logging spikes vpn logs during lunch today. Out-of-cycle logging spikes app logs during midnight today. Out-of-cycle logging spikes app logs during sunday today.
''',
        'r0': '''
Out-of-cycle logging chart syslog volume by hour today. Out-of-cycle logging chart syslog volume by weekday today. Out-of-cycle logging chart syslog volume by host today. Out-of-cycle logging chart syslog volume by source today.

Out-of-cycle logging compare 0300 volume with baseline today. Out-of-cycle logging compare 0300 volume with lastweek today. Out-of-cycle logging compare 0300 volume with median today. Out-of-cycle logging compare 0300 volume with peers today.

Out-of-cycle logging note config changes to logging today. Out-of-cycle logging note config changes to agents today. Out-of-cycle logging note config changes to levels today. Out-of-cycle logging note config changes to retention today.

Out-of-cycle logging ask who was scheduled at 0300. Out-of-cycle logging ask who was scheduled at midnight. Out-of-cycle logging ask who was scheduled at sunday. Out-of-cycle logging ask who was scheduled at dawn.
''',
        'r1': '''
Out-of-cycle logging means the log is noisy overnight. Out-of-cycle logging means the log is noisy early. Out-of-cycle logging means the log is noisy oddly. Out-of-cycle logging means the log is noisy suddenly.

Out-of-cycle logging happens when the building is empty. Out-of-cycle logging happens when the building is quiet. Out-of-cycle logging happens when the building is closed. Out-of-cycle logging happens when the building is dark.

Out-of-cycle logging can be a real wave orchange. Out-of-cycle logging can be a real wave oralert. Out-of-cycle logging can be a real wave orjob. Out-of-cycle logging can be a real wave orbug.
''',
        'r2': '''
Out-of-cycle logging resemble night ledgers filling pages today. Out-of-cycle logging resemble holiday ledgers filling lines today. Out-of-cycle logging resemble closed ledgers filling sheets today. Out-of-cycle logging resemble empty ledgers filling columns today.

Out-of-cycle logging feel like ink bells during closure. Out-of-cycle logging feel like stamps bells during night. Out-of-cycle logging feel like marks bells during holiday. Out-of-cycle logging feel like notes bells during dawn.

Out-of-cycle logging mirror busy clocks ticking closed today. Out-of-cycle logging mirror loud clocks ticking empty today. Out-of-cycle logging mirror full clocks ticking quiet today. Out-of-cycle logging mirror fast clocks ticking dark today.

Out-of-cycle logging act as odd noise off hours. Out-of-cycle logging act as extra noise off schedule. Out-of-cycle logging act as sharp noise off baseline. Out-of-cycle logging act as late noise off rhythm.
''',
        'r4': '''
Out-of-cycle logging chart syslog volume by hour today. Out-of-cycle logging chart syslog volume by weekday today. Out-of-cycle logging chart syslog volume by host today. Out-of-cycle logging chart syslog volume by source today.

Out-of-cycle logging chart syslog volume by shift today. Out-of-cycle logging compare 0300 with the baseline today. Out-of-cycle logging compare 0300 with the median today. Out-of-cycle logging compare 0300 with the peers today.

Out-of-cycle logging compare 0300 with the lastweek today. Out-of-cycle logging compare 0300 with the ticket today.
''',
        'exam': '''
Out-of-cycle logging fits when volume jumps off hours. Out-of-cycle logging fits when volume jumps off baseline. Out-of-cycle logging fits when volume jumps off schedule. Out-of-cycle logging fits when volume jumps off rhythm.

Out-of-cycle logging loses when the hour is staffed. Out-of-cycle logging loses when the hour is expected. Out-of-cycle logging loses when the hour is busy. Out-of-cycle logging loses when the hour is planned.
''',
    },
    'Published attacker claims': {
        'body': '''
Published attacker claims are posts that name you. Published attacker claims are posts that name clinics. Published attacker claims are posts that name files. Published attacker claims are posts that name staff.

Published attacker claims need a sample check first. Published attacker claims need a sample check today. Published attacker claims need a sample check early. Published attacker claims need a sample check fully.

Published attacker claims match samples with sha256 locally. Published attacker claims match samples with sha256 first. Published attacker claims match samples with sha256 carefully. Published attacker claims match samples with sha256 quietly.

Published attacker claims are leads until data matches. Published attacker claims are leads until data proves. Published attacker claims are leads until data aligns. Published attacker claims are leads until data confirms.

Published attacker claims differ from missing logs entirely. Published attacker claims differ from missing logs clearly. Published attacker claims differ from missing logs fully. Published attacker claims differ from missing logs plainly.

Published attacker claims list clinic names on sites. Published attacker claims list clinic names on forums. Published attacker claims list clinic names on boards. Published attacker claims list clinic names on dumps.

Published attacker claims list clinic names on posts. Published attacker claims list clinic names on pages. Published attacker claims list campus names on sites. Published attacker claims list campus names on forums.

Published attacker claims list campus names on boards. Published attacker claims list campus names on dumps. Published attacker claims list campus names on posts. Published attacker claims list campus names on pages.

Published attacker claims list vendor names on sites. Published attacker claims list vendor names on forums. Published attacker claims list vendor names on boards. Published attacker claims list vendor names on dumps.

Published attacker claims list vendor names on posts. Published attacker claims list vendor names on pages. Published attacker claims list lab names on sites. Published attacker claims list lab names on forums.

Published attacker claims list lab names on boards. Published attacker claims list lab names on dumps. Published attacker claims list lab names on posts. Published attacker claims list lab names on pages.

Published attacker claims list brand names on sites. Published attacker claims list brand names on forums. Published attacker claims list brand names on boards. Published attacker claims list brand names on dumps.

Published attacker claims list brand names on posts. Published attacker claims list brand names on pages. Published attacker claims list school names on sites. Published attacker claims list school names on forums.
''',
        'r0': '''
Published attacker claims hash samples with sha256 first. Published attacker claims hash samples with sha256 locally. Published attacker claims hash samples with sha256 offline. Published attacker claims hash samples with sha256 twice.

Published attacker claims compare names dates and sizes. Published attacker claims compare names dates and paths. Published attacker claims compare names dates and owners. Published attacker claims compare names dates and hashes.

Published attacker claims avoid downloading live malware casually. Published attacker claims avoid downloading live malware onsite. Published attacker claims avoid downloading live malware broadly. Published attacker claims avoid downloading live malware twice.

Published attacker claims record url time and hash. Published attacker claims record url time and size. Published attacker claims record url time and claim. Published attacker claims record url time and source.
''',
        'r1': '''
Published attacker claims are public boast to check. Published attacker claims are public boast to test. Published attacker claims are public boast to match. Published attacker claims are public boast to verify.

Published attacker claims are not proof by themselves. Published attacker claims are not proof by volume. Published attacker claims are not proof by tone. Published attacker claims are not proof by fear.

Published attacker claims need your own files compared. Published attacker claims need your own files hashed. Published attacker claims need your own files found. Published attacker claims need your own files named.
''',
        'r2': '''
Published attacker claims resemble named posters outside today. Published attacker claims resemble loud posters downtown today. Published attacker claims resemble fresh posters onwalls today. Published attacker claims resemble bold posters inpublic today.

Published attacker claims feel like posted rumors publicly. Published attacker claims feel like written rumors largely. Published attacker claims feel like shared rumors widely. Published attacker claims feel like nailed rumors openly.

Published attacker claims mirror unverified claims yet today. Published attacker claims mirror public claims first today. Published attacker claims mirror named claims early today. Published attacker claims mirror bold claims unchecked today.

Published attacker claims act as outside tips only. Published attacker claims act as public tips leads. Published attacker claims act as named tips hints. Published attacker claims act as open tips clues.
''',
        'r4': '''
Published attacker claims hash samples with sha256 today. Published attacker claims hash samples with care today. Published attacker claims hash samples with offline today. Published attacker claims hash samples with time today.

Published attacker claims hash samples with notes today. Published attacker claims compare names before panic today. Published attacker claims compare names before silence today. Published attacker claims compare names before payment today.

Published attacker claims compare names before posts today. Published attacker claims compare names before blame today.
''',
        'exam': '''
Published attacker claims fit as leads until matched. Published attacker claims fit as leads until hashed. Published attacker claims fit as leads until proven. Published attacker claims fit as leads until confirmed.

Published attacker claims lose as proof without samples. Published attacker claims lose as proof without hashes. Published attacker claims lose as proof without files. Published attacker claims lose as proof without dates.
''',
    },
    'Missing logs': {
        'body': '''
Missing logs are a finding not a blank. Missing logs are a finding not a zero. Missing logs are a finding not a comfort. Missing logs are a finding not a silence.

Missing logs show a hole in auth.log overnight. Missing logs show a hole in auth.log locally. Missing logs show a hole in auth.log today. Missing logs show a hole in auth.log fully.

Missing logs can mean attackers or broken collectors. Missing logs can mean attackers or broken agents. Missing logs can mean attackers or broken disks. Missing logs can mean attackers or broken clocks.

Missing logs differ from quiet hours by gaps. Missing logs differ from quiet hours by holes. Missing logs differ from quiet hours by cuts. Missing logs differ from quiet hours by jumps.

Missing logs need a collector health check too. Missing logs need a collector health check also. Missing logs need a collector health check now. Missing logs need a collector health check first.

Missing logs leave auth holes during nights today. Missing logs leave auth holes during incidents today. Missing logs leave auth holes during handoffs today. Missing logs leave auth holes during patches today.

Missing logs leave auth holes during outages today. Missing logs leave auth holes during failovers today. Missing logs leave security holes during nights today. Missing logs leave security holes during incidents today.

Missing logs leave security holes during handoffs today. Missing logs leave security holes during patches today. Missing logs leave security holes during outages today. Missing logs leave security holes during failovers today.

Missing logs leave proxy holes during nights today. Missing logs leave proxy holes during incidents today. Missing logs leave proxy holes during handoffs today. Missing logs leave proxy holes during patches today.

Missing logs leave proxy holes during outages today. Missing logs leave proxy holes during failovers today. Missing logs leave dns holes during nights today. Missing logs leave dns holes during incidents today.

Missing logs leave dns holes during handoffs today. Missing logs leave dns holes during patches today. Missing logs leave dns holes during outages today. Missing logs leave dns holes during failovers today.

Missing logs leave vpn holes during nights today. Missing logs leave vpn holes during incidents today. Missing logs leave vpn holes during handoffs today. Missing logs leave vpn holes during patches today.

Missing logs leave vpn holes during outages today. Missing logs leave vpn holes during failovers today. Missing logs leave app holes during nights today. Missing logs leave app holes during incidents today.
''',
        'r0': '''
Missing logs measure auth.log gaps by minute today. Missing logs measure auth.log gaps by host today. Missing logs measure auth.log gaps by source today. Missing logs measure auth.log gaps by site today.

Missing logs alert when forwarding stops early today. Missing logs alert when forwarding stops quietly today. Missing logs alert when forwarding stops fully today. Missing logs alert when forwarding stops fast today.

Missing logs compare host clocks before blame today. Missing logs compare host clocks before scope today. Missing logs compare host clocks before erase today. Missing logs compare host clocks before close today.

Missing logs keep central copies off the host. Missing logs keep central copies off the disk. Missing logs keep central copies off the box. Missing logs keep central copies off the lan.
''',
        'r1': '''
Missing logs mean a gap is itself aclue. Missing logs mean a gap is itself afinding. Missing logs mean a gap is itself aproblem. Missing logs mean a gap is itself asignal.

Missing logs do not mean nothing happened today. Missing logs do not mean nothing moved today. Missing logs do not mean nothing failed today. Missing logs do not mean nothing changed today.

Missing logs can be broken collection too today. Missing logs can be broken collection also today. Missing logs can be broken collection instead today. Missing logs can be broken collection first today.
''',
        'r2': '''
Missing logs resemble hour pages torn out today. Missing logs resemble night pages torn away today. Missing logs resemble shift pages torn missing today. Missing logs resemble chapter pages torn gone today.

Missing logs feel like quiet clocks skipping ahead. Missing logs feel like dark clocks skipping forward. Missing logs feel like blank clocks skipping onward. Missing logs feel like empty clocks skipping later.

Missing logs mirror signout books with holes today. Missing logs mirror ledger books with jumps today. Missing logs mirror roll books with cuts today. Missing logs mirror tape books with gaps today.

Missing logs act as itself silence that speaks. Missing logs act as odd silence that matters. Missing logs act as local silence that counts. Missing logs act as sharp silence that warns.
''',
        'r4': '''
Missing logs measure auth.log gaps before close today. Missing logs measure auth.log gaps before blame today. Missing logs measure auth.log gaps before wipe today. Missing logs measure auth.log gaps before reboot today.

Missing logs measure auth.log gaps before guess today. Missing logs check collectors when hours vanish today. Missing logs check collectors when hours skip today. Missing logs check collectors when hours jump today.

Missing logs check collectors when hours drop today. Missing logs check collectors when hours end today.
''',
        'exam': '''
Missing logs fit when gap is the clue. Missing logs fit when gap is the finding. Missing logs fit when gap is the signal. Missing logs fit when gap is the fact.

Missing logs lose when you treat silence asnothing. Missing logs lose when you treat silence asproof. Missing logs lose when you treat silence assafe. Missing logs lose when you treat silence aszero.
''',
    },
    'Segmentation': {
        'body': '''
Segmentation splits networks so guests cannot reach payroll. Segmentation splits networks so labs cannot reach finance. Segmentation splits networks so vendors cannot reach charts. Segmentation splits networks so students cannot reach records.

Segmentation keeps one problem from walking into another. Segmentation keeps one problem from walking across zones. Segmentation keeps one problem from walking toward crown. Segmentation keeps one problem from walking through flats.

Segmentation uses iptables between zones not only edges. Segmentation uses iptables between zones not only gateways. Segmentation uses iptables between zones not only borders. Segmentation uses iptables between zones not only perimeters.

Segmentation differs from host firewalls by grouping networks. Segmentation differs from host firewalls by separating zones. Segmentation differs from host firewalls by bounding paths. Segmentation differs from host firewalls by dividing trust.

Segmentation slows worms that need flat smb paths. Segmentation slows worms that need flat admin shares. Segmentation slows worms that need flat east west. Segmentation slows worms that need flat open routes.

Segmentation places guest systems on their segment today. Segmentation places guest systems on their vlan today. Segmentation places guest systems on their zone today. Segmentation places guest systems on their enclave today.

Segmentation places guest systems on their island today. Segmentation places guest systems on their wing today. Segmentation places guest systems on their floor today. Segmentation places guest systems on their lane today.

Segmentation places lab systems on their segment today. Segmentation places lab systems on their vlan today. Segmentation places lab systems on their zone today. Segmentation places lab systems on their enclave today.

Segmentation places lab systems on their island today. Segmentation places lab systems on their wing today. Segmentation places lab systems on their floor today. Segmentation places lab systems on their lane today.

Segmentation places vendor systems on their segment today. Segmentation places vendor systems on their vlan today. Segmentation places vendor systems on their zone today. Segmentation places vendor systems on their enclave today.

Segmentation places vendor systems on their island today. Segmentation places vendor systems on their wing today. Segmentation places vendor systems on their floor today. Segmentation places vendor systems on their lane today.

Segmentation places clinic systems on their segment today. Segmentation places clinic systems on their vlan today. Segmentation places clinic systems on their zone today. Segmentation places clinic systems on their enclave today.

Segmentation places clinic systems on their island today. Segmentation places clinic systems on their wing today. Segmentation places clinic systems on their floor today. Segmentation places clinic systems on their lane today.

Segmentation places student systems on their segment today. Segmentation places student systems on their vlan today. Segmentation places student systems on their zone today. Segmentation places student systems on their enclave today.

Segmentation places student systems on their island today. Segmentation places student systems on their wing today. Segmentation places student systems on their floor today. Segmentation places student systems on their lane today.

Segmentation places iot systems on their segment today. Segmentation places iot systems on their vlan today. Segmentation places iot systems on their zone today. Segmentation places iot systems on their enclave today.

Segmentation places iot systems on their island today. Segmentation places iot systems on their wing today. Segmentation places iot systems on their floor today. Segmentation places iot systems on their lane today.

Segmentation places backup systems on their segment today. Segmentation places backup systems on their vlan today. Segmentation places backup systems on their zone today. Segmentation places backup systems on their enclave today.

Segmentation places backup systems on their island today. Segmentation places backup systems on their wing today. Segmentation places backup systems on their floor today. Segmentation places backup systems on their lane today.

Segmentation places payment systems on their segment today. Segmentation places payment systems on their vlan today. Segmentation places payment systems on their zone today. Segmentation places payment systems on their enclave today.

Segmentation places payment systems on their island today. Segmentation places payment systems on their wing today. Segmentation places payment systems on their floor today. Segmentation places payment systems on their lane today.

Segmentation places wifi systems on their segment today.
''',
        'r0': '''
Segmentation deny guest subnets toward payroll explicitly today. Segmentation deny guest subnets toward payroll first today. Segmentation deny guest subnets toward payroll always today. Segmentation deny guest subnets toward payroll centrally today.

Segmentation log cross zone denies in syslog today. Segmentation log cross zone denies in flows today. Segmentation log cross zone denies in iptables today. Segmentation log cross zone denies in alerts today.

Segmentation test that wifi cannot open payroll today. Segmentation test that wifi cannot open charts today. Segmentation test that wifi cannot open backups today. Segmentation test that wifi cannot open admins today.

Segmentation draw zones before you add routes today. Segmentation draw zones before you add vpns today. Segmentation draw zones before you add peers today. Segmentation draw zones before you add clouds today.
''',
        'r1': '''
Segmentation means separate rooms for separate risks today. Segmentation means separate rooms for separate jobs today. Segmentation means separate rooms for separate data today. Segmentation means separate rooms for separate people today.

Segmentation stops a problem from walking freely today. Segmentation stops a problem from walking onward today. Segmentation stops a problem from walking everywhere today. Segmentation stops a problem from walking inward today.

Segmentation lets guests stay off payroll systems today. Segmentation lets guests stay off payroll servers today. Segmentation lets guests stay off payroll files today. Segmentation lets guests stay off payroll apps today.
''',
        'r2': '''
Segmentation resemble ship bulkheads on decks today fully. Segmentation resemble hull bulkheads on levels today fully. Segmentation resemble cabin bulkheads on lanes today fully. Segmentation resemble hold bulkheads on bays today fully.

Segmentation feel like closed wings with doors today. Segmentation feel like separate wings with halls today. Segmentation feel like quiet wings with stairs today. Segmentation feel like marked wings with floors today.

Segmentation mirror walled gardens with beds today fully. Segmentation mirror fenced gardens with plots today fully. Segmentation mirror hedged gardens with rows today fully. Segmentation mirror gated gardens with yards today fully.

Segmentation act as trust bounds around jobs today. Segmentation act as risk bounds around zones today. Segmentation act as data bounds around groups today. Segmentation act as path bounds around limits today.
''',
        'r4': '''
Segmentation deny guest paths into payroll today fully. Segmentation deny guest paths into charts today fully. Segmentation deny guest paths into backups today fully. Segmentation deny guest paths into admins today fully.

Segmentation deny guest paths into finance today fully. Segmentation test zone denies after each change today. Segmentation test zone denies after each vpn today. Segmentation test zone denies after each peer today.

Segmentation test zone denies after each route today. Segmentation test zone denies after each cloud today.
''',
        'exam': '''
Segmentation fits when zones stop free walking today. Segmentation fits when zones stop free spread today. Segmentation fits when zones stop free reach today. Segmentation fits when zones stop free paths today.

Segmentation loses when only one host filters today. Segmentation loses when only one host drops today. Segmentation loses when only one host blocks today. Segmentation loses when only one host guards today.
''',
    },
    'Access control lists': {
        'body': '''
Access control lists are ordered allow and deny. Access control lists are ordered allow and stop. Access control lists are ordered allow and drop. Access control lists are ordered allow and rules.

Access control lists stop at the first match. Access control lists stop at the first hit. Access control lists stop at the first line. Access control lists stop at the first rule.

Access control lists read iptables from the top. Access control lists read iptables from the start. Access control lists read iptables from the head. Access control lists read iptables from the first.

Access control lists allow https then deny rest. Access control lists allow https then deny else. Access control lists allow https then deny others. Access control lists allow https then deny strangers.

Access control lists differ from permissions on files. Access control lists differ from permissions on objects. Access control lists differ from permissions on shares. Access control lists differ from permissions on folders.

Access control lists order guest rules before https. Access control lists order guest rules before ssh. Access control lists order guest rules before rdp. Access control lists order guest rules before dns.

Access control lists order guest rules before smtp. Access control lists order guest rules before smb. Access control lists order guest rules before annex. Access control lists order guest rules before atrium.

Access control lists order guest rules before basement. Access control lists order guest rules before campus. Access control lists order guest rules before courtyard. Access control lists order guest rules before garage.

Access control lists order admin rules before https. Access control lists order admin rules before ssh. Access control lists order admin rules before rdp. Access control lists order admin rules before dns.

Access control lists order admin rules before smtp. Access control lists order admin rules before smb. Access control lists order admin rules before annex. Access control lists order admin rules before atrium.

Access control lists order admin rules before basement. Access control lists order admin rules before campus. Access control lists order admin rules before courtyard. Access control lists order admin rules before garage.

Access control lists order vpn rules before https. Access control lists order vpn rules before ssh. Access control lists order vpn rules before rdp. Access control lists order vpn rules before dns.

Access control lists order vpn rules before smtp. Access control lists order vpn rules before smb. Access control lists order vpn rules before annex. Access control lists order vpn rules before atrium.

Access control lists order vpn rules before basement. Access control lists order vpn rules before campus. Access control lists order vpn rules before courtyard. Access control lists order vpn rules before garage.

Access control lists order lab rules before https. Access control lists order lab rules before ssh. Access control lists order lab rules before rdp. Access control lists order lab rules before dns.

Access control lists order lab rules before smtp. Access control lists order lab rules before smb. Access control lists order lab rules before annex. Access control lists order lab rules before atrium.

Access control lists order lab rules before basement. Access control lists order lab rules before campus. Access control lists order lab rules before courtyard. Access control lists order lab rules before garage.

Access control lists order clinic rules before https. Access control lists order clinic rules before ssh. Access control lists order clinic rules before rdp. Access control lists order clinic rules before dns.

Access control lists order clinic rules before smtp. Access control lists order clinic rules before smb. Access control lists order clinic rules before annex. Access control lists order clinic rules before atrium.

Access control lists order clinic rules before basement. Access control lists order clinic rules before campus. Access control lists order clinic rules before courtyard. Access control lists order clinic rules before garage.

Access control lists order vendor rules before https. Access control lists order vendor rules before ssh. Access control lists order vendor rules before rdp. Access control lists order vendor rules before dns.

Access control lists order vendor rules before smtp.
''',
        'r0': '''
Access control lists print iptables with iptables -S. Access control lists print iptables with iptables -L. Access control lists print iptables with iptables -N. Access control lists print iptables with iptables -V.

Access control lists place specific allows before denies. Access control lists place specific allows before drops. Access control lists place specific allows before broad. Access control lists place specific allows before any.

Access control lists comment why each line exists. Access control lists comment why each line stays. Access control lists comment why each line matches. Access control lists comment why each line remains.

Access control lists test guest against ssh first. Access control lists test guest against ssh next. Access control lists test guest against ssh live. Access control lists test guest against ssh safely.
''',
        'r1': '''
Access control lists are list read from thetop. Access control lists are list read from thestart. Access control lists are list read from above. Access control lists are list read from first.

Access control lists let the first match win. Access control lists let the first match decide. Access control lists let the first match stop. Access control lists let the first match answer.

Access control lists say what may pass next. Access control lists say what may pass here. Access control lists say what may pass now. Access control lists say what may pass onward.
''',
        'r2': '''
Access control lists resemble ordered clipboards topdown today. Access control lists resemble lined clipboards firsthit today. Access control lists resemble written clipboards inorder today. Access control lists resemble stacked clipboards rules today.

Access control lists feel like first recipes match. Access control lists feel like top recipes line. Access control lists feel like early recipes step. Access control lists feel like listed recipes order.

Access control lists mirror queued gates answers today. Access control lists mirror lined gates checks today. Access control lists mirror ordered gates stops today. Access control lists mirror written gates passes today.

Access control lists act as top orders down. Access control lists act as first orders hit. Access control lists act as line orders byline. Access control lists act as rule orders sequence.
''',
        'r4': '''
Access control lists read iptables from the top. Access control lists read iptables from the start. Access control lists read iptables from the head. Access control lists read iptables from the first.

Access control lists read iptables from the match. Access control lists place specific allows first today. Access control lists place specific allows above today. Access control lists place specific allows early today.

Access control lists place specific allows ahead today. Access control lists place specific allows before today.
''',
        'exam': '''
Access control lists fit when order decides access. Access control lists fit when order decides passage. Access control lists fit when order decides hits. Access control lists fit when order decides rules.

Access control lists lose when the question isfile. Access control lists lose when the question isobject. Access control lists lose when the question isfolder. Access control lists lose when the question isshare.
''',
    },
    'Permissions': {
        'body': '''
Permissions say who may read change or run. Permissions say who may read change or execute. Permissions say who may read change or write. Permissions say who may read change or delete.

Permissions set payroll files to mode 640 group. Permissions set payroll files to mode 600 owner. Permissions set payroll files to mode 440 readers. Permissions set payroll files to mode 750 admins.

Permissions show with chmod checks and icacls listings. Permissions show with chmod checks and icacls reviews. Permissions show with chmod checks and icacls audits. Permissions show with chmod checks and icacls diffs.

Permissions differ from network lists by binding objects. Permissions differ from network lists by naming people. Permissions differ from network lists by limiting files. Permissions differ from network lists by scoping actions.

Permissions support least privilege on each file today. Permissions support least privilege on each folder today. Permissions support least privilege on each share today. Permissions support least privilege on each object today.

Permissions grant owner rights on the file today. Permissions grant owner rights on the folder today. Permissions grant owner rights on the share today. Permissions grant owner rights on the mailbox today.

Permissions grant owner rights on the record today. Permissions grant owner rights on the script today. Permissions grant owner rights on the image today. Permissions grant owner rights on the key today.

Permissions grant owner rights on the annex today. Permissions grant group rights on the file today. Permissions grant group rights on the folder today. Permissions grant group rights on the share today.

Permissions grant group rights on the mailbox today. Permissions grant group rights on the record today. Permissions grant group rights on the script today. Permissions grant group rights on the image today.

Permissions grant group rights on the key today. Permissions grant group rights on the annex today. Permissions grant payroll rights on the file today. Permissions grant payroll rights on the folder today.

Permissions grant payroll rights on the share today. Permissions grant payroll rights on the mailbox today. Permissions grant payroll rights on the record today. Permissions grant payroll rights on the script today.

Permissions grant payroll rights on the image today. Permissions grant payroll rights on the key today. Permissions grant payroll rights on the annex today. Permissions grant clinic rights on the file today.

Permissions grant clinic rights on the folder today. Permissions grant clinic rights on the share today. Permissions grant clinic rights on the mailbox today. Permissions grant clinic rights on the record today.

Permissions grant clinic rights on the script today. Permissions grant clinic rights on the image today. Permissions grant clinic rights on the key today. Permissions grant clinic rights on the annex today.

Permissions grant audit rights on the file today. Permissions grant audit rights on the folder today. Permissions grant audit rights on the share today. Permissions grant audit rights on the mailbox today.

Permissions grant audit rights on the record today. Permissions grant audit rights on the script today. Permissions grant audit rights on the image today. Permissions grant audit rights on the key today.

Permissions grant audit rights on the annex today. Permissions grant backup rights on the file today. Permissions grant backup rights on the folder today. Permissions grant backup rights on the share today.

Permissions grant backup rights on the mailbox today. Permissions grant backup rights on the record today. Permissions grant backup rights on the script today. Permissions grant backup rights on the image today.

Permissions grant backup rights on the key today. Permissions grant backup rights on the annex today. Permissions grant app rights on the file today. Permissions grant app rights on the folder today.

Permissions grant app rights on the share today. Permissions grant app rights on the mailbox today. Permissions grant app rights on the record today. Permissions grant app rights on the script today.

Permissions grant app rights on the image today. Permissions grant app rights on the key today. Permissions grant app rights on the annex today. Permissions grant vendor rights on the file today.

Permissions grant vendor rights on the folder today.
''',
        'r0': '''
Permissions run icacls before changing a folder today. Permissions run icacls before changing a share today. Permissions run icacls before changing a file today. Permissions run icacls before changing a key today.

Permissions use chmod then ls to verify today. Permissions use chmod then ls to confirm today. Permissions use chmod then ls to record today. Permissions use chmod then ls to compare today.

Permissions remove everyone write from shares today fully. Permissions remove everyone write from folders today fully. Permissions remove everyone write from scripts today fully. Permissions remove everyone write from keys today fully.

Permissions log permission changes in syslog today fully. Permissions log permission changes in audit today fully. Permissions log permission changes in tickets today fully. Permissions log permission changes in diffs today fully.
''',
        'r1': '''
Permissions mean who may touch this thing today. Permissions mean who may touch this file today. Permissions mean who may touch this folder today. Permissions mean who may touch this share today.

Permissions cover read change and run rights today. Permissions cover read change and run actions today. Permissions cover read change and run jobs today. Permissions cover read change and run needs today.

Permissions should match the job not habit today. Permissions should match the job not fear today. Permissions should match the job not ease today. Permissions should match the job not rank today.
''',
        'r2': '''
Permissions resemble folder stamps on covers today fully. Permissions resemble file stamps on edges today fully. Permissions resemble drawer stamps on labels today fully. Permissions resemble binder stamps on spines today fully.

Permissions feel like allowed names on diaries today. Permissions feel like listed names on ledgers today. Permissions feel like marked names on albums today. Permissions feel like signed names on folders today.

Permissions mirror action locks per object today fully. Permissions mirror person locks per folder today fully. Permissions mirror role locks per file today fully. Permissions mirror job locks per share today fully.

Permissions act as touch labels for rights today. Permissions act as use labels for limits today. Permissions act as edit labels for scope today. Permissions act as run labels for needs today.
''',
        'r4': '''
Permissions run icacls before you widen today fully. Permissions run icacls before you share today fully. Permissions run icacls before you copy today fully. Permissions run icacls before you grant today fully.

Permissions run icacls before you ship today fully. Permissions remove everyone write from shares today fully. Permissions remove everyone write from folders today fully. Permissions remove everyone write from scripts today fully.

Permissions remove everyone write from keys today fully. Permissions remove everyone write from roots today fully.
''',
        'exam': '''
Permissions fit when the object lists people today. Permissions fit when the object lists actions today. Permissions fit when the object lists rights today. Permissions fit when the object lists modes today.

Permissions lose when the list is network today. Permissions lose when the list is ordered today. Permissions lose when the list is packet today. Permissions lose when the list is zone today.
''',
    },
    'Application allow lists': {
        'body': '''
Application allow lists run only named approved programs. Application allow lists run only named approved binaries. Application allow lists run only named approved tools. Application allow lists run only named approved apps.

Application allow lists block anything missing from them. Application allow lists block anything missing from lists. Application allow lists block anything missing from policy. Application allow lists block anything missing from names.

Application allow lists log denies as applocker events. Application allow lists log denies as applocker rows. Application allow lists log denies as applocker hits. Application allow lists log denies as applocker codes.

Application allow lists differ from blocking lists default. Application allow lists differ from blocking lists tightness. Application allow lists differ from blocking lists naming. Application allow lists differ from blocking lists refusal.

Application allow lists stop unknown encryptors and droppers. Application allow lists stop unknown encryptors and tools. Application allow lists stop unknown encryptors and scripts. Application allow lists stop unknown encryptors and loaders.

Application allow lists name clinic apps for payroll. Application allow lists name clinic apps for charts. Application allow lists name clinic apps for imaging. Application allow lists name clinic apps for mail.

Application allow lists name clinic apps for browser. Application allow lists name clinic apps for shell. Application allow lists name clinic apps for annex. Application allow lists name clinic apps for atrium.

Application allow lists name clinic apps for basement. Application allow lists name clinic apps for campus. Application allow lists name clinic apps for courtyard. Application allow lists name clinic apps for garage.

Application allow lists name kiosk apps for payroll. Application allow lists name kiosk apps for charts. Application allow lists name kiosk apps for imaging. Application allow lists name kiosk apps for mail.

Application allow lists name kiosk apps for browser. Application allow lists name kiosk apps for shell. Application allow lists name kiosk apps for annex. Application allow lists name kiosk apps for atrium.

Application allow lists name kiosk apps for basement. Application allow lists name kiosk apps for campus. Application allow lists name kiosk apps for courtyard. Application allow lists name kiosk apps for garage.

Application allow lists name lab apps for payroll. Application allow lists name lab apps for charts. Application allow lists name lab apps for imaging. Application allow lists name lab apps for mail.

Application allow lists name lab apps for browser. Application allow lists name lab apps for shell. Application allow lists name lab apps for annex. Application allow lists name lab apps for atrium.

Application allow lists name lab apps for basement. Application allow lists name lab apps for campus. Application allow lists name lab apps for courtyard. Application allow lists name lab apps for garage.

Application allow lists name front apps for payroll. Application allow lists name front apps for charts. Application allow lists name front apps for imaging. Application allow lists name front apps for mail.

Application allow lists name front apps for browser. Application allow lists name front apps for shell. Application allow lists name front apps for annex. Application allow lists name front apps for atrium.

Application allow lists name front apps for basement. Application allow lists name front apps for campus. Application allow lists name front apps for courtyard. Application allow lists name front apps for garage.

Application allow lists name vendor apps for payroll. Application allow lists name vendor apps for charts. Application allow lists name vendor apps for imaging. Application allow lists name vendor apps for mail.

Application allow lists name vendor apps for browser. Application allow lists name vendor apps for shell. Application allow lists name vendor apps for annex. Application allow lists name vendor apps for atrium.

Application allow lists name vendor apps for basement. Application allow lists name vendor apps for campus. Application allow lists name vendor apps for courtyard. Application allow lists name vendor apps for garage.

Application allow lists name student apps for payroll. Application allow lists name student apps for charts. Application allow lists name student apps for imaging. Application allow lists name student apps for mail.

Application allow lists name student apps for browser.
''',
        'r0': '''
Application allow lists hash allowed binaries with sha256. Application allow lists hash allowed binaries with catalogs. Application allow lists hash allowed binaries with signers. Application allow lists hash allowed binaries with paths.

Application allow lists start in audit before enforce. Application allow lists start in audit before block. Application allow lists start in audit before deny. Application allow lists start in audit before prod.

Application allow lists review applocker denies each morning. Application allow lists review applocker denies each change. Application allow lists review applocker denies each pilot. Application allow lists review applocker denies each ticket.

Application allow lists sign updates before they run. Application allow lists sign updates before they land. Application allow lists sign updates before they ship. Application allow lists sign updates before they replace.
''',
        'r1': '''
Application allow lists mean only named programs run. Application allow lists mean only named programs start. Application allow lists mean only named programs launch. Application allow lists mean only named programs execute.

Application allow lists refuse everything else by default. Application allow lists refuse everything else by design. Application allow lists refuse everything else by policy. Application allow lists refuse everything else by name.

Application allow lists are tighter than a blocklist. Application allow lists are tighter than a denylist. Application allow lists are tighter than a banlist. Application allow lists are tighter than a stoplist.
''',
        'r2': '''
Application allow lists resemble approved menus only today. Application allow lists resemble named menus dishes today. Application allow lists resemble listed menus meals today. Application allow lists resemble signed menus plates today.

Application allow lists feel like named stages acts. Application allow lists feel like listed stages players. Application allow lists feel like known stages scenes. Application allow lists feel like billed stages shows.

Application allow lists mirror packed kits tools today. Application allow lists mirror labeled kits bins today. Application allow lists mirror signed kits sets today. Application allow lists mirror chosen kits gear today.

Application allow lists act as name gates checks. Application allow lists act as list gates doors. Application allow lists act as known gates entries. Application allow lists act as signed gates starts.
''',
        'r4': '''
Application allow lists hash allowed binaries first today. Application allow lists hash allowed binaries today today. Application allow lists hash allowed binaries again today. Application allow lists hash allowed binaries fully today.

Application allow lists hash allowed binaries offline today. Application allow lists review applocker denies daily today. Application allow lists review applocker denies early today. Application allow lists review applocker denies fully today.

Application allow lists review applocker denies live today. Application allow lists review applocker denies after today.
''',
        'exam': '''
Application allow lists fit when only named programs. Application allow lists fit when only named binaries. Application allow lists fit when only named tools. Application allow lists fit when only named apps.

Application allow lists lose when unknown code runs. Application allow lists lose when unknown code starts. Application allow lists lose when unknown code launches. Application allow lists lose when unknown code stays.
''',
    },
    'Isolation': {
        'body': '''
Isolation keeps a risky system working but contained. Isolation keeps a risky system working but bounded. Isolation keeps a risky system working but local. Isolation keeps a risky system working but alone.

Isolation places unpatched instruments off the internet path. Isolation places unpatched instruments off the file shares. Isolation places unpatched instruments off the mail route. Isolation places unpatched instruments off the guest wifi.

Isolation uses iptables so it cannot wander today. Isolation uses iptables so it cannot scan today. Isolation uses iptables so it cannot reach today. Isolation uses iptables so it cannot call today.

Isolation differs from segmentation by focusing one today. Isolation differs from segmentation by holding risk today. Isolation differs from segmentation by feeding work today. Isolation differs from segmentation by limiting one today.

Isolation still lets the job happen locally today. Isolation still lets the job happen safely today. Isolation still lets the job happen daily today. Isolation still lets the job happen fully today.

Isolation holds lab gear away from shares today. Isolation holds lab gear away from mail today. Isolation holds lab gear away from internet today. Isolation holds lab gear away from admins today.

Isolation holds lab gear away from backups today. Isolation holds lab gear away from guests today. Isolation holds lab gear away from charts today. Isolation holds lab gear away from updates today.

Isolation holds lab gear away from annex today. Isolation holds clinic gear away from shares today. Isolation holds clinic gear away from mail today. Isolation holds clinic gear away from internet today.

Isolation holds clinic gear away from admins today. Isolation holds clinic gear away from backups today. Isolation holds clinic gear away from guests today. Isolation holds clinic gear away from charts today.

Isolation holds clinic gear away from updates today. Isolation holds clinic gear away from annex today. Isolation holds imaging gear away from shares today. Isolation holds imaging gear away from mail today.

Isolation holds imaging gear away from internet today. Isolation holds imaging gear away from admins today. Isolation holds imaging gear away from backups today. Isolation holds imaging gear away from guests today.

Isolation holds imaging gear away from charts today. Isolation holds imaging gear away from updates today. Isolation holds imaging gear away from annex today. Isolation holds badge gear away from shares today.

Isolation holds badge gear away from mail today. Isolation holds badge gear away from internet today. Isolation holds badge gear away from admins today. Isolation holds badge gear away from backups today.

Isolation holds badge gear away from guests today. Isolation holds badge gear away from charts today. Isolation holds badge gear away from updates today. Isolation holds badge gear away from annex today.

Isolation holds ot gear away from shares today. Isolation holds ot gear away from mail today. Isolation holds ot gear away from internet today. Isolation holds ot gear away from admins today.

Isolation holds ot gear away from backups today. Isolation holds ot gear away from guests today. Isolation holds ot gear away from charts today. Isolation holds ot gear away from updates today.

Isolation holds ot gear away from annex today. Isolation holds vendor gear away from shares today. Isolation holds vendor gear away from mail today. Isolation holds vendor gear away from internet today.

Isolation holds vendor gear away from admins today. Isolation holds vendor gear away from backups today. Isolation holds vendor gear away from guests today. Isolation holds vendor gear away from charts today.

Isolation holds vendor gear away from updates today. Isolation holds vendor gear away from annex today. Isolation holds kiosk gear away from shares today. Isolation holds kiosk gear away from mail today.

Isolation holds kiosk gear away from internet today. Isolation holds kiosk gear away from admins today. Isolation holds kiosk gear away from backups today. Isolation holds kiosk gear away from guests today.

Isolation holds kiosk gear away from charts today. Isolation holds kiosk gear away from updates today. Isolation holds kiosk gear away from annex today. Isolation holds legacy gear away from shares today.

Isolation holds legacy gear away from mail today.
''',
        'r0': '''
Isolation remove default routes from the enclave today. Isolation remove default routes from the vlan today. Isolation remove default routes from the host today. Isolation remove default routes from the instrument today.

Isolation allow only the needed peer address today. Isolation allow only the needed peer portless today. Isolation allow only the needed peer name today. Isolation allow only the needed peer path today.

Isolation log denied attempts in syslog today fully. Isolation log denied attempts in iptables today fully. Isolation log denied attempts in flows today fully. Isolation log denied attempts in alerts today fully.

Isolation review the path each quarter today fully. Isolation review the path each change today fully. Isolation review the path each ticket today fully. Isolation review the path each month today fully.
''',
        'r1': '''
Isolation means let it work without wandering today. Isolation means let it work without roaming today. Isolation means let it work without reaching today. Isolation means let it work without spreading today.

Isolation fits gear you cannot safely patch today. Isolation fits gear you cannot safely replace today. Isolation fits gear you cannot safely move today. Isolation fits gear you cannot safely retire today.

Isolation keeps the job and drops thepath today. Isolation keeps the job and drops thewalk today. Isolation keeps the job and drops theroam today. Isolation keeps the job and drops thehop today.
''',
        'r2': '''
Isolation resemble powered booths with walls today fully. Isolation resemble fed booths with gates today fully. Isolation resemble lit booths with fences today fully. Isolation resemble worked booths with rails today fully.

Isolation feel like busy rooms still fed today. Isolation feel like active rooms still held today. Isolation feel like useful rooms still bounded today. Isolation feel like needed rooms still local today.

Isolation mirror workshop benches without halls today fully. Isolation mirror lab benches without doors today fully. Isolation mirror studio benches without streets today fully. Isolation mirror bench benches without roads today fully.

Isolation act as local care with bounds today. Isolation act as daily care with limits today. Isolation act as needed care with walls today. Isolation act as live care with fences today.
''',
        'r4': '''
Isolation remove default routes from enclaves today fully. Isolation remove default routes from instruments today fully. Isolation remove default routes from labs today fully. Isolation remove default routes from kiosks today fully.

Isolation remove default routes from legacy today fully. Isolation allow only the needed peer today fully. Isolation allow only the needed path today fully. Isolation allow only the needed name today fully.

Isolation allow only the needed host today fully. Isolation allow only the needed flow today fully.
''',
        'exam': '''
Isolation fits when risky gear must work today. Isolation fits when risky gear must stay today. Isolation fits when risky gear must run today. Isolation fits when risky gear must serve today.

Isolation loses when the whole zone splits today. Isolation loses when the whole zone segments today. Isolation loses when the whole zone divides today. Isolation loses when the whole zone groups today.
''',
    },
    'Patching': {
        'body': '''
Patching applies the vendor fix so a hole. Patching applies the vendor fix so a bug. Patching applies the vendor fix so a flaw. Patching applies the vendor fix so a gap.

Patching lands in a pilot group before everyone. Patching lands in a pilot group during windows. Patching lands in a pilot group after tests. Patching lands in a pilot group with rollback.

Patching records status in syslog and tickets today. Patching records status in syslog and inventory today. Patching records status in syslog and baselines today. Patching records status in syslog and reports today.

Patching differs from workarounds by closing causes today. Patching differs from workarounds by using vendor today. Patching differs from workarounds by removing bugs today. Patching differs from workarounds by shipping fixes today.

Patching does not replace allow lists alone today. Patching does not replace allow lists fully today. Patching does not replace allow lists ever today. Patching does not replace allow lists entirely today.

Patching schedules browser fixes after pilot today fully. Patching schedules browser fixes after test today fully. Patching schedules browser fixes after window today fully. Patching schedules browser fixes after rollback today fully.

Patching schedules browser fixes after ticket today fully. Patching schedules browser fixes after backup today fully. Patching schedules browser fixes after notice today fully. Patching schedules browser fixes after measure today fully.

Patching schedules browser fixes after annex today fully. Patching schedules kernel fixes after pilot today fully. Patching schedules kernel fixes after test today fully. Patching schedules kernel fixes after window today fully.

Patching schedules kernel fixes after rollback today fully. Patching schedules kernel fixes after ticket today fully. Patching schedules kernel fixes after backup today fully. Patching schedules kernel fixes after notice today fully.

Patching schedules kernel fixes after measure today fully. Patching schedules kernel fixes after annex today fully. Patching schedules vpn fixes after pilot today fully. Patching schedules vpn fixes after test today fully.

Patching schedules vpn fixes after window today fully. Patching schedules vpn fixes after rollback today fully. Patching schedules vpn fixes after ticket today fully. Patching schedules vpn fixes after backup today fully.

Patching schedules vpn fixes after notice today fully. Patching schedules vpn fixes after measure today fully. Patching schedules vpn fixes after annex today fully. Patching schedules mail fixes after pilot today fully.

Patching schedules mail fixes after test today fully. Patching schedules mail fixes after window today fully. Patching schedules mail fixes after rollback today fully. Patching schedules mail fixes after ticket today fully.

Patching schedules mail fixes after backup today fully. Patching schedules mail fixes after notice today fully. Patching schedules mail fixes after measure today fully. Patching schedules mail fixes after annex today fully.

Patching schedules agent fixes after pilot today fully. Patching schedules agent fixes after test today fully. Patching schedules agent fixes after window today fully. Patching schedules agent fixes after rollback today fully.

Patching schedules agent fixes after ticket today fully. Patching schedules agent fixes after backup today fully. Patching schedules agent fixes after notice today fully. Patching schedules agent fixes after measure today fully.

Patching schedules agent fixes after annex today fully. Patching schedules firmware fixes after pilot today fully. Patching schedules firmware fixes after test today fully. Patching schedules firmware fixes after window today fully.

Patching schedules firmware fixes after rollback today fully. Patching schedules firmware fixes after ticket today fully. Patching schedules firmware fixes after backup today fully. Patching schedules firmware fixes after notice today fully.

Patching schedules firmware fixes after measure today fully. Patching schedules firmware fixes after annex today fully. Patching schedules library fixes after pilot today fully. Patching schedules library fixes after test today fully.

Patching schedules library fixes after window today fully. Patching schedules library fixes after rollback today fully. Patching schedules library fixes after ticket today fully. Patching schedules library fixes after backup today fully.

Patching schedules library fixes after notice today fully. Patching schedules library fixes after measure today fully. Patching schedules library fixes after annex today fully. Patching schedules runtime fixes after pilot today fully.

Patching schedules runtime fixes after test today fully.
''',
        'r0': '''
Patching pilot one ring before the fleet today. Patching pilot one ring before the clinic today. Patching pilot one ring before the campus today. Patching pilot one ring before the kiosks today.

Patching keep rollback media until stable today fully. Patching keep rollback media until verified today fully. Patching keep rollback media until measured today fully. Patching keep rollback media until signed today fully.

Patching match syslog success to inventory today fully. Patching match syslog success to tickets today fully. Patching match syslog success to hosts today fully. Patching match syslog success to rings today fully.

Patching separate emergency fixes from monthly today fully. Patching separate emergency fixes from routine today fully. Patching separate emergency fixes from bundles today fully. Patching separate emergency fixes from features today fully.
''',
        'r1': '''
Patching means put the vendor fix on today. Patching means put the vendor fix in today. Patching means put the vendor fix live today. Patching means put the vendor fix first today.

Patching starts with a small group first today. Patching starts with a small group today today. Patching starts with a small group safely today. Patching starts with a small group early today.

Patching closes a known hole onpurpose today fully. Patching closes a known hole forreal today fully. Patching closes a known hole atlast today fully. Patching closes a known hole incause today fully.
''',
        'r2': '''
Patching resemble fresh panes set straight today fully. Patching resemble new panes set clean today fully. Patching resemble maker panes set true today fully. Patching resemble vendor panes set flush today fully.

Patching feel like worn soles replaced properly today. Patching feel like cracked soles replaced fully today. Patching feel like thin soles replaced early today. Patching feel like old soles replaced right today.

Patching mirror maker repairs by design today fully. Patching mirror vendor repairs by spec today fully. Patching mirror shop repairs by pattern today fully. Patching mirror yard repairs by plan today fully.

Patching act as known fixes after tests today. Patching act as vendor fixes after pilots today. Patching act as real fixes after windows today. Patching act as scheduled fixes after checks today.
''',
        'r4': '''
Patching pilot fixes before the fleet today fully. Patching pilot fixes before the clinic today fully. Patching pilot fixes before the campus today fully. Patching pilot fixes before the kiosks today fully.

Patching pilot fixes before the weekend today fully. Patching keep rollback until you verify today fully. Patching keep rollback until you measure today fully. Patching keep rollback until you sign today fully.

Patching keep rollback until you close today fully. Patching keep rollback until you trust today fully.
''',
        'exam': '''
Patching fits when a vendor fix closes today. Patching fits when a vendor fix lands today. Patching fits when a vendor fix ships today. Patching fits when a vendor fix applies today.

Patching loses when you only hide symptoms today. Patching loses when you only hide noise today. Patching loses when you only hide alerts today. Patching loses when you only hide paths today.
''',
    },
    'Encryption as a mitigation': {
        'body': '''
Encryption as a mitigation keeps stolen copies unreadable. Encryption as a mitigation keeps stolen copies opaque. Encryption as a mitigation keeps stolen copies useless. Encryption as a mitigation keeps stolen copies sealed.

Encryption as a mitigation needs keys kept elsewhere. Encryption as a mitigation needs keys kept offline. Encryption as a mitigation needs keys kept separate. Encryption as a mitigation needs keys kept vaulted.

Encryption as a mitigation uses bitlocker on laptops. Encryption as a mitigation uses bitlocker on disks. Encryption as a mitigation uses bitlocker on backups. Encryption as a mitigation uses bitlocker on tapes.

Encryption as a mitigation fails if keys travel. Encryption as a mitigation fails if keys sit. Encryption as a mitigation fails if keys ride. Encryption as a mitigation fails if keys leak.

Encryption as a mitigation differs from hiding today. Encryption as a mitigation differs from deletion today. Encryption as a mitigation differs from obscurity today. Encryption as a mitigation differs from hope today.

Encryption as a mitigation seals laptops with aes. Encryption as a mitigation seals laptops with keys. Encryption as a mitigation seals laptops with vaults. Encryption as a mitigation seals laptops with modules.

Encryption as a mitigation seals laptops with tpm. Encryption as a mitigation seals laptops with passphrases. Encryption as a mitigation seals laptops with custodians. Encryption as a mitigation seals laptops with splits.

Encryption as a mitigation seals laptops with annex. Encryption as a mitigation seals tapes with aes. Encryption as a mitigation seals tapes with keys. Encryption as a mitigation seals tapes with vaults.

Encryption as a mitigation seals tapes with modules. Encryption as a mitigation seals tapes with tpm. Encryption as a mitigation seals tapes with passphrases. Encryption as a mitigation seals tapes with custodians.

Encryption as a mitigation seals tapes with splits. Encryption as a mitigation seals tapes with annex. Encryption as a mitigation seals disks with aes. Encryption as a mitigation seals disks with keys.

Encryption as a mitigation seals disks with vaults. Encryption as a mitigation seals disks with modules. Encryption as a mitigation seals disks with tpm. Encryption as a mitigation seals disks with passphrases.

Encryption as a mitigation seals disks with custodians. Encryption as a mitigation seals disks with splits. Encryption as a mitigation seals disks with annex. Encryption as a mitigation seals backups with aes.

Encryption as a mitigation seals backups with keys. Encryption as a mitigation seals backups with vaults. Encryption as a mitigation seals backups with modules. Encryption as a mitigation seals backups with tpm.

Encryption as a mitigation seals backups with passphrases. Encryption as a mitigation seals backups with custodians. Encryption as a mitigation seals backups with splits. Encryption as a mitigation seals backups with annex.

Encryption as a mitigation seals mail with aes. Encryption as a mitigation seals mail with keys. Encryption as a mitigation seals mail with vaults. Encryption as a mitigation seals mail with modules.

Encryption as a mitigation seals mail with tpm. Encryption as a mitigation seals mail with passphrases. Encryption as a mitigation seals mail with custodians. Encryption as a mitigation seals mail with splits.

Encryption as a mitigation seals mail with annex. Encryption as a mitigation seals databases with aes. Encryption as a mitigation seals databases with keys. Encryption as a mitigation seals databases with vaults.

Encryption as a mitigation seals databases with modules. Encryption as a mitigation seals databases with tpm. Encryption as a mitigation seals databases with passphrases. Encryption as a mitigation seals databases with custodians.

Encryption as a mitigation seals databases with splits. Encryption as a mitigation seals databases with annex. Encryption as a mitigation seals images with aes. Encryption as a mitigation seals images with keys.

Encryption as a mitigation seals images with vaults. Encryption as a mitigation seals images with modules. Encryption as a mitigation seals images with tpm. Encryption as a mitigation seals images with passphrases.

Encryption as a mitigation seals images with custodians. Encryption as a mitigation seals images with splits. Encryption as a mitigation seals images with annex. Encryption as a mitigation seals exports with aes.

Encryption as a mitigation seals exports with keys.
''',
        'r0': '''
Encryption as a mitigation store keys off media. Encryption as a mitigation store keys off tapes. Encryption as a mitigation store keys off laptops. Encryption as a mitigation store keys off shares.

Encryption as a mitigation check bitlocker status monthly. Encryption as a mitigation check bitlocker status today. Encryption as a mitigation check bitlocker status live. Encryption as a mitigation check bitlocker status fully.

Encryption as a mitigation rotate keys after staff. Encryption as a mitigation rotate keys after theft. Encryption as a mitigation rotate keys after loss. Encryption as a mitigation rotate keys after drift.

Encryption as a mitigation test restore without media. Encryption as a mitigation test restore without panic. Encryption as a mitigation test restore without keys. Encryption as a mitigation test restore without hopes.
''',
        'r1': '''
Encryption as a mitigation leaves stolen files unreadable. Encryption as a mitigation leaves stolen files useless. Encryption as a mitigation leaves stolen files sealed. Encryption as a mitigation leaves stolen files dark.

Encryption as a mitigation works if keys stay. Encryption as a mitigation works if keys remain. Encryption as a mitigation works if keys hide. Encryption as a mitigation works if keys split.

Encryption as a mitigation does not stop theft. Encryption as a mitigation does not stop loss. Encryption as a mitigation does not stop copying. Encryption as a mitigation does not stop taking.
''',
        'r2': '''
Encryption as a mitigation resemble locked cases traveling. Encryption as a mitigation resemble sealed cases cases. Encryption as a mitigation resemble shut cases satchels. Encryption as a mitigation resemble coded cases diaries.

Encryption as a mitigation feel like pocket keys. Encryption as a mitigation feel like split secrets. Encryption as a mitigation feel like home codes. Encryption as a mitigation feel like kept clasps.

Encryption as a mitigation mirror opaque boxes cargo. Encryption as a mitigation mirror sealed boxes tapes. Encryption as a mitigation mirror dark boxes drawers. Encryption as a mitigation mirror shut boxes albums.

Encryption as a mitigation act as theft later. Encryption as a mitigation act as loss after. Encryption as a mitigation act as copy anyway. Encryption as a mitigation act as take useless.
''',
        'r4': '''
Encryption as a mitigation store keys off media. Encryption as a mitigation store keys off tapes. Encryption as a mitigation store keys off laptops. Encryption as a mitigation store keys off shares.

Encryption as a mitigation store keys off disks. Encryption as a mitigation check bitlocker before travel. Encryption as a mitigation check bitlocker before loan. Encryption as a mitigation check bitlocker before ship.

Encryption as a mitigation check bitlocker before reuse. Encryption as a mitigation check bitlocker before retire.
''',
        'exam': '''
Encryption as a mitigation fits stolen copies unreadable. Encryption as a mitigation fits stolen copies useless. Encryption as a mitigation fits stolen copies sealed. Encryption as a mitigation fits stolen copies opaque.

Encryption as a mitigation loses if keys travel. Encryption as a mitigation loses if keys sit. Encryption as a mitigation loses if keys leak. Encryption as a mitigation loses if keys ride.
''',
    },
    'Monitoring': {
        'body': '''
Monitoring watches logs so action can happen sooner. Monitoring watches logs so action can happen today. Monitoring watches logs so action can happen live. Monitoring watches logs so action can happen early.

Monitoring pages on call when 4625 spikes fast. Monitoring pages on call when 4625 spikes now. Monitoring pages on call when 4625 spikes live. Monitoring pages on call when 4625 spikes early.

Monitoring reads auth.log in minutes not months today. Monitoring reads auth.log in minutes not quarters today. Monitoring reads auth.log in minutes not later today. Monitoring reads auth.log in minutes not never today.

Monitoring differs from a firewall by alerting people. Monitoring differs from a firewall by watching signals. Monitoring differs from a firewall by paging humans. Monitoring differs from a firewall by timing response.

Monitoring does not replace least privilege alone today. Monitoring does not replace least privilege fully today. Monitoring does not replace least privilege ever today. Monitoring does not replace least privilege entirely today.

Monitoring alerts on sprays within minutes today fully. Monitoring alerts on sprays within shifts today fully. Monitoring alerts on sprays within windows today fully. Monitoring alerts on sprays within hours today fully.

Monitoring alerts on sprays within bursts today fully. Monitoring alerts on sprays within pages today fully. Monitoring alerts on sprays within tickets today fully. Monitoring alerts on sprays within rotations today fully.

Monitoring alerts on sprays within annex today fully. Monitoring alerts on lockouts within minutes today fully. Monitoring alerts on lockouts within shifts today fully. Monitoring alerts on lockouts within windows today fully.

Monitoring alerts on lockouts within hours today fully. Monitoring alerts on lockouts within bursts today fully. Monitoring alerts on lockouts within pages today fully. Monitoring alerts on lockouts within tickets today fully.

Monitoring alerts on lockouts within rotations today fully. Monitoring alerts on lockouts within annex today fully. Monitoring alerts on travel within minutes today fully. Monitoring alerts on travel within shifts today fully.

Monitoring alerts on travel within windows today fully. Monitoring alerts on travel within hours today fully. Monitoring alerts on travel within bursts today fully. Monitoring alerts on travel within pages today fully.

Monitoring alerts on travel within tickets today fully. Monitoring alerts on travel within rotations today fully. Monitoring alerts on travel within annex today fully. Monitoring alerts on gaps within minutes today fully.

Monitoring alerts on gaps within shifts today fully. Monitoring alerts on gaps within windows today fully. Monitoring alerts on gaps within hours today fully. Monitoring alerts on gaps within bursts today fully.

Monitoring alerts on gaps within pages today fully. Monitoring alerts on gaps within tickets today fully. Monitoring alerts on gaps within rotations today fully. Monitoring alerts on gaps within annex today fully.

Monitoring alerts on denies within minutes today fully. Monitoring alerts on denies within shifts today fully. Monitoring alerts on denies within windows today fully. Monitoring alerts on denies within hours today fully.

Monitoring alerts on denies within bursts today fully. Monitoring alerts on denies within pages today fully. Monitoring alerts on denies within tickets today fully. Monitoring alerts on denies within rotations today fully.

Monitoring alerts on denies within annex today fully. Monitoring alerts on spikes within minutes today fully. Monitoring alerts on spikes within shifts today fully. Monitoring alerts on spikes within windows today fully.

Monitoring alerts on spikes within hours today fully. Monitoring alerts on spikes within bursts today fully. Monitoring alerts on spikes within pages today fully. Monitoring alerts on spikes within tickets today fully.

Monitoring alerts on spikes within rotations today fully. Monitoring alerts on spikes within annex today fully. Monitoring alerts on newbins within minutes today fully. Monitoring alerts on newbins within shifts today fully.

Monitoring alerts on newbins within windows today fully. Monitoring alerts on newbins within hours today fully. Monitoring alerts on newbins within bursts today fully. Monitoring alerts on newbins within pages today fully.

Monitoring alerts on newbins within tickets today fully. Monitoring alerts on newbins within rotations today fully. Monitoring alerts on newbins within annex today fully. Monitoring alerts on beacons within minutes today fully.

Monitoring alerts on beacons within shifts today fully.
''',
        'r0': '''
Monitoring page 4625 spikes within minutes today fully. Monitoring page 4625 spikes within shifts today fully. Monitoring page 4625 spikes within windows today fully. Monitoring page 4625 spikes within bursts today fully.

Monitoring forward auth.log off the host today fully. Monitoring forward auth.log off the disk today fully. Monitoring forward auth.log off the lan today fully. Monitoring forward auth.log off the box today fully.

Monitoring tune alerts after false pages today fully. Monitoring tune alerts after false storms today fully. Monitoring tune alerts after false noise today fully. Monitoring tune alerts after false floods today fully.

Monitoring pair each alert with a owner today. Monitoring pair each alert with a runbook today. Monitoring pair each alert with a ticket today. Monitoring pair each alert with a clock today.
''',
        'r1': '''
Monitoring means watch so you can act today. Monitoring means watch so you can call today. Monitoring means watch so you can stop today. Monitoring means watch so you can help today.

Monitoring should ring while time remains today fully. Monitoring should ring while time exists today fully. Monitoring should ring while time lasts today fully. Monitoring should ring while time holds today fully.

Monitoring is useless if nobody hears today fully. Monitoring is useless if nobody owns today fully. Monitoring is useless if nobody answers today fully. Monitoring is useless if nobody acts today fully.
''',
        'r2': '''
Monitoring resemble night watches that ring today fully. Monitoring resemble hall watches that call today fully. Monitoring resemble dock watches that signal today fully. Monitoring resemble yard watches that shout today fully.

Monitoring feel like small bells heard early today. Monitoring feel like real bells heard live today. Monitoring feel like sharp bells heard now today. Monitoring feel like clear bells heard soon today.

Monitoring mirror awake lookouts on shift today fully. Monitoring mirror named lookouts on duty today fully. Monitoring mirror paired lookouts on hours today fully. Monitoring mirror staffed lookouts on nights today fully.

Monitoring act as time notice in minutes today. Monitoring act as live notice in pages today. Monitoring act as early notice in hands today. Monitoring act as real notice in shifts today.
''',
        'r4': '''
Monitoring page 4625 spikes within minutes today fully. Monitoring page 4625 spikes within shifts today fully. Monitoring page 4625 spikes within windows today fully. Monitoring page 4625 spikes within bursts today fully.

Monitoring page 4625 spikes within hours today fully. Monitoring forward auth.log off the host today fully. Monitoring forward auth.log off the disk today fully. Monitoring forward auth.log off the box today fully.

Monitoring forward auth.log off the lan today fully. Monitoring forward auth.log off the laptop today fully.
''',
        'exam': '''
Monitoring fits when signals reach people fast today. Monitoring fits when signals reach people live today. Monitoring fits when signals reach people early today. Monitoring fits when signals reach people now today.

Monitoring loses when nobody owns the page today. Monitoring loses when nobody owns the alert today. Monitoring loses when nobody owns the bell today. Monitoring loses when nobody owns the watch today.
''',
    },
    'Least privilege': {
        'body': '''
Least privilege grants only rights the job needs. Least privilege grants only rights the job uses. Least privilege grants only rights the job requires. Least privilege grants only rights the job holds.

Least privilege rejects standing admin kept for convenience. Least privilege rejects standing admin kept for habit. Least privilege rejects standing admin kept for speed. Least privilege rejects standing admin kept for comfort.

Least privilege shows with whoami and sudo reviews. Least privilege shows with whoami and sudo checks. Least privilege shows with whoami and sudo diffs. Least privilege shows with whoami and sudo audits.

Least privilege limits helpdesk to reception resets today. Least privilege limits helpdesk to reception roles today. Least privilege limits helpdesk to reception scopes today. Least privilege limits helpdesk to reception groups today.

Least privilege differs from monitoring by preventing today. Least privilege differs from monitoring by narrowing today. Least privilege differs from monitoring by removing today. Least privilege differs from monitoring by bounding today.

Least privilege scopes front roles down daily today. Least privilege scopes front roles down tightly today. Least privilege scopes front roles down fully today. Least privilege scopes front roles down early today.

Least privilege scopes front roles down live today. Least privilege scopes front roles down now today. Least privilege scopes front roles down again today. Least privilege scopes front roles down quietly today.

Least privilege scopes front roles down annex today. Least privilege scopes clinic roles down daily today. Least privilege scopes clinic roles down tightly today. Least privilege scopes clinic roles down fully today.

Least privilege scopes clinic roles down early today. Least privilege scopes clinic roles down live today. Least privilege scopes clinic roles down now today. Least privilege scopes clinic roles down again today.

Least privilege scopes clinic roles down quietly today. Least privilege scopes clinic roles down annex today. Least privilege scopes vendor roles down daily today. Least privilege scopes vendor roles down tightly today.

Least privilege scopes vendor roles down fully today. Least privilege scopes vendor roles down early today. Least privilege scopes vendor roles down live today. Least privilege scopes vendor roles down now today.

Least privilege scopes vendor roles down again today. Least privilege scopes vendor roles down quietly today. Least privilege scopes vendor roles down annex today. Least privilege scopes student roles down daily today.

Least privilege scopes student roles down tightly today. Least privilege scopes student roles down fully today. Least privilege scopes student roles down early today. Least privilege scopes student roles down live today.

Least privilege scopes student roles down now today. Least privilege scopes student roles down again today. Least privilege scopes student roles down quietly today. Least privilege scopes student roles down annex today.

Least privilege scopes kiosk roles down daily today. Least privilege scopes kiosk roles down tightly today. Least privilege scopes kiosk roles down fully today. Least privilege scopes kiosk roles down early today.

Least privilege scopes kiosk roles down live today. Least privilege scopes kiosk roles down now today. Least privilege scopes kiosk roles down again today. Least privilege scopes kiosk roles down quietly today.

Least privilege scopes kiosk roles down annex today. Least privilege scopes lab roles down daily today. Least privilege scopes lab roles down tightly today. Least privilege scopes lab roles down fully today.

Least privilege scopes lab roles down early today. Least privilege scopes lab roles down live today. Least privilege scopes lab roles down now today. Least privilege scopes lab roles down again today.

Least privilege scopes lab roles down quietly today. Least privilege scopes lab roles down annex today. Least privilege scopes night roles down daily today. Least privilege scopes night roles down tightly today.

Least privilege scopes night roles down fully today. Least privilege scopes night roles down early today. Least privilege scopes night roles down live today. Least privilege scopes night roles down now today.

Least privilege scopes night roles down again today. Least privilege scopes night roles down quietly today. Least privilege scopes night roles down annex today. Least privilege scopes backup roles down daily today.

Least privilege scopes backup roles down tightly today.
''',
        'r0': '''
Least privilege run whoami groups on sample admins. Least privilege run whoami groups on sample desks. Least privilege run whoami groups on sample kiosks. Least privilege run whoami groups on sample apps.

Least privilege read sudo lists for extra roots. Least privilege read sudo lists for extra shells. Least privilege read sudo lists for extra commands. Least privilege read sudo lists for extra groups.

Least privilege expire admin roles after the ticket. Least privilege expire admin roles after the change. Least privilege expire admin roles after the window. Least privilege expire admin roles after the task.

Least privilege separate day accounts from admins today. Least privilege separate day accounts from roots today. Least privilege separate day accounts from operators today. Least privilege separate day accounts from owners today.
''',
        'r1': '''
Least privilege means only the rights the jobneeds. Least privilege means only the rights the workuses. Least privilege means only the rights the taskholds. Least privilege means only the rights the rolefits.

Least privilege drops extra admin kept for ease. Least privilege drops extra admin kept for habit. Least privilege drops extra admin kept for speed. Least privilege drops extra admin kept for comfort.

Least privilege makes stolen accounts less useful today. Least privilege makes stolen accounts less broad today. Least privilege makes stolen accounts less dangerous today. Least privilege makes stolen accounts less powerful today.
''',
        'r2': '''
Least privilege resemble one keys for cabinet today. Least privilege resemble desk keys for drawers today. Least privilege resemble role keys for rooms today. Least privilege resemble job keys for gates today.

Least privilege feel like shift badges for floors. Least privilege feel like task badges for wings. Least privilege feel like named badges for doors. Least privilege feel like daily badges for desks.

Least privilege mirror needed tools on hooks today. Least privilege mirror job tools on belts today. Least privilege mirror task tools on racks today. Least privilege mirror role tools on boards today.

Least privilege act as daily limits on power. Least privilege act as named limits on reach. Least privilege act as job limits on scope. Least privilege act as role limits on rights.
''',
        'r4': '''
Least privilege run whoami on sample admins today. Least privilege run whoami on sample desks today. Least privilege run whoami on sample kiosks today. Least privilege run whoami on sample apps today.

Least privilege run whoami on sample vendors today. Least privilege expire admin roles after tickets today. Least privilege expire admin roles after changes today. Least privilege expire admin roles after windows today.

Least privilege expire admin roles after tasks today. Least privilege expire admin roles after pilots today.
''',
        'exam': '''
Least privilege fits when rights match the job. Least privilege fits when rights match the task. Least privilege fits when rights match the role. Least privilege fits when rights match the work.

Least privilege loses when admin stands for convenience. Least privilege loses when admin stands for habit. Least privilege loses when admin stands for speed. Least privilege loses when admin stands for comfort.
''',
    },
    'Configuration enforcement': {
        'body': '''
Configuration enforcement puts approved settings back after drift. Configuration enforcement puts approved settings back after edits. Configuration enforcement puts approved settings back after tweaks. Configuration enforcement puts approved settings back after local.

Configuration enforcement shows drift with gpresult each morning. Configuration enforcement shows drift with gpresult each cycle. Configuration enforcement shows drift with gpresult each night. Configuration enforcement shows drift with gpresult each change.

Configuration enforcement returns open inbound rules to baseline. Configuration enforcement returns open inbound rules to deny. Configuration enforcement returns open inbound rules to policy. Configuration enforcement returns open inbound rules to standard.

Configuration enforcement differs from one audit by repeating. Configuration enforcement differs from one audit by restoring. Configuration enforcement differs from one audit by enforcing. Configuration enforcement differs from one audit by looping.

Configuration enforcement covers laptops that leave the building. Configuration enforcement covers laptops that leave the image. Configuration enforcement covers laptops that leave the lan. Configuration enforcement covers laptops that leave the dock.

Configuration enforcement resets firewall settings to baseline today. Configuration enforcement resets firewall settings to deny today. Configuration enforcement resets firewall settings to standard today. Configuration enforcement resets firewall settings to policy today.

Configuration enforcement resets firewall settings to image today. Configuration enforcement resets firewall settings to gold today. Configuration enforcement resets firewall settings to ticket today. Configuration enforcement resets firewall settings to catalog today.

Configuration enforcement resets firewall settings to annex today. Configuration enforcement resets service settings to baseline today. Configuration enforcement resets service settings to deny today. Configuration enforcement resets service settings to standard today.

Configuration enforcement resets service settings to policy today. Configuration enforcement resets service settings to image today. Configuration enforcement resets service settings to gold today. Configuration enforcement resets service settings to ticket today.

Configuration enforcement resets service settings to catalog today. Configuration enforcement resets service settings to annex today. Configuration enforcement resets share settings to baseline today. Configuration enforcement resets share settings to deny today.

Configuration enforcement resets share settings to standard today. Configuration enforcement resets share settings to policy today. Configuration enforcement resets share settings to image today. Configuration enforcement resets share settings to gold today.

Configuration enforcement resets share settings to ticket today. Configuration enforcement resets share settings to catalog today. Configuration enforcement resets share settings to annex today. Configuration enforcement resets browser settings to baseline today.

Configuration enforcement resets browser settings to deny today. Configuration enforcement resets browser settings to standard today. Configuration enforcement resets browser settings to policy today. Configuration enforcement resets browser settings to image today.

Configuration enforcement resets browser settings to gold today. Configuration enforcement resets browser settings to ticket today. Configuration enforcement resets browser settings to catalog today. Configuration enforcement resets browser settings to annex today.

Configuration enforcement resets usb settings to baseline today. Configuration enforcement resets usb settings to deny today. Configuration enforcement resets usb settings to standard today. Configuration enforcement resets usb settings to policy today.

Configuration enforcement resets usb settings to image today. Configuration enforcement resets usb settings to gold today. Configuration enforcement resets usb settings to ticket today. Configuration enforcement resets usb settings to catalog today.

Configuration enforcement resets usb settings to annex today. Configuration enforcement resets wifi settings to baseline today. Configuration enforcement resets wifi settings to deny today. Configuration enforcement resets wifi settings to standard today.

Configuration enforcement resets wifi settings to policy today. Configuration enforcement resets wifi settings to image today. Configuration enforcement resets wifi settings to gold today. Configuration enforcement resets wifi settings to ticket today.

Configuration enforcement resets wifi settings to catalog today. Configuration enforcement resets wifi settings to annex today. Configuration enforcement resets agent settings to baseline today. Configuration enforcement resets agent settings to deny today.

Configuration enforcement resets agent settings to standard today. Configuration enforcement resets agent settings to policy today. Configuration enforcement resets agent settings to image today. Configuration enforcement resets agent settings to gold today.

Configuration enforcement resets agent settings to ticket today. Configuration enforcement resets agent settings to catalog today. Configuration enforcement resets agent settings to annex today. Configuration enforcement resets logging settings to baseline today.

Configuration enforcement resets logging settings to deny today.
''',
        'r0': '''
Configuration enforcement run gpresult after travel days today. Configuration enforcement run gpresult after travel weeks today. Configuration enforcement run gpresult after travel returns today. Configuration enforcement run gpresult after travel changes today.

Configuration enforcement alert when inbound any appears today. Configuration enforcement alert when inbound any returns today. Configuration enforcement alert when inbound any sticks today. Configuration enforcement alert when inbound any lands today.

Configuration enforcement store baselines in versioned repos today. Configuration enforcement store baselines in versioned tickets today. Configuration enforcement store baselines in versioned catalogs today. Configuration enforcement store baselines in versioned images today.

Configuration enforcement remeasure after every image update today. Configuration enforcement remeasure after every image swap today. Configuration enforcement remeasure after every image loan today. Configuration enforcement remeasure after every image rebuild today.
''',
        'r1': '''
Configuration enforcement means approved settings win again today. Configuration enforcement means approved settings win daily today. Configuration enforcement means approved settings win overnight today. Configuration enforcement means approved settings win always today.

Configuration enforcement fixes drift without waiting months today. Configuration enforcement fixes drift without waiting audits today. Configuration enforcement fixes drift without waiting complaints today. Configuration enforcement fixes drift without waiting loss today.

Configuration enforcement covers laptops that come home today. Configuration enforcement covers laptops that come back today. Configuration enforcement covers laptops that come late today. Configuration enforcement covers laptops that come loose today.
''',
        'r2': '''
Configuration enforcement resemble daily molds pressed back today. Configuration enforcement resemble nightly molds pressed true today. Configuration enforcement resemble shop molds pressed flush today. Configuration enforcement resemble yard molds pressed square today.

Configuration enforcement feel like posted rulers reset each. Configuration enforcement feel like marked rulers reset dawn. Configuration enforcement feel like known rulers reset again. Configuration enforcement feel like shared rulers reset daily.

Configuration enforcement mirror approved settings returned overnight today. Configuration enforcement mirror gold settings returned early today. Configuration enforcement mirror named settings returned fully today. Configuration enforcement mirror written settings returned back today.

Configuration enforcement act as drift correction after edits. Configuration enforcement act as policy correction after tweaks. Configuration enforcement act as baseline correction after travel. Configuration enforcement act as standard correction after loans.
''',
        'r4': '''
Configuration enforcement run gpresult after each trip today. Configuration enforcement run gpresult after each image today. Configuration enforcement run gpresult after each loan today. Configuration enforcement run gpresult after each change today.

Configuration enforcement run gpresult after each week today. Configuration enforcement reset inbound any back today today. Configuration enforcement reset inbound any back nightly today. Configuration enforcement reset inbound any back fully today.

Configuration enforcement reset inbound any back live today. Configuration enforcement reset inbound any back early today.
''',
        'exam': '''
Configuration enforcement fits when drift is put back. Configuration enforcement fits when drift is put right. Configuration enforcement fits when drift is put baseline. Configuration enforcement fits when drift is put straight.

Configuration enforcement loses when a one time audit. Configuration enforcement loses when a one time look. Configuration enforcement loses when a one time note. Configuration enforcement loses when a one time photo.
''',
    },
    'Decommissioning': {
        'body': '''
Decommissioning retires systems deliberately and records the records. Decommissioning retires systems deliberately and records the owners. Decommissioning retires systems deliberately and records the dates. Decommissioning retires systems deliberately and records the tickets.

Decommissioning removes accounts before the box lingers today. Decommissioning removes accounts before the box stays today. Decommissioning removes accounts before the box remains today. Decommissioning removes accounts before the box forgets today.

Decommissioning drops the host from diagrams together today. Decommissioning drops the host from diagrams sameweek today. Decommissioning drops the host from diagrams promptly today. Decommissioning drops the host from diagrams fully today.

Decommissioning handles data before disks leave site today. Decommissioning handles data before disks leave hands today. Decommissioning handles data before disks leave racks today. Decommissioning handles data before disks leave vendors today.

Decommissioning logs the shutdown in syslog once today. Decommissioning logs the shutdown in syslog clearly today. Decommissioning logs the shutdown in syslog fully today. Decommissioning logs the shutdown in syslog early today.

Decommissioning retires demo hosts after tickets today fully. Decommissioning retires demo hosts after backups today fully. Decommissioning retires demo hosts after wipes today fully. Decommissioning retires demo hosts after inventory today fully.

Decommissioning retires demo hosts after diagrams today fully. Decommissioning retires demo hosts after accounts today fully. Decommissioning retires demo hosts after keys today fully. Decommissioning retires demo hosts after names today fully.

Decommissioning retires demo hosts after annex today fully. Decommissioning retires lab hosts after tickets today fully. Decommissioning retires lab hosts after backups today fully. Decommissioning retires lab hosts after wipes today fully.

Decommissioning retires lab hosts after inventory today fully. Decommissioning retires lab hosts after diagrams today fully. Decommissioning retires lab hosts after accounts today fully. Decommissioning retires lab hosts after keys today fully.

Decommissioning retires lab hosts after names today fully. Decommissioning retires lab hosts after annex today fully. Decommissioning retires vendor hosts after tickets today fully. Decommissioning retires vendor hosts after backups today fully.

Decommissioning retires vendor hosts after wipes today fully. Decommissioning retires vendor hosts after inventory today fully. Decommissioning retires vendor hosts after diagrams today fully. Decommissioning retires vendor hosts after accounts today fully.

Decommissioning retires vendor hosts after keys today fully. Decommissioning retires vendor hosts after names today fully. Decommissioning retires vendor hosts after annex today fully. Decommissioning retires kiosk hosts after tickets today fully.

Decommissioning retires kiosk hosts after backups today fully. Decommissioning retires kiosk hosts after wipes today fully. Decommissioning retires kiosk hosts after inventory today fully. Decommissioning retires kiosk hosts after diagrams today fully.

Decommissioning retires kiosk hosts after accounts today fully. Decommissioning retires kiosk hosts after keys today fully. Decommissioning retires kiosk hosts after names today fully. Decommissioning retires kiosk hosts after annex today fully.

Decommissioning retires pilot hosts after tickets today fully. Decommissioning retires pilot hosts after backups today fully. Decommissioning retires pilot hosts after wipes today fully. Decommissioning retires pilot hosts after inventory today fully.

Decommissioning retires pilot hosts after diagrams today fully. Decommissioning retires pilot hosts after accounts today fully. Decommissioning retires pilot hosts after keys today fully. Decommissioning retires pilot hosts after names today fully.

Decommissioning retires pilot hosts after annex today fully. Decommissioning retires legacy hosts after tickets today fully. Decommissioning retires legacy hosts after backups today fully. Decommissioning retires legacy hosts after wipes today fully.

Decommissioning retires legacy hosts after inventory today fully. Decommissioning retires legacy hosts after diagrams today fully. Decommissioning retires legacy hosts after accounts today fully. Decommissioning retires legacy hosts after keys today fully.

Decommissioning retires legacy hosts after names today fully. Decommissioning retires legacy hosts after annex today fully. Decommissioning retires test hosts after tickets today fully. Decommissioning retires test hosts after backups today fully.

Decommissioning retires test hosts after wipes today fully. Decommissioning retires test hosts after inventory today fully. Decommissioning retires test hosts after diagrams today fully. Decommissioning retires test hosts after accounts today fully.

Decommissioning retires test hosts after keys today fully. Decommissioning retires test hosts after names today fully. Decommissioning retires test hosts after annex today fully. Decommissioning retires loan hosts after tickets today fully.

Decommissioning retires loan hosts after backups today fully.
''',
        'r0': '''
Decommissioning disable accounts the same day today fully. Decommissioning disable accounts the same week today fully. Decommissioning disable accounts the same ticket today fully. Decommissioning disable accounts the same hour today fully.

Decommissioning wipe disks before they leave today fully. Decommissioning wipe disks before they resell today fully. Decommissioning wipe disks before they donate today fully. Decommissioning wipe disks before they recycle today fully.

Decommissioning remove dns names and certs today fully. Decommissioning remove dns names and vpns today fully. Decommissioning remove dns names and keys today fully. Decommissioning remove dns names and agents today fully.

Decommissioning update inventory when power drops today fully. Decommissioning update inventory when power ends today fully. Decommissioning update inventory when power stops today fully. Decommissioning update inventory when power goes today fully.
''',
        'r1': '''
Decommissioning means turn it off on purpose today. Decommissioning means turn it off on record today. Decommissioning means turn it off on ticket today. Decommissioning means turn it off on schedule today.

Decommissioning takes the keys back too today fully. Decommissioning takes the keys back also today fully. Decommissioning takes the keys back fully today fully. Decommissioning takes the keys back early today fully.

Decommissioning stops forgotten systems staying online today fully. Decommissioning stops forgotten systems staying open today fully. Decommissioning stops forgotten systems staying live today fully. Decommissioning stops forgotten systems staying reachable today fully.
''',
        'r2': '''
Decommissioning resemble named ships struck off today fully. Decommissioning resemble old ships struck registers today fully. Decommissioning resemble retired ships struck lists today fully. Decommissioning resemble closed ships struck berths today fully.

Decommissioning feel like signed shops closing fully today. Decommissioning feel like keyed shops closing back today. Decommissioning feel like named shops closing done today. Decommissioning feel like ticketed shops closing shut today.

Decommissioning mirror planned exits with keys today fully. Decommissioning mirror recorded exits with power today fully. Decommissioning mirror owned exits with data today fully. Decommissioning mirror dated exits with diagrams today fully.

Decommissioning act as planned endings not drift today. Decommissioning act as owned endings not forgetting today. Decommissioning act as ticketed endings not lingering today. Decommissioning act as dated endings not ghosts today.
''',
        'r4': '''
Decommissioning disable accounts the same day today fully. Decommissioning disable accounts the same week today fully. Decommissioning disable accounts the same ticket today fully. Decommissioning disable accounts the same hour today fully.

Decommissioning disable accounts the same change today fully. Decommissioning wipe disks before they leave today fully. Decommissioning wipe disks before they resell today fully. Decommissioning wipe disks before they donate today fully.

Decommissioning wipe disks before they recycle today fully. Decommissioning wipe disks before they move today fully.
''',
        'exam': '''
Decommissioning fits when retirement is intentional today fully. Decommissioning fits when retirement is recorded today fully. Decommissioning fits when retirement is complete today fully. Decommissioning fits when retirement is owned today fully.

Decommissioning loses when the box stays forgotten today. Decommissioning loses when the box stays online today. Decommissioning loses when the box stays unnamed today. Decommissioning loses when the box stays keyed today.
''',
    },
    'Endpoint protection': {
        'body': '''
Endpoint protection watches hosts for malware and behavior. Endpoint protection watches hosts for malware and tools. Endpoint protection watches hosts for malware and hooks. Endpoint protection watches hosts for malware and drops.

Endpoint protection quarantines a trojan and still asks. Endpoint protection quarantines a trojan and still tickets. Endpoint protection quarantines a trojan and still traces. Endpoint protection quarantines a trojan and still hunts.

Endpoint protection logs quarantine events in syslog today. Endpoint protection logs quarantine events in console today. Endpoint protection logs quarantine events in alerts today. Endpoint protection logs quarantine events in tickets today.

Endpoint protection does not replace patching or backups. Endpoint protection does not replace patching or lists. Endpoint protection does not replace patching or segments. Endpoint protection does not replace patching or rights.

Endpoint protection differs from a firewall by watching. Endpoint protection differs from a firewall by behavior. Endpoint protection differs from a firewall by files. Endpoint protection differs from a firewall by process.

Endpoint protection flags inject behavior on laptops today. Endpoint protection flags inject behavior on kiosks today. Endpoint protection flags inject behavior on clinics today. Endpoint protection flags inject behavior on labs today.

Endpoint protection flags inject behavior on servers today. Endpoint protection flags inject behavior on jumps today. Endpoint protection flags inject behavior on images today. Endpoint protection flags inject behavior on desks today.

Endpoint protection flags inject behavior on annex today. Endpoint protection flags hook behavior on laptops today. Endpoint protection flags hook behavior on kiosks today. Endpoint protection flags hook behavior on clinics today.

Endpoint protection flags hook behavior on labs today. Endpoint protection flags hook behavior on servers today. Endpoint protection flags hook behavior on jumps today. Endpoint protection flags hook behavior on images today.

Endpoint protection flags hook behavior on desks today. Endpoint protection flags hook behavior on annex today. Endpoint protection flags encrypt behavior on laptops today. Endpoint protection flags encrypt behavior on kiosks today.

Endpoint protection flags encrypt behavior on clinics today. Endpoint protection flags encrypt behavior on labs today. Endpoint protection flags encrypt behavior on servers today. Endpoint protection flags encrypt behavior on jumps today.

Endpoint protection flags encrypt behavior on images today. Endpoint protection flags encrypt behavior on desks today. Endpoint protection flags encrypt behavior on annex today. Endpoint protection flags spawn behavior on laptops today.

Endpoint protection flags spawn behavior on kiosks today. Endpoint protection flags spawn behavior on clinics today. Endpoint protection flags spawn behavior on labs today. Endpoint protection flags spawn behavior on servers today.

Endpoint protection flags spawn behavior on jumps today. Endpoint protection flags spawn behavior on images today. Endpoint protection flags spawn behavior on desks today. Endpoint protection flags spawn behavior on annex today.

Endpoint protection flags persist behavior on laptops today. Endpoint protection flags persist behavior on kiosks today. Endpoint protection flags persist behavior on clinics today. Endpoint protection flags persist behavior on labs today.

Endpoint protection flags persist behavior on servers today. Endpoint protection flags persist behavior on jumps today. Endpoint protection flags persist behavior on images today. Endpoint protection flags persist behavior on desks today.

Endpoint protection flags persist behavior on annex today. Endpoint protection flags beacon behavior on laptops today. Endpoint protection flags beacon behavior on kiosks today. Endpoint protection flags beacon behavior on clinics today.

Endpoint protection flags beacon behavior on labs today. Endpoint protection flags beacon behavior on servers today. Endpoint protection flags beacon behavior on jumps today. Endpoint protection flags beacon behavior on images today.

Endpoint protection flags beacon behavior on desks today. Endpoint protection flags beacon behavior on annex today. Endpoint protection flags dump behavior on laptops today. Endpoint protection flags dump behavior on kiosks today.

Endpoint protection flags dump behavior on clinics today. Endpoint protection flags dump behavior on labs today. Endpoint protection flags dump behavior on servers today. Endpoint protection flags dump behavior on jumps today.

Endpoint protection flags dump behavior on images today. Endpoint protection flags dump behavior on desks today. Endpoint protection flags dump behavior on annex today. Endpoint protection flags rename behavior on laptops today.

Endpoint protection flags rename behavior on kiosks today.
''',
        'r0': '''
Endpoint protection review quarantine reasons not just counts. Endpoint protection review quarantine reasons not just names. Endpoint protection review quarantine reasons not just totals. Endpoint protection review quarantine reasons not just colors.

Endpoint protection keep agents current with content today. Endpoint protection keep agents current with engines today. Endpoint protection keep agents current with policies today. Endpoint protection keep agents current with certs today.

Endpoint protection test that tamper protection holds today. Endpoint protection test that tamper protection stays today. Endpoint protection test that tamper protection works today. Endpoint protection test that tamper protection alerts today.

Endpoint protection send detections to syslog centrally today. Endpoint protection send detections to syslog promptly today. Endpoint protection send detections to syslog fully today. Endpoint protection send detections to syslog live today.
''',
        'r1': '''
Endpoint protection means software on the computer watches. Endpoint protection means software on the computer checks. Endpoint protection means software on the computer guards. Endpoint protection means software on the computer looks.

Endpoint protection catches bad programs and odd behavior. Endpoint protection catches bad programs and odd actions. Endpoint protection catches bad programs and odd tools. Endpoint protection catches bad programs and odd hooks.

Endpoint protection is not a reason to skipatches. Endpoint protection is not a reason to skipbackups. Endpoint protection is not a reason to skiprights. Endpoint protection is not a reason to skiplists.
''',
        'r2': '''
Endpoint protection resemble desk sentries at level today. Endpoint protection resemble bench sentries at side today. Endpoint protection resemble counter sentries at edge today. Endpoint protection resemble station sentries at hand today.

Endpoint protection feel like room lookouts inside walls. Endpoint protection feel like shop lookouts inside floors. Endpoint protection feel like lab lookouts inside benches. Endpoint protection feel like ward lookouts inside desks.

Endpoint protection mirror program checks on behavior today. Endpoint protection mirror file checks on actions today. Endpoint protection mirror process checks on starts today. Endpoint protection mirror tool checks on hooks today.

Endpoint protection act as host watchers not patches. Endpoint protection act as local watchers not backups. Endpoint protection act as desk watchers not rights. Endpoint protection act as live watchers not segments.
''',
        'r4': '''
Endpoint protection review quarantine reasons daily today fully. Endpoint protection review quarantine reasons fully today fully. Endpoint protection review quarantine reasons early today fully. Endpoint protection review quarantine reasons live today fully.

Endpoint protection review quarantine reasons after today fully. Endpoint protection send detections to syslog today fully. Endpoint protection send detections to owners today fully. Endpoint protection send detections to tickets today fully.

Endpoint protection send detections to pages today fully. Endpoint protection send detections to hunts today fully.
''',
        'exam': '''
Endpoint protection fits when the host agent quarantines. Endpoint protection fits when the host agent blocks. Endpoint protection fits when the host agent alerts. Endpoint protection fits when the host agent watches.

Endpoint protection loses as a reason to skippatching. Endpoint protection loses as a reason to skipbackups. Endpoint protection loses as a reason to skiprights. Endpoint protection loses as a reason to skiplists.
''',
    },
    'Host firewalls': {
        'body': '''
Host firewalls filter packets on the computer itself. Host firewalls filter packets on the computer locally. Host firewalls filter packets on the computer too. Host firewalls filter packets on the computer still.

Host firewalls use iptables to drop stranger packets. Host firewalls use iptables to drop stranger probes. Host firewalls use iptables to drop stranger scans. Host firewalls use iptables to drop stranger inbound.

Host firewalls differ from IDS sensors that alert. Host firewalls differ from IDS sensors that watch. Host firewalls differ from IDS sensors that notice. Host firewalls differ from IDS sensors that record.

Host firewalls still matter behind a network firewall. Host firewalls still matter behind a network edge. Host firewalls still matter behind a network gateway. Host firewalls still matter behind a network filter.

Host firewalls allow management only from one subnet. Host firewalls allow management only from one jump. Host firewalls allow management only from one admin. Host firewalls allow management only from one bastion.

Host firewalls drop unexpected inbound using iptables today. Host firewalls drop unexpected inbound using policy today. Host firewalls drop unexpected inbound using baseline today. Host firewalls drop unexpected inbound using deny today.

Host firewalls drop unexpected inbound using rules today. Host firewalls drop unexpected inbound using profiles today. Host firewalls drop unsolicited inbound using iptables today. Host firewalls drop unsolicited inbound using policy today.

Host firewalls drop unsolicited inbound using baseline today. Host firewalls drop unsolicited inbound using deny today. Host firewalls drop unsolicited inbound using rules today. Host firewalls drop unsolicited inbound using profiles today.

Host firewalls drop scanned inbound using iptables today. Host firewalls drop scanned inbound using policy today. Host firewalls drop scanned inbound using baseline today. Host firewalls drop scanned inbound using deny today.

Host firewalls drop scanned inbound using rules today. Host firewalls drop scanned inbound using profiles today. Host firewalls drop stranger inbound using iptables today. Host firewalls drop stranger inbound using policy today.

Host firewalls drop stranger inbound using baseline today. Host firewalls drop stranger inbound using deny today. Host firewalls drop stranger inbound using rules today. Host firewalls drop stranger inbound using profiles today.

Host firewalls drop guest inbound using iptables today. Host firewalls drop guest inbound using policy today. Host firewalls drop guest inbound using baseline today. Host firewalls drop guest inbound using deny today.

Host firewalls drop guest inbound using rules today. Host firewalls drop guest inbound using profiles today. Host firewalls drop rogue inbound using iptables today. Host firewalls drop rogue inbound using policy today.
''',
        'r0': '''
Host firewalls set iptables input policy drop today. Host firewalls set iptables input policy deny today. Host firewalls set iptables input policy reject today. Host firewalls set iptables input policy tight today.

Host firewalls print rules with iptables -S today. Host firewalls print rules with iptables -L today. Host firewalls print rules with iptables -N today. Host firewalls print rules with iptables -V today.

Host firewalls log drops to syslog first today. Host firewalls log drops to syslog early today. Host firewalls log drops to syslog live today. Host firewalls log drops to syslog fully today.

Host firewalls allow admin subnets before drops today. Host firewalls allow admin subnets before denies today. Host firewalls allow admin subnets before rejects today. Host firewalls allow admin subnets before closes today.
''',
        'r1': '''
Host firewalls mean the computer has its ownrules. Host firewalls mean the computer has its owndoor. Host firewalls mean the computer has its ownlist. Host firewalls mean the computer has its ownfilter.

Host firewalls drop packets instead of only alerting. Host firewalls drop packets instead of only watching. Host firewalls drop packets instead of only noting. Host firewalls drop packets instead of only logging.

Host firewalls still help behind the big gateway. Host firewalls still help behind the big edge. Host firewalls still help behind the big firewall. Host firewalls still help behind the big border.
''',
        'r2': '''
Host firewalls resemble inner cabin rules too today. Host firewalls resemble local cabin rules still today. Host firewalls resemble room cabin rules also today. Host firewalls resemble desk cabin rules anyway today.

Host firewalls feel like bedroom latches inner today. Host firewalls feel like drawer latches extra today. Host firewalls feel like cabinet latches local today. Host firewalls feel like closet latches second today.

Host firewalls mirror inside doors buildings today fully. Host firewalls mirror local doors lobbies today fully. Host firewalls mirror room doors gates today fully. Host firewalls mirror cabin doors edges today fully.

Host firewalls act as host filters level today. Host firewalls act as local filters policy today. Host firewalls act as packet filters choices today. Host firewalls act as own filters rules today.
''',
        'r4': '''
Host firewalls set iptables policy to drop today. Host firewalls set iptables policy to deny today. Host firewalls set iptables policy to reject today. Host firewalls set iptables policy to tight today.

Host firewalls set iptables policy to baseline today. Host firewalls print iptables rules before changes today. Host firewalls print iptables rules before travel today. Host firewalls print iptables rules before loans today.

Host firewalls print iptables rules before images today. Host firewalls print iptables rules before pilots today.
''',
        'exam': '''
Host firewalls fit when the host filters packets. Host firewalls fit when the host filters inbound. Host firewalls fit when the host filters strangers. Host firewalls fit when the host filters scans.

Host firewalls lose when the tool only alerts. Host firewalls lose when the tool only watches. Host firewalls lose when the tool only notices. Host firewalls lose when the tool only records.
''',
    },
    'Host intrusion prevention': {
        'body': '''
Host intrusion prevention blocks behavior not only signatures. Host intrusion prevention blocks behavior not only hashes. Host intrusion prevention blocks behavior not only names. Host intrusion prevention blocks behavior not only files.

Host intrusion prevention stops injection into another process. Host intrusion prevention stops injection into another service. Host intrusion prevention stops injection into another binary. Host intrusion prevention stops injection into another task.

Host intrusion prevention differs from IDS by blocking. Host intrusion prevention differs from IDS by stopping. Host intrusion prevention differs from IDS by preventing. Host intrusion prevention differs from IDS by halting.

Host intrusion prevention differs from firewalls by behavior. Host intrusion prevention differs from firewalls by processes. Host intrusion prevention differs from firewalls by actions. Host intrusion prevention differs from firewalls by calls.

Host intrusion prevention logs blocks in syslog promptly. Host intrusion prevention logs blocks in syslog fully. Host intrusion prevention logs blocks in syslog live. Host intrusion prevention logs blocks in syslog early.

Host intrusion prevention halts inject actions on laptops. Host intrusion prevention halts inject actions on servers. Host intrusion prevention halts inject actions on kiosks. Host intrusion prevention halts inject actions on clinics.

Host intrusion prevention halts inject actions on labs. Host intrusion prevention halts inject actions on jumps. Host intrusion prevention halts hook actions on laptops. Host intrusion prevention halts hook actions on servers.

Host intrusion prevention halts hook actions on kiosks. Host intrusion prevention halts hook actions on clinics. Host intrusion prevention halts hook actions on labs. Host intrusion prevention halts hook actions on jumps.

Host intrusion prevention halts hollow actions on laptops. Host intrusion prevention halts hollow actions on servers. Host intrusion prevention halts hollow actions on kiosks. Host intrusion prevention halts hollow actions on clinics.

Host intrusion prevention halts hollow actions on labs. Host intrusion prevention halts hollow actions on jumps. Host intrusion prevention halts dump actions on laptops. Host intrusion prevention halts dump actions on servers.

Host intrusion prevention halts dump actions on kiosks. Host intrusion prevention halts dump actions on clinics. Host intrusion prevention halts dump actions on labs. Host intrusion prevention halts dump actions on jumps.

Host intrusion prevention halts encrypt actions on laptops. Host intrusion prevention halts encrypt actions on servers. Host intrusion prevention halts encrypt actions on kiosks. Host intrusion prevention halts encrypt actions on clinics.

Host intrusion prevention halts encrypt actions on labs. Host intrusion prevention halts encrypt actions on jumps. Host intrusion prevention halts spawn actions on laptops. Host intrusion prevention halts spawn actions on servers.
''',
        'r0': '''
Host intrusion prevention block process injection early today. Host intrusion prevention block process injection live today. Host intrusion prevention block process injection fully today. Host intrusion prevention block process injection fast today.

Host intrusion prevention alert and stop not onlywatch. Host intrusion prevention alert and stop not onlylog. Host intrusion prevention alert and stop not onlypage. Host intrusion prevention alert and stop not onlynote.

Host intrusion prevention tune after real app pilots. Host intrusion prevention tune after real app tickets. Host intrusion prevention tune after real app owners. Host intrusion prevention tune after real app tests.

Host intrusion prevention send blocks to syslog centrally. Host intrusion prevention send blocks to syslog live. Host intrusion prevention send blocks to syslog fully. Host intrusion prevention send blocks to syslog promptly.
''',
        'r1': '''
Host intrusion prevention means bad behavior gets stopped. Host intrusion prevention means bad behavior gets blocked. Host intrusion prevention means bad behavior gets halted. Host intrusion prevention means bad behavior gets cut.

Host intrusion prevention does more than a camera. Host intrusion prevention does more than a note. Host intrusion prevention does more than a log. Host intrusion prevention does more than a watch.

Host intrusion prevention looks actions not only names. Host intrusion prevention looks actions not only files. Host intrusion prevention looks actions not only hashes. Host intrusion prevention looks actions not only lists.
''',
        'r2': '''
Host intrusion prevention resemble line referees stopping today. Host intrusion prevention resemble field referees halting today. Host intrusion prevention resemble court referees blocking today. Host intrusion prevention resemble lane referees cutting today.

Host intrusion prevention feel like live judges calls. Host intrusion prevention feel like instant judges stops. Host intrusion prevention feel like active judges blocks. Host intrusion prevention feel like present judges halts.

Host intrusion prevention mirror acting guards now today. Host intrusion prevention mirror stopping guards fights today. Host intrusion prevention mirror halting guards moves today. Host intrusion prevention mirror blocking guards blows today.

Host intrusion prevention act as host prevention live. Host intrusion prevention act as behavior prevention blocks. Host intrusion prevention act as action prevention stops. Host intrusion prevention act as process prevention halts.
''',
        'r4': '''
Host intrusion prevention block process injection early today. Host intrusion prevention block process injection live today. Host intrusion prevention block process injection fully today. Host intrusion prevention block process injection fast today.

Host intrusion prevention block process injection now today. Host intrusion prevention tune blocks with app owners. Host intrusion prevention tune blocks with app pilots. Host intrusion prevention tune blocks with app tickets.

Host intrusion prevention tune blocks with app tests. Host intrusion prevention tune blocks with app labs.
''',
        'exam': '''
Host intrusion prevention fit when behavior is stopped. Host intrusion prevention fit when behavior is blocked. Host intrusion prevention fit when behavior is halted. Host intrusion prevention fit when behavior is prevented.

Host intrusion prevention lose when tool only alerts. Host intrusion prevention lose when tool only records. Host intrusion prevention lose when tool only watches. Host intrusion prevention lose when tool only logs.
''',
    },
    'Disabling unused ports and protocols': {
        'body': '''
Disabling unused ports and protocols shows iptables -S. Disabling unused ports and protocols shows iptables -L. Disabling unused ports and protocols shows iptables -N. Disabling unused ports and protocols shows iptables -V.

Disabling unused ports and protocols runs ss -lnt. Disabling unused ports and protocols runs ss -l. Disabling unused ports and protocols runs ss -t. Disabling unused ports and protocols runs ss -u.

Disabling unused ports and protocols closes unused telnet. Disabling unused ports and protocols closes forgotten ftp. Disabling unused ports and protocols closes legacy rpc. Disabling unused ports and protocols closes extra smb.

Disabling unused ports and protocols shuts old protocols. Disabling unused ports and protocols shuts idle listeners. Disabling unused ports and protocols shuts stale daemons. Disabling unused ports and protocols shuts spare services.

Disabling unused ports and protocols drops telnet listeners. Disabling unused ports and protocols drops telnet daemons. Disabling unused ports and protocols drops telnet services. Disabling unused ports and protocols drops telnet sockets.

Disabling unused ports and protocols drops telnet banners. Disabling unused ports and protocols drops telnet legacy. Disabling unused ports and protocols drops telnet extras. Disabling unused ports and protocols drops telnet defaults.

Disabling unused ports and protocols drops ftp listeners. Disabling unused ports and protocols drops ftp daemons. Disabling unused ports and protocols drops ftp services. Disabling unused ports and protocols drops ftp sockets.

Disabling unused ports and protocols drops ftp banners. Disabling unused ports and protocols drops ftp legacy. Disabling unused ports and protocols drops ftp extras. Disabling unused ports and protocols drops ftp defaults.

Disabling unused ports and protocols drops rpc listeners. Disabling unused ports and protocols drops rpc daemons. Disabling unused ports and protocols drops rpc services. Disabling unused ports and protocols drops rpc sockets.

Disabling unused ports and protocols drops rpc banners. Disabling unused ports and protocols drops rpc legacy. Disabling unused ports and protocols drops rpc extras. Disabling unused ports and protocols drops rpc defaults.

Disabling unused ports and protocols drops smb listeners. Disabling unused ports and protocols drops smb daemons. Disabling unused ports and protocols drops smb services. Disabling unused ports and protocols drops smb sockets.

Disabling unused ports and protocols drops smb banners. Disabling unused ports and protocols drops smb legacy. Disabling unused ports and protocols drops smb extras. Disabling unused ports and protocols drops smb defaults.

Disabling unused ports and protocols drops rdp listeners. Disabling unused ports and protocols drops rdp daemons. Disabling unused ports and protocols drops rdp services. Disabling unused ports and protocols drops rdp sockets.
''',
        'r0': '''
Disabling unused ports and protocols list listeners nightly. Disabling unused ports and protocols list listeners fully. Disabling unused ports and protocols list listeners live. Disabling unused ports and protocols list listeners early.

Disabling unused ports and protocols compare ss output. Disabling unused ports and protocols compare ss baseline. Disabling unused ports and protocols compare ss images. Disabling unused ports and protocols compare ss tickets.

Disabling unused ports and protocols disable legacy protocols. Disabling unused ports and protocols disable legacy suites. Disabling unused ports and protocols disable legacy auth. Disabling unused ports and protocols disable legacy shares.

Disabling unused ports and protocols log closures centrally. Disabling unused ports and protocols log closures clearly. Disabling unused ports and protocols log closures fully. Disabling unused ports and protocols log closures once.
''',
        'r1': '''
Disabling unused ports and protocols means close unused. Disabling unused ports and protocols means close extra. Disabling unused ports and protocols means close old. Disabling unused ports and protocols means close idle.

Disabling unused ports and protocols stops listening needlessly. Disabling unused ports and protocols stops listening forever. Disabling unused ports and protocols stops listening openly. Disabling unused ports and protocols stops listening widely.

Disabling unused ports and protocols shrinks what answers. Disabling unused ports and protocols shrinks what listens. Disabling unused ports and protocols shrinks what speaks. Disabling unused ports and protocols shrinks what offers.
''',
        'r2': '''
Disabling unused ports and protocols resemble boarded hatches. Disabling unused ports and protocols resemble shut shutters. Disabling unused ports and protocols resemble sealed tubes. Disabling unused ports and protocols resemble closed gates.

Disabling unused ports and protocols feel like latches. Disabling unused ports and protocols feel like bells. Disabling unused ports and protocols feel like levers. Disabling unused ports and protocols feel like switches.

Disabling unused ports and protocols mirror quiet rooms. Disabling unused ports and protocols mirror dark lamps. Disabling unused ports and protocols mirror locked drawers. Disabling unused ports and protocols mirror covered vents.

Disabling unused ports and protocols act as closure. Disabling unused ports and protocols act as shrinkage. Disabling unused ports and protocols act as silence. Disabling unused ports and protocols act as reduction.
''',
        'r4': '''
Disabling unused ports and protocols list listeners tonight. Disabling unused ports and protocols list listeners fully. Disabling unused ports and protocols list listeners live. Disabling unused ports and protocols list listeners early.

Disabling unused ports and protocols list listeners again. Disabling unused ports and protocols close unused listeners. Disabling unused ports and protocols close unused daemons. Disabling unused ports and protocols close unused services.

Disabling unused ports and protocols close unused sockets. Disabling unused ports and protocols close unused legacy.
''',
        'exam': '''
Disabling unused ports and protocols fit unused listeners. Disabling unused ports and protocols fit unused protocols. Disabling unused ports and protocols fit unused daemons. Disabling unused ports and protocols fit unused services.

Disabling unused ports and protocols lose needed services. Disabling unused ports and protocols lose needed paths. Disabling unused ports and protocols lose needed listeners. Disabling unused ports and protocols lose needed jobs.
''',
    },
    'Changing default passwords': {
        'body': '''
Changing default passwords replaces vendor secrets before cabling. Changing default passwords replaces vendor secrets before joining. Changing default passwords replaces vendor secrets before routing. Changing default passwords replaces vendor secrets before exposure.

Changing default passwords stores new secrets in vaults. Changing default passwords stores new secrets in safes. Changing default passwords stores new secrets in tickets. Changing default passwords stores new secrets in custodians.

Changing default passwords shows defaults in auth.log early. Changing default passwords shows defaults in auth.log still. Changing default passwords shows defaults in auth.log live. Changing default passwords shows defaults in auth.log first.

Changing default passwords differs from rotation by firstuse. Changing default passwords differs from rotation by dayone. Changing default passwords differs from rotation by install. Changing default passwords differs from rotation by arrival.

Changing default passwords covers switches cameras and printers. Changing default passwords covers switches cameras and badges. Changing default passwords covers switches cameras and kiosks. Changing default passwords covers switches cameras and controllers.

Changing default passwords changes switch secrets before cabling. Changing default passwords changes switch secrets before routing. Changing default passwords changes switch secrets before exposure. Changing default passwords changes switch secrets before imaging.

Changing default passwords changes switch secrets before joining. Changing default passwords changes switch secrets before power. Changing default passwords changes camera secrets before cabling. Changing default passwords changes camera secrets before routing.

Changing default passwords changes camera secrets before exposure. Changing default passwords changes camera secrets before imaging. Changing default passwords changes camera secrets before joining. Changing default passwords changes camera secrets before power.

Changing default passwords changes printer secrets before cabling. Changing default passwords changes printer secrets before routing. Changing default passwords changes printer secrets before exposure. Changing default passwords changes printer secrets before imaging.

Changing default passwords changes printer secrets before joining. Changing default passwords changes printer secrets before power. Changing default passwords changes badge secrets before cabling. Changing default passwords changes badge secrets before routing.

Changing default passwords changes badge secrets before exposure. Changing default passwords changes badge secrets before imaging. Changing default passwords changes badge secrets before joining. Changing default passwords changes badge secrets before power.

Changing default passwords changes kiosk secrets before cabling. Changing default passwords changes kiosk secrets before routing. Changing default passwords changes kiosk secrets before exposure. Changing default passwords changes kiosk secrets before imaging.

Changing default passwords changes kiosk secrets before joining. Changing default passwords changes kiosk secrets before power. Changing default passwords changes controller secrets before cabling. Changing default passwords changes controller secrets before routing.
''',
        'r0': '''
Changing default passwords check auth.log for vendor names. Changing default passwords check auth.log for vendor logins. Changing default passwords check auth.log for vendor fails. Changing default passwords check auth.log for vendor successes.

Changing default passwords vault the new secret immediately. Changing default passwords vault the new secret once. Changing default passwords vault the new secret fully. Changing default passwords vault the new secret early.

Changing default passwords block install until the change. Changing default passwords block install until the vault. Changing default passwords block install until the test. Changing default passwords block install until the ticket.

Changing default passwords inventory devices that ship secrets. Changing default passwords inventory devices that ship logins. Changing default passwords inventory devices that ship accounts. Changing default passwords inventory devices that ship passes.
''',
        'r1': '''
Changing default passwords means change the sticker secret. Changing default passwords means change the sticker login. Changing default passwords means change the sticker code. Changing default passwords means change the sticker word.

Changing default passwords happens before the device joins. Changing default passwords happens before the device routes. Changing default passwords happens before the device serves. Changing default passwords happens before the device listens.

Changing default passwords puts new secret in avault. Changing default passwords puts new secret in asafe. Changing default passwords puts new secret in aticket. Changing default passwords puts new secret in acustody.
''',
        'r2': '''
Changing default passwords resemble recut locks first today. Changing default passwords resemble rekeyed locks early today. Changing default passwords resemble changed locks arrival today. Changing default passwords resemble fresh locks dayone today.

Changing default passwords feel like carton combinations changed. Changing default passwords feel like sticker combinations replaced. Changing default passwords feel like printed combinations retired. Changing default passwords feel like factory combinations gone.

Changing default passwords mirror new keys before today. Changing default passwords mirror fresh keys entry today. Changing default passwords mirror owned keys secrets today. Changing default passwords mirror vaulted keys codes today.

Changing default passwords act as day first steps. Changing default passwords act as install first work. Changing default passwords act as arrival first care. Changing default passwords act as setup first duty.
''',
        'r4': '''
Changing default passwords change vendor secrets first today. Changing default passwords change vendor secrets today today. Changing default passwords change vendor secrets fully today. Changing default passwords change vendor secrets early today.

Changing default passwords change vendor secrets once today. Changing default passwords vault new secrets immediately today. Changing default passwords vault new secrets together today. Changing default passwords vault new secrets fully today.

Changing default passwords vault new secrets offline today. Changing default passwords vault new secrets named today.
''',
        'exam': '''
Changing default passwords fit before the device joins. Changing default passwords fit before the device routes. Changing default passwords fit before the device serves. Changing default passwords fit before the device listens.

Changing default passwords lose after it is exposed. Changing default passwords lose after it is routed. Changing default passwords lose after it is joined. Changing default passwords lose after it is public.
''',
    },
    'Removing unnecessary software': {
        'body': '''
Removing unnecessary software shrinks programs that can break. Removing unnecessary software shrinks programs that can leak. Removing unnecessary software shrinks programs that can run. Removing unnecessary software shrinks programs that can fail.

Removing unnecessary software drops games trials and toolbars. Removing unnecessary software drops games trials and runtimes. Removing unnecessary software drops games trials and helpers. Removing unnecessary software drops games trials and extras.

Removing unnecessary software shows leftovers in tasklist still. Removing unnecessary software shows leftovers in tasklist early. Removing unnecessary software shows leftovers in tasklist live. Removing unnecessary software shows leftovers in tasklist fully.

Removing unnecessary software differs from patching by removal. Removing unnecessary software differs from patching by absence. Removing unnecessary software differs from patching by shrinkage. Removing unnecessary software differs from patching by deletion.

Removing unnecessary software supports allow lists by naming. Removing unnecessary software supports allow lists by fewer. Removing unnecessary software supports allow lists by clarity. Removing unnecessary software supports allow lists by scope.

Removing unnecessary software removes game tools from images. Removing unnecessary software removes game tools from laptops. Removing unnecessary software removes game tools from kiosks. Removing unnecessary software removes game tools from labs.

Removing unnecessary software removes game tools from clinics. Removing unnecessary software removes game tools from loans. Removing unnecessary software removes trial tools from images. Removing unnecessary software removes trial tools from laptops.

Removing unnecessary software removes trial tools from kiosks. Removing unnecessary software removes trial tools from labs. Removing unnecessary software removes trial tools from clinics. Removing unnecessary software removes trial tools from loans.

Removing unnecessary software removes toolbar tools from images. Removing unnecessary software removes toolbar tools from laptops. Removing unnecessary software removes toolbar tools from kiosks. Removing unnecessary software removes toolbar tools from labs.

Removing unnecessary software removes toolbar tools from clinics. Removing unnecessary software removes toolbar tools from loans. Removing unnecessary software removes runtime tools from images. Removing unnecessary software removes runtime tools from laptops.

Removing unnecessary software removes runtime tools from kiosks. Removing unnecessary software removes runtime tools from labs. Removing unnecessary software removes runtime tools from clinics. Removing unnecessary software removes runtime tools from loans.

Removing unnecessary software removes helper tools from images. Removing unnecessary software removes helper tools from laptops. Removing unnecessary software removes helper tools from kiosks. Removing unnecessary software removes helper tools from labs.

Removing unnecessary software removes helper tools from clinics. Removing unnecessary software removes helper tools from loans. Removing unnecessary software removes coupon tools from images. Removing unnecessary software removes coupon tools from laptops.
''',
        'r0': '''
Removing unnecessary software compare tasklist with the image. Removing unnecessary software compare tasklist with the catalog. Removing unnecessary software compare tasklist with the baseline. Removing unnecessary software compare tasklist with the ticket.

Removing unnecessary software remove old runtimes before handoff. Removing unnecessary software remove old runtimes before imaging. Removing unnecessary software remove old runtimes before loan. Removing unnecessary software remove old runtimes before deploy.

Removing unnecessary software record what left the image. Removing unnecessary software record what left the build. Removing unnecessary software record what left the host. Removing unnecessary software record what left the ticket.

Removing unnecessary software recheck after vendor updates today. Removing unnecessary software recheck after vendor bundles today. Removing unnecessary software recheck after vendor agents today. Removing unnecessary software recheck after vendor drivers today.
''',
        'r1': '''
Removing unnecessary software means fewer programs fewer holes. Removing unnecessary software means fewer programs fewer risks. Removing unnecessary software means fewer programs fewer bugs. Removing unnecessary software means fewer programs fewer surprises.

Removing unnecessary software clears tools you do use. Removing unnecessary software clears tools you do need. Removing unnecessary software clears tools you do trust. Removing unnecessary software clears tools you do name.

Removing unnecessary software happens before a laptop leaves. Removing unnecessary software happens before a laptop ships. Removing unnecessary software happens before a laptop loans. Removing unnecessary software happens before a laptop deploys.
''',
        'r2': '''
Removing unnecessary software resemble cleared benches counters today. Removing unnecessary software resemble bare benches hooks today. Removing unnecessary software resemble empty benches trays today. Removing unnecessary software resemble open benches racks today.

Removing unnecessary software feel like sorted drawers tools. Removing unnecessary software feel like named drawers only. Removing unnecessary software feel like needed drawers gear. Removing unnecessary software feel like daily drawers kits.

Removing unnecessary software mirror smaller kits sets today. Removing unnecessary software mirror tighter kits bags today. Removing unnecessary software mirror lighter kits belts today. Removing unnecessary software mirror chosen kits tools today.

Removing unnecessary software act as surface shrinkage work. Removing unnecessary software act as program shrinkage care. Removing unnecessary software act as image shrinkage hygiene. Removing unnecessary software act as tool shrinkage limits.
''',
        'r4': '''
Removing unnecessary software compare tasklist with images today. Removing unnecessary software compare tasklist with catalogs today. Removing unnecessary software compare tasklist with baselines today. Removing unnecessary software compare tasklist with tickets today.

Removing unnecessary software compare tasklist with builds today. Removing unnecessary software remove unused runtimes first today. Removing unnecessary software remove unused runtimes fully today. Removing unnecessary software remove unused runtimes early today.

Removing unnecessary software remove unused runtimes today today. Removing unnecessary software remove unused runtimes again today.
''',
        'exam': '''
Removing unnecessary software fit when unused programs leave. Removing unnecessary software fit when unused programs shrink. Removing unnecessary software fit when unused programs drop. Removing unnecessary software fit when unused programs go.

Removing unnecessary software lose when you only patch. Removing unnecessary software lose when you only watch. Removing unnecessary software lose when you only rename. Removing unnecessary software lose when you only hide.
''',
    },
}
