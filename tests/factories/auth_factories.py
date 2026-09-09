from jose import jwt  # type: ignore

from config import settings


def manager_token():
    payload = {
        "employee_id": 1,
        "role": "manager"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
