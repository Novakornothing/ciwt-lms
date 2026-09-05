# CIWT Learning Management System

Demo-ready web LMS with **proprietary** curriculum for IT support and network operations training (Navy IST / contractor prototype). Not official CompTIA content.

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

## Smoke check

With the app running:

```bash
python smoke_test.py http://127.0.0.1:5050
```

## Courses

- IT Support Technician Fundamentals
- Network Operations Fundamentals

Original instructional content for demonstration only.
