from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    """Payload required to create a new expense."""

    title: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    date: date

    @field_validator("title", "category")
    @classmethod
    def strip_and_validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be empty or contain only whitespace")

        return value


class Expense(ExpenseCreate):
    """Expense returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., gt=0)