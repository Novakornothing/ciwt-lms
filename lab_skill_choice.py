"""Per-lab decision cases for the activity and ticket labs.

Each lab has its own options. The generic act-now / schedule / confirm-change /
request bank is not used. The note states the case and the options. It does
not mark which option is correct.
"""
from __future__ import annotations

import lab_skills as SK

DEC = [("Decision", "one of the options written in the note")]
NET = [("Network address", "the first address of the block, not a host address")]


def add(lid, prose2, prose3, cases, syntax=DEC):
    def enrich(f, seed):
        i = int(seed) % len(cases)
        j = (i + 1) % len(cases)
        for step in range(1, len(cases) + 1):
            cand = (i + step) % len(cases)
            if cases[cand][1] != cases[i][1]:
                j = cand
                break
        f["assisted_case"], f["assisted_answer"] = cases[i]
        f["ticket_case"], f["ticket_answer"] = cases[j]
        f["options"] = ", ".join(dict.fromkeys(a for _, a in cases))

    def note(key):
        def run(f):
            return f"{f[key]}\nOptions: {f['options']}\nSubmit one option exactly."
        return run

    SK.SPECS[lid] = {
        "syntax": syntax,
        "enrich": enrich,
        "stages": {
            "assisted": {
                "checker": "decision", "prose": prose2, "note": note("assisted_case"),
                "fix": lambda f: [f["assisted_answer"]], "plant": lambda f: [],
                "checks": lambda f: [{"kind": "decision"}],
            },
            "ticket": {
                "checker": "decision", "prose": prose3, "note": note("ticket_case"),
                "fix": lambda f: [f["ticket_answer"]], "plant": lambda f: [],
                "checks": lambda f: [{"kind": "decision"}],
            },
        },
    }


add("ticket-intake",
    "The queue in front of you is not the mouse request from the walkthrough. Read the practice note, name the type, how many people are affected, and whether it escalates, using only the options the note lists.",
    "A second item arrived while the first was still open. It is a different kind of request. Classify that one. Do not reuse the practice line if the story changed.",
    (("One person wants a new mouse. Nothing is broken.", "request 1 no"),
     ("Half the badge readers stopped this morning.", "incident many yes"),
     ("A single user forgot a password and can wait.", "request 1 no"),
     ("The file server is down for every desk in the wing.", "incident many yes")))

add("hw-board",
    "The board on the bench is not the one from the walkthrough photo. Read the practice note and submit the form factor it describes.",
    "A second board is on the side bench. Submit the form factor for that description. The practice answer is about the other board.",
    (("Full tower rear I/O and four memory slots.", "atx"),
     ("Square, smaller than a tower board, not the tiniest square.", "microatx"),
     ("The small square used in the tiniest cases.", "mini-itx"),
     ("Full tower size with the current Intel desktop socket.", "atx")))

add("hw-cables",
    "The connector in the practice note is not the one you matched in the walkthrough. Submit the cable that fits that job.",
    "The incident note describes a different connector and a different job. Submit the cable for that one.",
    (("A console port on a switch, rolled pinout.", "rollover"),
     ("Two switches, gigabit, no fibre, 30 metres.", "cat6"),
     ("A fibre uplink between buildings.", "lc-fiber"),
     ("An older phone handset with four contacts.", "rj11")))

add("hw-pc-build",
    "The quote in the practice note is a different budget and a different workload than the walkthrough build. Submit the part the note's constraints allow.",
    "A second quote arrived with its own constraint. Submit the part for that quote.",
    (("CAD, ECC memory, tower case, 750 W.", "ecc-tower"),
     ("Thin client, no discrete GPU, 65 W.", "mini-pc"),
     ("The socket on the board is AM5 and the quote asks for the matching CPU.", "am5-cpu"),
     ("The case is mini-ITX and the quote lists an ATX board.", "reject-board")))

add("ticket-method",
    "The practice note is a fresh symptom, not the outage you ordered in the walkthrough. Submit the next step the story supports.",
    "The incident note is a second symptom with a different scope. Submit the next step for that story.",
    (("The user says nothing works, and you have not asked what changed.", "question"),
     ("You have a theory and have not tested it.", "test"),
     ("The test confirmed the theory and the user is still down.", "plan"),
     ("The fix is in and you have not checked the original symptom.", "verify")))

add("wifi-secure",
    "The router in the practice note is not in the state you left the walkthrough router. Submit harden or leave.",
    "The incident note describes a second radio. Submit harden or leave for that radio. Do not copy the practice decision.",
    (("WEP is on and WPS is enabled.", "harden"),
     ("WPA3, WPS off, a long passphrase.", "leave"),
     ("The guest network has no passphrase.", "harden"),
     ("Only the SSID text would change on an already WPA3 network.", "leave")))

