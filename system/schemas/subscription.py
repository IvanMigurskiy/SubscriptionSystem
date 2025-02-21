from typing import Optional

from pydantic import BaseModel

from system.enums import SubscriptionRate


class SubscriptionCreate(BaseModel):
    name: str
    type: SubscriptionRate
    price: float
    auto_renew: bool = False
    duration: int
    payment_method_id: Optional[int] = None


class SubscriptionResponse(SubscriptionCreate):
    id: int
    is_active: bool
    open_date: str
    end_date: str

    class Config:
        from_attributes = True
