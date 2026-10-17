"""Pure aggregation helpers for Helix dashboards (no Flask / DB imports).

Everything here takes plain model rows or dicts so it is easy to unit test.
"""
import json
import re
from collections import OrderedDict

from .models import NON_READING_KEYS, NON_READING_LABELS, STATE_KEYS

HEAT_COLS = 20
HEAT_ROWS = 60
MAX_SEGMENTS = 1500
MAX_SEGMENT_MS = 120_000


def _int(v, default=0, lo=None, hi=None):
    try:
        out = int(float(v))
    except (TypeError, ValueError):
        out = default
    if lo is not None:
        out = max(lo, out)
    if hi is not None:
        out = min(hi, out)
    return out


def loads(raw, default):
    try:
        val = json.loads(raw or '')
    except (TypeError, ValueError):
        return default
    return val if isinstance(val, type(default)) else default


def is_reading_key(key, label=''):
    return (key or '') not in NON_READING_KEYS and (label or '') not in NON_READING_LABELS


def clean_segments(segments, limit=250):
    out = []
    for seg in (segments or [])[:limit]:
        if not isinstance(seg, dict):
            continue
        t0 = _int(seg.get('t0'), lo=0)
        t1 = _int(seg.get('t1'), t0, lo=t0)
        if t1 - t0 > MAX_SEGMENT_MS:
            t1 = t0 + MAX_SEGMENT_MS
        key = str(seg.get('aoi') or 'unknown')[:80]
        conf = seg.get('conf') or 0
        try:
            conf = round(max(0.0, min(1.0, float(conf))), 2)
        except (TypeError, ValueError):
            conf = 0.0
        out.append({
            't0': t0, 't1': t1, 'aoi': key,
            'label': str(seg.get('label') or STATE_KEYS.get(key) or key)[:240],
            'n': _int(seg.get('n'), lo=0, hi=5000),
            'conf': conf,
        })
    return out


def merge_timeline(existing_json, segments, limit=250):
    cur = loads(existing_json, [])
    cur.extend(clean_segments(segments, limit=limit))
    if len(cur) > MAX_SEGMENTS:
        cur = cur[-MAX_SEGMENTS:]
    return json.dumps(cur)


def clean_heat(heat):
    """Validate a client heat grid: {"cols":20,"rows":60,"cells":{"x,y":ms}}."""
    if not isinstance(heat, dict):
        return None
    cells = heat.get('cells') or {}
    if not isinstance(cells, dict):
        return None
    out = {}
    for k, v in list(cells.items())[:HEAT_COLS * HEAT_ROWS]:
        try:
            x, y = (int(p) for p in str(k).split(','))
        except ValueError:
            continue
        if 0 <= x < HEAT_COLS and 0 <= y < HEAT_ROWS:
            ms = _int(v, lo=0, hi=3_600_000)
            if ms:
                out[f'{x},{y}'] = ms
    return {'cols': HEAT_COLS, 'rows': HEAT_ROWS, 'cells': out}


def clean_layout(layout):
    out = []
    for item in (layout or [])[:80]:
        if not isinstance(item, dict):
            continue
        try:
            y0 = max(0.0, min(1.0, float(item.get('y0') or 0)))
            y1 = max(y0, min(1.0, float(item.get('y1') or y0)))
        except (TypeError, ValueError):
            continue
        out.append({
            'key': str(item.get('key') or '')[:80],
            'label': str(item.get('label') or '')[:240],
            'order': _int(item.get('order'), lo=0, hi=999),
            'kind': str(item.get('kind') or 'heading')[:20],
            'y0': round(y0, 4), 'y1': round(y1, 4),
        })
    return out


def accuracy_band(score, mode='gaze'):
    if mode == 'passive':
        return {'label': 'Passive', 'tone': 'info', 'help': 'Scroll/visibility signal - no camera'}
    score = score or 0
    if score >= 70:
        return {'label': 'Good', 'tone': 'success', 'help': 'Heading-level AOIs are reliable'}
    if score >= 45:
        return {'label': 'Fair', 'tone': 'warning', 'help': 'Use section-level trends only'}
    if score > 0:
        return {'label': 'Poor', 'tone': 'danger', 'help': 'Treat AOIs as rough; recalibration was suggested'}
    return {'label': 'Uncalibrated', 'tone': 'secondary', 'help': 'No validation result'}


