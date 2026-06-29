"""
Routes/Endpoints para Game
Caminho: app/presentation/api/routes/games.py
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.infrastructure.repositories.game_repository import GameRepository, GamePlayerRepository
from app.infrastructure.repositories.player_repository import PlayerRepository
from app.application.service.game_service import GameService
from app.domain.schemas.game import (
    GameCreate,
    GameUpdate,
    GameResponse,
    GameDetailResponse,
    GameStatsResponse,
    GameUpdateScore,
    GamePlayerCreate
)

router = APIRouter(prefix="/games", tags=["Games"])

def get_game_service(db: Session = Depends(get_db)) -> GameService:
    """Dependency Injection para GameService"""
    game_repo = GameRepository(db)
    game_player_repo = GamePlayerRepository(db)
    player_repo = PlayerRepository(db)
    return GameService(game_repo, player_repo, game_player_repo)


@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED, summary="Criar um novo jogo")
def create_game(game: GameCreate, service: GameService = Depends(get_game_service)):
    """
    Cria um novo jogo com os dados fornecidos
    - **date**: Data do jogo
    - **location**: Local do jogo
    - **players**: Lista de jogadores participantes (opcional)
    - **notes**: Notas adicionais sobre o jogo (opcional)

    O placar é calculado automaticamente baseado nos gols marcados pelos jogadores.
    """
    return service.create_game(game)

@router.get("/", response_model=List[GameResponse], summary="Listar todos os jogos")
def list_games(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100), start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, service: GameService = Depends(get_game_service)):
    """
    Lista todos os jogos com paginação e filtros opcionais
    - **skip**: Quantidade de registros a pular (padrão: 0)
    - **limit**: Quantidade máxima de registros a retornar (padrão: 100, máximo: 100)
    - **start_date**: Filtrar jogos a partir desta data (opcional)
    - **end_date**: Filtrar jogos até esta data (opcional)
    """
    return service.list_games(skip=skip, limit=limit, start_date=start_date, end_date=end_date)

@router.get("/{game_id}", response_model=GameDetailResponse, summary="Obter detalhes de um jogo específico")
def get_game(game_id: int, service: GameService = Depends(get_game_service)):
    """
    Busca um jogo específico pelo ID com todos os detalhes, incluindo jogadores e placar
    """
    return service.get_game(game_id)

@router.patch("/{game_id}", response_model=GameDetailResponse, summary="Atualizar um jogo existente")
def update_game(game_id: int, game: GameUpdate, service: GameService = Depends(get_game_service)):
    """
    Atualiza os dados de um jogo existente
    - **game_id**: ID do jogo a ser atualizado
    - **game**: Dados atualizados do jogo
    """
    return service.update_game(game_id, game)

@router.patch("/{game_id}/score", response_model=GameDetailResponse, summary="Atualizar o placar de um jogo")
def update_score(game_id: int, score_update: GameUpdateScore, service: GameService = Depends(get_game_service)):
    """
    Atualiza o placar de um jogo existente
    - **game_id**: ID do jogo a ser atualizado
    - **score_update**: Dados para atualização do placar (gols marcados por cada jogador)

    Útil quando você deseja atualizar o placar manualmente ao invés de calculá-lo baseado nos scouts dos jogadores
    """
    return service.update_score(game_id, score_update)

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir um jogo")
def delete_game(game_id: int, service: GameService = Depends(get_game_service)):
    """
    Exclui um jogo específico pelo ID
    - **game_id**: ID do jogo a ser excluído

    As estatísticas dos jogadores realcionados a este jogo são revertidas automaticamente para manter a consistência dos dados.
    """
    return service.delete_game(game_id)

@router.post("/{game_id}/players", response_model=GameDetailResponse, status_code=status.HTTP_201_CREATED, summary="Adicionar um jogador a um jogo")
def add_player_to_game(game_id: int, player: GamePlayerCreate, service: GameService = Depends(get_game_service)):
    """
    Adiciona um jogador a um jogo específico
    - **game_id**: ID do jogo ao qual o jogador será adicionado
    - **player**: Dados do jogador a ser adicionado ao jogo
    """
    return service.add_player_to_game(game_id, player)

@router.get("/{game_id}/stats", response_model=GameStatsResponse, summary="Obter estatísticas de um jogo")
def get_game_stats(game_id: int, service: GameService = Depends(get_game_service)):
    """
    Obtém as estatísticas de um jogo específico, incluindo gols marcados, assistências, cartões e outras métricas relevantes
    - **game_id**: ID do jogo para o qual as estatísticas serão obtidas
    """
    return service.get_game_to_stats(game_id)