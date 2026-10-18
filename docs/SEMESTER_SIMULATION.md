# Adaptive semester simulation (pass 13)

**This is a synthetic engine check, not evidence of learning gains.** The "students" are 20 synthetic accounts
(`simNN@synthetic.invalid`, in a class named "SYNTHETIC SIMULATION — not real students") whose answers are drawn
from fixed per-objective probabilities. The tool tells you whether the adaptive engine *behaves* as designed;
it says nothing about whether real students learn more.

## Run it

Always on a copy of the database. The tool refuses `ciwt_lms.db`, and the app-wide DB guard refuses it too unless
`CIWT_ALLOW_REAL_DB=1` is set.

```bash
cp ciwt_lms.db /tmp/sim.db
DATABASE_URL=sqlite:////tmp/sim.db ./venv/bin/python tools/semester_sim.py /tmp/sim.json --days 28 --seed 13
```

The smoke version, `tests/test_semester_sim.py`, runs 22 simulated days on a fresh DB as part of `pytest`.
The last full run is saved in `docs/readiness/semester-sim-pass13.json` (12 of 12 checks passed, seed 13, 28 days).

## The cohort

| Profile | Count | Behaviour |
|---|---|---|
| strong | 4 | high correct-answer probability on every objective |
| good | 5 | above average |
| mixed | 5 | good overall, but 2 objectives each at p = 0.15 |
| weak | 4 | low probability everywhere |
| disengaged | 2 | stop working on day 9 |

They work through ITSUP chapters 1–4 using the real HTTP routes: lessons, study-time heartbeats, chapter checks,
daily review, reviews, mastery checks (test-outs) and one graded knowledge test on day 10. Lab completions are
written directly; the lab simulator has its own e2e suites.

**Time.** After each simulated day, every timestamp belonging to the synthetic accounts is moved back one day,
including the daily-review day keys. The engine compares stored times with the real clock, so it sees the history
age as it would over a real term. No clock is patched.

## What it checks

1. Reviews are inserted for every objective a mixed student is weak on.
2. Every strong student is offered a mastery check and passes at least one.
3. After a test-out, the path no longer sends that student into the chapter.
4. No weak student passes a mastery check.
5. Spaced review comes due: the daily review serves "due" items to every engaged student.
6. "Who needs me" lists every weak student with a reason other than inactivity.
7. "Who needs me" flags both disengaged students as inactive.
8. The top of "Who needs me" is never a strong student.
9. No strong student appears in "Who needs me".
10. The briefing to-do names only students who need help.
11. The briefing focus list includes every weak student and no strong one.
12. No adaptive action changes a grade. The gradebook CSV and graded rows are identical before and after each
    day's adaptive actions.

## Bugs it found (fixed in pass 13)

- **Reading-only objectives blocked test-outs.** `policy.strong_so_far` counted objectives that had no answered
  items, so a strong student was never "strong so far". It now counts only answered objectives.
- **Daily review keyed by real date.** This was a simulation artifact, not an app bug. The aging step now shifts
  the daily-review day keys as well.

## Known limits

- A test-out skips the chapter check. If an instructor gives quizzes a non-zero gradebook weight, the
  completion percentage drops for students who tested out; grades themselves don't change.
- When students tie, the briefing to-do picks one student per kind alphabetically, so a mixed student can rank
  above a weak one.
- Answer probabilities are fixed. Nobody in the cohort learns, so this can't test whether reviews help.