def session_breakdown(sess):
    """Return ms per state for a session, falling back to its timeline for old rows."""
    total = sess.total_ms or 0
    parts = {
        'attentive': sess.attentive_ms or 0,
        'off_page': sess.off_page_ms or 0,
        'face_lost': sess.face_lost_ms or 0,
        'hidden': sess.hidden_ms or 0,
        'low_conf': sess.low_conf_ms or 0,
    }
    if not total:
        tl = loads(sess.timeline_json, [])
        for seg in tl:
            d = max(0, (seg.get('t1') or 0) - (seg.get('t0') or 0))
            key = seg.get('aoi') or ''
            if key in ('off_page', 'chrome'):
                parts['off_page'] += d
            elif key in ('_face_lost', '_camera_off'):
                parts['face_lost'] += d
            elif key in ('_hidden', '_other_tab', '_asleep'):
                parts['hidden'] += d
            elif key == '_low_conf':
                parts['low_conf'] += d
            elif key in ('_idle', '_paused'):
                parts['off_page'] += d
            else:
                parts['attentive'] += d
        total = sum(parts.values())
    parts['total'] = total
    return parts


def pct(part, whole):
    return int(round(100.0 * part / whole)) if whole else 0


def student_summaries(sessions, users, enrolled_ids=None):
    """One row per student with attention quality aggregates."""
    rows = OrderedDict()
    for s in sessions:
        r = rows.get(s.user_id)
        if r is None:
            u = users.get(s.user_id)
            r = rows[s.user_id] = {
                'user_id': s.user_id,
                'name': u.full_name if u else f'User {s.user_id}',
                'email': getattr(u, 'email', ''),
                'sessions': 0, 'gaze_sessions': 0, 'passive_sessions': 0,
                'lessons': set(), 'acc_sum': 0, 'acc_n': 0, 'last': None,
                'attentive': 0, 'off_page': 0, 'face_lost': 0, 'hidden': 0,
                'low_conf': 0, 'total': 0, 'recalibrations': 0, 'demo': False,
            }
        r['sessions'] += 1
        r['lessons'].add(s.lesson_id)
        if (s.mode or 'gaze') == 'passive':
            r['passive_sessions'] += 1
        else:
            r['gaze_sessions'] += 1
            if s.calibration_score:
                r['acc_sum'] += s.calibration_score
                r['acc_n'] += 1
        r['recalibrations'] += s.recalibrations or 0
        r['demo'] = r['demo'] or bool(getattr(s, 'is_demo', False))
        if s.started_at and (r['last'] is None or s.started_at > r['last']):
            r['last'] = s.started_at
        b = session_breakdown(s)
        for k in ('attentive', 'off_page', 'face_lost', 'hidden', 'low_conf', 'total'):
            r[k] += b[k]
    out = []
    for r in rows.values():
        r['lessons'] = len(r['lessons'])
        r['accuracy'] = int(round(r['acc_sum'] / r['acc_n'])) if r['acc_n'] else 0
        r['band'] = accuracy_band(r['accuracy'], 'passive' if not r['gaze_sessions'] else 'gaze')
        t = r['total']
        r['attentive_pct'] = pct(r['attentive'], t)
        r['off_pct'] = pct(r['off_page'], t)
        r['face_lost_pct'] = pct(r['face_lost'], t)
        r['hidden_pct'] = pct(r['hidden'], t)
        r['low_conf_pct'] = pct(r['low_conf'], t)
        r['minutes'] = round(t / 60000.0, 1)
        flags = []
        if r['face_lost_pct'] >= 25:
            flags.append('Camera often lost the face')
        if r['hidden_pct'] >= 30:
            flags.append('Tab frequently hidden')
        if r['gaze_sessions'] and r['accuracy'] and r['accuracy'] < 45:
            flags.append('Low calibration accuracy')
        r['flags'] = flags
        out.append(r)
    out.sort(key=lambda x: x['name'])
    if enrolled_ids is not None:
        seen = {r['user_id'] for r in out}
        missing = [uid for uid in enrolled_ids if uid not in seen]
        return out, missing
    return out, []


