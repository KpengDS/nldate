"""Regression tests for relative expressions with an implicit one-day offset."""

from datetime import date

import pytest

from nldate import parse


@pytest.mark.parametrize(
    ("reference", "expected"),
    [
        (date(2026, 11, 4), date(2026, 11, 6)),
        (date(2025, 12, 30), date(2026, 1, 1)),
        (date(2024, 2, 27), date(2024, 2, 29)),
        (date(2024, 2, 28), date(2024, 3, 1)),
        (date(2025, 2, 27), date(2025, 3, 1)),
    ],
)
def test_the_day_after_tomorrow(reference: date, expected: date) -> None:
    assert parse("the day after tomorrow", reference) == expected


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("  THE   DAY AFTER Tomorrow  ", date(2026, 11, 6)),
        ("the day before yesterday", date(2026, 11, 2)),
        ("the day after today", date(2026, 11, 5)),
        ("the day before December 1st, 2025", date(2025, 11, 30)),
        ("two weeks from the day after tomorrow", date(2026, 11, 20)),
    ],
)
def test_implicit_day_offset(expression: str, expected: date) -> None:
    assert parse(expression, date(2026, 11, 4)) == expected


@pytest.mark.parametrize(
    "expression",
    ["the day after", "the day after nonsense", "the days after tomorrow"],
)
def test_invalid_implicit_day_offset(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression, date(2026, 11, 4))


def test_implicit_day_offset_overflow() -> None:
    with pytest.raises(ValueError):
        parse("the day after tomorrow", date(9999, 12, 30))
