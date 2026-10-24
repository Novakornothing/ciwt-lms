"""Student skills portfolio (Priority 3, part 1). Pending SME review.

/portfolio shows a student's verified competencies (objectives the adaptive engine rates mastered), completed real-VM and
simulated labs with process-quality badges from the lab process analysis (e.g. “Diagnosed before changing”), and
certification domain readiness (A+ Core 1/2, Network+) derived from the curated objective-to-exam mapping. Students choose
private or shareable; a shareable portfolio has an unguessable link /portfolio/u/<token> (read-only, noindex). Exports:
printable page and OpenBadges 2.0-shaped JSON. Instructors can open the portfolio of a student in their class.
"""
import json
import secrets
from datetime import datetime, timezone

from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from curriculum_v2.objectives import OBJECTIVES
from . import build as B

_models = {}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def define_models(db):
    if 'm' in _models:
        return _models['m']

    class PortfolioSetting(db.Model):
        __tablename__ = 'portfolio_setting'
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
        visibility = db.Column(db.String(10), default='private', nullable=False)   # private|link
        token = db.Column(db.String(64), unique=True, index=True)
        updated_at = db.Column(db.DateTime, default=utcnow)

    _models['m'] = PortfolioSetting
    return PortfolioSetting


def register(app, db, d):
    PS = define_models(db)

    def setting(uid, create=False):
        s = db.session.get(PS, uid)
        if s is None and create:
            s = PS(user_id=uid, visibility='private')
            db.session.add(s)
        return s

    def exam_sittings(user):
        """Per exam: the best VOUCHER READY sitting, else the latest submitted one (Option B pass 5)."""
        ESA = d.get('ExamSimAttempt')
        if ESA is None:
            return []
        from curriculum_v2.cert import exam_sim as ES
        from curriculum_v2.cert.exams import EXAMS
        rows = ESA.query.filter(ESA.user_id == user.id, ESA.submitted_at.isnot(None)).order_by(ESA.submitted_at.desc()).all()
        out = []
        for ex in EXAMS:
            mine = [r for r in rows if r.exam == ex and r.mode != 'drill']
            if not mine:
                continue
            ready = [r for r in mine if r.badge == 'ready']
            r = max(ready, key=lambda x: (x.score or 0, x.submitted_at)) if ready else mine[0]
            out.append({'exam': ex, 'code': EXAMS[ex]['code'], 'name': EXAMS[ex]['name'], 'score': r.score,
                        'bar': ES.PASS_SCORE[ex], 'ready': r.badge == 'ready',
                        'status': ES.VOUCHER_STATUS.get(r.badge, 'REMEDIATION REQUIRED'),
                        'date': str(r.submitted_at)[:10], 'mode': ('Exam mode' if r.strict else 'Practice mode') + ' · '
                        + ES.MODES.get(r.mode, {}).get('name', r.mode)})
        return out

    def collect(user):
        from mastery import lab_diagnosis as LDX
        courses, states_all, comps = [], {}, []
        eng = d['mastery']().engine
        for e in d['Enrollment'].query.filter_by(user_id=user.id).all():
            section = db.session.get(d['ClassSection'], e.section_id)
            course = db.session.get(d['Course'], section.course_id) if section else None
            if not course:
                continue
            try:
                st = eng.student_state(section, user, log=False)
                states = st['states']
            except Exception:
                db.session.rollback()
                states = {}
            mastered = [o for o, s in states.items() if s.get('status') == 'mastered']
            for o in mastered:
                comps.append({'id': o, 'course': course.code, 'text': OBJECTIVES.get(o, {}).get('text', o),
                              'pct': states[o]['pct'], 'when': (states[o].get('last_when') or '') and str(states[o]['last_when'])[:10]})
            states_all.update(states)
            courses.append({'code': course.code, 'title': course.title, 'section': section.name,
                            'mastered': len(mastered), 'objectives': len(states)})
        labs = []
        LP = d['lab_api'].LabProgress
        for row in LP.query.filter_by(user_id=user.id).filter(LP.completed_at.isnot(None)).order_by(LP.completed_at).all():
            lab = d['get_lab'](row.lab_id) or {}
            try:
                ana = LDX.analyze(d['lab_api'].events_for(user.id, row.lab_id), lab=lab)
            except Exception:
                ana = None
            kind = lab.get('kind', '')
            labs.append({'id': row.lab_id, 'title': lab.get('title', row.lab_id), 'score': round(row.best_score or row.score or 0),
                         'kind': 'Real Linux VM' if row.lab_id.startswith('linux-vm') else 'Simulation' + (f' ({kind})' if kind else ''),
                         'completed': str(row.completed_at)[:10], 'badges': B.lab_badges(ana)})
        return {'student': {'name': f'{user.first_name} {user.last_name}'.strip() if hasattr(user, 'first_name') else user.email},
                'generated': utcnow().strftime('%Y-%m-%d'), 'courses': courses, 'competencies': comps, 'labs': labs,
                'exam_sittings': exam_sittings(user),
                'certifications': B.cert_readiness(states_all)}

    def render(user, owner, public=False):
        pf = collect(user)
        s = setting(user.id)
        share = url_for('portfolio_public', token=s.token, _external=True) if s and s.visibility == 'link' and s.token else None
        return render_template('portfolio/portfolio.html', pf=pf, owner=owner, public=public, setting=s, share=share, user=user)

    @app.route('/portfolio')
    @login_required
    def portfolio_home():
        if current_user.role != 'student':
            abort(403)
        return render(current_user, owner=True)

    @app.route('/portfolio/visibility', methods=['POST'])
    @login_required
    def portfolio_visibility():
        if current_user.role != 'student':
            abort(403)
        s = setting(current_user.id, create=True)
        v = request.form.get('visibility')
        s.visibility = 'link' if v == 'link' else 'private'
        if s.visibility == 'link' and (not s.token or request.form.get('new_link')):
            s.token = secrets.token_urlsafe(24)
        s.updated_at = utcnow()
        db.session.commit()
        flash('Portfolio is now ' + ('shareable by link.' if s.visibility == 'link' else 'private.'), 'success')
        return redirect(url_for('portfolio_home'), code=303)

    @app.route('/portfolio/export.json')
    @login_required
    def portfolio_export():
        if current_user.role != 'student':
            abort(403)
        pf = collect(current_user)
        s = setting(current_user.id)
        verify = url_for('portfolio_public', token=s.token, _external=True) if s and s.visibility == 'link' else url_for('portfolio_home', _external=True)
        body = json.dumps(B.openbadges(pf, url_for('landing', _external=True) if 'landing' in app.view_functions else request.host_url, verify), indent=2)
        return Response(body, mimetype='application/json', headers={'Content-Disposition': 'attachment; filename=portfolio.json'})

    @app.route('/portfolio/u/<token>')
    def portfolio_public(token):
        s = PS.query.filter_by(token=token).first()
        if not s or s.visibility != 'link' or len(token) < 20:
            abort(404)
        user = db.session.get(d['User'], s.user_id)
        resp = app.make_response(render(user, owner=False, public=True))
        resp.headers['X-Robots-Tag'] = 'noindex, nofollow'
        return resp

    @app.route('/instructor/section/<int:section_id>/portfolio/<int:user_id>')
    @login_required
    def portfolio_instructor(section_id, user_id):
        section = db.get_or_404(d['ClassSection'], section_id)
        if current_user.role not in ('instructor', 'admin') or not d['can_access_section'](current_user, section):
            abort(403)
        if not d['Enrollment'].query.filter_by(user_id=user_id, section_id=section_id).first():
            abort(404)
        return render(db.get_or_404(d['User'], user_id), owner=False)

    api = type('PortfolioAPI', (), {})()
    api.PortfolioSetting, api.collect = PS, collect
    app.extensions['ciwt_portfolio'] = api
    return api
