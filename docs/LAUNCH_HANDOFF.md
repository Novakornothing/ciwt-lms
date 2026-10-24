# CIWT LMS — launch handoff (24 Oct 2026)

Everything is on the local `refinement` branch (Option B pass 3; see `git log -1`). **Nothing has been pushed.** `ciwt_lms.db` was
never opened for writing; its sha256 is still `47fabc92dafe16cf128b34e90c8235d61d02bc735738a83b8a6172fb93597939`.
All new curriculum-facing content is tagged **Pending SME review**.

## Option B features (passes 1–6, Pending SME review)

| Feature | Where | Notes |
|---|---|---|
| Exam-Day Readiness Simulator (student) | `/student/section/<id>/exam-sim` → start → `/student/section/<id>/exam-sim/<attempt>` → `/result` | 220-1201, 220-1202 and N10-009 forms; full or sprint; practice (pause allowed) or strict exam timing; PBQs first with "Skip PBQs & return later"; flag for review; scaled 100–900 score against the pass bar (675 / 700 / 720); badge Ready / Borderline / Needs remediation with lesson and ladder-rung links per weak domain. |
| Exam-Day Readiness Simulator (instructor) | `/instructor/section/<id>/exam-sim` | Every sitting in the section with score, badge, domains and flags. Students get 403. |
| Stateful Windows 11 / Cisco IOS engine | All 66 Windows/IOS command labs | Fallback commands (`ipconfig`, `Get-NetIPConfiguration`, `show running-config`, `show vlan brief`, `show cdp neighbors`, `write memory` …) answer from the lab's live state, so the output changes as the student fixes the fault. |
| Packet / Frame Walk | 49 network labs (e.g. `/labs/sw-vlan-access`) | ARP, ICMP, DNS and HTTPS walks hop by hop over the live topology; while the fault is present the walk stops at the failing hop. JSON at `/labs/<lab>/packet-flow?type=…`. |
| SVG hardware / cable bench | `hw-board`, `hw-pc-build` (board mode) and `hw-cables` (cable mode) | Drag-free SVG bench: board components and T568A/T568B straight, crossover and split-pair wiring. No inline styles. |
| Bespoke explanation ladders | All 539 sections (ITSUP 296, NETOPS 154, CLIENT 89) | Every section has its own R1 plain / R2 analogy (with analogy map and "Where the analogy breaks") / R3 SVG visual (`aria-label`) / R4 widget + lab rung, with balanced quick checks tagged to same-chapter misconceptions. 0 `same_as`, 0 templated NETOPS sections. |
| Exam simulator pass 5 (integration) | Mastery, Why, Portfolio, instructor simulator page | Submitted sittings are mastery evidence (kind `exam_sim`, weight 0.85; each item maps back to its course objective). "Why this student is struggling" shows an `Exam Sim (code): score/900 · status (weak: domain)` pill; a remediation or weak-domain sitting adds the weakest domain to "Where stuck", links to the student's result (staff read-only view) and raises severity on Who needs me. `/portfolio` lists the best VOUCHER READY (else latest) sitting per exam, and `/portfolio/export.json` carries a VOUCHER READY OpenBadges assertion. The class page has **Export Scores CSV** (`/instructor/section/<id>/exam-sim/export.csv`) and **Sync Latest Exam-Sim Scores to Gradebook / LTI** (`POST …/sync-gradebook`: `exam_sim_grade` line items, plus an AGS column per exam when the LMS granted line-item and score scopes). |
| Exam simulator pass 6 (polish) | Sim PBQs, gradebook, outcomes, take page, landing | All 9 simulation PBQs map to a curated course objective (SIM-N-1 NO-2.2, N-2 NO-9.2, N-3 IT-5.1, A1-1 IT-5.2, A1-2 IT-3.1, A1-3 IT-3.4, A2-1 IT-8.2, A2-2 IT-11.1, A2-3 IT-10.2), so they record mastery on that objective and remediation links the matching R1 ladder section. Synced `exam_sim_grade` rows show as an **Exam Sim** column in the instructor gradebook (`220-1202: 774/900 (VOUCHER READY)`), as `Exam-Day Simulator <code>` columns in `gradebook.csv` and as a card on the student grades page; the weighted course grade is unchanged. The outcomes report (HTML, CSV, JSON) adds **Exam-Day Simulator & Voucher Readiness** per exam and overall (sittings, candidates, VOUCHER READY count/% on best sitting, mean latest scaled score; drills excluded). Single/multi options shuffle deterministically per sitting (`Random(f'{attempt_id}:{i}:{item}')`). Keyboard shortcuts: ←/→ or N/P, 1–6 select, F flag, W whiteboard (ignored while typing). The landing page has a **What Sets Novak LMS™ Apart** section (5 pillars). |
| Pass 7 audit fixes | Remediation, drill, Speed-Drill, outcomes | `remediation()` now puts first the lesson whose ladder section is tagged with the sim's course objective (previously SIM-N-2 and SIM-A2-1 linked only unrelated sections and SIM-N-1's first link was off-topic); all 9 sims now open their own R1 section. The missed-objective drill falls back to the weakest domain if the missed objectives have no single/multi items. Speed-Drill: the Blitz clock running out during feedback no longer redraws a card; keyboard keys (1–4, Enter, G, R); the ticking clock is no longer inside an aria-live region. Outcomes JSON carries a `basis` note per exam (VOUCHER READY = best sitting, mean = latest sitting). |
| Partial credit, ADA time, candidate agreement | `curriculum_v2/cert/exam_sim.py` | Scaled score = `scaled(earned, possible)` from `earned_and_possible()`: a k-part PBQ is worth k points, one per sub-part; domain % uses the same points; `att.correct` still counts fully right questions. Leads/TAs set **Time Accommodations (ADA / Section 504)** per student (1.0×, 1.25×, 1.5×, 2.0×; table `exam_sim_accommodation`, covered by `/my-data` export/delete); the multiplier applies to every new sitting and drill and shows as "1.5× time accommodation applied — 135 min". The clock does not start until the candidate selects **I Agree — Start Exam Clock** on the Candidate Agreement & Exam Instructions card (`POST …/begin`); a direct submit or auto-save starts it automatically. |
| Exam simulator pass 4 (testing-centre realism) | `/student/section/<id>/exam-sim` | Three lengths: Official 90 questions / 90 min / 5 PBQs (`max`), Standard 45 / 90 min / 4 PBQs, Sprint 15 / 20 min / 2 PBQs. One-question-at-a-time view by default (Previous / Next / Question X of N / Review Screen; practice mode can switch to the scroll view, exam mode cannot). Server auto-save (`POST …/exam-sim/<attempt>/autosave`, debounced on every change and navigation) restores answers, flags and the whiteboard on refresh or another device. Practice pause is server-side (`POST …/pause`): remaining seconds are frozen and the deadline moves forward on resume. In exam mode a late submit grades the answers auto-saved before deadline + 30 s instead of zeroing them. |
| Interactive simulation PBQs | 9 `sim_pbq` items (3 each for 220-1201, 220-1202, N10-009) in `curriculum_v2/cert/sim_pbq.py` | Open every sitting. Tabs: read-only diagnostic terminal (`show vlan brief`, `show ip route`, `show access-lists`, `ipconfig /all`, `Get-Service`, `icacls` …), clickable topology / board diagram, config inspector; then 3–4 remediation sub-fields. All-or-nothing for the score, "n/m parts right" in feedback. |
| Whiteboard and eliminator | Exam-sim take page | "Whiteboard / Scratchpad" side drawer (auto-saved and kept in sessionStorage) with "Insert CIDR / Binary Grid" (128…1 and /24–/30 table). Strike-out button on every single/multi option, also Alt+Click or right-click. |
| Candidate Score Report + missed-objective drill | Exam-sim result page | Printable report (name, section, exam code and version, date/time, mode, simulated scaled score, pass bar, VOUCHER READY / BORDERLINE / REMEDIATION REQUIRED, domain bars, missed objective codes). "Drill My Missed Objectives Now (10 questions)" (`POST …/remediate-drill`) starts a 10-question practice sitting from the missed objectives (weakest domain if nothing was missed). |
| Speed-Drill | `/student/section/<id>/speed-drill` (linked from the section page, simulator home and results) | 98 cards: ports & protocols, IEEE/Wi-Fi/cable/hardware specs, Windows/Linux/IOS commands, acronyms and security/cloud concepts, filterable by exam and category. 60-second Blitz (4 balanced options, streak, instant feedback, retry queue) and Flip-Card study (Got it / Review again), recorded per user (Leitner boxes) in `speed_drill_stat`. |

