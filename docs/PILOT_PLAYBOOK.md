# Pilot playbook — running one real class

Two pages and six steps. Everything below exists in the app today. New text is **Pending SME review**.

## 1. Create or clone the section and get a join code
- **Instructor → Sections** (`/instructor/sections`, or the **Sections** menu in the header).
- To reuse last term's setup, click **Clone** on that row. Clone copies the adaptive, ladder, Helix and grading settings and the release schedule. The new section starts with an empty roster and its own join code.
- The roster page (`/instructor/section/<id>/roster`) shows the **join code**. Use **Regenerate** if the code leaks.

## 2. Turn on adaptivity, the comprehension gate and the Helix policy
Open **Setup** (`/instructor/section/<id>/setup`). It is one page with seven areas:
1. **Roster & multi-section**: students and the join code.
2. **Adaptive path & comprehension gate** (Mastery settings):
   - Adaptivity is on by default.
   - **The comprehension gate is on by default.** "Next lesson" waits until every section's quick check is passed, or the student has seen every explanation.
3. **Explanation ladder**: on, with up to 4 alternative explanations: R1 plain language, R2 analogy, R3 visual/step-by-step, R4 try it.
4. **Helix policy**: Helix is offered as an opt-in with consent. Turn it off for the class if your college has not approved it. It never affects grades.
5. **Staff roles**:
   - Add TAs, who can grade and see analytics.
   - Add observers, who are read-only.
6. **LTI 1.3** (optional): see step 3.
7. **Accessibility & FERPA**: share `/accessibility` with students who use assistive technology.

## 3. Enroll students (pick one)
- **Join code:** students sign in and enter it at `/join`.
- **CSV:** on the roster page, import columns `email, full_name, role`. Missing accounts are created; students sign in with SSO or a password reset.
- **LTI 1.3:** follow **LMS connection** (`/instructor/section/<id>/lti`) → **Sync roster**.
  - Removing students the LMS no longer lists is opt-in, and their records are kept.
  - Turn on **auto-passback** to send each quiz, test or lab score as soon as it is finished.

## 4. First week
**Students:**
- Read a lesson section, then answer its quick check (not graded).
- A miss swaps the section in place to the next explanation. A badge ("Swapped to R1: Plain language — step 1 of 4") and an R0 → R4 pill show where they are.
- When they pass, a **Continue to next section ↓** chip appears. After the last section the chip reads **All sections verified — Continue to next lesson**.

**Instructor, daily:** open **Who needs me** (`/instructor/section/<id>/mastery/today`). If a student needs an accommodation, use **Grant section gate bypass**.

## 5. Mid-week: read "Why this student is struggling"
The class page and Who needs me show one card per struggling student, readable in under 10 seconds. Each card has four labelled rows:
- **Where stuck:** sections they ran out of explanations on or keep missing (or, failing that, a lab habit).
- **What clicked:** a badge such as "✓ Best style: Analogy (R2)", plus how many struggles it resolved.
- **Signals:** one-line tags, e.g. `Lab: Changed config before diagnosing` (links to the attempt's process analysis, where each mistake has an **Open <lesson> · <section> in <style> →** button) and `Helix: Not opted in` (or attention notes when the student consented).
- **Next action:** **Draft message** (a draft only; nothing is sent until you press send), **Open R2 preview** (the rung that works for them) and **Grant gate bypass**.

When no one is struggling the card says so, and the class ladder page says "nothing to show yet" for What finally clicked.

### What students see
- "X of Y sections verified" at the top and bottom of every lesson, with a **What to do next** line.
- Under each section: **Check understanding** and **Explain it another way (style)**; after a pass, a **Next section ↓** chip.
- At the end of the chapter: **Continue to Adaptive Check →** and **Continue to Lab →**, so there is no dead end.

### Support
- Contact & Support (`contact@novakornothing.com`, configurable with `NOVAK_CONTACT_EMAIL`) is in every page footer, on `/contact` (with an instructor and student FAQ) and on each section's Setup page.
- novakornothing.com shows the hero, a privacy note, an FAQ and a contact section (preview at `/landing` or `/?landing=1`).

## 6. End of term: pull the outcomes report
- **Outcomes** (`/instructor/section/<id>/outcomes`) lists one row per course objective with:
  - the CompTIA objective it maps to
  - initial → current mastery
  - which explanation (R0–R4) resolved struggles, plus how many were exhausted
  - lab process %
  - attempt count
- Download the report as **CSV** or **JSON**, or use **Print**.
- Admins get the institution-wide version at `/admin/outcomes`.
- Rows built on demo accounts are labelled. Do not report them as real outcomes.

Before the pilot starts, also do the manual deployment steps in `LAUNCH_HANDOFF.md` (IdP test, domain/TLS, secrets).
