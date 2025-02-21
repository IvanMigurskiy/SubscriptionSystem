from enum import Enum


class PaymentStatus(str, Enum):
    CREATED = 'CREATED'
    PAID = 'PAID'
    EXPIRED = 'EXPIRED'
    CANCELED = 'CANCELED'


class SubscriptionRate(str, Enum):
    STANDARD = 'STANDARD'
    PREMIUM = 'PREMIUM'
    FAMILY = 'FAMILY'
