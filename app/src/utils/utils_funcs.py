from fastapi.responses import RedirectResponse


def home_response(mode: str | None,
                  key: str,
                  value: str) -> RedirectResponse:
    response = RedirectResponse(
        url=f"/?mode={mode}",
        status_code=302
    )
    response.set_cookie(key=key, value=value, max_age=1)
    return response


def custom_response(url: str,
                    mode: str | None,
                    key: str,
                    value: str) -> RedirectResponse:
    response = RedirectResponse(
        url=f"{url}?mode={mode}",
        status_code=302
    )
    response.set_cookie(key=key, value=value, max_age=1)
    return response
