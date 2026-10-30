"""Admin > Exports: cmi5 packages, LRS credentials, registrations, and statements."""
import secrets

from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from . import package, runtime
from .util import VERB_NAME


_bag = {}


def exports_context():
    """POST handler and template data for Admin → Exports. A redirect is returned as-is."""
    M = _bag['M']
    db_session = _bag['db']
    new_credential = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'credential':
            name = (request.form.get('name') or 'LRS client').strip()[:120] or 'LRS client'
            key = 'lrs_' + secrets.token_hex(6)
            secret = secrets.token_urlsafe(24)
            row = M('LrsClient')(name=name, key=key, secret_hash=generate_password_hash(secret), active=True)
            db_session().add(row)
            db_session().commit()
            new_credential = {'key': key, 'secret': secret, 'name': name}
            flash('Learning record store credential created. Copy the secret now; it is not shown again.', 'success')
        elif action == 'revoke':
            row = M('LrsClient').query.filter_by(id=request.form.get('client_id', type=int)).first()
            if row:
                row.active = False
                db_session().commit()
                flash(f'Revoked {row.name}.', 'info')
        elif action == 'import':
            upload = request.files.get('package')
            if not upload or not upload.filename:
                flash('Choose a cmi5.xml file or a zip package.', 'warning')
            else:
                try:
                    course = package.import_package(upload.filename, upload.read())
                    flash(f'Imported “{course.title}”.', 'success')
                except ValueError as exc:
                    flash(str(exc), 'danger')
        elif action == 'register':
            course = M('Cmi5Course').query.filter_by(id=request.form.get('course_id', type=int)).first()
            if course is None:
                flash('Choose a course.', 'warning')
            else:
                reg = runtime.create_registration(course, request.form.get('learner') or 'Learner')
                return redirect(url_for('cmi5.admin_cmi5_registration', registration_id=reg.id))
        elif action == 'live':
            code = (request.form.get('course_code') or '').upper()
            try:
                course = package.ensure_live_course(code, request.host_url)
                reg = runtime.create_registration(course, request.form.get('learner') or 'Learner')
                return redirect(url_for('cmi5.admin_cmi5_registration', registration_id=reg.id))
            except ValueError as exc:
                flash(str(exc), 'danger')
    imported = M('Cmi5Course').query.order_by(M('Cmi5Course').id.desc()).all()
    clients = M('LrsClient').query.order_by(M('LrsClient').id.desc()).all()
    registrations = M('Cmi5Registration').query.order_by(M('Cmi5Registration').id.desc()).limit(30).all()
    statements = M('XapiStatement').query.order_by(M('XapiStatement').stored.desc()).limit(25).all()
    return {
        'imported': imported,
        'clients': clients,
        'registrations': registrations,
        'course_titles': {c.id: c.title for c in imported},
        'statements': _statement_rows(statements),
        'new_credential': new_credential,
        'endpoint': request.host_url.rstrip('/') + '/xAPI/',
    }


