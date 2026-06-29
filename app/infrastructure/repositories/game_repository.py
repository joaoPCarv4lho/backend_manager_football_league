"""Repository para operações com Game e GamePlayer
caminho: app/infrastructure/repositories/game_repository.py
"""

from typing import List, Optional
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.infrastructure.models.game import Game, GamePlayer
from app.domain.schemas.game import GameCreate, GameUpdate, GamePlayerCreate

class GameRepository:
    """Repository Pattern para Game"""

    def __init__(self, db: Session):
        self.db = db

    def create_game(self, game_data: GameCreate) -> Game:
        """Cria um novo jogo com os jogadores associados"""
        game = Game(
            game_id=game_data.id,
            date=game_data.date,
            location=game_data.location,
            notes=game_data.notes
        )
        self.db.add(game)
        self.db.flush()  # Para obter o ID do jogo antes de criar os GamePlayers

        for player_data in game_data.game_players:
            game_player = GamePlayer(
                game_id=game.id,
                player_id=player_data.player_id,
                team=player_data.team,
                goals=player_data.goals,
                assists=player_data.assists
            )
            self.db.add(game_player)
        self.db.commit()
        self.db.refresh(game)
        return game
    
    def get_by_id(self, game_id: int, with_players: bool = False) -> Optional[Game]:
        """Obtém um jogo por ID"""
        query = self.db.query(Game)

        if with_players:
            query = query.options(joinedload(Game.game_players))
        return query.filter(Game.id == game_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Game]:
        """Lista todos os jogos, com opções de paginação e filtro por data"""
        query = self.db.query(Game)

        if start_date:
            query = query.filter(Game.date >= start_date)
        if end_date:
            query = query.filter(Game.date <= end_date)
        
        return query.order_by(desc(Game.date)).offset(skip).limit(limit).all()

    def update_game(self, game_id: int, game_data: GameUpdate) -> Optional[Game]:
        """Atualiza um jogo existente"""
        game = self.get_by_id(game_id)
        if not game:
            return None
        
        update_data = game_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(game, field, value)

        self.db.commit()
        self.db.refresh(game)
        return game

    def update_score(self, game_id: int, white_score: int, red_score: int) -> Optional[Game]:
        """Atualiza apenas o placar de um jogo"""
        game = self.get_by_id(game_id)
        if not game:
            return None
        
        game.team_white_score = white_score
        game.team_red_score = red_score

        self.db.commit()
        self.db.refresh(game)
        return game
    
    def delete(self, game_id: int) -> bool:
        """Exclui um jogo por ID"""
        game = self.get_by_id(game_id)
        if not game:
            return False
        
        self.db.delete(game)
        self.db.commit()
        return True
    
    def get_player_games(self, player_id: int) -> List[Game]:
        """Lista os jogos de um jogador"""
        return self.db.query(Game).join(GamePlayer).filter(GamePlayer.player_id == player_id).order_by(desc(Game.date)).all()

    def get_recent_games(self, limit: int = 5) -> List[Game]:
        """Retorna os jogos mais recentes"""
        return self.db.query(Game).order_by(desc(Game.date)).limit(limit).all()


class GamePlayerRepository:
    """Repository Pattern para GamePlayer"""

    def __init__(self, db: Session):
        self.db = db

    def create_game_player(self, game_player_data: GamePlayerCreate) -> GamePlayer:
        """Adiciona um jogador a um jogo"""
        game_player = GamePlayer(
            game_id=game_player_data.game_id,
            **game_player_data.model_dump()
        )
        self.db.add(game_player)
        self.db.commit()
        self.db.refresh(game_player)
        return game_player

    def get_by_id(self, game_player_id: int) -> Optional[GamePlayer]:
        """Busca um GamePlayer por ID"""
        return self.db.query(GamePlayer).filter(GamePlayer.id == game_player_id).first()

    def get_by_game_and_player(self, game_id: int, player_id: int) -> Optional[GamePlayer]:
        """Busca um GamePlayer por ID do jogo e ID do Jogador"""
        return self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id, GamePlayer.player_id == player_id).first()
    
    def update_scouts(self, game_player_id: int, goals: Optional[int] = None, assists: Optional[int] = None) -> Optional[GamePlayer]:
        """Atualiza os scouts de um GamePlayer"""
        game_player = self.get_by_id(game_player_id)
        if not game_player:
            return None
        
        game_player.goals = goals if goals is not None else game_player.goals
        game_player.assists = assists if assists is not None else game_player.assists

        self.db.commit()
        self.db.refresh(game_player)
        return game_player

    def delete(self, game_player_id: int) -> bool:
        """Remove um jogador de um jogo"""
        game_player = self.get_by_id(game_player_id)
        if not game_player:
            return False
        
        self.db.delete(game_player)
        self.db.commit()
        return True

    def get_by_game(self, game_id: int) -> List[GamePlayer]:
        """Retorna todos os jogadores de um jogo específico"""
        return self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    
    def _sum_goals_by_team(self, game_id: int, team: str) -> int:
        """Soma os gols de um time em um jogo específico"""
        return self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id, GamePlayer.team == team).with_entities(func.sum(GamePlayer.goals)).scalar() or 0