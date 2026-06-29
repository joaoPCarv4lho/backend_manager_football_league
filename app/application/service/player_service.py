"""Service para lógica de Player"""

from typing import List, Optional
from app.infrastructure.repositories.player_repository import PlayerRepository
from app.domain.schemas.player import (
    PlayerCreate, PlayerUpdate, PlayerResponse, PlayerStatsResponse, PlayerScoutUpdate
)
from fastapi import HTTPException, status


class ServicePlayer:
    """Service para Player"""

    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    def create_player(self, player_data: PlayerCreate) -> PlayerResponse:
        """Cria um novo Jogador"""
        #verifica se o jogador já existe
        player_name = player_data.name
        existing_player = self.repository.get_by_name(player_name)

        if existing_player:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Jogador já está cadastrado")
        player = self.repository.create(player_data)

        return PlayerResponse.model_validate(player)
    
    def get_player(self, player_id: int) -> PlayerResponse:
        """Busca um jogador pelo ID"""
        player = self.repository.get_by_id(player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogador não encontrado")

        return PlayerResponse.model_validate(player)
    
    def get_all_players(self, skip: int = 0, limit: int = 100) -> List[PlayerResponse]:
        """Lista todos os jogadores com paginação"""
        players = self.repository.get_all(skip=skip, limit=limit)

        return [PlayerResponse.model_validate(p) for p in players]
    
    def update_player(self, player_id: int, player_update: PlayerUpdate) -> PlayerResponse:
        """Atualiza os dados de um jogador"""
        player = self.repository.update(player_id, player_update)
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogador não encontrado")

        return PlayerResponse.model_validate(player)
    
    def update_player_scout(self, player_id: int, scout_update: PlayerScoutUpdate) -> PlayerStatsResponse:
        """Atualiza os scouts (gosls, assistências, partidas) de um jogador"""
        player = self.repository.update_scouts(
            player_id,
            scout_update.goals if scout_update.goals is not None else 0,
            scout_update.assists if scout_update.assists is not None else 0
        )
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogador não encontrado")

        return PlayerStatsResponse.model_validate(player)
    
    def delete_player(self, player_id: int) -> dict:
        """Remove um jogador pelo ID"""
        success = self.repository.delete(player_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogador não encontrado")
        return {"message": "Jogador desativado com sucesso"}

    def get_player_stats(self, player_id: int) -> PlayerStatsResponse:
        """Busca as estatísticas de um jogador pelo ID"""

        player = self.repository.get_by_id(player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogador não encontrado")

        return PlayerStatsResponse(
            id=player.id, # type: ignore
            name=player.name, # type: ignore
            shirt_number=player.shirt_number, # type: ignore
            position=player.position, # type: ignore
            team=player.team, # type: ignore
            goals=player.total_goals or 0, # type: ignore
            assists=player.total_assists or 0, # type: ignore
            matches_played=player.total_games or 0 # type: ignore
        )

    def get_top_scorers(self, limit: int = 10) -> List[PlayerStatsResponse]:
        """Busca os maiores artilheiros"""
        players = self.repository.get_top_scorrers(limit=limit)
        return [PlayerStatsResponse.model_validate(p) for p in players]
    
    def get_top_assisters(self, limit: int = 10) -> List[PlayerStatsResponse]:
        """Busca os líderes em assistências"""
        players = self.repository.get_top_assisters(limit=limit)
        return [PlayerStatsResponse.model_validate(p) for p in players]

    def _player_to_stats(self, player) -> PlayerStatsResponse:
        """Converte um Player para PlayerStatsResponse"""

        goals_per_game = player.total_goals / player.total_games if player.total_games > 0 else 0
        assists_per_game = player.total_assists / player.total_games if player.total_games > 0 else 0

        return PlayerStatsResponse(
            id=player.id, # type: ignore
            name=player.name, # type: ignore
            shirt_number=player.shirt_number, # type: ignore
            position=player.position, # type: ignore
            team=player.team, # type: ignore
            goals=player.total_goals or 0, # type: ignore
            assists=player.total_assists or 0, # type: ignore
            matches_played=player.total_games or 0, # type: ignore
            goals_per_game=goals_per_game, # type: ignore
            assists_per_game=assists_per_game # type: ignore
        )