"""Shared fixtures: one seeded throwaway SQLite DB for the whole test session."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
_tmp = tempfile.mkdtemp(prefix='ciwt-test-')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmp, 'test.db')
os.environ.setdefault('SECRET_KEY', 'test')

import app as lms  # noqa: E402  (seeds the temp DB on import)


@pytest.fixture(scope='session')
def app():
    # most tests exercise behaviour, not CSRF; tests/test_csrf.py turns it back on
    lms.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return lms.app


@pytest.fixture(scope='session')
def mod():
    return lms


def _login(client, email, pw):
    r = client.post('/login', data={'email': email, 'password': pw})
    assert r.status_code in (302, 303), r.status_code
    return client


@pytest.fixture
def anon(app):
    return app.test_client()


@pytest.fixture
def student(app):
    return _login(app.test_client(), 'student1@lms.local', 'student123')


@pytest.fixture
def student2(app):
    return _login(app.test_client(), 'student2@lms.local', 'student123')


@pytest.fixture
def outsider(app):
    """student25 is enrolled in section B only, not section A (id 1)."""
    return _login(app.test_client(), 'student25@lms.local', 'student123')


@pytest.fixture
def instructor(app):
    return _login(app.test_client(), 'instructor@lms.local', 'teach123')


@pytest.fixture
def instructor2(app):
    """instructor2 teaches section C only."""
    return _login(app.test_client(), 'instructor2@lms.local', 'teach123')


@pytest.fixture
def admin(app):
    return _login(app.test_client(), 'admin@lms.local', 'admin123')


@pytest.fixture(scope='session')
def ids(app, mod):
    with app.app_context():
        sec = mod.ClassSection.query.get(1)
        lesson = (mod.Lesson.query.join(mod.Module).filter(mod.Module.course_id == sec.course_id)
                  .order_by(mod.Module.order, mod.Lesson.order).first())
        quiz = mod.Quiz.query.filter_by(module_id=lesson.module_id).first()
        test = mod.KnowledgeTest.query.filter_by(course_id=sec.course_id).order_by(mod.KnowledgeTest.order).first()
        s1 = mod.User.query.filter_by(email='student1@lms.local').first()
        return {'section': 1, 'lesson': lesson.id, 'module': lesson.module_id, 'quiz': quiz.id if quiz else None,
                'test': test.id, 'student1': s1.id}
