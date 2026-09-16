import pytest

from vendmate.app import create_app
from vendmate.repository import Repository, seed


@pytest.fixture
def repo():
    r = Repository()
    seed(r)
    r.register_user("admin", "admin123")
    return r


@pytest.fixture
def app(repo):
    application = create_app(repo=repo, secret_key="test-secret")
    application.config.update(TESTING=True)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username="admin", password="admin123"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)
