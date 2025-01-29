from typing import Annotated

import datetime

from pathlib import Path

from uuid import UUID


from fastapi import Depends, Query
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError


from app.src.databases.engine import main_session
from app.src.sessions.sessions import cookie, verifier, SessionData
from app.src.databases.models import User


BASE_DIR = Path(__file__).parent.parent.parent.parent

PUBLIC_KEY = (BASE_DIR / 'public_key.pem').read_text()

PRIVATE_KEY = (BASE_DIR / 'private_key.pem').read_text()


async def connect_db():
    async with main_session() as session:
        yield session


SessionDB = Annotated[AsyncSession, Depends(connect_db)]


def find_mode(mode: str | None = Query(default=None)):
    return mode


Mode = Annotated[str | None, Depends(find_mode)]


def find_sort(sort: str | None = Query(default=None)):
    return sort


Sort = Annotated[str | None, Depends(find_sort)]

templates = Jinja2Templates(directory='app/src/templates')

SessionCookie = Annotated[UUID, Depends(cookie)]

SessionDataV = Annotated[SessionData, Depends(verifier)]


def decode_token(
        token: str | None
):
    decoded_token = jwt.decode(token=token, key=PUBLIC_KEY, algorithms=['RS256'])
    return decoded_token


def generate_token(
        payload: dict
):
    token = jwt.encode(
        claims=payload,
        key=PRIVATE_KEY,
        algorithm='RS256'
    )
    return token


def login_payload(
        u: User,
        remember,
        username: str
):
    exp = datetime.timedelta(hours=24)
    max_age = 86400
    now = datetime.datetime.utcnow()
    if remember:
        exp = datetime.timedelta(hours=120)
        max_age *= 5

    payload = {
        'sub': str(u.id),
        'username': username,
        'exp': int((now + exp).timestamp()),
        'isa': int((now).timestamp())
    }
    return payload, max_age