add("sec-malware",
    "The pop-up in the practice note is a different moment than the walkthrough. Submit isolate, preserve, or document.",
    "The incident note is a later moment. Submit the action for those facts.",
    (("The user has not clicked the scareware pop-up.", "isolate"),
     ("The user closed the same pop-up yesterday and nothing else changed.", "preserve"),
     ("A shared drive was encrypted and a ransom note is in the folder.", "isolate"),
     ("A known toolbar was removed and a scan is clean.", "document")))

add("ops-backup",
    "The practice note describes a backup design. Submit accept or reject against a real second copy, a second medium, an off-site copy, and a tested restore.",
    "The incident note is a second design. Submit accept or reject for that design.",
    (("One copy on the same server as the original.", "reject"),
     ("A second disk, a monthly tape off site, and a restore last week.", "accept"),
     ("A USB drive in the same drawer as the laptop.", "reject"),
     ("Three copies, two media, one off site, and last month's restore opened.", "accept")))

add("virt-vm",
    "The practice note is a guest request. Submit the firmware and chip choice it implies.",
     "The incident note is a different guest. Submit the choice for that request.",
    (("Windows 11 with Secure Boot required.", "uefi-sb"),
     ("A legacy installer that only boots BIOS.", "bios"),
     ("The guest must attest with a virtual TPM.", "vtpm"),
     ("The guest is a Linux router and Secure Boot is not required.", "uefi-plain")))

add("mob-mdm",
    "The phone in the practice note is out of policy in a way the walkthrough device was not. Submit the action the note allows.",
    "The incident note is a second device. Submit the action for that device.",
    (("A corporate phone is not enrolled and the user wants email.", "enroll"),
     ("A personal phone is asking for the company VPN profile.", "refuse-vpn"),
     ("MDM says the corporate phone is jailbroken.", "wipe"),
     ("The corporate phone is enrolled and compliant and the user forgot the passcode.", "reset-passcode")))

add("sec-gpg",
    "The practice note describes one file and what should happen to it. Submit encrypt, decrypt, or refuse.",
    "The incident note is a second file. Submit the action for that file.",
    (("A spreadsheet of payroll must go to the accountant, who has published a key.", "encrypt"),
     ("You received a file encrypted to your key.", "decrypt"),
     ("A caller wants the private key emailed so they can decrypt.", "refuse"),
     ("The file is already encrypted to the right key and they want a second copy.", "leave")))

add("sec-win-fw",
    "The practice note proposes one firewall allow. Submit allow or deny.",
    "The incident note proposes a different allow. Submit allow or deny for that one.",
    (("Any source to TCP 3389.", "deny"),
     ("The jump host only, to TCP 22.", "allow"),
     ("Any source to TCP 445.", "deny"),
     ("The management subnet to TCP 443 on the admin console.", "allow")))

add("sec-win-policy",
    "The practice note is one account-policy change. Submit apply or reject.",
    "The incident note is a second policy change. Submit apply or reject.",
    (("Minimum length 4, because users complain.", "reject"),
     ("Lockout after 5 failures, 15 minutes.", "apply"),
     ("Maximum password age 10 years.", "reject"),
     ("Minimum age 1 day so a user cannot cycle back to the old password.", "apply")))

add("sec-win-events",
    "The practice note quotes one security event. Submit the triage word the note allows.",
    "The incident note quotes a second event. Submit the triage for that line.",
    (("4625 from the user's own desk, one failure, then a success.", "benign"),
     ("4625 from a country the user has never used, fifty times.", "investigate"),
     ("1102, the security log was cleared at 02:00.", "investigate"),
     ("4624, interactive logon at the console during the user's shift.", "benign")))

add("sec-acl",
    "The practice note describes one packet and one list. Submit pass or drop.",
    "The incident note is a second packet. Submit pass or drop. Order and direction are in the note.",
    (("First rule denies any, and a later rule would permit the host.", "drop"),
     ("First rule permits the host, and a later rule denies the subnet.", "pass"),
     ("The list is applied inbound and the packet is leaving.", "pass"),
     ("The list denies the source and is applied on the interface the packet enters.", "drop")))

add("sec-phish",
    "The practice note describes one message or one object. Submit report, refuse, or allow.",
    "The incident note is a second lure. Submit the action for that one.",
    (("The display name is Payroll and the address is a lookalike domain.", "report"),
     ("A caller wants a password read aloud.", "refuse"),
     ("A USB stick labeled salaries is in the parking lot.", "refuse"),
     ("A meeting reminder from the company calendar, link on the company domain.", "allow")))

