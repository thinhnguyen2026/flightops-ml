"""Build leakage-safe modeling datasets from canonical flight data."""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

TARGET_COLUMN: Final[str] = "departure_delay_15min"
MODEL_FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    "carrier",
    "origin",
    "destination",
    "route",
    "day_of_week",
    "scheduled_departure_hour",
    "scheduled_departure_hour_sin",
    "scheduled_departure_hour_cos",
    "scheduled_arrival_hour",
    "scheduled_elapsed_minutes",
    "distance_miles",
)

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

def hhmm_to_hour(
    value: object,
) -> object:
    """Convert a BTS HHMM scheduled time into an hour."""

    if pd.isna(value):
        return pd.NA

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return pd.NA

    if not numeric.is_integer():
        return pd.NA

    hhmm = int(numeric)

    if hhmm == 2400:
        return 0

    if (
        hhmm < 0
        or hhmm > 2359
        or hhmm % 100 >= 60
    ):
        return pd.NA

    return hhmm // 100

def add_scheduled_features(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Create leakage-safe features from scheduled information."""

    output = frame.copy()

    output["route"] = (
        output["origin"]
        .astype("string")
        .str.cat(
            output[
                "destination"
            ].astype("string"),
            sep="->",
        )
    )

    output[
        "scheduled_departure_hour"
    ] = (
        output[
            "scheduled_departure"
        ]
        .map(hhmm_to_hour)
        .astype("Int64")
    )

    output[
        "scheduled_arrival_hour"
    ] = (
        output[
            "scheduled_arrival"
        ]
        .map(hhmm_to_hour)
        .astype("Int64")
    )

    departure_hour = pd.to_numeric(
        output[
            "scheduled_departure_hour"
        ],
        errors="coerce",
    )

    radians = (
        2
        * np.pi
        * departure_hour
        / 24
    )

    output[
        "scheduled_departure_hour_sin"
    ] = np.sin(radians)

    output[
        "scheduled_departure_hour_cos"
    ] = np.cos(radians)

    output["day_of_week"] = (
        pd.to_numeric(
            output["day_of_week"],
            errors="coerce",
        )
    )

    output[
        "scheduled_elapsed_minutes"
    ] = pd.to_numeric(
        output[
            "scheduled_elapsed_minutes"
        ],
        errors="coerce",
    )

    output["distance_miles"] = (
        pd.to_numeric(
            output["distance_miles"],
            errors="coerce",
        )
    )

    return output

def build_modeling_dataset(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Build leakage-safe feature matrix plus target."""

    population = (
        build_modeling_population(
            frame
        )
    )

    featured = add_scheduled_features(
        population
    )

    columns = [
        "flight_date",
        *MODEL_FEATURE_COLUMNS,
        TARGET_COLUMN,
    ]

    return featured.loc[
        :,
        columns,
    ].copy()