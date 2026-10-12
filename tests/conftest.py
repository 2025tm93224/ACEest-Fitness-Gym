"""Shared fixtures for ACEest Flask tests."""
import pytest

from app import create_app, db


class TestConfig:
    TESTING = True
    SECRET_KEY = "pytest-only-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.drop_all()
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def sample_client(app):
    from app.models import Client
    from app.programs import PROGRAMS

    program = "Fat Loss (FL) – 3 day"
    item = Client(
        name="Test Client",
        age=30,
        height=170.0,
        weight=70.0,
        program=program,
        calories=round(70 * PROGRAMS[program]["factor"]),
        target_weight=65.0,
        target_adherence=80,
    )
    db.session.add(item)
    db.session.commit()
    return item
