from fastapi import Request

from app.src.utils.utils_funcs import custom_response


def error_403_forbidden(reqeust: Request, exception):
    query_parameters = dict(reqeust.query_params)
    return custom_response(url='/', key='error', value='Too long', mode=query_parameters.get('mode'))
