import pytest

from auth.google_oauth import is_allowed_email, AuthError


def test_allowed_domain_passes():
    assert is_allowed_email("paul@duomo.co.kr", allowed_domain="duomo.co.kr") is True


def test_disallowed_domain_blocked():
    assert is_allowed_email("attacker@gmail.com", allowed_domain="duomo.co.kr") is False


def test_no_at_sign_raises():
    with pytest.raises(AuthError):
        is_allowed_email("not-an-email", allowed_domain="duomo.co.kr")


def test_case_insensitive_domain():
    assert is_allowed_email("paul@DUOMO.CO.KR", allowed_domain="duomo.co.kr") is True
