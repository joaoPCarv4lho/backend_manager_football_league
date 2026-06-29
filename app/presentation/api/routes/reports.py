"""Routes/Endpoints para Relatórios (recurso Pro)"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.repositories.player_repository import PlayerRepository
from app.infrastructure.repositories.finance_repository import (
    FinanceRepository,
    MonthlyPaymentRepository,
)
from app.application.service.finance_service import FinanceService
from app.application.service.report_service import ReportService
from app.domain.schemas.report import ScoutReport, AwardsReport
from app.domain.schemas.finance import FinanceSummaryResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """Dependency Injection do ReportService"""
    player_repo = PlayerRepository(db)
    finance_service = FinanceService(
        FinanceRepository(db), player_repo, MonthlyPaymentRepository(db)
    )
    return ReportService(player_repo, finance_service)


@router.get("/scouts", response_model=ScoutReport, summary="Relatório de scouts dos jogadores")
def scouts_report(service: ReportService = Depends(get_report_service)):
    """Ranking consolidado de todos os jogadores por total de scouts (gols + assistências)."""
    return service.scouts_report()


@router.get("/awards", response_model=AwardsReport, summary="Premiação anual")
def awards_report(service: ReportService = Depends(get_report_service)):
    """Premiação baseada nos scouts acumulados: artilheiro, líder de assistências e craque."""
    return service.awards_report()


@router.get("/financial/{year}", response_model=FinanceSummaryResponse, summary="Consolidado financeiro anual")
def financial_report(year: int, service: ReportService = Depends(get_report_service)):
    """Resumo financeiro do ano (receitas, despesas, saldo líquido e meses)."""
    return service.financial_year(year)
