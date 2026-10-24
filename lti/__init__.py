"""LTI 1.3 + LTI Advantage, tool side (pass 12).

  /lti/login                OIDC third-party login initiation (GET or POST from the LMS)
  /lti/launch               id_token form_post: resource link launch or deep-linking request
  /lti/jwks                 this tool's public key set
  /lti/config.json          tool URLs; /lti/config/canvas.json is a Canvas developer-key JSON
  /lti/deep-link/<token>    instructor picks lessons / labs / chapter checks / tests; signed response
  /lti/context/<id>/map     instructor maps an LMS course to one of their classes
  /admin/lti …              platform registrations (admin)
  /instructor/section/<id>/lti         links, scores to the LMS (AGS), roster sync (NRPS)

Security model: state is single-use and bound to the browser with a cookie; nonce is single-use;
id_token signature is checked against the platform JWKS (kid) with iss / aud / azp / exp / iat /
deployment / version / message-type checks (core.validate_id_token). LMS roles never grant admin
here; an existing local account is only linked by email when the admin turned that on for the
platform and never for admin accounts. Not 1EdTech-certified; tested against the in-repo mock
platform only (tools/lti_mock_platform.py), not a live Canvas, Blackboard or Moodle.
"""
import hashlib
import json
import os
import secrets
import time
from datetime import timedelta
from types import SimpleNamespace
from urllib.parse import urlencode, urlparse

from flask import (abort, flash, jsonify, make_response, redirect, render_template, request, session, url_for)
from flask_login import current_user, login_required, login_user

from . import core
from .http import Transport, url_allowed
from .keys import ToolKeys
from .models import define_models, utcnow

LOGIN_TTL = timedelta(minutes=10)
DL_TTL = timedelta(hours=1)
JWKS_TTL = 600
STATE_COOKIE = 'lti1p3_state'
KINDS = {
    'canvas': {'label': 'Canvas', 'issuer': 'https://canvas.instructure.com',
               'auth_login_url': 'https://sso.canvaslms.com/api/lti/authorize_redirect',
               'auth_token_url': 'https://sso.canvaslms.com/login/oauth2/token',
               'jwks_url': 'https://sso.canvaslms.com/api/lti/security/jwks'},
    'blackboard': {'label': 'Blackboard Learn', 'issuer': 'https://blackboard.com',
                   'auth_login_url': 'https://developer.blackboard.com/api/v1/gateway/oidcauth',
                   'auth_token_url': 'https://developer.blackboard.com/api/v1/gateway/oauth2/jwttoken',
                   'jwks_url': 'https://developer.blackboard.com/api/v1/management/applications/<client_id>/jwks.json'},
    'moodle': {'label': 'Moodle', 'issuer': 'https://<your-moodle-site>',
               'auth_login_url': 'https://<your-moodle-site>/mod/lti/auth.php',
               'auth_token_url': 'https://<your-moodle-site>/mod/lti/token.php',
               'jwks_url': 'https://<your-moodle-site>/mod/lti/certs.php'},
    'other': {'label': 'Other LTI 1.3 platform', 'issuer': '', 'auth_login_url': '', 'auth_token_url': '', 'jwks_url': ''},
}
GRADED = ('quiz', 'test', 'lab', 'course')


