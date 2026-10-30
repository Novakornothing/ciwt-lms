"""Skip What You Know, Help Desk Queue, and Daily Review.

Registered from app.py. Tables are additive. Nothing here calls an external model API.
"""


def register(app, db, deps):
    from .routes import register as _register
    return _register(app, db, deps)
