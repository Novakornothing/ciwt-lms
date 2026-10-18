"""CIWT gradebook: per-section grade grid for instructors, grades/progress for students.

Built on the existing models (KnowledgeTest/TestAttempt, Quiz/QuizAttempt,
LabCompletion, Enrollment). Adds two small tables: per-section settings
(category weights + best/latest policy) and per-cell instructor overrides
(score override or excused, with a required note and audit trail).

Pass 3: an editable letter scale, late-penalty rules with per-item due dates, quiz
attempts tied to the class they were taken in (older attempts without a class are
counted only inside the student's enrollment window), and a signature-checked cache
plus pagination for large classes.

Helix attention data is deliberately NOT an input to any grade.
"""
import csv
import json
import math
import statistics
import threading
from datetime import datetime, timedelta, timezone
from io import StringIO
from types import SimpleNamespace

from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required


def utcnow():
    """Naive UTC now. Replaces the deprecated datetime.utcnow(); stored columns stay naive UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

CATEGORIES = [
    ('tests', 'Knowledge tests'),
    ('skills', 'Skills exams'),
    ('quizzes', 'Progress quizzes'),
    ('labs', 'Live labs'),
]
# labs weight defaults to 0 so existing grades are unchanged until an instructor opts in
DEFAULT_WEIGHTS = {'tests': 70, 'skills': 30, 'quizzes': 0, 'labs': 0}
DEFAULT_SCALE = [(93, 'A'), (90, 'A-'), (87, 'B+'), (83, 'B'), (80, 'B-'), (77, 'C+'), (73, 'C'), (70, 'C-'), (60, 'D'), (0, 'F')]
PER_PAGE_CHOICES = (25, 50, 100, 200)
_cache = {}
_gb_cache = {}           # (section_id,) -> (signature, data)
_gb_lock = threading.Lock()
MIGRATIONS = [
    ('gradebook_setting', 'letter_scale', 'TEXT'),
    ('gradebook_setting', 'late_per_day', 'FLOAT DEFAULT 0'),
    ('gradebook_setting', 'late_max', 'FLOAT DEFAULT 0'),
    ('gradebook_setting', 'late_grace_hours', 'INTEGER DEFAULT 0'),
    ('gradebook_setting', 'weight_labs', 'INTEGER DEFAULT 0'),
]


def ensure_schema(db):
    """Add pass-3 columns to an existing database without touching data."""
    from sqlalchemy import inspect, text
    try:
        insp = inspect(db.engine)
        tables = set(insp.get_table_names())
        with db.engine.begin() as conn:
            for table, col, ddl in MIGRATIONS:
                if table in tables and col not in {c['name'] for c in insp.get_columns(table)}:
                    conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {col} {ddl}'))
    except Exception as exc:  # pragma: no cover
        print('Gradebook schema note:', exc)


def define_models(db):
    if 'm' in _cache:
        return _cache['m']

    class GradebookSetting(db.Model):
        __tablename__ = 'gradebook_setting'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), unique=True, nullable=False)
        weight_tests = db.Column(db.Integer, default=DEFAULT_WEIGHTS['tests'])
        weight_skills = db.Column(db.Integer, default=DEFAULT_WEIGHTS['skills'])
        weight_quizzes = db.Column(db.Integer, default=DEFAULT_WEIGHTS['quizzes'])
        weight_labs = db.Column(db.Integer, default=DEFAULT_WEIGHTS['labs'])
        policy = db.Column(db.String(10), default='best')  # best | latest
        pass_mark = db.Column(db.Integer, default=80)
        updated_at = db.Column(db.DateTime, default=utcnow)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
        letter_scale = db.Column(db.Text)                 # JSON [[min, label], ...] high to low; NULL = default
        late_per_day = db.Column(db.Float, default=0)     # percentage points off per (started) day late
        late_max = db.Column(db.Float, default=0)         # cap on the late deduction (points)
        late_grace_hours = db.Column(db.Integer, default=0)

    class GradeDue(db.Model):
        """Optional due date for one graded item in one class (drives late penalties)."""
        __tablename__ = 'grade_due'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        item_type = db.Column(db.String(10), nullable=False)  # test | quiz
        item_id = db.Column(db.Integer, nullable=False)
        due_at = db.Column(db.DateTime, nullable=False)
        updated_at = db.Column(db.DateTime, default=utcnow)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    class GradeOverride(db.Model):
        __tablename__ = 'grade_override'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        item_type = db.Column(db.String(10), nullable=False)  # test | quiz
        item_id = db.Column(db.Integer, nullable=False)
        score = db.Column(db.Float)
        excused = db.Column(db.Boolean, default=False)
        note = db.Column(db.String(300), default='')
        updated_at = db.Column(db.DateTime, default=utcnow)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    _cache['m'] = SimpleNamespace(GradebookSetting=GradebookSetting, GradeOverride=GradeOverride, GradeDue=GradeDue)
    return _cache['m']


# ---------------------------------------------------------------- pure computation
def parse_scale(raw):
    """JSON or list -> validated [(min, label)] high-to-low ending at 0, or the default scale."""
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        rows = []
        for item in data or []:
            lo, lab = (item['min'], item['label']) if isinstance(item, dict) else (item[0], item[1])
            lo, lab = float(lo), str(lab).strip()[:4]
            if lab and 0 <= lo <= 100:
                rows.append((lo, lab))
        rows = sorted({lo: lab for lo, lab in rows}.items(), key=lambda x: -x[0])
        if not rows:
            return list(DEFAULT_SCALE)
        if rows[-1][0] > 0:
            rows.append((0, 'F'))
        return [(int(lo) if float(lo).is_integer() else lo, lab) for lo, lab in rows]
    except (TypeError, ValueError, KeyError, IndexError):
        return list(DEFAULT_SCALE)


def letter(score, pass_mark=80, scale=None):
    if score is None:
        return '—'
    for cut, lab in (scale or DEFAULT_SCALE):
        if score >= cut:
            return lab
    return (scale or DEFAULT_SCALE)[-1][1]


def letter_counts(grades, scale):
    out = []
    for lo, lab in scale:
        out.append({'label': lab, 'min': lo, 'n': 0})
    for g in grades:
        for b in out:
            if g >= b['min']:
                b['n'] += 1
                break
    return out


def late_penalty(completed_at, due_at, per_day, cap, grace_hours=0):
    """(days_late, points_off) for one attempt. Each started day after due + grace costs per_day."""
    if not completed_at or not due_at or not per_day:
        return 0, 0.0
    over = completed_at - (due_at + timedelta(hours=grace_hours or 0))
    if over.total_seconds() <= 0:
        return 0, 0.0
    days = math.ceil(over.total_seconds() / 86400.0)
    off = days * float(per_day)
    if cap:
        off = min(off, float(cap))
    return days, round(off, 1)


def in_window(when, enrolled_at, end_date):
    """Whether an attempt with no class recorded falls inside this enrollment."""
    if when is None:
        return False
    if enrolled_at and when < enrolled_at - timedelta(hours=12):
        return False
    if end_date and when.date() > end_date + timedelta(days=1):
        return False
    return True


def pick(attempt_scores, policy):
    """attempt_scores: list of (completed_at, score) newest-first or any order."""
    vals = [(t or datetime.min, s) for t, s in attempt_scores if s is not None]
    if not vals:
        return None
    if policy == 'latest':
        return sorted(vals, key=lambda x: x[0])[-1][1]
    return max(s for _, s in vals)


def weighted_grade(cat_avgs, weights):
    """Weighted mean over categories that have data; weights renormalised."""
    num = den = 0.0
    for key, avg in cat_avgs.items():
        w = weights.get(key, 0) or 0
        if avg is None or w <= 0:
            continue
        num += avg * w
        den += w
    return round(num / den, 1) if den else None


def describe(scores):
    s = [x for x in scores if x is not None]
    if not s:
        return {'n': 0, 'mean': None, 'median': None, 'low': None, 'high': None, 'sd': None}
    return {'n': len(s), 'mean': round(sum(s) / len(s), 1), 'median': round(statistics.median(s), 1),
            'low': round(min(s), 1), 'high': round(max(s), 1),
            'sd': round(statistics.pstdev(s), 1) if len(s) > 1 else 0.0}


def histogram(scores, edges=(0, 60, 70, 80, 90, 101)):
    s = [x for x in scores if x is not None]
    out = []
    for lo, hi in zip(edges, edges[1:]):
        n = len([x for x in s if lo <= x < hi])
        out.append({'label': f'{lo}–{hi - 1}' if hi <= 100 else f'{lo}–100', 'n': n, 'lo': lo})
    peak = max([b['n'] for b in out] or [1]) or 1
    for b in out:
        b['pct'] = int(round(100.0 * b['n'] / peak))
    return out


def register(app, db, deps):
    """deps: User, ClassSection, Enrollment, KnowledgeTest, TestAttempt, Quiz, QuizAttempt,
    Module, LabCompletion, can_access_section, is_content_available, audit, role_required."""
    m = define_models(db)
    d = SimpleNamespace(**deps)
    Setting, Override, Due = m.GradebookSetting, m.GradeOverride, m.GradeDue

    def settings_for(section_id):
        s = Setting.query.filter_by(section_id=section_id).first()
        if s is None:
            s = SimpleNamespace(weight_tests=DEFAULT_WEIGHTS['tests'], weight_skills=DEFAULT_WEIGHTS['skills'],
                                weight_quizzes=DEFAULT_WEIGHTS['quizzes'], weight_labs=DEFAULT_WEIGHTS['labs'], policy='best', pass_mark=80, id=None,
                                letter_scale=None, late_per_day=0, late_max=0, late_grace_hours=0, updated_at=None)
        # plain snapshot: safe to cache across requests
        return SimpleNamespace(id=s.id, weight_tests=s.weight_tests, weight_skills=s.weight_skills,
                               weight_quizzes=s.weight_quizzes, weight_labs=getattr(s, 'weight_labs', 0) or 0, policy=s.policy or 'best', pass_mark=s.pass_mark or 80,
                               scale=parse_scale(getattr(s, 'letter_scale', None)),
                               custom_scale=bool(getattr(s, 'letter_scale', None)),
                               late_per_day=getattr(s, 'late_per_day', 0) or 0, late_max=getattr(s, 'late_max', 0) or 0,
                               late_grace_hours=getattr(s, 'late_grace_hours', 0) or 0, updated_at=s.updated_at)

    def signature(section, quiz_ids):
        """Cheap aggregate fingerprint of everything compute() reads; changes invalidate the cache."""
        from sqlalchemy import func
        q = db.session.query
        sig = [
            q(func.count(d.Enrollment.id), func.max(d.Enrollment.id), func.sum(d.Enrollment.progress_percent))
            .filter(d.Enrollment.section_id == section.id).first(),
            q(func.count(d.TestAttempt.id), func.max(d.TestAttempt.id), func.max(d.TestAttempt.completed_at))
            .filter(d.TestAttempt.section_id == section.id).first(),
            q(func.count(d.QuizAttempt.id), func.max(d.QuizAttempt.id)).filter(d.QuizAttempt.quiz_id.in_(quiz_ids or [0])).first(),
            q(func.count(Override.id), func.max(Override.updated_at)).filter(Override.section_id == section.id).first(),
            q(func.count(Due.id), func.max(Due.updated_at)).filter(Due.section_id == section.id).first(),
            q(Setting.updated_at).filter(Setting.section_id == section.id).first(),
            q(func.count(d.KnowledgeTest.id), func.max(d.KnowledgeTest.id)).filter(d.KnowledgeTest.course_id == section.course_id).first(),
            (section.end_date, section.course_id),
            lab_sig(section),
            testout_sig(section),
        ]
        return repr([tuple(x) if x is not None and not isinstance(x, tuple) else x for x in sig])

    def labs_api():
        return app.extensions.get('ciwt_lab_progress')

    def testout_model():
        mx = app.extensions.get('ciwt_mastery')
        return getattr(getattr(mx, 'models', None), 'MasteryCheck', None) if mx else None

    def testout_passes(section_id, uids):
        """pass 14: {(user_id, chapter): completed_at} for passed chapter mastery checks (test-outs) in this class.
        A passed test-out marks that chapter's check quiz 'Exempt (test-out)' when the student has no quiz attempt:
        it is left out of completion and averages like an excused item, and no score is invented."""
        MC = testout_model()
        if MC is None:
            return {}
        out = {}
        for c in MC.query.filter(MC.section_id == section_id, MC.kind == 'testout', MC.passed.is_(True),
                                 MC.user_id.in_(list(uids) or [0])).all():
            t = c.target or ''
            if t.startswith('CH-') and t[3:].isdigit():
                out[(c.user_id, int(t[3:]))] = c.completed_at
        return out

    def section_uids(section):
        return [e.user_id for e in d.Enrollment.query.filter_by(section_id=section.id).all()]

    def lab_sig(section):
        api = labs_api()
        if not api:
            return None
        try:
            return api.lab_signature(section_uids(section))
        except Exception:
            return None

    def testout_sig(section):
        MC = testout_model()
        if MC is None:
            return None
        from sqlalchemy import func
        return tuple(db.session.query(func.count(MC.id), func.max(MC.completed_at))
                     .filter(MC.section_id == section.id, MC.kind == 'testout', MC.passed.is_(True)).first())

    def invalidate(section_id):
        with _gb_lock:
            _gb_cache.pop(section_id, None)

    def staff_section(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if current_user.role == 'admin':
            return section
        if current_user.role != 'instructor' or not d.can_access_section(current_user, section):
            abort(403)
        return section

    def items_for(section):
        tests = d.KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(d.KnowledgeTest.order).all()
        items = []
        for t in sorted(tests, key=lambda t: (1 if (t.title or '').startswith('Skills ') else 0, t.order or 0)):
            cat = 'skills' if (t.title or '').startswith('Skills ') else 'tests'
            items.append({'type': 'test', 'id': t.id, 'title': t.title, 'short': short(t.title), 'category': cat,
                          'passing': t.passing_score or 80, 'obj': t})
        mods = d.Module.query.filter_by(course_id=section.course_id).order_by(d.Module.order).all()
        for mod in mods:
            for q in d.Quiz.query.filter_by(module_id=mod.id).all():
                items.append({'type': 'quiz', 'id': q.id, 'title': q.title, 'short': f'Q{mod.order}',
                              'category': 'quizzes', 'passing': 80, 'module_order': mod.order, 'obj': q})
        api = labs_api()
        if api:
            # one aggregated column: mean best score over the course lab set (unstarted labs count 0)
            items.append({'type': 'lab', 'id': 0, 'title': 'Live labs (mean best score over the course lab set)', 'short': 'Labs',
                          'category': 'labs', 'passing': 80})
        return items

    def short(title):
        t = (title or '').replace('Knowledge Test', 'KT').replace('Skills ', '').replace(' — ', ' ')
        words = t.split()
        return ' '.join(words[-2:]) if len(t) > 14 else t

    def compute(section, user_ids=None, use_cache=True):
        """Grade grid for a class. Full-class results are cached and re-used until the
        signature (attempts, overrides, settings, due dates, enrollments) changes."""
        items = items_for(section)
        quiz_ids = [i['id'] for i in items if i['type'] == 'quiz']
        if user_ids is None and use_cache:
            sig = signature(section, quiz_ids)
            with _gb_lock:
                hit = _gb_cache.get(section.id)
            if hit and hit[0] == sig:
                data = dict(hit[1]); data['cached'] = True
                return data
        data = _compute(section, items, user_ids)
        if user_ids is None and use_cache:
            with _gb_lock:
                _gb_cache[section.id] = (sig, data)
                if len(_gb_cache) > 64:
                    _gb_cache.pop(next(iter(_gb_cache)))
        data = dict(data); data['cached'] = False
        return data

    def _compute(section, items, user_ids=None):
        st = settings_for(section.id)
        weights = {'tests': st.weight_tests or 0, 'skills': st.weight_skills or 0, 'quizzes': st.weight_quizzes or 0,
                   'labs': getattr(st, 'weight_labs', 0) or 0}
        for it in items:
            it.pop('obj', None)          # keep the cached structure free of ORM objects
        enrolls = d.Enrollment.query.filter_by(section_id=section.id).all()
        if user_ids is not None:
            enrolls = [e for e in enrolls if e.user_id in user_ids]
        uids = [e.user_id for e in enrolls] or [0]
        users = {u.id: SimpleNamespace(id=u.id, first_name=u.first_name, last_name=u.last_name, email=u.email,
                                       full_name=u.full_name)
                 for u in d.User.query.filter(d.User.id.in_(uids)).all()}
        test_ids = [i['id'] for i in items if i['type'] == 'test'] or [0]
        quiz_ids = [i['id'] for i in items if i['type'] == 'quiz'] or [0]
        dues = {(x.item_type, x.item_id): x.due_at for x in Due.query.filter_by(section_id=section.id).all()}
        late_on = bool(st.late_per_day)
        t_att = {}
        for a in d.TestAttempt.query.filter(d.TestAttempt.section_id == section.id,
                                            d.TestAttempt.test_id.in_(test_ids),
                                            d.TestAttempt.user_id.in_(uids)).all():
            if a.completed_at is None:
                continue
            t_att.setdefault((a.user_id, a.test_id), []).append(SimpleNamespace(id=a.id, completed_at=a.completed_at, score=a.score))
        # Quiz attempts: those recorded for THIS class, plus legacy attempts with no class recorded
        # that fall inside the student's enrollment window (so a repeat course doesn't import old scores).
        enrolled_at = {e.user_id: e.enrolled_at for e in enrolls}
        has_sec = hasattr(d.QuizAttempt, 'section_id')
        q_att, q_excluded = {}, 0
        for a in d.QuizAttempt.query.filter(d.QuizAttempt.quiz_id.in_(quiz_ids), d.QuizAttempt.user_id.in_(uids)).all():
            sid = getattr(a, 'section_id', None) if has_sec else None
            if sid is not None and sid != section.id:
                q_excluded += 1
                continue
            if sid is None and not in_window(a.completed_at, enrolled_at.get(a.user_id), section.end_date):
                q_excluded += 1
                continue
            q_att.setdefault((a.user_id, a.quiz_id), []).append(SimpleNamespace(id=a.id, completed_at=a.completed_at, score=a.score))
        lab_sc = {}
        if any(i['type'] == 'lab' for i in items) and labs_api():
            try:
                lab_sc = labs_api().lab_scores(section, [e.user_id for e in enrolls])
            except Exception as exc:  # pragma: no cover
                print('gradebook labs note:', exc)
        overrides = {(o.user_id, o.item_type, o.item_id): SimpleNamespace(score=o.score, excused=o.excused, note=o.note,
                                                                         updated_at=o.updated_at)
                     for o in Override.query.filter_by(section_id=section.id).all()}
        exempt = testout_passes(section.id, [e.user_id for e in enrolls]) if any(i['type'] == 'quiz' for i in items) else {}
        rows = []
        late_cells = 0
        for e in enrolls:
            u = users.get(e.user_id)
            if not u:
                continue
            cells, cat_scores = [], {k: [] for k, _ in CATEGORIES}
            done = 0
            for it in items:
                if it['type'] == 'lab':
                    sc, n_done, n_labs = lab_sc.get(u.id, (None, 0, 0))
                    atts = [SimpleNamespace(id=0, completed_at=None, score=sc)] if sc is not None else []
                    it['detail'] = f'{n_labs} labs'
                else:
                    atts = (t_att if it['type'] == 'test' else q_att).get((u.id, it['id']), [])
                atts = sorted(atts, key=lambda a: a.completed_at or datetime.min, reverse=True)
                due = dues.get((it['type'], it['id']))
                adj = []
                for a in atts:
                    days, off = late_penalty(a.completed_at, due, st.late_per_day, st.late_max, st.late_grace_hours) if late_on else (0, 0.0)
                    adj.append((a.completed_at, None if a.score is None else max(0.0, a.score - off), days, off))
                raw = pick([(t, sc) for t, sc, _, _ in adj], st.policy)
                chosen = next((x for x in adj if x[1] == raw), None) if raw is not None else None
                ov = overrides.get((u.id, it['type'], it['id']))
                score, status = raw, ('scored' if raw is not None else 'missing')
                if ov and ov.excused:
                    score, status = None, 'excused'
                elif ov and ov.score is not None:
                    score, status = ov.score, 'override'
                elif raw is None and it['type'] == 'quiz' and (u.id, it.get('module_order')) in exempt:
                    score, status = None, 'exempt'
                late_days, late_off = (chosen[2], chosen[3]) if chosen and status == 'scored' else (0, 0.0)
                if late_off:
                    late_cells += 1
                if score is not None:
                    cat_scores[it['category']].append(score)
                    done += 1
                cells.append({'item': it, 'score': None if score is None else round(score, 1), 'raw': raw,
                              'status': status, 'attempts': len(atts), 'override': ov,
                              'latest_id': atts[0].id if atts and it['type'] == 'test' else None,
                              'latest_at': atts[0].completed_at if atts else None,
                              'due_at': due, 'late_days': late_days, 'late_off': late_off,
                              'passed': score is not None and score >= it['passing']})
            cat_avgs = {k: (round(sum(v) / len(v), 1) if v else None) for k, v in cat_scores.items()}
            grade = weighted_grade(cat_avgs, weights)
            gradable = len([c for c in cells if c['status'] not in ('excused', 'exempt') and (weights.get(c['item']['category'], 0) > 0)])
            done_gradable = len([c for c in cells if c['score'] is not None and weights.get(c['item']['category'], 0) > 0])
            rows.append({'user': u, 'enrollment': SimpleNamespace(id=e.id, enrolled_at=e.enrolled_at, progress_percent=e.progress_percent),
                         'cells': cells, 'cat_avgs': cat_avgs, 'grade': grade,
                         'letter': letter(grade, st.pass_mark, st.scale), 'completion': int(round(100.0 * done_gradable / gradable)) if gradable else 0,
                         'at_risk': grade is not None and grade < st.pass_mark,
                         'progress': int(e.progress_percent or 0)})
        rows.sort(key=lambda r: (r['user'].last_name, r['user'].first_name))
        # per-item stats (column summaries)
        col_stats = []
        for i, it in enumerate(items):
            scores = [r['cells'][i]['score'] for r in rows if r['cells'][i]['score'] is not None]
            ds = describe(scores)
            ds['pass_rate'] = int(round(100.0 * len([s for s in scores if s >= it['passing']]) / len(scores))) if scores else None
            ds['submitted'] = len(scores)
            col_stats.append(ds)
        grades = [r['grade'] for r in rows if r['grade'] is not None]
        summary = describe(grades)
        summary.update({
            'students': len(rows), 'graded': len(grades),
            'pass_rate': int(round(100.0 * len([g for g in grades if g >= st.pass_mark]) / len(grades))) if grades else None,
            'at_risk': len([r for r in rows if r['at_risk']]),
            'completion': int(round(sum(r['completion'] for r in rows) / len(rows))) if rows else 0,
            'histogram': histogram(grades),
            'cat_means': {k: describe([r['cat_avgs'][k] for r in rows])['mean'] for k, _ in CATEGORIES},
            'late_cells': late_cells, 'quiz_attempts_excluded': q_excluded,
            'letters': letter_counts(grades, st.scale),
            # seeded demo accounts (@lms.local) have generated test attempts: say so wherever their grades show
            'demo': any((r['user'].email or '').endswith('@lms.local') and
                        any(c['item']['type'] == 'test' and c['attempts'] for c in r['cells']) for r in rows),
        })
        return {'settings': st, 'weights': weights, 'columns': items, 'rows': rows, 'col_stats': col_stats,
                'summary': summary, 'dues': dues}

    # ---------------------------------------------------------------- instructor
    @login_required
    def instructor_gradebook(section_id):
        section = staff_section(section_id)
        data = compute(section)
        show_quizzes = request.args.get('quizzes') == '1' or data['weights']['quizzes'] > 0
        # server-side filter + pagination (client-side sort/filter still works within a page)
        q = (request.args.get('q') or '').strip().lower()
        risk = request.args.get('risk') == '1'
        per = request.args.get('per', type=int) or 50
        per = per if per in PER_PAGE_CHOICES else 50
        rows = [r for r in data['rows'] if (not q or q in r['user'].full_name.lower() or q in (r['user'].email or '').lower())
                and (not risk or r['at_risk'])]
        pages = max(1, math.ceil(len(rows) / per))
        page = min(max(1, request.args.get('page', type=int) or 1), pages)
        view = dict(data, rows=rows[(page - 1) * per: page * per])
        pager = {'page': page, 'pages': pages, 'per': per, 'total': len(rows), 'q': q, 'risk': risk,
                 'first': (page - 1) * per + 1 if rows else 0, 'last': min(page * per, len(rows)),
                 'choices': PER_PAGE_CHOICES}
        return render_template('gradebook/instructor.html', section=section, gb=view, categories=CATEGORIES,
                               show_quizzes=show_quizzes, pager=pager, full=data)

    @login_required
    def instructor_gradebook_student(section_id, user_id):
        section = staff_section(section_id)
        data = compute(section, user_ids={user_id})
        if not data['rows']:
            abort(404)
        return render_template('gradebook/student_detail.html', section=section, gb=data, row=data['rows'][0],
                               categories=CATEGORIES, staff=True)

    @login_required
    def gradebook_override(section_id):
        section = staff_section(section_id)
        uid = request.form.get('user_id', type=int)
        item_type = request.form.get('item_type')
        item_id = request.form.get('item_id', type=int)
        if item_type not in ('test', 'quiz', 'lab') or not uid or (not item_id and item_type != 'lab'):
            abort(400)
        if not d.Enrollment.query.filter_by(section_id=section.id, user_id=uid).first():
            abort(404)
        action = request.form.get('action', 'save')
        ov = Override.query.filter_by(section_id=section.id, user_id=uid, item_type=item_type, item_id=item_id).first()
        note = (request.form.get('note') or '').strip()[:300]
        if action == 'clear':
            if ov:
                db.session.delete(ov)
                db.session.commit()
            invalidate(section.id)
            d.audit('grade_override_clear', f'section={section.id} user={uid} {item_type}={item_id}')
            flash('Override removed — the recorded attempt score applies again.', 'info')
        else:
            excused = bool(request.form.get('excused'))
            raw = (request.form.get('score') or '').strip()
            score = None
            if not excused:
                try:
                    score = float(raw)
                except ValueError:
                    flash('Enter a score from 0 to 100, or mark the item excused.', 'warning')
                    return redirect(url_for('instructor_gradebook_student', section_id=section.id, user_id=uid))
                if not 0 <= score <= 100:
                    flash('Scores must be between 0 and 100.', 'warning')
                    return redirect(url_for('instructor_gradebook_student', section_id=section.id, user_id=uid))
            if not note:
                flash('Add a short note explaining the override (it is kept in the audit log).', 'warning')
                return redirect(url_for('instructor_gradebook_student', section_id=section.id, user_id=uid))
            if not ov:
                ov = Override(section_id=section.id, user_id=uid, item_type=item_type, item_id=item_id)
                db.session.add(ov)
            ov.score, ov.excused, ov.note = score, excused, note
            ov.updated_at, ov.updated_by = utcnow(), current_user.id
            db.session.commit()
            invalidate(section.id)
            d.audit('grade_override', f'section={section.id} user={uid} {item_type}={item_id} score={score} excused={excused}')
            flash('Grade override saved.', 'success')
        return redirect(url_for('instructor_gradebook_student', section_id=section.id, user_id=uid))

    @login_required
    def gradebook_settings(section_id):
        section = staff_section(section_id)
        s = Setting.query.filter_by(section_id=section.id).first() or Setting(section_id=section.id)

        def w(name, default):
            try:
                return max(0, min(100, int(request.form.get(name, default))))
            except (TypeError, ValueError):
                return default
        s.weight_tests = w('weight_tests', 70)
        s.weight_skills = w('weight_skills', 30)
        s.weight_quizzes = w('weight_quizzes', 0)
        s.weight_labs = w('weight_labs', 0)
        if s.weight_tests + s.weight_skills + s.weight_quizzes + s.weight_labs == 0:
            flash('At least one category needs a weight above zero.', 'warning')
            return redirect(url_for('instructor_gradebook', section_id=section.id))
        s.policy = 'latest' if request.form.get('policy') == 'latest' else 'best'
        s.pass_mark = w('pass_mark', 80) or 80

        def f(name, lo, hi):
            try:
                return max(lo, min(hi, float(request.form.get(name) or 0)))
            except (TypeError, ValueError):
                return 0.0
        s.late_per_day = f('late_per_day', 0, 100)
        s.late_max = f('late_max', 0, 100)
        s.late_grace_hours = int(f('late_grace_hours', 0, 24 * 14))
        s.updated_at, s.updated_by = utcnow(), current_user.id
        db.session.add(s)
        db.session.commit()
        invalidate(section.id)
        d.audit('gradebook_settings', f'section={section.id} w={s.weight_tests}/{s.weight_skills}/{s.weight_quizzes}/{s.weight_labs} policy={s.policy} '
                                      f'late={s.late_per_day}/day max={s.late_max} grace={s.late_grace_hours}h')
        flash('Gradebook settings saved.', 'success')
        return redirect(url_for('instructor_gradebook', section_id=section.id))

    @login_required
    def gradebook_scale(section_id):
        """Letter-scale editor: rows of (minimum %, label), saved high to low."""
        section = staff_section(section_id)
        s = Setting.query.filter_by(section_id=section.id).first() or Setting(section_id=section.id)
        if request.form.get('action') == 'reset':
            s.letter_scale = None
            msg = 'Letter scale reset to the default.'
        else:
            mins, labels = request.form.getlist('scale_min'), request.form.getlist('scale_label')
            rows, errors = [], []
            for lo, lab in zip(mins, labels):
                lo, lab = (lo or '').strip(), (lab or '').strip()
                if not lo and not lab:
                    continue
                try:
                    v = float(lo)
                except ValueError:
                    errors.append(f'"{lo}" is not a number'); continue
                if not 0 <= v <= 100:
                    errors.append(f'{v:g} is outside 0-100'); continue
                if not lab or len(lab) > 4:
                    errors.append(f'label for {v:g}% must be 1-4 characters'); continue
                rows.append((v, lab))
            if len({v for v, _ in rows}) != len(rows):
                errors.append('each minimum can be used once')
            if not rows:
                errors.append('add at least one letter')
            if errors:
                flash('Letter scale not saved: ' + '; '.join(errors[:4]) + '.', 'warning')
                return redirect(url_for('instructor_gradebook', section_id=section.id) + '#gbScale')
            scale = parse_scale([[v, lab] for v, lab in rows])
            s.letter_scale = json.dumps([[lo, lab] for lo, lab in scale])
            msg = 'Letter scale saved: ' + ', '.join(f'{lab} ≥{lo:g}' for lo, lab in scale) + '.'
        s.updated_at, s.updated_by = utcnow(), current_user.id
        db.session.add(s)
        db.session.commit()
        invalidate(section.id)
        d.audit('gradebook_scale', f'section={section.id} scale={s.letter_scale or "default"}')
        flash(msg, 'success')
        return redirect(url_for('instructor_gradebook', section_id=section.id) + '#gbScale')

    @login_required
    def gradebook_due(section_id):
        """Set/clear due dates (datetime-local, class time) for graded items."""
        section = staff_section(section_id)
        valid = {(i['type'], i['id']) for i in items_for(section)}
        existing = {(x.item_type, x.item_id): x for x in Due.query.filter_by(section_id=section.id).all()}
        changed = 0
        for key, val in request.form.items():
            if not key.startswith('due_'):
                continue
            try:
                _, typ, iid = key.split('_', 2)
                iid = int(iid)
            except ValueError:
                continue
            if (typ, iid) not in valid:
                continue
            val = (val or '').strip()
            row = existing.get((typ, iid))
            if not val:
                if row:
                    db.session.delete(row); changed += 1
                continue
            try:
                when = datetime.strptime(val[:16], '%Y-%m-%dT%H:%M')
            except ValueError:
                flash(f'Could not read the date "{val}".', 'warning'); continue
            if not row:
                row = Due(section_id=section.id, item_type=typ, item_id=iid, due_at=when)
                db.session.add(row)
            elif row.due_at == when:
                continue
            row.due_at, row.updated_at, row.updated_by = when, utcnow(), current_user.id
            changed += 1
        db.session.commit()
        invalidate(section.id)
        d.audit('gradebook_due', f'section={section.id} changed={changed}')
        flash(f'Due dates saved ({changed} changed).', 'success')
        return redirect(url_for('instructor_gradebook', section_id=section.id) + '#gbDue')

    @login_required
    def gradebook_csv(section_id):
        section = staff_section(section_id)
        data = compute(section)
        buf = StringIO()
        wtr = csv.writer(buf)
        head = ['last_name', 'first_name', 'email', 'course_grade', 'letter', 'completion_pct', 'lesson_progress_pct']
        head += [f'{c[1]} avg' for c in CATEGORIES]
        head += [f"{it['title']} ({it['type']} {it['id']})" for it in data['columns']]
        wtr.writerow(head)
        for r in data['rows']:
            u = r['user']
            line = [u.last_name, u.first_name, u.email, r['grade'] if r['grade'] is not None else '', r['letter'],
                    r['completion'], r['progress']]
            line += [r['cat_avgs'][k] if r['cat_avgs'][k] is not None else '' for k, _ in CATEGORIES]
            for c in r['cells']:
                line.append('EX' if c['status'] == 'excused' else 'Exempt (test-out)' if c['status'] == 'exempt' else ('' if c['score'] is None else
                            (f"{c['score']} (late -{c['late_off']:g})" if c['late_off'] else c['score'])))
            wtr.writerow(line)
        wtr.writerow([])
        wtr.writerow(['Class mean', '', '', data['summary']['mean'] or '', '', data['summary']['completion'], ''] +
                     ['' for _ in CATEGORIES] + [cs['mean'] if cs['mean'] is not None else '' for cs in data['col_stats']])
        d.audit('gradebook_export', f'section={section.id}')
        fname = f"gradebook-section-{section.id}-{utcnow().strftime('%Y%m%d')}.csv"
        return Response(buf.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={fname}'})

    # ---------------------------------------------------------------- student
    @login_required
    def student_grades():
        enrolls = d.Enrollment.query.filter_by(user_id=current_user.id).all()
        cards = []
        for e in enrolls:
            section = db.session.get(d.ClassSection, e.section_id)
            if not section:
                continue
            data = compute(section, user_ids={current_user.id})
            if data['rows']:
                cards.append({'section': section, 'row': data['rows'][0], 'gb': data})
        return render_template('gradebook/student_overview.html', cards=cards, categories=CATEGORIES)

    @login_required
    def student_section_grades(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if not d.Enrollment.query.filter_by(section_id=section.id, user_id=current_user.id).first():
            if current_user.role in ('admin', 'instructor'):
                return redirect(url_for('instructor_gradebook', section_id=section.id))
            flash('You are not enrolled in this class.', 'warning')
            return redirect(url_for('student_grades'))
        data = compute(section, user_ids={current_user.id})
        row = data['rows'][0]
        for c in row['cells']:
            it = c['item']
            c['available'] = (it['type'] == 'quiz') or d.is_content_available(section.id, 'test', it['id'], current_user.id)
        # class context without exposing classmates: only item means
        return render_template('gradebook/student_detail.html', section=section, gb=data, row=row,
                               categories=CATEGORIES, staff=False)

    for rule, ep, fn, methods in [
        ('/instructor/section/<int:section_id>/gradebook', 'instructor_gradebook', instructor_gradebook, ['GET']),
        ('/instructor/section/<int:section_id>/gradebook/student/<int:user_id>', 'instructor_gradebook_student', instructor_gradebook_student, ['GET']),
        ('/instructor/section/<int:section_id>/gradebook/override', 'gradebook_override', gradebook_override, ['POST']),
        ('/instructor/section/<int:section_id>/gradebook/settings', 'gradebook_settings', gradebook_settings, ['POST']),
        ('/instructor/section/<int:section_id>/gradebook/scale', 'gradebook_scale', gradebook_scale, ['POST']),
        ('/instructor/section/<int:section_id>/gradebook/due', 'gradebook_due', gradebook_due, ['POST']),
        ('/instructor/section/<int:section_id>/gradebook.csv', 'gradebook_csv', gradebook_csv, ['GET']),
        ('/student/grades', 'student_grades', student_grades, ['GET']),
        ('/student/section/<int:section_id>/grades', 'student_section_grades', student_section_grades, ['GET']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)
    app.extensions['ciwt_gradebook'] = SimpleNamespace(compute=compute, models=m, invalidate=invalidate)
    return m
