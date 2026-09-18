"""
Application logging configuration.
"""

import logging
import os


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