add("sec-mfa",
    "The practice note describes one pair of factors. Submit counts or does-not-count.",
    "The incident note is a second pair. Submit counts or does-not-count.",
    (("A password and a PIN, both things the user knows.", "does-not-count"),
     ("A password and a hardware key.", "counts"),
     ("Two passwords stored in the same manager.", "does-not-count"),
     ("A fingerprint and a phone prompt.", "counts")))

add("sec-cert",
    "The practice note describes one browser warning. Submit the failure it names.",
    "The incident note is a different warning. Submit the failure for that warning.",
    (("The name on the certificate is not the name in the address bar.", "name"),
     ("The certificate expired last week.", "date"),
     ("The issuer is not in the trust store.", "issuer"),
     ("The certificate was revoked.", "revoked")))

add("sec-ir",
    "The practice note is a fresh incident. Submit the first move.",
    "The incident note is a second case. Submit the first move for that scope.",
    (("One laptop, the user has not clicked, the pop-up is still on screen.", "isolate"),
     ("A file server is encrypting shares right now.", "isolate"),
     ("The machine is already offline and you have not copied the volatile data.", "preserve"),
     ("The user is working and a scan finished clean after a toolbar removal.", "document")))

add("sec-risk",
    "The practice note gives a likelihood and an impact. Submit the bucket the note's words support.",
    "The incident note is a second risk. Submit the bucket for that pair.",
    (("Rare, and the impact is a full payroll outage.", "high"),
     ("Constant, and the impact is a misspelled footer.", "low"),
     ("Likely, and the impact is a day of lost orders.", "high"),
     ("Unlikely, and the impact is one user resetting a password.", "low")))

add("sec-vuln",
    "The practice note is one scan finding. Submit patch, mitigate, or accept.",
    "The incident note is a second finding. Submit the action for that finding.",
    (("Critical, on the payroll server, a fix exists.", "patch"),
     ("Critical, on a host with no route from the network, a fix exists.", "mitigate"),
     ("Low, on a lab printer, no fix, no data.", "accept"),
     ("High, on the VPN gateway, the vendor fix is a week away and a workaround exists.", "mitigate")))

add("sec-classify",
    "The practice note describes one collection of data. Submit the handling label.",
    "The incident note is a second collection. Submit the label for that collection.",
    (("Student grades on a file share.", "restricted"),
     ("A public event poster.", "public"),
     ("Staff home addresses.", "confidential"),
     ("The cafeteria menu.", "public")))

add("sec-arch",
    "The practice note describes a recovery site. Submit hot, warm, or cold.",
    "The incident note is a second site. Submit hot, warm, or cold for that design.",
    (("Data is current and the site is already running.", "hot"),
     ("Hardware is racked and the data is a day old.", "warm"),
     ("A contract for space, no hardware, backups in a box.", "cold"),
     ("The brochure says redundant and the data is restored only after a purchase order.", "cold")))

add("sec-vendor",
    "The practice note quotes one clause. Submit accept or renegotiate.",
    "The incident note quotes a second clause. Submit accept or renegotiate.",
    (("The vendor never says who reports a breach.", "renegotiate"),
     ("The vendor reports a breach within 72 hours and the data location is named.", "accept"),
     ("The vendor may use the data to train a model.", "renegotiate"),
     ("The vendor deletes the data at the end of the contract and says where it lived.", "accept")))

add("sec-zerotrust",
    "The practice note is one access request. Submit grant or deny.",
    "The incident note is a second request. Submit grant or deny. Being on the campus network is not a reason by itself.",
    (("The user is on the campus Wi-Fi and wants payroll, with no second factor.", "deny"),
     ("The user is off site, device is healthy, second factor succeeded, role includes payroll.", "grant"),
     ("A contractor wants the file server. The contract ended yesterday.", "deny"),
     ("The same user, healthy device, second factor, asking for the wiki their role includes.", "grant")))

add("sec-awareness",
    "The practice note is one message a colleague forwarded. Submit report, delete, or reply.",
    "The incident note is a second message. Submit the action for this one.",
    (("The link host is not the company and the display name is Payroll.", "report"),
     ("A newsletter the user subscribed to, from the publisher's own domain.", "delete"),
     ("The sender asks the user to reply with a password to confirm the account.", "report"),
     ("A calendar invite from the user's manager, on the company domain, for a meeting already on the calendar.", "reply")))

add("sec-iam",
    "The practice note describes how access is granted. Submit the model name.",
    "The incident note describes a second job. Submit the model for that job.",
    (("People are copied into a group that already has the rights for the job.", "rbac"),
     ("One shared password is taped under the keyboard.", "shared"),
     ("Each permission is attached to the person, with no role.", "dac"),
     ("A label on the file decides who may read it.", "mac")))

