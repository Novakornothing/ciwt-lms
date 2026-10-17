"""Clearly-labelled demo data for Helix dashboards (is_demo=True on every row)."""
import json
import random
import re
from datetime import datetime, timedelta, timezone

from .analytics import HEAT_COLS, HEAT_ROWS
from .models import ENGINE, POLICY_VERSION, STATE_KEYS


def utcnow():
    """Naive UTC now. Replaces the deprecated datetime.utcnow(); stored columns stay naive UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _headings(html):
    labels = []
    for raw in re.findall(r'<h[2-4][^>]*>(.*?)</h[2-4]>', html or '', flags=re.I | re.S):
        lab = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', raw)).strip()
        if lab and lab not in labels:
            labels.append(lab[:240])
    return labels[:9] or ['Lesson body', 'Practice standard for this lesson', 'Beyond the quiz']


def seed_demo(db, m, section, students, lessons):
    rnd = random.Random(1337 + section.id)
    if not lessons or not students:
        return 0
    created = 0
    for li, les in enumerate(lessons):
        labels = _headings(les.content)
        n = len(labels)
        layout = [{'key': f'h{i}-demo', 'label': lab, 'order': i, 'kind': 'heading',
                   'y0': round(i / n, 4), 'y1': round((i + 1) / n, 4)} for i, lab in enumerate(labels)]
        for si, stu in enumerate(students):
            if (si + li) % 7 == 6:
                continue  # not everyone opts in for every lesson
            passive = si % 5 == 4
            mode = 'passive' if passive else 'gaze'
            acc = 0 if passive else max(30, min(92, int(rnd.gauss(70, 14))))
            started = utcnow() - timedelta(days=6 - li, hours=si, minutes=rnd.randint(0, 50))
            t = 0
            timeline, buckets = [], {}
            heat = {}
            totals = dict(attentive=0, off_page=0, face_lost=0, hidden=0, low_conf=0)
            skip_aoi = {3, 4} if si == 2 else set()
            for hi, lab in enumerate(labels):
                base = rnd.uniform(9, 28) * 1000 * (1.25 if hi in (1, 2) else 1.0)
                if hi in skip_aoi:
                    base = rnd.uniform(0.6, 1.5) * 1000
                if hi == n - 1:
                    base *= 0.45  # end-of-lesson headings get skimmed - a realistic pattern
                dwell = int(base)
                visits = 1 + rnd.randint(0, 2)
                key = f'h{hi}-demo'
                timeline.append({'t0': t, 't1': t + dwell, 'aoi': key, 'label': lab,
                                 'n': max(4, dwell // 60), 'conf': round(rnd.uniform(.55, .95), 2)})
                buckets[key] = {'label': lab, 'order': hi, 'dwell': dwell, 'visits': visits, 'first': t, 'last': t + dwell}
                totals['attentive'] += dwell
                # heat: mostly left/centre text column of the AOI's vertical band
                y0, y1 = int(hi / n * HEAT_ROWS), max(int(hi / n * HEAT_ROWS) + 1, int((hi + 1) / n * HEAT_ROWS))
                for _ in range(max(3, dwell // 700)):
                    x = min(HEAT_COLS - 1, max(0, int(rnd.gauss(7.5, 3.5))))
                    y = rnd.randint(y0, y1 - 1)
                    heat[f'{x},{y}'] = heat.get(f'{x},{y}', 0) + 60
                t += dwell
                # interleave realistic non-reading states
                roll = rnd.random()
                if roll < 0.18 and not passive:
                    st, d = '_face_lost', rnd.randint(1500, 6000)
                    totals['face_lost'] += d
                elif roll < 0.30:
                    st, d = '_hidden', rnd.randint(3000, 15000)
                    totals['hidden'] += d
                elif roll < 0.45:
                    st, d = 'off_page', rnd.randint(800, 4000)
                    totals['off_page'] += d
                elif roll < 0.52 and not passive:
                    st, d = '_low_conf', rnd.randint(1000, 4000)
                    totals['low_conf'] += d
                else:
                    st, d = None, 300
                if st:
                    timeline.append({'t0': t, 't1': t + d, 'aoi': st, 'label': STATE_KEYS[st], 'n': d // 60, 'conf': 0.2})
                    b = buckets.setdefault(st, {'label': STATE_KEYS[st], 'order': 999, 'dwell': 0, 'visits': 0,
                                                'first': t, 'last': t})
                    b['dwell'] += d
                    b['visits'] += 1
                    b['last'] = t + d
                t += d
            total = sum(totals.values())
            sess = m.HelixGazeSession(
                user_id=stu.id, section_id=section.id, lesson_id=les.id,
                engine='passive' if passive else ENGINE, consent_version=POLICY_VERSION,
                started_at=started, ended_at=started + timedelta(milliseconds=t), status='ended',
                calibration_points=0 if passive else 9, calibration_score=acc,
                validation_error_px=0 if passive else int(40 + (100 - acc) * 3.2),
                validation_precision_px=0 if passive else int(20 + (100 - acc) * 1.1),
                recalibrations=1 if acc and acc < 50 else 0,
                viewport_w=390 if passive else 1440, viewport_h=844 if passive else 900,
                sample_count=t // (250 if passive else 45), mode=mode,
                device='mobile' if passive else 'desktop',
                total_ms=total, attentive_ms=totals['attentive'], off_page_ms=totals['off_page'],
                face_lost_ms=totals['face_lost'], hidden_ms=totals['hidden'], low_conf_ms=totals['low_conf'],
                timeline_json=json.dumps(timeline),
                heat_json=json.dumps({'cols': HEAT_COLS, 'rows': HEAT_ROWS, 'cells': heat}),
                layout_json=json.dumps(layout), last_seq=3, last_seen_at=started + timedelta(milliseconds=t),
                client_uuid=f'demo-{section.id}-{les.id}-{stu.id}', is_demo=True,
            )
            db.session.add(sess)
            db.session.flush()
            for key, b in buckets.items():
                db.session.add(m.HelixAoiBucket(
                    session_id=sess.id, user_id=stu.id, section_id=section.id, lesson_id=les.id,
                    aoi_key=key, aoi_label=b['label'], aoi_order=b['order'],
                    aoi_kind='state' if key in STATE_KEYS else 'heading',
                    dwell_ms=b['dwell'], visits=b['visits'], first_ms=b['first'], last_ms=b['last']))
            created += 1
    db.session.commit()
    return created
