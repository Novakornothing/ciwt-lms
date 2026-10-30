"""Original one-line teachings for every Security topic leaf.

R0 uses the technical lines. R1 uses the plain line. R2 uses the story.
Those three vocabularies stay apart so the five paths are genuinely different.
"""

# name -> (means, case, plain, story)
GLOSS = {}


def g(name, means, case, plain, story):
    if name in GLOSS:
        raise ValueError('duplicate gloss ' + name)
    GLOSS[name] = (means, case, plain, story)


# --- 1.1 controls ---
g('Technical controls',
  'A technical control is a setting or tool on a system that enforces a rule even when nobody is watching.',
  'A firewall drops inbound administration traffic from the internet while the office is closed.',
  'The box itself says no.',
  'A turnstile does not care that the visitor is in a hurry.')
g('Managerial controls',
  'A managerial control is a decision written down: a policy, a standard, or a risk acceptance with an owner.',
  'Leadership signs a rule that customer lists may not be copied to personal mail.',
  'Someone in charge writes the rule and owns it.',
  'The clinic director posts who may enter the records room, and signs the page.')
g('Operational controls',
  'An operational control is a habit people practice, such as training, a backup drill, or a visitor log.',
  'Every Friday the desk practices restoring one file and writes down how long it took.',
  'People practice the habit, not only the poster.',
  'The night crew walks the fire drill until the route is boring.')
g('Physical controls',
  'A physical control is a tangible barrier: a lock, a badge reader, a camera, or a guard.',
  'The server closet door will not open without a badge, even for someone who knows the wifi password.',
  'A real-world barrier stands in the way.',
  'A locked cupboard keeps the spare keys off the lobby counter.')
g('Preventive controls',
  'A preventive control stops the bad action before it succeeds.',
  'A badge reader refuses a stranger before that person reaches the racks.',
  'It blocks the trouble before it starts.',
  'A bike lock works before the ride-away, not after the empty rack.')
g('Deterrent controls',
  'A deterrent control makes the bad action look costly so many people choose not to try.',
  'A sign, a camera dome, and a light over the door convince a passerby to keep walking.',
  'It warns people off before they try.',
  'A barking dog behind a fence changes a stranger\'s mind.')
g('Detective controls',
  'A detective control notices that something already happened and raises a signal.',
  'An alert fires after a login from a country the user has never visited.',
  'It tells you after the fact.',
  'A smoke alarm does not put out the match. It shouts.')
g('Corrective controls',
  'A corrective control repairs damage or restores a known-good state after something went wrong.',
  'After ransomware, the team restores last night\'s clean copy and resets the affected accounts.',
  'It cleans up after the mess.',
  'The mop comes out after the spill, not before it.')
g('Compensating controls',
  'A compensating control is a stand-in when the preferred control cannot be used yet.',
  'An old app cannot do multi-factor sign-in, so the team allows it only from one admin jump host.',
  'A second lock covers for the one you cannot fit.',
  'The side door has no badge reader, so a guard stands there during the remodel.')
g('Directive controls',
  'A directive control tells people what they must do, such as a mandatory procedure or a posted instruction.',
  'The change procedure says every firewall edit needs a ticket number before it is typed.',
  'It gives an order people are expected to follow.',
  'The recipe card says wash hands first, and the cook is supposed to obey.')

# --- 1.2 concepts ---
g('Confidentiality',
  'Confidentiality means only approved readers can see the data.',
  'A payroll sheet is forwarded to a personal mailbox.',
  'Only the right folks may see the secret.',
  'A clasped diary stops a roommate from reading the page.')
g('Integrity',
  'Integrity means the contents were not changed unless an approved person changed them.',
  'An invoice total is edited after the manager already approved it.',
  'The message should arrive the way it was sent.',
  'A sealed evidence bag shows whether someone opened it.')
g('Availability',
  'Availability means the approved service is usable at the time the work needs it.',
  'The payroll site is up but so slow that nobody can submit timesheets on Friday afternoon.',
  'People can do the job when they need to.',
  'A clinic door locked all morning protects privacy and also blocks care.')
g('Non-repudiation',
  'Non-repudiation means the actor cannot credibly deny the action later because the proof is tied to them.',
  'A signed approval record shows which manager released the payment, and that manager cannot shrug it off.',
  'You can show who did it, later.',
  'A signed delivery slip keeps the courier from saying the parcel never left.')
g('Authentication',
  'Authentication answers who is asking, by checking a secret, a device, or a body trait.',
  'A user proves identity with a password plus a prompt on a phone they carry.',
  'Prove you are you, before the door opens.',
  'The desk checks a photo ID before handing over the chart.')
g('Authorization',
  'Authorization answers what that identified person is allowed to do.',
  'The nurse can read the chart but cannot approve a drug order the policy reserves for a doctor.',
  'Being known is not the same as being allowed.',
  'The badge opens the lobby, not the pharmacy safe.')
g('Accounting',
  'Accounting records who did what, and when, so the action can be reviewed.',
  'The payment system writes the user, the amount, and the time for every transfer.',
  'Write down who did the thing.',
  'The sign-out sheet shows which nurse took the narcotics cabinet key.')
g('Gap analysis',
  'A gap analysis compares the control you have with the control the rule requires, and names the difference.',
  'The standard wants disk encryption on every laptop, and twelve loaner laptops have none.',
  'Compare what you have with what the rule demands.',
  'The inspector\'s checklist has a blank line where the extinguisher should be.')
g('Adaptive identity',
  'Adaptive identity changes how hard the sign-in is based on risk signals such as place, device, and behavior.',
  'A login from the usual office laptop is quiet, but the same account from a new country must pass an extra check.',
  'A stranger place earns a harder question.',
  'The doorman waves at regulars and stops to ask visitors for a name.')
g('Threat scope reduction',
  'Threat scope reduction shrinks how far one compromise can travel.',
  'A breached guest laptop cannot reach the payroll servers because the networks are separated.',
  'Make one broken thing less able to burn the rest.',
  'A fire door keeps a kitchen flare out of the dining room.')
g('Policy-driven access',
  'Policy-driven access grants entry from rules, not from a standing assumption that the inside is safe.',
  'The file share opens only when the user, the device health, and the hour all match the written rule.',
  'The rule decides, every time.',
  'The pharmacy window opens only when the prescription and the ID both match.')
g('Policy administrator',
  'The policy administrator tells the enforcer the decision: allow, deny, or revoke.',
  'After the engine says deny, the administrator pushes that deny to the gateway in front of the app.',
  'This role delivers the yes or the no.',
  'The head nurse tells the door guard the visitor is not on today\'s list.')
g('Policy engine',
  'The policy engine is the decider that weighs signals against the rules and produces allow or deny.',
  'The engine sees a healthy device and a normal hour and returns allow for the mail app.',
  'This part thinks. It does not stand at the door.',
  'The charge nurse reads the chart and decides, then someone else walks the patient in.')
g('Implicit trust zones',
  'An implicit trust zone is a network area that still assumes "inside means safe," which zero trust refuses to do.',
  'Once a laptop is on the office wifi, every internal app accepts it with no further check.',
  'Being inside the building is not a free pass.',
  'A wristband for the fair should not also open the cash office.')
g('Subjects and systems',
  'Subjects are the people or services asking, and systems are the things they ask. Both must be identified.',
  'A backup job is a subject. The payroll database is a system. The rule names both.',
  'Name the asker and the thing being asked.',
  'The form has a line for the person and a line for the room they want.')
g('Policy enforcement point',
  'The policy enforcement point is the gate that actually allows or blocks the request.',
  'The application gateway drops the session when the decision comes back deny.',
  'This is the door that moves.',
  'The guard, not the rulebook, is the one who stops the visitor.')
g('Bollards',
  'Bollards are short sturdy posts that stop a vehicle from reaching a door or a storefront.',
  'A car cannot jump the curb into the clinic entrance because steel posts stand in the way.',
  'Posts that stop a car.',
  'Stones in front of a shop window keep a runaway cart from smashing the glass.')
g('Access-control vestibule',
  'An access-control vestibule is a small two-door room where the first door must close before the second opens.',
  'A tailgater stuck between the lobby doors cannot reach the office until the desk releases the inner door.',
  'Two doors, and only one opens at a time.',
  'An airlock lets one person through, not a crowd hanging on a coat.')
g('Fencing',
  'Fencing marks and delays entry to a yard, a roof, or a lot, and it works best with lighting and a watch.',
  'The generator yard has a fence tall enough that a casual climb is obvious on camera.',
  'A fence slows people down and shows the boundary.',
  'A garden fence does not stop a determined thief, but it shows who stepped over.')
g('Video surveillance',
  'Video surveillance records or watches a space so you can see what happened, and sometimes who.',
  'The loading dock camera shows a person propping the door at 02:10, which the badge log missed.',
  'Cameras remember the scene. They do not lock the door.',
  'A shop camera shows the empty shelf later. It did not hold the door shut.')
g('Security guards',
  'A security guard is a person who can challenge, escort, and respond when a sensor or a camera cannot judge intent.',
  'The guard walks the visitor to the conference room and waits while the host comes down.',
  'A person who can ask "who are you here for?"',
  'A receptionist who actually looks up is a guard in softer clothes.')
g('Access badges',
  'An access badge is a token the door checks. Lost badges must be disabled the same day.',
  'A former contractor\'s badge still opens the side door because nobody revoked it on the last day.',
  'A card is a key. Cancel it when the person leaves.',
  'A hotel keycard should die at checkout, not next month.')
g('Protective lighting',
  'Protective lighting removes dark hiding spots around doors, fences, and parking so people and cameras can see.',
  'The rear door camera is useless until the lamp above it is replaced.',
  'Light makes sneaking harder.',
  'A porch lamp keeps the package thief from working unseen.')
g('Infrared sensors',
  'Infrared sensors notice heat or a broken invisible beam, which fits doorways and short halls.',
  'A beam across the closet door trips when someone steps through after hours.',
  'It notices heat or a broken beam.',
  'A store door chime made of light, not sound.')
g('Pressure sensors',
  'Pressure sensors notice weight on a mat, a pad, or a floor, which fits a spot where feet must land.',
  'A mat inside the records room alarms when someone stands on it while the door contact stays quiet.',
  'It notices weight where a person must step.',
  'A loose stair that creaks only when a foot lands.')
g('Microwave sensors',
  'Microwave sensors flood a volume with radio energy and notice movement that disturbs the field.',
  'The warehouse bay uses microwave sensors because the space is too wide for a single beam.',
  'It notices motion in a big open room.',
  'A pond ripple shows that something moved, even at the far edge.')
g('Ultrasonic sensors',
  'Ultrasonic sensors do a similar job with sound people cannot hear, and they struggle through heavy curtains and soft rooms.',
  'A plush conference room full of drapes is a poor place for ultrasonic sensors, so the team picks another type.',
  'Silent sound that notices motion, unless the room swallows it.',
  'A bat\'s squeak bounces off a wall and gets lost in heavy curtains.')
g('Honeypots',
  'A honeypot is a decoy system that should never receive real work, so any touch is suspicious.',
  'An unused server that mimics a file share logs every login attempt and pages the on-call person.',
  'A fake box. Nobody real should knock.',
  'A dummy wallet on the counter. The person who grabs it is the one you watch.')
g('Honeynets',
  'A honeynet is a small network of decoys, used when you want to watch how an intruder moves, not just one box.',
  'The lab keeps a fake segment of servers that production accounts are not allowed to use.',
  'A whole fake street, not one fake house.',
  'A row of empty storefronts. Footsteps there are not customers.')
g('Honeyfiles',
  'A honeyfile is a decoy document that legitimate jobs never open, so an open is a signal.',
  'A folder named salaries-full.xls sits where payroll staff are told never to click, and an open creates an alert.',
  'A fake file. Opening it is the alarm.',
  'A marked bill in the till. If it shows up later, you know the drawer was touched.')
g('Honeytokens',
  'A honeytoken is a fake credential, record, or key that has no real use, so using it means theft.',
  'A dummy API key in a private repo triggers an alert the moment it is used from the internet.',
  'A fake secret. Using it proves someone stole it.',
  'A spare house key that opens nothing, hidden where only a snooper would look.')

# --- 1.3 change ---
g('Change approval',
  'Change approval is the recorded yes from the person allowed to accept the risk of the edit.',
  'A firewall rule is typed at midnight with no ticket and no approver.',
  'Get the yes, in writing, before the edit.',
  'The kitchen does not change the menu until the owner nods.')
g('Change ownership',
  'Change ownership names the person who will carry the change and answer questions after it lands.',
  'The ticket says "network team" and nobody knows who will roll the rule back if mail breaks.',
  'One person owns the change, by name.',
  'One cook owns the new soup, not "the kitchen" in general.')
g('Stakeholders',
  'Stakeholders are the people who feel the change: the requester, the operators, and anyone whose work stops.',
  'Payroll is not told that the file server will reboot during Friday close.',
  'Tell the people whose work will stop.',
  'You warn the diners before you close the kitchen for the stove repair.')
g('Impact analysis',
  'Impact analysis lists what can break, who is affected, and how bad that is, before you start.',
  'Rebooting the identity server also stops wifi sign-in, which the ticket never mentioned.',
  'Write what can break before you touch it.',
  'The plumber asks which rooms lose water before closing the main valve.')
g('Test results',
  'Test results are the evidence that the change worked in a safe place, or that it failed and should not go forward.',
  'The new agent crashed the pilot laptops, and the notes still say "looks fine."',
  'Show the test, not a feeling.',
  'Taste the soup in a small bowl before you serve the room.')
g('Backout plan',
  'A backout plan is the path back to the last known-good state, written before you need it.',
  'The new rule blocks mail, and nobody saved the previous ruleset.',
  'Know how to undo it before you do it.',
  'Keep yesterday\'s recipe card on the counter while you try a new one.')
g('Maintenance window',
  'A maintenance window is the agreed time when interruption is allowed.',
  'A reboot starts at 10:00 on a clinic morning because the window was "whenever."',
  'Do the risky work in the hour you were given.',
  'The shop repairs the oven after the lunch rush, not during it.')
g('Standard operating procedure',
  'A standard operating procedure is the step-by-step way the organization already agreed to do a repeated job.',
  'A new hire invents a personal way to add firewall rules instead of following the written steps.',
  'Follow the agreed steps for a job you do often.',
  'Every closer follows the same lockup list, not a private habit.')
g('Allow lists and deny lists',
  'An allow list names what may run or connect. A deny list names what is blocked and misses everything unnamed.',
  'A laptop that allows only approved apps stops a random download that a deny list had never heard of.',
  'Naming what is allowed is tighter than naming what is banned.',
  'A guest list is safer than a list of people you hope stay away.')
g('Restricted activities',
  'Restricted activities are jobs the change window forbids, such as schema edits or production data copies.',
  'Someone uses the maintenance window to try a risky database rewrite that was never in the ticket.',
  'The window is not a free pass for every idea.',
  'Fixing the oven is not permission to remodel the dining room.')
g('Downtime',
  'Downtime is the period users cannot do the work, and it belongs in the ticket before it happens.',
  'The identity reboot takes forty minutes, and the desk only planned for five.',
  'Say how long the work will be stopped.',
  'Tell the diners the kitchen is dark for half an hour, not "a minute."')
g('Service restart',
  'A service restart stops and starts one background service, which can drop active sessions for that service only.',
  'Restarting the mail transfer service kicks open connections, even though the server itself stays up.',
  'Restarting one service is smaller than rebooting the whole machine, and it still interrupts that service.',
  'Relighting one burner does not shut the whole stove, but that pan stops cooking.')
g('Application restart',
  'An application restart bounces one program. Users of that program lose unsaved state. Other programs stay up.',
  'The scheduling app is restarted at lunch and three clerks lose the form they had not saved.',
  'Warn people to save before you bounce their app.',
  'Closing one cookbook does not close the whole kitchen, but that recipe is gone from the counter.')
g('Legacy applications',
  'A legacy application is an old program the business still needs, often unable to meet a new control without a workaround.',
  'The billing app only speaks an old sign-in method, so it is kept behind a jump host instead of exposed.',
  'Old apps often cannot take the new lock. Fence them instead of pretending.',
  'The old oven has no thermostat, so you do not leave it unattended.')
g('Dependencies',
  'Dependencies are the other systems a change relies on, or that rely on it.',
  'The badge system looks independent until you learn it asks the directory server for every name.',
  'Ask what else breaks if this one stops.',
  'The soup depends on the stock pot. The stock pot depends on the burner.')
g('Updating diagrams',
  'Updating diagrams means the picture of the network or the system matches what you just changed.',
  'A new guest network exists, and the wall diagram still shows one flat network.',
  'Fix the picture the same day you move the wires.',
  'The seating chart is wrong the moment you add a table and do not redraw it.')
g('Updating policies and procedures',
  'Updating policies and procedures means the written rules match the new practice, or people will follow the old page.',
  'Remote wipe is now mandatory, and the handbook still says "optional."',
  'Change the page people are told to follow.',
  'The lockup list still says the old alarm code, so the closer sets the wrong one.')
g('Version control',
  'Version control keeps each revision of a config or a script, with who changed it and a way to return to an older one.',
  'The infrastructure file is edited on a laptop with no history, and nobody can see yesterday\'s version.',
  'Keep every revision, and the name of who made it.',
  'Save the recipe under a new date instead of erasing the card.')

# --- 1.4 cryptography ---
g('Public keys',
  'A public key is the half of a key pair you may share. People use it to lock a message to you or to check your signature.',
  'The finance lead publishes a public key so payroll can be locked to that lead alone.',
  'Share this half. It locks things to you. It does not open them.',
  'The mailbox slot accepts letters. It does not hand them back out.')
g('Private keys',
  'A private key is the half you keep secret. It opens what was locked to your public key and it creates signatures.',
  'A private key file sits world-readable in a shared folder, so anyone on the host can impersonate the owner.',
  'This half stays secret. It opens and it signs.',
  'The mailbox key stays in your pocket, not taped to the slot.')
g('Key escrow',
  'Key escrow keeps a copy of a key with a trusted holder so the organization can recover data if the owner is gone.',
  'A laptop is encrypted and the only key was in the employee\'s head, so the company cannot recover the files after they leave.',
  'A trusted copy of the key, for the day the owner is gone.',
  'A spare house key at the lawyer\'s office, not under the mat.')
