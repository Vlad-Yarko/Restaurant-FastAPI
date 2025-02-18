from uuid import UUID, uuid4

import os

from fastapi import HTTPException

from fastapi_sessions.frontends.implementations import CookieParameters, SessionCookie
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier

from dotenv import load_dotenv, find_dotenv

from app.src.schemas.base_schemas import SessionData


load_dotenv(find_dotenv())


cookie_parameters = CookieParameters(
    max_age=200
)


cookie = SessionCookie(
    identifier='general_identifier',
    cookie_name='session',
    cookie_params=cookie_parameters,
    secret_key=os.getenv('SECRET_TOKEN')
)


backend = InMemoryBackend[UUID, SessionData]()


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier='general_identifier',
    backend=backend,
    auto_error=True,
    auth_http_exception=HTTPException(status_code=403, detail='No session')
)
