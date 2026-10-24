# Production hosting (persistent storage)

The free Render plan, and any container without a mounted volume, has **ephemeral storage**: the filesystem is
reset on every deploy or restart. That deletes grades, mastery history, lab attempts, LTI keys and SSO links. Use
one of the persistent set-ups below for anything beyond a demo.

## What has to persist

| Data | Where | Setting |
|---|---|---|
| Database (SQLite + `-wal`/`-shm` files) | `/var/data/ciwt/ciwt_lms.db` | `DATABASE_URL=sqlite:////var/data/ciwt/ciwt_lms.db`, `CIWT_SQLITE_WAL=1` |
| or PostgreSQL | managed service | `DATABASE_URL=postgresql://…` (`postgres://` is accepted and rewritten) |
| LTI tool key (+ rotated keys) | `/var/data/ciwt/instance/lti/` | `CIWT_INSTANCE_DIR=/var/data/ciwt/instance` (or `LTI_PRIVATE_KEY`) |
| SSO settings and identity links | database tables `institution`, `sso_identity` | OIDC secrets: `SSO_<SLUG>_CLIENT_SECRET` env vars |
| Backups | `/var/data/ciwt/backups/` | `CIWT_BACKUP_DIR`, `CIWT_BACKUP_KEEP` (default 14) |

Always set `SECRET_KEY` (64 random characters). `/healthz` returns 200 only when the templates are present and
the database answers; it also reports the database backend and whether the SQLite folder is writable.

## Option A — Render (paid plan + disk)

`render.yaml` is a Blueprint for a **paid** web service with a 5 GB disk mounted at `/var/data`, health check
`/healthz`, a generated `SECRET_KEY`, and SQLite in WAL mode on the disk. On first boot the bundled
`ciwt_lms.db` is copied onto the disk; after that the disk copy is the live database and deploys never touch it.

1. Push the `refinement` branch (see LAUNCH_HANDOFF) and create a Blueprint from the repo in Render.
2. After the first deploy, open `/healthz` and check `"database": "ok"` and `"storage": {"writable": true, "persistent_hint": true}`.
3. Render snapshots disks daily. For an off-site copy, run `python tools/backup_db.py` from the Render Shell (or a
   scheduled job on the same service) and download `/var/data/ciwt/backups/*.db.gz`.
4. Keep `--workers 1 --threads 8` with SQLite. A disk can be attached to only one instance, so for horizontal
   scaling switch to PostgreSQL (comment block at the end of `render.yaml`).

## Option B — Docker / Docker Compose (school server, DoD-ready VM, Fly.io)

```bash
cp .env.example .env        # set SECRET_KEY
docker compose up -d --build
curl -fsS http://127.0.0.1:8000/healthz
```

The image runs as a non-root user and keeps all state in the named volume `ciwt-data` (`/var/data/ciwt`). The
`backup` service writes a verified, gzipped SQLite backup every 24 h and keeps 14. Put the app behind a TLS
reverse proxy (nginx, Caddy, IIS ARR); campus SSO needs HTTPS, because the SAML ACS and OIDC redirect URLs are
built from the forwarded scheme (`FORWARDED_ALLOW_IPS`).

On Fly.io: `fly volumes create ciwt_data --size 5`, mount it at `/var/data`, and use the same Dockerfile.

On a locked-down VM: build the image on a connected machine (`docker save ciwt-lms | gzip > ciwt-lms.tar.gz`),
then load it on the VM. The image needs no outbound internet unless you enable OIDC discovery or the AI tutor's
`NOVAK_AI_API_KEY` hook.

## Option C — plain VM with systemd (no Docker)

```bash
sudo mkdir -p /var/data/ciwt/{instance,backups} && sudo chown ciwt /var/data/ciwt -R
cp ciwt_lms.db /var/data/ciwt/ciwt_lms.db      # first time only
# /etc/systemd/system/ciwt.service → Environment=DATABASE_URL=sqlite:////var/data/ciwt/ciwt_lms.db
#   Environment=CIWT_INSTANCE_DIR=/var/data/ciwt/instance CIWT_SQLITE_WAL=1 SECRET_KEY=…
#   ExecStart=/opt/ciwt/venv/bin/gunicorn app:app --bind 127.0.0.1:8000 --workers 1 --threads 8
# crontab: 15 3 * * *  cd /opt/ciwt && DATABASE_URL=… venv/bin/python tools/backup_db.py --dest /var/data/ciwt/backups
```

## Backups and restore

- `python tools/backup_db.py` takes a consistent online snapshot (SQLite backup API, safe while the server runs),
  runs `PRAGMA integrity_check` on it, gzips it, and rotates old copies. With PostgreSQL it runs `pg_dump -Fc`.
- `python tools/backup_db.py --restore-check FILE.db.gz` proves a backup restores.
- Restore (SQLite): stop the app, `gunzip -c FILE.db.gz > /var/data/ciwt/ciwt_lms.db`, delete any
  `ciwt_lms.db-wal`/`-shm`, then start the app. With PostgreSQL: `pg_restore --clean --no-owner -d "$DATABASE_URL" FILE.pgdump`.

## PostgreSQL notes

SQLAlchemy creates the schema on first boot, and the start-up migrations add the tenant columns. The test suite
and the release checks in this repo run on SQLite. PostgreSQL support has not been load-tested here, so run
`tools/upgrade_check.py` and a smoke pass against a staging PostgreSQL database before you cut over.
To move existing SQLite data, export with `tools/backup_db.py` and import with a tool such as `pgloader`.

## Multi-tenant and SSO checklist

1. Sign in as the platform admin, open **Admin → Institutions**, and add the college or command (slug, email domain, colours, logo).
2. Give campus IT the SP metadata URL (`/sso/<slug>/saml/metadata.xml`) or the OIDC redirect URI shown on the page.
3. Paste the IdP settings into the SSO JSON, then use **Test campus sign-in**.
4. Share `https://<host>/t/<slug>`, the branded sign-in page with "Sign in with your campus ID".
