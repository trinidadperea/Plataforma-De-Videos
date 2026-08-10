from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature

from config import (
    serializer,
    COOKIE_NAME,
    MAX_AGE_SECONDS,
)


def create_session_cookie(username: str) -> str:

    return serializer.dumps({
        "username": username
    })


def get_current_user(request: Request) -> str:

    token = request.cookies.get(
        COOKIE_NAME
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="No autenticado"
        )

    try:

        data = serializer.loads(
            token,
            max_age=MAX_AGE_SECONDS
        )

    except BadSignature:

        raise HTTPException(
            status_code=401,
            detail="Sesión inválida"
        )

    return data["username"]


def get_optional_user(request: Request):

    token = request.cookies.get(
        COOKIE_NAME
    )

    if not token:
        return None

    try:

        data = serializer.loads(
            token,
            max_age=MAX_AGE_SECONDS
        )

        return data["username"]

    except BadSignature:

        return None


def require_user_or_login(request: Request):

    token = request.cookies.get(
        COOKIE_NAME
    )

    if not token:

        return RedirectResponse(
            "/login",
            status_code=302
        )

    try:

        data = serializer.loads(
            token,
            max_age=MAX_AGE_SECONDS
        )

        return data["username"]

    except BadSignature:

        return RedirectResponse(
            "/login",
            status_code=302
        )