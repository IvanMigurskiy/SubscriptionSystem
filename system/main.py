import logging
from fastapi import FastAPI
import uvicorn

from database import engine
from models import Base
from api import *


# Initializing FastAPI instance
app = FastAPI(title='Subscription system', description='Subscription system', version='1.0', docs_url='/api/docs')

# Initializing routers
app.include_router(user_router, prefix='/user', tags=['Пользователи'])
app.include_router(subscription_router, prefix='/subscription', tags=['Подписки'])
app.include_router(payment_router, prefix='/payment', tags=['Платежи'])
app.include_router(payment_method_router, prefix='/payment_method', tags=['Способы оплаты'])
app.include_router(notification_router, prefix='/notification', tags=['Уведомления'])

# Entry point
if __name__ == '__main__':
    # Creating engine
    Base.metadata.create_all(engine)

    # Running the web server
    uvicorn.run('main:app', host='0.0.0.0', log_level=logging.DEBUG, reload=True)