def aoi_rollup(buckets, layout_order=None):
    """Class dwell per AOI label with 'thin' flag (< 45% of a fair share)."""
    grouped = OrderedDict()
    total = 0
    for b in buckets:
        if not is_reading_key(b.aoi_key, b.aoi_label):
            continue
        key = b.aoi_label or b.aoi_key
        g = grouped.get(key)
        if g is None:
            g = grouped[key] = {'label': key, 'key': b.aoi_key, 'order': b.aoi_order or 0,
                                'kind': getattr(b, 'aoi_kind', None) or 'heading',
                                'dwell_ms': 0, 'visits': 0, 'students': set()}
        g['dwell_ms'] += b.dwell_ms or 0
        g['visits'] += b.visits or 0
        g['students'].add(b.user_id)
        g['order'] = min(g['order'], b.aoi_order or 0)
        total += b.dwell_ms or 0
    fair = (total / len(grouped)) if grouped else 0
    out = []
    peak = max([g['dwell_ms'] for g in grouped.values()] or [1]) or 1
    for g in grouped.values():
        out.append({
            'label': g['label'], 'key': g['key'], 'order': g['order'], 'kind': g['kind'],
            'dwell_ms': g['dwell_ms'], 'minutes': g['dwell_ms'] / 60000.0,
            'seconds': round(g['dwell_ms'] / 1000.0, 1),
            'visits': g['visits'], 'students': len(g['students']),
            'share': pct(g['dwell_ms'], total),
            'bar': int(round(100.0 * g['dwell_ms'] / peak)),
            'thin': bool(fair) and g['dwell_ms'] < fair * 0.45,
        })
    return out, total


def aoi_matrix(buckets, users):
    """Student x AOI share matrix (each student's row sums to ~100%)."""
    aois = OrderedDict()
    per = OrderedDict()
    for b in sorted(buckets, key=lambda x: (x.aoi_order or 0)):
        if not is_reading_key(b.aoi_key, b.aoi_label):
            continue
        label = b.aoi_label or b.aoi_key
        aois.setdefault(label, b.aoi_order or 0)
        row = per.setdefault(b.user_id, {})
        row[label] = row.get(label, 0) + (b.dwell_ms or 0)
    labels = [k for k, _ in sorted(aois.items(), key=lambda kv: kv[1])]
    rows = []
    for uid, cells in per.items():
        tot = sum(cells.values()) or 1
        u = users.get(uid)
        rows.append({
            'user_id': uid,
            'name': u.full_name if u else f'User {uid}',
            'cells': [{'label': lab, 'ms': cells.get(lab, 0), 'share': pct(cells.get(lab, 0), tot)}
                      for lab in labels],
        })
    rows.sort(key=lambda r: r['name'])
    # column means, so "thin for this student" can be judged against the class
    means = []
    for i, lab in enumerate(labels):
        vals = [r['cells'][i]['share'] for r in rows]
        means.append(int(round(sum(vals) / len(vals))) if vals else 0)
    return {'labels': labels, 'rows': rows, 'means': means}


def aggregate_heat(sessions):
    grid = [[0] * HEAT_COLS for _ in range(HEAT_ROWS)]
    n = 0
    for s in sessions:
        heat = loads(getattr(s, 'heat_json', '') or '{}', {})
        cells = heat.get('cells') or {}
        if cells:
            n += 1
        for k, v in cells.items():
            try:
                x, y = (int(p) for p in k.split(','))
            except ValueError:
                continue
            if 0 <= x < HEAT_COLS and 0 <= y < HEAT_ROWS:
                grid[y][x] += int(v or 0)
    peak = max(max(r) for r in grid) or 1
    norm = [[round(c / peak, 3) for c in row] for row in grid]
    return {'cols': HEAT_COLS, 'rows': HEAT_ROWS, 'grid': norm, 'sessions': n}


