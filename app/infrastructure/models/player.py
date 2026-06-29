"""Model de Jogador"""

from sqlalchemy import Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import cast
from app.core.database import Base

class Player(Base):
    """Model de Jogador"""

    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    shirt_number: Mapped[int] = mapped_column(nullable=False)
    team: Mapped[str] = mapped_column(nullable=False)
    position: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    monthly_fee_paid: Mapped[bool] = mapped_column(default=False)

    total_goals: Mapped[int] = mapped_column(default=0)
    total_assists: Mapped[int] = mapped_column(default=0)
    total_games: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    game_players = relationship("GamePlayer", back_populates="player")

    @property
    def total_scouts(self) -> int:
        """Total de scouts (gols + assistências)"""
        return (self.total_goals or 0) + (self.total_assists or 0)

    def __repr__(self) -> str:
        return f"<Player {self.name} - #{self.shirt_number}>"