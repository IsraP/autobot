from datetime import date, time, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


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


class OptionalFeature(BaseModel):
    code: int = Field(alias="Codigo")
    description: str = Field(alias="Descricao")


class CarInfoApi(BaseModel):
    id: int = Field(alias="Codigo")
    created_at: str = Field(alias="DataCadastro")
    updated_at: str = Field(alias="DataModificacao")
    vehicle_type: str = Field(alias="TipoVeiculo")
    manufacture_year: int = Field(alias="AnoFabricacao")
    model_year: int = Field(alias="AnoModelo")
    transmission: str = Field(alias="Cambio")
    fuel: str = Field(alias="Combustivel")
    color: str = Field(alias="Cor")
    mileage: float = Field(alias="Km")
    brand_id: int = Field(alias="CodigoMarca")
    brand: str = Field(alias="Marca")
    model_id: int = Field(alias="CodigoModelo")
    featured: bool = Field(alias="Destaque")
    model: str = Field(alias="Modelo")
    version: str = Field(alias="Versao")
    plate: str = Field(alias="Placa")
    doors: int = Field(alias="Portas")
    price: float = Field(alias="Preco")
    classified_price: float = Field(alias="PrecoClassificados")
    renavam: str = Field(alias="Renavam")
    chassis: str = Field(alias="Chassi")
    zero_km: bool = Field(alias="ZeroKm")
    video_url: Optional[str] = Field(None, alias="UrlVideo")
    notes: Optional[str] = Field(None, alias="Observacao")
    features: List[OptionalFeature] = Field(alias="Opcionais")
    category: str = Field(alias="Categoria")

    class Config:
        allow_population_by_field_name = True