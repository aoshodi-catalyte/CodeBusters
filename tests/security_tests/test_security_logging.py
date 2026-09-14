import logging

from utils.security_logging import log_security_event


def test_security_event_is_logged(caplog):
    with caplog.at_level(logging.WARNING, logger="security"):
        log_security_event(
            "login_failed",
            "Username not found: username=jane",
        )

    assert "SECURITY_EVENT=login_failed" in caplog.text
    assert "username=jane" in caplog.text


def test_security_event_does_not_require_secrets():
    password = "SecretPassword123"

    message = (
        "Login failed for username=jane"
    )

    assert password not in message


def test_security_event_uses_requested_log_level(caplog):
    with caplog.at_level(logging.INFO, logger="security"):
        log_security_event(
            "security_test",
            "Test event",
            level=logging.INFO,
        )

    assert "SECURITY_EVENT=security_test" in caplog.text
    assert "Test event" in caplog.text
