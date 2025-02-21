from fastapi import HTTPException
from fastapi import Request, Response

from system.utils import TokenEngine


async def get_user_from_cookie(request: Request):
    if not (cookie_result := TokenEngine.verify_token(request.cookies.get('subscr_system')))[0]:
        raise HTTPException(status_code=401)
    yield cookie_result[1]


async def set_user_in_cookie(response: Response, user: str):
    access_token = TokenEngine.create_access_token(user)
    response.set_cookie('subscr_system', access_token, httponly=True)


async def reset_user_from_cookie(response: Response):
    response.delete_cookie('subscr_system')