g('Full-disk encryption',
  'Full-disk encryption locks the whole drive, so a stolen powered-off laptop does not yield the files.',
  'A lost laptop with no disk encryption gives the finder the customer list at boot.',
  'The whole drive is locked when the power is off.',
  'Locking the entire suitcase, not one pocket.')
g('Partition encryption',
  'Partition encryption locks one slice of the disk, which fits a data volume that should stay sealed while the system volume stays separate.',
  'The data partition is encrypted and the operating-system partition is not, so the boot files are still readable.',
  'One slice of the disk is locked. The rest may not be.',
  'Locking one drawer of the desk, not the whole desk.')
g('File encryption',
  'File encryption locks individual files, which is useful for a spreadsheet that must travel or sit on a shared disk.',
  'One payroll file is locked to the finance key, and the rest of the home folder stays readable.',
  'Lock the file, not necessarily the whole disk.',
  'A sealed envelope inside an otherwise open bag.')
g('Volume encryption',
  'Volume encryption locks a logical volume, such as a mounted data disk, as one unit.',
  'The customer-data volume is encrypted, and a second scratch volume used for exports is forgotten.',
  'A whole volume, one lock.',
  'A locked trunk, while the glove box is a different decision.')
g('Database encryption',
  'Database encryption locks the database files or tablespace so a copied database file is not readable.',
  'Someone copies the database files off a backup disk and can read them because the files were stored in the clear.',
  'The database files themselves are locked.',
  'The ledger is locked, not only the office door.')
g('Record encryption',
  'Record encryption locks specific fields, such as a national ID column, while other columns stay usable.',
  'The ID column is encrypted and the name column is not, so reports still run without exposing the ID.',
  'Lock the sensitive field. Leave the rest usable if the design says so.',
  'Blacking out the account number on a form while the name stays visible.')
g('Transport encryption',
  'Transport encryption protects data while it moves, so a listener on the path cannot read it.',
  'A login page served without TLS lets the cafe network read the password.',
  'Lock the trip between two places.',
  'A sealed courier pouch, not a postcard.')
g('Asymmetric encryption',
  'Asymmetric encryption uses a key pair: one key locks or checks, the other unlocks or signs.',
  'Mail is locked to the recipient\'s public key, and only that person\'s private key opens it.',
  'Two different keys. One can be shared.',
  'A padlock anyone can snap shut, and one key that opens it.')
g('Symmetric encryption',
  'Symmetric encryption uses the same secret to lock and unlock, which is fast and depends on sharing that secret safely.',
  'A laptop disk uses one key for both directions, stored in a chip, not mailed around.',
  'One shared secret locks and unlocks.',
  'One house key that both locks and opens the same door.')
g('Key exchange',
  'Key exchange lets two parties agree on a shared secret over an open path without sending that secret itself.',
  'A browser and a site agree on a session key in the TLS handshake, then use that key for the rest of the visit.',
  'Agree on a secret without saying the secret out loud.',
  'Two people mix paint in public and end up with a color nobody else can copy.')
g('Algorithms and key length',
  'An algorithm is the method. Key length is the size of the secret. A short or retired method is a weakness even if the idea of encryption is right.',
  'A partner still offers an old export-grade cipher, and the team refuses it for a current one with a long key.',
  'The method and the size of the secret both matter.',
  'A tiny padlock on a shed is a lock, and it is still a bad lock.')
g('Trusted platform module',
  'A trusted platform module is a chip that stores keys and measurements so a disk key can be sealed to that computer.',
  'Replacing the motherboard makes the disk ask for a recovery key because the chip identity changed.',
  'A chip on the board that holds keys for this computer.',
  'A lockbox bolted to one truck, not a key left in the cup holder.')
g('Hardware security module',
  'A hardware security module is a dedicated device that creates and stores keys and can perform crypto operations without exporting the private key.',
  'The payment keys live in an HSM, so an admin who can read the app server still cannot copy the private key.',
  'A separate box whose job is to keep keys.',
  'A bank vault, not a drawer in the cashier\'s desk.')
g('Key management system',
  'A key management system creates, stores, rotates, and retires keys so people are not emailing secrets around.',
  'A team rotates the database key on a schedule and the old key is retired instead of left valid forever.',
  'A system that births, stores, and retires keys.',
  'A key cabinet with a log, not a junk drawer.')
g('Secure enclave',
  'A secure enclave is a protected area of a processor that handles secrets even if the main operating system is compromised.',
  'A phone stores the biometric match inside an enclave, so a rooted app still cannot read the template.',
  'A small locked room inside the chip.',
  'A safe inside the office, still shut if the office door is open.')
g('Steganography',
  'Steganography hides a message inside something ordinary, such as a picture, so the existence of the message is the secret.',
  'A photo posted on a chat contains a hidden payload, which encryption alone would have made obvious as ciphertext.',
  'Hiding the fact that a message exists.',
  'A note written inside a painting\'s frame, not a locked box on the table.')
g('Tokenization',
  'Tokenization replaces a sensitive value with a stand-in token that maps back only inside a protected system.',
  'The register stores a token instead of the card number, and the real number stays in the payment vault.',
  'Swap the secret for a stand-in that is useless outside the vault.',
  'A coat check ticket is not the coat.')
g('Data masking',
  'Data masking shows a fake or partial value so people can work without seeing the real secret.',
  'Support staff see only the last four digits of a national ID while the full value stays in the guarded column.',
  'Show a stand-in or a fragment, not the real secret.',
  'A redacted letter still lets you read the story around the black bars.')
g('Hashing',
  'Hashing turns data into a fixed fingerprint. You cannot rebuild the file from the fingerprint, and a tiny change makes a new fingerprint.',
  'A downloaded installer is checked with a hash so you know the bytes were not altered.',
  'A fingerprint, not a lock and not a disguise.',
  'A wax seal shows tampering. It does not hide the letter.')
g('Salting',
  'A salt is a unique extra value mixed in before a password is hashed, so identical passwords do not produce identical fingerprints.',
  'Two users pick the same password, and their stored hashes differ because each has its own salt.',
  'Add a unique extra before the fingerprint, so twins do not look identical.',
  'Two identical letters get different wax seals because each envelope has its own stamp.')
g('Digital signatures',
  'A digital signature is made with a private key so others can check, with the public key, that the content came from the holder and was not edited.',
  'A script is signed. A one-byte change makes the check fail, and the missing private key means a stranger cannot forge a new signature.',
  'Proof of who signed, and that the bytes stayed put.',
  'A notarized signature on a will. The notary does not hide the will.')
g('Key stretching',
  'Key stretching deliberately slows password hashing so guessing millions of passwords becomes expensive.',
  'The password store uses a slow hash on purpose, so a stolen database is harder to grind through.',
  'Make each guess slower, on purpose.',
  'A lock that takes a full second to try, so a thief cannot rattle it a million times a minute.')
g('Open public ledgers',
  'An open public ledger is an append-only record many parties can see, which fits shared history, not private files.',
  'A team considers a public ledger for patient notes and rejects it because the notes must stay private.',
  'A shared history everyone can read. A poor place for secrets.',
  'A town notice board, not a locked diary.')
g('Certificate authorities',
  'A certificate authority signs certificates so others can trust a name-to-key binding if they trust that authority.',
  'The company trusts a small set of authorities, and a certificate signed by a stranger is not accepted.',
  'A signer that others already trust.',
  'A notary the court already recognizes.')
g('Certificate revocation lists',
  'A certificate revocation list is a published list of certificates the authority says are no longer trusted.',
  'A stolen code-signing certificate is listed as revoked, and clients that check the list refuse it.',
  'A published list of certificates that went bad.',
  'A posted list of cancelled membership cards.')
g('Online certificate status',
  'Online certificate status is a live check that asks whether one certificate is still good, instead of downloading a whole list.',
  'The browser asks the status service about one certificate during the handshake and gets a "good" answer.',
  'Ask about this one certificate, right now.',
  'Calling the bank to ask if one card is still valid, instead of reading a phone book of cancelled cards.')
g('Self-signed certificates',
  'A self-signed certificate is signed by its own key, so nothing outside that key vouches for it.',
  'A lab site uses a self-signed certificate, and users are told not to click through the same warning on the public internet.',
  'Signed by itself. Trust it only when you already expected it.',
  'A note that says "trust me" in the writer\'s own handwriting, with no witness.')
g('Third-party certificates',
  'A third-party certificate is signed by an authority your devices already trust, which is the normal choice for a public site.',
  'The public mail site presents a certificate from a known authority, and the name matches the site.',
  'Signed by someone your devices were built to trust.',
  'A passport stamped by a government the border already recognizes.')
g('Root of trust',
  'The root of trust is the anchor you already believe, such as a root certificate in the trust store, from which other trust is chained.',
  'A new root is added to a laptop without approval, and every site that chains to it would look valid.',
  'The anchor you already believe. Adding a new one is a serious act.',
  'The one official stamp the office agreed to honor. A second stamp is a decision, not a convenience.')
g('Certificate signing requests',
  'A certificate signing request carries the public key and the name you want, and you send it to an authority to be signed. The private key stays home.',
  'An admin builds a request for mail.example.edu and sends only the request, not the private key.',
  'Ask for a signature. Do not send the private key with the request.',
  'You hand the notary a form and your public name, not the key to your house.')
g('Wildcard certificates',
  'A wildcard certificate covers many names in one level, such as every host directly under a domain, which is convenient and broader than a single name.',
  'A certificate for *.example.edu covers mail and files, and a leak of its key affects all of those names.',
  'One certificate, many names under one parent. A wider blast radius.',
  'A master key that opens every room on one floor, not just one office.')
g('Subject alternative names',
  'A subject alternative name lists extra names on one certificate, such as the bare domain and www, so one certificate can match several exact names.',
  'The certificate lists example.edu and www.example.edu, and a request for mail.example.edu still fails because that name is absent.',
  'The extra names printed on the certificate. If your name is not listed, it does not match.',
  'A guest list with two spellings of the host. A third spelling is still not invited.')

# --- 2.1 actors ---
g('Nation-state actors',
  'A nation-state actor works for a government, with time, money, and patience aimed at espionage or disruption.',
  'A quiet multi-month intrusion steals research, with custom tools and no ransom note.',
  'A government-backed intruder with patience and a budget.',
  'A foreign ministry, not a kid in a parking lot.')
g('Unskilled attackers',
  'An unskilled attacker uses tools and instructions written by someone else, and often makes noise.',
  'A reused kit scans the whole internet for one known bug and trips every alarm.',
  'Someone running another person\'s kit.',
  'A person using a copied recipe who burns the first pan.')
g('Hacktivists',
  'A hacktivist is driven by a cause, and often wants the attack seen.',
  'A site is defaced with a slogan after the organization takes a public position.',
  'A cause, and they often want an audience.',
  'A protester with a paint can, not a burglar who wants to stay unseen.')
g('Insider threats',
  'An insider already has some access. The motive may be money, a grudge, or a careless shortcut.',
  'An employee copies a customer list to a personal drive the week before resigning.',
  'Someone who already has a key.',
  'A cashier who knows the safe, not a stranger at the window.')
g('Organized crime',
  'Organized crime treats intrusion as a business, usually for money: theft, fraud, or extortion.',
  'A crew sells access to a compromised mail account and follows with a payment fraud.',
  'A business whose product is crime.',
  'A theft ring, not a one-time prank.')
g('Shadow IT',
  'Shadow IT is a system the business uses that the security and IT teams did not approve or even know about.',
  'A team stores customer files in a personal cloud drive because the official share felt slow.',
  'A tool the company uses that nobody official approved.',
  'A second cash box under the counter that the accountant has never seen.')
g('Internal versus external actors',
  'Internal actors start from inside the trust boundary. External actors must first get in.',
  'The same stolen file looks different if the copy was made by a logged-in employee rather than a stranger on the internet.',
  'Did they start inside, or did they have to break in?',
  'A housemate versus a stranger on the porch.')
g('Resources and funding',
  'Resources and funding describe how much time, money, and infrastructure an actor can spend.',
  'A months-long quiet intrusion with custom infrastructure points at funding a hobby kit does not have.',
  'How much can they spend?',
  'A tourist with a pocket map versus a crew with a truck.')
g('Sophistication and capability',
  'Sophistication is how advanced the tools and the tradecraft are, which is separate from how angry the actor is.',
  'A novel technique that avoids every known signature is a capability clue, not a motive clue.',
  'How skilled is the method?',
  'A locksmith versus someone rattling the handle.')
g('Data theft as a motive',
  'Data theft means the goal is to take information and keep or sell it.',
  'A database is copied out and no ransom note appears.',
  'They want the information itself.',
  'A pickpocket wants the wallet, not a speech.')
g('Espionage',
  'Espionage seeks secrets for a strategic advantage, often quietly and over a long time.',
  'Research files leave in small pieces for months, with no bragging and no ransom.',
  'Quiet theft of secrets for a long game.',
  'Someone who photographs the blueprints and leaves the safe looking shut.')
g('Service disruption',
  'Service disruption aims to stop the work, whether or not data is stolen.',
  'A flood of traffic knocks the booking site offline on the busiest morning.',
  'The goal is to stop the service.',
  'Someone pulls the fire alarm to empty the store.')
g('Blackmail',
  'Blackmail threatens to reveal or destroy something unless the victim pays or complies.',
  'A note threatens to publish stolen mail unless a payment arrives by Friday.',
  'Pay, or we expose you.',
  'A stranger who says they will tell the town unless you hand over cash.')
g('Financial gain',
  'Financial gain is the motive when the attacker wants money, directly or by selling what they took.',
  'Fraudulent invoices go out from a compromised mailbox the same day.',
  'They want money.',
  'A till thief, not a speechmaker.')
g('Political or philosophical motives',
  'A political or philosophical motive aims at a cause, a government, or a belief, more than at a payday.',
  'Systems tied to a public policy decision are targeted the week the decision is announced.',
  'A belief is the fuel.',
  'Someone who paints a slogan, not someone who empties the register.')
g('Ethical disclosure motives',
  'An ethical motive seeks a fix, not harm: the finder reports the flaw through an agreed channel.',
  'A researcher reports a bug to the security mailbox and waits before saying anything public.',
  'They want the hole closed, and they use the front door.',
  'A neighbor who tells you the back window is unlocked, instead of climbing in.')
g('Revenge',
  'Revenge is personal. The target is often a former employer, a coworker, or a partner.',
  'A fired administrator deletes backups the night the access should have been removed.',
  'A grudge, aimed at people they know.',
  'A former roommate who scratches the door on the way out.')
g('Chaos and war',
  'Chaos and war motives seek damage, fear, or advantage in a conflict, not a tidy ransom.',
  'Systems that run a public utility are disrupted with no demand and no theft.',
  'The point is damage or conflict.',
  'Smashing the windows with no interest in the cash drawer.')

# --- 2.2 paths ---
g('Email as an attack path',
  'Email carries links and attachments into the inbox people already trust.',
  'A message that looks like payroll asks the user to sign in on a page the company does not own.',
  'The inbox is a door.',
  'A letter on the mat that asks you to mail your house key.')
g('Text messages as an attack path',
  'Text messages are short, urgent, and easy to spoof, which makes them a favorite path for links.',
  'A text says the package is held and the link is not the carrier\'s real site.',
  'A short text can be a trap.',
  'A note slipped under the door that says "call this number now."')
g('Instant messages as an attack path',
  'Chat messages arrive from accounts that can be taken over, and people reply faster than they do to mail.',
  'A coworker\'s chat account asks for the VPN code five minutes after that coworker\'s phone was stolen.',
  'Chat feels friendly, which is why it works.',
  'A familiar voice at the back door asking you to toss the keys.')
g('Image-based attacks',
  'Some attacks hide in an image file that a viewer or a browser mishandles.',
  'A picture attached to a ticket is not opened on the admin workstation until it is checked.',
  'A picture can carry more than a picture.',
  'A poster with a razor behind the paper.')
g('File-based attacks',
  'File-based attacks ride in documents and archives people are used to opening.',
  'A spreadsheet from a partner macro-enables itself and runs a payload.',
  'The file is the bait.',
  'A recipe card that also tells you to unlock the back door.')
g('Voice-call attacks',
  'A voice call lets the attacker sound urgent and senior, which pushes people to skip the callback.',
  'A caller claims to be the new finance lead and demands a password read aloud.',
  'A phone voice is not proof of identity.',
  'Someone at the door who says they are the landlord and wants the spare key.')
g('Removable media',
  'Removable media such as a found USB drive can run or plant code the moment it is mounted on a work computer.',
  'A stick labeled "salaries" in the parking lot is turned in, not plugged into a workstation.',
  'Do not mount a found drive on a work computer.',
  'A pie left on the step. You do not feed it to the family before you know who baked it.')
g('Vulnerable client software',
  'Client software on the user\'s machine, such as a browser or a reader, is an attack path when it is unpatched.',
  'An old reader opens a booby-trapped file that a current reader would have refused.',
  'The program on the desk can be the hole.',
  'A rusty latch on the window the family actually uses.')
g('Agentless exposure',
  'Agentless management reaches a host without a permanent agent, which is useful and also a path if the remote interface is weak.',
  'A management port left open so scanners can reach it is also open to everyone else on that network.',
  'A door with no guard posted, just because you did not install an agent.',
  'A shed with no lock, visited by whoever walks by, not only the owner.')
g('Unsupported systems',
  'An unsupported system no longer receives fixes, so every new flaw stays open.',
  'A server the vendor stopped patching last year still faces the internal network.',
  'No more fixes means the hole stays.',
  'A roof the builder will not repair. Every storm gets in.')
g('Wireless networks',
  'Wireless networks can be joined from the parking lot, so a weak passphrase or an open guest path matters.',
  'The old guest network has no isolation, and a phone in the lot reaches a printer admin page.',
  'People can join from outside the walls.',
  'A conversation shouted across the yard.')
g('Wired networks',
  'A wired port in a lobby or a conference room is an attack path if it lands on an inside network.',
  'A visitor plugs into a wall port and receives an address on the staff network.',
  'A cable can be as open as a radio if the port is lazy.',
  'An unlocked side door on the alley.')
g('Bluetooth',
  'Bluetooth is a short-range radio. Left discoverable, it lets nearby devices pair or probe.',
  'A conference-room laptop is discoverable all day, and a phone in the next chair can attempt a pair.',
  'Short-range radio is still radio.',
  'A baby monitor someone in the hallway can hear.')
g('Open service ports',
  'An open service port is a listening door. If the service is buggy or forgotten, the port is the path.',
  'A forgotten database port answers on the server\'s public address.',
  'If it listens, someone can knock.',
  'A window left open on the ground floor.')
