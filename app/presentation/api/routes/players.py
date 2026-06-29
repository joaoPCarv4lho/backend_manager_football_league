"""Routes/Endpoints para Player"""


from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.application.service.player_service import ServicePlayer
from app.domain.schemas.player import (
    PlayerCreate, PlayerResponse, PlayerUpdate, PlayerStatsResponse, PlayerScoutUpdate
)
from app.infrastructure.repositories.player_repository import PlayerRepository

router = APIRouter(prefix="/players", tags=["Players"])
def get_player_service(db: Session = Depends(get_db)) -> ServicePlayer:
    """Dependency para obter o ServicePlayer"""

    repository = PlayerRepository(db=db)
    return ServicePlayer(repository=repository)


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED, summary="Criar um novo jogador")
def create_player(player_data: PlayerCreate, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para criar um novo jogador

    - **name**: nome/apelido do jogador 
    - **shirt_number**: número da camisa do jogador
    """
    return service.create_player(player_data)

@router.get("/", response_model=List[PlayerResponse], summary="Listar todos os jogadores")
def get_all_players(skip: int = 0, limit: int = 100, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para listar todos os jogadores com paginação
    
    - **skip**: número de registros a pular (padrão: 0)
    - **limit**: número máximo de registros a retornar (padrão: 100)
    """
    return service.get_all_players(skip=skip, limit=limit)

@router.get("/{player_id}", response_model=PlayerResponse, summary="Obter detalhes de um jogador específico")
def get_player_by_id(player_id: int, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para obter detalhes de um jogador específico

    - **player_id**: ID do jogador a ser retornado
    """
    return service.get_player(player_id)

@router.patch("/{player_id}", response_model=PlayerResponse, summary="Atualizar os dados de um jogador")
def update_player(player_id: int, player_update: PlayerUpdate, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para atualizar os dados de um jogador
    
    - **player_id**: ID do jogador a ser atualizado
    """
    return service.update_player(player_id, player_update)

@router.patch("/{player_id}/scout", response_model=PlayerStatsResponse, summary="Atualizar os scouts (gols, assistências, partidas) de um jogador")
def update_player_scout(player_id: int, scout_update: PlayerScoutUpdate, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para atualizar os scouts (gols, assistências, partidas) de um jogador
    
    - **goals**: número de gols a ser adicionado ao total do jogador
    - **assists**"número de assistências a ser adicionado ao total do jogador
    - **matches_played**: número de partidas jogadas a ser adicionado ao total do jogador
    """
    return service.update_player_scout(player_id, scout_update)

@router.delete("/{player_id}", response_model=PlayerResponse, summary="Deletar um jogador")
def delete_player(player_id: int, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para deletar um jogador
    (soft delete - marca como inativo)
    """
    return service.delete_player(player_id)

@router.get("/{player_id}/stats", response_model=PlayerStatsResponse, summary="Obter as estatísticas de um jogador")
def get_player_stats(player_id: int, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para obter as estatísticas de um jogador
    """
    return service.get_player_stats(player_id)

@router.get("/rankings/top-scorers", response_model=List[PlayerStatsResponse], summary="Obter os jogadores com mais gols")
def get_top_scorers(limit: int = 10, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para obter os jogadores com mais gols
    - **limit**: número máximo de jogadores a retornar (padrão: 10)
    """
    return service.get_top_scorers(limit=limit)

@router.get("/rankings/top-assists", response_model=List[PlayerStatsResponse], summary="Obter os jogadores com mais assistências")
def get_top_assists(limit: int = 10, service: ServicePlayer = Depends(get_player_service)):
    """
    Endpoint para obter os jogadores com mais assistências
    - **limit**: número máximo de jogadores a retornar (padrão: 10)
    """
    return service.get_top_assisters(limit=limit)