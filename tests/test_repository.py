import pytest

from vendmate.repository import Repository, seed


@pytest.fixture
def repo():
    r = Repository()
    seed(r)
    return r


def test_register_user_rejects_empty_username(repo):
    with pytest.raises(ValueError):
        repo.register_user("   ", "secretpw")


def test_register_user_rejects_short_password(repo):
    with pytest.raises(ValueError):
        repo.register_user("frank", "abc")


def test_register_user_rejects_duplicate_username(repo):
    repo.register_user("grace", "secretpw")
    with pytest.raises(ValueError):
        repo.register_user("grace", "another-pw")


def test_authenticate_returns_none_for_unknown_user(repo):
    assert repo.authenticate("nobody", "whatever") is None


def test_authenticate_returns_user_for_correct_credentials(repo):
    repo.register_user("heidi", "secretpw")
    user = repo.authenticate("heidi", "secretpw")
    assert user is not None
    assert user.username == "heidi"


def test_get_machine_raises_for_unknown_id(repo):
    with pytest.raises(KeyError):
        repo.get_machine("NOPE")


def test_revenue_report_is_empty_with_no_purchases(repo):
    assert repo.revenue_report() == {}
