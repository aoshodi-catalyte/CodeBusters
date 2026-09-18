import logging


from utils.logging_config import configure_logging


def test_configure_logging_sets_default_level(monkeypatch):
    monkeypatch.delenv(
        "LOG_LEVEL",
        raising=False,
    )

    configure_logging()

    assert logging.getLogger().level == logging.INFO


def test_configure_logging_respects_log_level(monkeypatch):
    monkeypatch.setenv(
        "LOG_LEVEL",
        "DEBUG",
    )

    configure_logging()

    assert logging.getLogger().level == logging.DEBUG
