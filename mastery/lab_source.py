"""Live-lab adapter for process diagnosis (pass 12, after the labs merge).

``make_lab_events(LabProgress, LabEvent)`` returns ``lab_events(user_id, section_id) -> {lab_id: [LabEvent, ...]}``:
the labs the student worked *in that class* (``lab_progress.section_id``), each with the events of its
**latest attempt** (``lab_event.attempt`` = 1 + resets before it), in ``seq`` order. Read-only.
``lab_def(get_lab)`` returns ``lab_id -> {'id', 'title', 'objectives'}`` for ``diagnose(..., lab=...)``.
"""
from sqlalchemy import func


def make_lab_events(LabProgress, LabEvent, limit_labs=40, limit_events=600):
    def lab_events(user_id, section_id):
        rows = (LabProgress.query.filter_by(user_id=user_id, section_id=section_id)
                .order_by(LabProgress.updated_at.desc()).limit(limit_labs).all())
        out = {}
        for r in rows:
            latest = (LabEvent.query.with_entities(func.max(LabEvent.attempt))
                      .filter_by(user_id=user_id, lab_id=r.lab_id).scalar())
            if not latest:
                continue
            evs = (LabEvent.query.filter_by(user_id=user_id, lab_id=r.lab_id, attempt=latest)
                   .order_by(LabEvent.seq).limit(limit_events).all())
            if evs:
                out[r.lab_id] = evs
        return out
    return lab_events


def lab_def(get_lab):
    def one(lab_id):
        lab = get_lab(lab_id)
        if not lab:
            return None
        return {'id': lab['id'], 'title': lab.get('title') or lab['id'], 'kind': lab.get('kind'),
                'objectives': [{'id': o['id'], 'text': o.get('text', o['id'])} for o in lab.get('objectives') or []]}
    return one
