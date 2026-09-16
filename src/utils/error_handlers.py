from fastapi import HTTPException, status

def handle_repo_exception(db, exc, not_found_errors=(), conflict_errors=()):
    db.rollback()

    if isinstance(exc, not_found_errors):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

    if isinstance(exc, conflict_errors):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc)
    ) from exc
