"""Ground-up teaching for people who have never done this job.
Prepended onto each chapter's first lesson (and key later lessons).
"""


def _s(title, body):
    return f'<section class="sublesson ground"><h3>{title}</h3>\n{body}\n</section>\n'


# Chapter 1 — start from zero
CH1 = "".join([
_s("Start here if you have never done this", """
<p>This course does not assume you have built a PC, worked a help desk, or taken a vendor exam. If the words motherboard, IP address, or ticket feel new, that is expected. Read this block slowly. The later chapters only work if these pictures are in your head.</p>
"""),
_s("What a computer is, in one picture", """
<p>A computer is a box that:</p>
<ol>
<li>Takes power from the wall</li>
<li>Has a brain (CPU) that follows instructions</li>
<li>Has short-term workspace (memory / RAM) that empties when power is gone</li>
<li>Has long-term storage (disk / SSD) that keeps files when power is gone</li>
<li>Talks to humans through a screen, keyboard, and pointing device</li>
<li>Often talks to other computers through a network</li>
</ol>
<p>If power never arrives, nothing else matters. If the brain cannot start, the disk can be healthy and you will still see a dark or beeping box. If memory is unseated, the brain may beep and never show Windows. Those neighborhoods are Chapter 2 and 3. You do not need them today. You need the picture.</p>
"""),
_s("What software is", """
<p>Hardware is the parts you can point at. Software is instructions. An <strong>operating system</strong> (Windows, macOS, a Linux desktop) is the big program that starts after firmware and then lets you run other programs: Outlook, a browser, a shop tool. An <strong>application</strong> is one of those other programs. A <strong>driver</strong> is a small program that teaches the OS how to talk to a specific device (a NIC, a printer).</p>
<p>When “the computer is broken,” you must learn to ask: power, hardware start, operating system, one application, or the network path to something else. Beginners treat all of those as one blob. This course splits the blob.</p>
"""),
_s("What a user actually brings you", """
<p>They do not bring you a layer of the OSI model. They bring a job they cannot finish: a report that will not send, a badge that will not open a door, a printer that will not print the watchbill. Your first sentence is that job, not a part name. Chapter 1.1 trains that sentence until it is boring.</p>
"""),
_s("What a ticket is", """
<p>A ticket is the written memory of the shop. You, sleep, and the next watch. If it is not in the ticket, it did not happen. Beginners write slogans (“VPN broken”). This chapter trains evidence: who, what outcome, tests and results, next person.</p>
"""),
_s("Words you will hear this week", """
<table class="port-table">
<tr><th>Word</th><th>Plain meaning</th></tr>
<tr><td>Outcome</td><td>What they must be able to do again</td></tr>
<tr><td>Break/fix</td><td>It used to work</td></tr>
<tr><td>Service request</td><td>They never had it</td></tr>
<tr><td>Incident</td><td>Bigger than one desk, or safety/security</td></tr>
<tr><td>Escalate</td><td>Hand to the owner who is allowed to finish it</td></tr>
<tr><td>Firmware / UEFI</td><td>Tiny software on the board that runs before Windows</td></tr>
<tr><td>POST</td><td>That firmware checking hardware before Windows</td></tr>
<tr><td>ESD</td><td>Tiny static shock that can kill chips; strap exists to prevent it</td></tr>
</table>
"""),
])

CH1_L2 = _s("Electricity you need as a technician, not as an engineer", """
<p>Wall power is dangerous. The PC power supply changes wall power into the lower voltages the board and drives use. You do not measure those voltages in this course unless a later shop SOP says so with the right meter and training. You <em>do</em> learn: unplug from the wall before you open a panel; do not open the supply itself; a hot outlet or a shock is an incident, not a “quick swap.”</p>
<p>Static electricity from your body can punch a hole in a chip you cannot see. The strap dumps that charge into the same ground as the mat and chassis. That is why the strap goes on skin, not over a hoodie.</p>
""")

CH1_L3 = _s("Why writing is part of the repair", """
<p>If you only fix the box and walk away, the shop has no memory. The next person repeats your work or makes it worse. Documentation is not extra. It is how a 24-hour shop exists.</p>
""")