## Verification (run against a DB copy, never the real `ciwt_lms.db`)

```
cp ciwt_lms.db /tmp/ob3.db
./venv/bin/python tools/ladder_check.py --max-skips 0 --require-complete
DATABASE_URL=sqlite:////tmp/ob3.db ./venv/bin/python tools/curriculum_readiness.py /tmp/ob3_readiness   # 29/29
DATABASE_URL=sqlite:////tmp/ob3.db ./venv/bin/python tools/sme_priority_review.py                     # 0 / 0 / 0 / 0
DATABASE_URL=sqlite:////tmp/ob3.db ./venv/bin/python -m pytest -q tests/test_option_b_pass1.py \
  tests/test_option_b_pass2.py tests/test_option_b_pass3.py tests/test_exam_sim_upgrades.py tests/test_prepilot_ux.py \
  tests/test_ladder_content.py tests/test_ladder_engine.py
```

`docs/SME_PRIORITY_REVIEW.md` reports 0 disputed items, 0 keys ≥ 1.15× the longest distractor across every item pool and ladder check, 0 `same_as` and 0 templated NETOPS sections.

## Discrepancy fixes, content round 7 and legal notices (Pending SME review)
- **Explanations scope toggle:** `?scope=course` on `/instructor/section/<id>/ladder` (and CSV) rolls up every section of the course the user can see; pill toggle "This class (X students) | All <COURSE> sections (Y sections, Z students)".
- **Who needs me:** empty state plus the "Helix attention signals: 0 students opted in…" note; alias URL `/instructor/section/<id>/who-needs-me`.
- **Priority 1:** Q9.11 re-asked about ext4 vs Windows case sensitivity (no Samba-dependent key); X-IT-11.3.3 lost its second defensible distractor ("documented vendor fix").
- **Priority 2:** NQ1.5 now uses parallel TLS services (LDAPS/HTTPS/IMAPS/SMTPS); NQ4.5 swaps AAAA for DNSKEY. All 169 ladder quick checks whose key was >1.15× the longest distractor were rebalanced (realistic, parallel distractors or a tighter key), including the NETOPS generator.
- **Ladder hygiene:** 6 misconception tags on IT-12.2 replaced by two new IT-12.2 misconceptions; 44 R1 plain-language rungs rewritten into short sentences. `tools/ladder_check.py --max-skips 0 --require-complete`: 0 skips, 0 errors, 0 warnings.
- **Priority 3/4:** NETOPS capstone ladders (1.4–6.4) now carry lesson-specific lines; 29 IT-7.x/IT-12.x cert items cite CompTIA/NIST/ITIL/RFC/PCI DSS sources; the misplaced RAM section and duplicate "Client addressing" were removed from NETOPS 1.2.
- **Legal/branding:** header "Novak LMS™"; footer "© 2026 Novak LMS™ · Privacy · Contact: novakornothing@gmail.com" in the LMS and on novakornothing.com; public `/privacy` with a plain-language summary.
- Regenerated: `SME_PRIORITY_REVIEW.md`, `curriculum_v2/cert/alignment.json`, screenshots 01–05. Playwright + axe at 390/1280 light/dark: 84 checks, 0 problems.

