from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from system.database import get_db
from system.models import Subscription, User
from system.schemas.notification import NotificationResponse
from .utils import get_user_from_cookie

router = APIRouter()


@router.get(
    '/',
    summary='Получить уведомления о подписках',
    response_model=list[NotificationResponse],
    responses={401: {}, 404: {'description': 'Пользователь не найден'}},
)
async def get_notifications(
    db: Session = Depends(get_db),
    user_mail: str = Depends(get_user_from_cookie),
):
    user = db.query(User).filter(User.email == user_mail).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    subscriptions = (
        db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.is_active.is_(True)).all()
    )

    notifications = []
    for subscription in subscriptions:
        days_left = max((datetime.fromisoformat(subscription.end_date) - datetime.now()).days, 0)
        if subscription.auto_renew:
            message = (
                f'Для подписки {subscription.name} будет выполнен автоплатёж в размере {subscription.price} '
                f'руб. через {days_left} дней'
            )
        else:
            message = f'Подписка {subscription.name} истекает через {days_left} дней'
        notifications.append(NotificationResponse(subscription_id=subscription.id, message=message))
    return notifications
