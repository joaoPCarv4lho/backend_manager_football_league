"""Routes/Endpoints de cobrança (Stripe)"""

from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.application.service.billing_service import BillingService
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.models.user import User
from app.presentation.api.deps import get_current_user
from app.domain.schemas.billing import CheckoutSessionResponse

router = APIRouter(prefix="/billing", tags=["Billing"])


def get_billing_service(db: Session = Depends(get_db)) -> BillingService:
    """Dependency Injection do BillingService"""
    return BillingService(UserRepository(db))


@router.post("/checkout", response_model=CheckoutSessionResponse, summary="Iniciar assinatura do plano Pro")
def create_checkout(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
):
    """Cria uma sessão de checkout do Stripe e retorna a URL para concluir o pagamento."""
    return CheckoutSessionResponse(url=service.create_checkout_session(current_user))


@router.post("/portal", response_model=CheckoutSessionResponse, summary="Gerenciar assinatura")
def create_portal(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
):
    """Cria uma sessão do portal de cobrança do Stripe (atualizar/cancelar assinatura)."""
    return CheckoutSessionResponse(url=service.create_portal_session(current_user))


@router.post("/webhook", summary="Webhook do Stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    service: BillingService = Depends(get_billing_service),
):
    """Recebe eventos do Stripe (verificados por assinatura) e sincroniza o plano do usuário."""
    payload = await request.body()
    return service.handle_webhook(payload, stripe_signature)
