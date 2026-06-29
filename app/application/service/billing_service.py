"""Service de cobrança de assinaturas via Stripe"""

from typing import Optional

import stripe
from fastapi import HTTPException, status

from app.config import settings
from app.infrastructure.models.user import User, PlanEnum
from app.infrastructure.repositories.user_repository import UserRepository

# Status de assinatura Stripe que concedem acesso ao plano Pro
_ACTIVE_STATUSES = {"active", "trialing", "past_due"}


class BillingService:
    """Encapsula a integração com o Stripe (checkout, portal e webhooks)"""

    def __init__(self, repository: UserRepository):
        self.repository = repository
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY

    # ----------------- Checkout / Portal -----------------
    def _ensure_configured(self):
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PRICE_PRO:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cobrança não configurada (defina STRIPE_SECRET_KEY e STRIPE_PRICE_PRO).",
            )

    def _ensure_customer(self, user: User) -> str:
        """Garante que o usuário tem um cliente Stripe, criando se necessário"""
        if user.stripe_customer_id:
            return user.stripe_customer_id
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={"user_id": str(user.id)},
        )
        self.repository.set_stripe_customer_id(user.id, customer.id)
        return customer.id

    def create_checkout_session(self, user: User) -> str:
        """Cria uma sessão de checkout de assinatura do plano Pro e retorna a URL"""
        self._ensure_configured()
        customer_id = self._ensure_customer(user)
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{"price": settings.STRIPE_PRICE_PRO, "quantity": 1}],
            success_url=f"{settings.FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/billing/cancel",
            metadata={"user_id": str(user.id)},
        )
        return session.url

    def create_portal_session(self, user: User) -> str:
        """Cria uma sessão do portal de cobrança (gerenciar/cancelar assinatura)"""
        self._ensure_configured()
        if not user.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário ainda não possui assinatura.",
            )
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/billing",
        )
        return session.url

    # ----------------- Webhooks -----------------
    def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Verifica a assinatura do webhook e processa o evento"""
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Webhook de cobrança não configurado.",
            )
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.SignatureVerificationError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assinatura de webhook inválida.")

        self.process_event(event["type"], event["data"]["object"])
        return {"received": True}

    def process_event(self, event_type: str, obj: dict) -> None:
        """Despacha um evento Stripe para sincronizar o plano do usuário.

        Separado da verificação de assinatura para permitir teste direto da lógica.
        """
        if event_type == "checkout.session.completed":
            self._sync_from_checkout(obj)
        elif event_type in (
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ):
            self._sync_from_subscription(obj)

    def _sync_from_checkout(self, session: dict) -> None:
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        user = self._resolve_user(session, customer_id)
        if not user:
            return
        if customer_id and not user.stripe_customer_id:
            self.repository.set_stripe_customer_id(user.id, customer_id)
        # Concede o Pro; o estado detalhado é confirmado pelos eventos de subscription
        self.repository.set_subscription(user.id, subscription_id, PlanEnum.pro)

    def _sync_from_subscription(self, subscription: dict) -> None:
        customer_id = subscription.get("customer")
        user = self.repository.get_by_stripe_customer_id(customer_id) if customer_id else None
        if not user:
            return
        is_pro = subscription.get("status") in _ACTIVE_STATUSES
        self.repository.set_subscription(
            user.id,
            subscription.get("id") if is_pro else None,
            PlanEnum.pro if is_pro else PlanEnum.basic,
        )

    def _resolve_user(self, obj: dict, customer_id: Optional[str]) -> Optional[User]:
        """Resolve o usuário pelo metadata.user_id e, em fallback, pelo customer_id"""
        meta = obj.get("metadata") or {}
        user_id = meta.get("user_id")
        if user_id:
            return self.repository.get_by_id(int(user_id))
        if customer_id:
            return self.repository.get_by_stripe_customer_id(customer_id)
        return None
