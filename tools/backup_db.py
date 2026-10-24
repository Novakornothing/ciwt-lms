#!/usr/bin/env python3
"""Consistent, rotating database backups for CIWT LMS.

SQLite: uses the online backup API (safe while the server is running, WAL included), then gzips and verifies
the copy with PRAGMA integrity_check. PostgreSQL: runs pg_dump --format=custom. Keeps the newest --keep files.

  python tools/backup_db.py                         # DATABASE_URL or ./ciwt_lms.db -> $CIWT_BACKUP_DIR or ./backups
  python tools/backup_db.py --dest /var/data/ciwt/backups --keep 14
  python tools/backup_db.py --restore-check backups/ciwt-20261024-0300.db.gz

Never writes to the source database. Exit code is non-zero if the backup or its verification fails, so cron or a
Render cron job can alert on it.
"""
import argparse
import gzip
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sqlite_path(url):
    """sqlite:///relative.db or sqlite:////abs/path.db -> filesystem path; None for other databases."""
    return url[len('sqlite:///'):] if url.startswith('sqlite:///') else None


def check_sqlite(path):
    con = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    try:
        ok = con.execute('PRAGMA integrity_check').fetchone()[0]
        users = con.execute('SELECT count(*) FROM user').fetchone()[0]
    finally:
        con.close()
    return ok, users


def backup_sqlite(src, dest_dir, stamp):
    if not os.path.isfile(src):
        sys.exit(f'database not found: {src}')
    out = dest_dir / f'ciwt-{stamp}.db.gz'
    with tempfile.TemporaryDirectory() as tmp:
        snap = os.path.join(tmp, 'snap.db')
        s = sqlite3.connect(f'file:{src}?mode=ro', uri=True)
        d = sqlite3.connect(snap)
        with d:
            s.backup(d)
        s.close()
        d.close()
        ok, users = check_sqlite(snap)
        if ok != 'ok':
            sys.exit(f'integrity_check failed on the snapshot: {ok}')
        with open(snap, 'rb') as fi, gzip.open(out, 'wb', compresslevel=6) as fo:
            shutil.copyfileobj(fi, fo)
    return out, f'{users} users, integrity ok'


def backup_pg(url, dest_dir, stamp):
    out = dest_dir / f'ciwt-{stamp}.pgdump'
    url = url.replace('postgresql+psycopg://', 'postgresql://').replace('postgres://', 'postgresql://')
    r = subprocess.run(['pg_dump', '--format=custom', '--no-owner', '--file', str(out), url], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('pg_dump failed: ' + r.stderr.strip()[:400])
    return out, 'pg_dump custom format (restore with pg_restore --clean --no-owner -d $DATABASE_URL FILE)'


def rotate(dest_dir, keep):
    files = sorted([p for p in dest_dir.glob('ciwt-*') if p.suffix in ('.gz', '.pgdump')], key=lambda p: p.stat().st_mtime)
    for p in files[:-keep] if keep > 0 else []:
        p.unlink()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--url', default=os.environ.get('DATABASE_URL') or 'sqlite:///' + str(ROOT / 'ciwt_lms.db'))
    ap.add_argument('--dest', default=os.environ.get('CIWT_BACKUP_DIR') or str(ROOT / 'backups'))
    ap.add_argument('--keep', type=int, default=int(os.environ.get('CIWT_BACKUP_KEEP', '14')))
    ap.add_argument('--restore-check', metavar='FILE', help='decompress a .db.gz to a temp file and verify it')
    a = ap.parse_args(argv)
    if a.restore_check:
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, 'r.db')
            with gzip.open(a.restore_check, 'rb') as fi, open(p, 'wb') as fo:
                shutil.copyfileobj(fi, fo)
            ok, users = check_sqlite(p)
        print(f'{a.restore_check}: integrity {ok}, {users} users')
        return 0 if ok == 'ok' else 1
    dest = Path(a.dest)
    dest.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    path = sqlite_path(a.url)
    out, note = backup_sqlite(path, dest, stamp) if path else backup_pg(a.url, dest, stamp)
    rotate(dest, a.keep)
    print(f'backup written: {out} ({out.stat().st_size // 1024} KiB; {note})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
