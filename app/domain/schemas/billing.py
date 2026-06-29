"""Schemas Pydantic para cobrança (Stripe)"""

from pydantic import BaseModel


class CheckoutSessionResponse(BaseModel):
    """URL para redirecionar o usuário (checkout ou portal de cobrança)"""
    url: str
