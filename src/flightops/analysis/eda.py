"""Reusable exploratory analysis for canonical flight data."""

from __future__ import annotations

from typing import Any

import pandas as pd


def modeling_population_mask(
    frame: pd.DataFrame,
) -> pd.Series:
    """Return rows eligible for departure-delay modeling."""

    required = {
        "cancelled",
        "departure_delay_minutes",
    }

    missing = sorted(
        required.difference(frame.columns)
    )

    if missing:
        raise ValueError(
            "Modeling population requires columns: "
            f"{', '.join(missing)}"
        )

    cancelled = pd.to_numeric(
        frame["cancelled"],
        errors="coerce",
    )

    delay = pd.to_numeric(
        frame["departure_delay_minutes"],
        errors="coerce",
    )

    return cancelled.eq(0) & delay.notna()


def overview_summary(
    frame: pd.DataFrame,
) -> dict[str, Any]:
    """Build high-level EDA metrics."""

    required = {
        "cancelled",
        "departure_delay_minutes",
    }

    missing = sorted(
        required.difference(frame.columns)
    )

    if missing:
        raise ValueError(
            "EDA overview requires columns: "
            f"{', '.join(missing)}"
        )

    cancelled = pd.to_numeric(
        frame["cancelled"],
        errors="coerce",
    )

    delay = pd.to_numeric(
        frame["departure_delay_minutes"],
        errors="coerce",
    )

    operated_mask = cancelled.eq(0)
    cancelled_mask = cancelled.eq(1)

    modeling_mask = (
        operated_mask
        & delay.notna()
    )

    modeling_delay = delay[
        modeling_mask
    ]

    delayed_mask = (
        modeling_delay >= 15
    )

    modeling_rows = int(
        modeling_mask.sum()
    )

    delayed_rows = int(
        delayed_mask.sum()
    )

    on_time_rows = (
        modeling_rows - delayed_rows
    )

    delay_rate = (
        float(delayed_rows / modeling_rows)
        if modeling_rows
        else 0.0
    )

    return {
        "total_rows": len(frame),
        "operated_rows": int(
            operated_mask.sum()
        ),
        "cancelled_rows": int(
            cancelled_mask.sum()
        ),
        "unknown_cancellation_rows": int(
            (
                ~operated_mask
                & ~cancelled_mask
            ).sum()
        ),
        "modeling_rows": modeling_rows,
        "delayed_15min_rows": delayed_rows,
        "on_time_rows": on_time_rows,
        "delay_rate_15min": round(
            delay_rate,
            6,
        ),
        "mean_departure_delay_minutes": (
            round(
                float(modeling_delay.mean()),
                3,
            )
            if modeling_rows
            else None
        ),
        "median_departure_delay_minutes": (
            round(
                float(modeling_delay.median()),
                3,
            )
            if modeling_rows
            else None
        ),
        "p90_departure_delay_minutes": (
            round(
                float(
                    modeling_delay.quantile(
                        0.90
                    )
                ),
                3,
            )
            if modeling_rows
            else None
        ),
    }


def delay_by_group(
    frame: pd.DataFrame,
    group_column: str,
    min_flights: int = 1,
) -> pd.DataFrame:
    """Summarize departure delay by a grouping column."""

    required = {
        group_column,
        "cancelled",
        "departure_delay_minutes",
    }

    missing = sorted(
        required.difference(frame.columns)
    )

    if missing:
        raise ValueError(
            "Grouped delay analysis requires "
            f"columns: {', '.join(missing)}"
        )

    modeling_mask = (
        modeling_population_mask(frame)
    )

    delay = pd.to_numeric(
        frame["departure_delay_minutes"],
        errors="coerce",
    )

    group_values = frame[
        group_column
    ]

    valid_mask = (
        modeling_mask
        & group_values.notna()
    )

    work = pd.DataFrame(
        {
            group_column: group_values[
                valid_mask
            ],
            "departure_delay_minutes": (
                delay[valid_mask]
            ),
        }
    )

    work["delayed_15min"] = (
        work["departure_delay_minutes"]
        >= 15
    ).astype(int)

    summary = (
        work.groupby(
            group_column,
            dropna=False,
        )
        .agg(
            flights=(
                "departure_delay_minutes",
                "size",
            ),
            delayed_15min=(
                "delayed_15min",
                "sum",
            ),
            mean_delay_minutes=(
                "departure_delay_minutes",
                "mean",
            ),
            median_delay_minutes=(
                "departure_delay_minutes",
                "median",
            ),
        )
        .reset_index()
    )

    summary["delay_rate_15min"] = (
        summary["delayed_15min"]
        / summary["flights"]
    )

    summary = summary[
        summary["flights"]
        >= min_flights
    ].copy()

    summary[
        "delay_rate_15min"
    ] = summary[
        "delay_rate_15min"
    ].round(6)

    summary[
        "mean_delay_minutes"
    ] = summary[
        "mean_delay_minutes"
    ].round(3)

    summary[
        "median_delay_minutes"
    ] = summary[
        "median_delay_minutes"
    ].round(3)

    return summary.sort_values(
        [
            "delay_rate_15min",
            "flights",
        ],
        ascending=[
            False,
            False,
        ],
    ).reset_index(drop=True)


def _hhmm_to_hour(
    value: object,
) -> object:
    """Convert BTS HHMM time into scheduled departure hour."""

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


def add_departure_hour(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Add scheduled departure hour from HHMM time."""

    if "scheduled_departure" not in frame:
        raise ValueError(
            "scheduled_departure column is required"
        )

    output = frame.copy()

    output[
        "scheduled_departure_hour"
    ] = (
        output["scheduled_departure"]
        .map(_hhmm_to_hour)
        .astype("Int64")
    )

    return output


def departure_hour_summary(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize delays by scheduled departure hour."""

    enriched = add_departure_hour(
        frame
    )

    summary = delay_by_group(
        enriched,
        "scheduled_departure_hour",
    )

    return summary.sort_values(
        "scheduled_departure_hour"
    ).reset_index(drop=True)


def daily_delay_summary(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize departure delays by flight date."""

    summary = delay_by_group(
        frame,
        "flight_date",
    )

    return summary.sort_values(
        "flight_date"
    ).reset_index(drop=True)