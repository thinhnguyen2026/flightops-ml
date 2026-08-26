"""Build leakage-safe modeling datasets from canonical flight data."""

from __future__ import annotations

from typing import Final

import pandas as pd

TARGET_COLUMN: Final[str] = "departure_delay_15min"


BASE_REQUIRED_COLUMNS: Final[set[str]] = {
    "flight_date",
    "carrier",
    "origin",
    "destination",
    "day_of_week",
    "scheduled_departure",
    "scheduled_arrival",
    "scheduled_elapsed_minutes",
    "distance_miles",
    "cancelled",
    "departure_delay_minutes",
}


def validate_modeling_columns(
    frame: pd.DataFrame,
) -> None:
    """Ensure columns required for modeling are available."""

    missing = sorted(
        BASE_REQUIRED_COLUMNS.difference(
            frame.columns
        )
    )

    if missing:
        raise ValueError(
            "Modeling dataset is missing required columns: "
            f"{', '.join(missing)}"
        )


def build_modeling_population(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Filter to operated flights with an observed delay outcome."""

    validate_modeling_columns(frame)

    output = frame.copy()

    output["cancelled"] = pd.to_numeric(
        output["cancelled"],
        errors="coerce",
    )

    output["departure_delay_minutes"] = (
        pd.to_numeric(
            output["departure_delay_minutes"],
            errors="coerce",
        )
    )

    modeling_mask = (
        output["cancelled"].eq(0)
        & output[
            "departure_delay_minutes"
        ].notna()
    )

    output = output.loc[
        modeling_mask
    ].copy()

    output["flight_date"] = pd.to_datetime(
        output["flight_date"],
        errors="coerce",
    )

    invalid_dates = int(
        output["flight_date"].isna().sum()
    )

    if invalid_dates:
        raise ValueError(
            "Modeling population contains "
            f"{invalid_dates} invalid flight dates"
        )

    output[TARGET_COLUMN] = (
        output[
            "departure_delay_minutes"
        ]
        .ge(15)
        .astype("int8")
    )

    return output.reset_index(
        drop=True
    )