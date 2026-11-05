"""Deterministic parsing of calendar dates and relative date expressions."""

import calendar
import re
from datetime import date, timedelta

_WEEKDAYS = {name.lower(): index for index, name in enumerate(calendar.day_name)}
_MONTHS = {
    name.lower(): index
    for names in (calendar.month_name, calendar.month_abbr)
    for index, name in enumerate(names)
    if name
}
_MONTHS.update(
    {
        f"{name.lower()}.": index
        for index, name in enumerate(calendar.month_abbr)
        if name
    }
)
_SMALL = dict(
    zip(
        [
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
        ],
        range(20),
        strict=True,
    )
)
_TENS = dict(
    zip(
        ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"],
        range(20, 100, 10),
        strict=True,
    )
)


def _number(text: str) -> int:
    if text.isdecimal():
        return int(text)
    if text in {"a", "an"}:
        return 1
    words = text.replace("-", " ").split()
    total = current = 0
    previous = ""
    for word in words:
        if word == "and" and previous in {"hundred", "thousand"}:
            pass
        elif word in _SMALL and (
            not previous
            or previous in _TENS
            or previous in {"hundred", "thousand", "and"}
        ):
            if previous in _TENS and _SMALL[word] not in range(1, 10):
                raise ValueError("Invalid written number")
            current += _SMALL[word]
        elif word in _TENS and (
            not previous or previous in {"hundred", "thousand", "and"}
        ):
            current += _TENS[word]
        elif word == "hundred" and previous in _SMALL and 1 <= current <= 9:
            current *= 100
        elif word == "thousand" and current and not total:
            total, current = current * 1000, 0
        else:
            raise ValueError("Invalid written number")
        previous = word
    if not words or previous == "and":
        raise ValueError("Invalid written number")
    return total + current


def _duration(text: str) -> dict[str, int]:
    amounts: dict[str, int] = {}
    pattern = r"(.+?)\s+(days?|weeks?|months?|years?)(?=[\s,]|$)"
    position = 0
    for match in re.finditer(pattern, text):
        if match.start() != position:
            raise ValueError("Invalid duration")
        quantity = match[1].strip()
        if position:
            quantity = re.sub(r"^(?:and\s+|,\s*(?:and\s+)?)", "", quantity)
        unit = match[2].rstrip("s")
        amounts[unit] = amounts.get(unit, 0) + _number(quantity)
        position = match.end()
    if not amounts or text[position:].strip():
        raise ValueError("Invalid duration")
    return amounts


def _shift(base: date, amounts: dict[str, int], direction: int) -> date:
    months = direction * (amounts.get("year", 0) * 12 + amounts.get("month", 0))
    year, month = divmod(base.year * 12 + base.month - 1 + months, 12)
    month += 1
    if not 1 <= year <= 9999:
        raise ValueError("Date out of range")
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day) + timedelta(
        days=direction * (amounts.get("day", 0) + 7 * amounts.get("week", 0))
    )


def _parse(text: str, reference: date) -> date:
    if text in {"today", "now", "tomorrow", "yesterday"}:
        return reference + timedelta(
            days={"today": 0, "now": 0, "tomorrow": 1, "yesterday": -1}[text]
        )

    if match := re.fullmatch(
        r"(?:(next|last|this) )?(" + "|".join(_WEEKDAYS) + r")", text
    ):
        modifier, weekday = match.groups()
        difference = _WEEKDAYS[weekday] - reference.weekday()
        if modifier == "next":
            difference = difference % 7 or 7
        elif modifier == "last":
            difference = -((-difference) % 7 or 7)
        elif modifier is None:
            difference %= 7
        # "This" selects the weekday in the reference's Monday–Sunday week.
        return reference + timedelta(days=difference)

    if match := re.fullmatch(r"in (.+)", text):
        return _shift(reference, _duration(match[1]), 1)
    if match := re.fullmatch(r"(.+) (ago|later|hence)", text):
        return _shift(reference, _duration(match[1]), -1 if match[2] == "ago" else 1)
    if match := re.fullmatch(r"(.+?) (before|after|from) (.+)", text):
        return _shift(
            _parse(match[3], reference),
            _duration(match[1]),
            -1 if match[2] == "before" else 1,
        )
    if match := re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text):
        return date(int(match[1]), int(match[2]), int(match[3]))
    if match := re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", text):
        return date(int(match[1]), int(match[2]), int(match[3]))
    if match := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text):
        return date(int(match[3]), int(match[1]), int(match[2]))

    # English month names are explicit, so parsing is independent of OS locale.
    cleaned = re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", text).replace(",", "")
    if match := re.fullmatch(r"([a-z]+\.?) (\d{1,2})(?: (\d{4}))?", cleaned):
        month, day, year = match.groups()
    elif match := re.fullmatch(r"(\d{1,2}) ([a-z]+\.?)(?: (\d{4}))?", cleaned):
        day, month, year = match.groups()
    else:
        raise ValueError("Unrecognized expression")
    if month not in _MONTHS:
        raise ValueError("Unknown month")
    return date(int(year) if year else reference.year, _MONTHS[month], int(day))


def parse(s: str, today: date | None = None) -> date:
    """Parse an English date relative to ``today`` (default: the local date).

    Numeric slash dates accept year/month/day and month/day/year, with a
    four-digit year and one- or two-digit months and days.
    Abbreviated month names accept an optional trailing period.
    Next/last weekdays are strictly
    future/past; this weekday belongs to the current Monday–Sunday week.
    Month/year offsets clamp to the last valid day of the destination month,
    then apply week/day offsets. Invalid or out-of-range dates raise ValueError.
    """
    if not isinstance(s, str) or not s.strip():
        raise ValueError(f"Unrecognized date: {s!r}")
    try:
        return _parse(
            " ".join(s.lower().split()), today if today is not None else date.today()
        )
    except (ValueError, OverflowError, RecursionError) as error:
        raise ValueError(f"Unrecognized or invalid date: {s!r}") from error
