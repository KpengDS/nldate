"""Regression coverage for explicit numeric date formats."""

from datetime import date

import pytest

from nldate import parse


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2025/12/1", date(2025, 12, 1)),
        ("2025/12/01", date(2025, 12, 1)),
        ("2025/1/2", date(2025, 1, 2)),
        ("2025/01/02", date(2025, 1, 2)),
        ("2025/1/02", date(2025, 1, 2)),
        ("2025/01/2", date(2025, 1, 2)),
        ("12/1/2025", date(2025, 12, 1)),
        ("12/01/2025", date(2025, 12, 1)),
        ("1/2/2025", date(2025, 1, 2)),
        ("01/02/2025", date(2025, 1, 2)),
        ("2025-12-01", date(2025, 12, 1)),
    ],
)
def test_numeric_date_formats(expression: str, expected: date) -> None:
    assert parse(expression, date(2030, 6, 15)) == expected


@pytest.mark.parametrize("expression", ["2024/2/29", "02/29/2024"])
def test_slash_leap_day(expression: str) -> None:
    assert parse(expression) == date(2024, 2, 29)


@pytest.mark.parametrize(
    "expression",
    [
        "2025/2/29",
        "2025/13/1",
        "2025/1/32",
        "2025/0/1",
        "2025/1/0",
        "0000/1/1",
        "02/29/2025",
        "13/01/2025",
        "2025/1",
        "25/1/2",
        "2025/001/02",
        "2025/1/2 extra",
    ],
)
def test_invalid_slash_dates(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression)


def test_relative_expression_with_slash_date() -> None:
    assert parse("5 days before 2025/12/1") == date(2025, 11, 26)
    assert parse("one month after 2024/1/31") == date(2024, 2, 29)