## Final pre-pilot UX pass (Pending SME review)
- Lessons: "X of Y sections verified" top and bottom; **What to do next** callouts; buttons **Check understanding**, **Explain it another way (style)**, **Next section ↓**, **Continue to Adaptive Check →**, **Continue to Lab →**.
- Struggling-student cards: Where stuck / What clicked badge / Lab and Helix tags / **Draft message**, **Open Rn preview**, **Grant gate bypass**. Empty states added.
- Contact: `NOVAK_CONTACT_EMAIL` (default novakornothing@gmail.com) in the footer, `/contact` (also `/help`) with FAQ, and on Setup.
- novakornothing.com landing: hero + privacy note + 5-question FAQ + contact (mailto, Sign in). Preview: `/landing`, `/?landing=1`.
- Screenshots: `/workspace/ciwt/screenshots/pilot-demo/01…05` (05 = landing). Playwright + axe sweep at 390/1280, light/dark: 72 checks, 0 problems.

## Pilot polish pass (Pending SME review)
- **Student flow:**
  - A missed check swaps the section in place, with a badge (for example "Swapped to R2: Analogy — step 2 of 4") and an R0 → R4 progress pill.
  - Passing shows a one-tap "Continue to next section ↓" chip, or "All sections verified — Continue to next lesson →" after the last section.
  - Locked sections fade in as they unlock (no animation under reduced motion).
