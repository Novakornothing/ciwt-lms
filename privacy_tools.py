"""Student-record export and deletion, and Helix data retention (pass 10).

The record is found from the database schema itself: every table with a foreign key to ``user.id``
is visited, then every table with a foreign key to a row that will be deleted, until nothing new is
found. So a table added later is covered without editing this file.

Column rules
------------
* A non-nullable foreign key to a deleted row means the row belongs to the student: it is exported
  and deleted (attempts, enrollments, time logs, messages, Helix sessions, buckets, consents …).
* ``OWNED_NULLABLE`` lists nullable columns that still mean ownership (a per-student content release
  would otherwise turn into a whole-class release if it were set to NULL): those rows are deleted too.
* Any other nullable foreign key ("updated_by", "activated_by", the audit log's user) is set to NULL,
  so shared records stay but no longer point at the person. Audit rows of the student also lose
  their IP address.
"""
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update, delete

OWNED_NULLABLE = {('content_release', 'user_id')}
SECRET_COLUMNS = {('user', 'password_hash'), ('api_token', 'token_hash'), ('api_token', 'token')}
SCRUB_ON_NULLIFY = {'audit_event': {'ip': ''}}


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _pk(table):
    cols = list(table.primary_key.columns)
    return cols[0] if len(cols) == 1 else None


def plan(db, user_id):
    """Return (delete, nullify): delete = {table: set(pk)}, nullify = {(table, column): set(pk)}."""
    md = db.metadata
    tables = {t.name: t for t in md.sorted_tables}
    doomed = {'user': {user_id}}
    nullify = {}
    changed = True
    while changed:
        changed = False
        for t in md.sorted_tables:
            pk = _pk(t)
            if pk is None:
                continue
            for col in t.columns:
                for fk in col.foreign_keys:
                    target = fk.column.table.name
                    ids = doomed.get(target)
                    if not ids:
                        continue
                    rows = db.session.execute(select(pk).where(col.in_(list(ids)))).scalars().all()
                    if not rows:
                        continue
                    if not col.nullable or (t.name, col.name) in OWNED_NULLABLE:
                        cur = doomed.setdefault(t.name, set())
                        new = set(rows) - cur
                        if new:
                            cur |= new
                            changed = True
                    else:
                        nullify.setdefault((t.name, col.name), set()).update(rows)
    # a row that is deleted anyway needs no nullify
    nullify = {k: v - doomed.get(k[0], set()) for k, v in nullify.items()}
    nullify = {k: v for k, v in nullify.items() if v}
    return doomed, nullify, tables


def _jsonable(v):
    if isinstance(v, datetime):
        return v.isoformat() + 'Z'
    if isinstance(v, (bytes, bytearray)):
        return None
    return v


def export(db, user_id):
    """Everything stored about the user, as a JSON-serialisable dict (secrets removed)."""
    doomed, nullify, tables = plan(db, user_id)
    out = {'generated_utc': _utcnow().isoformat() + 'Z', 'user_id': user_id, 'tables': {}, 'referenced_in': {}}
    for name, ids in sorted(doomed.items()):
        t = tables[name]
        pk = _pk(t)
        rows = db.session.execute(select(t).where(pk.in_(list(ids))).order_by(pk)).mappings().all()
        out['tables'][name] = [{k: _jsonable(v) for k, v in r.items() if (name, k) not in SECRET_COLUMNS} for r in rows]
    for (name, col), ids in sorted(nullify.items()):
        t = tables[name]
        pk = _pk(t)
        rows = db.session.execute(select(t).where(pk.in_(list(ids))).order_by(pk)).mappings().all()
        out['referenced_in'][f'{name}.{col}'] = [{k: _jsonable(v) for k, v in r.items() if (name, k) not in SECRET_COLUMNS} for r in rows]
    out['counts'] = {k: len(v) for k, v in out['tables'].items()}
    return out


def delete_record(db, user_id):
    """Delete the user's record (see module docstring). Returns {'deleted': {...}, 'anonymised': {...}}."""
    doomed, nullify, tables = plan(db, user_id)
    anonymised = {}
    for (name, col), ids in nullify.items():
        t = tables[name]
        pk = _pk(t)
        values = {col: None}
        values.update({c: v for c, v in SCRUB_ON_NULLIFY.get(name, {}).items() if c in t.c})
        db.session.execute(update(t).where(pk.in_(list(ids))).values(**values))
        anonymised[f'{name}.{col}'] = len(ids)
    if any(name == 'audit_event' for (name, _col) in nullify):
        import hashlib
        from sqlalchemy import text as _sql_text
        rows = db.session.execute(_sql_text('SELECT id, created_at, user_id, role, action, detail, path, ip, section_id FROM audit_event WHERE hash IS NOT NULL ORDER BY id')).mappings().all()
        prev = ''
        for r in rows:
            ca = r['created_at']
            if isinstance(ca, str):
                ca = datetime.fromisoformat(ca)
            ca_str = ca.replace(microsecond=0).isoformat() if ca else '' 
            raw = '|'.join(str(x if x is not None else '') for x in (
                prev, ca_str, r['user_id'], r['role'], r['action'], r['detail'], r['path'], r['ip'], r['section_id']))
            h = hashlib.sha256(raw.encode()).hexdigest()
            db.session.execute(_sql_text('UPDATE audit_event SET prev_hash=:p, hash=:h WHERE id=:i'), {'p': prev, 'h': h, 'i': r['id']})
            prev = h
    deleted = {}
    for t in reversed(db.metadata.sorted_tables):      # children before parents
        ids = doomed.get(t.name)
        if ids:
            db.session.execute(delete(t).where(_pk(t).in_(list(ids))))
            deleted[t.name] = len(ids)
    db.session.commit()
    return {'deleted': deleted, 'anonymised': anonymised}


# ------------------------------------------------------------------------------ Helix retention
def helix_retention_days(app):
    """0 or less keeps Helix data until someone deletes it."""
    try:
        return int(app.config.get('HELIX_RETENTION_DAYS', 365))
    except (TypeError, ValueError):
        return 365


def helix_cleanup(db, models, days, dry_run=False, now=None):
    """Delete Helix sessions (with their AOI buckets), attention events and accuracy-study records older
    than ``days``. Consent records are kept: they are the proof of what was agreed and when."""
    if days is None or days <= 0:
        return {'days': days, 'cutoff': None, 'sessions': 0, 'buckets': 0, 'events': 0, 'accuracy_records': 0, 'dry_run': dry_run}
    cutoff = (now or _utcnow()) - timedelta(days=days)
    S, B, E, R = models.HelixGazeSession, models.HelixAoiBucket, models.HelixAttentionEvent, models.HelixAccuracyRecord
    sids = [s for (s,) in db.session.query(S.id).filter(S.started_at < cutoff).all()]
    nb = B.query.filter(B.session_id.in_(sids or [0])).count()
    ev_col = E.created_at
    ne = E.query.filter(ev_col < cutoff).count()
    nr = R.query.filter(R.created_at < cutoff).count()
    out = {'days': days, 'cutoff': cutoff.isoformat() + 'Z', 'sessions': len(sids), 'buckets': nb, 'events': ne,
           'accuracy_records': nr, 'dry_run': dry_run}
    if not dry_run:
        if sids:
            B.query.filter(B.session_id.in_(sids)).delete(synchronize_session=False)
            S.query.filter(S.id.in_(sids)).delete(synchronize_session=False)
        E.query.filter(ev_col < cutoff).delete(synchronize_session=False)
        R.query.filter(R.created_at < cutoff).delete(synchronize_session=False)
        db.session.commit()
    return out


def to_json(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False, default=str)
