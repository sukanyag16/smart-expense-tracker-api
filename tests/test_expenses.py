import pytest
from fastapi.testclient import TestClient

from src import storage
from src.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def use_temporary_storage(tmp_path, monkeypatch):
    """Use a fresh temporary JSON file for every test."""
    test_file = tmp_path / "expenses.json"
    test_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(storage, "DATA_FILE", test_file)


def valid_expense(**overrides):
    """Return a valid expense payload with optional field overrides."""
    payload = {
        "title": "Lunch",
        "amount": 250.50,
        "category": "Food",
        "date": "2026-08-01",
    }
    payload.update(overrides)
    return payload


def test_create_expense():
    response = client.post("/expenses", json=valid_expense())

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Lunch"
    assert body["amount"] == 250.50
    assert body["category"] == "Food"
    assert body["date"] == "2026-08-01"


def test_multiple_expenses_receive_unique_ids():
    first = client.post(
        "/expenses",
        json=valid_expense(title="Lunch"),
    ).json()

    second = client.post(
        "/expenses",
        json=valid_expense(title="Coffee"),
    ).json()

    assert first["id"] == 1
    assert second["id"] == 2


def test_get_expenses_when_empty():
    response = client.get("/expenses")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_expenses():
    client.post("/expenses", json=valid_expense())

    client.post(
        "/expenses",
        json=valid_expense(
            title="Uber",
            amount=400,
            category="Travel",
        ),
    )

    response = client.get("/expenses")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_expenses_by_category():
    client.post("/expenses", json=valid_expense())

    client.post(
        "/expenses",
        json=valid_expense(
            title="Uber",
            category="Travel",
        ),
    )

    response = client.get("/expenses?category=Food")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "Food"


def test_category_filter_is_case_insensitive():
    client.post(
        "/expenses",
        json=valid_expense(category="Food"),
    )

    response = client.get("/expenses?category=food")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "Food"


def test_unknown_category_returns_empty_list():
    client.post("/expenses", json=valid_expense())

    response = client.get("/expenses?category=Education")

    assert response.status_code == 200
    assert response.json() == []


def test_calculate_overall_total():
    client.post(
        "/expenses",
        json=valid_expense(amount=250.50),
    )

    client.post(
        "/expenses",
        json=valid_expense(
            title="Uber",
            amount=400,
            category="Travel",
        ),
    )

    response = client.get("/expenses/total")

    assert response.status_code == 200
    assert response.json() == {"total": 650.50}


def test_calculate_total_by_category():
    client.post(
        "/expenses",
        json=valid_expense(amount=250),
    )

    client.post(
        "/expenses",
        json=valid_expense(
            title="Coffee",
            amount=150,
            category="Food",
        ),
    )

    client.post(
        "/expenses",
        json=valid_expense(
            title="Uber",
            amount=400,
            category="Travel",
        ),
    )

    response = client.get("/expenses/total?category=Food")

    assert response.status_code == 200
    assert response.json() == {
        "category": "Food",
        "total": 400.0,
    }


def test_unknown_category_total_is_zero():
    response = client.get("/expenses/total?category=Unknown")

    assert response.status_code == 200
    assert response.json() == {
        "category": "Unknown",
        "total": 0,
    }


def test_delete_expense():
    created = client.post(
        "/expenses",
        json=valid_expense(),
    ).json()

    response = client.delete(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Expense deleted successfully"
    }

    assert client.get("/expenses").json() == []


def test_delete_nonexistent_expense_returns_404():
    response = client.delete("/expenses/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Expense not found"
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("amount", 0),
        ("amount", -100),
        ("title", ""),
        ("title", "   "),
        ("category", ""),
        ("category", "   "),
        ("date", "not-a-date"),
    ],
)
def test_invalid_expense_is_rejected(field, value):
    payload = valid_expense(**{field: value})

    response = client.post("/expenses", json=payload)

    assert response.status_code == 422


def test_title_and_category_are_trimmed():
    response = client.post(
        "/expenses",
        json=valid_expense(
            title="   Lunch   ",
            category="   Food   ",
        ),
    )

    assert response.status_code == 201

    body = response.json()
    assert body["title"] == "Lunch"
    assert body["category"] == "Food"


def test_id_generation_remains_unique_after_deletion():
    first = client.post(
        "/expenses",
        json=valid_expense(title="First"),
    ).json()

    second = client.post(
        "/expenses",
        json=valid_expense(title="Second"),
    ).json()

    third = client.post(
        "/expenses",
        json=valid_expense(title="Third"),
    ).json()

    client.delete(f"/expenses/{second['id']}")

    fourth = client.post(
        "/expenses",
        json=valid_expense(title="Fourth"),
    ).json()

    assert first["id"] == 1
    assert third["id"] == 3
    assert fourth["id"] == 4