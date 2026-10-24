# Launch handoff

What ships on the `refinement` branch, how to check it, and the manual steps left before a pilot.
All new content is tagged **Pending SME review**.

## Option B features (passes 1–3)

| Feature | Where | Notes |
|---|---|---|
| Exam-Day Readiness Simulator (student) | `/student/section/<id>/exam-sim` → start → `/student/section/<id>/exam-sim/<attempt>` → `/result` | 220-1201, 220-1202 and N10-009 forms; full or sprint; practice (pause allowed) or strict exam timing; PBQs first with "Skip PBQs & return later"; flag for review; scaled 100–900 score against the pass bar (675 / 700 / 720); badge Ready / Borderline / Needs remediation with lesson and ladder-rung links per weak domain. |
| Exam-Day Readiness Simulator (instructor) | `/instructor/section/<id>/exam-sim` | Every sitting in the section with score, badge, domains and flags. Students get 403. |
| Stateful Windows 11 / Cisco IOS engine | All 66 Windows/IOS command labs | Fallback commands (`ipconfig`, `Get-NetIPConfiguration`, `show running-config`, `show vlan brief`, `show cdp neighbors`, `write memory` …) answer from the lab's live state, so the output changes as the student fixes the fault. |
| Packet / Frame Walk | 49 network labs (e.g. `/labs/sw-vlan-access`) | ARP, ICMP, DNS and HTTPS walks hop by hop over the live topology; while the fault is present the walk stops at the failing hop. JSON at `/labs/<lab>/packet-flow?type=…`. |
| SVG hardware / cable bench | `hw-board`, `hw-pc-build` (board mode) and `hw-cables` (cable mode) | Drag-free SVG bench: board components and T568A/T568B straight, crossover and split-pair wiring. No inline styles. |
| Bespoke explanation ladders | All 539 sections (ITSUP 296, NETOPS 154, CLIENT 89) | Every section has its own R1 plain / R2 analogy (with analogy map and "Where the analogy breaks") / R3 SVG visual (`aria-label`) / R4 widget + lab rung, with balanced quick checks tagged to same-chapter misconceptions. 0 `same_as`, 0 templated NETOPS sections. |

## Verification (run against a DB copy, never the real `ciwt_lms.db`)

```
cp ciwt_lms.db /tmp/ob3.db
./venv/bin/python tools/ladder_check.py --max-skips 0 --require-complete
DATABASE_URL=sqlite:////tmp/ob3.db ./venv/bin/python tools/curriculum_readiness.py /tmp/ob3_readiness   # 29/29
DATABASE_URL=sqlite:////tmp/ob3.db ./venv/bin/python tools/sme_priority_review.py                     # 0 / 0 / 0 / 0
DATABASE_URL=sqlite:////tmp/ob3.db ./venv/bin/python -m pytest -q tests/test_option_b_pass1.py \
  tests/test_option_b_pass2.py tests/test_option_b_pass3.py tests/test_prepilot_ux.py \
  tests/test_ladder_content.py tests/test_ladder_engine.py
```

`docs/SME_PRIORITY_REVIEW.md` reports 0 disputed items, 0 keys ≥ 1.15× the longest distractor across every item pool and ladder check, 0 `same_as` and 0 templated NETOPS sections.

## Manual steps before a pilot

- IdP / SSO test sign-in with a real institutional account.
- Domain and TLS for the production host.
- Production secrets (`SECRET_KEY`, mail, `NOVAK_CONTACT_EMAIL`) set outside the repo.
- SME review of every item and ladder marked **Pending SME review** (start with `docs/SME_PRIORITY_REVIEW.md`).
