"""
Utility helpers for parsing SQLAlchemy database errors.

This module provides functions that extract structured diagnostic
information from low‑level SQLAlchemy exceptions so repositories
can convert them into domain‑level errors cleanly.
"""

from sqlalchemy.exc import IntegrityError


def parse_integrity_error(exc: IntegrityError):
    """
    Extract constraint and message details from an IntegrityError.

    Parameters:
    exc : IntegrityError
        The SQLAlchemy IntegrityError raised during a failed database
        operation, typically due to a UNIQUE or FOREIGN KEY constraint.

    Returns a tuple containing:
        - The constraint name, if available (PostgreSQL provides this)
        - A lowercase string representation of the underlying DB error
    """

    constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    error_message = str(exc.orig).lower()
    return constraint, error_message
