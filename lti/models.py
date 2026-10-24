"""LTI tables. Created with db.create_all() like the rest of the app (new tables only; no change to
existing ones)."""
import json
from datetime import datetime, timezone
from types import SimpleNamespace

_cache = {}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def define_models(db):
    if 'm' in _cache:
        return _cache['m']

    class LtiPlatform(db.Model):
        """One LMS registration (issuer + client_id), created by an admin."""
        __tablename__ = 'lti_platform'
        __table_args__ = (db.UniqueConstraint('issuer', 'client_id', name='uq_lti_platform_iss_client'),)
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        kind = db.Column(db.String(20), default='other')          # canvas | blackboard | moodle | other
        issuer = db.Column(db.String(255), nullable=False)
        client_id = db.Column(db.String(255), nullable=False)
        auth_login_url = db.Column(db.String(500), nullable=False)   # platform OIDC authorization endpoint
        auth_token_url = db.Column(db.String(500), nullable=False)   # OAuth2 token endpoint (AGS / NRPS)
        token_audience = db.Column(db.String(500))                   # aud for client assertions if not the token URL
        jwks_url = db.Column(db.String(500), nullable=False)
        deployment_ids_json = db.Column(db.Text, default='[]')
        link_by_email = db.Column(db.Boolean, default=False)         # link to an existing account with the same email
        create_accounts = db.Column(db.Boolean, default=True)        # create a local account on first launch
        active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=utcnow)
        updated_at = db.Column(db.DateTime, default=utcnow)

        @property
        def deployment_ids(self):
            try:
                return [str(x) for x in json.loads(self.deployment_ids_json or '[]')]
            except ValueError:
                return []

        def reg(self):
            return {'issuer': self.issuer, 'client_id': self.client_id, 'deployment_ids': self.deployment_ids,
                    'auth_token_url': self.auth_token_url, 'token_audience': self.token_audience}

    class LtiLogin(db.Model):
        """OIDC login in flight: state ↔ nonce, single use, short-lived."""
        __tablename__ = 'lti_login'
        id = db.Column(db.Integer, primary_key=True)
        state = db.Column(db.String(64), unique=True, nullable=False, index=True)
        nonce = db.Column(db.String(64), nullable=False)
        platform_id = db.Column(db.Integer, db.ForeignKey('lti_platform.id'), nullable=False)
        target_link_uri = db.Column(db.String(1000))
        created_at = db.Column(db.DateTime, default=utcnow)
        used_at = db.Column(db.DateTime)

    class LtiUserLink(db.Model):
        __tablename__ = 'lti_user_link'
        __table_args__ = (db.UniqueConstraint('platform_id', 'sub', name='uq_lti_user_sub'),)
        id = db.Column(db.Integer, primary_key=True)
        platform_id = db.Column(db.Integer, db.ForeignKey('lti_platform.id'), nullable=False)
        sub = db.Column(db.String(255), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        how = db.Column(db.String(20))                  # created | email | roster | manual
        lms_email = db.Column(db.String(255))
        lms_name = db.Column(db.String(255))
        last_roles = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=utcnow)
        last_seen = db.Column(db.DateTime, default=utcnow)

    class LtiContext(db.Model):
        """An LMS course (context) and the class section it is mapped to here."""
        __tablename__ = 'lti_context'
        __table_args__ = (db.UniqueConstraint('platform_id', 'context_id', name='uq_lti_context'),)
        id = db.Column(db.Integer, primary_key=True)
        platform_id = db.Column(db.Integer, db.ForeignKey('lti_platform.id'), nullable=False)
        deployment_id = db.Column(db.String(255))
        context_id = db.Column(db.String(255), nullable=False)
        title = db.Column(db.String(255))
        label = db.Column(db.String(255))
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), index=True)
        lineitems_url = db.Column(db.String(1000))
        ags_scopes = db.Column(db.Text)
        memberships_url = db.Column(db.String(1000))
        created_at = db.Column(db.DateTime, default=utcnow)
        last_seen = db.Column(db.DateTime, default=utcnow)

    class LtiResourceLink(db.Model):
        __tablename__ = 'lti_resource_link'
        __table_args__ = (db.UniqueConstraint('platform_id', 'resource_link_id', name='uq_lti_resource_link'),)
        id = db.Column(db.Integer, primary_key=True)
        platform_id = db.Column(db.Integer, db.ForeignKey('lti_platform.id'), nullable=False)
        context_pk = db.Column(db.Integer, db.ForeignKey('lti_context.id'))
        resource_link_id = db.Column(db.String(255), nullable=False)
        title = db.Column(db.String(255))
        target = db.Column(db.String(120))              # lesson:<id> | quiz:<id> | test:<id> | lab:<id> | course
        lineitem_url = db.Column(db.String(1000))
        created_at = db.Column(db.DateTime, default=utcnow)
        last_seen = db.Column(db.DateTime, default=utcnow)

    class LtiDeepLink(db.Model):
        """A deep-linking request waiting for the instructor's selection."""
        __tablename__ = 'lti_deep_link'
        id = db.Column(db.Integer, primary_key=True)
        token = db.Column(db.String(64), unique=True, nullable=False)
        platform_id = db.Column(db.Integer, db.ForeignKey('lti_platform.id'), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        claims_json = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=utcnow)
        used_at = db.Column(db.DateTime)

    class LtiSyncLog(db.Model):
        __tablename__ = 'lti_sync_log'
        id = db.Column(db.Integer, primary_key=True)
        platform_id = db.Column(db.Integer, db.ForeignKey('lti_platform.id'))
        context_pk = db.Column(db.Integer, db.ForeignKey('lti_context.id'))
        kind = db.Column(db.String(20))                 # scores | roster
        actor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        at = db.Column(db.DateTime, default=utcnow)
        ok = db.Column(db.Integer, default=0)
        failed = db.Column(db.Integer, default=0)
        skipped = db.Column(db.Integer, default=0)
        detail = db.Column(db.Text)

    class LtiSectionSetting(db.Model):
        """Per-class LTI policy (school-ready pass). Defaults keep the original behaviour: nobody removed, manual passback."""
        __tablename__ = 'lti_section_setting'
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), primary_key=True)
        remove_dropped = db.Column(db.Boolean, default=False)   # NRPS: un-enroll linked students the LMS no longer lists
        auto_passback = db.Column(db.Boolean, default=False)    # send a student's score when they finish a quiz/test/lab
        exempt_full = db.Column(db.Boolean, default=False)      # tested-out (exempt) items: send 100 instead of skipping

    _cache['m'] = SimpleNamespace(LtiSectionSetting=LtiSectionSetting, LtiPlatform=LtiPlatform, LtiLogin=LtiLogin, LtiUserLink=LtiUserLink,
                                  LtiContext=LtiContext, LtiResourceLink=LtiResourceLink, LtiDeepLink=LtiDeepLink,
                                  LtiSyncLog=LtiSyncLog)
    return _cache['m']
