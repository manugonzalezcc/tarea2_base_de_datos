"""Repository for Loan database operations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Sequence

from advanced_alchemy.repository import SQLAlchemySyncRepository
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models import Book, Loan, LoanStatus


class LoanRepository(SQLAlchemySyncRepository[Loan]):
    """Repository for loan database operations."""

    model_type = Loan

    def get_active_loans(self) -> Sequence[Loan]:
        """Return loans with status ACTIVE."""

        return self.list(Loan.status == LoanStatus.ACTIVE)

    def get_overdue_loans(self) -> Sequence[Loan]:
        """Return loans past due_date and still ACTIVE; also mark them as OVERDUE."""

        today = date.today()

        stmt = sa.select(Loan).where(
            sa.and_(
                Loan.status == LoanStatus.ACTIVE,
                Loan.due_date < today,
            )
        )
        overdue_loans = list(self.session.execute(stmt).scalars().all())

        for loan in overdue_loans:
            loan.status = LoanStatus.OVERDUE
            self.update(loan)

        return overdue_loans

    def calculate_fine(self, loan_id: int) -> Decimal:
        """Calculate fine: $500 per day late, max $50000."""

        loan = self.get(loan_id)
        today = date.today()
        if today <= loan.due_date:
            return Decimal("0.00")

        days_late = (today - loan.due_date).days
        fine = Decimal(days_late) * Decimal("500")
        if fine > Decimal("50000"):
            fine = Decimal("50000")

        return fine.quantize(Decimal("0.01"))

    def return_book(self, loan_id: int) -> Loan:
        """Process book return.

        - status -> RETURNED
        - return_dt -> today
        - fine_amount -> calculated if overdue
        - increment book stock
        """

        loan = self.get(loan_id)
        if loan.status == LoanStatus.RETURNED:
            return loan

        today = date.today()
        loan.return_dt = today
        loan.status = LoanStatus.RETURNED

        if today > loan.due_date:
            loan.fine_amount = self.calculate_fine(loan_id)
        else:
            loan.fine_amount = None

        # Increment stock
        book = self.session.get(Book, loan.book_id)
        if book is not None:
            book.stock += 1
            self.session.add(book)

        return self.update(loan)

    def get_user_loan_history(self, user_id: int) -> Sequence[Loan]:
        """Return user's full loan history ordered by loan date desc."""

        stmt = sa.select(Loan).where(Loan.user_id == user_id).order_by(Loan.loan_dt.desc())
        return list(self.session.execute(stmt).scalars().all())


async def provide_loan_repo(db_session: Session) -> LoanRepository:
    """Provide loan repository instance with auto-commit."""
    return LoanRepository(session=db_session, auto_commit=True)