# Chapter 2
CH2 = "".join([
_s("Start here — the parts inside the box", """
<p>Open the picture in your head before you open a panel. Inside a typical desktop:</p>
<ul>
<li><strong>Motherboard</strong> — the floor everything plugs into</li>
<li><strong>CPU</strong> — the brain, sits in a socket, needs a cooler</li>
<li><strong>RAM</strong> — short-term workspace, sticks in DIMM slots</li>
<li><strong>Storage</strong> — SSD or HDD, keeps files</li>
<li><strong>Power supply (PSU)</strong> — brick in the corner that feeds the board</li>
<li><strong>Case</strong> — metal that holds mounts and airflow</li>
</ul>
<p>A laptop has the same ideas in a tighter, often sealed box. You will not force a laptop apart in Chapter 1–2.</p>
"""),
_s("What “form factor” means if you have never heard it", """
<p>Form factor is the size and screw pattern of the board, and therefore which case it fits. It is not the brand name on the Amazon title. ATX is the common large desktop board. microATX is smaller (this course card is 9.6 × 9.6 in). Mini-ITX is smaller still. If the holes do not line up, you bought the wrong board, not “almost the right board.”</p>
"""),
])

CH2_L2 = _s("Firmware before Windows — from zero", """
<p>When you press power, the board does not jump into Windows. A tiny program stored on the board (UEFI / BIOS) runs first. It checks “is there a CPU, is there memory, can I see a disk” — that check is POST. Then it starts a bootloader, which starts the operating system.</p>
<p>If you never hear a beep and never see a manufacturer logo, you may still be in power or POST. If you see Windows, POST already succeeded. Beginners skip this and reinstall Windows on a box that never left POST.</p>
""")

CH2_L4 = _s("Memory from zero", """
<p>RAM is a workspace, not a filing cabinet. The filing cabinet is the disk. If RAM is missing or unseated, the brain often cannot even start the workspace, so you get beeps and no Windows. DDR4 and DDR5 are generations — the notch is in a different place so you cannot mix them without violence. Do not file the notch.</p>
""")

# Chapter 3
CH3 = "".join([
_s("Start here — files live on storage", """
<p>A file is a named pile of bytes: a document, a photo, Windows itself. Storage is where files sleep when the power is off. If the OS disk is dead or unplugged, the box cannot start Windows even if RAM and CPU are perfect. If the OS disk is fine and the user “lost a file,” that is often delete, a different folder, or no backup — not “buy a new SSD first.”</p>
"""),
_s("HDD, SSD, NVMe without the brochure", """
<p>An HDD is a spinning platter with a head. It can click. An SSD stores data in chips with no spinning parts. NVMe is a fast way for some SSDs to talk to the board, often as a short M.2 stick. M.2 is the shape of the slot. Not every M.2 stick is NVMe. You order both the shape and the protocol, plus the length.</p>
"""),
])

CH3_L2 = _s("Backup versus RAID from zero", """
<p>A backup is a second copy you can restore, preferably not only in the same box. RAID is a way to glue disks together for speed or to survive one disk dying. RAID does not undo “I deleted the budget folder” and does not undo ransomware. Beginners hear “we have RAID” and skip backups. That is how shops lose a week of work.</p>
""")

# Chapter 4
CH4 = _s("Start here — a laptop is still a computer", """
<p>Same ideas as the tower: power, brain, memory, storage, screen. Differences that bite beginners: the battery can swell and become a safety ticket; the power brick wattage must match what the chassis expects; parts are often sealed and named by service tag, not “a 15-inch screen.” Phones and tablets add radios (Wi-Fi, cellular) and sometimes a work profile (MDM) you do not wipe in a hallway.</p>
""")

# Chapter 5
CH5 = "".join([
_s("Start here — what a network is", """
<p>A network is more than one device sharing a path so they can exchange data. At home that path is often a small router plus Wi-Fi. At work it is switches, routers, cables, and wireless access points owned by a shop. You do not need to design that plant in Chapter 5. You need to read what one PC believes about the path.</p>
"""),
_s("Address, door, name — said slowly", """
<p><strong>IP address</strong> — the number this PC is using on the network, like a house number.</p>
<p><strong>Subnet mask</strong> — which part of that number is “this street” versus “this house.”</p>
<p><strong>Default gateway</strong> — the first door off this street. If you cannot reach the door, you are not leaving the LAN.</p>
<p><strong>DNS</strong> — the phone book from names people type (<code>mail.example.mil</code>) to numbers stacks route. If the number works and the name does not, you have a name problem, not “the internet is dead.”</p>
<p><strong>APIPA / 169.254.x.x</strong> — the PC gave itself a number because no one handed it a real lease. Do not start a DNS lecture here. Fix link and DHCP first.</p>
"""),
])

