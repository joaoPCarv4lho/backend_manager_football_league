"""Models de jogos (Game) e Jogadores por jogo (GamePlayer)"""

from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from datetime import datetime, timezone
from app.core.database import Base
import enum

class TeamEnum(str, enum.Enum):
    """Enum para times"""
    Branco = "Branco"
    Vermelho = "Vermelho"


class Game(Base):
    """Model de jogo"""

    __tablename__ = "tb_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    team_white_score: Mapped[int] = mapped_column(Integer, default=0)
    team_red_score: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    game_players = relationship("GamePlayer", back_populates="game", cascade="all, delete-orphan")

    @property
    def winner(self) -> str:
        """Retorna o time vencedor"""
        white_score = self.team_white_score or 0
        red_score = self.team_red_score or 0
        if white_score > red_score:
            return "Branco"
        elif red_score > white_score:
            return "Vermelho"
        else:
            return "Empate"

    @property
    def total_goals(self) -> int:
        """Total de gols no jogo"""
        return (self.team_white_score or 0) + (self.team_red_score or 0)

    def __repr__(self) -> str:
        if isinstance(self.date, (int, float)):
            date_str = datetime.fromtimestamp(self.date, timezone.utc).strftime('%Y-%m-%d')
        elif isinstance(self.date, datetime):
            date_str = self.date.strftime('%Y-%m-%d')
        else:
            date_str = "No Date"
        return f"<Game {self.id} - {date_str} - {self.team_white_score} x {self.team_red_score}>"

class GamePlayer(Base):
    """Model de Jogador por jogo"""

    __tablename__ = "tb_game_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("tb_games.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    team: Mapped[Enum] = mapped_column(Enum(TeamEnum), nullable=False)
    goals: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)

    game = relationship("Game", back_populates="game_players")
    player = relationship("Player", back_populates="game_players")

    @property
    def total_scouts(self) -> int:
        """Total de scouts (gols + assistências)"""
        return (self.goals or 0) + (self.assists or 0)
    
    def __repr__(self) -> str:
        return f"<GamePlayer {self.player_id} - Game {self.game_id} - Team {self.team} - Goals {self.goals} - Assists {self.assists}>"