g('Default credentials',
  'Default credentials are the username and password the vendor shipped. They are published, so they are not a secret.',
  'A new camera still signs in with admin and the printed password.',
  'The password on the sticker is not a password.',
  'A lock that still uses the combination printed on the box.')
g('Managed service providers in the supply chain',
  'A managed service provider with admin rights in your network is a high-value path, because one breach there reaches many customers.',
  'The outsourced desktop team uses one shared remote tool, and a breach of that tool lands inside the clinic.',
  'Your helper\'s keys are your keys, if they get stolen.',
  'The building superintendent has a master key. If their ring is stolen, every office is open.')
g('Vendors in the supply chain',
  'A vendor who ships software, devices, or updates can push a problem into your environment on purpose or by accident.',
  'A badge-printer update arrives from the vendor and the team checks the signature before installing it.',
  'The company you buy from can carry trouble in with the delivery.',
  'A baker who delivers bread can also, by mistake, deliver a spoiled batch.')
g('Suppliers in the supply chain',
  'A supplier upstream of your vendor can tamper with parts or code before your vendor even sees them.',
  'A library inside a product was altered at the supplier, and the vendor shipped it in good faith.',
  'Trouble can start further up the chain than the company you pay.',
  'The flour mill, not the corner bakery, is where the bad batch began.')
g('Phishing',
  'Phishing is a message that pretends to be trusted so you will click, open, or type a secret.',
  'The display name says Payroll and the link host is not the company.',
  'A fake message that wants a click or a secret.',
  'A letter that looks like the bank and asks for the PIN.')
g('Vishing',
  'Vishing is phishing by voice.',
  'A caller says they are the help desk and asks for the multi-factor code that just appeared.',
  'The phone version of a fake letter.',
  'A voice on the line that sounds like the bank and is not.')
g('Smishing',
  'Smishing is phishing by text message.',
  'A text about a held package uses a link that is one letter off the real carrier.',
  'The text-message version of a fake letter.',
  'A postcard-sized lie on your phone.')
g('Misinformation and disinformation',
  'Misinformation is false content spread without a careful lie behind it. Disinformation is a deliberate lie. Both steer people into bad decisions.',
  'A forged memo tells staff the password rules changed and to send their old password to a new address.',
  'False news that makes people act.',
  'A rumor on the bulletin board that the doors will be unlocked tonight.')
g('Impersonation',
  'Impersonation is pretending to be a specific person or role so the target skips verification.',
  'Someone at the lobby says they are the new auditor and asks to be let into the server room.',
  'They pretend to be someone you would obey.',
  'A stranger in a courier vest who wants the back room.')
g('Business email compromise',
  'Business email compromise abuses a real or lookalike mailbox to redirect money or data.',
  'A thread with the finance lead is continued from a lookalike address asking for a new bank account.',
  'A money request that rides a trusted conversation.',
  'A note in the boss\'s handwriting that says "pay this new account," written by someone else.')
g('Pretexting',
  'Pretexting builds a made-up story so the target will volunteer a secret or skip a step.',
  'A caller invents a failed audit and asks the desk to read a password to "fix the record."',
  'A story built to make you help.',
  'A person who claims the delivery was already paid, and asks you to open the gate.')
g('Watering-hole attacks',
  'A watering-hole attack compromises a site the target group already visits, instead of emailing them.',
  'The industry association page the nurses check each morning starts serving a malicious download.',
  'Poison the place they already go.',
  'Spiking the coffee urn in the break room instead of mailing each person a cup.')
g('Brand impersonation',
  'Brand impersonation copies a known logo, tone, and name so the fake feels official.',
  'A login page copies the company colors and still uses a domain the company does not own.',
  'Looks like the brand. Check the real name.',
  'A fake storefront with the real shop\'s sign hung over a different door.')
g('Typosquatting',
  'Typosquatting registers a name that is one character off a real one, hoping for a mistype or a quick glance.',
  'example.com is real and exarnple.com is the trap.',
  'A name that is almost right.',
  'A street sign with one letter changed, pointing at the wrong house.')

# --- 2.3 vulnerabilities ---
g('Memory injection',
  'Memory injection puts attacker code into a running process so the process does the attacker\'s work.',
  'A legitimate helper process starts making network calls the vendor never wrote.',
  'Code sneaks into a program that is already running.',
  'Someone slips a new card into a deck the dealer is already holding.')
g('Buffer overflows',
  'A buffer overflow writes past the end of a reserved space and can change what the program does next.',
  'A too-long name field crashes a service and, in the worst case, redirects it.',
  'Too much data spills out of the box it was given.',
  'Pouring a gallon into a pint glass so the spill hits the switch beside it.')
g('Race conditions',
  'A race condition, including time-of-check to time-of-use, acts on a fact that changes between the check and the action.',
  'A file is checked as safe, then swapped for another file before the program opens it.',
  'The world changes between the look and the leap.',
  'You check the stove is off, and someone turns it on before you leave.')
g('Malicious updates',
  'A malicious update is a fix channel that delivers harm because the update itself was altered or the source was wrong.',
  'An update arrives from a lookalike server, and the team rejects it because the signature does not match.',
  'The patch can be the poison if you do not check who signed it.',
  'A "repair" person who replaces a good lock with their own.')
g('Operating-system vulnerabilities',
  'An operating-system vulnerability is a flaw in the platform itself, so every app on that host inherits the risk until it is patched or isolated.',
  'A kernel bug lets a local user become administrator, and the patch is waiting in the change window.',
  'A hole in the floor, not in one piece of furniture.',
  'A crack in the foundation, under every room.')
g('SQL injection',
  'SQL injection happens when user input is glued into a database query and the database treats it as commands.',
  'A search box accepts a quote and a phrase that dumps the user table.',
  'The database obeyed the visitor, not just the search.',
  'A diner who writes "and also bring the cash drawer" on the order slip, and the kitchen obeys.')
g('Cross-site scripting',
  'Cross-site scripting lets an attacker run script in another user\'s browser by planting it in a page the user trusts.',
  'A comment field stores a script that steals the next reader\'s session.',
  'The page runs the attacker\'s script in the victim\'s browser.',
  'A note on the bulletin board that the reader\'s own hands obey.')
g('Firmware weaknesses',
  'Firmware is the code in a device that sits under the operating system. A flaw there survives a normal reinstall.',
  'A network camera has a firmware bug, and reinstalling nothing on the server fixes it. The camera needs its own update.',
  'The code under the operating system.',
  'A bad lock built into the door, not a bad sign hung on it.')
g('End-of-life hardware',
  'End-of-life hardware is no longer sold or fixed by the maker, so new flaws stay open.',
  'A badge controller the vendor ended still sits on the office network.',
  'The maker walked away. The risk did not.',
  'An appliance the company no longer repairs, still plugged in.')
g('Legacy hardware',
  'Legacy hardware is old equipment the business still needs, often unable to speak modern authentication or encryption.',
  'A lab instrument only supports an old wireless protection mode, so it is fenced onto its own segment.',
  'Old gear that cannot take a modern lock needs a fence.',
  'A truck with no seatbelts. You do not send it on the highway. You keep it in the yard.')
g('Virtual machine escape',
  'Virtual machine escape breaks out of a guest into the host or another guest, which defeats the isolation you thought you had.',
  'A bug in the hypervisor would let a test guest read the host\'s disks, so the test guests stay patched and untrusted.',
  'The guest climbs out of its room.',
  'A hotel guest who gets from their room into the manager\'s office through a shared vent.')
g('Virtual machine sprawl',
  'Virtual machine sprawl is a pile of forgotten guests that still run, still hold data, and still miss patches.',
  'A demo server from last year is still online with a default password.',
  'Forgotten machines are still machines.',
  'Spare keys cut for a party and never collected.')
g('Cloud-specific weaknesses',
  'Cloud-specific weaknesses include open storage, overly broad roles, and metadata services that hand out credentials if you can reach them.',
  'A storage bucket is world-readable, which would never have been a "share" on the old file server.',
  'The cloud adds its own ways to leave the door open.',
  'A storage unit with the roll-up door left up on a public alley.')
g('Service-provider supply chain',
  'A service-provider flaw is a weakness in a company that runs something for you, such as mail or identity.',
  'The hosted mail provider is breached, and every mailbox that lived there is in scope.',
  'When the helper is hit, you are hit.',
  'The laundry service loses the uniforms. Your closet did not have to be picked.')
g('Hardware-provider supply chain',
  'A hardware-provider weakness is a tampered or flawed device before it ever reaches your rack.',
  'A batch of badges arrives and the team checks serials against the order before issuing them.',
  'The box can be wrong before you unbox it.',
  'A lock purchased already keyed to a stranger.')
g('Software-provider supply chain',
  'A software-provider weakness is a library, build system, or update channel that ships someone else\'s code under a trusted name.',
  'A tiny helper library used by the billing app is altered, and every install of the app inherits it.',
  'Trusted software can carry a stranger\'s change.',
  'A spice jar refilled by someone who is not the brand on the label.')
g('Cryptographic weaknesses',
  'A cryptographic weakness is a broken or retired method, a short key, or a secret that was reused or leaked.',
  'A partner offers a retired hash for signatures, and the team refuses.',
  'The math or the secret is no longer strong.',
  'A padlock everyone already knows how to shim.')
g('Misconfiguration',
  'Misconfiguration is a system that works as designed and is still unsafe because the settings are wrong.',
  'A database allows any host to connect because the allow rule says any.',
  'Nothing is "broken." The settings are wrong.',
  'A door that locks perfectly, installed backward.')
g('Mobile-device weaknesses',
  'Mobile weaknesses include lost devices, sideloaded apps, weak screen locks, and phones that leave the building every night.',
  'A phone with no screen lock and company mail is left in a taxi.',
  'A computer that lives in a pocket.',
  'A wallet that also opens the office.')
g('Zero-day vulnerabilities',
  'A zero-day is a flaw the vendor has not patched yet, so signature-only defenses can miss it and other controls have to carry the load.',
  'A new bug has no patch on Tuesday, so the team isolates the exposed service until the fix exists.',
  'No patch yet. Reduce how far it can reach.',
  'A leak nobody has a patch for. You put a bucket under it and close the room.')

# --- 2.4 malicious activity ---
g('Ransomware',
  'Ransomware locks data or systems and demands payment for a key that may never come.',
  'File names turn into junk and a note demands payment by Monday.',
  'They lock your files and ask for money.',
  'Someone changes the locks on your house and mails you a ransom for the new key.')
g('Trojans',
  'A trojan looks useful or harmless and also does something harmful.',
  'A "invoice viewer" also installs a remote control tool.',
  'It looks helpful and it is not.',
  'A free sample that also picks the pocket.')
g('Worms',
  'A worm spreads on its own, without a person opening a file.',
  'One vulnerable server infects the next across the same segment overnight.',
  'It travels by itself.',
  'A rumor that walks from room to room with nobody carrying a letter.')
g('Spyware',
  'Spyware hides and collects information: keystrokes, screens, or files.',
  'A browser add-on the user does not remember installing sends browsing history out.',
  'It watches and sends what it sees.',
  'A hidden camera in the lobby clock.')
g('Bloatware',
  'Bloatware is extra software that ships on a device, eating resources and adding a surface you did not ask for.',
  'A new laptop comes with three toolbars and a game the image should have removed.',
  'Extra programs you did not want, still able to cause trouble.',
  'Free gadgets taped to a new appliance, each with its own plug.')
g('Viruses',
  'A virus attaches to a host file and runs when that host runs, then tries to attach to more files.',
  'A shared template starts infecting other documents on the file share when people open it.',
  'It rides inside another file.',
  'A cold that spreads when people share the same pen.')
g('Keyloggers',
  'A keylogger records what is typed, including passwords.',
  'A workstation starts sending out bursts every time someone types into a login form.',
  'It records the keys.',
  'Someone writing down every number you punch into the alarm.')
g('Logic bombs',
  'A logic bomb waits for a date, an event, or a person\'s departure, then does harm.',
  'A script in a finance folder is set to delete shares if one employee\'s account is disabled.',
  'It waits, then it acts.',
  'A timer on the oven set by someone who already left the building.')
g('Rootkits',
  'A rootkit hides deep, often from the tools you would use to find it, so the view you see is a lie.',
  'Task lists look normal while a hidden process still calls out.',
  'It hides from the tools that should show it.',
  'A false wall. The room looks empty because the wall is the trick.')
g('Physical brute force',
  'Physical brute force breaks in by force: a kicked door, a smashed lock, a rammed gate.',
  'The rear door frame is splintered and the alarm sensor was ripped off.',
  'They break the thing instead of tricking it.',
  'A shoulder against the door, not a copied key.')
g('RFID cloning',
  'RFID cloning copies a badge or a tag so a second token acts like the real one.',
  'A visitor stands close to an employee badge and later the same badge number appears at two doors at once.',
  'A copied badge.',
  'A photocopy of a keycard that the door cannot tell from the original.')
g('Environmental attacks',
  'Environmental attacks use heat, cold, water, or power to damage systems or force a bad decision.',
  'A portable heater is left aimed at a closet sensor so the room overheats and gear shuts down.',
  'They attack the room, not the password.',
  'Flooding the basement to kill the files, instead of stealing them.')
g('Distributed denial of service',
  'A distributed denial of service uses many sources to flood a service until real users cannot get through. Some floods amplify or reflect off other servers.',
  'The booking site dies under traffic from thousands of addresses, while the servers themselves look healthy.',
  'A crowd blocks the door so real customers cannot enter.',
  'A fake line around the block that never buys anything.')
g('DNS attacks',
  'DNS attacks corrupt or redirect name lookups so people reach the attacker while typing a name they trust.',
  'Staff asking for the payroll site are sent to a lookalike address because a resolver was poisoned.',
  'The phone book lies.',
  'A swapped street sign that sends visitors to the wrong house.')
g('Wireless attacks',
  'Wireless attacks include rogue access points, evil twins, and cracking a weak passphrase from nearby.',
  'A second network appears with the clinic\'s name, and a laptop joins it from the lobby.',
  'A fake or weak radio.',
  'A person in the parking lot holding a sign that copies the shop\'s name.')
g('On-path attacks',
  'An on-path attack sits between two parties and reads or alters the traffic.',
  'On an open cafe network, a tool relays a login that was not protected by TLS.',
  'Someone stands in the middle of the conversation.',
  'A courier who opens the envelope, reads it, and reseals it.')
g('Credential replay',
  'Credential replay reuses a captured login or token so the attacker does not need the password again.',
  'A stolen session cookie is reused from another computer after the user already signed in.',
  'They reuse a captured "I already proved it."',
  'A used concert wristband that still scans.')
g('Malicious code on the network',
  'Malicious code on the network is a payload moving between hosts, not only sitting in a mailbox.',
  'A worm copy is pulled from one workstation to another over a file share.',
  'The bad program is traveling the wires.',
  'A spoiled dish passed from table to table, not mailed from outside.')
g('Injection attacks',
  'Injection attacks feed commands into a program through a field that should have been data.',
  'A form field includes instructions the server executes.',
  'Data becomes orders.',
  'An order slip that also says "open the safe."')
g('Application buffer overflows',
  'An application buffer overflow is the same spill, inside one app, often reached through a field or a file that app parses.',
  'A crafted image crashes the viewer and is being checked as more than a crash.',
  'One app spills past its buffer.',
  'One glass on the table overflows onto the remote beside it.')
g('Application replay',
  'Application replay resends a valid request, such as a payment, so the action happens twice.',
  'A captured "transfer" request is sent again and a second payment leaves.',
  'They repeat a real request.',
  'Cashing the same check twice.')
g('Privilege escalation',
  'Privilege escalation turns a small foothold into a bigger right, such as from a user to an administrator.',
  'A help-desk account that can reset passwords is used to take over a domain admin.',
  'A small key is traded up for a bigger one.',
  'A lobby badge that somehow opens the vault.')
g('Request forgery',
  'Request forgery tricks a browser or a server into sending a request the user or the server did not intend.',
  'A logged-in admin visits a malicious page that submits a password reset on their behalf.',
  'The browser is tricked into asking.',
  'A form the clerk signs because it was slipped under a real form.')
g('Directory traversal',
  'Directory traversal uses path tricks such as ".." to read files outside the folder the app should serve.',
  'A download link with extra ".." segments returns a configuration file.',
  'They climb out of the folder you meant to share.',
  'A hotel guest who takes the stairs into the staff hallway.')
g('Downgrade attacks',
  'A downgrade attack pushes a connection onto an older, weaker method the attacker can break.',
  'A client is coaxed into an old version of TLS that the server should have refused.',
  'They force the old, weak handshake.',
  'Talking someone into using the rusty padlock instead of the new one.')
g('Hash collisions',
  'A hash collision is two different inputs with the same fingerprint, which can undermine a check that trusts the fingerprint alone.',
  'A weak hash lets a swapped file keep the fingerprint the change ticket recorded.',
  'Two different files, one fingerprint. The check is lying if the method is weak.',
  'Two different letters that leave the same wax mark.')
g('Birthday attacks',
  'A birthday attack uses the math of shared birthdays: collisions show up sooner than people expect, which is why short fingerprints are risky.',
  'A short hash used for file identity is rejected because collisions are too cheap to find.',
  'Matches happen sooner than a coin-flip story suggests.',
  'In a small room, two people share a birthday sooner than you would bet.')
g('Password spraying',
  'Password spraying tries a few common passwords against many accounts, staying under the lockout on each one.',
  'Dozens of accounts show one failure each, all with the same common password, in the same hour.',
  'One guess, many doors, so no single door slams shut.',
  'Trying the same cheap key in every mailbox on the street, once.')
g('Password brute force',
  'Password brute force tries many guesses against one account until it hits or the lockout trips.',
  'One account shows thousands of failures from one address in a minute.',
  'Many guesses, one door.',
  'Rattling one lock for an hour.')
g('Account lockout indicators',
  'A burst of lockouts can mean guessing, a broken app, or a user who forgot a password. The pattern tells you which.',
  'Twenty accounts lock in five minutes, which is not a single forgetful user.',
  'Lots of locks at once is a signal, not a coincidence.',
  'Every locker in the row slamming shut together.')
g('Concurrent sessions',
  'Concurrent sessions mean the same account is signed in from two places at once, which may be impossible travel or a shared password.',
  'One nurse is signed in at the clinic and from another country at the same minute.',
  'Two places at once.',
  'The same coat checked at two doors at the same time.')
