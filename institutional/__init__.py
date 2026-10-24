"""Institutions (tenants): campus SSO (OIDC + SAML 2.0 SP), data isolation, per-college branding, outcomes reports.

Every pre-existing user and class belongs to the default tenant (slug ``default``); a NULL institution_id also means
the default tenant, so rows created by older code paths stay visible exactly as before. Admins of the default tenant
are platform admins; admins of any other tenant are institution admins confined to their own institution.
"""
import csv
import io
import json
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from flask import Response, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user
from sqlalchemy import event as sa_event
from werkzeug.security import generate_password_hash

from . import oidc as O
from . import outcomes as OUT
from . import saml as S

DEFAULT_SLUG = 'default'
HEX = re.compile(r'^#[0-9a-fA-F]{6}$')
SLUG = re.compile(r'^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$')
DEFAULT_ROLE_MAP = {'admin': [], 'instructor': ['faculty', 'instructor', 'instructors', 'teacher']}
ROLE_ATTRS = ('groups', 'roles', 'eduPersonAffiliation', 'urn:oid:1.3.6.1.4.1.5923.1.1.1.1')
TENANT_ADMIN_ENDPOINTS = ('admin_institutions', 'admin_institution_edit', 'admin_outcomes')


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4   # noqa: E731
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def on_color(hexc):
    """Black or white text, whichever contrasts more with the brand colour (WCAG relative luminance)."""
    L = _lum(hexc)
    return '#000000' if (L + 0.05) / 0.05 >= 1.05 / (L + 0.05) else '#ffffff'


def map_role(attrs, cfg):
    """IdP groups/affiliations -> LMS role. Admin is granted only by an explicit role_map entry."""
    rm = cfg.get('role_map') or DEFAULT_ROLE_MAP
    key = cfg.get('role_attribute')
    vals = set()
    for k, v in (attrs or {}).items():
        if (k == key) if key else (k in ROLE_ATTRS):
            vals |= {str(x).strip().lower() for x in (v if isinstance(v, list) else [v])}
    for role in ('admin', 'instructor'):
        if vals & {x.lower() for x in rm.get(role, [])}:
            return role
    return 'student'


