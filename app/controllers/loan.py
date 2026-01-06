"""Controller for Loan endpoints."""

from datetime import timedelta
from decimal import Decimal
from typing import Sequence

from advanced_alchemy.exceptions import DuplicateKeyError, NotFoundError
from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData

from app.controllers import duplicate_error_handler, not_found_error_handler
from app.dtos.loan import LoanCreateDTO, LoanReadDTO, LoanUpdateDTO
from app.models import Loan
from app.repositories.loan import LoanRepository, provide_loan_repo


class LoanController(Controller):
    """Controller for loan management operations."""

    path = "/loans"
    tags = ["loans"]
    return_dto = LoanReadDTO
    dependencies = {"loans_repo": Provide(provide_loan_repo)}
    exception_handlers = {
        NotFoundError: not_found_error_handler,
        DuplicateKeyError: duplicate_error_handler,
    }

    @get("/")
    async def list_loans(self, loans_repo: LoanRepository) -> Sequence[Loan]:
        """Get all loans."""
        return loans_repo.list()

    @get("/active")
    async def list_active_loans(self, loans_repo: LoanRepository) -> Sequence[Loan]:
        """Get loans with status ACTIVE."""

        return loans_repo.get_active_loans()

    @get("/overdue")
    async def list_overdue_loans(self, loans_repo: LoanRepository) -> Sequence[Loan]:
        """Get overdue loans and mark them as OVERDUE."""

        return loans_repo.get_overdue_loans()

    @get("/user/{user_id:int}")
    async def get_user_loan_history(self, user_id: int, loans_repo: LoanRepository) -> Sequence[Loan]:
        """Get full loan history of a user."""

        return loans_repo.get_user_loan_history(user_id=user_id)

    @get("/{id:int}")
    async def get_loan(self, id: int, loans_repo: LoanRepository) -> Loan:
        """Get a loan by ID."""
        return loans_repo.get(id)

    @get("/{id:int}/fine")
    async def get_loan_fine(self, id: int, loans_repo: LoanRepository) -> dict[str, str]:
        """Calculate fine for a loan."""

        fine: Decimal = loans_repo.calculate_fine(loan_id=id)
        return {"fine_amount": str(fine)}

    @post("/", dto=LoanCreateDTO)
    async def create_loan(
        self,
        data: DTOData[Loan],
        loans_repo: LoanRepository,
    ) -> Loan:
        """Create a new loan."""

        instance = data.create_instance()
        instance.due_date = instance.loan_dt + timedelta(days=14)
        return loans_repo.add(instance)

    @post("/{id:int}/return")
    async def return_loan_book(self, id: int, loans_repo: LoanRepository) -> Loan:
        """Process return of a loan."""

        return loans_repo.return_book(loan_id=id)

    @patch("/{id:int}", dto=LoanUpdateDTO)
    async def update_loan(
        self,
        id: int,
        data: DTOData[Loan],
        loans_repo: LoanRepository,
    ) -> Loan:
        """Update a loan by ID."""
        loan, _ = loans_repo.get_and_update(match_fields="id", id=id, **data.as_builtins())

        return loan

    @delete("/{id:int}")
    async def delete_loan(self, id: int, loans_repo: LoanRepository) -> None:
        """Delete a loan by ID."""
        loans_repo.delete(id)
