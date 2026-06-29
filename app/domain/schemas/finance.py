"""
Schemas Pydantic para Finance e MonthlyPayment
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class MonthlyPaymentBase(BaseModel):
    """Schema base de MonthlyPayment"""
    player_id: int = Field(..., gt=0, description="ID do jogador")
    amount: Decimal = Field(..., ge=0, decimal_places=2, description="Valor da mensalidade")

class MonthlyPaymentCreate(MonthlyPaymentBase):
    """Schema para criação de MonthlyPayment"""
    pass

class MonthlyPaymentUpdate(BaseModel):
    """Schema para atualização de MonthlyPayment"""
    amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    paid: Optional[bool] = None

class MonthlyPaymentResponse(MonthlyPaymentBase):
    """Schema de resposta para MonthlyPayment"""
    id: int
    finance_id: int
    paid: bool
    paid_at: Optional[datetime] = None
    player_name: Optional[str] = None

class FinanceBase(BaseModel):
    """Schema base para Finance"""
    month: int = Field(..., ge=1, le=12, description="Mês (1-12)")
    year: int = Field(..., ge=2020, le=2200, description="Ano")
    guest_revenue: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2, description="Receita com convidados")
    court_cost: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2, description="Custo da quadra")
    misc_expenses: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2, description="Despesas diversas")
    notes: Optional[str] = Field(None, max_length=500, description="Observações")

    @validator('month')
    def validate_month(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Month must be between 1 and 12')
        return v
    

class FinanceCreate(FinanceBase):
    """Schema para criação de Finance"""
    monthly_fee: Decimal = Field(..., gt=0, decimal_places=2, description="Valor da mensalidade padrão")
    include_active_players: bool = Field(default=True, description="Se True, cria pagamentos automaticamente para jogadores ativos")

class FinanceUpdate(BaseModel):
    """Schema para atualização de Finance"""
    guest_revenue: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    court_cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    misc_expenses: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notes: Optional[str] = Field(None, max_length=500)

class FinanceResponse(FinanceBase):
    """Schema de resposta de Finance"""
    id: int
    total_revenue: Decimal
    balance: Decimal
    accumulated: Decimal
    created_at: datetime
    updated_at: datetime

    total_expenses: Decimal
    total_income: Decimal
    net_balance: Decimal

    payments_count: int = 0
    paid_count: int = 0
    pending_count: int = 0

    class Config:
        from_attributes = True

class FinanceDetailResponse(FinanceResponse):
    """Schema de resposta detalhada de Finance com todos os pagamentos"""
    payments: List[MonthlyPaymentResponse] = []

    class Config:
        from_attributes = True

class FinanceSummaryResponse(BaseModel):
    """Schema para um resumo financeiro de um período (geralmente anual)"""
    total_revenue: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    total_months: int
    months: List[FinanceResponse]

    class Config:
        from_attributes = True

class PaymentMarkPaidRequest(BaseModel):
    """Schema para marcar pagamento como pago/não pago"""
    player_id: int = Field(..., gt=0, description="ID do jogador")
    paid: bool = Field(default=True, description="True para marcar como pago, False para pendente")