def mount_admin(bp, models, deps):
    def M(name):
        return models[name]

    def db_session():
        return M('LrsClient').query.session

    _bag['M'] = M
    _bag['db'] = db_session

    @bp.route('/admin/exports/cmi5/<course_code>.zip')
    @login_required
    def admin_cmi5_download(course_code):
        if current_user.role != 'admin':
            abort(403)
        try:
            payload, filename = package.build_zip(course_code)
        except ValueError:
            abort(404)
        resp = Response(payload, mimetype='application/zip')
        resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

    @bp.route('/admin/exports/registration/<int:registration_id>', methods=['GET', 'POST'])
    @login_required
    def admin_cmi5_registration(registration_id):
        if current_user.role != 'admin':
            abort(403)
        registration = M('Cmi5Registration').query.filter_by(id=registration_id).first_or_404()
        course = M('Cmi5Course').query.filter_by(id=registration.course_id).first()
        if request.method == 'POST':
            au = M('Cmi5AU').query.filter_by(
                id=request.form.get('au_id', type=int), course_id=course.id,
            ).first_or_404()
            action = request.form.get('action')
            if action == 'waive':
                try:
                    runtime.waive_au(registration, au, 'Administrative')
                    flash(f'Waived “{au.title}”.', 'success')
                except ValueError as exc:
                    flash(str(exc), 'warning')
                return redirect(url_for('cmi5.admin_cmi5_registration', registration_id=registration.id))
            mode = request.form.get('launch_mode') or 'Normal'
            _session_row, target = runtime.launch_session(registration, au, request.host_url, mode)
            return redirect(target)
        rows = runtime.registration_rows(registration)
        statements = M('XapiStatement').query.filter_by(registration=registration.uuid).order_by(
            M('XapiStatement').stored.desc()).limit(40).all()
        return render_template(
            'admin_cmi5_registration.html', admin_tab='admin_exports',
            registration=registration, course=course, rows=rows, statements=_statement_rows(statements),
        )

    def _aus(course):
        return M('Cmi5AU').query.filter_by(course_id=course.id).order_by(M('Cmi5AU').sort_order, M('Cmi5AU').id).all()

    @bp.route('/admin/exports/api/import', methods=['POST'])
    @login_required
    def admin_cmi5_api_import():
        if current_user.role != 'admin':
            abort(403)
        upload = request.files.get('package')
        if upload is None:
            return {'error': 'Choose a package.'}, 400
        try:
            course = package.import_package(upload.filename or 'course.zip', upload.read())
        except ValueError as exc:
            return {'error': str(exc)}, 400
        return {'id': course.id, 'title': course.title, 'aus': len(_aus(course))}

    @bp.route('/admin/exports/api/launch', methods=['POST'])
    @login_required
    def admin_cmi5_api_launch():
        if current_user.role != 'admin':
            abort(403)
        data = request.get_json(force=True, silent=True) or {}
        course = M('Cmi5Course').query.filter_by(id=data.get('course_id')).first()
        if course is None:
            return {'error': 'Unknown course.'}, 404
        aus = _aus(course)
        index = int(data.get('au_index') or 0)
        if index < 0 or index >= len(aus):
            return {'error': 'No assignable unit at that index.'}, 404
        try:
            registration = runtime.create_registration(
                course, data.get('learner') or 'Learner',
                actor=data.get('actor'), registration_uuid=data.get('registration'),
            )
        except ValueError as exc:
            return {'error': str(exc)}, 400
        session_row, target = runtime.launch_session(
            registration, aus[index], request.host_url, data.get('launch_mode') or 'Normal',
        )
        return {'url': target, 'session_id': session_row.uuid, 'registration': registration.uuid}

    @bp.route('/admin/exports/api/waive', methods=['POST'])
    @login_required
    def admin_cmi5_api_waive():
        if current_user.role != 'admin':
            abort(403)
        data = request.get_json(force=True, silent=True) or {}
        registration = M('Cmi5Registration').query.filter_by(uuid=data.get('registration')).first()
        if registration is None:
            return {'error': 'Unknown registration.'}, 404
        aus = _aus(M('Cmi5Course').query.filter_by(id=registration.course_id).first())
        index = int(data.get('au_index') or 0)
        try:
            runtime.waive_au(registration, aus[index], data.get('reason') or 'Administrative')
        except (ValueError, IndexError) as exc:
            return {'error': str(exc)}, 400
        return {'ok': True}

    @bp.route('/admin/exports/api/abandon', methods=['POST'])
    @login_required
    def admin_cmi5_api_abandon():
        if current_user.role != 'admin':
            abort(403)
        data = request.get_json(force=True, silent=True) or {}
        return {'ok': runtime.abandon_session(data.get('session_id') or '')}

    @bp.route('/admin/exports/api/course/<int:course_id>', methods=['DELETE'])
    @login_required
    def admin_cmi5_api_delete(course_id):
        if current_user.role != 'admin':
            abort(403)
        course = M('Cmi5Course').query.filter_by(id=course_id).first()
        if course is None:
            return {'ok': True}
        package._delete_course(course)
        db_session().commit()
        return {'ok': True}


def _statement_rows(rows):
    import json
    out = []
    for row in rows:
        try:
            body = json.loads(row.body)
        except Exception:
            body = {}
        actor = ((body.get('actor') or {}).get('account') or {}).get('name') or ''
        out.append({
            'id': row.id,
            'stored': row.stored,
            'verb': VERB_NAME.get(row.verb_id) or (row.verb_id or '').rsplit('/', 1)[-1],
            'activity': row.object_id or '',
            'actor': actor,
            'registration': row.registration or '',
            'voided': row.voided,
            'voiding': row.is_voiding,
        })
    return out
