"""Schemas Pydantic para Player"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PlayerBase(BaseModel):
    """Schema base para Player"""
    name: str = Field(..., title="Nome do jogador", min_length=10, max_length=100)
    shirt_number: int = Field(..., title="Número da camisa", ge=1, le=99)
    team: str = Field(..., title="Cor da camisa do time do Jogador")
    position: str = Field(..., title="Posição do jogador", min_length=2)
    is_active: bool = Field(default=True, title="Indica se o jogador está ativo")


class PlayerCreate(PlayerBase):
    """Schema para criação de Player"""
    pass

class PlayerUpdate(BaseModel):
    """Schema para atualização de Player"""
    name: Optional[str] = Field(None, title="Nome do jogador", min_length=10, max_length=100)
    shirt_number: Optional[int] = Field(None, title="Número da camisa", ge=1, le=99)
    position: Optional[str] = Field(None, title="Posição do jogador", min_length=2)

class PlayerScoutUpdate(BaseModel):
    """Schema para atualização de scout do Player"""
    goals: Optional[int] = Field(0, title="Número de gols", ge=0)
    assists: Optional[int] = Field(0, title="Número de assistências", ge=0)
    matches_played: Optional[int] = Field(0, title="Número de partidas jogadas", ge=0)

class PlayerResponse(PlayerBase):
    """Schema de resposta para Player"""
    id: int = Field(..., title="ID do jogador")
    created_at: datetime = Field(..., title="Data de criação")
    updated_at: datetime = Field(..., title="Data de atualização")
    goals: int = Field(0, title="Número de gols")
    assists: int = Field(0, title="Número de assistências")
    matches_played: int = Field(0, title="Número de partidas jogadas")

    @property
    def total_scouts(self) -> int:
        """Calcula o total de scouts (gols + assistências)"""
        return self.goals + self.assists

    class Config:
        from_attributes = True

class PlayerStatsResponse(BaseModel):
    """Schema de resposta para estatísticas do Player"""
    id: int = Field(..., title="ID do jogador")
    name: str = Field(..., title="Nome do jogador")
    shirt_number: int = Field(..., title="Número da camisa")
    team: str = Field(..., title="Cor da camisa do time do Jogador")
    position: str = Field(..., title="Posição do jogador")
    goals: int = Field(0, title="Número de gols")
    assists: int = Field(0, title="Número de assistências")
    matches_played: int = Field(0, title="Número de partidas jogadas")

    class Config:
        from_attributes = True