g('Blocked content',
  'Blocked content is a filter doing its job. A sudden spike can mean a campaign, not a single misclick.',
  'The web filter blocks the same new domain for half the staff in an hour.',
  'The filter is catching something. Ask whether it is one person or a wave.',
  'The metal detector beeping for every third person in line.')
g('Impossible travel',
  'Impossible travel is a sign-in pattern no person could physically do in the time between the two events.',
  'A login in one city and another login an hour later on another continent.',
  'Nobody travels that fast.',
  'A punch clock that shows you in two buildings an hour apart, oceans away.')
g('Resource consumption',
  'Resource consumption is a sudden hunger for CPU, disk, or bandwidth that can mean mining, encryption, or a flood.',
  'A file server\'s disks hit full and the CPU stays pegged while files are being rewritten.',
  'The machine is suddenly working too hard.',
  'The oven running at full blast with nothing in it.')
g('Resource inaccessibility',
  'Resource inaccessibility means a system people need is gone: locked, deleted, or too slow to use.',
  'The file share opens and every folder the morning shift needs is encrypted junk.',
  'The thing they need is gone or unusable.',
  'The pantry door opens onto empty shelves.')
g('Out-of-cycle logging',
  'Out-of-cycle logging is a burst of logs, or a logging change, at a time the baseline says should be quiet.',
  'The security log triples in size at 03:00, when the office is empty.',
  'The log is noisy when the building should be quiet.',
  'The sign-out sheet filling up in the middle of the night.')
g('Published attacker claims',
  'Published claims are posts, leak sites, or bragging that name your organization. Treat them as a lead, then verify.',
  'A leak site lists the clinic. The team checks whether the sample files are real before they panic or ignore it.',
  'A public boast is a tip, not proof, until you match it to your data.',
  'A rumor on the town board. You still check the till.')
g('Missing logs',
  'Missing logs are a finding. Attackers and broken collectors both create gaps. A gap is not "nothing happened."',
  'The authentication log has a two-hour hole on the night of the incident.',
  'A gap in the record is itself a clue.',
  'A page torn out of the sign-out book.')

# --- 2.5 mitigations ---
g('Segmentation',
  'Segmentation splits a network so a problem in one part does not freely walk into another.',
  'Guest wifi cannot open a session to the payroll servers.',
  'Separate the rooms so a fire stays in one.',
  'A fire door between the kitchen and the dining room.')
g('Access control lists',
  'An access control list is an ordered set of allow and deny rules. The first match usually wins.',
  'A list allows TCP 443 and then denies the rest, so a guest on port 22 is denied.',
  'A written list of what may pass, read from the top.',
  'A bouncer with a clipboard. The first line that matches is the answer.')
g('Permissions',
  'Permissions say which accounts can read, change, or run a file or an object.',
  'A payroll file is mode 640, group payroll, and nobody else can read it.',
  'Who may touch this thing.',
  'A diary the household can see and only the owner can rewrite.')
g('Application allow lists',
  'An application allow list runs only named programs and refuses everything else.',
  'A clinic PC refuses a downloaded viewer because that viewer is not on the list.',
  'Only named programs may run.',
  'A kitchen that cooks only from the approved menu.')
g('Isolation',
  'Isolation keeps a risky system able to do its job and unable to reach everything else.',
  'A lab instrument that cannot be patched is placed on a segment with no path to the internet or to file shares.',
  'Let it work. Do not let it wander.',
  'A sick pet in a separate room, still fed, not loose in the house.')
g('Patching',
  'Patching applies the vendor\'s fix so a known hole closes.',
  'A browser update lands in the weekly window and the known bug is gone on the pilot group first.',
  'Put the fix on, after you know what it changes.',
  'Replacing a cracked pane instead of taping it forever.')
g('Encryption as a mitigation',
  'Encryption as a mitigation means stolen copies are unreadable if the keys stayed safe.',
  'A stolen backup tape is useless because the backup was encrypted and the key was not on the tape.',
  'If they take the files, they still cannot read them.',
  'A stolen suitcase that is locked, with the key still in your pocket.')
g('Monitoring',
  'Monitoring watches logs and signals so a bad event is seen while there is still time to act.',
  'A spike in failed logins pages the on-call person in minutes, not at next month\'s review.',
  'Watch, so you can act.',
  'A smoke alarm you actually hear.')
g('Least privilege',
  'Least privilege gives each account only the rights the job needs, and no standing admin "just in case."',
  'The front desk can reset passwords for the reception role and cannot touch domain admin.',
  'Only the rights the job needs.',
  'A waiter\'s key opens the dining room, not the office safe.')
g('Configuration enforcement',
  'Configuration enforcement puts the approved settings back when drift appears.',
  'A laptop that someone set to allow any inbound traffic is returned to the baseline overnight.',
  'The approved settings win, again and again.',
  'The shop resets the thermostat to the posted number every morning.')
g('Decommissioning',
  'Decommissioning retires a system on purpose: access removed, data handled, and the box no longer forgotten online.',
  'A demo server is powered off, its accounts are removed, and the diagram drops it the same week.',
  'Turn it off on purpose, and remove its keys.',
  'Closing a shop: the sign comes down and the keys are collected.')
g('Endpoint protection',
  'Endpoint protection watches the host for malware and suspicious behavior, and it is not a reason to skip patches.',
  'The agent quarantines a trojan the user downloaded, and the ticket still asks how it got there.',
  'Software on the computer that watches for bad programs.',
  'A smoke detector in the room. It is not a lock on the door.')
g('Host firewalls',
  'A host firewall filters traffic on the computer itself, which still matters behind a network firewall.',
  'A laptop denies inbound connections except a management port from one admin subnet.',
  'The computer has its own door policy.',
  'A lock on the bedroom door, even though the building has a lobby.')
g('Host intrusion prevention',
  'Host intrusion prevention blocks suspicious behavior on the machine, not only known file signatures.',
  'A process that starts injecting into another process is stopped by the host prevention agent.',
  'It blocks bad behavior on the box.',
  'A guard who stops a fight, not only a camera that records it.')
g('Disabling unused ports and protocols',
  'Disabling unused ports and protocols removes listeners and old protocols you do not need.',
  'A server that only serves HTTPS has file-sharing and old remote protocols turned off.',
  'If you do not use it, do not leave it listening.',
  'Boarding the windows you never open.')
g('Changing default passwords',
  'Changing default passwords replaces the published vendor secret before the device joins the real network.',
  'A new switch is not cabled in until the admin password is changed and stored in the vault.',
  'Change the sticker password first.',
  'You rekey the lock before you move in, not after the first party.')
g('Removing unnecessary software',
  'Removing unnecessary software shrinks the number of programs that can be buggy or abused.',
  'The standard image drops games, old runtimes, and trial tools before a laptop is handed out.',
  'Fewer programs, fewer holes.',
  'Clearing the counter so only the tools you use are within reach.')

# --- 3.1 architecture ---
g('Cloud responsibility split',
  'The responsibility split says which security jobs stay with you and which the cloud provider handles. The split changes with the service model.',
  'In a rented virtual machine you still patch the guest operating system. In a finished app the provider patches the platform.',
  'Know which locks are yours.',
  'In a rented apartment you still lock your door. The landlord owns the roof.')
g('Hybrid cloud',
  'A hybrid cloud keeps some systems on your floor and some in a provider, and the path between them is part of the design.',
  'The identity server stays in the clinic and the mail servers live at a provider, joined by a private path.',
  'Some of it is here, some of it is there, and the road between them matters.',
  'A shop with a back room you own and a warehouse you rent across town.')
g('Third-party cloud vendors',
  'A third-party cloud vendor runs the platform. You still configure your part, and you still need a contract and an exit plan.',
  'The team reads which logs the vendor will actually hand over before they move the records.',
  'They run the building. You still choose the locks on your suite.',
  'A hotel. You do not own the elevators, and you still watch your room.')
g('Infrastructure as code',
  'Infrastructure as code describes servers and networks in files that can be reviewed, repeated, and rolled back.',
  'A firewall change is a reviewed file, not a click someone made at midnight and forgot.',
  'The setup lives in a file you can read and undo.',
  'A recipe card instead of a cook who only remembers.')
g('Serverless computing',
  'Serverless runs small functions without a server you patch. You still own the code, the permissions, and the data the function can reach.',
  'A function is given a role that can read every bucket, which is wider than the one job it does.',
  'You do not patch the server. You still own the code and the rights.',
  'A pop-up kitchen. You do not own the stove, and you still choose what goes in the pot.')
g('Microservices',
  'Microservices split an application into small services that talk to each other, which multiplies the number of doors to lock.',
  'Each small service has its own identity, and a shared admin token between all of them is rejected.',
  'Many small doors, each with its own key.',
  'A food hall of stalls. Each stall locks its own till.')
g('Air-gapped networks',
  'An air gap has no network path to other networks. Data moves only by a controlled physical transfer.',
  'The safety system has no cable to the office network, and updates arrive on a checked drive.',
  'No wire. No radio. A deliberate carry is the only path.',
  'A room with no phone line. Messages arrive on paper, by hand.')
g('Logical segmentation',
  'Logical segmentation separates traffic with tags, rules, or virtual networks even when the cables share a building.',
  'Staff and guests share a switch and do not share a broadcast domain or a route.',
  'Separate by rules, even on the same gear.',
  'One building, two locked hallways.')
g('Software-defined networking',
  'Software-defined networking sets paths and policy in software so a change can be reviewed and repeated.',
  'A new segment is described in the controller and pushed, instead of typed differently on each switch.',
  'The map lives in software you can review.',
  'Changing the seating from a plan, not by dragging chairs at random.')
g('On-premises infrastructure',
  'On-premises infrastructure is gear you house and usually patch, power, and physically protect yourself.',
  'The file server in the closet is yours to patch, cool, and badge-protect.',
  'If it sits in your closet, the locks are yours.',
  'A stove you own. You buy the gas and you change the fuse.')
g('Centralized versus decentralized design',
  'Centralized design puts a function in one place, which is easier to control and easier to take down. Decentralized design spreads it, which survives a single loss and is harder to govern.',
  'One identity server is simple to audit and is also a single outage for every login.',
  'One place is easier to watch and easier to lose. Many places survive and are harder to govern.',
  'One cash office versus a till in every stall.')
g('Containerization',
  'A container packages an app and its libraries. It is not a full virtual machine, and a weak host or a broad mount can undo the separation.',
  'A container is not given the host\'s docker socket, because that socket is a path to the host.',
  'A packed app. Not a magic wall.',
  'A lunch box. It is not a locked room.')
g('Virtualization',
  'Virtualization runs guests on a host. The host and the hypervisor become high-value, because they sit under every guest.',
  'The hypervisor is patched on a stricter schedule than any single guest.',
  'The floor under all the rooms matters most.',
  'The hotel foundation. A crack there reaches every suite.')
g('Internet of things',
  'Internet-of-things devices are small networked things, often with weak defaults and rare updates.',
  'A smart thermostat ships with a published password and is not joined to the office network until that changes.',
  'Little networked things with weak defaults.',
  'A toy with a microphone, left on the conference table.')
g('Industrial control systems',
  'Industrial control systems run physical processes. Availability and safety outrank a casual reboot.',
  'A pump controller is not scanned with an aggressive probe during production.',
  'It moves real machines. Do not poke it casually.',
  'The boiler. You do not "just restart it" to see what happens.')
g('Real-time operating systems',
  'A real-time operating system promises timing. A late answer can be a failure even if the answer is correct.',
  'A controller that must answer in milliseconds is not loaded with extra agents that steal that time.',
  'On time matters as much as correct.',
  'A kitchen timer that rings late has already burned the dish.')
g('Embedded systems',
  'An embedded system is a computer built into a device, often with little room for extra security software.',
  'A door controller cannot run a full anti-malware suite, so it is segmented and its firmware is tracked.',
  'A computer inside a device, with little room for extras.',
  'The computer in a car key. You do not install a toolbox on it.')
g('High availability',
  'High availability keeps a service up through failure by having another instance ready to carry the work.',
  'Two application nodes sit behind a balancer so one can die and the site stays up.',
  'A second copy ready to carry the work.',
  'Two pilots. One can step out and the plane continues.')
g('Architecture tradeoffs',
  'Architecture tradeoffs weigh availability, resilience, cost, speed, scale, ease of deployment, who holds the risk, recovery, and whether a thing can be patched at all.',
  'A cheap single server is easy to deploy and is also a single outage and a single place to patch.',
  'Every design gives something up. Name what you gave up.',
  'A cheap lock is easy to fit and easy to pick. Say which one you chose.')

# --- 3.2 infrastructure ---
g('Device placement',
  'Device placement puts each box where its job matches the traffic it must see and the traffic it must not see.',
  'A sensor that should see intranet traffic is mistakenly placed outside the firewall, where it sees only internet noise.',
  'Put the box where the right traffic passes.',
  'A ticket booth at the wrong gate sees the wrong crowd.')
g('Security zones',
  'Security zones group systems with the same trust and the same rules, such as guest, user, server, and management.',
  'Printers live in a zone that can be reached for printing and cannot start connections to databases.',
  'Group things that share a trust level.',
  'Staff hallway, public lobby, and the safe room. Different rules.')
g('Attack surface',
  'Attack surface is every place an attacker can try: ports, apps, accounts, and physical access.',
  'Turning off three unused services shrinks the surface before any new product is bought.',
  'Every place someone can try.',
  'Every window and door, not only the front door you like.')
g('Connectivity choices',
  'Connectivity choices decide how a system reaches others: a private circuit, a VPN, or the open internet.',
  'Admin access to the servers uses a private path, not an open port on the internet.',
  'How it connects is a security decision.',
  'A private alley versus the public sidewalk.')
g('Failure modes',
  'A failure mode is how the design behaves when something breaks: fail open, fail closed, or fail to a reduced service.',
  'The door controller loses power and unlocks, which is a fail-open choice the team did not intend for the server room.',
  'When it breaks, does the door swing open or stay shut?',
  'A gate that springs open in a power cut, whether you meant that or not.')
g('Active versus passive devices',
  'An active device can block or change traffic. A passive device only observes.',
  'An inline preventer can drop a bad packet. A tap only copies it for someone to read.',
  'One can stop traffic. The other only watches.',
  'A guard who can shut the door, versus a camera that only records.')
g('Inline versus tap monitoring',
  'Inline monitoring sits in the path and can add delay or become a single point of failure. A tap copies traffic without sitting in the path.',
  'A tap on the server link feeds the sensor, so a sensor crash does not drop the clinic\'s traffic.',
  'In the path, you can block and you can break it. A tap only copies.',
  'Standing in the doorway versus watching from a side window.')
g('Jump servers',
  'A jump server is a hardened middle host. Admins sign in there, and only from there to the systems they manage.',
  'Direct SSH from the internet to the database is closed. Admins enter through one jump host with multi-factor sign-in.',
  'One hardened stepping stone, not a door on every server.',
  'A single guarded gatehouse. You do not give every room a street door.')
g('Proxy servers',
  'A proxy makes requests on behalf of clients, which lets you filter, log, and hide internal addresses.',
  'User browsers send web requests through a proxy that logs the destination and blocks a known-bad category.',
  'A middleman you run, on purpose.',
  'A concierge who fetches the parcel and writes down who asked.')
g('Intrusion detection and prevention',
  'Detection alerts on suspicious traffic. Prevention can also block it. Both depend on placement and on tuning.',
  'An alert fires on a known pattern, and a preventer in front of the app drops the same pattern.',
  'One warns. One can also stop.',
  'A smoke alarm versus a sprinkler.')
g('Load balancers',
  'A load balancer spreads work across servers and can stop sending work to a server that has failed.',
  'Two web nodes sit behind a balancer, and a failed health check pulls the sick node out.',
  'It shares the work and can skip a sick server.',
  'A host who seats parties across two dining rooms and skips the room with the broken oven.')
g('Network sensors',
  'A network sensor watches copies of traffic and turns them into alerts or records.',
  'A sensor on the server tap notices a workstation beaconing to a new address every minute.',
  'It watches copies of traffic.',
  'A lookout on the balcony who writes down what they see.')
g('Port security and 802.1X',
  'Port security and 802.1X stop an unknown device from simply plugging in and joining the network.',
  'A lobby wall port does nothing until the device authenticates.',
  'Plugging in is not joining.',
  'A door that asks who you are before the latch moves.')
g('Extensible authentication protocol',
  'Extensible authentication protocol is the framework many network sign-ins use inside 802.1X, including methods that protect the password.',
  'The wifi uses a method that does not send the password in the clear to the access point.',
  'The sign-in method inside the network handshake.',
  'The way the door asks for proof, not the door itself.')
g('Web application firewalls',
  'A web application firewall inspects HTTP requests for attacks such as injection and forged requests.',
  'A request with a classic injection pattern is dropped before it reaches the billing app.',
  'A filter that understands web requests.',
  'A reader at the kitchen door who rejects an order slip full of nonsense commands.')
g('Unified threat management',
  'Unified threat management combines several network controls, such as firewall, filtering, and detection, in one appliance.',
  'A small office uses one appliance for firewall, web filter, and basic detection, and still keeps it patched.',
  'Several jobs in one box. That box becomes important.',
  'One employee who is cook, cashier, and guard. If they are out, everything stops.')
g('Next-generation firewalls',
  'A next-generation firewall understands applications and users, not only ports.',
  'The rule allows the payroll app for the finance group and does not allow "any TCP 443" as a stand-in.',
  'It can say which app and which person, not only which port.',
  'A bouncer who checks the name and the purpose, not only that you have a coat.')
g('Layer 4 and layer 7 filtering',
  'Layer 4 filtering sees ports and addresses. Layer 7 filtering sees the application content.',
  'Port 443 is allowed, and a layer 7 rule still blocks a file-sharing app hiding inside that port.',
  'Ports are one view. The actual app is a deeper view.',
  'Checking that a truck arrived versus checking what is in the crates.')
g('Virtual private networks',
  'A VPN builds an encrypted path. It does not make the far end trustworthy, and it does not replace a password.',
  'A home user reaches the clinic through a VPN and still signs in with multi-factor authentication.',
  'An encrypted tunnel. Not a free pass once you arrive.',
  'An armored car. The cargo is still checked at the dock.')
g('Remote access',
  'Remote access lets people work from outside. It needs strong sign-in, a limited landing zone, and logging.',
  'Contractors reach one jump host, not the whole internal network, and the session is logged.',
  'Outside in, through a door you designed.',
  'A service entrance with a log, not a propped-open alley door.')
