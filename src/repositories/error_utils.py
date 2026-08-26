def parse_integrity_error(exc: IntegrityError):
    constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    error_message = str(exc.orig).lower()
    return constraint, error_message
