from typing import Union

from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse

from secrets import token_hex

from bcrypt import gensalt, hashpw

from jose import JWTError

from app.src.databases.requests import orm_find_account, orm_create_account, orm_update_profile_image
from app.src.utils.utils_funcs import home_response, custom_response
from app.src.utils.utils import templates, Mode, SessionDB, SessionDataV, decode_token, generate_token, login_payload, SessionCookie
from app.src.schemas.forms import FileSchema, LoginAccountSchema, CreateAccountSchema, MailCodeSchema
from app.src.mails.mail import custom_email
from app.src.mails.mail_schemas import authorization_code
from app.src.sessions.funcs import generate_code_session, delete_all_data, generate_code_session_login
from app.src.sessions.sessions import cookie


router = APIRouter(
    prefix='/account'
)


@router.get('/signup', response_class=HTMLResponse)
async def signup_hand_get(
        request: Request,
        mode: Mode
):

    template_response = {
        'request': request,
        'mode': mode,
        'title': 'Sign up'
    }
    return templates.TemplateResponse('signup.html', template_response)


@router.post('/signup', response_class=RedirectResponse)
async def signup_hand_post(
        mode: Mode,
        bg: BackgroundTasks,
        username: str = Form(...),
        password: str = Form(...),
        email: str = Form(...)
):

    data = {
        'username': username,
        'password': password,
        'email': email
    }

    try:
        user = CreateAccountSchema(**data)
        u = await user.model_async_validate()

        creds = {
            'username': username,
            'password': password,
            'email': email
        }

        response = custom_response(
            url=f'/account/verify/email',
            key='success',
            value='Code was sent on your email',
            mode=mode
        )

        response, code = await generate_code_session(
            response=response,
            **creds
        )

        mail_creds = {
            'email': email,
            'code': code,
            'action': 'signup'
        }

        bg.add_task(custom_email,
                    recipients=[email],
                    subject='Authorization',
                    body=authorization_code(**mail_creds)
                    )
        response.set_cookie(key='action', value='signup', max_age=300)
        return response

    except ValueError as e:
        return custom_response(url=f'/account/signup', mode=mode, key='error', value=str(e))


@router.get('/verify/email', dependencies=[Depends(cookie)])
async def signup_email_hand_get(
        request: Request,
        mode: Mode
):

    template_data = {
        'request': request,
        'mode': mode
    }

    response = templates.TemplateResponse('email.html', template_data)
    return response


@router.post('/signup/email', dependencies=[Depends(cookie)])
async def signup_email_hand(
        mode: Mode,
        session: SessionDB,
        session_id: SessionCookie,
        session_data: SessionDataV,
        code: str = Form(...)
):

    try:
        data = {
            'code': code,
            'sent_code': session_data.code
        }
        varify_code = MailCodeSchema(**data)
        await varify_code.model_async_validate()

        password = session_data.password
        username = session_data.username
        email = session_data.email
        await orm_create_account(
            user_name=username,
            password=hashpw(password.encode(), gensalt()),
            session=session,
            email=email)

        response = home_response(mode=mode, key='success', value='You signed up successfully')
        response = await delete_all_data(
            response=response,
            session_id=session_id
        )
        return response

    except ValueError as e:
        return custom_response(url='/account/verify/email', key='error', value=str(e), mode=mode)


@router.get('/login', response_class=Union[HTMLResponse, RedirectResponse])
async def login_hand_get(
        request: Request,
        mode: Mode
):

    if token := request.cookies.get('token'):
        try:
            decode_token(token)
            return home_response(key="error", value="You are already logged in", mode=mode)
        except JWTError:
            return custom_response(url='/account/login', key='error', value='Your token has expired', mode=mode)

    template_data = {
        'request': request,
        'mode': mode,
        'title': 'Login page'
    }
    return templates.TemplateResponse("login.html", template_data)


@router.post('/login/email', dependencies=[Depends(cookie)])
async def verify_email_login_hand(
        request: Request,
        mode: Mode,
        session_id: SessionCookie,
        session_data: SessionDataV,
        code: str = Form(...)
):

    data = {
        'code': code,
        'sent_code': session_data.code
    }
    try:
        varify_code = MailCodeSchema(**data)
        await varify_code.model_async_validate()

        payload, max_age = login_payload(
            u=session_data.u,
            username=session_data.username,
            remember=session_data.remember
        )
        token = generate_token(payload)

        response = home_response(key='success', value="You logged in successfully", mode=mode)
        response.set_cookie(key='token', value=token, max_age=max_age)

        response = await delete_all_data(
            response=response,
            session_id=session_id
        )
        return response

    except ValueError as e:
        return custom_response(url='/account/verify/email', key='error', value=str(e), mode=mode)


