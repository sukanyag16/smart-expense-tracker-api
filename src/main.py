from fastapi import FastAPI

from src.routes import router as expenses_router


app = FastAPI(
    title="Smart Expense Tracker API",
    description=(
        "A REST API for creating, viewing, filtering, totaling, "
        "and deleting personal expenses."
    ),
    version="1.0.0",
)

app.include_router(expenses_router)