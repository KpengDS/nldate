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


@pytest.mark.parametrize(
    ("month", "name"),
    list(
        enumerate(
            (
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ),
            start=1,
        )
    ),
)
@pytest.mark.parametrize("period", ["", "."])
@pytest.mark.parametrize("day_first", [False, True])
def test_abbreviated_months(
    month: int, name: str, period: str, day_first: bool
) -> None:
    expression = (
        f"1st {name}{period}, 2025" if day_first else f"{name}{period} 1st, 2025"
    )
    assert parse(expression) == date(2025, month, 1)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("Dec. 1, 2025", date(2025, 12, 1)),
        ("  DEC.   1, 2025  ", date(2025, 12, 1)),
        ("Dec. 1", date(2030, 12, 1)),
        ("1 Dec.", date(2030, 12, 1)),
        ("Feb. 29, 2024", date(2024, 2, 29)),
        ("5 days before Dec. 1, 2025", date(2025, 11, 26)),
        ("one month after Jan. 31, 2024", date(2024, 2, 29)),
        ("December 1st, 2025", date(2025, 12, 1)),
    ],
)
def test_dotted_month_expressions(expression: str, expected: date) -> None:
    assert parse(expression, date(2030, 6, 15)) == expected


@pytest.mark.parametrize(
    "expression",
    ["Dec.. 1, 2025", "D.ec 1, 2025", "Abc. 1, 2025", "Feb. 29, 2025", "Dec. 32, 2025"],
)
def test_invalid_dotted_month_dates(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression)
