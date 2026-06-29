"""Configurações da Aplicação"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    """Configurações gerais da aplicação"""

    SECRET_KEY: str = Field(..., description="Chave secreta para geração de tokens JWT")
    ALGORITHM: str = Field(default="HS256", description="Algoritmo JWT padrão")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, description="Tempo de expiração do token de acesso em minutos (padrão: 1 dia)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Tempo de expiração do refresh token em dias (padrão: 7 dias)")
    DATABASE_URL: str
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]


    APP_NAME: str = "Football League Management"
    DEBUG: bool = False

    # Stripe (cobrança de assinaturas). Vazio = cobrança desabilitada.
    STRIPE_SECRET_KEY: str = Field(default="", description="Chave secreta da API Stripe (sk_...)")
    STRIPE_WEBHOOK_SECRET: str = Field(default="", description="Segredo de verificação do webhook Stripe (whsec_...)")
    STRIPE_PRICE_PRO: str = Field(default="", description="ID do Price recorrente do plano Pro (price_...)")
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="URL base do frontend para redirecionos de checkout")


    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()