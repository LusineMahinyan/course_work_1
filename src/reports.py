import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """
    Рассчитывает средние траты по каждому дню недели за последние 3 месяца от указанной даты.
    Если дата не указана, берется текущая дата.
    """
    logging.info(f"Запуск отчёта 'Траты по дням недели' с датой: {date or 'текущая дата'}")

    if date is None:
        end_date = datetime.today()
    else:
        try:
            end_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            logging.error("Неверный формат даты. Используйте YYYY-MM-DD.")
            raise

    start_date = end_date - timedelta(days=90)

    if not pd.api.types.is_datetime64_any_dtype(transactions["Дата операции"]):
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], errors="coerce")

    filtered = transactions[
        (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
    ]

    filtered = filtered[filtered["Сумма операции"] < 0]

    filtered["День недели"] = filtered["Дата операции"].dt.day_name(locale="ru_RU.UTF-8")

    avg_spending = filtered.groupby("День недели")["Сумма операции"].mean().abs()

    weekdays_order = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    avg_spending.index = avg_spending.index.str.lower()
    avg_spending = avg_spending.reindex(weekdays_order).fillna(0)

    result = avg_spending.round(2).to_dict()

    logging.info(f"Средние траты по дням недели: {result}")

    return json.dumps(result, ensure_ascii=False)
