import json

import pandas as pd

from src.reports import spending_by_weekday


def test_spending_by_weekday_basic() -> None:
    data = {
        "Дата операции": [
            "2024-06-01",
            "2024-06-02",
            "2024-06-03",
            "2024-05-25",
            "2024-05-26",
            "2024-04-30",
            "2024-06-01",
        ],
        "Сумма операции": [-1000, -2000, -1500, -500, -800, -300, 1000],
    }
    df = pd.DataFrame(data)

    result_json = spending_by_weekday(df, "2024-06-03")
    result = json.loads(result_json)

    # Проверяем ключи дней недели (на русском)
    expected_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    assert all(day in result for day in expected_days)

    # Проверяем, что суммы положительные
    assert all(v >= 0 for v in result.values())

    # Проверяем, что доход (положительная сумма) не учтен
    assert result["суббота"] < 1000