add("sec-change",
    "The practice note is one change someone wants tonight. Submit window, review, or stop.",
    "The incident note is a second change. Submit window, review, or stop.",
    (("The payroll database, during the day, no back-out plan.", "stop"),
     ("A tested printer driver, in the Sunday window, with a back-out.", "window"),
     ("An emergency, the trading system is down, and the change is the vendor's fix.", "review"),
     ("A cosmetic logo on the intranet, no window booked, no one affected if it waits.", "review")))

add("sec-indicators",
    "The practice note lists signals from one hour. Submit the one you would chase first.",
    "The incident note is a later hour. Submit the signal you would chase in that list.",
    (("A successful logon from the user's own desk.", "ignore"),
     ("A logon from a country the user has never used.", "chase"),
     ("A backup job that finished on schedule.", "ignore"),
     ("The security log was cleared.", "chase")))

add("sec-dlp",
    "The practice note describes data leaving by one path. Submit block or allow.",
    "The incident note is a second transfer. Submit block or allow.",
    (("A spreadsheet of account numbers, attached to a personal webmail.", "block"),
     ("A photo of the office dog, to a personal address.", "allow"),
     ("The customer list, copied to a USB stick.", "block"),
     ("A published price list, emailed to a customer who asked for it.", "allow")))

add("sec-privacy",
    "The practice note is one request about personal data. Submit fulfill, refuse, or narrow.",
    "The incident note is a second request. Submit fulfill, refuse, or narrow.",
    (("The person asks for a copy of their own record.", "fulfill"),
     ("A manager asks for a full mailbox export of a colleague.", "refuse"),
     ("A lawyer's letter asks for one customer's invoices, and the letter matches the file.", "narrow"),
     ("A stranger asks for the staff directory.", "refuse")))

add("sec-pentest",
    "The practice note is a scope statement. Submit in-scope or out-of-scope.",
    "The incident note asks to go past the first scope. Submit in-scope or out-of-scope.",
    (("The statement names the VPN and the tester wants the VPN.", "in-scope"),
     ("The statement names the VPN and the tester wants the payroll server, which is not named.", "out-of-scope"),
     ("The statement says production is excluded and the target is production.", "out-of-scope"),
     ("The statement names the three web servers and the tester is on the second of them.", "in-scope")))

add("sec-wireless",
    "The practice note describes one wireless choice. Submit the design word the note allows.",
    "The incident note is a second wireless decision. Submit the design for that one.",
    (("Guest traffic can reach payroll, and the only control is a longer passphrase.", "segment"),
     ("Guest traffic is on its own VLAN and cannot route to staff.", "leave"),
     ("The staff SSID is open.", "encrypt"),
     ("The staff SSID is WPA3 and guests are already segmented.", "leave")))

add("sec-logtriage",
    "The practice note asks one question. Submit which log you open.",
    "The incident note asks a different question. Submit the log for that question.",
    (("Who failed to log on.", "security"),
     ("Which process crashed.", "application"),
     (("A disk filled up.", "system")),
     ("A website returned 500.", "web")))

# fix the accidental nested tuple in sec-logtriage by re-registering cleanly
add("sec-logtriage",
    "The practice note asks one question. Submit which log you open.",
    "The incident note asks a different question. Submit the log for that question.",
    (("Who failed to log on.", "security"),
     ("Which process crashed.", "application"),
     ("A disk filled up.", "system"),
     ("A website returned 500.", "web")))

SK.SPECS["net-subnet"] = {
    "syntax": NET,
    "enrich": lambda f, seed: None,
    "stages": {
        "assisted": {
            "checker": "network-address",
            "prose": "The practice note gives an address and a prefix that are not the ones you already calculated. Submit only the network address for that prefix. A host address or a broadcast address will not match.",
            "note": lambda f: f"Address: {f['number_ip']}\nPrefix length: {f['number_prefix']}\nSubmit the network address only.",
            "fix": lambda f: [f["assisted_answer"]], "plant": lambda f: [],
            "checks": lambda f: [{"kind": "network-address"}],
        },
        "ticket": {
            "checker": "network-address",
            "prose": "The incident note is a second block, in a different range. Submit that network address. The practice network is a different block.",
            "note": lambda f: f"Address: {f['ticket_ip']}\nPrefix length: {f['ticket_prefix']}\nSubmit the network address only.",
            "fix": lambda f: [f["ticket_answer"]], "plant": lambda f: [],
            "checks": lambda f: [{"kind": "network-address"}],
        },
    },
}
