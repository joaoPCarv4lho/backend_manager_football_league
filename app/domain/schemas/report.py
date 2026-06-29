"""Schemas Pydantic para relatórios (recurso Pro)"""

from typing import List, Optional

from pydantic import BaseModel


class ScoutReportItem(BaseModel):
    """Linha do relatório de scouts de um jogador"""
    player_id: int
    name: str
    position: str
    goals: int
    assists: int
    total_scouts: int
    games: int


class ScoutReport(BaseModel):
    """Relatório consolidado de scouts de todos os jogadores"""
    total_players: int
    items: List[ScoutReportItem]


class PlayerAward(BaseModel):
    """Vencedor de uma categoria de premiação"""
    player_id: int
    name: str
    value: int  # valor da métrica (gols, assistências ou soma)


class AwardsReport(BaseModel):
    """Premiação anual baseada nos scouts acumulados"""
    top_scorer: Optional[PlayerAward] = None          # artilheiro
    top_assister: Optional[PlayerAward] = None         # líder de assistências
    player_of_the_season: Optional[PlayerAward] = None  # craque (gols + assistências)
