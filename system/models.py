from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass

# User data (email, password from account, activity)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    subscriptions = relationship('Subscription', back_populates='user')
    payment_methods = relationship('PaymentMethod', back_populates='user')
    payments = relationship('Payment', back_populates='user')

# Subscription data (type of subscription, price, activity, subscription period,
# auto payment, date of start and end)
class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, nullable=False)  # Тип подписки, например, "Premium", "Basic"
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    duration = Column(Integer, default=30)
    auto_renew = Column(Boolean, default=False)
    open_date = Column(String)
    end_date = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    payment_method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=True, default=None)
    user = relationship('User', back_populates='subscriptions')
    payments = relationship('Payment', back_populates='subscription')
    payment_method = relationship('PaymentMethod', back_populates='subscriptions')

# Payment data (price, date of payment, status)
class PaymentMethod(Base):
    __tablename__ = 'payment_methods'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # Тип способа оплаты (например, "карта", "PayPal")
    card_number = Column(String, unique=True)
    expiry_date = Column(String)
    cvv = Column(Integer)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='payment_methods')
    payments = relationship('Payment', back_populates='payment_method')
    subscriptions = relationship('Subscription', back_populates='payment_method')

# Method of payment (type, card number, expiration date, CVV, activity)
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    open_date = Column(String)
    payment_method_id = Column(Integer, ForeignKey('payment_methods.id'))
    user = relationship('User', back_populates='payments')
    subscription = relationship('Subscription', back_populates='payments')
    payment_method = relationship('PaymentMethod', back_populates='payments')
