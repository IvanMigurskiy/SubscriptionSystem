from pydantic import BaseModel


class PaymentMethodCreate(BaseModel):
    type: str
    card_number: str
    expiry_date: str
    cvv: int


class ActivePaymentMethodResponse(PaymentMethodCreate):
    id: int

    class Config:
        from_attributes = True


class PaymentMethodResponse(ActivePaymentMethodResponse):
    is_active: bool
