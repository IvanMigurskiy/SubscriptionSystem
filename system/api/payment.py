from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from system.database import get_db
from system.enums import PaymentStatus
from system.models import Payment, User, PaymentMethod, Subscription
from system.schemas.payment import PaymentCreate, PaymentResponse, PaymentStatusUpdate
from .utils import get_user_from_cookie

router = APIRouter()


@router.post(
    '/new',
    summary='Создать платёж',
    response_model=PaymentResponse,
    responses={401: {}, 404: {'description': 'Пользователь не найден / Подписка не найдена / Метод оплаты не найден'}},
)
async def create_payment(
    payment: PaymentCreate, db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)
):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    subscription = (
        db.query(Subscription).filter(Subscription.id == payment.subscription_id, Subscription.is_active).first()
    )
    if not subscription:
        raise HTTPException(status_code=404, detail='Подписка не найдена')
    payment_method = (
        db.query(PaymentMethod).filter(PaymentMethod.id == payment.payment_method_id, PaymentMethod.is_active).first()
    )
    if not payment_method:
        raise HTTPException(status_code=404, detail='Метод оплаты не найден')

    new_payment = Payment(
        amount=payment.amount,
        status=PaymentStatus.CREATED,
        user_id=user.id,
        open_date=datetime.now().isoformat(),
        subscription_id=payment.subscription_id,
        payment_method_id=payment.payment_method_id,
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


@router.get(
    '/list',
    summary='Получить список платежей пользователя',
    response_model=list[PaymentResponse],
    responses={401: {}, 404: {'description': 'Пользователь не найден'}},
)
async def get_payment_list(db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    payments = db.query(Payment).filter(Payment.user_id == user.id).all()
    return payments


@router.post(
    '/set_status',
    summary='Изменить статус платежа',
    response_model=PaymentResponse,
    responses={401: {}, 403: {'description': 'Доступ запрещён'}, 404: {'description': 'Платёж не найден'}},
)
async def set_payment_status(
    payment_status_update: PaymentStatusUpdate,
    db: Session = Depends(get_db),
    user_mail: str = Depends(get_user_from_cookie),
):
    payment = db.query(Payment).filter(Payment.id == payment_status_update.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail='Платёж не найден')

    user = db.query(User).filter(User.email == user_mail).first()
    if payment.user_id != user.id:
        raise HTTPException(status_code=403, detail='Доступ запрещён')

    payment.status = payment_status_update.status
    db.commit()
    db.refresh(payment)
    return payment