@router.post('/login', response_class=HTMLResponse)
async def login_hand_post(
        request: Request,
        mode: Mode,
        bg: BackgroundTasks,
        session: SessionDB,
        username: str = Form(...),
        password: str = Form(...),
        remember: str = Form(None)
):

    data = {
        'username': username,
        'password': password,
    }

    if token := request.cookies.get('token'):
        try:
            decode_token(token)
        except JWTError:
            return home_response(key='error', value='You are already logged in', mode=mode)
        return home_response(key='error', value='You are already logged in', mode=mode)

    try:
        user = LoginAccountSchema(**data)
        await user.model_async_validate()
        u = await orm_find_account(user_name=username, session=session)

        response = custom_response(
            url=f'/account/verify/email',
            key='success',
            value='Code was sent on your email',
            mode=mode
        )

        response, code = await generate_code_session_login(
            response=response,
            u=u,
            username=username,
            remember=remember
        )

        mail_creds = {
            'email': u.email,
            'code': code,
            'action': 'login'
        }
        bg.add_task(custom_email,
                    recipients=[u.email],
                    subject='Authentication',
                    body=authorization_code(**mail_creds)
                    )
        response.set_cookie(key='action', value='login', max_age=300)
        return response

    except Exception as e:
        return custom_response(url=f'/account/login', key='error', value=str(e), mode=mode)


@router.get('/logout', response_class=HTMLResponse)
async def logout_hand(
        request: Request,
        mode: Mode,
):

    if request.cookies.get('token'):
        response = home_response(mode=mode, key='success', value='You logged out successfully')
        response.delete_cookie(key='token')
        return response
    else:
        response = home_response(mode=mode, key='error', value='You are not logged in')
        return response


@router.get(path='/profile', response_class=HTMLResponse)
async def profile_hand(
        request: Request,
        mode: Mode,
        session: SessionDB
):

    if token := request.cookies.get('token'):
        try:
            decoded_token = decode_token(token)
            user = await orm_find_account(user_name=decoded_token.get('username'), session=session)

            img_path = user.image_path
            template_data = {
                    'request': request,
                    'title': 'My profile',
                    'image': img_path,
                    'username': decoded_token.get('username'),
                    'mode': mode
                }
            response = templates.TemplateResponse('profile.html', template_data)
            return response
        except JWTError:
            return home_response(key='error', value="You are not logged in", mode=mode)
    else:

        return home_response(key='error', value="You are not logged in", mode=mode)


@router.get('/profile/update_image', response_class=HTMLResponse)
async def update_image_hand_get(
        request: Request,
        mode: Mode
):
    if token := request.cookies.get('token'):
        try:
            decoded_token = decode_token(token)
            template_data = {
                    'request': request,
                    'title': 'Update profile image',
                    'mode': mode
                }
            response = templates.TemplateResponse('up_image.html', template_data)
            return response
        except JWTError:
            return home_response(mode=mode, key='error', value='You are not logged in')
    else:
        return home_response(mode=mode, key='error', value='You are not logged in')


@router.post('/profile/update_image', response_class=RedirectResponse)
async def update_image_hand_post(
        request: Request,
        mode: Mode,
        session: SessionDB,
        file: UploadFile = File(default=None)
):

    if token := request.cookies.get('token'):
        try:
            decoded_token = decode_token(token)
            file_form = FileSchema(file=file)
            random_hash = token_hex(16)
            file_name = random_hash + '.' + file.filename.split('.')[1]

            with open(f'app/src/static/user_images/{file_name}', 'wb') as f:
                f.write(file.file.read())

            await orm_update_profile_image(
                username=decoded_token.get('username'),
                image_path=file_name,
                session=session
            )
            return custom_response(url='/account/profile', mode=mode, key='success', value="You updated image successfully")

        except ValueError as e:
            return custom_response(url='/account/profile/update_image', mode=mode, key='error', value=str(e))
        except JWTError:
            return home_response(mode=mode, key='error', value='You are not logged in')
    else:
        return custom_response(url='/account/login', mode=mode, key='error', value="You are not logged in")