CH5_L2 = _s("What a port is if you have never heard it", """
<p>Think of the PC as a building. The IP address is the street address. A port is a numbered door on that building. Web often uses 80 or 443. DNS uses 53. Remote desktop often uses 3389. Ping does not knock on those doors. Ping only asks “does this address answer a small are-you-there.” Beginners ping a server, get a reply, and cannot understand why Outlook still fails. Different door.</p>
""")

# Chapter 6
CH6 = _s("Start here — virtual machines", """
<p>A virtual machine is a computer made of files sitting on another computer (the host). The Windows you type in on this bench may already be a guest. If the host is out of disk or the virtual cable is unplugged, every guest looks sick. You still inventory the guest first. You do not delete snapshots you do not own.</p>
""")

# Chapter 7
CH7 = _s("Start here — why a method exists", """
<p>Without a method, beginners change four things and cannot say what worked. The method is: name the outcome and the scope, pick the cheapest test that can kill a theory, change one thing, see whether the outcome is back, write it down. “Reimage” is not a method. It is an expensive last move.</p>
""")

# Chapter 8
CH8 = _s("Start here — Windows as the shop’s default client", """
<p>Most staff desks in this course run Windows. Install and repair of Windows are changes. They need inventory first (name, edition, disks). A box that never left POST does not need setup.exe. Update is part of the description of the box, not trivia.</p>
""")

# Chapter 9
CH9 = _s("Start here — other operating systems exist", """
<p>Linux and macOS are still “brain + memory + disk + network.” Commands are spelled differently. <code>ip a</code> is cousin to ipconfig. You are not a Linux admin after this chapter. You are someone who will not type <code>mkfs</code> as a first move and will not hallway-wipe a managed Mac.</p>
""")

# Chapter 10
CH10 = _s("Start here — security is part of the ticket", """
<p>Security is not a separate personality. Least privilege means you do not hand out admin because it is easier. A phishing mail is an incident when credentials were typed. Defender stays on. Passwords stay out of tickets. You isolate and hand off; you do not become a one-person incident-response team with a USB cleaner.</p>
""")

# Chapter 11
CH11 = _s("Start here — software problems have a scope", """
<p>One app on one profile is not a dead computer. Ask: this app only? this Windows profile only? this PC only? every PC? The answer picks repair versus network versus rebuild. Rebuild without backup is how shops lose files.</p>
""")

# Chapter 12
CH12 = _s("Start here — the shop is a system", """
<p>Change control, privacy, backup, and tickets are how a schoolhouse does not injure people or data. RAID is not backup. A snapshot is not off-site backup. Adding DNS after 1500 against policy is a change even if it “only takes a second.”</p>
""")

# Chapter 13
CH13 = _s("Start here — the lab guest is a real PC for this course", """
<p>You will type commands on a Windows guest. Inventory it first. Do not diskpart clean. The commands are spelled so a stranger can repeat them. This chapter is reps of Chapters 5 and 8, not a new theory dump.</p>
""")

FIRST = {
    1: CH1, 2: CH2, 3: CH3, 4: CH4, 5: CH5, 6: CH6,
    7: CH7, 8: CH8, 9: CH9, 10: CH10, 11: CH11, 12: CH12, 13: CH13,
}
OTHER = {
    (1, 2): CH1_L2,
    (1, 3): CH1_L3,
    (2, 2): CH2_L2,
    (2, 4): CH2_L4,
    (3, 2): CH3_L2,
    (5, 2): CH5_L2,
}


def apply_ground_up(pack):
    for ch in pack:
        if not isinstance(ch, dict):
            continue
        cno = ch.get("order")
        for les in ch.get("lessons") or []:
            o = les.get("order")
            chunks = []
            if o == 1 and cno in FIRST:
                chunks.append(FIRST[cno])
            extra = OTHER.get((cno, o))
            if extra:
                chunks.append(extra)
            if chunks:
                html = les.get("html") or ""
                # put ground-up right after the style/note so beginners see it first
                les["html"] = "\n".join(chunks) + html
    return pack
