"""Routes/Endpoints de autenticação"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.application.service.auth_service import AuthService
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.models.user import User
from app.domain.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.presentation.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency Injection do AuthService"""
    return AuthService(UserRepository(db))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Registrar novo coordenador")
def register(data: UserCreate, service: AuthService = Depends(get_auth_service)):
    """Registra um novo usuário/coordenador (plano Básico por padrão)."""
    return service.register(data)


@router.post("/login", response_model=Token, summary="Login (gera token JWT)")
def login(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends(get_auth_service)):
    """
    Autentica o usuário e retorna um token de acesso.

    Use o campo **username** para o e-mail e **password** para a senha
    (formato OAuth2, compatível com o botão *Authorize* do Swagger).
    """
    return service.login(UserLogin(email=form_data.username, password=form_data.password))


@router.get("/me", response_model=UserResponse, summary="Dados do usuário autenticado")
def me(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado."""
    return current_user
