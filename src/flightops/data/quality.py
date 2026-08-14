"""Reusable data-quality checks for canonical flight data."""

from __future__ import annotations

from typing import Any

import pandas as pd


def missing_counts(
    frame: pd.DataFrame,
) -> dict[str, int]:
    """Return missing-value counts for every column."""

    return {
        column: int(frame[column].isna().sum())
        for column in frame.columns
    }


def missing_rates(
    frame: pd.DataFrame,
) -> dict[str, float]:
    """Return missing-value rates for every column."""

    row_count = len(frame)

    if row_count == 0:
        return {
            column: 0.0
            for column in frame.columns
        }

    return {
        column: round(
            float(frame[column].isna().sum())
            / row_count,
            6,
        )
        for column in frame.columns
    }


def duplicate_row_count(
    frame: pd.DataFrame,
) -> int:
    """Count exact duplicate rows."""

    return int(frame.duplicated().sum())


def invalid_airport_code_count(
    series: pd.Series,
) -> int:
    """Count non-null values that are not 3-letter airport codes."""

    cleaned = (
        series.dropna()
        .astype(str)
        .str.strip()
    )

    valid = cleaned.str.fullmatch(
        r"[A-Z]{3}",
        na=False,
    )

    return int((~valid).sum())


def _is_valid_hhmm(value: object) -> bool:
    """Return whether a value represents a valid HHMM time."""

    if pd.isna(value):
        return True

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False

    if not numeric.is_integer():
        return False

    hhmm = int(numeric)

    if hhmm == 2400:
        return True

    if hhmm < 0 or hhmm > 2359:
        return False

    minutes = hhmm % 100

    return minutes < 60


def invalid_scheduled_departure_count(
    series: pd.Series,
) -> int:
    """Count invalid non-null scheduled departure times."""

    valid = series.map(_is_valid_hhmm)

    return int((~valid).sum())


def basic_quality_summary(
    frame: pd.DataFrame,
) -> dict[str, Any]:
    """Build structural data-quality summary."""

    row_count = len(frame)
    duplicate_rows = duplicate_row_count(frame)

    invalid_airports = {}

    for column in (
        "origin",
        "destination",
    ):
        if column in frame.columns:
            invalid_airports[column] = (
                invalid_airport_code_count(
                    frame[column]
                )
            )

    invalid_times = None

    if (
        "scheduled_departure"
        in frame.columns
    ):
        invalid_times = (
            invalid_scheduled_departure_count(
                frame[
                    "scheduled_departure"
                ]
            )
        )

    duplicate_rate = (
        round(
            duplicate_rows / row_count,
            6,
        )
        if row_count
        else 0.0
    )

    return {
        "row_count": int(row_count),
        "column_count": len(frame.columns),
        "duplicate_rows": duplicate_rows,
        "duplicate_rate": duplicate_rate,
        "missing_by_column": (
            missing_counts(frame)
        ),
        "missing_rate_by_column": (
            missing_rates(frame)
        ),
        "invalid_airport_codes": (
            invalid_airports
        ),
        "invalid_scheduled_departure_times": (
            invalid_times
        ),
    }