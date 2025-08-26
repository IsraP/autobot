from datetime import date, time, datetime
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
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.strftime("%H:%M"),
        }

class Lead(BaseModel):
    id: str
    client: str
    last_client_message: str
    car: Optional[Car] = None
    is_birthday: Optional[bool] = None
    received_at: datetime
    updated_at: datetime

    class Config:
        exclude_none = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.strftime("%H:%M"),
        }


class InteractionOrigin(str, Enum):
    CLIENT = "CLIENT"
    STORE = "STORE"


class Interaction(BaseModel):
    origin: InteractionOrigin
    sent_at: time
    content: str

    class Config:
        json_encoders = {
            Enum: lambda v: v.value,
            time: lambda v: v.strftime("%H:%M"),
        }


class Answer(BaseModel):
    intent: str
    content: str