g('Transport layer security',
  'Transport layer security encrypts and authenticates a connection, usually after a certificate check.',
  'The mail site presents a certificate whose name matches, and the browser refuses a name that does not.',
  'A protected connection with a name check.',
  'A sealed pouch addressed to a specific person. The wrong name is a reason to refuse it.')
g('IPsec',
  'IPsec protects IP traffic, often as a site-to-site tunnel or a remote-access tunnel, with its own keys and policies.',
  'Two clinics link their networks with an IPsec tunnel, and the interesting traffic is named in the policy.',
  'A tunnel for IP traffic, with its own rules.',
  'A private road between two buildings, with a gate list of which trucks may use it.')
g('Software-defined WAN',
  'A software-defined WAN steers traffic across several links based on policy, such as sending voice on the clean link and bulk copies on the cheap one.',
  'The clinic uses broadband and a private circuit, and voice is pinned to the circuit when the broadband gets lossy.',
  'Several roads, and a policy that picks the road.',
  'A dispatcher who sends the ambulance on the clear street and the supply truck on the cheap one.')
g('Secure access service edge',
  'Secure access service edge combines wide-area steering with security checks near the user, so branch traffic is inspected without hauling everything to one office.',
  'A branch user\'s web traffic is checked at a nearby security edge instead of backhauled to the main clinic.',
  'Check close to the user, and steer the rest.',
  'A guard at each shop door, not one guard who makes every customer drive downtown first.')
g('Choosing effective controls',
  'Choosing effective controls means picking a control that actually reduces the risk you named, at a cost you can run.',
  'A camera is not chosen as the fix for a missing backup. A tested restore is.',
  'The control has to match the risk.',
  'A smoke alarm does not replace a lock, and a lock does not replace the alarm.')

# --- 3.3 data ---
g('Regulated data',
  'Regulated data is information a law tells you how to handle, such as health, payment, or student records.',
  'A clinic note is not pasted into a personal chat because the law and the policy both forbid it.',
  'A law tells you how to handle it.',
  'Medicine in a labeled cabinet, not loose in a purse.')
g('Trade secrets',
  'A trade secret is valuable because it stays secret. Careless sharing destroys the value and the legal claim.',
  'A formula is posted in a public ticket "so the vendor can see it."',
  'Its value is that outsiders do not have it.',
  'The family recipe. Once it is on the diner menu\'s back wall, it is not a secret.')
g('Intellectual property',
  'Intellectual property includes creations the organization owns or licenses, such as code, designs, and content.',
  'A contractor copies the product design into a personal portfolio site.',
  'Work the organization owns or licenses.',
  'The shop\'s sign and recipes. They are not free to take home.')
g('Legal information',
  'Legal information includes matters under privilege or contract, and it is not dumped into a wide ticket.',
  'A lawsuit strategy is filed in a help-desk ticket the whole company can read.',
  'Keep legal matters in the channel meant for them.',
  'A letter from the lawyer stays in the lawyer\'s folder.')
g('Financial information',
  'Financial information includes accounts, payroll, and card data, and it draws both criminals and regulators.',
  'A spreadsheet of card numbers is mailed to a personal address "for the weekend."',
  'Money data. Thieves and rules both care.',
  'The till tape. It does not go home in a pocket.')
g('Human-readable and machine data',
  'Some data people can read, such as a note. Some is for machines, such as a log or a token. Both can be sensitive.',
  'A session token looks like junk and is still a secret. A memo looks harmless and can still be regulated.',
  'Junk-looking data can be a secret. Plain words can be too.',
  'A coat-check ticket looks meaningless and still claims a coat. A diary looks ordinary and is private.')
g('Data classifications',
  'Classifications such as public, internal, confidential, and restricted tell people how careful to be. The label is useless if nobody handles it that way.',
  'A file marked restricted is stored in a world-readable share, so the label and the handling disagree.',
  'The label only works if the handling matches.',
  'A jar marked "poison" that is stored with the sugar has a lying label or a careless shelf.')
g('Data at rest, in transit, and in use',
  'Data at rest sits on disk. Data in transit moves. Data in use is open in memory or on a screen. Each state needs its own protection.',
  'A laptop disk is encrypted, the mail path uses TLS, and the screen still shows a record in a busy lobby.',
  'Sitting, moving, or open on a screen. Three different moments.',
  'A locked safe, an armored car, and the moment the teller has the cash on the counter.')
g('Data sovereignty',
  'Data sovereignty means the laws of the place where data sits or is processed can apply, which can surprise a team that "just picked a region."',
  'Patient records are stored in another country whose law conflicts with the clinic\'s duty.',
  'Where it sits can decide which law applies.',
  'A safe deposit box in another town, under that town\'s rules.')
g('Geolocation restrictions',
  'Geolocation restrictions limit where a sign-in or a data access may happen.',
  'The payroll app refuses a sign-in from a country where the company has no staff.',
  'Some places are simply not allowed.',
  'The shop key does not work from another city\'s door.')
g('Masking, tokenization, and obfuscation',
  'Masking shows a fake or partial value. Tokenization swaps in a stand-in. Obfuscation, including hiding a message, makes the real value hard to see. None of them is a substitute for access control by itself.',
  'Support sees the last four digits. The payment system stores a token. A hidden comment in a file is still not access control.',
  'Hiding or swapping the value is not the same as deciding who may ask.',
  'Black bars, coat checks, and invisible ink. The door lock is still a separate thing.')
g('Permission restrictions on data',
  'Permission restrictions limit which accounts can read or change the data, which is the control masking does not replace.',
  'The restricted share allows the records group to read and denies everyone else, including the help desk.',
  'Who may open it, by account.',
  'The diary key is held by one person, not by everyone who can see the shelf.')

# --- 3.4 resilience ---
g('Load balancing versus clustering',
  'Load balancing spreads requests. Clustering ties systems so they share state or take over for each other. They solve related problems and are not the same knob.',
  'A balancer shares web traffic. A database cluster keeps a second node able to take over the data.',
  'Sharing the line is not the same as a partner who can take the book.',
  'Two cashiers versus a second person who can finish the same sale.')
g('Hot sites',
  'A hot site is ready to run, with current or near-current data, so the switch is fast and the cost is high.',
  'A second clinic system is live and receiving copies, and a drill switches to it in minutes.',
  'Already running. Expensive. Fast.',
  'A second kitchen with the soup already warm.')
g('Warm sites',
  'A warm site has gear and some data, and it needs a restore or a catch-up before it carries the full load.',
  'The spare site has servers racked and last night\'s backup, and the team plans hours, not minutes.',
  'Gear is there. Data needs a catch-up.',
  'A second kitchen with cold ingredients and a recipe, not a hot pot.')
g('Cold sites',
  'A cold site is space and maybe power. You bring the systems and the data, so it is cheap and slow.',
  'An empty room with power is not a recovery plan for a Monday morning outage.',
  'A room. You still have to move in.',
  'An empty stall at the market. You still haul the stove.')
g('Geographic dispersion',
  'Geographic dispersion places copies far enough apart that one fire, flood, or outage does not take both.',
  'The backup site is in another region, not in the building next door on the same power grid.',
  'Far enough that one disaster does not get both.',
  'A spare key at a relative\'s house across town, not in the same drawer.')
g('Platform diversity',
  'Platform diversity avoids a single product bug taking down every copy at once.',
  'Two different name resolvers are used so one vendor bug does not blank every lookup.',
  'Do not bet everything on one product\'s bug.',
  'Two suppliers for flour, so one bad mill does not close the bakery.')
g('Multi-cloud recovery',
  'Multi-cloud recovery keeps a path to run in more than one provider so one provider\'s outage is not the end.',
  'The design can bring the public site up in a second provider, and that path is actually tested.',
  'More than one provider, and a tested way to move.',
  'A second market you can sell in if the first one floods.')
g('Continuity of operations',
  'Continuity of operations is how the work continues, including who decides, who works, and what "good enough" looks like.',
  'If the building closes, appointments move to phone visits and the paper downtime packet is already printed.',
  'How the job continues, not only how the server reboots.',
  'If the stove dies, you still serve the cold menu you planned.')
g('Capacity planning',
  'Capacity planning asks whether people, technology, and space can carry the load you are promising, including during a failover.',
  'The spare site has half the disk of production, so a full failover would fill it on day one.',
  'Can the spare actually hold the work?',
  'A spare dining room with four chairs cannot seat the Saturday crowd.')
g('Tabletop exercises',
  'A tabletop exercise talks through an incident around a table so people find the gaps without breaking production.',
  'The team walks a ransomware story and discovers nobody knows who may approve a shutdown.',
  'Talk it through before you have to do it.',
  'A fire drill discussed in the break room, with the map on the table.')
g('Failover tests',
  'A failover test actually moves the work to the spare and proves users can work there.',
  'The team fails the database to the second node on a Sunday and times how long the app is quiet.',
  'Actually switch, and time it.',
  'Cooking the Saturday menu once in the spare kitchen.')
g('Simulation tests',
  'A simulation test runs a realistic scenario, sometimes with injected signals, to see whether detection and response work.',
  'A planned phishing simulation and a fake alert are used to time the on-call response.',
  'A realistic rehearsal.',
  'A surprise drill with a smoke machine, not only a conversation.')
g('Parallel processing tests',
  'A parallel processing test runs the spare alongside production and compares results before you trust the spare.',
  'The spare site processes a copy of the day\'s orders and the totals match production.',
  'Run both, and compare, before you trust the spare.',
  'Two cooks make the same soup. You taste both before you retire the first pot.')
g('Onsite and offsite backups',
  'Onsite backups restore quickly and die in the same fire. Offsite backups survive the building and take longer to reach.',
  'A copy in the closet and a copy in another region are both on the schedule, for different reasons.',
  'Near is fast and fragile. Far is slow and survives.',
  'A spare key in the kitchen and another at a relative\'s house.')
g('Backup frequency and encryption',
  'Frequency decides how much work you can lose. Encryption decides whether a stolen backup is readable.',
  'Nightly encrypted backups mean a theft of the tape is ugly and a lunchtime mistake can lose a day of work.',
  'How often, and whether a thief can read the copy.',
  'A photo of the recipe every night, locked in a box.')
g('Snapshots, replication, and journals',
  'A snapshot is a point-in-time image. Replication copies changes to another system. A journal records the changes so you can roll forward.',
  'A database replica is minutes behind, and the journal can replay the last transactions after a restore.',
  'A photo, a live copy, and a list of changes. They are different tools.',
  'A picture of the kitchen, a second kitchen being updated, and the order tickets that came in since.')
g('Recovery testing',
  'A backup you have never restored is a hope. Recovery testing proves the copy actually comes back.',
  'Once a quarter the team restores one file server to an isolated host and opens a real file.',
  'Restore it once in a while or you do not have a backup.',
  'You bake from the spare recipe card once, to be sure it is readable.')
g('Generators',
  'A generator makes power when the utility is out, after a short delay, and it needs fuel and a test.',
  'The clinic generator starts in the quarterly test and runs long enough to carry the server room.',
  'It makes power, if it has fuel and if you have tested it.',
  'A spare stove in the yard. It only helps if the gas bottle is full.')
g('Uninterruptible power supplies',
  'An uninterruptible power supply bridges the seconds or minutes until a generator starts or the system shuts down cleanly.',
  'A five-minute UPS keeps the servers up through a blink and is not treated as an overnight plan.',
  'A short bridge, not an overnight plan.',
  'A thermos of hot water. It is not a second stove.')

# --- 4.1 hardening ---
g('Establishing a secure baseline',
  'Establishing a baseline means writing the approved settings once, from a known-good build, before copies go out.',
  'The laptop image is built, measured, and signed off before the first employee receives one.',
  'Write the approved setup before you copy it.',
  'Agree on the recipe before you cook fifty pans.')
g('Deploying a baseline',
  'Deploying a baseline means new systems start from that approved build, not from a one-off click path.',
  'A new server is cloned from the approved image instead of hand-built on a Friday.',
  'New systems start from the approved copy.',
  'Every new pot starts from the same recipe card.')
g('Maintaining a baseline',
  'Maintaining a baseline means drift is found and pulled back, and the baseline itself changes only through the change process.',
  'A monthly check finds a server whose firewall was turned off and puts the approved rules back.',
  'Keep systems on the approved setup, and change the setup only on purpose.',
  'Taste the soup every service and correct it. Change the card only when the owner says so.')
g('Hardening workstations and servers',
  'Hardening workstations and servers removes what you do not need, patches what you keep, and turns on the host controls.',
  'A server loses unused services, gains a host firewall, and keeps automatic updates for the approved channel.',
  'Less stuff, current fixes, host controls on.',
  'Clear the bench, oil the tools you keep, and lock the drawer.')
g('Hardening network devices',
  'Hardening a switch or router means a current image, no default password, management only from the management network, and unused ports shut.',
  'A switch loses its published admin password, stops offering old remote protocols, and shuts empty ports.',
  'The network box gets the same care as a server.',
  'The front-door lock is rekeyed, and the side door you never use is barred.')
g('Hardening cloud infrastructure',
  'Hardening cloud infrastructure means tight roles, private storage, logged admin actions, and no open management ports.',
  'A storage bucket is private, the admin role is small, and the audit log is on.',
  'Close the cloud doors you did not mean to open.',
  'A rented stall with the shutter down and the till key on a short ring.')
g('Hardening operational technology',
  'Hardening operational technology respects safety and timing: segment it, control who can change it, and do not run reckless scans.',
  'The pump network has no path from guest wifi, and changes go through the plant procedure.',
  'Protect it without knocking it over.',
  'You lock the boiler room. You do not kick the boiler to test the lock.')
g('Wireless site surveys',
  'A site survey measures real signal, interference, and coverage in the building before you place access points.',
  'The survey shows a dead zone in radiology that a guess from the hallway missed.',
  'Measure the building. Do not guess.',
  'Walk the dining room with a candle before you decide where the lamps go.')
g('Heat maps',
  'A heat map draws where the signal is strong or weak so you can see coverage and overlap.',
  'The map shows two access points shouting on the same channel in one hall.',
  'A picture of strong and weak signal.',
  'A sketch of where the room is bright and where it is dim.')
g('Access-point placement',
  'Access-point placement puts radios where people work, away from metal and noise, and not in a spot that spills into the street more than it must.',
  'An access point moves from inside a metal ceiling to the hallway, and the spill into the parking lot drops.',
  'Put the radio where the people are, and mind where the signal leaks.',
  'Hang the lamp over the table, not inside the closet.')
g('Mobile device management',
  'Mobile device management pushes settings, apps, and remote actions such as lock and wipe to phones and tablets the organization allows.',
  'A lost phone is locked from the console the same hour it is reported.',
  'A way to set and, if needed, wipe the phones you manage.',
  'A key cabinet that can also change the locks on the company cars.')
g('Bring-your-own-device',
  'Bring-your-own-device means the person owns the phone. You still need a rule for company data on it.',
  'A personal phone may read mail only inside a managed work profile that can be removed without wiping the photos.',
  'Their phone. Your data still needs a rule.',
  'A personal car used for a delivery. The packages are still the shop\'s.')
g('Corporate-owned devices',
  'A corporate-owned device is the organization\'s hardware, so the organization can set stricter controls and can wipe the whole device.',
  'A company phone requires a long screen lock and disk encryption before mail appears.',
  'The company owns it, so the company can set the rules.',
  'A company truck. The shop decides the locks.')
g('Choose-your-own-device',
  'Choose-your-own-device lets a person pick from a list the organization approved and still manages.',
  'Staff pick from three approved phones, and every one of them enrolls in management.',
  'They choose from a list you already trust.',
  'Pick any company bike. Every bike still has the shop\'s lock.')
g('Cellular, Wi-Fi, and Bluetooth connections',
  'Phones move between cellular, wifi, and Bluetooth. Each path has its own exposure, and a policy should say which are allowed for work.',
  'Work mail is allowed on cellular and the company wifi, and Bluetooth file sharing stays off.',
  'Three radios. Decide which ones may carry work.',
  'Three doors on a shop. You do not leave all three propped open.')
g('WPA3',
  'WPA3 is the current wifi protection meant to replace older handshakes that leak a password to offline guessing.',
  'The staff network uses WPA3, and a device that only speaks an older mode stays on a fenced guest path.',
  'The current wifi lock.',
  'A new deadbolt. The old skeleton key is not "close enough" for the office.')
g('RADIUS for wireless',
  'RADIUS lets each person sign in to wifi with their own account instead of a shared passphrase taped to the wall.',
  'Staff wifi asks for the directory account, and a departing employee loses wifi when the account is disabled.',
  'Each person signs in. There is no shared password on a sticky note.',
  'A door that checks your own badge, not a keypad code everyone knows.')
g('Mobile application control',
  'Mobile application control limits which apps may be installed, often with an allow list and a block on sideloading.',
  'A phone refuses a side-loaded game because only the approved store apps are allowed.',
  'Only approved apps.',
  'The company truck only carries the approved tools, not a stranger\'s toolbox.')
g('Jailbreak and root detection',
  'Jailbreak and root detection notices when a phone\'s protections have been removed, and the policy can then block company data.',
  'A rooted phone loses access to mail until it is restored or replaced.',
  'If the phone\'s own locks were ripped out, do not trust it with company data.',
  'A truck with the door alarm cut. You do not load the till into it.')
g('Screen locks and full-device encryption',
  'A screen lock stops a casual finder. Full-device encryption stops someone who pulls the storage out. You want both.',
  'A phone with a PIN and encryption is lost, and the data is not readable without the PIN.',
  'A lock on the screen and a lock on the storage.',
  'A locked car and a locked case in the trunk.')
g('Remote wipe',
  'Remote wipe erases company data, or the whole device, when the device is lost or the person leaves.',
  'A stolen tablet is wiped from the console before the end of the shift.',
  'Erase it from far away when it is gone.',
  'Calling the bank to kill a lost card.')
g('Sandboxing',
  'Sandboxing runs untrusted code or documents in a confined space so a crash or a payload does not own the whole computer.',
  'An email attachment opens in a sandbox that cannot read the user\'s documents folder.',
  'Let it run where it cannot reach the rest.',
  'A stray animal in a pen, not loose in the kitchen.')

# --- 4.2 assets ---
g('Procurement',
  'Procurement is how you buy. Security belongs in the purchase: requirements, vendor checks, and no surprise cloud signups.',
  'A camera purchase includes a requirement to change the default password and to disable old protocols.',
  'Buy it with the security needs already on the order.',
  'You order a lock, not a door with a hole where the lock should be.')
