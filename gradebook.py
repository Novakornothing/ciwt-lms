"""CIWT gradebook: per-section grade grid for instructors, grades/progress for students.

Built on the existing models (KnowledgeTest/TestAttempt, Quiz/QuizAttempt,
LabCompletion, Enrollment). Adds two small tables: per-section settings
(category weights + best/latest policy) and per-cell instructor overrides
(score override or excused, with a required note and audit trail).

Helix attention data is deliberately NOT an input to any grade.
"""
import csv
import statistics
from datetime import datetime
from io import StringIO
from types import SimpleNamespace

from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

CATEGORIES = [
    ('tests', 'Knowledge tests'),
    ('skills', 'Skills exams'),
    ('quizzes', 'Progress quizzes'),
]
DEFAULT_WEIGHTS = {'tests': 70, 'skills': 30, 'quizzes': 0}
_cache = {}


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
        policy = db.Column(db.String(10), default='best')  # best | latest
        pass_mark = db.Column(db.Integer, default=80)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow)
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
        updated_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    _cache['m'] = SimpleNamespace(GradebookSetting=GradebookSetting, GradeOverride=GradeOverride)
    return _cache['m']


# ---------------------------------------------------------------- pure computation
def letter(score, pass_mark=80):
    if score is None:
        return '—'
    for cut, lab in ((93, 'A'), (90, 'A-'), (87, 'B+'), (83, 'B'), (80, 'B-'), (77, 'C+'), (73, 'C'), (70, 'C-'), (60, 'D')):
        if score >= cut:
            return lab
    return 'F'


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
    Setting, Override = m.GradebookSetting, m.GradeOverride

    def settings_for(section_id):
        s = Setting.query.filter_by(section_id=section_id).first()
        if s is None:
            s = SimpleNamespace(weight_tests=DEFAULT_WEIGHTS['tests'], weight_skills=DEFAULT_WEIGHTS['skills'],
                                weight_quizzes=DEFAULT_WEIGHTS['quizzes'], policy='best', pass_mark=80, id=None)
        return s

    def staff_section(section_id):
        section = d.ClassSection.query.get_or_404(section_id)
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
        return items

    def short(title):
        t = (title or '').replace('Knowledge Test', 'KT').replace('Skills ', '').replace(' — ', ' ')
        words = t.split()
        return ' '.join(words[-2:]) if len(t) > 14 else t

    def compute(section, user_ids=None):
        st = settings_for(section.id)
        weights = {'tests': st.weight_tests or 0, 'skills': st.weight_skills or 0, 'quizzes': st.weight_quizzes or 0}
        items = items_for(section)
        enrolls = d.Enrollment.query.filter_by(section_id=section.id).all()
        if user_ids is not None:
            enrolls = [e for e in enrolls if e.user_id in user_ids]
        uids = [e.user_id for e in enrolls] or [0]
        users = {u.id: u for u in d.User.query.filter(d.User.id.in_(uids)).all()}
        test_ids = [i['id'] for i in items if i['type'] == 'test'] or [0]
        quiz_ids = [i['id'] for i in items if i['type'] == 'quiz'] or [0]
        t_att = {}
        for a in d.TestAttempt.query.filter(d.TestAttempt.section_id == section.id,
                                            d.TestAttempt.test_id.in_(test_ids),
                                            d.TestAttempt.user_id.in_(uids)).all():
            if a.completed_at is None:
                continue
            t_att.setdefault((a.user_id, a.test_id), []).append(a)
        q_att = {}
        for a in d.QuizAttempt.query.filter(d.QuizAttempt.quiz_id.in_(quiz_ids), d.QuizAttempt.user_id.in_(uids)).all():
            q_att.setdefault((a.user_id, a.quiz_id), []).append(a)
        overrides = {(o.user_id, o.item_type, o.item_id): o for o in Override.query.filter_by(section_id=section.id).all()}
        rows = []
        for e in enrolls:
            u = users.get(e.user_id)
            if not u:
                continue
            cells, cat_scores = [], {k: [] for k, _ in CATEGORIES}
            done = 0
            for it in items:
                atts = (t_att if it['type'] == 'test' else q_att).get((u.id, it['id']), [])
                atts = sorted(atts, key=lambda a: a.completed_at or datetime.min, reverse=True)
                raw = pick([(a.completed_at, a.score) for a in atts], st.policy)
                ov = overrides.get((u.id, it['type'], it['id']))
                score, status = raw, ('scored' if raw is not None else 'missing')
                if ov and ov.excused:
                    score, status = None, 'excused'
                elif ov and ov.score is not None:
                    score, status = ov.score, 'override'
                if score is not None:
                    cat_scores[it['category']].append(score)
                    done += 1
                cells.append({'item': it, 'score': None if score is None else round(score, 1), 'raw': raw,
                              'status': status, 'attempts': len(atts), 'override': ov,
                              'latest_id': atts[0].id if atts and it['type'] == 'test' else None,
                              'latest_at': atts[0].completed_at if atts else None,
                              'passed': score is not None and score >= it['passing']})
            cat_avgs = {k: (round(sum(v) / len(v), 1) if v else None) for k, v in cat_scores.items()}
            grade = weighted_grade(cat_avgs, weights)
            gradable = len([c for c in cells if c['status'] != 'excused' and (weights.get(c['item']['category'], 0) > 0)])
            done_gradable = len([c for c in cells if c['score'] is not None and weights.get(c['item']['category'], 0) > 0])
            rows.append({'user': u, 'enrollment': e, 'cells': cells, 'cat_avgs': cat_avgs, 'grade': grade,
                         'letter': letter(grade, st.pass_mark), 'completion': int(round(100.0 * done_gradable / gradable)) if gradable else 0,
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
        })
        return {'settings': st, 'weights': weights, 'columns': items, 'rows': rows, 'col_stats': col_stats, 'summary': summary}

    # ---------------------------------------------------------------- instructor
    @login_required
    def instructor_gradebook(section_id):
        section = staff_section(section_id)
        data = compute(section)
        show_quizzes = request.args.get('quizzes') == '1' or data['weights']['quizzes'] > 0
        return render_template('gradebook/instructor.html', section=section, gb=data, categories=CATEGORIES,
                               show_quizzes=show_quizzes)

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
        if item_type not in ('test', 'quiz') or not uid or not item_id:
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
            ov.updated_at, ov.updated_by = datetime.utcnow(), current_user.id
            db.session.commit()
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
        if s.weight_tests + s.weight_skills + s.weight_quizzes == 0:
            flash('At least one category needs a weight above zero.', 'warning')
            return redirect(url_for('instructor_gradebook', section_id=section.id))
        s.policy = 'latest' if request.form.get('policy') == 'latest' else 'best'
        s.pass_mark = w('pass_mark', 80) or 80
        s.updated_at, s.updated_by = datetime.utcnow(), current_user.id
        db.session.add(s)
        db.session.commit()
        d.audit('gradebook_settings', f'section={section.id} w={s.weight_tests}/{s.weight_skills}/{s.weight_quizzes} policy={s.policy}')
        flash('Gradebook settings saved.', 'success')
        return redirect(url_for('instructor_gradebook', section_id=section.id))

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
                line.append('EX' if c['status'] == 'excused' else ('' if c['score'] is None else c['score']))
            wtr.writerow(line)
        wtr.writerow([])
        wtr.writerow(['Class mean', '', '', data['summary']['mean'] or '', '', data['summary']['completion'], ''] +
                     ['' for _ in CATEGORIES] + [cs['mean'] if cs['mean'] is not None else '' for cs in data['col_stats']])
        d.audit('gradebook_export', f'section={section.id}')
        fname = f"gradebook-section-{section.id}-{datetime.utcnow().strftime('%Y%m%d')}.csv"
        return Response(buf.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={fname}'})

    # ---------------------------------------------------------------- student
    @login_required
    def student_grades():
        enrolls = d.Enrollment.query.filter_by(user_id=current_user.id).all()
        cards = []
        for e in enrolls:
            section = d.ClassSection.query.get(e.section_id)
            if not section:
                continue
            data = compute(section, user_ids={current_user.id})
            if data['rows']:
                cards.append({'section': section, 'row': data['rows'][0], 'gb': data})
        return render_template('gradebook/student_overview.html', cards=cards, categories=CATEGORIES)

    @login_required
    def student_section_grades(section_id):
        section = d.ClassSection.query.get_or_404(section_id)
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
        ('/instructor/section/<int:section_id>/gradebook.csv', 'gradebook_csv', gradebook_csv, ['GET']),
        ('/student/grades', 'student_grades', student_grades, ['GET']),
        ('/student/section/<int:section_id>/grades', 'student_section_grades', student_section_grades, ['GET']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)
    app.extensions['ciwt_gradebook'] = SimpleNamespace(compute=compute, models=m)
    return m
