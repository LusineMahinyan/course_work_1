import json

from src.services import analyze_cashback_categories, find_phone_transactions, investment_bank


def test_investment_bank_basic() -> None:
    transactions = [
        {"Дата операции": "2024-06-01", "Сумма операции": -1712},
        {"Дата операции": "2024-06-15", "Сумма операции": -2050},
        {"Дата операции": "2024-05-20", "Сумма операции": -900},
        {"Дата операции": "2024-06-10", "Сумма операции": 500},
    ]
    result = investment_bank("2024-06", transactions, 50)
    assert result == 38


def test_investment_bank_no_transactions() -> None:
    transactions: list[dict[str, int | str]] = [
        {"Дата операции": "2024-05-20", "Сумма операции": -900},
        {"Дата операции": "2024-06-10", "Сумма операции": 500},  # доход
    ]
    result = investment_bank("2024-06", transactions, 10)
    assert result == 0


def test_investment_bank_rounding_100() -> None:
    transactions = [
        {"Дата операции": "2024-06-01", "Сумма операции": -320},
        {"Дата операции": "2024-06-05", "Сумма операции": -450},
    ]
    result = investment_bank("2024-06", transactions, 100)
    assert result == 130


def test_investment_bank_positive_transactions() -> None:
    transactions = [
        {"Дата операции": "2024-06-01", "Сумма операции": 300},
        {"Дата операции": "2024-06-02", "Сумма операции": -250},
    ]
    result = investment_bank("2024-06", transactions, 10)
    assert result == 0


def test_find_phone_transactions() -> None:
    transactions = [
        {"Дата операции": "2024-06-01", "Сумма операции": -500, "Описание": "Я МТС +7 921 11-22-33"},
        {"Дата операции": "2024-06-02", "Сумма операции": -300, "Описание": "Нет номера"},
        {"Дата операции": "2024-06-03", "Сумма операции": -450, "Описание": "Тинькофф Мобайл +7 995 555-55-55"},
    ]
    result = find_phone_transactions(transactions)
    parsed = json.loads(result)

    assert len(parsed) == 2
    assert "+7 921 11-22-33" in parsed[0]["Описание"]
    assert "+7 995 555-55-55" in parsed[1]["Описание"]


def test_analyze_cashback_categories_basic() -> None:
    data = [
        {"Дата операции": "2024-06-01", "Сумма операции": -1000, "Категория": "Категория 1"},
        {"Дата операции": "2024-06-02", "Сумма операции": -2000, "Категория": "Категория 2"},
        {"Дата операции": "2024-06-15", "Сумма операции": -500, "Категория": "Категория 1"},
        {"Дата операции": "2024-05-30", "Сумма операции": -700, "Категория": "Категория 3"},
        {"Дата операции": "2024-06-10", "Сумма операции": 300, "Категория": "Категория 1"},  # доход, не учитываем
    ]

    result_json = analyze_cashback_categories(data, 2024, 6)
    result = json.loads(result_json)

    assert isinstance(result, dict)
    assert result.get("Категория 1") == 1500  # 1000 + 500
    assert result.get("Категория 2") == 2000
    assert "Категория 3" not in result  # транзакция в мае — игнорируем


def test_analyze_cashback_categories_no_transactions() -> None:
    data = [
        {"Дата операции": "2024-05-01", "Сумма операции": -1000, "Категория": "Категория 1"},
    ]

    result_json = analyze_cashback_categories(data, 2024, 6)
    result = json.loads(result_json)
    assert result == {}


def test_analyze_cashback_categories_positive_amounts_ignored() -> None:
    data = [
        {"Дата операции": "2024-06-01", "Сумма операции": 1000, "Категория": "Категория 1"},  # доход
        {"Дата операции": "2024-06-05", "Сумма операции": -500, "Категория": "Категория 1"},
    ]

    result_json = analyze_cashback_categories(data, 2024, 6)
    result = json.loads(result_json)

    assert result.get("Категория 1") == 500