g('Ownership and classification',
  'Every asset needs an owner and a classification so someone is accountable and the handling is clear.',
  'The payroll database has a named owner and a restricted label, written in the inventory.',
  'Name who owns it and how sensitive it is.',
  'Every jar has a label and a person who refills it.')
g('Inventory',
  'An inventory is the list of hardware, software, and data you actually have. You cannot protect what you cannot list.',
  'A forgotten test server is missing from the inventory and missing from the patch list.',
  'If it is not on the list, you will not patch it.',
  'A pantry with no list grows mystery jars.')
g('Enumeration',
  'Enumeration discovers what is really on the network or in the accounts, and it is how you find the inventory lies.',
  'A scan finds a webcam the inventory never listed.',
  'Look, and compare with the list.',
  'Counting the spoons instead of trusting last year\'s note.')
g('Sanitization',
  'Sanitization removes data so the next user of a device or a disk cannot read it. Deleting a shortcut is not sanitization.',
  'A laptop is wiped with a method that matches the data\'s sensitivity before it is resold.',
  'Remove the data, not just the icon.',
  'Washing the cutting board, not wiping the crumbs onto the floor.')
g('Destruction',
  'Destruction physically ruins media when sanitization is not enough or not possible.',
  'A failed drive that cannot be wiped is shredded, and the certificate is filed.',
  'Break it so the data cannot come back.',
  'Burning a notebook you cannot erase.')
g('Certification of disposal',
  'Certification of disposal is the record that sanitization or destruction happened, who did it, and when.',
  'The recycler\'s certificate is matched to the drive serials before the ticket closes.',
  'Keep the proof that it was destroyed or wiped.',
  'A receipt for the shredding, not a shrug.')
g('Data retention',
  'Retention says how long you keep data and when you must delete it. Keeping everything forever is not the safe default.',
  'Mail older than the policy is deleted on schedule, including the backups that would resurrect it.',
  'Keep it for the required time, then actually let it go.',
  'Leftovers have a date on the lid. After that date they leave the fridge.')

# --- 4.3 vulnerability management ---
g('Vulnerability scans',
  'A vulnerability scan looks for known flaws and weak settings. It is not an exploit, and it is not proof that a flaw is reachable.',
  'A weekly scan lists an old library on a server that is not exposed, and the ticket records both facts.',
  'A search for known holes. Confirm before you panic.',
  'A health inspector with a checklist, not a wrecking crew.')
g('Static application testing',
  'Static testing reads the code or the binary without running it, which finds some bugs before the app is live.',
  'The build fails because the static check finds a query built by gluing user input into a string.',
  'Read the code before it runs.',
  'Reading a recipe for a mistake before you turn on the stove.')
g('Dynamic application testing',
  'Dynamic testing runs the app and sends it inputs, which finds flaws that only appear in motion.',
  'A test user sends a crafted search and the running app returns another user\'s row.',
  'Poke the running app in a safe test.',
  'Tasting the soup while it cooks, on purpose, in the test kitchen.')
g('Package monitoring',
  'Package monitoring watches libraries and packages for newly announced flaws.',
  'A dependency alert names a library in the billing app the morning a flaw is published.',
  'Watch the ingredients, not only the finished pot.',
  'A recall notice on a spice you already bought.')
g('Threat feeds',
  'A threat feed is a stream of indicators, such as bad addresses, that you can use to detect or block.',
  'The firewall starts blocking addresses from a feed after the team checks the feed\'s false-alarm rate.',
  'A list of known-bad clues, used with judgment.',
  'A daily list of stolen-card numbers the cashier can check.')
g('Open-source intelligence',
  'Open-source intelligence is what you can learn from public sources: job posts, code, leaks, and your own exposed services.',
  'A job posting describes the exact badge system, which tells an attacker where to look.',
  'Public information is still information.',
  'The shop window that shows the safe from the street.')
g('Information-sharing organizations',
  'Information-sharing organizations let peers warn each other about threats under rules about what you may repeat.',
  'A peer clinic warns of a campaign, and the team uses the indicator without posting the peer\'s name in a public chat.',
  'Share with peers, and honor the rules of the share.',
  'Shop owners on a street who warn each other, and do not put the warning on a billboard.')
g('Dark-web monitoring',
  'Dark-web monitoring looks for your data or your name in criminal markets. A hit is a lead to verify, not an automatic breach declaration.',
  'A sample of mail shows up in a monitoring report, and the team checks whether the sample is real.',
  'A sighting in a criminal market is a lead. Verify it.',
  'A rumor that your keys are for sale. You still check the lock.')
g('False positives and false negatives',
  'A false positive is an alert or a finding that is not real. A false negative is a real problem the tool missed.',
  'A scan flags a patched library because the banner string never changed, and a quiet host with a real bug is missed.',
  'A cry of wolf, and a wolf nobody cried about. Track both.',
  'A smoke alarm that screams at toast, and one that stays silent in a real fire.')
g('Prioritizing vulnerabilities',
  'Prioritizing means fixing the reachable, severe, and valuable issues first, not the longest list.',
  'An internet-facing critical bug is scheduled before a low finding on a lab printer.',
  'Fix what can hurt you first.',
  'You mop the flood before you polish the window.')
g('CVE identifiers',
  'A CVE identifier is a public name for a known vulnerability so two people can be sure they mean the same flaw.',
  'The ticket names CVE and the year and number, and the tech looks up that exact flaw rather than a vendor nickname.',
  'A shared name for one flaw.',
  'A case number so two clerks do not argue about which complaint.')
g('CVSS scores',
  'A CVSS score is a standardized severity number. It is a starting point, not a substitute for how the flaw sits in your environment.',
  'A high score on a system that is off the network is scheduled behind a medium score on the public website.',
  'A number that starts the conversation. Your exposure finishes it.',
  'A weather score. You still look out your own window.')
g('Exposure factor',
  'Exposure factor is the portion of an asset you expect to lose if the event happens.',
  'A laptop theft might expose the whole unencrypted disk, so the exposure factor for that data is total.',
  'How much of the thing you lose if it happens.',
  'A spill that ruins the whole pot, not a sip.')
g('Environmental and business impact',
  'Environmental and business impact ask what the flaw does here: which process stops, which law applies, which customer is hurt.',
  'The same bug on a kiosk and on the payroll server is not the same business impact.',
  'What it does to this organization, not to a generic one.',
  'A broken oven on a Saturday is not the same as a broken oven on a closed Monday.')
g('Risk tolerance',
  'Risk tolerance is how much risk the organization will carry. It decides which findings can wait and which cannot.',
  'Leadership accepts a low finding on a lab for thirty days and refuses to accept an internet-facing critical bug overnight.',
  'How much risk you are willing to carry.',
  'How spicy the kitchen will serve. Some dishes are off the menu.')
g('Patch remediation',
  'Patch remediation is putting the fix on, through the change process, with a way back.',
  'The pilot group gets the patch on Tuesday, and the rest follow after the pilot stays healthy.',
  'Apply the fix, with a way back.',
  'Replace the cracked pane, and keep the old one until you know the new one fits.')
g('Compensating controls for vulnerabilities',
  'A compensating control reduces the risk when you cannot patch yet.',
  'An unpatchable instrument is firewalled so only one management host can reach it.',
  'If you cannot fix it yet, fence it.',
  'You cannot replace the lock today, so you station a person at the door.')
g('Exceptions and exemptions',
  'An exception is a recorded, time-boxed decision to live with a finding. An exemption is a formal waiver. Silence is neither.',
  'A legacy app has a ninety-day exception, an owner, and a compensating control. It is not "we will get to it."',
  'Write it down, name an owner, and put a date on it.',
  'A signed note that the broken stair may stay for a month, not a shrug.')
g('Rescanning and verification',
  'Rescanning and verification prove the finding is gone, or prove the compensating control is in place.',
  'After the patch, the same scan no longer reports the flaw, and the ticket records that result.',
  'Check again. Hope is not verification.',
  'You run the water after the plumber leaves.')
g('Vulnerability reporting',
  'Vulnerability reporting tells the right people what was found, what was fixed, and what was accepted, in language they can use.',
  'A monthly note to leadership lists open critical items, owners, and dates, without a dump of raw scan noise.',
  'Tell the right people, in words they can act on.',
  'A short note to the owner: what broke, who is fixing it, and when.')

# --- 4.4 monitoring ---
g('Monitoring systems, applications, and infrastructure',
  'Monitoring covers hosts, the apps on them, and the network underneath. A quiet app log does not mean the host is healthy, and the reverse is also true.',
  'The website looks up while the host disk is filling, because nobody watched the host.',
  'Watch the machine, the program, and the network. Each can fail alone.',
  'Watch the stove, the soup, and the gas line. Any one can ruin dinner.')
g('Log aggregation',
  'Log aggregation copies logs to a central place so one missing host does not erase the story.',
  'Authentication logs are shipped off the server every minute, and a later wipe of the server does not wipe the copy.',
  'Keep a copy of the logs somewhere else.',
  'A second copy of the sign-out sheet in the office, not only on the clipboard that can walk away.')
g('Alerting',
  'Alerting tells a person when a rule trips. An alert with no owner is a log line with extra steps.',
  'Failed-login spikes page the on-call person, who has a written first step.',
  'A signal that reaches a person who knows the first step.',
  'A bell someone is assigned to answer.')
g('Alert tuning',
  'Alert tuning reduces noise so real events are not lost, without quietly deleting the detections you still need.',
  'A chatty backup alert is adjusted with a note, and the failed-login alert is left loud.',
  'Quiet the noise. Do not mute the fire bell.',
  'Stop yelling about every crumb. Keep yelling about smoke.')
g('Quarantine',
  'Quarantine isolates a suspect file or host so it cannot keep spreading while you look.',
  'A workstation is pulled off the network and left running so memory evidence is not thrown away.',
  'Separate it. Do not destroy the evidence in the rush.',
  'Move the spoiled pot off the stove. Do not scrape it into the trash before anyone looks.')
g('Archiving logs',
  'Archiving keeps logs for the retention period in a store that is cheaper and still protected from tampering.',
  'Ninety days of hot logs stay searchable, and a year of older logs sits in locked archive storage.',
  'Keep them for the required time, locked.',
  'Old receipts in a locked box, not in the alley.')
g('Security information and event management',
  'A SIEM collects and correlates logs. It does not decide guilt by itself. A person still judges the alert.',
  'The SIEM ties a bad login to a new process on the same host, and an analyst opens the ticket.',
  'It gathers clues. A person still decides.',
  'A clerk who stacks the receipts. The owner still decides if the till is short.')
g('Data loss prevention',
  'Data loss prevention watches for sensitive data leaving by mail, web, or a device, and it blocks or alerts.',
  'A mail rule stops a message that contains a full set of card numbers.',
  'It watches for secrets walking out.',
  'A guard who stops a box of files at the door.')
g('SNMP traps',
  'An SNMP trap is a device pushing an event, such as a port down or a temperature alarm, to a listener.',
  'A switch sends a trap when a trunk port drops, and the listener opens a ticket.',
  'The device speaks up when something happens.',
  'A stove that rings when the temperature runs away.')
g('NetFlow',
  'NetFlow and similar records summarize who talked to whom, on which ports, and how much, without storing every packet.',
  'Flow records show a workstation sending gigabytes at night to an address nobody recognizes.',
  'A summary of conversations, not the full transcript.',
  'A log of who called whom and for how long, not a recording of every word.')
g('Endpoint detection and response',
  'Endpoint detection and response watches behavior on the host and can isolate the host or pull artifacts for a look.',
  'The agent isolates a laptop that started encrypting files, and the analyst pulls the process list.',
  'A watcher on the computer that can also cut it off.',
  'A floor manager who can lock the shop door and still tell you what they saw.')

# --- 4.5 enterprise capabilities ---
g('Firewall rules and screened subnets',
  'Firewall rules should default to deny. A screened subnet is a buffer zone between the internet and the inside, for systems that must be reachable.',
  'The public website sits in a screened subnet. The database stays inside, and the firewall allows only the app port.',
  'Deny by default. Put public systems in a buffer, not on the couch with the crown jewels.',
  'A porch for visitors. The family rooms stay behind another door.')
g('IDS and IPS signatures',
  'Signatures match known bad patterns. They miss what they have never seen, and they need updates. Trends in the alerts matter as much as one hit.',
  'A new signature pack is applied after a test, and a sudden rise in one signature becomes a ticket.',
  'Known patterns, kept current. Watch the trend, not only one beep.',
  'A wanted poster. It does not catch a face that is not on it, and a stack of the same poster in one day means something.')
g('Web filtering',
  'Web filtering blocks or allows sites by policy, whether the filter sits on the device or on a central proxy.',
  'The clinic blocks a category of sites at the proxy, and a bypass on one laptop is treated as drift.',
  'A policy for where browsers may go.',
  'A door list for which shops the delivery driver may enter.')
g('URL scanning and categorization',
  'URL scanning checks a link in the moment. Categorization sorts sites into buckets such as news or malware so a policy can act.',
  'A fresh phishing link is scanned and blocked even though it is too new for yesterday\'s category list.',
  'Check the link, and sort the site.',
  'Looking at a package and also knowing which shelf it belongs on.')
g('Reputation block lists',
  'A reputation block list refuses addresses or domains that many others have already seen as bad.',
  'Mail from a domain on the reputation list is rejected at the gateway.',
  'Refuse names that already have a bad reputation.',
  'A diner who is barred at every door on the street.')
g('Group Policy',
  'Group Policy pushes Windows settings from a central place so one laptop cannot quietly drift forever.',
  'A screen-lock policy arrives from the domain, and a local change is overwritten at the next refresh.',
  'Central rules for Windows machines.',
  'A posted kitchen standard that every station is reset to.')
g('SELinux',
  'SELinux is a mandatory access control system on some Linux hosts. It confines processes even if they are tricked.',
  'A web service is confined so a flaw in the service cannot read the payroll files.',
  'Even a tricked program stays in its lane.',
  'A cook who can reach the soup and cannot reach the safe, even if they are fooled.')
g('Secure protocol selection',
  'Secure protocol selection means using the protected version and the right port, and turning the clear-text version off.',
  'File transfer for admin work uses SSH, and the old clear-text transfer service is not left listening.',
  'Pick the protected way, and turn the clear one off.',
  'Send the letter in a sealed pouch, and stop leaving postcards of the same note.')
g('DNS filtering',
  'DNS filtering refuses to resolve names you do not want people to reach, which stops some malware from finding its server.',
  'The clinic resolvers refuse a known malware domain, and the workstation\'s beacon fails.',
  'Do not answer the bad names.',
  'A phone book that omits the numbers you do not want called.')
g('SPF, DKIM, and DMARC',
  'SPF lists who may send mail for a domain. DKIM signs the message. DMARC says what receivers should do when those checks fail, and it asks for reports.',
  'A lookalike sender fails DMARC and the receiving gateway rejects it because the domain published a reject policy.',
  'Who may send, a signature, and a rule for failures.',
  'A list of couriers, a seal, and an order to refuse unsealed parcels.')
g('Email gateways',
  'An email gateway filters mail before it reaches the inbox: spam, malware, and spoofing.',
  'A gateway strips a dangerous attachment and tags the message so the user sees the warning.',
  'The mail is checked before the person sees it.',
  'A doorman who opens suspicious parcels in the lobby.')
g('File integrity monitoring',
  'File integrity monitoring alerts when important files change from a known-good fingerprint.',
  'The hash of a system binary changes overnight, and the alert fires before the morning shift.',
  'Tell me when an important file changes.',
  'A seal on the pantry. A broken seal is the news.')
g('Network access control',
  'Network access control checks a device before it joins, and can put a sick or unknown device on a limited network.',
  'A laptop missing disk encryption is placed on a remediation network instead of the staff network.',
  'Check the device before it joins the real network.',
  'A coat check that also turns away a guest with no ticket.')
g('User and entity behavior analytics',
  'Behavior analytics learns a normal pattern and flags a break, such as a user pulling far more files than usual.',
  'An account that usually reads five records a day downloads five thousand, and an alert opens.',
  'It notices when someone stops acting like themselves.',
  'A regular who suddenly orders the entire menu to go.')

# --- 4.6 identity ---
g('Provisioning accounts',
  'Provisioning creates an account with the right access on the day the person starts, from a request, not from a hallway favor.',
  'A new nurse gets the nurse role on Monday morning because a ticket said so, not because someone copied an admin.',
  'Create the account from a request, with the right access.',
  'Cut a key for the new hire on their first morning, from the list, not from a spare you found.')
g('Deprovisioning accounts',
  'Deprovisioning removes or disables access the day the person leaves, including remote access, badges, and tokens.',
  'A contractor\'s account and badge die on the last afternoon, not at the next quarterly cleanup.',
  'Take the keys back the day they leave.',
  'Collect the house key at the end of the visit, not next year.')
g('Permission assignments',
  'Permission assignments are the rights you grant. Extra rights "to be helpful" become the next incident.',
  'A temp receives the mail role and not a copy of the director\'s groups.',
  'Grant the rights the job needs, and write them down.',
  'Hand the waiter the dining-room key, not the whole ring.')
g('Identity proofing',
  'Identity proofing checks that a person is who they claim before you give them an account or a reset.',
  'A password reset for a director is done only after a callback to the number already on file.',
  'Prove the person before you hand over the account.',
  'You check a photo ID before you cut a new key.')
g('Federation',
  'Federation lets one organization trust identities from another, under rules, so people do not need a second password for everything.',
  'A partner clinic\'s staff reach one shared app with their home login, and only the groups named in the agreement.',
  'Trust another organization\'s identities, on purpose and within limits.',
  'Accepting a sister shop\'s employee badge for the shared storeroom, and nowhere else.')
g('Single sign-on',
  'Single sign-on lets a person authenticate once and reach several apps. The one login becomes a high-value target, so it needs strong proof.',
  'Staff sign in once to reach mail and the chart, and that one login requires a second factor.',
  'One strong login for many doors. Protect that login.',
  'One master key. It deserves the best lock on the ring.')
g('LDAP',
  'LDAP is a directory protocol. The protected form keeps lookups from traveling in the clear.',
  'The app queries the directory over the protected port, and anonymous browsing of the whole directory is off.',
  'The phone book protocol. Use the locked version.',
  'Looking up an extension on a private list, not shouting the names down the hall.')