def merged_layout(sessions):
    """Average AOI y-positions across sessions (for heatmap labels)."""
    acc = OrderedDict()
    for s in sessions:
        for item in loads(getattr(s, 'layout_json', '') or '[]', []):
            lab = item.get('label')
            if not lab:
                continue
            a = acc.setdefault(lab, {'label': lab, 'order': item.get('order', 0), 'y0': 0, 'y1': 0, 'n': 0,
                                     'kind': item.get('kind', 'heading')})
            a['y0'] += item.get('y0', 0)
            a['y1'] += item.get('y1', 0)
            a['n'] += 1
    out = []
    for a in acc.values():
        out.append({'label': a['label'], 'order': a['order'], 'kind': a['kind'],
                    'y0': round(a['y0'] / a['n'], 4), 'y1': round(a['y1'] / a['n'], 4)})
    out.sort(key=lambda x: x['y0'])
    return out


def timeline_lanes(sessions, users, max_lanes=40):
    lanes = []
    for s in sessions[:max_lanes]:
        segs = loads(s.timeline_json, [])
        dur = max([seg.get('t1', 0) for seg in segs] or [0])
        u = users.get(s.user_id)
        lanes.append({
            'session_id': s.id,
            'name': u.full_name if u else f'User {s.user_id}',
            'user_id': s.user_id,
            'started': s.started_at.strftime('%Y-%m-%d %H:%M') if s.started_at else '',
            'mode': s.mode or 'gaze',
            'accuracy': s.calibration_score or 0,
            'duration_ms': dur,
            'segments': [[seg.get('t0', 0), seg.get('t1', 0), seg.get('aoi', ''), seg.get('label', '')]
                         for seg in segs],
        })
    return lanes


def drift_svg(drift_json, width=280, height=64):
    """Server-rendered sparkline of implicit-sample error (px) over a session.

    Grey = each click/tap/caret sample, blue = rolling median, dashed line = recalibration.
    Returns '' when there is nothing to draw.
    """
    from markupsafe import Markup, escape
    pts = loads(drift_json or '[]', [])
    if not isinstance(pts, list):
        return ''
    data = [p for p in pts if isinstance(p, dict)]
    errs = [p.get('err') for p in data if p.get('src') != 'recal' and isinstance(p.get('err'), (int, float))]
    if not errs:
        return ''
    top = max(200, max(errs))
    n = len(data)

    def x(i):
        return 6 + (i * (width - 12) / (n - 1) if n > 1 else (width - 12) / 2)

    def y(v):
        return round(height - 6 - (v / top) * (height - 16), 1)

    raw, med, marks, dots = [], [], [], []
    for i, p in enumerate(data):
        if p.get('src') == 'recal':
            marks.append(f'<line x1="{x(i):.1f}" x2="{x(i):.1f}" y1="4" y2="{height - 4}" stroke="#f59e0b" stroke-dasharray="3 3"><title>recalibrated</title></line>')
            continue
        raw.append(f'{x(i):.1f},{y(p.get("err") or 0)}')
        med.append(f'{x(i):.1f},{y(p.get("med") or 0)}')
        dots.append(f'<circle cx="{x(i):.1f}" cy="{y(p.get("err") or 0)}" r="2.2" fill="#0f172a"><title>{escape(str(p.get("src") or ""))}: {int(p.get("err") or 0)} px</title></circle>')
    label = f'Implicit-sample error over the session: median {sorted(errs)[len(errs) // 2]} px across {len(errs)} samples'
    svg = (f'<svg class="hx-drift" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{escape(label)}">'
           f'<text x="4" y="10" font-size="9" fill="#64748b">{int(top)} px</text>'
           + ''.join(marks)
           + f'<polyline fill="none" stroke="#94a3b8" stroke-width="1" points="{" ".join(raw)}"/>'
           + f'<polyline fill="none" stroke="#0ea5e9" stroke-width="2.5" points="{" ".join(med)}"/>'
           + ''.join(dots) + '</svg>')
    return Markup(svg)


