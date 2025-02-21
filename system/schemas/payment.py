from pydantic import BaseModel
from system.enums import PaymentStatus


class PaymentCreate(BaseModel):
    amount: float
    subscription_id: int
    payment_method_id: int


class PaymentResponse(PaymentCreate):
    open_date: str
    id: int
    status: PaymentStatus

    class Config:
        from_attributes = True


class PaymentStatusUpdate(BaseModel):
    payment_id: int
    status: PaymentStatus
