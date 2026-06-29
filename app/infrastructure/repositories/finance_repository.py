"""
Repository para operações com Finance e MonthlyPayment
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime
from decimal import Decimal
from app.infrastructure.models.finance import Finance, MonthlyPayment
from app.domain.schemas.finance import FinanceCreate, FinanceUpdate

class FinanceRepository:
    """Repository Pattern para Finance"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, finance_data: FinanceCreate) -> Finance:
        """Cria um novo registro financeiro mensal"""

        finance = Finance(
            month=finance_data.month,
            year=finance_data.year,
            guest_revenue=finance_data.guest_revenue,
            court_cost=finance_data.court_cost,
            misc_expenses=finance_data.misc_expenses,
            notes=finance_data.notes
        )
        self.db.add(finance)
        self.db.commit()
        self.db.refresh(finance)
        return finance
    
    def get_by_id(self, finance_id: int, with_payments: bool = False) -> Optional[Finance]:
        """Busca finanças por ID"""

        query = self.db.query(Finance)
        if with_payments:
            query = query.options(joinedload(Finance.payments))
        return query.filter(Finance.id == finance_id).first()
    
    def get_by_month_year(self, month: int, year: int, with_payments: bool = False) -> Optional[Finance]:
        """Busca finanças por mês e ano específicos"""

        query = self.db.query(Finance)
        if with_payments:
            query = query.options(joinedload(Finance.payments))
        return query.filter(and_(Finance.month == month, Finance.year == year)).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, year: Optional[int] = None) -> List[Finance]:
        """Lista todos os registros financeiros"""

        query = self.db.query(Finance)
        if year:
            query = query.filter(Finance.year == year)
        return query.order_by(Finance.year.desc(), Finance.month.desc()).offset(skip).limit(limit).all()
    
    def update(self, finance_id: int, finance_data: FinanceUpdate) -> Optional[Finance]:
        """Atualiza um registo financeiro"""

        finance = self.get_by_id(finance_id)
        if not finance:
            return None
        
        update_data = finance_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(finance, field, value)
        self.db.commit()
        self.db.refresh(finance)
        return finance
    
    def update_totals(self, finance_id: int, total_revenue: Decimal, balance: Decimal, accumulated: Decimal) -> Optional[Finance]:
        """Atualiza os totais calculados (receita, saldo, acumulado)"""

        finance = self.get_by_id(finance_id)
        if not finance:
            return None
        
        finance.total_revenue = total_revenue
        finance.balance = balance
        finance.accumulated_balance = accumulated

        self.db.commit()
        self.db.refresh(finance)
        return finance
    
    def delete(self, finance_id: int) -> bool:
        """Remove um registro financeiro"""

        finance = self.get_by_id(finance_id)
        if not finance:
            return False
        self.db.delete(finance)
        self.db.commit()
        return True
    
    def get_year_summary(self, year: int) -> List[Finance]:
        """Retorna o resumo de todos os meses de um ano"""
        return self.db.query(Finance).filter(Finance.year == year).order_by(Finance.month).all()

    def get_accumulated_balance(self, up_to_month: int, up_to_year: int) -> Decimal:
        """Calcula saldo acumulado até determinado mês/ano"""

        finances = self.db.query(Finance).filter(or_(Finance.year < up_to_year, Finance.year == up_to_year), and_(Finance.month <= up_to_month)).all()
        total = Decimal(sum(f.balance for f in finances) if finances else Decimal("0.00"))
        return total


class MonthlyPaymentRepository:
    """Repository Pattern para MonthlyPayment"""

    def __init__(self, db: Session):
        self.db = db
    
    def create(self, finance_id: int, player_id: int, amount: Decimal) -> MonthlyPayment:
        """Cria um novo pagamento mensal"""

        payment = MonthlyPayment(
            finance_id=finance_id,
            player_id=player_id,
            amount=amount,
            paid=False
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def create_bulk(self, finance_id: int, payments_data: List[tuple]) -> List[MonthlyPayment]:
        """
        Cria múltiplos pagamentos de uma vez
        Args:
            finance_id: ID do registro financeiro
            payments_data: Lista de tuplas (player_id, amount)
        """

        payments = []
        for player_id, amount in payments_data:
            payment = MonthlyPayment(
                finance_id=finance_id,
                player_id=player_id,
                amount=amount,
                paid=False
            )
            payments.append(payment)
            self.db.add(payment)
        self.db.commit()
        for payment in payments:
            self.db.refresh(payment)
        return payments

    def get_by_id(self, payment_id: int) -> Optional[MonthlyPayment]:
        """Busca pagamento por ID"""
        return self.db.query(MonthlyPayment).filter(MonthlyPayment.id == payment_id).first()
    
    def get_by_finance_and_player(self, finance_id: int, player_id: int) -> Optional[MonthlyPayment]:
        """Busca pagamento por finanças e jogador"""
        return self.db.query(MonthlyPayment).filter(and_(MonthlyPayment.finance_id == finance_id, MonthlyPayment.player_id == player_id)).first()
    
    def get_by_finance(self, finance_id: int) -> List[MonthlyPayment]:
        """Retorna todos os pagamentos de um mês"""
        return self.db.query(MonthlyPayment).filter(MonthlyPayment.finance_id == finance_id).all()
    
    def mark_as_paid(self, payment_id: int, paid: bool = True) -> Optional[MonthlyPayment]:
        """Marca pagamento como pago/não pago"""

        payment = self.get_by_id(payment_id)
        if not payment:
            return None
        payment.paid = paid
        payment.paid_at = datetime.now()

        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def update_amount(self, payment_id: int, amount: Decimal) -> Optional[MonthlyPayment]:
        """Atualiza o valor de um pagamento"""

        payment = self.get_by_id(payment_id)
        if not payment:
            return None
        payment.amount = amount
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def delete(self, payment_id: int) -> bool:
        """Remove um pagamento"""

        payment = self.get_by_id(payment_id)
        if not payment:
            return False
        self.db.delete(payment)
        self.db.commit()
        return True
    
    def count_paid(self, finance_id: int) -> int:
        """Conta quantos pagamentos foram feitos"""
        return self.db.query(MonthlyPayment).filter(and_(MonthlyPayment.finance_id == finance_id, MonthlyPayment.paid == True)).count()
    
    def count_pending(self, finance_id: int) -> int:
        """Conta quantos pagamentos estão pendentes"""
        return self.db.query(MonthlyPayment).filter(and_(MonthlyPayment.finance_id == finance_id, MonthlyPayment.paid == False)).count()
    
    def get_total_paid(self, finance_id: int) -> Decimal:
        """Soma o total de pagamentos que foram feitos"""

        payments = self.db.query(MonthlyPayment).filter(and_(MonthlyPayment.finance_id == finance_id, MonthlyPayment.paid == True)).all()
        total = Decimal(sum(p.amount for p in payments) if payments else Decimal("0.00"))
        return total
    
    def get_total_pending(self, finance_id: int) -> Decimal:
        """Soma o total de pagamentos pendentes"""

        payments = self.db.query(MonthlyPayment).filter(and_(MonthlyPayment.finance_id == finance_id, MonthlyPayment.paid == False)).all()
        total = Decimal(sum(p.amount for p in payments) if payments else Decimal("0.00"))
        return total