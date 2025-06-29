import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму отложенных средств в «Инвесткопилку» за указанный месяц.

    :param month: Строка в формате 'YYYY-MM', например '2024-06'
    :param transactions: список словарей с транзакциями, где есть поля:
        - 'Дата операции' (str, 'YYYY-MM-DD')
        - 'Сумма операции' (число)
    :param limit: шаг округления (например, 10, 50, 100)
    :return: сумма отложенных рублей (float)
    """
    logging.info(f"Запуск расчёта Инвесткопилки для месяца {month} с лимитом округления {limit} ₽")

    filtered = filter(
        lambda t: t.get("Дата операции", "").startswith(month),
        transactions,
    )

    def rounding_diff(amount: float) -> float:
        if amount >= 0:
            return 0.0
        abs_amount = abs(amount)
        rounded = ((abs_amount + limit - 1) // limit) * limit
        diff = rounded - abs_amount
        logging.debug(f"Трата: {abs_amount}, округление до {rounded}, откладываем {diff}")
        return diff

    diffs = map(lambda t: rounding_diff(t["Сумма операции"]), filtered)
    total = round(sum(diffs), 2)

    logging.info(f"Итоговая сумма Инвесткопилки за {month}: {total} ₽")
    return total


def investment_bank_json(month: str, transactions: List[Dict[str, Any]], limit: int) -> str:
    """Возвращает JSON с результатом работы investment_bank"""
    total = investment_bank(month, transactions, limit)
    response = {
        "month": month,
        "limit": limit,
        "invested": total,
    }
    return json.dumps(response, ensure_ascii=False, indent=2)


def find_phone_transactions(transactions: List[Dict[str, Any]]) -> str:
    """
    Возвращает JSON со всеми транзакциями, в которых в поле 'Описание' указан номер телефона.
    """
    pattern = re.compile(r"\+7[\s\-]?\d{3}[\s\-]?\d{2,3}[\s\-]?\d{2}[\s\-]?\d{2}")
    logging.info("Начат поиск транзакций с номерами телефонов")

    result = [transaction for transaction in transactions if pattern.search(str(transaction.get("Описание", "")))]

    logging.info(f"Найдено {len(result)} транзакций с номерами телефонов")
    return json.dumps(result, ensure_ascii=False, indent=2)


logging.basicConfig(level=logging.INFO)


def analyze_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> str:
    """
    Анализирует транзакции по категориям и возвращает JSON с суммой расходов по каждой категории
    для заданного месяца и года.
    """
    logging.info(f"Старт анализа кешбэка за {year}-{month:02}")

    filtered = filter(
        lambda transaction: isinstance(transaction.get("Дата операции"), str)
        and datetime.strptime(transaction["Дата операции"], "%Y-%m-%d").year == year
        and datetime.strptime(transaction["Дата операции"], "%Y-%m-%d").month == month,
        data,
    )

    cashback_by_category: Dict[str, float] = {}

    for tx in filtered:
        amount = tx.get("Сумма операции", 0)
        category = tx.get("Категория", "Без категории")

        if amount < 0:  # Учитываем только расходы
            cashback_by_category[category] = cashback_by_category.get(category, 0) + abs(amount)

    logging.info(f"Кешбэк по категориям: {cashback_by_category}")

    return json.dumps(cashback_by_category, ensure_ascii=False)


if __name__ == "__main__":
    example_transactions = [
        {"Дата операции": "2024-06-01", "Сумма операции": -1712},
        {"Дата операции": "2024-06-02", "Сумма операции": -349},
        {"Дата операции": "2024-06-03", "Сумма операции": -489},
        {"Дата операции": "2024-07-01", "Сумма операции": -2100},
        {"Дата операции": "2024-06-15", "Сумма операции": 500},
    ]
    print(investment_bank_json("2024-06", example_transactions, 50))
