# Explanation ladder: authoring guide (schema v1, pass 19)

The explanation ladder lets a lesson change for each student, in place, while they read it. After each concept
section there is a short micro-check. If the student misses it, or presses **Explain it another way**, *their* copy of
the lesson replaces that section with the next rung, a genuinely different explanation, and asks a fresh check. If
they miss again, it moves up another rung. The rung that worked is what they see when they come back, and they can
always toggle back to the original. When a section's rungs run out, the student is flagged to the instructor with the
section and the rungs that were tried.

This guide is for content authors. The engine, UI and instructor controls are documented in REFINEMENT_NOTES (pass 19).

## The rungs

| Rung | Kind | What it must be |
|---|---|---|
| R0 | original | The section as written in the lesson. Never edited here. |
| R1 | `plain` | The same idea in plain language: short sentences, everyday words, one idea per sentence, jargon defined or dropped. |
| R2 | `analogy` | A different analogy or a real-world story that maps onto the idea part by part. Say where the analogy stops working if that could mislead. |
| R3 | `visual` | A picture or a trace: an inline `<svg>` diagram (with `role="img"`, an `aria-label` and a `<title>`) and/or a numbered `<ol class="ladder-trace">` walk-through. |
| R4 | `try` | Hands-on: a mini interactive (`order`, `sort` or `reveal`) and/or a link into the matching lab (`lab={'id': ..., 'note': ...}`). |

**Different, not paraphrased.** Each rung must explain the idea another way, not reword the original. The validator
fails a rung whose word overlap with the original, or with another rung, is above 0.55 (token Jaccard).

**No new rules.** Rungs re-explain what the lesson already teaches. Do not add course policy, numbers or procedures
that are not in the lesson or in the cited primary source.

**Accuracy and level.** Write for intro college IT students. Check every technical fact against a primary source
(vendor documentation, RFCs, standards, the official exam objectives) and name it in `source`. If the rung only
re-explains the lesson, say so: `Course lesson 1.1 "…" (the original section), re-explained`.

## Checks

The original (R0) and every rung each have 1–2 quick checks:

- Each check tests the same idea **in a different form** from the original's check: a new scenario, the reverse
  direction, or "which of these is an example". It must not repeat another check's question.
- Give 2–3 distractors that are plausible wrong ideas. Tag at least one with a misconception id, such as an existing
  `MC-IT1-…` from `curriculum_v2/misconceptions.py` or a new one defined in your file.
- `why` explains why the key is right **and** why the main distractor is wrong, in at least 10 words.
- **Balance option lengths.** The key must not be the giveaway longest option. The validator fails a file where the
  key is the uniquely longest option in more than 30% of its checks, and warns on each check where the key is more
  than 15% longer than every distractor. Shorten the key (the `why` carries the explanation), or lengthen
  distractors with plausible detail that keeps the same wrong idea.
- Option order is shuffled deterministically. Write the key and distractors in any order.

## Files and layout

There is one file per chapter, so authors never edit the same file:

```
curriculum_v2/ladder/itsup/ch01.py … ch13.py
curriculum_v2/ladder/netops/ch01.py … ch06.py, ch09.py
curriculum_v2/ladder/client/ch01.py … ch06.py
```

`CHAPTER` is the chapter's **order in its course** (the module order), not the lesson number. CLIENT chapter 1 holds
lessons labelled 8.1–8.4. Files are discovered automatically, so do not edit `__init__.py`, `schema.py`,
`sections.py` or anyone else's chapter files. If you need a schema change, write it down in your branch's
MERGE_NOTES and keep going.

**Current assignments (pass 19):**

- refinement: ITSUP chapters 1–6.
- `content`: all NETOPS chapters.
- `labs`: ITSUP chapters 7–13 and all CLIENT chapters.

## Sections and ids

A concept section is one `<section class="sublesson …">` block of the lesson, which is how every lesson is built
(the pass-19 census found no headings outside such blocks). Its id (`sid`) is a slug of its first `<h3>` heading,
with `-2`, `-3` and so on for repeats in the same lesson. Get the exact ids and headings from the scaffold:

```bash
./venv/bin/python tools/ladder_check.py --scaffold NETOPS 2 > /tmp/ch02.py   # sids, headings, kinds, word counts
```

Every section of every lesson needs exactly one entry:

- `section(...)`: a full ladder (R1–R4 plus checks). This is the default for anything that explains a concept.
- `same_as(target_sid, heading, note)`: this section restates a concept already laddered **in the same lesson**
  (lessons often explain an idea in the core section, then again at depth). It uses that ladder. Do not use it to
  avoid writing a genuinely separate concept.