def register(app, db, d):
    User, ClassSection = d['User'], d['ClassSection']

    class Institution(db.Model):
        __tablename__ = 'institution'
        id = db.Column(db.Integer, primary_key=True)
        slug = db.Column(db.String(40), unique=True, nullable=False)
        name = db.Column(db.String(160), nullable=False)
        logo_url = db.Column(db.String(400))
        primary_color = db.Column(db.String(7), default='#1f3a5f')
        accent_color = db.Column(db.String(7), default='#c8a24a')
        domain = db.Column(db.String(200))
        sso_config_json = db.Column(db.Text, default='{}')
        active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=utcnow)

        @property
        def sso(self):
            try:
                v = json.loads(self.sso_config_json or '{}')
                return v if isinstance(v, dict) else {}
            except ValueError:
                return {}

    class SsoIdentity(db.Model):
        __tablename__ = 'sso_identity'
        __table_args__ = (db.UniqueConstraint('institution_id', 'protocol', 'subject', name='uq_sso_identity'),)
        id = db.Column(db.Integer, primary_key=True)
        institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        protocol = db.Column(db.String(8), nullable=False)
        subject = db.Column(db.String(255), nullable=False)
        last_login = db.Column(db.DateTime, default=utcnow)

    class SsoPending(db.Model):
        """SAML AuthnRequests in flight, keyed by RelayState (the ACS POST is cross-site, so no session cookie)."""
        __tablename__ = 'sso_pending'
        token = db.Column(db.String(64), primary_key=True)
        institution_id = db.Column(db.Integer, nullable=False)
        request_id = db.Column(db.String(64), nullable=False)
        created_at = db.Column(db.DateTime, default=utcnow)

    class SsoReplay(db.Model):
        __tablename__ = 'sso_replay'
        assertion_id = db.Column(db.String(128), primary_key=True)
        seen_at = db.Column(db.DateTime, default=utcnow)

    api = SimpleNamespace(Institution=Institution, SsoIdentity=SsoIdentity, SsoPending=SsoPending,
                          http=O.default_http, _default=None)

    # ------------------------------------------------------------------ schema + tenant helpers
    def ensure_schema():
        """Idempotent migration: tenant columns, the default institution, and existing rows assigned to it."""
        from sqlalchemy import inspect, text
        insp = inspect(db.engine)
        for table in ('user', 'class_section'):
            if 'institution_id' not in {c['name'] for c in insp.get_columns(table)}:
                with db.engine.begin() as conn:
                    conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN institution_id INTEGER'))
        inst = Institution.query.filter_by(slug=DEFAULT_SLUG).first()
        if not inst:
            inst = Institution(slug=DEFAULT_SLUG, name=app.config.get('SITE_NAME', 'CIWT'), active=True)
            db.session.add(inst)
            db.session.commit()
        with db.engine.begin() as conn:
            for table in ('user', 'class_section'):
                conn.execute(text(f'UPDATE "{table}" SET institution_id = :i WHERE institution_id IS NULL'), {'i': inst.id})
        api._default = inst.id

    def default_id():
        if api._default is None:
            row = Institution.query.filter_by(slug=DEFAULT_SLUG).first()
            api._default = row.id if row else 0
        return api._default

    def tid(obj):
        return getattr(obj, 'institution_id', None) or default_id()

    def is_platform_admin(user):
        return getattr(user, 'role', None) == 'admin' and tid(user) == default_id()

    def same_tenant(user, obj):
        return is_platform_admin(user) or tid(user) == tid(obj)

    def scope(query, model, user):
        """Filter a User/ClassSection query to the caller's tenant (platform admins see everything)."""
        if is_platform_admin(user):
            return query
        t, col = tid(user), model.institution_id
        return query.filter(col == t) if t != default_id() else query.filter(db.or_(col == t, col.is_(None)))

    def tenant_of(user):
        return db.session.get(Institution, tid(user))

    @sa_event.listens_for(ClassSection, 'before_insert')
    def _section_tenant(mapper, conn, target):
        if target.institution_id is None:
            try:
                if current_user and current_user.is_authenticated:
                    target.institution_id = tid(current_user)
            except Exception:
                pass

    # ------------------------------------------------------------------ institution admins are fenced in
    @app.before_request
    def _tenant_fence():
        """Catch-all isolation: any route addressing a class or a person of another institution is a 404, whatever
        the view's own checks say; institution admins also stay out of platform-wide /admin pages."""
        if not getattr(current_user, 'is_authenticated', False) or is_platform_admin(current_user):
            return None
        va = request.view_args or {}
        sid = va.get('section_id')
        if isinstance(sid, int):
            sec = db.session.get(ClassSection, sid)
            if sec is not None and tid(sec) != tid(current_user):
                abort(404)
        uid = va.get('user_id')
        if isinstance(uid, int) and current_user.role in ('instructor', 'admin'):
            other = db.session.get(User, uid)
            if other is not None and tid(other) != tid(current_user):
                abort(404)
        if current_user.role == 'admin' and request.path.startswith('/admin') and (request.endpoint or '') not in TENANT_ADMIN_ENDPOINTS:
            abort(403)
        return None

    # ------------------------------------------------------------------ branding
    def brand():
        inst = None
        if getattr(current_user, 'is_authenticated', False) and tid(current_user) != default_id():
            inst = tenant_of(current_user)
        elif session.get('tenant'):
            inst = Institution.query.filter_by(slug=session['tenant'], active=True).first()
        return inst if inst and inst.slug != DEFAULT_SLUG else None

    @app.context_processor
    def _tenant_ctx():
        def sso_institutions():
            try:
                return [i for i in Institution.query.filter_by(active=True).order_by(Institution.name).all()
                        if i.sso.get('protocol') in ('oidc', 'saml')]
            except Exception:
                db.session.rollback()
                return []
        try:
            b = brand()
        except Exception:
            db.session.rollback()
            b = None
        return {'tenant_brand': b, 'sso_institutions': sso_institutions}

    def tenant_landing(slug):
        inst = Institution.query.filter_by(slug=slug, active=True).first_or_404()
        if inst.slug == DEFAULT_SLUG:
            session.pop('tenant', None)
            return redirect(url_for('login'))
        session['tenant'] = inst.slug
        return render_template('institutional/tenant_landing.html', inst=inst)

    def tenant_css(slug):
        inst = Institution.query.filter_by(slug=slug).first_or_404()
        p = inst.primary_color if HEX.match(inst.primary_color or '') else '#1f3a5f'
        a = inst.accent_color if HEX.match(inst.accent_color or '') else '#c8a24a'
        css = (f':root{{--tenant-primary:{p};--tenant-on-primary:{on_color(p)};--tenant-accent:{a};--tenant-on-accent:{on_color(a)}}}\n'
               '.tenant-banner{background:var(--tenant-primary);color:var(--tenant-on-primary)}\n'
               '.tenant-banner a{color:var(--tenant-on-primary)}\n'
               '.topbar{border-bottom:4px solid var(--tenant-accent)}\n'
               '.btn-tenant{background:var(--tenant-primary);color:var(--tenant-on-primary);border-color:var(--tenant-primary)}\n'
               '.btn-tenant:hover,.btn-tenant:focus{background:var(--tenant-accent);color:var(--tenant-on-accent)}\n')
        return Response(css, mimetype='text/css', headers={'Cache-Control': 'public, max-age=300'})

    # ------------------------------------------------------------------ SSO
    def _cfg(inst):
        cfg = inst.sso
        env_secret = os.environ.get(f'SSO_{inst.slug.upper().replace("-", "_")}_CLIENT_SECRET')
        if env_secret:
            cfg['client_secret'] = env_secret
        return cfg

    def sp_entity(inst):
        return _cfg(inst).get('sp_entity_id') or url_for('sso_saml_metadata', slug=inst.slug, _external=True)

    def acs_url(inst):
        return url_for('sso_saml_acs', slug=inst.slug, _external=True)

    def oidc_redirect(inst):
        return url_for('sso_oidc_callback', slug=inst.slug, _external=True)

    def _safe_next(n):
        return n if n and n.startswith('/') and not n.startswith('//') and '\\' not in n else None

    def provision(inst, protocol, ident):
        """Just-in-time provisioning + account linking. Never crosses tenants; admin only via explicit role_map."""
        cfg = _cfg(inst)
        email = (ident.get('email') or '').strip().lower()
        subject = ident.get('sub') or ident.get('name_id') or email
        if not email or '@' not in email:
            raise ValueError('Your campus sign-in did not include an email address.')
        doms = [x.strip().lower() for x in (inst.domain or '').split(',') if x.strip()]
        dom = email.rsplit('@', 1)[1]
        if doms and not any(dom == x or dom.endswith('.' + x) for x in doms):
            raise ValueError(f'{email} is not an address at {inst.name}.')
        link = SsoIdentity.query.filter_by(institution_id=inst.id, protocol=protocol, subject=subject).first()
        user = db.session.get(User, link.user_id) if link else User.query.filter_by(email=email).first()
        role = map_role(ident.get('attributes'), cfg)
        if user and tid(user) != inst.id:
            raise ValueError('That account belongs to a different institution. Ask your administrator to move it.')
        created = False
        if not user:
            if cfg.get('jit') is False:
                raise ValueError('No account exists for you yet. Ask your instructor to add you.')
            user = User(email=email, first_name=(ident.get('first_name') or email.split('@')[0])[:80],
                        last_name=(ident.get('last_name') or '')[:80], role=role, institution_id=inst.id,
                        password_hash=generate_password_hash(secrets.token_urlsafe(32)))
            db.session.add(user)
            db.session.flush()
            created = True
        elif cfg.get('sync_roles'):
            user.role = role
        if not link:
            db.session.add(SsoIdentity(institution_id=inst.id, user_id=user.id, protocol=protocol, subject=subject))
        else:
            link.last_login = utcnow()
        db.session.commit()
        session.pop('tenant', None)
        login_user(user)
        d['audit']('sso_login', f'{inst.slug} {protocol} {email}{" (new account)" if created else ""}')
        return user

    def _fail(inst, msg):
        d['audit']('sso_failed', f'{inst.slug if inst else "?"}: {msg}')
        flash(f'Campus sign-in failed: {msg}', 'danger')
        return redirect(url_for('login'))

    def sso_start():
        slug = (request.args.get('tenant') or '').strip()
        return redirect(url_for('sso_login', slug=slug)) if SLUG.match(slug) else redirect(url_for('login'))

    def sso_login(slug):
        inst = Institution.query.filter_by(slug=slug, active=True).first_or_404()
        cfg = _cfg(inst)
        nxt = _safe_next(request.args.get('next'))
        if cfg.get('protocol') == 'oidc':
            try:
                url, state, nonce, verifier = O.auth_url(cfg, oidc_redirect(inst), http=api.http)
            except Exception as e:
                return _fail(inst, f'identity provider unreachable ({e.__class__.__name__})')
            session['sso_oidc'] = {'slug': slug, 'state': state, 'nonce': nonce, 'verifier': verifier, 'next': nxt}
            return redirect(url)
        if cfg.get('protocol') == 'saml':
            if not cfg.get('idp_sso_url'):
                return _fail(inst, 'SAML IdP sign-on URL is not configured')
            tok = secrets.token_urlsafe(24)
            rid, url = S.authn_request(sp_entity(inst), acs_url(inst), cfg['idp_sso_url'], relay_state=tok)
            SsoPending.query.filter(SsoPending.created_at < utcnow() - timedelta(minutes=15)).delete()
            db.session.add(SsoPending(token=tok, institution_id=inst.id, request_id=rid))
            db.session.commit()
            if nxt:
                session['sso_next'] = nxt
            return redirect(url)
        abort(404)

    def sso_oidc_callback(slug):
        inst = Institution.query.filter_by(slug=slug, active=True).first_or_404()
        st = session.pop('sso_oidc', None)
        if not st or st.get('slug') != slug or not secrets.compare_digest(st.get('state', ''), request.args.get('state', '')):
            return _fail(inst, 'the sign-in response did not match this browser (state). Please try again.')
        if request.args.get('error'):
            return _fail(inst, request.args.get('error_description') or request.args['error'])
        try:
            ident = O.complete(_cfg(inst), request.args.get('code', ''), st['verifier'], st['nonce'], oidc_redirect(inst), http=api.http)
            provision(inst, 'oidc', ident)
        except (O.OidcError, ValueError) as e:
            db.session.rollback()
            return _fail(inst, str(e))
        return redirect(st.get('next') or url_for('index'))

    def sso_saml_metadata(slug):
        inst = Institution.query.filter_by(slug=slug).first_or_404()
        return Response(S.sp_metadata(sp_entity(inst), acs_url(inst), org=inst.name), mimetype='application/samlmetadata+xml')

    def sso_saml_acs(slug):
        inst = Institution.query.filter_by(slug=slug, active=True).first_or_404()
        cfg = _cfg(inst)
        pend = db.session.get(SsoPending, request.form.get('RelayState') or '\0')
        if pend and (pend.institution_id != inst.id or pend.created_at < utcnow() - timedelta(minutes=15)):
            pend = None
        try:
            ident = S.validate_response(request.form.get('SAMLResponse', ''), cfg, sp_entity(inst), acs_url(inst),
                                        request_id=pend.request_id if pend else None)
            if db.session.get(SsoReplay, ident['assertion_id']):
                raise S.SamlError('this assertion was already used (replay)')
            db.session.add(SsoReplay(assertion_id=ident['assertion_id']))
            if pend:
                db.session.delete(pend)
            ident['sub'] = ident['name_id']
            provision(inst, 'saml', ident)
        except (S.SamlError, ValueError) as e:
            db.session.rollback()
            return _fail(inst, str(e))
        return redirect(_safe_next(session.pop('sso_next', None)) or url_for('index'))

    # ------------------------------------------------------------------ admin
    def _admin_guard():
        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()
        if current_user.role != 'admin':
            abort(403)
        return None

    def _visible_insts():
        q = Institution.query.order_by(Institution.name)
        return q.all() if is_platform_admin(current_user) else q.filter_by(id=tid(current_user)).all()

    def _save(inst, form, platform):
        errors = []
        name = (form.get('name') or '').strip()
        if not name:
            errors.append('Name is required.')
        if platform:
            slug = (form.get('slug') or '').strip().lower()
            if not SLUG.match(slug):
                errors.append('Slug: 3–40 lowercase letters, digits or hyphens.')
            elif Institution.query.filter(Institution.slug == slug, Institution.id != (inst.id or 0)).first():
                errors.append('That slug is taken.')
            elif inst.slug == DEFAULT_SLUG and slug != DEFAULT_SLUG:
                errors.append('The default institution keeps the slug "default".')
            inst.slug = slug
            inst.active = slug == DEFAULT_SLUG or bool(form.get('active'))
        for f in ('primary_color', 'accent_color'):
            v = (form.get(f) or '').strip()
            if v and not HEX.match(v):
                errors.append(f'{f.replace("_", " ").capitalize()} must look like #1f3a5f.')
            setattr(inst, f, v or getattr(inst, f) or ('#1f3a5f' if f == 'primary_color' else '#c8a24a'))
        logo = (form.get('logo_url') or '').strip()
        if logo and not (logo.startswith('https://') or logo.startswith('/static/')):
            errors.append('Logo URL must be https:// or /static/.')
        try:
            cfg = json.loads(form.get('sso_config_json') or '{}')
            if not isinstance(cfg, dict) or cfg.get('protocol') not in (None, '', 'oidc', 'saml'):
                raise ValueError
            if cfg.get('protocol') == 'saml' and cfg.get('idp_cert'):
                S._load_cert(cfg['idp_cert'])
        except (ValueError, S.SamlError):
            errors.append('SSO settings must be a JSON object with "protocol": "oidc" or "saml" (and a valid PEM idp_cert for SAML).')
            cfg = None
        inst.name, inst.logo_url, inst.domain = name, logo or None, (form.get('domain') or '').strip().lower() or None
        if cfg is not None:
            inst.sso_config_json = json.dumps(cfg, indent=2)
        return errors

    def admin_institutions():
        g = _admin_guard()
        if g:
            return g
        platform = is_platform_admin(current_user)
        errors, draft = [], None
        if request.method == 'POST':
            if not platform:
                abort(403)
            draft = Institution()
            errors = _save(draft, request.form, True)
            if not errors:
                db.session.add(draft)
                db.session.commit()
                d['audit']('institution_create', draft.slug)
                flash(f'Created {draft.name}.', 'success')
                return redirect(url_for('admin_institution_edit', inst_id=draft.id))
            db.session.rollback()
        rows = [{'inst': i, 'users': User.query.filter(User.institution_id == i.id).count(),
                 'sections': ClassSection.query.filter(ClassSection.institution_id == i.id).count()} for i in _visible_insts()]
        return render_template('institutional/admin_list.html', rows=rows, platform=platform, errors=errors, draft=draft,
                               admin_tab='admin_institutions'), (400 if errors else 200)

    def admin_institution_edit(inst_id):
        g = _admin_guard()
        if g:
            return g
        inst = db.session.get(Institution, inst_id)
        if not inst or (not is_platform_admin(current_user) and inst.id != tid(current_user)):
            abort(404)
        errors = []
        if request.method == 'POST':
            errors = _save(inst, request.form, is_platform_admin(current_user))
            if not errors:
                db.session.commit()
                d['audit']('institution_update', inst.slug)
                flash('Saved.', 'success')
                return redirect(url_for('admin_institution_edit', inst_id=inst.id))
            db.session.rollback()
            inst = db.session.get(Institution, inst_id)
        urls = {'metadata': url_for('sso_saml_metadata', slug=inst.slug, _external=True), 'acs': acs_url(inst),
                'entity': sp_entity(inst), 'oidc_redirect': oidc_redirect(inst),
                'login': url_for('sso_login', slug=inst.slug, _external=True),
                'landing': url_for('tenant_landing', slug=inst.slug, _external=True)}
        return render_template('institutional/admin_edit.html', inst=inst, urls=urls, errors=errors,
                               platform=is_platform_admin(current_user), admin_tab='admin_institutions'), (400 if errors else 200)

    # ------------------------------------------------------------------ outcomes
    def _csv(rep, name):
        if request.args.get('format') == 'json':
            return app.response_class(json.dumps(OUT.to_json(rep), default=str, indent=1), mimetype='application/json',
                                      headers={'Content-Disposition': f'attachment; filename={name}.json'})
        buf = io.StringIO()
        w = csv.writer(buf)
        OUT.write_csv(rep, w)              # summary metrics first (stable header), then one row per course objective
        w.writerow([])
        w.writerow(OUT.OBJ_COLS)
        w.writerows(OUT.objective_rows(rep))
        return Response(buf.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={name}.csv'})

    def section_outcomes(section_id):
        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()
        section = db.session.get(ClassSection, section_id) or abort(404)
        if not d['can_access_section'](current_user, section):
            abort(403)
        rep = OUT.report(app, db, d, [section])
        if request.args.get('format') in ('csv', 'json'):
            return _csv(rep, f'outcomes-section-{section.id}')
        return render_template('institutional/outcomes.html', rep=rep, section=section, scope_label=section.name, sel=None)

    def admin_outcomes():
        g = _admin_guard()
        if g:
            return g
        sections = scope(ClassSection.query, ClassSection, current_user).order_by(ClassSection.name).all()
        platform = is_platform_admin(current_user)
        sel = request.args.get('institution', type=int) if platform else None
        if sel:
            sections = [s for s in sections if tid(s) == sel]
        rep = OUT.report(app, db, d, sections)
        if request.args.get('format') in ('csv', 'json'):
            return _csv(rep, 'outcomes-institution')
        label = tenant_of(current_user).name if not platform else (
            db.session.get(Institution, sel).name if sel and db.session.get(Institution, sel) else 'All institutions')
        return render_template('institutional/outcomes.html', rep=rep, section=None, scope_label=label,
                               institutions=_visible_insts() if platform else [], sel=sel, admin_tab='admin_outcomes')

    for rule, ep, fn, methods in [
        ('/t/<slug>', 'tenant_landing', tenant_landing, ['GET']),
        ('/t/<slug>/theme.css', 'tenant_css', tenant_css, ['GET']),
        ('/sso/start', 'sso_start', sso_start, ['GET']),
        ('/sso/<slug>/login', 'sso_login', sso_login, ['GET']),
        ('/sso/<slug>/oidc/callback', 'sso_oidc_callback', sso_oidc_callback, ['GET']),
        ('/sso/<slug>/saml/metadata.xml', 'sso_saml_metadata', sso_saml_metadata, ['GET']),
        ('/sso/<slug>/saml/acs', 'sso_saml_acs', sso_saml_acs, ['POST']),
        ('/admin/institutions', 'admin_institutions', admin_institutions, ['GET', 'POST']),
        ('/admin/institutions/<int:inst_id>', 'admin_institution_edit', admin_institution_edit, ['GET', 'POST']),
        ('/admin/outcomes', 'admin_outcomes', admin_outcomes, ['GET']),
        ('/instructor/section/<int:section_id>/outcomes', 'section_outcomes', section_outcomes, ['GET']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)
    csrf = app.extensions.get('csrf')
    if csrf:
        csrf.exempt(sso_saml_acs)   # cross-site POST from the IdP; integrity comes from the XML signature + RelayState

    api.ensure_schema, api.default_id, api.tid, api.same_tenant, api.scope = ensure_schema, default_id, tid, same_tenant, scope
    api.is_platform_admin, api.provision = is_platform_admin, provision
    app.extensions['ciwt_institutional'] = api
    return api
