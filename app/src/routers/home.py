from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from jose import JWTError

from app.src.utils.utils import Mode, templates, decode_token


router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def home_hand(request: Request, mode: Mode):

    if mode is None:
        mode = "light"

    response_data = {
        'request': request,
        'mode': mode,
        'title': 'Home page'
    }

    response = templates.TemplateResponse('index.html', response_data)

    if token := request.cookies.get('token'):
        try:
            username = decode_token(token=token).get('username')
        except JWTError:
            username = ""
    else:
        username = ""

    response.set_cookie(key='username', value=username)

    return response
