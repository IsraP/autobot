import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = 'Bearer'

class LoggedUser(BaseModel):
    username: str
    token: Token

class Car(BaseModel):
    name: str
    model: str
    year: Optional[str]
    plate: Optional[str]
    price: Optional[float]

    class Config:
        exclude_none = True

class Lead(BaseModel):
    id: str
    client: str
    last_client_message: str
    car: Optional[Car] = None
    is_birthday: Optional[bool] = None
    received_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        exclude_none = True


class InteractionOrigin(str, Enum):
    CLIENT = "CLIENT"
    STORE = "STORE"


class Interaction(BaseModel):
    origin: InteractionOrigin
    sent_at: datetime.time
    content: str

    class Config:
        json_encoders = {
            Enum: lambda v: v.value,
            datetime.time: lambda v: v.strftime("%H:%M"),
        }