- **Instructor views:**
  - "What finally clicked" badges on the ladder analytics page, the student ladder page and the mastery student page.
  - A "Why this student is struggling" card on the class page and in Who needs me. It combines ladder, lab flags and Helix (consent-aware) with one next action: message draft, rung preview or gate bypass.
- **Lab analysis:** each flagged mistake has a button, "Open <lesson> · <section> in <style> →", that deep-links to `/student/section/<s>/lesson/<l>?rung=R2&sid=<slug>#ladder-sec-<slug>` and opens that section on that rung.
- **Docs:**
  - `docs/PILOT_PLAYBOOK.md`
  - `docs/SME_PRIORITY_REVIEW.md` (produced by `tools/sme_priority_review.py`)
  - copies of both in this folder
- **Screenshots:** `/workspace/ciwt/screenshots/pilot-demo/01–04`.
- **Scale check:** `tests/test_reliability_scale.py` runs 60 students in 3 sections, with gate, hub, roster transfer, why cards, outcomes CSV/JSON, LTI passback/NRPS, hosting config vs docs, and backup + restore-check. All pages finish in under 1.5 s.
  - The hub limits the costly mastery % column to about 0.8 s per page view.
  - Sections not reached show "…" and fill in on the next visit; results are cached for 10 minutes.

## Remaining manual steps for production deployment
1. **Campus IdP:**
   - Send the SP metadata (`/sso/<slug>/saml/metadata.xml`) or the OIDC redirect URI to campus IT, and load their IdP metadata or client ID/secret in Admin → Institutions.
   - Run one live SAML and one live OIDC login with a test student and a test instructor. Check the role mapping and the `sso_login` entries in `/admin/audit-log`.
