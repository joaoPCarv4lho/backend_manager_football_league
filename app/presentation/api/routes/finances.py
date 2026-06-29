"""
Routes/Endpoints para Finance
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.infrastructure.repositories.finance_repository import (
    FinanceRepository, 
    MonthlyPaymentRepository
)
from app.infrastructure.repositories.player_repository import PlayerRepository
from app.application.service.finance_service import FinanceService
from app.domain.schemas.finance import (
    FinanceCreate,
    FinanceUpdate,
    FinanceResponse,
    FinanceDetailResponse,
    FinanceSummaryResponse,
    PaymentMarkPaidRequest
)

router = APIRouter(prefix="/finances", tags=["Finances"])

def get_finance_service(db: Session = Depends(get_db)) -> FinanceService:
    """Dependecy Injection do FinanceService"""

    finance_repo = FinanceRepository(db)
    payment_repo = MonthlyPaymentRepository(db)
    player_repo = PlayerRepository(db)
    return FinanceService(finance_repo, player_repo, payment_repo)

@router.post("/", response_model=FinanceDetailResponse, status_code=status.HTTP_201_CREATED, summary="Criar registro Financeiro")
def create_month(finance_data: FinanceCreate, service: FinanceService = Depends(get_finance_service)):
    """
    Cria um novo registro financeiro para um mês.
    
    - **month**: Mês (1-12)
    - **year**: Ano (ex: 2024)
    - **monthly_fee**: Valor da mensalidade padrão
    - **include_active_players**: Se True, cria pagamentos automaticamente para todos os jogadores ativos
    - **guest_revenue**: Receita com convidados (opcional)
    - **court_cost**: Custo da quadra (opcional)
    - **misc_expenses**: Despesas diversas (opcional)
    - **notes**: Observações (opcional)
    
    Quando `include_active_players` é True, o sistema automaticamente:
    1. Busca todos os jogadores ativos
    2. Cria um registro de pagamento para cada um
    3. Define o valor como `monthly_fee`
    4. Marca todos como não pagos inicialmente
    
    Os totais são calculados automaticamente:
    - `total_revenue`: Soma dos pagamentos marcados como pagos
    - `balance`: (total_revenue + guest_revenue) - (court_cost + misc_expenses)
    - `accumulated`: Saldo acumulado considerando meses anteriores
    """
    return service.create_month(finance_data)

@router.get("/", response_model=List[FinanceResponse], summary="Listar registros financeiros")
def list_months(
    skip: int = Query(0, ge=0, description="Número de registros a pular"), 
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"), 
    year: Optional[int] = Query(None, description="Filtrar por ano específico"),
    service: FinanceService = Depends(get_finance_service)
    ):
    """
    Lista todos os registros financeiros.
    
    Por padrão, retorna os registros ordenados por ano e mês (mais recentes primeiro).
    
    - **skip**: Número de registros a pular (para paginação)
    - **limit**: Número máximo de registros a retornar
    - **year**: Se fornecido, filtra apenas registros deste ano
    
    Exemplo: `GET /finances?year=2024` retorna apenas os meses de 2024
    """
    return service.list_months(skip, limit, year)

@router.get("/{finance_id}", response_model=FinanceDetailResponse, summary="Buscar registro financeiro por ID")
def ge_month(finance_id: int, service: FinanceService = Depends(get_finance_service)):
    """
    Busca um registro financeiro específico por ID.
    
    Retorna:
    - Todos os dados financeiros do mês
    - Lista completa de pagamentos com detalhes dos jogadores
    - Totais calculados
    """
    return service.get_month(finance_id)

@router.get("/month/{year}/{month}", response_model=FinanceDetailResponse, summary="Buscar registro por mês/ano")
def get_by_month_year(year: int, month: int = Path(..., ge=1, le=12, description="Mês 1-12"), service: FinanceService = Depends(get_finance_service)):
    """
    Busca um registro financeiro por mês e ano.
    
    Exemplo: `GET /finances/month/2024/3` busca o registro de Março/2024
    
    - **year**: Ano (ex: 2024)
    - **month**: Mês de 1 a 12
    """
    return service.get_by_month_year(month, year)

@router.patch("/{finance_id}", response_model=FinanceDetailResponse, summary="Atualizar registro Financeiro")
def update_month(finance_id: int, finance_data: FinanceUpdate, service: FinanceService = Depends(get_finance_service)):
    """
    Atualiza os dados de um registro financeiro.
    
    Você pode atualizar:
    - **guest_revenue**: Receita com convidados
    - **court_cost**: Custo da quadra
    - **misc_expenses**: Despesas diversas
    - **notes**: Observações
    
    Após a atualização, os totais são recalculados automaticamente.
    """
    return service.update_month(finance_id, finance_data)

@router.delete("/{finance_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover registro financeiro")
def delete_month(finance_id: int, service: FinanceService = Depends(get_finance_service)):
    """
    Remove um registro financeiro e todos os seus pagamentos.
    
    **Atenção**: Esta ação é irreversível e remove:
    - O registro financeiro
    - Todos os pagamentos associados
    
    Os saldos acumulados dos meses seguintes serão afetados.
    """
    return service.delete_month(finance_id)

@router.post("/{finance_id}/payments", response_model=FinanceDetailResponse, summary="Marcar pagamento como pago/não pago")
def mark_payment_as_paid(finance_id: int, payment_request: PaymentMarkPaidRequest, service: FinanceService = Depends(get_finance_service)):
    """
    Marca o pagamento de um jogador como pago ou não pago.
    
    - **player_id**: ID do jogador
    - **paid**: True para marcar como pago, False para marcar como não pago
    
    Quando marcado como pago:
    1. Atualiza o status do pagamento
    2. Registra a data/hora do pagamento
    3. Atualiza o campo `monthly_fee_paid` do jogador
    4. Recalcula os totais do mês
    5. Recalcula o saldo acumulado
    
    Retorna o registro financeiro completo atualizado.
    """
    return service.mark_payment_as_paid(finance_id, payment_request)

@router.get("/summary/{year}", response_model=FinanceSummaryResponse, summary="Resumo financeiro do ano")
def get_year_summary(year: int, service: FinanceService = Depends(get_finance_service)):
    """
    Retorna um resumo financeiro completo de um ano.
    
    Inclui:
    - **total_revenue**: Total de receitas do ano
    - **total_expenses**: Total de despesas do ano
    - **net_balance**: Saldo líquido do ano (receitas - despesas)
    - **total_months**: Número de meses registrados
    - **months**: Detalhes de cada mês
    
    Útil para:
    - Relatórios anuais
    - Análise de desempenho financeiro
    - Planejamento do próximo ano
    - Prestação de contas
    
    Exemplo: `GET /finances/summary/2024` retorna o resumo de 2024
    """
    return service.get_year_summary(year)