from fastapi import APIRouter, HTTPException, Query, status

from src.schemas import Expense, ExpenseCreate
from src.storage import (
    add_expense,
    calculate_total,
    delete_expense,
    get_expenses,
)


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.post(
    "",
    response_model=Expense,
    status_code=status.HTTP_201_CREATED,
    summary="Add an expense",
)
def create_expense(expense: ExpenseCreate) -> Expense:
    """Create and persist a new personal expense."""
    expense_data = expense.model_dump(mode="json")
    created_expense = add_expense(expense_data)

    return Expense(**created_expense)


@router.get(
    "/total",
    summary="Calculate total expenses",
)
def get_total_expenses(
    category: str | None = Query(
        default=None,
        description="Optional category used to calculate a category-specific total.",
    ),
) -> dict[str, str | float]:
    """Calculate the overall total or the total for a specific category."""
    total = calculate_total(category)

    if category is not None:
        return {
            "category": category.strip(),
            "total": total,
        }

    return {"total": total}


@router.get(
    "",
    response_model=list[Expense],
    summary="View expenses",
)
def list_expenses(
    category: str | None = Query(
        default=None,
        description="Optional category used to filter expenses.",
    ),
) -> list[Expense]:
    """Return all expenses or expenses matching a category."""
    expenses = get_expenses(category)

    return [Expense(**expense) for expense in expenses]


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an expense",
)
def remove_expense(expense_id: int) -> dict[str, str]:
    """Delete an expense using its unique ID."""
    deleted = delete_expense(expense_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return {"message": "Expense deleted successfully"}