def register(app, db, deps, csrf):
    """deps: User, ClassSection, Enrollment, Course, Module, Lesson, Quiz, KnowledgeTest, LabProgress,
    labs_for_course, get_lab, can_access_section, audit, role_required."""
    m = define_models(db)
    d = SimpleNamespace(**deps)
    app.config.setdefault('LTI_ALLOW_LOOPBACK_HTTP', os.environ.get('LTI_ALLOW_LOOPBACK_HTTP') == '1')
    app.config.setdefault('LTI_REQUIRE_STATE_COOKIE', os.environ.get('LTI_REQUIRE_STATE_COOKIE', '1') != '0')
    state = {'transport': None, 'keys': ToolKeys(app.instance_path)}

    def K():
        return state['keys']
    jwks_cache, token_cache = {}, {}

    def http():
        return state['transport'] or Transport(allow_loopback_http=app.config['LTI_ALLOW_LOOPBACK_HTTP'])

    def loopback_ok():
        return app.config['LTI_ALLOW_LOOPBACK_HTTP']

    def ext(endpoint, **kw):
        return url_for(endpoint, _external=True, **kw)

    def fail(code, message, status=400):
        app.logger.warning('LTI refused: %s: %s', code, message)
        try:
            d.audit('lti_refused', f'{code}: {message}'[:400])
        except Exception:
            db.session.rollback()
        return render_template('lti/error.html', code=code, message=message), status

    # ------------------------------------------------------------ platform keys
    def platform_jwks(p, refresh=False):
        hit = jwks_cache.get(p.jwks_url)
        if hit and not refresh and hit[0] > time.time():
            return hit[1]
        if not url_allowed(p.jwks_url, loopback_ok()):
            raise core.LtiError('jwks_url', 'Platform JWKS URL must be HTTPS.')
        r = http()('GET', p.jwks_url, {'Accept': 'application/json'})
        if not r.ok:
            raise core.LtiError('jwks_fetch', f'Could not fetch the platform key set (HTTP {r.status}).')
        try:
            ks = r.json()
        except ValueError:
            raise core.LtiError('jwks_fetch', 'Platform key set is not JSON.')
        jwks_cache[p.jwks_url] = (time.time() + JWKS_TTL, ks)
        return ks

    def verify(p, token, nonce):
        h = core.peek_header(token)
        ks = platform_jwks(p)
        if h.get('kid') and not any(k.get('kid') == h['kid'] for k in ks.get('keys', [])):
            ks = platform_jwks(p, refresh=True)          # platform rotated its keys
        return core.validate_id_token(token, p.reg(), ks, nonce)

    # ------------------------------------------------------------ service tokens (AGS / NRPS)
    def access_token(p, scopes):
        k = (p.id, ' '.join(sorted(scopes)))
        hit = token_cache.get(k)
        if hit and hit[0] > time.time():
            return hit[1]
        if not url_allowed(p.auth_token_url, loopback_ok()):
            raise core.LtiError('token_url', 'Platform token URL must be HTTPS.')
        r = http()('POST', p.auth_token_url, {'Accept': 'application/json'},
                   core.token_request_body(p.reg(), scopes, K().private_pem, K().kid))
        if not r.ok:
            raise core.LtiError('token', f'Platform refused the service token (HTTP {r.status}).')
        body = r.json() or {}
        tok = body.get('access_token')
        if not tok:
            raise core.LtiError('token', 'Platform token response has no access_token.')
        token_cache[k] = (time.time() + max(30, int(body.get('expires_in') or 3600) - 30), tok)
        return tok

    # ------------------------------------------------------------ account mapping
    def names(claims):
        first = (claims.get('given_name') or '').strip()
        last = (claims.get('family_name') or '').strip()
        if not (first or last):
            parts = (claims.get('name') or '').strip().split()
            first, last = (parts[0], ' '.join(parts[1:])) if parts else ('', '')
        return (first or 'LMS')[:80], (last or 'user')[:80]

    def local_email(p, sub):
        return f'lti-{p.id}-{hashlib.sha256(sub.encode()).hexdigest()[:16]}@lti.invalid'

    def map_user(p, claims, how_new='created'):
        """Return (user, link, note). Never changes the role of an existing account."""
        sub = str(claims['sub'])
        roles = claims.get(core.CLAIM['roles']) or claims.get('roles') or []
        link = m.LtiUserLink.query.filter_by(platform_id=p.id, sub=sub).first()
        email = (claims.get('email') or '').strip().lower()
        user = db.session.get(d.User, link.user_id) if link else None
        how = None
        if user is None and email and p.link_by_email:
            cand = d.User.query.filter(db.func.lower(d.User.email) == email).first()
            if cand and cand.role != 'admin':
                user, how = cand, 'email'
        if user is None:
            if not p.create_accounts:
                return None, None, 'This LMS account is not linked to an account here, and new accounts are turned off for this LMS.'
            role = core.map_role(roles) or 'student'
            first, last = names(claims)
            use_email = email if email and not d.User.query.filter(db.func.lower(d.User.email) == email).first() else local_email(p, sub)
            user = d.User(email=use_email, first_name=first, last_name=last, role=role)
            user.set_password(secrets.token_urlsafe(32))        # LMS launch only; no password login until reset
            db.session.add(user)
            db.session.flush()
            how = how_new
        if link is None:
            link = m.LtiUserLink(platform_id=p.id, sub=sub, user_id=user.id, how=how)
            db.session.add(link)
        link.lms_email = email or link.lms_email
        link.lms_name = (claims.get('name') or ' '.join(names(claims)))[:255]
        link.last_roles = json.dumps(roles)[:4000]
        link.last_seen = utcnow()
        note = None
        if core.is_staff(roles) and user.role == 'student':
            note = 'Your LMS role is staff, but your account here is a student account; ask an administrator to change it.'
        return user, link, note

    def ensure_enrolled(user, section):
        if user.role != 'student' or not section:
            return False
        if d.Enrollment.query.filter_by(user_id=user.id, section_id=section.id).first():
            return False
        db.session.add(d.Enrollment(user_id=user.id, section_id=section.id))
        return True

    def upsert_context(p, claims):
        ctx = claims.get(core.CLAIM['context']) or {}
        if not ctx.get('id'):
            return None
        c = m.LtiContext.query.filter_by(platform_id=p.id, context_id=str(ctx['id'])).first()
        if c is None:
            c = m.LtiContext(platform_id=p.id, context_id=str(ctx['id']))
            db.session.add(c)
        c.deployment_id = claims.get(core.CLAIM['deployment_id'])
        c.title = (ctx.get('title') or c.title or '')[:255]
        c.label = (ctx.get('label') or c.label or '')[:255]
        ags = claims.get(core.CLAIM['ags']) or {}
        if ags.get('lineitems'):
            c.lineitems_url = ags['lineitems']
        if ags.get('scope'):
            c.ags_scopes = ' '.join(ags['scope'])
        nrps = claims.get(core.CLAIM['nrps']) or {}
        if nrps.get('context_memberships_url'):
            c.memberships_url = nrps['context_memberships_url']
        c.last_seen = utcnow()
        db.session.flush()
        return c

    def upsert_link(p, c, claims, target):
        rl = claims.get(core.CLAIM['resource_link']) or {}
        r = m.LtiResourceLink.query.filter_by(platform_id=p.id, resource_link_id=str(rl['id'])).first()
        if r is None:
            r = m.LtiResourceLink(platform_id=p.id, resource_link_id=str(rl['id']))
            db.session.add(r)
        r.context_pk = c.id if c else r.context_pk
        r.title = (rl.get('title') or r.title or '')[:255]
        if target:
            r.target = target[:120]
        ags = claims.get(core.CLAIM['ags']) or {}
        if ags.get('lineitem'):
            r.lineitem_url = ags['lineitem']
        r.last_seen = utcnow()
        return r

    # ------------------------------------------------------------ targets
    def parse_target(t):
        kind, _, ident = (t or '').partition(':')
        if kind == 'course':
            return 'course', None
        if kind in ('lesson', 'quiz', 'test') and ident.isdigit():
            return kind, int(ident)
        if kind == 'lab' and ident and d.get_lab(ident):
            return 'lab', ident
        return None, None

    def target_url(section, target):
        kind, ident = parse_target(target)
        if kind == 'lesson':
            les = db.session.get(d.Lesson, ident)
            if les and les.module.course_id == section.course_id:
                return url_for('view_lesson', section_id=section.id, module_id=les.module_id, lesson_id=les.id)
        elif kind == 'quiz':
            q = db.session.get(d.Quiz, ident)
            if q and q.module.course_id == section.course_id:
                return url_for('take_quiz', section_id=section.id, quiz_id=q.id)
        elif kind == 'test':
            t = db.session.get(d.KnowledgeTest, ident)
            if t and t.course_id == section.course_id:
                return url_for('take_test', section_id=section.id, test_id=t.id)
        elif kind == 'lab':
            return url_for('interactive_lab', lab_id=ident, section_id=section.id)
        return None

    def home_url(user, section):
        if user.role == 'student':
            return url_for('student_section', section_id=section.id)
        return url_for('instructor_section', section_id=section.id)

    def catalog(section):
        """What an instructor can place into the LMS course: lessons, chapter checks, tests, labs."""
        course = db.session.get(d.Course, section.course_id)
        chapters = []
        for mod in d.Module.query.filter_by(course_id=course.id).order_by(d.Module.order).all():
            items = [{'target': f'lesson:{l.id}', 'title': l.title, 'kind': 'lesson'} for l in mod.lessons]
            items += [{'target': f'quiz:{q.id}', 'title': q.title, 'kind': 'quiz'}
                      for q in d.Quiz.query.filter_by(module_id=mod.id).order_by(d.Quiz.id).all()]
            chapters.append({'title': f'Chapter {mod.order}: {mod.title}', 'entries': items})
        tests = [{'target': f'test:{t.id}', 'title': t.title, 'kind': 'test'}
                 for t in d.KnowledgeTest.query.filter_by(course_id=course.id).order_by(d.KnowledgeTest.order).all()]
        labs = []
        for lab in d.labs_for_course(course):
            lab = lab if isinstance(lab, dict) else d.get_lab(lab)
            if lab:
                labs.append({'target': f'lab:{lab["id"]}', 'title': lab['title'], 'kind': 'lab'})
        return {'course': course, 'chapters': chapters, 'tests': tests, 'labs': labs,
                'course_item': {'target': 'course', 'title': f'{course.title}: class home and course grade', 'kind': 'course'}}

    def catalog_index(cat):
        out = {cat['course_item']['target']: cat['course_item']}
        for ch in cat['chapters']:
            for it in ch['entries']:
                out[it['target']] = it
        for it in cat['tests'] + cat['labs']:
            out[it['target']] = it
        return out

    # ------------------------------------------------------------ public endpoints
    @csrf.exempt
    def lti_login():
        f = request.values
        iss, hint = f.get('iss'), f.get('login_hint')
        if not iss or not hint:
            return fail('login_params', 'The LMS did not send iss and login_hint.')
        q = m.LtiPlatform.query.filter_by(issuer=iss, active=True)
        if f.get('reg', '').isdigit():
            q = q.filter_by(id=int(f['reg']))
        if f.get('client_id'):
            q = q.filter_by(client_id=f['client_id'])
        regs = q.all()
        if not regs:
            return fail('unknown_platform', 'This LMS is not registered here. An administrator adds it under Admin → LMS (LTI).')
        if len(regs) > 1:
            return fail('ambiguous_platform', 'Several registrations match this LMS; use the login URL with ?reg=<id> '
                        'shown on Admin → LMS (LTI).')
        p = regs[0]
        target = f.get('target_link_uri') or ext('lti_launch')
        if urlparse(target).netloc != urlparse(request.host_url).netloc:
            return fail('target_link_uri', 'target_link_uri does not point at this tool.')
        st, nonce = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        cutoff = utcnow() - LOGIN_TTL * 6
        m.LtiLogin.query.filter(m.LtiLogin.created_at < cutoff).delete()
        db.session.add(m.LtiLogin(state=st, nonce=nonce, platform_id=p.id, target_link_uri=target[:1000]))
        db.session.commit()
        params = {'scope': 'openid', 'response_type': 'id_token', 'response_mode': 'form_post', 'prompt': 'none',
                  'client_id': p.client_id, 'redirect_uri': ext('lti_launch'), 'login_hint': hint,
                  'state': st, 'nonce': nonce}
        if f.get('lti_message_hint'):
            params['lti_message_hint'] = f['lti_message_hint']
        sep = '&' if '?' in p.auth_login_url else '?'
        resp = redirect(p.auth_login_url + sep + urlencode(params), code=302)
        secure = request.is_secure
        resp.set_cookie(STATE_COOKIE, st, max_age=int(LOGIN_TTL.total_seconds()), httponly=True, secure=secure,
                        samesite='None' if secure else 'Lax', path='/lti/')
        return resp

    @csrf.exempt
    def lti_launch():
        if request.method != 'POST':
            return fail('method', 'LTI launches arrive as a form POST from the LMS.', 405)
        st, token = request.form.get('state', ''), request.form.get('id_token', '')
        if request.form.get('error'):
            return fail('platform_error', f'The LMS reported: {request.form.get("error")} {request.form.get("error_description", "")}')
        if not st or not token:
            return fail('launch_params', 'Missing state or id_token.')
        login = m.LtiLogin.query.filter_by(state=st).first()
        if login is None or login.used_at is not None or login.created_at < utcnow() - LOGIN_TTL:
            return fail('state', 'This launch is unknown, expired or already used. Open the link from the LMS again.')
        cookie = request.cookies.get(STATE_COOKIE)
        if cookie != st and (cookie or app.config['LTI_REQUIRE_STATE_COOKIE']):
            return fail('state_cookie', 'This launch did not start in this browser (state cookie missing or different). '
                        'If the LMS opens the tool in an iframe, open it in a new window or allow cookies for this site.')
        login.used_at = utcnow()
        db.session.commit()
        p = db.session.get(m.LtiPlatform, login.platform_id)
        if p is None or not p.active:
            return fail('unknown_platform', 'This LMS registration is turned off.')
        try:
            unverified = core.peek_claims(token)
            if unverified.get('iss') != p.issuer:
                raise core.LtiError('jwt_iss', 'id_token issuer does not match the login request.')
            claims = verify(p, token, login.nonce)
        except core.LtiError as e:
            return fail(e.code, str(e))
        user, link, note = map_user(p, claims)
        if user is None:
            db.session.rollback()
            return fail('no_account', note, 403)
        c = upsert_context(p, claims)
        mt = claims[core.CLAIM['message_type']]
        custom = claims.get(core.CLAIM['custom']) or {}
        rl = None
        if mt == core.MSG_LAUNCH:
            rl = upsert_link(p, c, claims, custom.get('ciwt_target'))
        db.session.commit()
        session.clear()
        login_user(user)
        session['lti'] = {'platform_id': p.id, 'context_pk': c.id if c else None, 'rl': rl.id if rl else None,
                          'return_url': (claims.get(core.CLAIM['launch_presentation']) or {}).get('return_url')}
        d.audit('lti_launch', f'platform {p.id} {mt} user {user.id} via {link.how or "link"}')
        if note:
            flash(note, 'warning')
        if mt == core.MSG_DL:
            if user.role not in ('instructor', 'admin') or not core.is_staff(claims.get(core.CLAIM['roles'])):
                return fail('dl_role', 'Only instructors can add content to an LMS course.', 403)
            tok = secrets.token_urlsafe(24)
            db.session.add(m.LtiDeepLink(token=tok, platform_id=p.id, user_id=user.id, claims_json=json.dumps(claims)))
            db.session.commit()
            return redirect(url_for('lti_deep_link', token=tok, ctx=c.id if c else ''))
        section = db.session.get(d.ClassSection, c.section_id) if c and c.section_id else None
        if section is None:
            if user.role in ('instructor', 'admin') and c:
                flash('This LMS course is not connected to a class here yet. Pick the class it belongs to.', 'info')
                return redirect(url_for('lti_context_map', cid=c.id))
            return render_template('lti/not_ready.html', ctx=c), 200
        if user.role == 'student':
            if ensure_enrolled(user, section):
                db.session.commit()
                d.audit('lti_enroll', f'user {user.id} section {section.id} (LMS launch)')
        elif not d.can_access_section(user, section):
            return fail('section_access', 'You launched from an LMS course mapped to a class you do not teach here.', 403)
        return redirect(target_url(section, rl.target if rl else None) or home_url(user, section))

    def lti_jwks():
        resp = jsonify(K().jwks())
        resp.headers['Cache-Control'] = 'public, max-age=300'
        return resp

    def tool_urls():
        return {'login': ext('lti_login'), 'launch': ext('lti_launch'), 'jwks': ext('lti_jwks'),
                'deep_link': ext('lti_launch'), 'domain': urlparse(request.host_url).hostname}

    def lti_config():
        return jsonify({'title': 'Novak Learning', 'oidc_initiation_url': ext('lti_login'), 'target_link_uri': ext('lti_launch'),
                        'redirect_uris': [ext('lti_launch')], 'jwks_uri': ext('lti_jwks'),
                        'messages': [core.MSG_LAUNCH, core.MSG_DL], 'scopes': list(core.SCOPE.values()),
                        'note': 'Not 1EdTech-certified. Tested against an in-repo mock platform only.'})

    def lti_canvas_config():
        """Paste into Canvas: Developer Keys → + LTI Key → Method: Paste JSON."""
        u = tool_urls()
        return jsonify({
            'title': 'Novak Learning', 'description': 'Lessons, live labs, chapter checks and tests.',
            'oidc_initiation_url': u['login'], 'target_link_uri': u['launch'], 'public_jwk_url': u['jwks'],
            'scopes': list(core.SCOPE.values()),
            'extensions': [{'domain': u['domain'], 'tool_id': 'novak-learning', 'platform': 'canvas.instructure.com',
                            'privacy_level': 'public', 'settings': {'text': 'Novak Learning', 'placements': [
                                {'placement': 'link_selection', 'message_type': core.MSG_DL, 'target_link_uri': u['launch']},
                                {'placement': 'assignment_selection', 'message_type': core.MSG_DL, 'target_link_uri': u['launch']},
                                {'placement': 'course_navigation', 'message_type': core.MSG_LAUNCH, 'target_link_uri': u['launch'],
                                 'custom_fields': {'ciwt_target': 'course'}}]}}],
            'custom_fields': {}})

    # ------------------------------------------------------------ deep linking
    @login_required
    def lti_deep_link(token):
        dl = m.LtiDeepLink.query.filter_by(token=token).first()
        if dl is None or dl.user_id != current_user.id:
            abort(404)
        if dl.used_at is not None or dl.created_at < utcnow() - DL_TTL:
            return fail('dl_expired', 'This content picker has expired. Start again from the LMS.')
        claims = json.loads(dl.claims_json)
        p = db.session.get(m.LtiPlatform, dl.platform_id)
        settings = claims.get(core.CLAIM['dl_settings']) or {}
        ctx_claim = claims.get(core.CLAIM['context']) or {}
        c = m.LtiContext.query.filter_by(platform_id=p.id, context_id=str(ctx_claim.get('id'))).first() if ctx_claim.get('id') else None
        mine = [s for s in d.ClassSection.query.order_by(d.ClassSection.name).all() if d.can_access_section(current_user, s)]
        section = db.session.get(d.ClassSection, c.section_id) if c and c.section_id else None
        if request.method == 'POST':
            if not section:
                sid = request.form.get('section_id', type=int)
                section = next((s for s in mine if s.id == sid), None)
                if section is None:
                    flash('Pick the class this LMS course belongs to.', 'warning')
                    return redirect(url_for('lti_deep_link', token=token))
                if c:
                    c.section_id = section.id
                    db.session.commit()
                    d.audit('lti_context_map', f'context {c.id} → section {section.id} (deep link)')
                if request.form.get('pick_only') and c:
                    return redirect(url_for('lti_deep_link', token=token), code=303)
            elif not d.can_access_section(current_user, section):
                abort(403)
            idx = catalog_index(catalog(section))
            chosen = [t for t in request.form.getlist('target') if t in idx]
            if not settings.get('accept_multiple', True):
                chosen = chosen[:1]
            if 'ltiResourceLink' not in (settings.get('accept_types') or ['ltiResourceLink']):
                return fail('dl_types', 'The LMS does not accept LTI resource links here.')
            gradebook = request.form.get('line_items') == '1'
            items = []
            for t in chosen:
                it = idx[t]
                li = ({'scoreMaximum': 100, 'label': it['title'][:200], 'resourceId': t, 'tag': 'novak'}
                      if gradebook and it['kind'] in GRADED else None)
                items.append(core.resource_link_item(it['title'], ext('lti_launch'), t, line_item=li))
            jwt_out = core.deep_link_response(p.reg(), claims, items, K().private_pem, K().kid,
                                              msg=f'Added {len(items)} item{"s" if len(items) != 1 else ""} from Novak Learning.' if items else None)
            dl.used_at = utcnow()
            db.session.commit()
            d.audit('lti_deep_link', f'platform {p.id}: {", ".join(chosen)[:300] or "nothing"}')
            return render_template('lti/autopost.html', action=settings['deep_link_return_url'], fields={'JWT': jwt_out},
                                   n=len(items), items=items)
        cat = catalog(section) if section else None
        return render_template('lti/deep_link.html', dl=dl, p=p, settings=settings, ctx=c, ctx_claim=ctx_claim,
                               section=section, sections=mine, cat=cat, graded=GRADED)

    @login_required
    def lti_context_map(cid):
        c = db.get_or_404(m.LtiContext, cid)
        if current_user.role not in ('instructor', 'admin'):
            abort(403)
        if not (m.LtiUserLink.query.filter_by(platform_id=c.platform_id, user_id=current_user.id).first()
                or current_user.role == 'admin'):
            abort(403)                       # only someone who launched from that LMS (or an admin) can map it
        if c.section_id and not d.can_access_section(current_user, db.session.get(d.ClassSection, c.section_id)):
            abort(403)
        mine = [s for s in d.ClassSection.query.order_by(d.ClassSection.name).all() if d.can_access_section(current_user, s)]
        if request.method == 'POST':
            sid = request.form.get('section_id', type=int)
            s = next((x for x in mine if x.id == sid), None)
            if s is None:
                abort(400)
            c.section_id = s.id
            db.session.commit()
            d.audit('lti_context_map', f'context {c.id} → section {s.id}')
            flash(f'LMS course “{c.title or c.context_id}” is now connected to {s.name}.', 'success')
            return redirect(url_for('instructor_lti', section_id=s.id))
        return render_template('lti/context_map.html', ctx=c, sections=mine, platform=db.session.get(m.LtiPlatform, c.platform_id))

    # ------------------------------------------------------------ AGS + NRPS
    def scores_for(section, target, user_ids):
        """Score 0-100 per user for one placed item, from the gradebook (late penalties, overrides and
        excused cells included) or the lab record. None = nothing to send yet."""
        kind, ident = parse_target(target)
        out = {}
        if kind in ('quiz', 'test', 'course'):
            exempt = scores_for.exempt = set()
            gb = app.extensions['ciwt_gradebook'].compute(section)
            for r in gb['rows']:
                if r['user'].id not in user_ids:
                    continue
                if kind == 'course':
                    out[r['user'].id] = r['grade']
                    continue
                cell = next((c for c in r['cells'] if c['item']['type'] == kind and c['item']['id'] == ident), None)
                out[r['user'].id] = cell['score'] if cell and cell['status'] in ('scored', 'override') else None
                if cell and cell['status'] == 'exempt':
                    exempt.add(r['user'].id)
        elif kind == 'lab':
            for uid in user_ids:
                row = d.LabProgress.query.filter_by(user_id=uid, lab_id=ident).first()
                out[uid] = round(max(row.best_score or 0, row.score or 0), 1) if row and (row.best_score or row.score) else None
        return out

    def find_or_create_lineitem(p, c, r):
        if r.lineitem_url:
            return r.lineitem_url
        if not c or not c.lineitems_url:
            return None
        scopes = (c.ags_scopes or '').split()
        tok = access_token(p, [core.SCOPE['lineitem']] if core.SCOPE['lineitem'] in scopes else [core.SCOPE['lineitem_ro']])
        sep = '&' if '?' in c.lineitems_url else '?'
        g = http()('GET', c.lineitems_url + sep + urlencode({'resource_link_id': r.resource_link_id}),
                   {'Authorization': f'Bearer {tok}', 'Accept': core.MT_LINEITEMS})
        if g.ok:
            found = [li for li in (g.json() or []) if li.get('resourceLinkId') == r.resource_link_id]
            if found:
                r.lineitem_url = found[0]['id']
                return r.lineitem_url
        if core.SCOPE['lineitem'] not in scopes:
            return None
        body = json.dumps({'scoreMaximum': 100, 'label': r.title or r.target, 'resourceId': r.target,
                           'resourceLinkId': r.resource_link_id, 'tag': 'novak'})
        cr = http()('POST', c.lineitems_url, {'Authorization': f'Bearer {tok}', 'Content-Type': core.MT_LINEITEM,
                                              'Accept': core.MT_LINEITEM}, body)
        if cr.ok:
            r.lineitem_url = (cr.json() or {}).get('id')
        return r.lineitem_url

    def section_setting(section_id):
        return db.session.get(m.LtiSectionSetting, section_id) or m.LtiSectionSetting(
            section_id=section_id, remove_dropped=False, auto_passback=False, exempt_full=False)

    def send_scores(section, actor, user_ids=None, auto=False):
        ctxs = m.LtiContext.query.filter_by(section_id=section.id).all()
        if auto and not ctxs:
            return None
        cfg = section_setting(section.id)
        sent = failed = skipped = 0
        lines = []
        for c in ctxs:
            p = db.session.get(m.LtiPlatform, c.platform_id)
            if not p or not p.active or core.SCOPE['score'] not in (c.ags_scopes or '').split():
                lines.append(f'{c.title or c.context_id}: the LMS did not grant the score scope.')
                continue
            enrolled = {e.user_id for e in d.Enrollment.query.filter_by(section_id=section.id)}
            links = {l.user_id: l for l in m.LtiUserLink.query.filter_by(platform_id=p.id)
                     if l.user_id in enrolled and (user_ids is None or l.user_id in user_ids)}
            for r in m.LtiResourceLink.query.filter_by(context_pk=c.id).order_by(m.LtiResourceLink.id).all():
                kind, _ = parse_target(r.target)
                if kind not in GRADED:
                    continue
                try:
                    li = find_or_create_lineitem(p, c, r)
                    if not li:
                        lines.append(f'{r.title or r.target}: no gradebook column in the LMS.')
                        continue
                    tok = access_token(p, [core.SCOPE['score']])
                    scores_for.exempt = set()
                    scores = scores_for(section, r.target, set(links))
                    for uid, link in sorted(links.items()):
                        sc, note = scores.get(uid), None
                        if sc is None and uid in scores_for.exempt and cfg.exempt_full:
                            sc, note = 100, 'Exempt: tested out with a mastery check'
                        if sc is None:
                            skipped += 1
                            continue
                        res = http()('POST', core.scores_url(li), {'Authorization': f'Bearer {tok}', 'Content-Type': core.MT_SCORE},
                                     json.dumps(core.score_payload(link.sub, sc, comment=note) if note else core.score_payload(link.sub, sc)))
                        if res.ok:
                            sent += 1
                        else:
                            failed += 1
                            lines.append(f'{r.title or r.target}: HTTP {res.status} for one student.')
                except (core.LtiError, ValueError, OSError) as e:
                    failed += 1
                    lines.append(f'{r.title or r.target}: {e}')
        log = m.LtiSyncLog(platform_id=ctxs[0].platform_id if ctxs else None, context_pk=ctxs[0].id if ctxs else None,
                           kind='auto-scores' if auto else 'scores', actor_id=actor.id, ok=sent, failed=failed, skipped=skipped, detail='\n'.join(lines)[:4000])
        db.session.add(log)
        db.session.commit()
        d.audit('lti_scores', f'section {section.id}: {sent} sent, {failed} failed, {skipped} with no score yet')
        return log

    def sync_roster(section, actor):
        ctxs = [c for c in m.LtiContext.query.filter_by(section_id=section.id).all() if c.memberships_url]
        added = linked = staff = inactive = failed = removed = 0
        lines = []
        cfg = section_setting(section.id)
        for c in ctxs:
            p = db.session.get(m.LtiPlatform, c.platform_id)
            if not p or not p.active:
                continue
            active, complete = set(), False
            try:
                tok = access_token(p, [core.SCOPE['nrps']])
                url, pages = c.memberships_url, 0
                while url and pages < 50:
                    pages += 1
                    r = http()('GET', url, {'Authorization': f'Bearer {tok}', 'Accept': core.MT_NRPS})
                    if not r.ok:
                        raise core.LtiError('nrps', f'Roster request refused (HTTP {r.status}).')
                    body = r.json() or {}
                    for mem in body.get('members') or []:
                        if (mem.get('status') or 'Active') != 'Active':
                            inactive += 1
                            continue
                        if not mem.get('user_id'):
                            continue
                        claims = {'sub': mem['user_id'], 'email': mem.get('email'), 'name': mem.get('name'),
                                  'given_name': mem.get('given_name'), 'family_name': mem.get('family_name'),
                                  core.CLAIM['roles']: mem.get('roles') or []}
                        before = m.LtiUserLink.query.filter_by(platform_id=p.id, sub=str(mem['user_id'])).first()
                        user, _link, _ = map_user(p, claims, how_new='roster')
                        if user is None:
                            failed += 1
                            continue
                        if before is None:
                            linked += 1
                        if core.is_staff(mem.get('roles')):
                            staff += 1
                        else:
                            active.add(user.id)
                            added += 1 if ensure_enrolled(user, section) else 0
                    url = core.parse_link_next(r.headers.get('link'))
                complete = not url
            except (core.LtiError, ValueError, OSError) as e:
                failed += 1
                lines.append(f'{c.title or c.context_id}: {e}')
            if cfg.remove_dropped and complete:   # only after a full, successful roster read
                linked_here = {l.user_id for l in m.LtiUserLink.query.filter_by(platform_id=p.id)}
                for e in d.Enrollment.query.filter_by(section_id=section.id).all():
                    u = db.session.get(d.User, e.user_id)
                    if u and u.role == 'student' and e.user_id in linked_here and e.user_id not in active:
                        db.session.delete(e)   # grades, attempts and lab history stay on the student record
                        removed += 1
        if not ctxs:
            lines.append('No connected LMS course offered a roster (Names and Role Provisioning) service.')
        lines.insert(0, f'{added} enrolled, {linked} newly linked, {staff} staff (not enrolled), '
                        + (f'{inactive} inactive or dropped in the LMS, {removed} removed from this class '
                           '(their records are kept).' if cfg.remove_dropped else
                           f'{inactive} inactive in the LMS (left as they are here; nobody is removed).'))
        log = m.LtiSyncLog(platform_id=ctxs[0].platform_id if ctxs else None, context_pk=ctxs[0].id if ctxs else None,
                           kind='roster', actor_id=actor.id, ok=added, failed=failed, skipped=inactive, detail='\n'.join(lines)[:4000])
        db.session.add(log)
        db.session.commit()
        d.audit('lti_roster', f'section {section.id}: ' + lines[0])
        return log

    # ------------------------------------------------------------ instructor page
    def staff_section(section_id):
        s = db.get_or_404(d.ClassSection, section_id)
        if not d.can_access_section(current_user, s):
            abort(403)
        return s

    @login_required
    def instructor_lti(section_id):
        s = staff_section(section_id)
        ctxs = m.LtiContext.query.filter_by(section_id=s.id).all()
        rows = []
        for c in ctxs:
            links = m.LtiResourceLink.query.filter_by(context_pk=c.id).order_by(m.LtiResourceLink.id).all()
            rows.append({'ctx': c, 'platform': db.session.get(m.LtiPlatform, c.platform_id), 'links': links,
                         'scopes': (c.ags_scopes or '').split()})
        enrolled = {e.user_id for e in d.Enrollment.query.filter_by(section_id=s.id)}
        n_linked = m.LtiUserLink.query.filter(m.LtiUserLink.user_id.in_(enrolled)).count() if enrolled else 0
        logs = (m.LtiSyncLog.query.filter(m.LtiSyncLog.context_pk.in_([c.id for c in ctxs]))
                .order_by(m.LtiSyncLog.at.desc()).limit(25).all()) if ctxs else []
        return render_template('lti/section.html', section=s, rows=rows, logs=logs, cfg=section_setting(s.id), n_linked=n_linked,
                               n_enrolled=len(enrolled), scope=core.SCOPE, parse_target=parse_target, graded=GRADED)

    @login_required
    def instructor_lti_scores(section_id):
        s = staff_section(section_id)
        log = send_scores(s, current_user)
        flash(f'Scores to the LMS: {log.ok} sent, {log.failed} failed, {log.skipped} with no score yet.',
              'success' if not log.failed else 'warning')
        return redirect(url_for('instructor_lti', section_id=s.id), code=303)

    @login_required
    def instructor_lti_roster(section_id):
        s = staff_section(section_id)
        log = sync_roster(s, current_user)
        flash('Roster from the LMS: ' + (log.detail or '').split('\n')[0], 'success' if not log.failed else 'warning')
        return redirect(url_for('instructor_lti', section_id=s.id), code=303)

    # ------------------------------------------------------------ admin
    def admin_only():
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)

    @login_required
    def admin_lti():
        admin_only()
        regs = m.LtiPlatform.query.order_by(m.LtiPlatform.name).all()
        counts = {p.id: {'users': m.LtiUserLink.query.filter_by(platform_id=p.id).count(),
                         'contexts': m.LtiContext.query.filter_by(platform_id=p.id).count()} for p in regs}
        return render_template('lti/admin.html', regs=regs, counts=counts, urls=tool_urls(), kinds=KINDS,
                               key_source=K().source(), kid=K().kid)

    def clean_url(v, label, errs):
        v = (v or '').strip()
        if not v:
            errs.append(f'{label} is required.')
        elif '<' in v or not url_allowed(v, loopback_ok()):
            errs.append(f'{label} must be a full https:// URL.')
        return v

    @login_required
    def admin_lti_edit(pid=None):
        admin_only()
        p = db.get_or_404(m.LtiPlatform, pid) if pid else None
        kind = request.values.get('kind') or (p.kind if p else 'canvas')
        if kind not in KINDS:
            kind = 'other'
        errs = []
        if request.method == 'POST':
            f = request.form
            name = (f.get('name') or '').strip()[:120]
            issuer = (f.get('issuer') or '').strip()
            client_id = (f.get('client_id') or '').strip()
            if not name:
                errs.append('Name is required.')
            if not issuer or '<' in issuer:
                errs.append('Issuer is required (exactly as the LMS sends it).')
            if not client_id:
                errs.append('Client ID is required.')
            login_url = clean_url(f.get('auth_login_url'), 'OIDC authorization URL', errs)
            token_url = clean_url(f.get('auth_token_url'), 'Token URL', errs)
            jwks_url = clean_url(f.get('jwks_url'), 'Platform JWKS URL', errs)
            aud = (f.get('token_audience') or '').strip() or None
            deps_ = [x.strip() for x in (f.get('deployment_ids') or '').replace(',', '\n').splitlines() if x.strip()]
            if not deps_:
                errs.append('Add at least one deployment ID.')
            dup = m.LtiPlatform.query.filter_by(issuer=issuer, client_id=client_id).first()
            if dup and (not p or dup.id != p.id):
                errs.append('A registration with this issuer and client ID already exists.')
            if not errs:
                if p is None:
                    p = m.LtiPlatform()
                    db.session.add(p)
                p.name, p.kind, p.issuer, p.client_id = name, kind, issuer, client_id
                p.auth_login_url, p.auth_token_url, p.jwks_url, p.token_audience = login_url, token_url, jwks_url, aud
                p.deployment_ids_json = json.dumps(deps_)
                p.link_by_email = f.get('link_by_email') == '1'
                p.create_accounts = f.get('create_accounts') == '1'
                p.active = f.get('active') == '1'
                p.updated_at = utcnow()
                db.session.commit()
                jwks_cache.pop(p.jwks_url, None)
                d.audit('lti_platform_save', f'{p.id} {p.name} ({p.issuer})')
                flash(f'Saved “{p.name}”.', 'success')
                return redirect(url_for('admin_lti'), code=303)
        preset = KINDS[kind]
        return render_template('lti/admin_edit.html', p=p, kind=kind, kinds=KINDS, preset=preset, errs=errs,
                               form=request.form if request.method == 'POST' else None, urls=tool_urls())

    @login_required
    def instructor_lti_settings(section_id):
        s = staff_section(section_id)
        cfg = db.session.get(m.LtiSectionSetting, s.id) or m.LtiSectionSetting(section_id=s.id)
        for k in ('remove_dropped', 'auto_passback', 'exempt_full'):
            setattr(cfg, k, request.form.get(k) == 'on')
        db.session.add(cfg)
        db.session.commit()
        d.audit('lti_settings', f'section {s.id}: remove_dropped={cfg.remove_dropped} auto={cfg.auto_passback} '
                                f'exempt_full={cfg.exempt_full}')
        flash('LMS settings saved.', 'success')
        return redirect(url_for('instructor_lti', section_id=s.id), code=303)

    AUTO_EPS = ('take_quiz', 'take_test')

    @app.after_request
    def _lti_auto_passback(resp):
        """Auto-passback: after a student submits a quiz, test or lab, send just their scores (opt-in per class)."""
        ep = request.endpoint or ''
        if (request.method != 'POST' or resp.status_code >= 400 or not current_user.is_authenticated
                or current_user.role != 'student' or not (ep in AUTO_EPS or 'lab' in ep)):
            return resp
        try:
            sid = (request.view_args or {}).get('section_id')
            sids = [sid] if sid else [e.section_id for e in d.Enrollment.query.filter_by(user_id=current_user.id)]
            for cfg in m.LtiSectionSetting.query.filter(m.LtiSectionSetting.section_id.in_(sids or [0]),
                                                        m.LtiSectionSetting.auto_passback.is_(True)).all():
                send_scores(db.session.get(d.ClassSection, cfg.section_id), current_user, {current_user.id}, auto=True)
        except Exception as exc:   # passback must never break a submission
            db.session.rollback()
            print('lti auto-passback:', exc)
        return resp

    rules = [
        ('/instructor/section/<int:section_id>/lti/settings', 'instructor_lti_settings', instructor_lti_settings, ['POST']),
        ('/lti/login', 'lti_login', lti_login, ['GET', 'POST']),
        ('/lti/launch', 'lti_launch', lti_launch, ['GET', 'POST']),
        ('/lti/jwks', 'lti_jwks', lti_jwks, ['GET']),
        ('/lti/config.json', 'lti_config', lti_config, ['GET']),
        ('/lti/config/canvas.json', 'lti_canvas_config', lti_canvas_config, ['GET']),
        ('/lti/deep-link/<token>', 'lti_deep_link', lti_deep_link, ['GET', 'POST']),
        ('/lti/context/<int:cid>/map', 'lti_context_map', lti_context_map, ['GET', 'POST']),
        ('/instructor/section/<int:section_id>/lti', 'instructor_lti', instructor_lti, ['GET']),
        ('/instructor/section/<int:section_id>/lti/scores', 'instructor_lti_scores', instructor_lti_scores, ['POST']),
        ('/instructor/section/<int:section_id>/lti/roster', 'instructor_lti_roster', instructor_lti_roster, ['POST']),
        ('/admin/lti', 'admin_lti', admin_lti, ['GET']),
        ('/admin/lti/new', 'admin_lti_new', admin_lti_edit, ['GET', 'POST']),
        ('/admin/lti/<int:pid>', 'admin_lti_edit', admin_lti_edit, ['GET', 'POST']),
    ]
    for rule, ep, fn, methods in rules:
        app.add_url_rule(rule, ep, fn, methods=methods)
    api = SimpleNamespace(models=m, keys=K, core=core, state=state, send_scores=send_scores, sync_roster=sync_roster,
                          jwks_cache=jwks_cache, token_cache=token_cache, catalog=catalog, scores_for=scores_for,
                          section_setting=section_setting)
    app.extensions['ciwt_lti'] = api
    return api
