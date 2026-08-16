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