- `skip(heading, reason, note)`: not a concept section. `reason` is one of `plan` (hour or timing plans),
  `activity` (a drill that is itself practice), `orientation` (start-here or signpost blocks) or `reference`
  (lookup tables and term lists). Skipped sections show as written, with no micro-check, and are counted separately
  in coverage.

## A section entry

```python
from curriculum_v2.ladder.schema import analogy, check, order, plain, reveal, same_as, section, skip, sort, tryit, visual

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 1
MISCONCEPTIONS = {   # new ids only; prefix MC-L-<course letters><chapter>-, e.g. MC-L-NO1-…, MC-L-CL3-…
    'MC-L-NO1-EXAMPLE': {'obj': 'NO-1.1', 'label': 'the wrong idea, in plain words', 'fix': 'what the lesson teaches instead',
                         'terms': ['words', 'to find the lesson section'], 'source': '…', 'review': 'Pending SME review'},
}
LESSONS = {
    '1.1': {
        'some-section-id': section(
            'Exact heading text', 'NO-1.1',
            [check('R0 question', 'key', ['distractor 1', 'distractor 2'], 'why …', mc=['MC-…', None])],
            plain('<p>…</p>', 'source', [check(...)]),
            analogy('<p>…</p>', 'source', [check(...)]),
            visual('<svg …>…</svg><ol class="ladder-trace">…</ol>', 'source', [check(...)]),
            tryit('<p>…</p>', 'source', [check(...)],
                  widget=order('prompt', ['step 1', 'step 2', 'step 3'], 'what to notice'),
                  lab={'id': 'an-existing-lab-id', 'note': 'what to do there'})),
        'a-restated-section': same_as('some-section-id', 'Its heading', 'why it is the same concept'),
        'hour-plan-for-1-1': skip('Hour plan for 1.1', 'plan', 'The teaching timetable.'),
    },
}
STAMPS = {}   # paste the output of: tools/ladder_check.py --stamp NETOPS 1
```

`curriculum_v2/ladder/itsup/ch01.py` is a complete worked example: all 22 sections of lesson 1.1, with 10 laddered,
7 `same_as` and 5 `skip`. It also shows small SVG helpers (`svg`, `box`, `arrow`) that draw in `currentColor`, so
diagrams work in light and dark mode. Copy those helpers into your file if you want them; do not import them from
another author's file.

**Widgets for R4:**

- `order(prompt, steps, done)`: the student puts shuffled steps in order. Give at least 3 steps.
- `sort(prompt, {bucket: [items]}, done)`: the student sorts items into buckets. Give at least 2 buckets and 4 items.
- `reveal(prompt, answer)`: the student predicts the answer, then reveals it.
- `lab={'id': …}` must be an existing lab id (`interactive_labs.LABS`). Prefer the lab or VM step that exercises
  exactly this idea.

**HTML rules.** No scripts, event handlers, forms, styles or remote `src`. Use `<p>`, `<ul>`, `<ol>`, `<strong>`,
`<em>`, `<code>`, `<table>` and inline `<svg>`. SVG text and lines use `currentColor`.

**Review status.** Every rung, check and new misconception carries `'Pending SME review'`; the helpers set it.

## Workflow

```bash
./venv/bin/python tools/ladder_check.py --scaffold ITSUP 7 > curriculum_v2/ladder/itsup/ch07.py   # then fill in every None
./venv/bin/python tools/ladder_check.py --course ITSUP --chapter 7 --sections                     # status of each section
./venv/bin/python tools/ladder_check.py --stamp ITSUP 7 >> curriculum_v2/ladder/itsup/ch07.py      # once the chapter is written
./venv/bin/python tools/ladder_check.py --course ITSUP --chapter 7 --require-complete               # must exit 0 before you commit
./venv/bin/python -m pytest -q tests/test_ladder_content.py
```

The checker reads lessons from a throwaway copy of `ciwt_lms.db`; it never opens the real database. Commit one
chapter per commit. Before committing, also run the checker over all files (no arguments) so you are sure your file
does not collide with anyone else's: a duplicate key or misconception id is an error.

**Stamps and staleness.** `STAMPS` records a fingerprint of each original section when its rungs were written. If
the original is later edited, the checker marks the section `stale` and asks for a re-review, so the rungs never
silently drift from the lesson they explain.

## Coverage

Run `tools/ladder_check.py` with no arguments. It prints, per course and chapter, how many concept sections are
laddered, `same_as`, skipped, missing or stale. `--json out.json` writes the same report together with every
section's status.
