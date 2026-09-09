"""Honest contact hours + extra teach for Chapters 2–13."""


def _h(title, body):
    return f'<section class="sublesson hours"><h3>{title}</h3>\n{body}\n</section>\n'


# chapter -> lesson -> minutes
MIN = {
    2: {1: 70, 2: 60, 3: 50, 4: 50, 5: 70, 6: 60},
    3: {1: 60, 2: 50, 3: 50, 4: 50, 5: 50},
    4: {1: 60, 2: 50, 3: 50, 4: 45},
    5: {1: 60, 2: 45, 3: 70, 4: 45, 5: 60},
    6: {1: 50, 2: 45, 3: 50, 4: 40},
    7: {1: 50, 2: 45, 3: 40, 4: 50},
    8: {1: 50, 2: 50, 3: 50, 4: 45},
    9: {1: 50, 2: 45, 3: 40, 4: 40},
    10: {1: 45, 2: 50, 3: 40, 4: 45},
    11: {1: 45, 2: 50, 3: 45, 4: 45},
    12: {1: 45, 2: 40, 3: 40, 4: 50},
    13: {1: 30, 2: 40, 3: 35, 4: 50, 5: 40, 6: 35},
}

EXTRA = {
    (2, 1): _h("Teach block — boards and boxes", """
<p>Spend a full period on form factor with a ruler if you have one. Students measure or read the card: 9.6 × 9.6 is microATX here. They name what you lose when you go Mini-ITX (slots, RAM count, GPU clearance) and what you gain (small case). Socket silkscreen is law. If the cooler does not match the socket, you do not “make it work.”</p>
<p>Worked miss: ordering “an ATX board for a small office PC” and receiving a full ATX that will not mount. The ticket should have listed the measured size and the socket.</p>
"""),
    (2, 5): _h("Teach block — three neighborhoods", """
<p>Draw three boxes on the board and keep them there all week: Power (no twitch, no LED), POST (beep/LED/codes), Display (POST already OK). Every hardware ticket this course starts by pointing at one box. Mixing them is how a GPU gets replaced for unseated RAM.</p>
<p>Run hw-board to submit this period. Answers on this card: microATX, LGA1700, DDR5, NVMe, POST memory.</p>
"""),
    (2, 6): _h("Teach block — inventory is a document", """
<p>Students produce a four-line inventory on paper and in the ticket: name, edition/build, RAM the OS sees, disk handles from list disk. They do not image. They do not clean. If About and the chassis disagree, class stops and talks seating/firmware — not setup.exe.</p>
"""),
    (3, 1): _h("Teach block — words that order parts", """
<p>M.2 is the slot shape. NVMe is a protocol that often uses that slot. SATA M.2 exists. Ordering “an M.2” without protocol and length is how the wrong stick arrives. HDD vs SSD failure stories are different: click and not-ready versus silent death. list disk is the only diskpart verb this block allows.</p>
"""),
    (3, 2): _h("Teach block — RAID stories", """
<p>Work three tickets: user deleted a file (backup), one disk in RAID 1 died (array still up, replace disk, still not a backup), RAID 0 volume gone (data gone unless backup). Do not let the class leave thinking parity is a time machine.</p>
"""),
    (5, 1): _h("Teach block — four lines on the board", """
<p>Address. Mask. Gateway. DNS. Stay here until every trainee can point at an ipconfig /all dump and mark those four. Then mark APIPA. Then say which lecture is forbidden on APIPA (DNS).</p>
"""),
    (5, 3): _h("Teach block — isolation table until boring", """
<p>Four failed-ping stories, class points at the domain. Then they run win-ipconfig and win-dns-break. Anyone who flushdns on APIPA repeats the table.</p>
"""),
    (5, 5): _h("Teach block — full triage as a period", """
<p>This is not a five-minute demo. Every trainee completes win-full-triage with a note that has action → result. Firewall stays on. Capstone check after.</p>
"""),
    (6, 1): _h("Teach block — you may already be a guest", """
<p>Read About and inventory. Name the guest. Ask: if five guests died together, who owns the host? Do not let the class plan five NIC swaps.</p>
"""),
    (7, 1): _h("Teach block — process on a live sentence", """
<p>Take “the internet is down” and walk identify (one vs many), cheap test, one change. Forty minutes of that beats a slide of seven words.</p>
"""),
    (8, 1): _h("Teach block — install is a change", """
<p>Inventory first. MEM beep is not setup.exe. In-place vs clean on the board with data-risk in the middle. No clean in class.</p>
"""),
    (10, 2): _h("Teach block — phish and malware as tickets", """
<p>Two full notes: not opened, and password typed. Class scores secrets and labels. No live malware. No Defender off.</p>
"""),
    (11, 1): _h("Teach block — scope before repair", """
<p>One app / one profile / one PC / many PCs. Three raw tickets. No one is allowed to say “reimage” until they pick a scope out loud.</p>
"""),
    (12, 4): _h("Teach block — two stories, two domains", """
<p>MEM beep vs tenant mail down. Class picks the lab before they open it. Wrong lab is the miss.</p>
"""),
    (13, 4): _h("Teach block — name resolution gym", """
<p>Full period on win-dns-break + win-full-triage. Same pass bar as 5.5. This chapter is reps, not new theory — give it time.</p>
"""),
}


def apply_hours_rest(pack):
    for ch in pack:
        if not isinstance(ch, dict):
            continue
        cno = ch.get("order")
        if cno not in MIN:
            continue
        total = 0
        for les in ch.get("lessons") or []:
            o = les.get("order")
            mins = MIN[cno].get(o)
            if mins:
                les["minutes"] = mins
                total += mins
            extra = EXTRA.get((cno, o))
            if extra:
                les["html"] = (les.get("html") or "") + extra
        if total:
            ch["minutes"] = total
    return pack
