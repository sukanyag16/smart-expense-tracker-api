import json
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).parent / "expenses.json"


def load_expenses() -> list[dict[str, Any]]:
    """Load all expenses from the JSON data file."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_expenses(expenses: list[dict[str, Any]]) -> None:
    """Persist all expenses to the JSON data file."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=2)


def get_next_id(expenses: list[dict[str, Any]]) -> int:
    """Return the next available expense ID."""
    if not expenses:
        return 1

    return max(expense["id"] for expense in expenses) + 1


def add_expense(expense_data: dict[str, Any]) -> dict[str, Any]:
    """Create and persist a new expense."""
    expenses = load_expenses()

    expense = {
        "id": get_next_id(expenses),
        **expense_data,
    }

    expenses.append(expense)
    save_expenses(expenses)

    return expense


def get_expenses(category: str | None = None) -> list[dict[str, Any]]:
    """Return all expenses, optionally filtered by category."""
    expenses = load_expenses()

    if category is None:
        return expenses

    normalized_category = category.strip().casefold()

    return [
        expense
        for expense in expenses
        if expense["category"].casefold() == normalized_category
    ]


def calculate_total(category: str | None = None) -> float:
    """Calculate the total expense amount, optionally by category."""
    expenses = get_expenses(category)

    return round(sum(expense["amount"] for expense in expenses), 2)


def delete_expense(expense_id: int) -> bool:
    """Delete an expense by ID. Return True when an expense was deleted."""
    expenses = load_expenses()

    updated_expenses = [
        expense for expense in expenses if expense["id"] != expense_id
    ]

    if len(updated_expenses) == len(expenses):
        return False

    save_expenses(updated_expenses)

    return True