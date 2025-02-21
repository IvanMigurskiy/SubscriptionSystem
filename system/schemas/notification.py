from pydantic import BaseModel


class NotificationResponse(BaseModel):
    subscription_id: int
    message: str
