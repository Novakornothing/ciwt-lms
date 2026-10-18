# Merge notes: `labs` (round 2/3, `757cc99`) into `refinement`

`labs` was last merged into `refinement` at `3350882` (merge commit `973fb66`). Since then `labs` added 15 commits
(round 2/3: ten more real Linux VM labs, the own-built `ciwt-linux.bin` VM image, Windows-sim fidelity and wrong
turns, lab scenarios SCN-DNS / SCN-LAN2, and the *Pending SME review* tag on every new lab). `refinement` had moved to
`22355a3` (pass 13 and pass 14 work). The merge was done locally in the `refinement` worktree; nothing was pushed, and
the `labs-wt` / `content-wt` worktrees were not touched.

A dry run (`git merge-tree --write-tree refinement labs`) showed one conflict; everything else merged automatically.

| File | Conflict | Resolution |
|---|---|---|
| `REFINEMENT_NOTES.md` | Both sides appended after the "Labs branch" section: refinement added the Pass 12 and Pass 13 sections, labs added the `### Labs branch, round 2/3` subsection. | Keep both. The labs subsection goes at the end of the "Labs branch" section (it is a `###` subsection of it), followed by Pass 12 and Pass 13 unchanged. |
| `tools/a11y_sweep.py` | Auto-merged. | Checked: labs' new pages (`lab-vm-disk`, `lab-vm-fw`, `lab-scenario`, `lab-scenario-stage`) sit beside refinement's mastery, gradebook and briefing pages. |

## Regenerated after the merge

- `curriculum_v2/cert/alignment.json`: `python tools/cert_coverage.py`. The new VM labs (`linux-vm-dns`,
  `linux-vm-nettrouble`, `linux-vm-disk`, …) now appear as lab evidence for the cert objectives they cover.
  `CERT_COVERAGE.md` (`tools/cert_coverage_md.py`) was already current.
- The icon subset (`python tools/build_icon_subset.py`) is unchanged: 144 icons, same hash. The new lab templates use
  no new icons.

## Checks on the merged tree (all on DB copies; `ciwt_lms.db` stays at sha `47fabc92…`)

- pytest: 646 passed, 1 failed. The failure is `tests/test_semester_sim.py::test_semester_simulation_smoke`. It is not
  caused by the merge: the synthetic simulation depended on Python's per-process string hash seed. With hash seed 3, a
  strong student picks the same distractor twice and lands in "Who needs me" with a mix-up reason. That is correct
  engine behaviour; the check is about the synthetic profile. Fix committed after the merge: `tools/semester_sim.py`
  pins `PYTHONHASHSEED=0` unless the caller sets one. See REFINEMENT_NOTES pass 14.
- Node: 41/41 (labs added one `lab-vmnet` test).
- Lab smoke on a fresh copy of `ciwt_lms.db` (`/tmp/p14/merge.db`, server on 127.0.0.1:5078), running
  `tools/labs_e2e.py --only 'linux-vm-(perms|disk|firewall|dns)|win-ipconfig|scn-dns|SCN-DNS|hw-cables|rtr-vlan-acl|ticket-intake' --views desktop,phone`:
  29/29. That covers 10 labs × desktop/phone (4 real VM labs, both SCN-DNS stages, Windows CLI, matching, IOS and
  ticket) plus 9 instructor checks (detail pages, gradebook labs column, CSV, results page).

## First boot against the real DB

Nothing new beyond the earlier labs merge. The scenarios store their state in the existing lab progress tables, and the
VM image is a static file. Take a backup of `ciwt_lms.db` first anyway; this merge never booted against it.
