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
| `CIWT_HELIX_RETENTION_DAYS` | `365` | Helix sessions, events and accuracy-study records older than this are removed by `flask --app app helix-cleanup` (cron) or Admin → Data & privacy; `0` keeps them |

## Production-style process

```bash
export SECRET_KEY='change-me'
gunicorn -b 0.0.0.0:5050 -w 2 'app:app'
```

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