g('OAuth',
  'OAuth lets an app receive limited access without receiving the user\'s password.',
  'A calendar helper gets a token that can read the calendar and cannot read mail.',
  'A limited token, not the password.',
  'A valet key that starts the car and does not open the trunk.')
g('SAML',
  'SAML carries a signed assertion that a trusted identity provider has already authenticated the user.',
  'The chart app trusts a signed assertion from the clinic identity provider and does not ask for a second password.',
  'A signed note that says this person already proved themselves.',
  'A sealed letter from the front desk telling the ward the visitor was already checked.')
g('Attestation',
  'Attestation is a statement that something is true: a device is healthy, a person still works here, or a control is in place.',
  'A laptop attests that disk encryption is on before the network lets it in.',
  'A formal "this is true" from a party you trust.',
  'A note from the mechanic that the brakes were checked.')
g('Mandatory access control',
  'Mandatory access control applies labels the user cannot simply give away. The system enforces the label.',
  'A secret-labeled file cannot be copied into a public folder by the file\'s owner, because the label forbids it.',
  'The system enforces the label, even against the owner.',
  'A classified stamp the clerk cannot peel off to be helpful.')
g('Discretionary access control',
  'Discretionary access control lets the owner decide who else may have the file.',
  'The owner of a project folder grants read to a teammate and can also grant too much if nobody reviews it.',
  'The owner chooses who else gets in.',
  'You decide who may borrow your book, which is friendly and easy to overdo.')
g('Role-based access control',
  'Role-based access control grants rights to a role, and people receive the role, so you change the role instead of editing every person.',
  'Nurses get the nurse role. When a nurse becomes a manager, the roles change and the old rights leave.',
  'Rights follow the job, not the person\'s name.',
  'Every waiter gets the waiter key. When they become a cook, they swap keys.')
g('Rule-based access control',
  'Rule-based access control applies rules such as "this department, this hour, this network."',
  'Payroll files open only from the finance network during business hours.',
  'If the rule matches, the door opens.',
  'The storeroom opens for kitchen staff, and only before noon.')
g('Attribute-based access control',
  'Attribute-based access control decides from attributes: who, what device, where, and how sensitive the data is.',
  'A doctor on a healthy clinic device can read a chart. The same account on a personal laptop cannot.',
  'Several facts combine into the decision.',
  'The pharmacy checks the badge, the hour, and the prescription together.')
g('Time-of-day restrictions',
  'Time-of-day restrictions limit when an account may sign in.',
  'The front-desk account works from 07:00 to 19:00 and is refused at 02:00.',
  'The account only works in its hours.',
  'The shop key turns during business hours and not at midnight.')
g('Multifactor authentication',
  'Multifactor authentication requires two or more different kinds of proof, not two copies of the same kind.',
  'A password plus a prompt on a phone is two kinds. A password plus a PIN is still only something you know.',
  'Two different kinds of proof.',
  'A key and a face at the door, not two keys on the same ring.')
g('Something you know, have, are, or where you are',
  'The factor kinds are something you know, something you have, something you are, and somewhere you are. Two of the same kind are not multi-factor.',
  'A fingerprint and a password are two kinds. Two passwords are one kind, twice.',
  'Know, have, are, or where. Mix the kinds.',
  'A password is a secret. A badge is a thing. A face is you. A building is a place.')
g('Password length, complexity, reuse, and age',
  'Length beats clever substitutions. Reuse across sites is dangerous. Forced frequent changes often create weaker passwords unless there is a reason.',
  'The policy wants a long passphrase and refuses the last few passwords, and it does not force a change every two weeks without cause.',
  'Long, not reused, and not rotated for sport.',
  'A long unique phrase on the diary, not a new short one every Monday that ends up on a sticky note.')
g('Password managers',
  'A password manager stores unique long passwords so people do not reuse one password everywhere. The manager itself needs a strong unlock.',
  'Each site gets its own long password from the manager, and the manager is unlocked with a long passphrase plus a second factor.',
  'A locked book of unique passwords. Guard the book.',
  'A key ring in a locked box, instead of one key that opens every door.')
g('Passwordless authentication',
  'Passwordless authentication uses a device or a biometric instead of a memorized secret, which removes password reuse and still needs a recovery plan.',
  'A security key signs the user in, and the recovery path is a second key in a safe, not a mailed password.',
  'No memorized secret. You still need a way back if the device is lost.',
  'A badge with no keypad. You still need a plan when the badge is lost.')
g('Just-in-time privilege',
  'Just-in-time privilege grants admin rights for a short window and takes them back, instead of leaving them on forever.',
  'An engineer receives admin for two hours to fix a server, and the right disappears when the window ends.',
  'Admin for a little while, then it is gone.',
  'Borrowing the master key for one job and handing it back.')
g('Password vaulting',
  'Password vaulting stores shared or privileged secrets in a vault that checks them out, records who took them, and can rotate them.',
  'The database password is checked out of a vault for a change and rotated after, instead of living in a chat.',
  'Secrets live in a vault with a log.',
  'The spare key is signed out of a cabinet, not copied into a group text.')
g('Ephemeral credentials',
  'Ephemeral credentials are short-lived. When they expire, a stolen copy dies quickly.',
  'A cloud job receives a token that lasts minutes, not a permanent key in a file.',
  'A secret that dies soon.',
  'A visitor badge that expires at the end of the day.')

# --- 4.7 automation ---
g('Automated user provisioning',
  'Automated provisioning creates and removes accounts from a trusted source, such as the HR system, so access follows hiring and leaving.',
  'When HR marks a person as departed, the account disables the same day without a separate favor.',
  'Hiring and leaving drive the accounts.',
  'The roster at the door updates when the manager updates the staff list.')
g('Guard rails and security groups',
  'Guard rails stop a configuration that breaks a rule. Security groups limit who or what can talk.',
  'A template refuses a storage bucket that is world-readable, and a security group allows only the app tier.',
  'The system refuses the unsafe shape.',
  'A jig that will not let you drill the hole in the wrong place.')
g('Ticket creation and escalation',
  'Automation can open a ticket and escalate it when an alert fires, so the event is not only a line in a chat.',
  'A high-severity alert opens a ticket and pages the on-call person if nobody accepts it in fifteen minutes.',
  'The alert becomes a ticket with an owner.',
  'The bell writes itself into the book and calls the manager if nobody answers.')
g('Continuous integration and testing',
  'Continuous integration builds and tests every change, including security checks, before the change reaches production.',
  'A change that fails the secret-scan or the unit tests does not ship.',
  'Every change is built and tested first.',
  'Every new recipe is tasted in the test kitchen before the dining room sees it.')
g('Benefits of automation',
  'Automation applies the same safe steps every time, scales without adding the same number of people, and shortens the time to react.',
  'A baseline is enforced on a hundred laptops overnight, which a person could not click through before morning.',
  'The same safe steps, faster, and at a size people cannot click by hand.',
  'A dishwasher that washes every plate the same way.')
g('Complexity and technical debt',
  'Automation that nobody understands becomes debt. A pile of scripts with no owner fails in the incident.',
  'A deploy pipeline only one person can fix sits untouched while that person is on leave.',
  'If only one person understands it, it is a risk.',
  'A machine only one cook can run. When they are out, dinner stops.')
g('Single points of failure in automation',
  'A single automation server or a single pipeline can stop every change, or can push a bad change everywhere at once.',
  'The one orchestration host is backed up and restricted, because a compromise there is a compromise of every system it touches.',
  'The robot can fail, and the robot can spread a mistake.',
  'One mixer for the whole bakery. If it breaks, or if someone salts the bowl, every loaf is affected.')
g('Security content automation protocol',
  'The security content automation protocol is a family of standards for describing checks, results, and configuration so tools can share them.',
  'A benchmark result is expressed in a standard form the dashboard can read without a custom parser for each tool.',
  'A common language for check results.',
  'A standard order slip every kitchen in the chain can read.')
g('Benchmarks',
  'A benchmark is an agreed set of settings, such as a hardened build guide, that you measure systems against.',
  'New servers are scored against a published benchmark, and the gaps become tickets.',
  'An agreed checklist you measure against.',
  'The health inspection sheet you cook toward, not a private hunch.')
g('Agents and agentless checks',
  'An agent sits on the host and can see more. An agentless check reaches in from outside and sees less, and it needs a path that itself must be locked.',
  'Servers run an agent for file integrity. Network gear is checked remotely because it cannot run that agent.',
  'A helper on the box sees more. A visitor check sees less and needs a door.',
  'A thermometer in the soup versus looking through the pot lid.')

# --- 4.8 incident response ---
g('Preparation',
  'Preparation is the work before the incident: contacts, logs, backups, and a plan people have actually read.',
  'The on-call list and the backup restore steps are printed before anything is on fire.',
  'Get ready before the bad day.',
  'The fire extinguisher is checked on a quiet Tuesday.')
g('Detection',
  'Detection is noticing that something is wrong, from an alert, a person, or a log.',
  'A user report and an alert agree that files are changing names, and the incident starts.',
  'Notice that it is happening.',
  'Someone smells smoke and says so.')
g('Analysis',
  'Analysis decides what you are looking at, how far it reaches, and how bad it is, before you wipe the only evidence.',
  'The team lists the affected hosts from the logs before anyone reimages a machine.',
  'Figure out the size before you erase the scene.',
  'You look at which burners are on before you flood the kitchen.')
g('Containment',
  'Containment stops the spread while you keep what you need to understand it.',
  'The sick laptop is isolated from the network and left powered on.',
  'Stop the spread. Keep the evidence.',
  'Shut the kitchen door. Do not throw out the spoiled pot yet.')
g('Eradication',
  'Eradication removes the cause: the malware, the account, the scheduled job, the vulnerable setting.',
  'A malicious scheduled task is copied into the ticket and then removed, and the stolen account is disabled.',
  'Remove the cause, after you have recorded it.',
  'Throw out the spoiled stock after you have written down what it was.')
g('Recovery',
  'Recovery brings the service back from a clean point and watches to see if the cause returns.',
  'Files return from a backup taken before the encryption started, and the server is watched overnight.',
  'Come back from a clean point, and watch.',
  'Cook a fresh pot from good stock, and taste it before you serve.')
g('Lessons learned',
  'Lessons learned name a change you will actually make, with an owner, after the service is back.',
  'The review adds a backup test to the monthly checklist and names who will run it.',
  'A change, and a person, not a shrug.',
  'After the fire, you move the towels off the stove, and someone owns that job.')
g('Incident training',
  'Incident training teaches people their role before the night it happens, including who they call and what they do not touch.',
  'The desk practices reporting a suspicious mail without clicking, and they know the on-call number.',
  'Practice the role before the night.',
  'A fire drill on a calm day.')
g('Root-cause analysis',
  'Root-cause analysis looks for why the incident was possible, not only which file was bad.',
  'The malware arrived because a service account had standing admin and no multi-factor sign-in. That is the cause to fix.',
  'Ask why it was possible.',
  'The spill happened because the pot handle stuck out. Move the handle, not only the mop.')
g('Threat hunting',
  'Threat hunting looks for trouble that alerts have not named, using a hypothesis and the logs.',
  'An analyst searches for a rare scheduled-task pattern after a peer warning, before any alert fires.',
  'Go look, with a reason, before the alarm.',
  'Checking the locks at night because the street had a break-in, even though your alarm is quiet.')
g('Legal hold',
  'A legal hold stops the normal deletion of records that a case may need.',
  'Mail for three named people is kept past the usual retention because counsel said to hold it.',
  'Do not delete what a case may need.',
  'A note on the filing cabinet: do not shred this drawer.')
g('Chain of custody',
  'Chain of custody records who had the evidence, when, and what they did, so the story of the evidence stays trustworthy.',
  'A drive is labeled, hashed, and signed over to the next person, and it is not left on a desk overnight.',
  'Write down every hand that held it.',
  'A evidence bag with a signature each time it changes hands.')
g('Forensic acquisition',
  'Forensic acquisition copies evidence in a way that preserves it, usually with a hash, and works from the copy.',
  'The team images the disk, hashes the image, and investigates the image while the original sits sealed.',
  'Copy it cleanly, hash it, and work on the copy.',
  'Photograph the scene and take notes before you clean.')
g('Preservation and e-discovery',
  'Preservation keeps evidence unchanged. E-discovery is the organized search and production of electronic records for a case.',
  'A hold is in place and a scoped search exports the messages counsel asked for, without a fishing expedition through every mailbox.',
  'Keep it unchanged, and search only what was asked.',
  'Leave the filing cabinet locked, and pull only the folders the lawyer named.')

# --- 4.9 investigations ---
g('Firewall logs',
  'Firewall logs show what was allowed or denied, which is often the first place to see a scan or a blocked path.',
  'The deny log shows one internal host trying many ports on the database, which the host should never do.',
  'Who was allowed, and who was refused.',
  'The door log: who came in, and who was turned away.')
g('Application logs',
  'Application logs show what the app itself did: logins to the app, errors, and transactions.',
  'The billing app log shows a user exporting a report they have never run, at 03:00.',
  'The app\'s own diary.',
  'The order tickets, not the building\'s door log.')
g('Endpoint logs',
  'Endpoint logs show processes, files, and sign-ins on a specific computer.',
  'The laptop log shows a new process starting from a user\'s download folder just before the files changed.',
  'What that one computer did.',
  'The notebook on one desk, not the whole building.')
g('Operating-system security logs',
  'Operating-system security logs record authentication, privilege use, and policy changes.',
  'Windows Security or the Linux authentication log shows a burst of failures and then one success.',
  'The system\'s record of who signed in and who changed rights.',
  'The sign-in book at the staff door.')
g('Intrusion-detection logs',
  'Intrusion-detection logs record the patterns the sensor matched.',
  'The sensor log shows a known pattern aimed at the web server, and the analyst checks whether it was blocked or only seen.',
  'What the sensor thought it saw.',
  'The lookout\'s notebook: what they recognized.')
g('Network logs and metadata',
  'Network logs and metadata describe connections: who, where, when, and how much, even when you do not have the contents.',
  'Metadata shows a host talking to a new address every hour, which is enough to start a question.',
  'The fact of the conversation, even without the words.',
  'A call log without a recording. It is still a lead.')
g('Vulnerability-scan output',
  'Scan output is a list of possible flaws. Read the port, the evidence, and whether the host is exposed before you treat every line as an incident.',
  'A critical finding on a host that is powered off in a closet is not the same as the same finding on the public site.',
  'A list of maybes. Read the exposure.',
  'An inspection list. A chipped plate in storage is not a fire.')
g('Dashboards and automated reports',
  'Dashboards and automated reports summarize. They can hide a gap. Open the underlying record when the picture looks too calm or too wild.',
  'A green dashboard sits over a collector that stopped receiving logs yesterday.',
  'A summary. Check that the summary is still being fed.',
  'A "kitchen is fine" sign while the order printer is unplugged.')
g('Packet captures',
  'A packet capture is the traffic itself, or a faithful record of it. It is heavier than a flow record and it can contain secrets, so it is handled as evidence.',
  'A short capture on the server link shows a clear-text password on a protocol that should have been encrypted.',
  'The traffic itself. Treat it as sensitive.',
  'A recording of the conversation, which you lock up because it contains secrets.')

# --- 5.1 governance ---
g('Guidelines',
  'A guideline is recommended practice. It is not a rule you are fired for breaking, and it should not be written as if it were.',
  'A guide suggests a passphrase style. The standard is what audits measure.',
  'Advice, not the rule.',
  'A cookbook suggestion, not the health-code line.')
g('Policies',
  'A policy is management\'s rule: what must be true, who owns it, and what happens if it is ignored.',
  'The password policy is signed by leadership and names the consequence for sharing an account.',
  'The rule from the top, with an owner.',
  'The house rule posted by the owner.')
g('Standards',
  'A standard is the measurable setting that makes a policy real, such as a minimum passphrase length or a required cipher.',
  'The policy says "protect laptops." The standard says full-disk encryption on every laptop.',
  'The measurable version of the rule.',
  'The recipe\'s exact temperature, under the house rule "serve safe food."')
g('Procedures',
  'A procedure is the step-by-step way to do the job so two people get the same safe result.',
  'The new-hire procedure says who requests the account, who approves it, and which role is granted.',
  'The steps.',
  'The opening checklist, in order.')
g('Regulatory and legal considerations',
  'Regulatory and legal considerations are the laws and regulators that apply to your data and your sector.',
  'A clinic in one state handles records under that state\'s health rules and under a federal rule, and the stricter duty wins.',
  'Which laws apply here.',
  'The health inspector and the fire marshal both get a say.')
g('Industry and local considerations',
  'Industry rules and local rules can be stricter than a generic textbook, and they can differ by city or by sector.',
  'A payment merchant follows the card-brand rules on top of the company policy.',
  'Your industry and your town can add rules.',
  'A restaurant follows the city food code, not only the chain\'s poster.')
g('National and global considerations',
  'National and global considerations show up when data or staff cross a border and more than one country\'s rules apply.',
  'A support team in another country is not given a data set the home country\'s law says must stay home.',
  'Borders change the rules.',
  'A recipe you may sell at home and may not ship abroad.')
g('Monitoring and revising governance',
  'Governance is reviewed on a schedule and after incidents, so the paper does not drift away from the practice.',
  'After a phishing incident, the reporting procedure is rewritten and the old poster comes down.',
  'Reread the rules, and fix them when the world changes.',
  'The menu is reprinted when the kitchen stops serving a dish.')
g('Boards and committees',
  'Boards and committees give governance a place to be decided and recorded, instead of living in one person\'s head.',
  'A security steering group meets monthly, records decisions, and assigns owners.',
  'A group that decides and writes it down.',
  'A weekly owners\' meeting with minutes, not a chat rumor.')
g('Centralized and decentralized governance',
  'Centralized governance makes one body set the rules. Decentralized governance lets units set more of their own, which can fit local work and can create contradictions.',
  'One company standard for encryption exists, and a clinic may add a stricter local rule, not a weaker one.',
  'One rulebook, or many. Weaker local rules are not the goal.',
  'One chain menu, with a local special that is stricter about allergens, not looser.')
g('Data owners',
  'A data owner decides classification, access, and retention for a set of data. The owner is accountable even if others operate the system.',
  'The finance director owns the payroll data and approves who may export it.',
  'The person accountable for the data.',
  'The chef owns the recipe, even if a cook stirs the pot.')
