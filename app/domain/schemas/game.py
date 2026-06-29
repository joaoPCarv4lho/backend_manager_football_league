"""Schemas pydantic para Game e GamePlayer"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class TeamEnum(str, Enum):
    """Enum para times"""
    Branco = "Branco"
    Vermelho = "Vermelho"

class GamePlayerBase(BaseModel):
    """Schema base de GamePlayer"""
    player_id: int = Field(..., description="ID do jogador", gt=0)
    game_id: Optional[int] = Field(None, description="ID do jogo")
    team: TeamEnum
    goals: int = Field(default=0, description="Número de gols do jogador", ge=0)
    assists: int = Field(default=0, description="Número de assistências do jogador", ge=0)

class GamePlayerCreate(GamePlayerBase):
    """Schema para criação de GamePlayer"""
    pass

class GamePlayerResponse(GamePlayerBase):
    """Schema para resposta de GamePlayer"""
    id: int
    game_id: int
    player_name: Optional[str] = None
    shirt_number: Optional[int] = None

    class Config:
        from_attributes = True


class GameBase(BaseModel):
    """Schema base de Game"""
    id: Optional[int] = Field(None, description="ID do jogo")
    date: datetime = Field(default_factory=datetime.utcnow, description="Data do jogo")
    location: Optional[str] = Field(None, description="Local do jogo")
    notes: Optional[str] = Field(None, description="Notas adicionais sobre o jogo")

class GameCreate(GameBase):
    """Schema para criação de Game"""
    team_white_score: int = Field(default=0, description="Pontuação do time branco", ge=0)
    team_red_score: int = Field(default=0, description="Pontuação do time vermelho", ge=0)
    game_players: List[GamePlayerCreate] = Field(default_factory=list, description="Lista de jogadores no jogo")

class GameUpdate(GameBase):
    """Schema para atualização de uma Partida"""
    date: Optional[datetime] = None
    team_white_score: Optional[int] = Field(None, description="Placar do time branco")
    team_red_score: Optional[int] = Field(None, description="Placar do time vermelho")
    location: Optional[str] = Field(None, description="Local do Jogo")
    notes: Optional[str] = Field(None, description="Notas adicionais sobre o jogo")

class GameUpdateScore(GameBase):
    """Schema para atualização apenas do placar de uma partida"""
    team_white_score: int = Field(..., description="Placar do time branco", ge=0)
    team_red_score: int = Field(..., description="Placar do time vermelho", ge=0)

class GameResponse(GameBase):
    """Schema para resposta de Game"""
    id: int
    team_white_score: int
    team_red_score: int
    winner: str
    total_goals: int

    class Config:
        from_attributes = True

class GameDetailResponse(GameResponse):
    """Schema para resposta detalhada de Game"""
    game_players: List[GamePlayerResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
    

class GameStatsResponse(BaseModel):
    """Schema para resposta de estatísticas de jogos"""
    id: int
    date: datetime
    team_white_score: int
    team_red_score: int
    winner: str
    total_goals: int
    team_white_players: List[GamePlayerResponse] = Field(default_factory=list)
    team_red_players: List[GamePlayerResponse] = Field(default_factory=list)
    top_scorers: Optional[GamePlayerResponse] = None
    top_assists: Optional[GamePlayerResponse] = None

    class Config:
        from_attributes = True
