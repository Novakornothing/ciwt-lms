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

## Production-style process

```bash
export SECRET_KEY='change-me'
gunicorn -b 0.0.0.0:5050 -w 2 'app:app'
```

## Admin tools

- **Re-seed demo database** — Admin dashboard (destroys live data)
- **Export scores CSV** / **item flags CSV**
- **Backup database** — downloads SQLite file
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
