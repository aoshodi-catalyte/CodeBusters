"""
Security event logging utilities.
"""

import logging


logger = logging.getLogger("security")


def log_security_event(
    event: str,
    message: str,
    level: int = logging.WARNING,
) -> None:
    """
    Write a security-related event to the application logs.

    Do not pass passwords, JWTs, reset codes, or other secrets
    in the message.
    """

    logger.log(
        level,
        "SECURITY_EVENT=%s | %s",
        event,
        message,
    )
