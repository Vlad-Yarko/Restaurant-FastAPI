from time import time

from fastapi.requests import Request
from fastapi import Response

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class LogTime(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time()

        response = await call_next(request)

        response.headers['Process-time'] = str(time() - start_time)

        return response
