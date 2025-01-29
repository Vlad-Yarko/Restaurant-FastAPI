from typing import Any

from pydantic import BaseModel


class SessionData(BaseModel):

    username: str | None = None
    password: str | None = None
    email: str | None = None
    code: str | None = None
    u: Any = None
    remember: Any = None
