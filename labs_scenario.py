"""Lab scenario mode: performance-based (PBQ-style) troubleshooting tickets that chain a real VM lab and a simulation.

A scenario is a ticket with stages. Each stage is a PBQ variant of an existing lab: same environment, same real grader,
but the objectives are not shown up front (the page shows 'hidden check N'), check results say only how many checks
pass, and the full objective list is revealed when the stage is resolved. Hints (two tiers, recorded) and the event
log work exactly as in the normal lab. Stage 2 unlocks when stage 1 is resolved; the hub shows time, hints, failed
checks and wrong turns per stage.
"""
from copy import deepcopy

SCENARIOS = [
    {
        "id": "SCN-DNS",
        "title": "Ticket SR-5307 — “The intranet is down for everyone”",
        "blurb": "Prove it is DNS from a user's Windows 11 PC (simulation), then fix the real resolver and client on two real Linux VMs.",
        "ticket": ("Reported 08:12 by the service desk: since this morning nobody on the 3rd floor can open the intranet or "
                   "external sites by name; the web proxy by IP still works. The intranet moved to a new server last week. "
                   "You have the reporting user's Windows 11 PC, and console access to the internal DNS server dns-01 and a "
                   "test workstation ws-22. Resolve the ticket: find the fault domain, fix it at the source, and verify."),
        "course_objectives": ["NO-4.2", "NO-6.1", "IT-13.2"],
        "minutes": 55,
        "stages": [
            {"id": "scn-dns-evidence", "base": "win-dns-break", "label": "Stage 1 · User's PC (Windows 11 simulation)",
             "brief": "Collect the evidence a second-line engineer will ask for, and decide whether this PC is the problem. "
                      "Do not change anything that is not broken."},
            {"id": "scn-dns-fix", "base": "linux-vm-dns", "label": "Stage 2 · DNS server and test client (2 real Linux VMs)",
             "brief": "Your evidence says the client is fine and names do not resolve. Fix name resolution end to end on "
                      "dns-01 and prove it from ws-22: internal names, the moved intranet, mail and internet names."},
        ],
    },
    {
        "id": "SCN-LAN2",
        "title": "Ticket NET-2207 — “LAN 2 has no network after Friday's change”",
        "blurb": "Fix a DHCP server and a router on two real Linux VMs, then bring the CFO's Windows laptop back (simulation).",
        "ticket": ("P2, raised Monday 07:55: every PC on LAN 2 shows 'No network' since Friday evening's change CHG-3317 on "
                   "the LAN 2 router. The ERP server (198.51.100.10, behind the core router 10.1.0.1) is unreachable from "
                   "LAN 2. The CFO's laptop must work before the 09:00 board meeting. You have the LAN 2 router rtr-2 "
                   "(it also serves DHCP) and a LAN 2 PC, pc-7, as real VMs, then the CFO's Windows 11 laptop."),
        "course_objectives": ["NO-4.1", "NO-6.1", "NO-6.3"],
        "minutes": 60,
        "stages": [
            {"id": "scn-lan2-fix", "base": "linux-vm-nettrouble", "label": "Stage 1 · LAN 2 router and PC (2 real Linux VMs)",
             "brief": "Restore LAN 2: PCs must get a working lease and reach the ERP server. Work one fault at a time and "
                      "verify the path hop by hop."},
            {"id": "scn-lan2-verify", "base": "win-dhcp-renew", "label": "Stage 2 · CFO's laptop (Windows 11 simulation)",
             "brief": "The network is fixed, but the CFO's laptop still holds what it got on Friday. Bring it back without a "
                      "reboot, and prove it reaches its gateway. Record the before state first."},
        ],
    },
]
SCN_BY_ID = {s["id"]: s for s in SCENARIOS}
STAGE_OF = {st["id"]: (s, i) for s in SCENARIOS for i, st in enumerate(s["stages"])}


def build(get_lab):
    """PBQ stage labs, derived from their base labs (same environment, grader, hints and solution)."""
    out = []
    for s in SCENARIOS:
        n = len(s["stages"])
        for i, st in enumerate(s["stages"]):
            base = get_lab(st["base"])
            if not base:
                continue
            lab = deepcopy(base)
            lab.update({
                "id": st["id"], "title": f"{s['id']} · {st['label']}", "pbq": True,
                "scenario": s["id"], "stage": i + 1, "stages": n, "base_lab": st["base"],
                "intro": s["ticket"] + " — " + st["brief"],
                "blurb": st["brief"], "builds_on": [],
                "success_msg": f"Stage {i + 1} of {n} resolved. " + (base.get("success_msg") or ""),
                "fallback": [],
            })
            lab["course_objectives"] = list(dict.fromkeys(list(s["course_objectives"]) + list(base.get("course_objectives") or [])))
            out.append(lab)
    return out


def masked_objectives(lab, objectives, complete):
    if not lab.get("pbq") or complete:
        return objectives
    return [dict(o, text=f"Hidden check {i + 1}") for i, o in enumerate(objectives)]


def pbq_message(lab, done):
    total = len(lab["objectives"])
    k = len([o for o in lab["objectives"] if o["id"] in done])
    return (f"Not resolved yet — {k} of {total} checks pass. The checks are hidden in a performance-based ticket; "
            "keep troubleshooting from the symptoms, or use Hint (recorded).")


def _turns(r):
    import json
    try:
        return list((json.loads(r.state_json or "{}") or {}).get("wrong_turns") or []) if r else []
    except ValueError:
        return []


def _mins(r):
    if not r or not r.started_at:
        return None
    end = r.completed_at or r.updated_at or r.started_at
    return max(1, round((end - r.started_at).total_seconds() / 60))


def status(s, rows):
    """rows: {lab_id: LabProgress row or None}. Per-stage status plus the ticket summary."""
    stages, prev_done = [], True
    for i, st in enumerate(s["stages"]):
        r = rows.get(st["id"])
        done = bool(r and r.completed_at)
        stages.append({**st, "n": i + 1, "row": r, "resolved": done, "unlocked": prev_done or done,
                       "score": round(max((r.best_score or 0), (r.score or 0))) if r else 0,
                       "hints": (r.hints_used or 0) if r else 0, "failed": (r.wrong or 0) if r else 0,
                       "turns": _turns(r), "minutes": _mins(r)})
        prev_done = done
    return {"stages": stages, "resolved": all(x["resolved"] for x in stages),
            "hints": sum(x["hints"] for x in stages), "failed": sum(x["failed"] for x in stages),
            "turns": [t for x in stages for t in x["turns"]], "minutes": sum(x["minutes"] or 0 for x in stages),
            "started": any(x["row"] for x in stages)}
