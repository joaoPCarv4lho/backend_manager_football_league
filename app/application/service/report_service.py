"""Service para geração de relatórios (recurso Pro)"""

from app.infrastructure.repositories.player_repository import PlayerRepository
from app.application.service.finance_service import FinanceService
from app.domain.schemas.report import (
    ScoutReport,
    ScoutReportItem,
    PlayerAward,
    AwardsReport,
)
from app.domain.schemas.finance import FinanceSummaryResponse


class ReportService:
    """Gera relatórios consolidados de scouts, premiações e finanças"""

    def __init__(self, player_repo: PlayerRepository, finance_service: FinanceService):
        self.player_repo = player_repo
        self.finance_service = finance_service

    def scouts_report(self) -> ScoutReport:
        """Relatório de scouts de todos os jogadores, ordenado por total (gols + assistências)"""
        players = self.player_repo.get_all(limit=10000)

        items = [
            ScoutReportItem(
                player_id=p.id,
                name=p.name,
                position=p.position,
                goals=p.total_goals or 0,
                assists=p.total_assists or 0,
                total_scouts=(p.total_goals or 0) + (p.total_assists or 0),
                games=p.total_games or 0,
            )
            for p in players
        ]
        items.sort(key=lambda i: (i.total_scouts, i.goals), reverse=True)

        return ScoutReport(total_players=len(items), items=items)

    def awards_report(self) -> AwardsReport:
        """Premiação: artilheiro, líder de assistências e craque (maior soma de scouts)"""
        players = self.player_repo.get_all(limit=10000)
        if not players:
            return AwardsReport()

        def goals(p):
            return p.total_goals or 0

        def assists(p):
            return p.total_assists or 0

        def total(p):
            return goals(p) + assists(p)

        top_scorer = max(players, key=goals)
        top_assister = max(players, key=assists)
        craque = max(players, key=total)

        return AwardsReport(
            top_scorer=PlayerAward(player_id=top_scorer.id, name=top_scorer.name, value=goals(top_scorer)) if goals(top_scorer) > 0 else None,
            top_assister=PlayerAward(player_id=top_assister.id, name=top_assister.name, value=assists(top_assister)) if assists(top_assister) > 0 else None,
            player_of_the_season=PlayerAward(player_id=craque.id, name=craque.name, value=total(craque)) if total(craque) > 0 else None,
        )

    def financial_year(self, year: int) -> FinanceSummaryResponse:
        """Consolidado financeiro anual (reutiliza o resumo do FinanceService)"""
        return self.finance_service.get_year_summary(year)
