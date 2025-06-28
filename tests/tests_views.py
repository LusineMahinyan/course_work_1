from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch, Mock

import pandas as pd

from src import views


def test_get_greeting() -> None:
    assert views.get_greeting(datetime(2024, 1, 1, 6)) == "Доброе утро"
    assert views.get_greeting(datetime(2024, 1, 1, 13)) == "Добрый день"
    assert views.get_greeting(datetime(2024, 1, 1, 19)) == "Добрый вечер"
    assert views.get_greeting(datetime(2024, 1, 1, 3)) == "Доброй ночи"


def test_get_card_stats() -> None:
    data = {"card": ["*12345678", "*12345678", "*87654321"], "amount": [-150.0, -50.0, -250.0]}
    df = pd.DataFrame(data)
    result = views.get_card_stats(df)
    expected = [
        {"last_digits": "5678", "total_spent": 200.0, "cashback": 2},
        {"last_digits": "4321", "total_spent": 250.0, "cashback": 2},
    ]
    assert result == expected


def test_get_top_transactions() -> None:
    data = {
        "date": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")],
        "payment_amount": [100, -300, 50],
        "category": ["A", "B", "C"],
        "description": ["desc1", "desc2", "desc3"],
    }
    df = pd.DataFrame(data)
    result = views.get_top_transactions(df)
    expected_dates = ["02.01.2024", "01.01.2024", "03.01.2024"]
    assert [item["date"] for item in result] == expected_dates


def test_filter_operations_by_date(tmp_path: Path) -> None:
    csv_content = """Дата операции,Сумма операции,Сумма платежа,Категория,Описание,Номер карты
01.06.2024,-100,-100,TestCat,desc1,*1234
15.06.2024,-200,-200,TestCat,desc2,*1234
20.07.2024,-300,-300,TestCat,desc3,*1234
"""
    file = tmp_path / "ops.csv"
    file.write_text(csv_content, encoding="utf-8")

    df = views.filter_operations_by_date("2024-06-15", filepath=str(file))
    assert all(df["date"] >= pd.Timestamp("2024-06-01"))
    assert all(df["date"] <= pd.Timestamp("2024-06-15"))
    assert len(df) == 2


@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": ["AAPL"]}')
@patch("src.views.requests.get")
def test_get_stock_prices(mock_requests_get: Mock, _: Mock) -> None:
    mock_requests_get.return_value.json.return_value = {"Global Quote": {"05. price": "150.12"}}
    result = views.get_stock_prices(api_key="test_api_key")
    assert result == [{"stock": "AAPL", "price": 150.12}]


@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD"]}')
@patch("src.views.requests.get")
def test_get_currency_rates(mock_requests_get: Mock, _: Mock) -> None:
    mock_requests_get.return_value.json.return_value = {"rates": {"USD": 0.013}}
    result = views.get_currency_rates()
    assert result == [{"currency": "USD", "rate": 76.92}]