def median_or_none(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    h = len(vals) // 2
    return round(vals[h] if len(vals) % 2 else (vals[h - 1] + vals[h]) / 2, 1)


def reading_recap(aois, total_ms, n_sections=None, sessions=()):
    """Student-facing, encouraging summary of their own reading on one lesson.

    aois: aoi_rollup() rows for this student + lesson. Never compares with classmates and never
    uses words like 'inattentive'; unmeasured time is described as unmeasured, not as a fault.
    """
    heads = [a for a in aois if (a.get('kind') or 'heading') == 'heading']
    read = [a for a in heads if a['dwell_ms'] >= 3000]
    n_total = max(n_sections or 0, len(heads)) or None
    minutes = round(total_ms / 60000.0, 1)
    out = {'minutes': minutes, 'sections_read': len(read), 'sections_total': n_total, 'sessions': len(sessions),
           'top': None, 'second_look': [], 'headline': '', 'notes': []}
    if not total_ms:
        out['headline'] = 'No reading time recorded yet for this lesson — that is completely fine.'
        return out
    if n_total and len(read) >= n_total:
        out['headline'] = f'Great coverage: you spent time on every section ({n_total}) over {minutes} min.'
    elif n_total:
        out['headline'] = f'Nice work: {minutes} min of reading across {len(read)} of {n_total} sections.'
    else:
        out['headline'] = f'Nice work: {minutes} min of reading on this lesson.'
    if heads:
        top = max(heads, key=lambda a: a['dwell_ms'])
        out['top'] = {'label': top['label'], 'key': top['key'], 'seconds': top['seconds']}
    thin = sorted([a for a in heads if a.get('thin')], key=lambda a: a['dwell_ms'])[:3]
    out['second_look'] = [{'label': a['label'], 'key': a['key'], 'seconds': a['seconds']} for a in thin]
    lost = sum((getattr(s, 'face_lost_ms', 0) or 0) + (getattr(s, 'low_conf_ms', 0) or 0) for s in sessions)
    tracked = sum(getattr(s, 'total_ms', 0) or 0 for s in sessions)
    if tracked and lost / tracked > 0.25:
        out['notes'].append('Some of your time was not measured (the camera could not see your eyes clearly). '
                            'That is normal and never counts against you.')
    if out['second_look']:
        out['notes'].append('Short sections are fine if you already know the material; a quick skim is all it takes.')
    return out


# ---------------------------------------------------------------- pass 10: accuracy study
def _float(v, default=None, lo=None, hi=None):
    try:
        out = float(v)
    except (TypeError, ValueError):
        return default
    if out != out:   # NaN
        return default
    if lo is not None:
        out = max(lo, out)
    if hi is not None:
        out = min(hi, out)
    return round(out, 2)


_BROWSER_RE = re.compile(r'^(Chrome|Chrome iOS|Edge|Firefox|Safari|Samsung|Opera|Other)( \d{1,3})?$')


def browser_tag(v):
    """Browser family + major version only (e.g. 'Chrome 141'); anything else becomes 'Other'."""
    v = str(v or '').strip()[:30]
    return v if _BROWSER_RE.match(v) else 'Other'


def res_bucket(res):
    """Camera resolution bucket by the long side of the delivered video (what the model saw)."""
    try:
        w, h = (int(x) for x in str(res).split('x'))
    except (TypeError, ValueError):
        return 'unknown'
    long_side = max(w, h)
    if long_side >= 1700:
        return '1080p'
    if long_side >= 1100:
        return '720p'
    if long_side >= 600:
        return '480p'
    return '<480p'


def _quantile(vals, q):
    vals = sorted(vals)
    if not vals:
        return None
    pos = (len(vals) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(vals) - 1)
    return round(vals[lo] + (vals[hi] - vals[lo]) * (pos - lo), 2)


def sign_test_p(wins, losses):
    """Exact two-sided sign test (ties dropped by the caller)."""
    from math import comb
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    p = sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return round(min(1.0, 2 * p), 4)


STUDY_MIN_USERS = 5          # below this, a group's numbers are shown greyed and flagged
STUDY_MIN_PAIRS = 10         # paired users needed before any default change is suggested
STUDY_MIN_GAIN_DEG = 0.5     # and the median paired gain must be at least this


def _metric(r):
    """Degrees when the distance estimate exists, else None (px are shown separately)."""
    return r.error_deg if r.error_deg is not None else None


def study_groups(records, key=('device', 'browser_family', 'res')):
    """Real accuracy per group. Each user counts once per group: per-user median first, then the
    median (and IQR) across users, so one enthusiastic participant cannot dominate a group."""
    groups = {}
    for r in records:
        k = {'device': r.device or 'desktop', 'browser': r.browser or 'Other',
             'browser_family': re.sub(r' \d+$', '', r.browser or 'Other'), 'res': res_bucket(r.camera_res),
             'engine': r.engine or '', 'method': r.arm_method or ''}
        gk = tuple(k[x] for x in key)
        groups.setdefault(gk, []).append(r)
    out = []
    for gk, rs in groups.items():
        per_user_deg, per_user_px, valid, ms = {}, {}, 0, []
        for r in rs:
            if not r.valid:
                continue
            valid += 1
            if _metric(r) is not None:
                per_user_deg.setdefault(r.user_id, []).append(_metric(r))
            if r.error_px is not None:
                per_user_px.setdefault(r.user_id, []).append(r.error_px)
            if r.calib_ms and r.kind != 'recheck':
                ms.append(r.calib_ms)
        ud = [median_or_none(v) for v in per_user_deg.values()]
        up = [median_or_none(v) for v in per_user_px.values()]
        users = {r.user_id for r in rs}
        out.append({
            'key': dict(zip(key, gk)), 'records': len(rs), 'users': len(users), 'valid_pct': pct(valid, len(rs)),
            'median_deg': median_or_none(ud), 'q1_deg': _quantile(ud, 0.25), 'q3_deg': _quantile(ud, 0.75),
            'users_deg': len(ud), 'median_px': median_or_none(up),
            'median_calib_s': round(median_or_none(ms) / 1000.0, 1) if ms else None,
            'enough': len(per_user_deg) >= STUDY_MIN_USERS,
        })
    out.sort(key=lambda g: (-g['users'], -g['records']))
    return out


def arm_comparison(records, device, factor):
    """Within-user comparison on one device class. factor 'method': dots vs follow (follow+dots
    counts as follow, it started that way); factor 'hires': 1080p requested vs not.
    Only full calibrations (not re-checks). Returns paired stats and an honest verdict."""
    def arm(r):
        if factor == 'method':
            return 'follow' if (r.arm_method or '').startswith('follow') else ('dots' if r.arm_method == 'dots' else None)
        return 'on' if r.arm_hires else 'off'
    a_name, b_name = ('dots', 'follow') if factor == 'method' else ('off', 'on')
    per = {}
    for r in records:
        if (r.device or 'desktop') != device or not r.valid or r.kind == 'recheck' or _metric(r) is None:
            continue
        a = arm(r)
        if a is None:
            continue
        per.setdefault(r.user_id, {}).setdefault(a, []).append(_metric(r))
    diffs = []
    arm_vals = {a_name: [], b_name: []}
    for uid, d in per.items():
        for a in (a_name, b_name):
            if d.get(a):
                arm_vals[a].append(median_or_none(d[a]))
        if d.get(a_name) and d.get(b_name):
            diffs.append(median_or_none(d[a_name]) - median_or_none(d[b_name]))   # >0: b better
    wins = len([x for x in diffs if x > 0])
    losses = len([x for x in diffs if x < 0])
    p = sign_test_p(wins, losses)
    med_gain = median_or_none(diffs)
    if len(diffs) < STUDY_MIN_PAIRS:
        verdict = f'Not enough paired data ({len(diffs)} of {STUDY_MIN_PAIRS} users tried both). Keep the current default.'
        suggest = None
    elif p < 0.05 and med_gain is not None and med_gain >= STUDY_MIN_GAIN_DEG:
        verdict = f'"{b_name}" was better for {wins} of {wins + losses} users (median {med_gain}\u00b0, sign test p={p}).'
        suggest = b_name
    elif p < 0.05 and med_gain is not None and med_gain <= -STUDY_MIN_GAIN_DEG:
        verdict = f'"{a_name}" was better for {losses} of {wins + losses} users (median {-med_gain}\u00b0, sign test p={p}).'
        suggest = a_name
    else:
        verdict = f'No clear difference ({wins} better / {losses} worse, median {med_gain}\u00b0, p={p}). Keep the current default.'
        suggest = None
    return {'device': device, 'factor': factor, 'a': a_name, 'b': b_name, 'pairs': len(diffs), 'wins_b': wins,
            'wins_a': losses, 'median_gain_deg': med_gain, 'p': p, 'verdict': verdict, 'suggest': suggest,
            'median_a': median_or_none(arm_vals[a_name]), 'n_a': len(arm_vals[a_name]),
            'median_b': median_or_none(arm_vals[b_name]), 'n_b': len(arm_vals[b_name])}


def calibration_class_rows(sessions, users):
    """Instructor view: per-student calibration quality and time (camera sessions only)."""
    per = {}
    for s in sessions:
        if (s.mode or 'gaze') != 'gaze':
            continue
        r = per.setdefault(s.user_id, {'sessions': 0, 'scores': [], 'deg': [], 'ms': [], 'recals': 0, 'rechecks': 0,
                                       'recheck_deg': None, 'recheck_px': None, 'losses': 0, 'sleeps': 0, 'tabs': 0,
                                       'modes': {}, 'devices': set(), 'last': None, 'demo': False, 'res': set()})
        r['sessions'] += 1
        if s.calibration_score:
            r['scores'].append(s.calibration_score)
        if s.validation_error_deg:
            r['deg'].append(s.validation_error_deg)
        if s.calib_ms:
            r['ms'].append(s.calib_ms)
        r['recals'] += s.recalibrations or 0
        r['rechecks'] += s.rechecks or 0
        if s.rechecks and (r.get('recheck_at') is None or (s.started_at and s.started_at >= r['recheck_at'])):
            r['recheck_deg'], r['recheck_px'], r['recheck_at'] = s.recheck_error_deg, s.recheck_error_px, s.started_at
        r['losses'] += s.camera_losses or 0
        r['sleeps'] += s.sleeps or 0
        r['tabs'] += s.tab_yields or 0
        if s.calib_mode:
            r['modes'][s.calib_mode] = r['modes'].get(s.calib_mode, 0) + 1
        r['devices'].add(s.device or 'desktop')
        if s.camera_res:
            r['res'].add(s.camera_res)
        if s.started_at and (r['last'] is None or s.started_at > r['last']):
            r['last'] = s.started_at
        r['demo'] = r['demo'] or bool(getattr(s, 'is_demo', False))
    rows = []
    for uid, r in per.items():
        u = users.get(uid)
        med = median_or_none(r['scores'])
        rows.append({'user_id': uid, 'name': u.full_name if u else f'User {uid}', 'sessions': r['sessions'],
                     'median_score': med, 'band': accuracy_band(med or 0), 'median_deg': median_or_none(r['deg']),
                     'median_calib_s': round(median_or_none(r['ms']) / 1000.0, 1) if r['ms'] else None,
                     'recals': r['recals'], 'rechecks': r['rechecks'], 'recheck_deg': r['recheck_deg'],
                     'recheck_px': r['recheck_px'], 'camera_losses': r['losses'], 'sleeps': r['sleeps'],
                     'tab_yields': r['tabs'], 'modes': r['modes'], 'devices': sorted(r['devices']),
                     'res': sorted(r['res']), 'last': r['last'], 'demo': r['demo']})
    rows.sort(key=lambda x: (x['median_score'] is None, x['median_score'] or 0))
    return rows
