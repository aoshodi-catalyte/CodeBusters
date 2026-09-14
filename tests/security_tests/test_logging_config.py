import logging
import os

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

def configure_logging() -> None:
    """
    Configure application-wide logging.
    """

    log_level = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    numeric_level = getattr(
        logging,
        log_level,
        logging.INFO,
    )

    logging.basicConfig(
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )

    logging.getLogger().setLevel(numeric_level)
