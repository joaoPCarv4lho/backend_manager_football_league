"""Repository para operações com User"""

from typing import Optional

from sqlalchemy.orm import Session

from app.infrastructure.models.user import User, PlanEnum


class UserRepository:
    """Repository Pattern para User"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Busca um usuário pelo ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário pelo e-mail"""
        return self.db.query(User).filter(User.email == email).first()

    def create(self, name: str, email: str, hashed_password: str, plan: PlanEnum = PlanEnum.basic) -> User:
        """Cria um novo usuário"""
        user = User(name=name, email=email, hashed_password=hashed_password, plan=plan)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_plan(self, user_id: int, plan: PlanEnum) -> Optional[User]:
        """Atualiza o plano de assinatura de um usuário"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.plan = plan
        self.db.commit()
        self.db.refresh(user)
        return user
