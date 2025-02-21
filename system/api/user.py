from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from system.models import User
from system.schemas.user import UserCreate, UserResponse, UserUpdate
from system.database import get_db
from system.utils import PasswordEngine
from fastapi import Response
from .utils import get_user_from_cookie, set_user_in_cookie, reset_user_from_cookie

router = APIRouter()


@router.post(
    '/register',
    summary='Зарегистрировать пользователя',
    response_model=UserResponse,
    responses={409: {'description': 'Пользователь уже существует'}},
)
async def register_user(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    # Проверка, существует ли пользователь
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail='Пользователь уже существует')
    # Хеширование пароля
    hashed_password = PasswordEngine.hash_password(user.password)
    # Создание нового пользователя
    new_user = User(email=user.email, password=hashed_password, is_active=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    await set_user_in_cookie(response, user.email)
    return new_user


@router.post(
    '/login',
    summary='Авторизоваться в системе',
    responses={401: {}, 404: {'description': 'Пользователь не существует'}},
    response_class=Response,
)
async def login_user(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    await reset_user_from_cookie(response)
    if not existing_user:
        raise HTTPException(status_code=404)
    if not PasswordEngine.verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401)
    await set_user_in_cookie(response, user.email)
    response.status_code = 200
    return response


@router.post('/logout', summary='Выйти из системы', response_class=Response)
async def logout(response: Response):
    await reset_user_from_cookie(response)
    response.status_code = 200
    return response


@router.get(
    '/info',
    summary='Получить информацию о текущем пользователе',
    response_model=UserResponse,
    responses={401: {}, 404: {'description': 'Пользователь не существует'}},
)
async def get_user_info(user_mail: str = Depends(get_user_from_cookie), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404)
    return user


@router.get('/list', summary='Получить список зарегистрированных пользователей', response_model=list[UserResponse])
async def get_user_list(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.put(
    '/update',
    summary='Обновить информацию о текущем пользователе',
    response_model=UserResponse,
    responses={401: {}, 404: {'description': 'Пользователь не существует'}},
)
async def update_user(
    response: Response,
    user_update: UserUpdate,
    user_mail: str = Depends(get_user_from_cookie),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404)

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    await set_user_in_cookie(response, user.email)
    return user


@router.delete(
    '/delete',
    summary='Удалить текущего пользователя',
    response_class=Response,
    responses={401: {}, 404: {'description': 'Пользователь не существует'}},
)
async def delete_user(user_mail: str = Depends(get_user_from_cookie), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        return Response(status_code=404)
    db.delete(user)
    db.commit()
    response = Response(status_code=200)
    await reset_user_from_cookie(response)
    return response
