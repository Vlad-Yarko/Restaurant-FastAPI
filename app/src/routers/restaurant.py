from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.src.databases.requests import orm_pizza_menu, orm_beverages_menu
from app.src.utils.utils import Mode, Sort, templates, SessionDB


router = APIRouter(prefix='/restaurant')


@router.get('/menu/pizza', response_class=HTMLResponse)
async def pizza_menu(request: Request,
                     mode: Mode,
                     sort: Sort,
                     session: SessionDB):

    piz_menu = await orm_pizza_menu(session)
    if sort:
        piz_menu = sorted(piz_menu, key=lambda x: x.price)

    template_data = {
        'request': request,
        'title': 'pizza',
        'sort': sort,
        'bg': 'warning',
        'menu': piz_menu,
        'mode': mode
    }
    return templates.TemplateResponse('universal_menu.html', template_data)


@router.get('/menu/beverages', response_class=HTMLResponse)
async def beverages_menu(request: Request,
                         mode: Mode,
                         sort: Sort,
                         session: SessionDB):

    bev_menu = await orm_beverages_menu(session)
    if sort:
        bev_menu = sorted(bev_menu, key=lambda x: x.price)

    template_data = {
        'request': request,
        'title': 'beverages',
        'sort': sort,
        'bg': 'info',
        'menu': bev_menu,
        'mode': mode
    }
    return templates.TemplateResponse('universal_menu.html', template_data)


@router.get('/menu', response_class=HTMLResponse)
async def all_menu(reqeust: Request,
                   mode: Mode,
                   sort: Sort,
                   session: SessionDB):

    bev_menu = await orm_beverages_menu(session)
    piz_menu = await orm_pizza_menu(session)
    if sort:
        piz_menu = sorted(piz_menu, key=lambda x: x.price)
        bev_menu = sorted(bev_menu, key=lambda x: x.price)

    template_data = {
        'request': reqeust,
        'title': 'menu',
        'sort': sort,
        'piz_menu': piz_menu,
        'bev_menu': bev_menu,
        'mode': mode
    }
    return templates.TemplateResponse('all_menu.html', template_data)
