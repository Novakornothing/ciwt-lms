# CIWT Learning Management System

Schoolhouse LMS with **proprietary** CIWT curriculum for IT support and network operations training. Original instructional content — not a vendor certification product.

## Demo accounts

| Role | Email | Password |
|------|--------|----------|
| Admin | admin@lms.local | admin123 |
| Instructor | instructor@lms.local | teach123 |
| Student | student1@lms.local | student123 |

## Run (development)

```bash
cd comptia-lms
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
PORT=5050 python app.py
```

Open http://127.0.0.1:5050 · [Demo guide](/demo) · [Gaps](/gaps)

`python app.py` (and `./start_lms.sh`) run with the Flask/Werkzeug **debugger off** and listen on all
interfaces (`HOST=0.0.0.0` by default). Turn the debugger on only for local work with `FLASK_DEBUG=1`;
it then binds to `127.0.0.1`, because the debugger runs code for anyone who can reach it. (To expose a
debug server anyway you must also set `CIWT_ALLOW_DEBUG_ON_NETWORK=1`; don't, through a tunnel.)

| Variable | Default | Effect |
|---|---|---|
| `FLASK_DEBUG` | off | `1` turns on the debugger and reloader (and binds to 127.0.0.1) |
| `HOST` / `PORT` | `0.0.0.0` (`127.0.0.1` in debug) / `5050` | Listen address |
| `CIWT_NEURAL_TTS` | `1` | `0` turns off the neural Listen voice, which sends lesson text to Microsoft's online speech service via edge-tts; the browser voice is used instead |
| `DATABASE_URL` | `sqlite:///ciwt_lms.db` | Database. Scripts, tests and one-off tools should point this at a **copy** |
| `CIWT_ALLOW_REAL_DB` | unset | `1` lets an *import* of `app` (gunicorn, `flask --app app …`, scripts) use the bundled `ciwt_lms.db` when `DATABASE_URL` is unset. Without it such an import is refused, because importing `app` runs the start-up sync that rewrites the DB. `python app.py`, `start_lms.sh`, the Procfile and render.yaml are allowed |
| `CIWT_HELIX_RETENTION_DAYS` | `365` | Helix sessions, events and accuracy-study records older than this are removed by `flask --app app helix-cleanup` (cron) or Admin → Data & privacy; `0` keeps them |

## Production-style process

```bash
export SECRET_KEY='change-me'
export CIWT_ALLOW_REAL_DB=1        # or DATABASE_URL=… (the Procfile and render.yaml set this already)
gunicorn -b 0.0.0.0:5050 -w 2 'app:app'
```

**Database guard (pass 13).** Importing `app` creates tables, runs migrations and syncs the curriculum into the
database. So a script or test that imports `app` with no `DATABASE_URL` refuses to run (RuntimeError) instead of
silently rewriting `ciwt_lms.db`. Use `DATABASE_URL=sqlite:////tmp/copy.db` for tools and experiments. Admin CLI
commands on the real DB need `CIWT_ALLOW_REAL_DB=1 flask --app app …`. The tests set their own temporary DB
(`tests/conftest.py`), and `tests/test_db_guard.py` checks the guard.

## Admin tools

- **Re-seed demo database** — Admin dashboard (destroys live data)
- **Export scores CSV** / **item flags CSV**
- **Backup database** — downloads SQLite file
- **Data & privacy** (`/admin/privacy`) — export a student's full record as JSON or delete it (all tables, Helix included; audited), and run the Helix retention cleanup. Public notice: `/privacy`
- Teaching time, test analytics, tickets
- Opt-in Helix attention (WebGazer engine): AOI timelines per student/lesson, instructor dashboard, written policy that this is a signal not an assessment (`/policy/attention`)

## Smoke check

With the app running:

```bash
python smoke_test.py http://127.0.0.1:5050
```

## Courses

- IT Support Technician Fundamentals
- Network Operations Fundamentals

Original instructional content for demonstration only.

## Refinement (2026-10)

See [REFINEMENT_NOTES.md](REFINEMENT_NOTES.md) for the Helix attention package, the gradebook, the mobile shell, and how to run the tests.
