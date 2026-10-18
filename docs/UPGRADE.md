# Upgrading an existing CIWT LMS install to the `refinement` release candidate

This was tested in pass 16 (18 Oct 2026). A copy of the current `ciwt_lms.db` was booted with the new code
(`tools/upgrade_check.py upgrade`), and the copy's checks passed 18/18:

- 21 tables were added, plus new columns on `gradebook_setting` and `helix_gaze_session`;
- no table lost rows and no column was dropped;
- `user` 28 → 28, `course` 3 → 3, `class_section` 4 → 4, `enrollment` 67 → 67, `test_attempt` 185 → 185, and
  `quiz_attempt`, `grade_override`, `grade_due` and `gradebook_setting` kept their rows (0 → 0);
- SQLite's `integrity_check` returned `ok`;
- the admin, instructor and student pages tested all loaded (200).

The only rows that changed were new `audit_event` rows from the test logins. This database has no separate
"submission" table: graded submissions are `test_attempt` and `quiz_attempt` rows. Migrations run automatically
at start-up. They only add tables and columns; nothing is dropped or rewritten.

A brand-new empty database also boots cleanly (7/7). It creates the schema and the **demo accounts**
(`admin@lms.local` and the others, with their published demo passwords). Change or remove those accounts before
any real use.

## Steps

Run these in the folder where the LMS lives (the one with `app.py`).

1. **Stop the LMS.** Stop the running `start_lms.sh`, `python app.py` or gunicorn process.

2. **Back up first.** Back up the database and the `instance/` folder, which holds the LTI signing keys if you
   connected an LMS. Neither is in git.

   ```bash
   STAMP=$(date +%Y%m%d-%H%M)
   mkdir -p ~/ciwt-backups
   python3 -c "import sqlite3; s=sqlite3.connect('ciwt_lms.db'); d=sqlite3.connect('$HOME/ciwt-backups/ciwt_lms-$STAMP.db'); s.backup(d); d.close(); s.close()"
   tar czf ~/ciwt-backups/instance-$STAMP.tgz instance/ 2>/dev/null || true
   python3 -c "import sqlite3; print(sqlite3.connect('$HOME/ciwt-backups/ciwt_lms-$STAMP.db').execute('pragma integrity_check').fetchone()[0])"   # expect: ok
   ```

   While the server is running you can also download a copy as admin from `/admin/backup-db`.

3. **Get the new code.**

   ```bash
   git fetch origin
   git checkout refinement          # or main, once refinement has been merged into it
   git pull --ff-only
   ./venv/bin/python -m pip install -r requirements.txt
   bash tools/fetch_v86.sh          # in-browser Linux VM files (pinned, sha256-checked; ciwt-linux.bin is in git)
   ```

4. **Rehearse on a copy (recommended).** This copies your database to `/tmp/ciwt-upgrade` and boots the new code
   against the copy on 127.0.0.1:5075. It compares every table's row count and columns, and loads key pages. Your
   real `ciwt_lms.db` is only read.

   ```bash
   ./venv/bin/python tools/upgrade_check.py upgrade --src ciwt_lms.db
   ```

   Every line should say `PASS`. The page checks use the demo logins. If you changed or removed the demo accounts,
   those checks fail, but the row-count, schema and integrity checks still apply.

5. **Start the LMS normally.** The first start applies the migrations and the content sync.

   ```bash
   export SECRET_KEY='a-long-random-value'   # required before real users
   ./start_lms.sh                            # or: CIWT_ALLOW_REAL_DB=1 gunicorn app:app --bind 127.0.0.1:5050
   ```

6. **Check it.** Sign in as admin and open `/admin/readiness`. As an instructor, open a class's gradebook and
   briefing. As a student, open a lesson and a Linux lab.

## Rolling back

1. Stop the LMS.
2. Run `git checkout <previous branch or commit>`.
3. Copy the backup over the database: `cp ~/ciwt-backups/ciwt_lms-$STAMP.db ciwt_lms.db`.
4. Restore `instance/` from its tarball if needed.
5. Start the LMS again.

The old code ignores the new tables and columns, but restoring the backup is the clean way back.

## Notes

- **Render free plan.** `render.yaml` uses Render's free plan, which has no persistent disk. A SQLite file there is
  lost on every deploy or restart, and the app then starts again with only the demo data. For real classes, use a
  persistent disk or a hosted database, and set `DATABASE_URL`.
- **Database guard.** Tools and scripts refuse to open the real `ciwt_lms.db` unless `DATABASE_URL` or
  `CIWT_ALLOW_REAL_DB=1` is set (see README). `start_lms.sh`, the Procfile and `render.yaml` set it for you.
