"""Helix - opt-in attention signal for CIWT lesson pages.

Layout
------
models.py     SQLAlchemy models (factory) + additive schema migrations
analytics.py  pure aggregation helpers used by dashboards and tests
routes.py     Flask blueprint: consent, session lifecycle API, dashboards, CSV
seed.py       clearly-labelled demo data (is_demo=True)

Client side lives in static/js/helix/ (core math, runtime, charts) and
static/css/helix.css. Templates are in templates/helix/.

Usage from app.py::

    import helix
    hx = helix.init_app(app, db, deps)   # before db.create_all()
"""
import mimetypes

# MediaPipe assets: make sure every host serves these with types browsers accept for
# WebAssembly streaming compile and ES-module import (some minimal images lack them).
mimetypes.add_type('application/wasm', '.wasm')
mimetypes.add_type('text/javascript', '.mjs')

from types import SimpleNamespace

from .models import ENGINE, POLICY_VERSION, STUDY_VERSION, define_models, ensure_schema  # noqa: F401


def init_app(app, db, deps):
    """Register Helix models + blueprint. ``deps`` must provide: User, Lesson,
    Module, ClassSection, Enrollment, can_access_section(user, section), audit(action, detail)."""
    models = define_models(db)
    from .routes import create_blueprint
    d = SimpleNamespace(db=db, **deps)
    app.register_blueprint(create_blueprint(d, models))
    csrf = app.extensions.get('csrf')
    if csrf is not None:
        from .routes import BEACON_VIEWS
        for name in BEACON_VIEWS:
            csrf.exempt('helix.routes.' + name)

    @app.context_processor
    def _helix_ctx():
        return {'helix_policy_version': POLICY_VERSION}

    return models


def seed_demo(db, models, section, students, lessons):
    from .seed import seed_demo as _seed
    return _seed(db, models, section, students, lessons)
