"""Dependências compartilhadas da camada de apresentação (autenticação)"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.infrastructure.models.user import User, PlanEnum
from app.infrastructure.repositories.user_repository import UserRepository

# Hierarquia de planos: quanto maior o valor, mais recursos
_PLAN_LEVEL = {PlanEnum.basic: 0, PlanEnum.pro: 1}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Resolve o usuário autenticado a partir do token JWT do header Authorization"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = UserRepository(db).get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_plan(minimum: PlanEnum):
    """Cria uma dependência que exige no mínimo o plano `minimum` do usuário autenticado"""

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if _PLAN_LEVEL[current_user.plan] < _PLAN_LEVEL[minimum]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Recurso disponível apenas no plano '{minimum.value}'. Faça upgrade do seu plano.",
            )
        return current_user

    return checker

