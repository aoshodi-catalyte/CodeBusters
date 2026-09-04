from jose import JWTError, ExpiredSignatureError, jwt
from config import settings
from exceptions.secure_login_exceptions import (
    TokenDecodeError,
    TokenExpiredError,
    TokenInvalidSignatureError,
    TokenMissingClaimError,
)

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except JWTError as exc:
        msg = str(exc).lower()
        if "signature" in msg or "invalid signature" in msg:
            raise TokenInvalidSignatureError() from exc
        raise TokenDecodeError(msg) from exc

    return payload


def extract_jti(payload: dict) -> str:
    jti = payload.get("jti")
    if jti is None:
        raise TokenMissingClaimError("jti")
    return jti
