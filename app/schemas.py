"""Contratos de entrada y salida de la API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import DonorStatus, Role


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("La contraseña debe incluir una mayúscula")
        if not any(char.islower() for char in value):
            raise ValueError("La contraseña debe incluir una minúscula")
        if not any(char.isdigit() for char in value):
            raise ValueError("La contraseña debe incluir un número")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DonorCreate(BaseModel):
    organization: str | None = Field(default=None, max_length=160)
    phone: str = Field(min_length=7, max_length=25, pattern=r"^[0-9+()\- ]+$")
    city: str = Field(min_length=2, max_length=100)
    resource_type: str = Field(min_length=2, max_length=100)
    available_quantity: str = Field(min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=500)


class DonorStatusUpdate(BaseModel):
    status: DonorStatus


class DonorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    organization: str | None
    phone: str
    city: str
    resource_type: str
    available_quantity: str
    notes: str | None
    status: DonorStatus
    created_at: datetime

