"""
Service para lógica de negócio de Finance
"""

from typing import List, Optional
from decimal import Decimal
from app.infrastructure.repositories.player_repository import PlayerRepository
from app.infrastructure.repositories.finance_repository import (
    FinanceRepository,
    MonthlyPaymentRepository
)
from app.domain.schemas.finance import (
    FinanceCreate,
    FinanceUpdate,
    FinanceResponse,
    FinanceDetailResponse,
    FinanceSummaryResponse,
    MonthlyPaymentResponse,
    PaymentMarkPaidRequest
)
from fastapi import HTTPException, status

class FinanceService:
    """Service com lógica de negócio para Finance"""

    def __init__(self, finance_repo: FinanceRepository, player_repo: PlayerRepository, payment_repo: MonthlyPaymentRepository):
        self.finance_repo = finance_repo
        self.player_repo = player_repo
        self.payment_repo = payment_repo
    
    def create_month(self, finance_data: FinanceCreate) -> FinanceDetailResponse:
        """
        Cria um novo registro mensal

        Fluxo:
        1. Valida se já não existe registro para o mês/ano
        2. Cria o registro financeiro
        3. Se solicitado, cria pagamentos para todos os jogadores ativos
        4. Recalcula totais (receita, saldo, acumulado)
        5. Retorna o registro completo com todos os pagamentos
        """

        #verificar se já existe um registro para esse mês/ano
        existing = self.finance_repo.get_by_month_year(finance_data.month, finance_data.year)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Finance record for {finance_data.year}-{finance_data.month:02d} already exists")
        
        #Criar registro
        finance = self.finance_repo.create(finance_data)

        #Se solicitado, cria pagamentos para todos os jogadores ativos
        if finance_data.include_active_players:
            active_players = self.player_repo.get_all(active_only=True)
            payments_data = [
                (player.id, finance_data.monthly_fee)
                for player in active_players
            ]
            if payments_data:
                self.payment_repo.create_bulk(finance.id, payments_data)

        #Recalcular totais
        self._recalculate_totals(finance.id)

        #Retornar registro completo
        return self._finance_to_detail_response(finance)
    
    def get_month(self, finance_id: int) -> FinanceDetailResponse:
        """Busca finanças de um mês por ID com todos os detalhes"""

        finance = self.finance_repo.get_by_id(finance_id, with_payments=True)
        if not finance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finance record not found")
        return self._finance_to_detail_response(finance)

    def get_by_month_year(self, month: int, year: int) -> FinanceDetailResponse:
        """Busca finanças por mês e ano específicos"""

        finance = self.finance_repo.get_by_month_year(month, year, with_payments=True)
        if not finance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Finance record for {year}-{month:02d} not found")
        return self._finance_to_detail_response(finance)

    def list_months(self, skip: int = 0, limit: int = 100, year: Optional[int] = None) -> List[FinanceDetailResponse]:
        """Lista todos os registros financeiros"""

        finances = self.finance_repo.get_all(skip, limit, year)
        return [self._finance_to_detail_response(f) for f in finances]
    
    def update_month(self, finance_id: int, finance_data: FinanceUpdate) -> FinanceDetailResponse:
        """
        Atualiza um registro financeiro

        Após atualizar, recalcula automaticamente os totais
        """

        finance = self.finance_repo.update(finance_id, finance_data)
        if not finance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finance record not found")
        
        #Recalcular totais
        self._recalculate_totals(finance_id)
        return self._finance_to_detail_response(finance)

    def delete_month(self, finance_id: int) -> dict:
        """Remove um registro financeiro e todos os seus pagamentos"""

        success = self.finance_repo.delete(finance_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finance record not found")
        return {"message": "Finance record deleted successfully"}
    
    def mark_payment_as_paid(self, finance_id: int, payment_request: PaymentMarkPaidRequest) -> FinanceDetailResponse:
        """
        Marca um pagamento como pago/não pago

        Fluxo:
        1. Valida se o finance existe
        2. Busca o pagamento do jogador
        3. Marca como pago/não pago
        4. Atualiza o status no player(montlhy_fee_paid)
        5. Recalcula os totais
        6. Retorna finance atualizado
        """

        #verificar se o finance existe
        finance = self.finance_repo.get_by_id(finance_id)
        if not finance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finance record not found")
        
        #buscar pagamento
        payment = self.payment_repo.get_by_finance_and_player(finance_id, payment_request.player_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found for thhis player")
        
        #marcar como pago/não pago
        self.payment_repo.mark_as_paid(payment.id, payment_request.paid)

        #atualizar status no player
        player = self.player_repo.get_by_id(payment_request.player_id)
        if player:
            player.monthly_fee_paid = payment_request.paid
        
        #recalcular totais
        self._recalculate_totals(finance_id)
        return self.get_month(finance_id)

    def get_year_summary(self, year: int) -> FinanceSummaryResponse:
        """
        Retorna resumo financeiro completo de um ano

        Inclui:
        - Total de receitas do ano
        - Total de despesas do ano
        - Saldo líquido do ano
        - Número de meses registrados
        - Detalhes de cada mês
        """

        finances = self.finance_repo.get_year_summary(year)
        if not finances:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No finance found for year {year}")
        
        #calcular totais do ano
        total_revenue = sum(f.total_income for f in finances)
        total_expenses = sum(f.total_expenses for f in finances)
        net_balance = total_revenue - total_expenses

        return FinanceSummaryResponse(
            total_revenue=Decimal(str(total_revenue)),
            total_expenses=Decimal(str(total_expenses)),
            net_balance=Decimal(str(net_balance)),
            total_months=len(finances),
            months=[self._finance_to_response(f) for f in finances]
        )

    def _recalculate_totals(self, finance_id: int):
        """
        Recalcula os totais de um registro financeiro

        Calcula:
        1. Receita total (soma dos pagamentos feitos)
        2. Saldo do mês (receitas - despesas)
        3. Saldo acumulado (saldo do mês anterior + saldo deste mês)
        """

        finance = self.finance_repo.get_by_id(finance_id)
        if not finance:
            return
        
        #Calcular receita com mensalidades pagas
        total_revenue = self.payment_repo.get_total_paid(finance_id)

        #Calcular saldo do mês
        total_income = total_revenue + finance.guest_revenue
        total_expenses = finance.court_cost + finance.misc_expenses
        balance = total_income - total_expenses

        #Calcular saldo acumulado (mês anterior + mês atual)
        previous_month = finance.month - 1 if finance.month > 1 else 12
        previous_year = finance.year if finance.month > 1 else finance.year - 1

        previous_finance = self.finance_repo.get_by_month_year(previous_month, previous_year)
        previous_accumulated = previous_finance.accumulated_balance if previous_finance else Decimal("0.00")
        accumulated = previous_accumulated + balance

        #Atualizar totais
        self.finance_repo.update_totals(finance_id, total_revenue, balance, accumulated)

    def _finance_to_response(self, finance) -> FinanceResponse:
        """Converte Finance para FinanceResponse (sem pagamentos)"""

        payments_count = len(finance.payments) if hasattr(finance, 'payments') else 0
        paid_count = self.payment_repo.count_paid(finance.id)
        pending_count = self.payment_repo.count_pending(finance.id)

        return FinanceResponse(
            id=finance.id,
            month=finance.month,
            year=finance.year,
            total_revenue=finance.total_revenue,
            guest_revenue=finance.guest_revenue,
            court_cost=finance.court_cost,
            misc_expenses=finance.misc_expenses,
            balance=finance.balance,
            accumulated=finance.accumulated_balance,
            notes=finance.notes,
            created_at=finance.created_at,
            updated_at=finance.updated_at,
            total_expenses=Decimal(str(finance.total_expenses)),
            total_income=Decimal(str(finance.total_income)),
            net_balance=Decimal(str(finance.net_balance)),
            payments_count=payments_count,
            paid_count=paid_count,
            pending_count=pending_count
        )

    
    def _finance_to_detail_response(self, finance) -> FinanceDetailResponse:
        """Converte Finance para FinanceDetailResponse (com pagamentos)"""

        #Recarregar com pagamentos se necessário
        if finance is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finance record not found")
        if not hasattr(finance, 'payments') or not finance.payments:
            finance = self.finance_repo.get_by_id(finance.id, with_payments=True)
            if finance is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finance record not found")
        
        #Converter pagamentos 
        payments_list = []
        for payment in getattr(finance, 'payments', []):
            player = self.player_repo.get_by_id(payment.player_id)
            payments_list.append(MonthlyPaymentResponse(
                id=payment.id,
                finance_id=payment.finance_id,
                player_id=payment.player_id,
                amount=payment.amount,
                paid=payment.paid,
                player_name=player.name if player else None
            ))

        #Retornar com pagamentos
        return FinanceDetailResponse(
            id=finance.id,
            month=finance.month,
            year=finance.year,
            total_revenue=finance.total_revenue,
            guest_revenue=finance.guest_revenue,
            court_cost=finance.court_cost,
            misc_expenses=getattr(finance, "misc_expenses", Decimal("0.00")),
            balance=finance.balance,
            accumulated=getattr(finance, "accumulated_balance", Decimal("0.00")),
            created_at=finance.created_at,
            updated_at=finance.updated_at,
            total_expenses=getattr(finance, "total_expenses", Decimal("0.00")),
            total_income=getattr(finance, "total_income", Decimal("0.00")),
            net_balance=getattr(finance, "net_balance", Decimal("0.00")),
            notes=finance.notes,
            payments=payments_list
        )
