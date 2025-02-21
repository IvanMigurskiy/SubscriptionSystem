from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from system.database import get_db
from system.models import PaymentMethod, User
from system.schemas.payment_method import PaymentMethodCreate, PaymentMethodResponse, ActivePaymentMethodResponse
from .utils import get_user_from_cookie

router = APIRouter()


@router.post(
    '/new',
    summary='Добавить способ оплаты',
    response_model=ActivePaymentMethodResponse,
    responses={
        401: {},
        403: {'description': 'Доступ запрещён'},
        404: {'description': 'Пользователь не найден'},
        409: {'description': 'Способ оплаты с таким номером карты уже существует'},
    },
)
async def create_payment_method(
    payment_method: PaymentMethodCreate, db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)
):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    new_payment_method = PaymentMethod(
        type=payment_method.type,
        user_id=user.id,
        card_number=payment_method.card_number,
        expiry_date=payment_method.expiry_date,
        cvv=payment_method.cvv,
    )
    db.add(new_payment_method)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail='Способ оплаты с таким номером карты уже существует')
    return new_payment_method


@router.get(
    '/info/{payment_method_id}',
    summary='Получить информацию о способе оплаты',
    response_model=PaymentMethodResponse,
    responses={401: {}, 403: {'description': 'Доступ запрещён'}, 404: {'description': 'Способ оплаты не найден'}},
)
async def get_payment_method(
    payment_method_id: int, db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)
):
    payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == payment_method_id).first()
    if not payment_method:
        raise HTTPException(status_code=404, detail='Способ оплаты не найден')
    user = db.query(User).filter(User.email == user_mail).first()
    if payment_method.user_id != user.id:
        raise HTTPException(status_code=403, detail='Доступ запрещён')
    return payment_method


@router.get(
    '/list',
    summary='Получить список способов оплаты',
    response_model=list[ActivePaymentMethodResponse],
    responses={401: {}, 404: {'description': 'Пользователь не найден'}},
)
async def get_payment_methods_list(db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    payment_methods = db.query(PaymentMethod).filter(PaymentMethod.user_id == user.id, PaymentMethod.is_active).all()
    return payment_methods


@router.put(
    '/update/{payment_method_id}',
    summary='Обновить способ оплаты',
    response_model=ActivePaymentMethodResponse,
    responses={401: {}, 403: {'description': 'Доступ запрещён'}, 404: {'description': 'Способ оплаты не найден'}},
)
async def update_payment_method(
    payment_method_id: int,
    payment_method_request: PaymentMethodCreate,
    db: Session = Depends(get_db),
    user_mail: str = Depends(get_user_from_cookie),
):
    payment_method = (
        db.query(PaymentMethod).filter(PaymentMethod.id == payment_method_id, PaymentMethod.is_active).first()
    )
    if not payment_method:
        raise HTTPException(status_code=404, detail='Способ оплаты не найден')

    user = db.query(User).filter(User.email == user_mail).first()
    if payment_method.user_id != user.id:
        raise HTTPException(status_code=403, detail='Доступ запрещён')

    for key, value in payment_method_request.dict(exclude_unset=True).items():
        setattr(payment_method, key, value)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail='Способ оплаты с таким номером карты уже существует')
    return payment_method


@router.delete(
    '/delete/{payment_method_id}',
    summary='Удалить способ оплаты',
    response_class=Response,
    responses={401: {}, 403: {'description': 'Доступ запрещён'}, 404: {'description': 'Способ оплаты не найден'}},
)
async def delete_payment_method(
    payment_method_id: int, db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)
):
    payment_method = (
        db.query(PaymentMethod).filter(PaymentMethod.id == payment_method_id, PaymentMethod.is_active).first()
    )
    if not payment_method:
        raise HTTPException(status_code=404, detail='Способ оплаты не найден')

    user = db.query(User).filter(User.email == user_mail).first()
    if payment_method.user_id != user.id:
        raise HTTPException(status_code=403, detail='Доступ запрещён')

    payment_method.is_active = False
    db.commit()
    return Response(status_code=200)
