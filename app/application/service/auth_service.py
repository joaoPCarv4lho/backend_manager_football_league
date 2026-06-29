"""Service de autenticação: registro e login"""

from fastapi import HTTPException, status

from app.infrastructure.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.domain.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    """Service com a lógica de autenticação"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, data: UserCreate) -> UserResponse:
        """Registra um novo usuário/coordenador"""
        if self.repository.get_by_email(data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

        user = self.repository.create(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return UserResponse.model_validate(user)

    def authenticate(self, email: str, password: str) -> User:
        """Valida credenciais e retorna o usuário"""
        user = self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
        return user

    def login(self, data: UserLogin) -> Token:
        """Autentica e gera o token de acesso"""
        user = self.authenticate(data.email, data.password)
        return Token(access_token=create_access_token(user.id))
