"""cmi5 course packages and the in-app xAPI learning record store.

Mounted on the existing Flask app. Statements, state, and profiles are stored
in the same database as the rest of Novak LMS. No extra service is required.
"""
from flask import Blueprint, Response, abort, jsonify, request

from .admin import mount_admin
from .lrs import mount as mount_lrs
from .models import define_models

bp = Blueprint('cmi5', __name__)


def register(app, db, deps, csrf):
    models = define_models(db)
    from . import lrs, package, runtime
    lrs.init(app, db, models)
    package.init(db, models, deps)
    runtime.init(app, db, models)
    mount_lrs(bp, csrf)
    mount_admin(bp, models, deps)
    _mount_public(bp, csrf, models)
    app.register_blueprint(bp)
    return models


def _mount_public(bp, csrf, models):
    from .runtime import fetch_auth

    @bp.route('/cmi5/fetch/<secret>', methods=['GET', 'POST'])
    @csrf.exempt
    def cmi5_fetch(secret):
        if request.method != 'POST':
            return jsonify({
                'error-code': '3',
                'error-text': 'The fetch URL only accepts POST.',
            }), 405
        return jsonify(fetch_auth(secret)), 200

    @bp.route('/cmi5/content/<int:course_id>/<path:relpath>')
    def cmi5_content(course_id, relpath):
        if relpath.startswith('/') or '..' in relpath.split('/'):
            abort(404)
        row = models['Cmi5File'].query.filter_by(course_id=course_id, path=relpath).first()
        if row is None:
            abort(404)
        resp = Response(bytes(row.content))
        resp.headers['Content-Type'] = row.content_type or 'application/octet-stream'
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        return resp

    @bp.route('/cmi5/return/<session_id>')
    def cmi5_return(session_id):
        from flask import render_template
        row = models['Cmi5Session'].query.filter_by(uuid=session_id).first()
        if row is None:
            abort(404)
        au = models['Cmi5AU'].query.filter_by(id=row.au_id).first()
        return render_template('cmi5_return.html', au=au, closed=bool(row.terminated_at or row.abandoned_at))
