from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import uvicorn

from app.src.middlewares.base_m import LogTime
from app.src.exceptions import error_403_forbidden
from app.src.routers import account, restaurant, home


app = FastAPI()

app.include_router(restaurant.router)
app.include_router(account.router)
app.include_router(home.router)

app.add_middleware(LogTime)

app.add_exception_handler(403, error_403_forbidden)

app.mount('/static', StaticFiles(directory='app/src/static'), name='static')


if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)
