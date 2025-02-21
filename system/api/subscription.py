from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from system.models import Subscription, User, PaymentMethod
from system.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from system.database import get_db
from .utils import get_user_from_cookie

router = APIRouter()


@router.post(
    '/new',
    summary='Оформить подписку',
    response_model=SubscriptionResponse,
    responses={
        401: {},
        404: {'description': 'Пользователь не найден / Метод оплаты не найден'},
        409: {'description': 'Пользователь не активен'},
    },
)
async def create_subscription(
    subscription: SubscriptionCreate, user_mail: str = Depends(get_user_from_cookie), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    if not user.is_active:
        raise HTTPException(status_code=409, detail='Пользователь не активен')
    if subscription.auto_renew and subscription.payment_method_id is None:
        raise HTTPException(status_code=404, detail='Метод оплаты не найден')
    if subscription.payment_method_id is not None:
        payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == subscription.payment_method_id).first()
        if not payment_method:
            raise HTTPException(status_code=404, detail='Метод оплаты не найден')
    open_date = datetime.now()
    new_subscription = Subscription(
        type=subscription.type,
        user_id=user.id,
        name=subscription.name,
        price=subscription.price,
        auto_renew=subscription.auto_renew,
        duration=subscription.duration,
        open_date=open_date.isoformat(),
        end_date=(open_date + timedelta(days=subscription.duration)).isoformat(),
        payment_method_id=subscription.payment_method_id,
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription


@router.get(
    '/info/{subscription_id}',
    summary='Получить информацию о подписке',
    response_model=SubscriptionResponse,
    responses={401: {}, 403: {'description': 'Доступ запрещён'}, 404: {'description': 'Подписка не найдена'}},
)
async def get_subscription_info(
    subscription_id: int, db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail='Подписка не найдена')
    user = db.query(User).filter(User.email == user_mail).first()
    if subscription.user_id != user.id:
        raise HTTPException(status_code=403, detail='Доступ запрещён')
    return subscription


@router.get(
    '/list',
    summary='Получить список подписок пользователя',
    response_model=list[SubscriptionResponse],
    responses={401: {}, 404: {'description': 'Пользователь не найден'}},
)
async def get_subscription_list(db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    subscriptions = db.query(Subscription).filter(Subscription.user_id == user.id).all()
    return subscriptions


@router.put(
    '/update/{subscription_id}',
    summary='Обновить подписку',
    response_model=SubscriptionResponse,
    responses={
        401: {},
        403: {'description': 'Доступ запрещён'},
        404: {'description': 'Подписка не найдена / Метод оплаты не найден'},
        409: {'description': 'Подписка отменена'},
    },
)
async def update_subscription(
    subscription_id: int,
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db),
    user_mail: str = Depends(get_user_from_cookie),
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail='Подписка не найдена')
    user = db.query(User).filter(User.email == user_mail).first()
    if subscription.user_id != user.id:
        raise HTTPException(status_code=403, detail='Доступ запрещён')
    if not subscription.is_active:
        raise HTTPException(status_code=409, detail='Подписка отменена')
    if subscription.auto_renew and subscription.payment_method_id is None:
        raise HTTPException(status_code=404, detail='Метод оплаты не найден')
    schema_data = subscription_data.model_dump(exclude_unset=True)
    if 'payment_method_id' in schema_data and subscription.payment_method_id is not None:
        payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == subscription.payment_method_id).first()
        if not payment_method:
            raise HTTPException(status_code=404, detail='Метод оплаты не найден')

    for key, value in schema_data.items():
        setattr(subscription, key, value)

    db.commit()
    return subscription


@router.delete(
    '/cancel/{subscription_id}',
    summary='Отменить подписку',
    response_class=Response,
    responses={
        401: {},
        403: {'description': 'Доступ запрещён'},
        404: {'description': 'Подписка не найдена'},
        409: {'description': 'Подписка уже отменена'},
    },
)
async def cancel_subscription(
    subscription_id: int, db: Session = Depends(get_db), user_mail: str = Depends(get_user_from_cookie)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail='Подписка не найдена')
    user = db.query(User).filter(User.email == user_mail).first()
    if subscription.user_id != user.id:
        raise HTTPException(status_code=403, detail='Доступ запрещён')
    if not subscription.is_active:
        raise HTTPException(status_code=409, detail='Подписка уже отменена')

    subscription.is_active = False
    db.commit()
    return Response(status_code=200)
