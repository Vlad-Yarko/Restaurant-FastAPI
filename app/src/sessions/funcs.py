from app.src.sessions.sessions import SessionData, backend, cookie

from fastapi import Response

from uuid import uuid4, UUID

from random import randint

from app.src.databases.models import User


async def generate_code_session(
        response: Response,
        username: str,
        password: str,
        email: str
) -> tuple[Response, str]:
    code = str(randint(100000, 999999))

    session_data_d = {
        'username': username,
        'password': password,
        'email': email,
        'code': code
    }
    session_data = SessionData(**session_data_d)
    session_data_id = uuid4()
    await backend.create(session_data_id, session_data)
    cookie.attach_to_response(response, session_data_id)
    return response, code


async def delete_all_data(
        response: Response,
        session_id: int
) -> Response:
    await backend.delete(session_id)
    cookie.delete_from_response(response=response)
    return response


async def generate_code_session_login(
        response: Response,
        u: User,
        remember,
        username: str
):
    code = str(randint(100000, 999999))
    session_data_d = {
        'code': code,
        'u': u,
        'remember': remember,
        'username': username
    }
    session_data = SessionData(**session_data_d)
    session_data_id = uuid4()
    await backend.create(session_data_id, session_data)
    cookie.attach_to_response(response, session_data_id)
    return response, code
