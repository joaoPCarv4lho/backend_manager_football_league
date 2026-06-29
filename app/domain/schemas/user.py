"""Schemas Pydantic para Usuário e autenticação"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PlanEnum(str, Enum):
    """Planos de assinatura disponíveis"""
    basic = "basic"
    pro = "pro"


class UserCreate(BaseModel):
    """Schema para registro de usuário"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do coordenador")
    email: str = Field(..., min_length=5, max_length=255, description="E-mail de login")
    password: str = Field(..., min_length=6, max_length=128, description="Senha")


class UserLogin(BaseModel):
    """Schema para login"""
    email: str
    password: str


class UserResponse(BaseModel):
    """Schema de resposta de usuário (sem dados sensíveis)"""
    id: int
    name: str
    email: str
    is_active: bool
    plan: PlanEnum
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema do token de acesso"""
    access_token: str
    token_type: str = "bearer"
