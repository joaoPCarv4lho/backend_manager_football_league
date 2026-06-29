"""Model de Usuário (coordenador da liga)"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PlanEnum(str, enum.Enum):
    """Planos de assinatura disponíveis"""
    basic = "basic"
    pro = "pro"


class User(Base):
    """Model de Usuário/Coordenador"""

    __tablename__ = "tb_users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    plan: Mapped[PlanEnum] = mapped_column(Enum(PlanEnum), default=PlanEnum.basic, nullable=False)

    # Cobrança (Stripe)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User {self.email} - {self.plan}>"