g('Controllers and processors',
  'A controller decides why and how personal data is processed. A processor handles it for the controller, under instructions.',
  'The clinic decides why records exist. The hosted mail company processes mail only under the contract.',
  'One decides. One handles it for them.',
  'The restaurant decides the menu. The laundry only washes what it is given.')
g('Custodians and stewards',
  'Custodians and stewards take care of the data day to day: backups, access changes, and the systems. They do not own the business decision.',
  'IT restores the payroll database. Finance still decides who may have an export.',
  'They care for it. They do not own the decision.',
  'The night porter locks up. The owner still decides who gets a key.')

# --- 5.2 risk ---
g('Risk identification',
  'Risk identification names what could go wrong, to which asset, from which threat, through which weakness.',
  'The register lists "lost unencrypted laptop" against the customer list, not a vague "cyber risk."',
  'Name the bad outcome in plain words.',
  'Write "the walk-in can fail," not "kitchen problems."')
g('Ad hoc, recurring, and continuous assessment',
  'Assessments can be one-time, on a schedule, or continuous. A one-time look does not replace a recurring one, and a tool that watches every day is still not a decision.',
  'A new clinic gets a one-time assessment, and the same checklist returns every quarter.',
  'Once, on a schedule, or all the time. Do not pretend once is enough.',
  'A grand opening inspection, a quarterly visit, and a thermometer that stays in the fridge.')
g('Qualitative risk analysis',
  'Qualitative analysis uses scales such as high, medium, and low when you do not have solid numbers.',
  'A lost badge is rated high impact and low likelihood after the revoke process improved.',
  'Words on a scale, when dollars are a guess.',
  'Calling a spill "a big mess" when you cannot price it yet.')
g('Quantitative risk analysis',
  'Quantitative analysis uses numbers: how often, how much is lost, and what that costs per year.',
  'The team estimates events per year and loss per event for laptop theft, then compares the cost of encryption.',
  'Numbers, when you can defend them.',
  'Pricing the spoiled stock instead of only saying it was bad.')
g('Single loss expectancy',
  'Single loss expectancy is the expected loss from one event: the asset value times the portion you expect to lose.',
  'A laptop worth little hardware holds data whose exposure is the real single loss.',
  'What one event costs.',
  'The cost of one burned dinner, not the cost of the stove.')
g('Annualized loss expectancy',
  'Annualized loss expectancy is the single-event loss times how many times a year you expect the event.',
  'A small loss that happens weekly can outrank a large loss that happens once a decade.',
  'One event\'s cost, times how often.',
  'A small spill every service costs more in a year than one rare flood.')
g('Annualized rate of occurrence',
  'The annualized rate of occurrence is how many times a year you expect the event.',
  'Phishing clicks are estimated at several a year. A flood of the server room is estimated far under one.',
  'How often, per year.',
  'How many times a year the fridge door is left open.')
g('Impact and likelihood',
  'Impact is how bad. Likelihood is how probable. Risk conversations need both, or everything looks "critical."',
  'A public website defacement is high visibility and, after the patch, lower likelihood than it was last quarter.',
  'How bad, and how likely. Both.',
  'A burned roast is bad. How often you leave the oven unattended decides the risk.')
g('Risk register',
  'A risk register is the list of risks, each with an owner, a rating, a response, and a review date.',
  'The unencrypted-laptop risk has an owner, a mitigation, and a date to check that encryption is actually on.',
  'A list with owners and dates.',
  'The repair list on the wall, with a name next to each item.')
g('Risk owners and thresholds',
  'A risk owner is accountable for the response. A threshold is the level that must be escalated instead of handled quietly.',
  'Anything rated high is reported to the steering group. Lower items stay with the named owner.',
  'A person, and a line that forces a bigger conversation.',
  'The cook owns small spills. A flood is called upstairs.')
g('Risk tolerance and appetite',
  'Appetite is how much risk leadership wants to seek. Tolerance is how much variation they will accept around that.',
  'Leadership will not accept unencrypted customer data, and they will accept a short delay on a low finding in a lab.',
  'How much risk they want, and how much wobble they will allow.',
  'How spicy the house cooks, and how far a dish can drift before it is sent back.')
g('Transfer, accept, avoid, and mitigate',
  'You can transfer risk (often by insurance or contract), accept it in writing, avoid the activity, or mitigate it with a control.',
  'The team mitigates laptop theft with encryption, transfers some residual risk with insurance, and does not merely ignore it.',
  'Share it, live with it on paper, stop the activity, or reduce it.',
  'Insure the van, accept a scratch, stop delivering, or add a better lock.')
g('Exemptions and exceptions',
  'An exemption waives a requirement. An exception allows a temporary miss. Both are written, owned, and dated.',
  'A device that cannot meet the screen-lock standard has a ninety-day exception and a locked cabinet as compensation.',
  'A written waiver or a dated miss. Not a quiet skip.',
  'A signed note that one fridge may run warm for a week, with a plan.')
g('Risk reporting',
  'Risk reporting tells decision makers the current risks, the trend, and the decisions they need to make.',
  'A quarterly report shows three risks past their review date and asks for a decision on one of them.',
  'Tell the people who can decide, while they can still decide.',
  'A Friday note: two repairs overdue, one choice only the owner can make.')
g('Business impact analysis',
  'A business impact analysis asks which processes matter, how fast they must return, and how much data loss is tolerable.',
  'Scheduling must return in four hours. The newsletter can wait a day. The analysis says so before the outage.',
  'Which work matters, how fast it must return, and how much loss you can stand.',
  'Dinner service cannot stop. The catering brochure can wait.')
g('Recovery time and recovery point',
  'Recovery time is how long you can be down. Recovery point is how much recent work you can afford to lose.',
  'A four-hour recovery time and a one-hour recovery point mean the spare must be ready and the copies must be frequent.',
  'How long you can be down, and how much recent work you can lose.',
  'How long the kitchen may be dark, and how many recent orders you can remake.')
g('Mean time to repair and between failures',
  'Mean time to repair is how long a fix takes on average. Mean time between failures is how long you typically run before something breaks.',
  'A disk array fails rarely and takes a day to rebuild, which belongs in the capacity plan.',
  'How long fixes take, and how long you usually last between breaks.',
  'How often the oven dies, and how long the repair truck takes.')

# --- 5.3 third parties ---
g('Vendor penetration testing',
  'Vendor penetration testing is a scoped attempt to break in, with permission, often required by contract or used to test a vendor.',
  'The contract lets you see a current test summary from the vendor, not their raw customer data.',
  'A permitted break-in test, scoped and reported.',
  'A hired inspector who tries the locks, with a letter that says they may.')
g('Right to audit',
  'A right to audit is a contract term that lets you check the vendor\'s controls, or accept an independent report in its place.',
  'The contract allows an audit or a current independent report before the renewal.',
  'You may look, or you may accept a trustworthy look by someone else.',
  'You may inspect the laundry, or accept the health certificate.')
g('Independent assessments',
  'An independent assessment is a review by someone who is not the vendor\'s sales team.',
  'A current independent report is read for exceptions, not just for the logo on the cover.',
  'Someone outside the vendor looked, and you read the exceptions.',
  'A health inspection, not the restaurant\'s own poster.')
g('Supply-chain analysis',
  'Supply-chain analysis asks who is upstream of your vendor and what happens if that upstream party fails or is compromised.',
  'The badge vendor depends on one chip supplier, and the team asks what a six-month delay would do.',
  'Look past the company you pay.',
  'Ask where the flour comes from, not only which bakery you bought the bread from.')
g('Vendor selection',
  'Vendor selection compares security, not only price, before the data moves.',
  'Two hosts are compared on encryption, logging, and exit terms, and the cheaper one loses because it cannot meet the standard.',
  'Choose with security in the score, before the data moves.',
  'You taste and you check the kitchen before you sign the catering contract.')
g('Vendor monitoring',
  'Vendor monitoring continues after the signature: incidents, reports, access reviews, and whether the service still matches the contract.',
  'A quarterly review checks who at the vendor still has admin access to the clinic tenant.',
  'Keep watching after you sign.',
  'You still visit the laundry after the contract starts.')
g('Questionnaires',
  'A questionnaire asks the vendor about controls. Answers are a start, not proof. Contradictions are worth a follow-up.',
  'A vendor claims encryption everywhere, and the contract exhibit shows an old clear-text transfer. The team asks.',
  'Questions are a start. Check the contradictions.',
  'A catering form that says "we refrigerate." You still look at the fridge.')
g('Rules of engagement',
  'Rules of engagement say what a test or a vendor may do, what is off limits, and who to call if something breaks.',
  'A test may scan the public site and may not touch the life-safety network, and the on-call number is on the first page.',
  'What is allowed, what is forbidden, and who to call.',
  'The inspector may open the fridge and may not turn off the walk-in during service.')
g('Service-level agreements',
  'A service-level agreement sets measurable expectations such as uptime, response time, and what happens when they are missed.',
  'The mail host owes a response within an hour for a severity-one incident, and the miss has a credit the team actually tracks.',
  'A measurable promise.',
  'The laundry promises same-day return, and you notice when they miss.')
g('Memoranda of agreement and understanding',
  'A memorandum of agreement is a cooperative commitment. A memorandum of understanding records a shared intent. Neither replaces a contract when money and data duties are serious.',
  'Two clinics share a memo about a drill, and the actual data sharing sits in a contract.',
  'A handshake on paper. Use a real contract for data and money.',
  'A note that two shops will share a parking lot, not the deed.')
g('Master service agreements and statements of work',
  'A master agreement sets the standing legal terms. A statement of work sets the specific job, dates, and deliverables.',
  'The master terms cover confidentiality, and this month\'s statement of work covers one network assessment.',
  'Standing terms, plus a page that says this job.',
  'The house account with the plumber, plus a note for this week\'s leak.')
g('Non-disclosure agreements',
  'A non-disclosure agreement limits how a party may share what they learn. It does not by itself make their security good.',
  'A vendor signs a non-disclosure agreement and still must meet the encryption standard. The signature is not the control.',
  'A promise not to blab. Not a security program.',
  'A promise not to copy the recipe. You still lock the kitchen.')
g('Business partnership agreements',
  'A business partnership agreement sets how two parties share work, risk, and duties, including security duties if you write them in.',
  'A joint clinic program spells out who patches the shared system and who reports an incident.',
  'Who does what, including the security chores.',
  'Two shops sharing a kitchen write down who cleans the walk-in.')

# --- 5.4 compliance and privacy ---
g('Internal and external compliance reporting',
  'Internal reporting tells leadership the truth. External reporting tells a regulator, a customer, or a partner what the rules require, on time.',
  'A breach clock starts, and counsel decides what external notice is due while leadership gets the internal facts the same day.',
  'Tell your own leaders, and tell outsiders when the rule says so.',
  'You tell the owner tonight and the inspector in the morning if the rule says morning.')
g('Fines and sanctions',
  'Fines and sanctions are official penalties for breaking a rule. They are a consequence, not the reason to protect people.',
  'A missed notification deadline can bring a fine, which the team treats as a clock, not as the whole duty.',
  'The official penalty. The duty is larger than the fine.',
  'A citation. You still feed people safely because it is the job.')
g('Reputational damage',
  'Reputational damage is the loss of trust after people learn you were careless.',
  'Patients leave after a public breach even though the fine was small.',
  'People stop trusting you.',
  'The dining room empties after one bad night is in the paper.')
g('Loss of license',
  'Loss of license means a regulator or a partner can stop you from operating or from taking a kind of payment.',
  'A payment processor can cut off card processing if the card-data rules are ignored.',
  'Someone with authority can shut the door.',
  'The health department can close the kitchen.')
g('Contractual impacts',
  'Contractual impacts are the duties and penalties in your contracts: notice, credits, or the right to walk away.',
  'A customer contract requires notice within seventy-two hours, which is tighter than the team\'s old habit.',
  'The contract can be stricter than your habit.',
  'The catering contract says you call the client the same day, not next week.')
g('Due diligence and due care',
  'Due diligence is looking carefully before you commit. Due care is the ongoing careful operation after you commit.',
  'The team reviews a vendor before signing, and then keeps patching after the system is live.',
  'Look before you leap, and keep being careful after.',
  'You inspect the kitchen before you hire, and you keep it clean after.')
g('Attestation and acknowledgement',
  'Attestation and acknowledgement are people or vendors formally saying they understand a rule. A signature is not proof they follow it.',
  'Staff acknowledge the phishing procedure annually, and the team still measures whether they report the simulations.',
  'They signed. You still check the behavior.',
  'A signed "I read the hygiene card" is not a clean cutting board.')
g('Data subjects',
  'A data subject is the person the data is about. They can have rights to know, to correct, and sometimes to delete.',
  'A patient asks for a copy of their record, and the request goes to the owner of that process, not into a random ticket.',
  'The person the data is about.',
  'The diner the reservation names. The card is about them.')
g('Right to be forgotten',
  'The right to be forgotten, where it applies, means deleting a person\'s data when the law says you must, including copies, unless an exception applies.',
  'A deletion request is checked against a legal hold before anyone wipes a mailbox.',
  'Delete when the law says so, unless a hold or another duty says keep.',
  'Throw out the old reservation, unless the lawyer said to keep that book.')
g('Data inventory and retention',
  'A data inventory says what you have, where it is, and how long you keep it. Retention without an inventory is a guess.',
  'The team finds a forgotten export of patient names on a file share and either protects it or deletes it under the schedule.',
  'Know what you have, where it sits, and when it goes.',
  'A list of every jar in the fridge and a date on each lid.')

# --- 5.5 audits ---
g('Internal audits',
  'An internal audit is your own organization checking itself, which is useful and is not a substitute for an outside look when one is required.',
  'An internal audit finds badge reviews are late, and the finding is tracked like any other.',
  'You check yourself. It still counts as a finding.',
  'The cook tastes the soup. A finding is still a finding.')
g('External audits',
  'An external audit is an outside party checking your controls or your books against a standard.',
  'An outside auditor asks for evidence of access reviews, not for a slide that says "we do security."',
  'An outsider checks the evidence.',
  'The inspector wants the temperature log, not a speech.')
g('Regulatory examinations',
  'A regulatory examination is a regulator looking at whether you meet the law, with consequences if you do not.',
  'The team produces the breach procedure and the last drill record when the examiner asks.',
  'The regulator is in the room.',
  'The fire marshal, not a friendly consultant.')
g('Penetration test types',
  'Penetration tests can be physical, technical, or both, and they are scoped attempts to find and show impact, with permission.',
  'A test includes a phishing note and a visit to the lobby, because the scope said both.',
  'A permitted attempt to get in, of a named kind.',
  'A hired person tries the front door, the alley, or both, because the letter said so.')
g('Known, partial, and unknown environments',
  'A known environment gives the tester inside information. A partial one gives some. An unknown one gives little, like an outsider. Each answers a different question.',
  'An unknown-environment test shows what a stranger can do. A known-environment test shows what a stolen admin laptop can do.',
  'How much the tester is told changes the question being asked.',
  'A stranger at the door, a delivery driver who knows the alley, or an employee. Three different tests.')
g('Offensive and defensive testing',
  'Offensive testing tries to get in. Defensive testing watches whether detection and response catch the attempt. Integrated tests do both.',
  'The same week, a tester sends a payload and the blue team is scored on whether they saw it and contained it.',
  'One side tries. The other side must notice.',
  'Someone tries the back door while you score whether the bell rang.')
g('Physical penetration tests',
  'A physical test tries doors, badges, tailgating, and locks, with permission and safety rules.',
  'A tester tailgates into the lobby and stops at the point the rules of engagement named.',
  'They try the building, safely, with permission.',
  'Someone hired to see if they can walk into the kitchen, and they stop where the letter says.')

# --- 5.6 awareness ---
g('Phishing campaigns',
  'A phishing campaign in awareness is a planned, safe test that teaches people to notice and report, not a trick to shame them.',
  'A monthly exercise uses a harmless lookalike, and the people who report it are thanked.',
  'A safe practice phish. Praise the report.',
  'A fire drill. You do not scold the person who pulls the alarm.')
g('Recognizing and reporting suspicious messages',
  'Recognizing and reporting means the person spots the oddity and uses the report path, without clicking and without investigating alone.',
  'A clerk uses the report button on a payroll lookalike and does not forward the attachment around the office.',
  'Spot it, report it, do not poke it.',
  'You tell the manager about a strange package. You do not open it in the break room.')
g('Anomalous behavior',
  'Anomalous behavior is a person or a system acting unlike their baseline: risky, unexpected, or simply a mistake.',
  'A quiet accountant starts emailing large files at midnight, and a peer asks rather than accusing.',
  'They stopped acting like themselves. Ask.',
  'A regular cook suddenly takes the till into the alley. You ask.')
g('User guidance and training',
  'Guidance and training teach the few behaviors that matter: how to report, how to handle data, and when to stop and ask.',
  'New hires practice the report button and the rule about found USB sticks in the first week.',
  'Teach the behaviors you actually need.',
  'Show the new cook the handwash sink on day one.')
g('Password and removable-media habits',
  'Password habits mean unique long secrets and no sharing. Removable-media habits mean found drives are not plugged into work computers.',
  'A shared front-desk password is replaced with personal accounts, and a found stick is handed to security.',
  'Do not share secrets. Do not mount found drives.',
  'No shared till code on a sticky note, and no mystery pie from the alley.')
g('Social-engineering awareness',
  'Social-engineering awareness teaches people that urgency, authority, and friendliness are tools, and that a callback on a known number is the counter.',
  'A caller claiming to be the CEO is asked for a ticket, and the desk calls back on the number in the directory.',
  'Urgency is a tactic. Call back on a number you already trust.',
  'A stranger in a nice coat still does not get the safe combination.')
g('Operational security',
  'Operational security means not leaking useful details: system names, schedules, and badges, in public posts or lobby conversations.',
  'A job post no longer lists the exact door-controller model and the vpn hostname.',
  'Do not hand out the map.',
  'You do not post the alarm code on the hiring flyer.')
g('Hybrid and remote-work habits',
  'Hybrid and remote habits cover home networks, shoulder surfing in public, printing, and where company devices may go.',
  'A laptop is not left unlocked in a coffee shop, and home printing of records is not allowed.',
  'The office rules travel with the person.',
  'The till rules still apply when you count cash at the picnic table.')
g('Recurring awareness programs',
  'A recurring program repeats training and measurement. A single annual video that nobody can remember is not a program.',
  'Short monthly topics replace a once-a-year video, and the report rate is tracked.',
  'Keep teaching, and measure it.',
  'Handwashing is coached every week, not once at orientation.')
