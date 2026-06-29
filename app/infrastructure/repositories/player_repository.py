"""Repository para operações com Player"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.infrastructure.models.player import Player
from app.domain.schemas.player import PlayerCreate, PlayerUpdate

class PlayerRepository:
    """Repository Pattern para Player"""
    
    def __init__(self, db: Session):
        self.db = db

    def create(self, player_create: PlayerCreate) -> Player:
        """Cria um novo Player"""
        db_player = Player(**player_create.dict())
        self.db.add(db_player)
        self.db.commit()
        self.db.refresh(db_player)
        return db_player

    def update(self, player_id: int, player_update: PlayerUpdate) -> Optional[Player]:
        """Atualiza um Player existente"""
        db_player = self.get_by_id(player_id)
        if db_player:
            for key, value in player_update.dict(exclude_unset=True).items():
                setattr(db_player, key, value)
            self.db.commit()
            self.db.refresh(db_player)
        return db_player

    def delete(self, player_id: int) -> Optional[Player]:
        """Deleta um Player pelo ID"""
        db_player = self.get_by_id(player_id)
        if db_player:
            self.db.delete(db_player)
            self.db.commit()
        return db_player

########### Getters adicionais para funcionalidades específicas ###########

    def get_all(self, active_only: bool = False, skip: int = 0, limit: int = 100) -> List[Player]:
        """Recupera todos os Players com paginação"""
        query = self.db.query(Player)
        if active_only:
            query = query.filter(Player.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, player_id: int) -> Optional[Player]:
        """Busca um jogador pelo ID"""
        return self.db.query(Player).filter(Player.id == player_id).first()
    
    def get_by_name(self, name: str) -> Optional[Player]:
        """Busca um jogador pelo nome"""
        return self.db.query(Player).filter(Player.name == name).first()

    def get_color_by_team(self, team: str) -> List[Player]:
        """Busca jogadores pela cor da camisa do time"""
        return self.db.query(Player).filter(Player.team == team).all()
    
    def get_top_scorrers(self, limit: int = 10) -> List[Player]:
        """Recupera os jogadores com mais gols"""
        return self.db.query(Player).order_by(Player.total_goals.desc()).limit(limit).all()
    
    def get_top_assisters(self, limit: int = 10) -> List[Player]:
        """Recupera os jogadores com mais assistências"""
        return self.db.query(Player).order_by(Player.total_assists.desc()).limit(limit).all()

    def reset_monthly_payments(self) -> int:
        """Reseta os pagamentos mensais de todos os jogadores e retorna o número de jogadores atualizados"""
        result = self.db.query(Player).update({"monthly_fee_paid": False})
        self.db.commit()
        return result

    def adjust_stats(self, player_id: int, goals_delta: int, assists_delta: int, games_delta: int) -> Optional[Player]:
        """Aplica deltas aos totais acumulados do jogador (gols, assistências, jogos) e persiste"""

        player = self.get_by_id(player_id)
        if not player:
            return None

        player.total_goals = (player.total_goals or 0) + goals_delta
        player.total_assists = (player.total_assists or 0) + assists_delta
        player.total_games = (player.total_games or 0) + games_delta

        self.db.commit()
        self.db.refresh(player)
        return player

    def update_scouts(self, player_id: int, goals: int, assis: int) -> Optional[Player]:
        """Atualiza o número de scouts de um jogador"""

        player = self.get_by_id(player_id)
        if not player:
            return None
        
        player.total_goals = player.total_goals + goals 
        player.total_assists = player.total_assists + assis

        self.db.commit()
        self.db.refresh(player)
        return player
