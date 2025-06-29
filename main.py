import pandas as pd
from src.services import investment_bank, find_phone_transactions, analyze_cashback_categories
from src.reports import spending_by_weekday

def main():
    # Пример данных
    transactions = [
        {"Дата операции": "2024-06-01", "Сумма операции": -1712, "Категория": "Продукты", "Описание": "Покупка"},
        {"Дата операции": "2024-06-15", "Сумма операции": -2050, "Категория": "Транспорт", "Описание": "Оплата проезда +7 921 111-22-33"},
        {"Дата операции": "2024-05-20", "Сумма операции": -900, "Категория": "Рестораны", "Описание": "Обед"},
        {"Дата операции": "2024-06-10", "Сумма операции": 500, "Категория": "Доход", "Описание": "Зарплата"},
        {"Дата операции": "2024-06-03", "Сумма операции": -350, "Категория": "Продукты", "Описание": "Магазин"},
    ]

    print("=== Инвесткопилка ===")
    invested = investment_bank("2024-06", transactions, 50)
    print(f"Отложено: {invested} ₽\n")

    print("=== Поиск транзакций с телефонами ===")
    phones_json = find_phone_transactions(transactions)
    print(phones_json, "\n")

    print("=== Анализ кешбэка по категориям ===")
    cashback_json = analyze_cashback_categories(transactions, 2024, 6)
    print(cashback_json, "\n")

    print("=== Траты по дням недели ===")
    # Для отчета создадим DataFrame
    df = pd.DataFrame(transactions)
    spend_by_day_df = spending_by_weekday(df, "2024-06-30")
    print(spend_by_day_df)


if __name__ == "__main__":
    main()
