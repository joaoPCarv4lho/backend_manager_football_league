"""
Service para lógica de negócio de Game
Caminho: app/application/services/game_service.py
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import func
from app.infrastructure.repositories.game_repository import GameRepository, GamePlayerRepository
from app.infrastructure.repositories.player_repository import PlayerRepository
from app.domain.schemas.game import (
    GameCreate,
    GameUpdate,
    GameResponse,
    GameDetailResponse,
    GameStatsResponse,
    GamePlayerResponse,
    GamePlayerCreate,
    GameUpdateScore
)
from fastapi import HTTPException, status

class GameService:
    """Service com lógica de negócio para Game"""

    def __init__(self, game_repo: GameRepository, player_repo: PlayerRepository, game_player_repo: GamePlayerRepository):
        self.game_repo = game_repo
        self.player_repo = player_repo
        self.game_player_repo = game_player_repo
    
    def create_game(self, game_data: GameCreate) -> GameDetailResponse:
        """Cria um novo jogo"""

        player_ids = [p.player_id for p in game_data.game_players]
        for player_id in player_ids:
            player = self.player_repo.get_by_id(player_id)
            if not player or not player.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Jogador com ID {player_id} não encontrado ou inativo")
        
        if len(player_ids) != len(set(player_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Jogadores duplicados na Lista de jogadores do jogo")
        
        game = self.game_repo.create_game(game_data=game_data)
        self._recalculate_score(game.id)
        self._update_player_stats(game.id)
        return self._game_to_detail_response(game)

    def get_game(self, game_id: int) -> GameDetailResponse:
        """Busca um jogo por ID"""
        
        game = self.game_repo.get_by_id(game_id, with_players=True)
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")
        return self._game_to_detail_response(game)

    def list_games(self, skip: int = 0, limit: int = 100, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[GameResponse]:
        """Lista todos os Jogos"""
        games = self.game_repo.get_all(skip=skip, limit=limit, start_date=start_date, end_date=end_date)
        return [self._game_to_response(g) for g in games]

    def update_game(self, game_id: int, game_data: GameUpdate) -> GameDetailResponse:
        """Atualiza um jogo"""
        
        game = self.game_repo.update_game(game_id, game_data)
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")
        return self._game_to_detail_response(game)

    def update_score(self, game_id: int, score_data: GameUpdateScore) -> GameDetailResponse:
        """Atualiza apenas o placar de um jogo"""

        game = self.game_repo.update_score(game_id, score_data.team_white_score, score_data.team_red_score)
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")
        return self._game_to_detail_response(game)

    def delete_game(self, game_id: int):
        """Exclui um jogo por ID"""

        game = self.game_repo.get_by_id(game_id, with_players=True)
        if game:
            for gp in game.game_players:
                self.player_repo.adjust_stats(gp.player_id, -gp.goals, -gp.assists, -1)
        success = self.game_repo.delete(game_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")
        return {"message": "Jogo excluído com sucesso"}

    def add_player_to_game(self, game_id: int, player_data: GamePlayerCreate) -> GameDetailResponse:
        """Adiciona um jogador a um jogo"""

        game = self.game_repo.get_by_id(game_id, with_players=True)
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")
        player = self.player_repo.get_by_id(player_data.player_id)
        if not player or not player.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Jogador não encontrado ou inativo")
        existing = self.game_player_repo.get_by_game_and_player(game_id, player_data.player_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Jogador já adicionado a este jogo")
        
        self.game_player_repo.create_game_player(player_data, game_id)
        self._recalculate_score(game_id)
        # Atualiza apenas o jogador recém-adicionado (evita recontar os demais)
        self.player_repo.adjust_stats(player_data.player_id, player_data.goals, player_data.assists, 1)
        return self.get_game(game_id)

    def get_game_to_stats(self, game_id: int) -> GameStatsResponse:
        """Retorna as estatísticas detalhadas de um jogo"""

        game = self.game_repo.get_by_id(game_id, with_players=True)
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")
        
        team_white_players = []
        team_red_players = []
        top_scorer = None
        top_assists = None
        max_goals = 0
        max_assists = 0

        for gp in game.game_players:
            player_response = self._game_player_to_response(gp)

            if gp.team.value == "Branco":
                team_white_players.append(player_response)
            else:
                team_red_players.append(player_response)
            
            if gp.goals > max_goals:
                max_goals = gp.goals
                top_scorer = player_response
            
            if gp.assists > max_assists:
                max_assists = gp.assists
                top_assists = player_response

        return GameStatsResponse(
            id=game.id,
            date=game.date,
            team_white_score=game.team_white_score,
            team_red_score=game.team_red_score,
            winner=game.winner,
            total_goals=game.total_goals,
            team_white_players=team_white_players,
            team_red_players=team_red_players,
            top_scorers=top_scorer if max_goals > 0 else None,
            top_assists=top_assists if max_assists > 0 else None
        )

    #----------------Funções auxiliares------------------#
    def _recalculate_score(self, game_id: int):
        """Recalcula o placar do jogo com base nos jogadores e seus scouts"""
        
        team_white_score = self.game_player_repo._sum_goals_by_team(game_id, "Branco")
        team_red_score = self.game_player_repo._sum_goals_by_team(game_id, "Vermelho")
        self.game_repo.update_score(game_id, team_white_score, team_red_score)

    def _update_player_stats(self, game_id: int):
        """Atualiza as estatísticas totais dos jogadores"""
        
        game_players = self.game_player_repo.get_by_game(game_id)
        for gp in game_players:
            self.player_repo.adjust_stats(gp.player_id, gp.goals, gp.assists, 1)

    def _game_to_response(self, game) -> GameResponse:
        """Converte Game para GameResponse"""
        return GameResponse(
            id=game.id,
            date=game.date,
            team_white_score=game.team_white_score,
            team_red_score=game.team_red_score,
            location=game.location,
            notes=game.notes,
            winner=game.winner,
            total_goals=game.total_goals
        )

    def _game_to_detail_response(self, game) -> GameDetailResponse:
        """Converte um objeto Game para GameDetailResponse"""
        
        game_players = [self._game_player_to_response(gp) for gp in game.game_players]
        return GameDetailResponse(
            id=game.id,
            date=game.date,
            team_white_score=game.team_white_score,
            team_red_score=game.team_red_score,
            location=game.location,
            notes=game.notes,
            winner=game.winner,
            total_goals=game.total_goals,
            game_players=game_players
        )

    def _game_player_to_response(self, game_player) -> GamePlayerResponse:
        """Converte um objeto GamePlayer para GamePlayerResponse"""
        
        player = self.player_repo.get_by_id(game_player.player_id)
        return GamePlayerResponse(
            id=game_player.id,
            game_id=game_player.game_id,
            player_id=game_player.player_id,
            team=game_player.team,
            goals=game_player.goals,
            assists=game_player.assists,
            player_name=player.name if player else None,
            shirt_number=player.shirt_number if player else None
        )