2. **GPL source:** `ciwt-linux.bin` (the v86 Linux image) contains GPL software. Publish the matching source archive (kernel, BusyBox and tools used to build it) at a public URL next to the image, and link it from the site footer or `/accessibility`/about page before public launch.
3. **Domain and TLS:**
   - Point a custom domain at the host (Render custom domain or a reverse proxy) and enable HTTPS (Render or Let's Encrypt certificate).
   - Then set the LMS/IdP redirect URLs to the final `https://` origin.
4. **Production secrets:**
   - `SECRET_KEY`: 64 random characters.
   - `NOVAK_AI_API_KEY`: only if the AI tutor should call the model.
   - **LTI RSA keypair:** keep it on persistent storage (`CIWT_INSTANCE_DIR=/var/data/ciwt/instance`) so it survives redeploys. Back up `instance/` with the database.
   - Never commit any of these.

## School-ready pass (1f3252c, Pending SME review)
- **Comprehension gate** (29cd8d0): students can't click past a lesson section until they pass its quick check or have tried every explanation. Exhausted students show up in "Who needs me". Server-side advance gate, live "X of Y sections verified" banner, section locks, per-student exemptions, optional strict quiz lock.
- **LTI 1.3:** per-section policy: opt-in removal of dropped students (only after a complete NRPS read, records kept), auto-passback after quiz/test/lab, exempt items as 100 or skipped. Sync history table.
- **Sections:** `/instructor/sections` hub with a cross-section comparison, a header section switcher, Clone (settings, weights and release schedule copied; empty roster; new join code), `/instructor/section/<id>/roster` (CSV import, transfer, drop, regenerate join code, staff roles) and `/join`.
- **Outcomes:** per-objective cert mapping (220-1201/1202, N10-009), initial→current mastery, R0–R4/Exhausted, lab process %, attempts. Export with `?format=csv|json`; print stylesheet.
- **Accessibility:** `/accessibility` (linked in the footer and setup checklist) and `docs/ACCESSIBILITY_WCAG21_AA.md`.
- **FERPA:** `/my-data` export (JSON or ZIP) and requests, `/instructor/section/<id>/privacy`, `/admin/ferpa` (anonymize, or delete activity, with typed-email confirmation), hash-chained `/admin/audit-log` (filters, CSV, tamper detection).
- **Roles:** `SectionStaff` lead/ta/observer. TAs grade and view analytics but can't change LTI, privacy or roster. Observers are read-only. One-page `/instructor/section/<id>/setup` covers all 7 areas.
- **Verification:**
  - Targeted set: 76 passed.
  - `tests/test_school_ready.py` (11 tests) passes.
  - Full suite earlier in this pass: 859 passed, 1 failed (test since fixed).
  - Playwright + axe on 13 pages × 390/1280 × light/dark: 52 checks, 0 violations (`tools/school_ready_shots.py`, screenshots in `screenshots/school/`).

## What's new in this milestone

| Area | Where | Notes |
|---|---|---|
| AI tutor | `/tutor`, plus an "Ask the tutor" drawer on lessons and labs; `/instructor/section/<id>/tutor` | Answers only from lessons, ladder rungs, glossary and lab guides (BM25). Cites section, rung and glossary terms. Refuses graded-answer requests and off-topic questions. Per-class on/off. Optional `NOVAK_AI_API_KEY` rephrasing, used only if it stays grounded in the retrieved passages. |
| Skills portfolio | `/portfolio`, `/portfolio/u/<token>`, `/portfolio/export.json` | Verified competencies, labs with process badges, A+ Core 1/2 and Network+ readiness. Printable. OpenBadges 2.0 JSON (unsigned, hosted verification). Private by default. |
| Campus SSO | `/sso/<slug>/login`, `/sso/<slug>/saml/metadata.xml`, `/sso/<slug>/saml/acs`, `/sso/<slug>/oidc/callback` | OIDC: auth code + PKCE S256, JWKS-verified ID token (iss/aud/exp/nonce), UserInfo; works with Okta, Entra ID, Google and Shibboleth. SAML 2.0 SP: XML signature over the Response or Assertion (pinned IdP cert, exc-c14n + RSA-SHA256), audience, recipient, time window, InResponseTo, replay and XXE protection. JIT provisioning with group → role mapping; admin role only via explicit mapping. |
| Multi-tenant | `institution` table; `institution_id` on `user` and `class_section`; `/admin/institutions`; `/t/<slug>` | Existing rows were moved to the `default` institution, so nothing changes for current users. Staff and institution admins get a 404 for any class or person in another institution. Institution admins can't open platform-wide `/admin` pages. Per-college colours, logo and banner (text colour chosen for WCAG contrast). |
| Outcomes | `/instructor/section/<id>/outcomes`, `/admin/outcomes`; `?format=csv`; print button | Objective mastery (first answered item vs now), which explanation-ladder rung resolved struggles, diagnose-first and verify-before-submit rates, real-VM completions, cert-domain readiness, grade distribution, logged study time. Every figure shows its denominator; "—" means no data. Demo seed data is flagged. |
| Hosting | `render.yaml`, `Dockerfile`, `docker-compose.yml`, `Procfile`, `docs/PRODUCTION_HOSTING.md`, `tools/backup_db.py`, `/healthz` | Persistent disk at `/var/data/ciwt` (SQLite WAL + `instance/` keys + backups) or PostgreSQL via `DATABASE_URL`. `/healthz` checks the DB and storage. |

## Verification (this run)

- **pytest:** full suite 847 passed + 2 failed in the long run; both fixed (render.yaml DB-guard flag, CSS bundle) and re-run green: 47/47 in the affected files. One VM-harness timeout passed on retry (warning). New suites: `tests/test_institutional.py` (12), `tests/test_ai_tutor.py`, `tests/test_portfolio.py`.
- **Upgrade rehearsal** on a copy of `ciwt_lms.db` (`tools/upgrade_check.py upgrade`): 18/18. No rows lost (users 28, classes 4,
  enrollments 67, test attempts 185), integrity ok, key pages 200. The tenant migration only adds columns.
- **Explanation-ladder browser run (`ladder_e2e`):** 43/43 at each of 390/1280 × light/dark.
- **New pages (`tools/launch_shots.py`):** tutor, portfolio, outcomes (class + admin), institutions, tenant landing and login
  picker, at 1280/390 × light/dark. 108/108: all 200, no sideways overflow, 0 axe WCAG 2.1 AA violations.
- **Real Linux VM:** booted and ran commands on a 390 px phone viewport.
- **Backup tool:** `tools/backup_db.py` snapshot + `--restore-check` passed (integrity ok).
- **Screenshots:** `/workspace/ciwt/screenshots/launch/01…08`.

**Not verified here:**

- PostgreSQL. It's supported in code, but the suite runs on SQLite.
- A real IdP. SSO was tested end to end with a mock IdP: signed SAML responses and a fake OIDC provider with real
  RS256 JWKS.
- Docker builds. There is no Docker daemon on this machine.

## 1. Push (when you're happy)

```bash
cd ciwt-lms
git status                         # clean
git log --oneline -5               # top commit 7d08575
git push origin refinement         # branch for review / PR
# or make it main directly:
git checkout main && git merge --ff-only refinement && git push origin main
```

GitHub isn't signed in on this machine; run `gh auth login` first. `ciwt_lms.db`, `instance/`, `.env` and `backups/`
are git-ignored.

## 2. Back up, then upgrade an existing install

```bash
# stop the LMS first
python tools/backup_db.py --dest backups            # consistent, verified, gzipped copy of ciwt_lms.db
python tools/backup_db.py --restore-check backups/ciwt-*.db.gz
tar czf instance-backup.tgz instance/               # LTI keys
git fetch && git checkout refinement
./venv/bin/python -m pip install -r requirements.txt   # adds lxml (SAML) and psycopg (optional PostgreSQL)
bash tools/fetch_v86.sh                             # VM emulator files, if not present
./venv/bin/python tools/upgrade_check.py upgrade --src ciwt_lms.db   # rehearsal on a copy; expect 18/18
./start_lms.sh                                      # migrations run automatically at start-up (add-only)
curl -fsS http://127.0.0.1:5050/healthz
```

Rollback: stop the app, `git checkout <previous commit>`, restore the `.db.gz` with `gunzip -c`, and delete any
`-wal`/`-shm` files.

## 3. Persistent hosting (pick one; full detail in `docs/PRODUCTION_HOSTING.md`)

- **Render (paid plan + disk):** create a Blueprint from `render.yaml`.
  - It sets up a 5 GB disk at `/var/data`, SQLite WAL on the disk, `CIWT_INSTANCE_DIR` on the disk, `/healthz` as
    the health check, and a generated `SECRET_KEY`.
  - **Don't use the free plan.** Its storage is wiped on every deploy.
- **Docker / VM:**
  ```bash
  cp .env.example .env    # then set SECRET_KEY in .env
  docker compose up -d --build
  ```
  - All state lives in the `ciwt-data` volume.
  - The `backup` service writes a verified backup every day and keeps 14.
  - Put the app behind a TLS reverse proxy; SSO needs HTTPS.
- **PostgreSQL:** set `DATABASE_URL=postgres://…`. Rehearse on staging first.

## 4. Turn on campus SSO for a college or command

1. Go to Admin → Institutions → Add, and enter the name, slug and email domain.
2. On the institution page, set the logo and colours, and paste the SSO JSON.
   - **OIDC:** issuer + `client_id`. Keep the secret in `SSO_<SLUG>_CLIENT_SECRET`.
   - **SAML:** `idp_entity_id`, `idp_sso_url`, `idp_cert`.
   - **Roles:** `role_map`, e.g. `{"instructor":["faculty"],"admin":["lms-admins"]}`.
3. Send campus IT the SP metadata URL, or the OIDC redirect URI, shown on that page. Then press **Test campus sign-in**.
4. Share `https://<host>/t/<slug>`.

## 5. SME review checklist

- [ ] Explanation ladders (ITSUP ch01–06, NETOPS ch01–06, CLIENT). Rungs R1–R4 and micro-checks are tagged
      "Pending SME review"; confirm accuracy and that keys are right.
- [ ] Glossary definitions used by the AI tutor (they are quoted verbatim in tutor answers).
- [ ] Tutor refusal wording and the cheat-detection list (`tutor/guard.py`).
- [ ] Lab process badges and "Where it went wrong" tips (`mastery/lab_diagnosis.py`).
- [ ] Objective → A+ Core 1/2 / Network+ domain mapping (`curriculum_v2/cert/mapping.py`). It drives the portfolio
      and outcomes readiness; the pages say it is not endorsed by CompTIA.
- [ ] Outcomes report definitions (shown on the page and in the `institutional/outcomes.py` docstring) before
      sharing figures outside the schoolhouse.
- [ ] Remove or re-password the demo accounts (`*@lms.local`) before real students arrive. Outcomes flags them as demo data.
- [ ] Privacy/legal: the public portfolio link (student opt-in), OpenBadges export, and SSO attribute release (email, name, groups only).

## Artifacts (`/workspace/artifacts`)

- `ciwt-lms-refined.tar.xz` / `ciwt-lms-refined-code.zip`: the source at 1f3252c (`git archive`; no DB, venv or keys).
- `ciwt-lms-vm-image.zip`: `static/vendor/v86/ciwt-linux.bin`.
- `course-package.zip`: syllabus, pacing, rubrics, glossary, lesson plans, lab manual, answer keys (instructor-only folder).
