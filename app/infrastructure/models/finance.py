"""
Models de Finanças (Finance) e Pagamentos Mensais (MonthlyPayment)
"""

from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, DateTime
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.core.database import Base

class Finance(Base):
    """
    Modelo de Finanças (Finance)

    Armazena informações financeiras de cada mês da liga:
    - Receitas (mensalidades + convidados)
    - Despesas (prêmios + custos operacionais)
    - Saldos (mensal + acumulado)
    """

    __tablename__ = "tb_finances"

    #Identificação
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # Ex: 1-12
    year: Mapped[int] = mapped_column(Integer, nullable=False)   # Ex: 2024

    #Receitas
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00) #Total arrecadado com mensalidades
    guest_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00) #Arrecadação de convidados

    #Despesas
    court_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00) #Custo de manutenção da quadra
    misc_expenses: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00) #Despesas diversas (prêmios, pós-jogo, etc)

    #Saldos
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00) #Saldo do mês (receitas - despesas)
    accumulated_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00) #Saldo acumulado até o mês atual

    #Metadata
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) #Observações adicionais
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc)) #Data de criação do registro
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)) #Data de última atualização do registro

    #Relacionamentos
    payments = relationship("MonthlyPayment", back_populates="finance") #Relacionamento com pagamentos mensais

    @property
    def total_expenses(self) -> Decimal:
        """Total de despesas do mês (custo da quadra + despesas diversas)"""
        return self.court_cost + self.misc_expenses

    @property
    def total_income(self) -> Decimal:
        """Total de receitas do mês"""
        return self.total_revenue + self.guest_revenue
    
    @property
    def net_balance(self) -> Decimal:
        """Saldo líquido (receitas - despesas)"""
        return self.total_income - self.total_expenses

    def __repr__(self):
        return f"<Finance(id={self.id}, month={self.month}, year={self.year}, balance={self.balance})>"

class MonthlyPayment(Base):
    """
    Model de Pagamento Mensal de jogador

    Representa o pagamento de mensalidade de um jogador específico em um mês específico
    """

    __tablename__ = "tb_monthly_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    finance_id: Mapped[int] = mapped_column(Integer, ForeignKey("tb_finances.id"), nullable=False) #Chave estrangeira para o mês de finanças
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False) #Chave estrangeira para o jogador

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00) #Valor pago
    paid: Mapped[bool] = mapped_column(Boolean, default=False) #Indica se o pagamento foi realizado
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc)) #Data do pagamento
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) #Observações adicionais

    #Relacionamentos
    finance = relationship("Finance", back_populates="payments") #Relacionamento com finanças
    player = relationship("Player") #Relacionamento com jogador (assumindo que existe um

    def __repr__(self):
        status = "Pago" if self.paid else "Pendente"
        return f"<MonthlyPayment(id={self.id}, player_id={self.player_id}, amount={self.amount}, status={status})>"