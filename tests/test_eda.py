"""Tests for exploratory flight analysis."""

import json
from pathlib import Path

import pandas as pd

from flightops.analysis.eda import (
    add_departure_hour,
    delay_by_group,
    overview_summary,
)
from flightops.analysis.eda_report import (
    write_eda_outputs,
)


def example_frame() -> pd.DataFrame:
    """Return a compact flight dataset for EDA tests."""

    return pd.DataFrame(
        {
            "flight_date": [
                "2025-01-01",
                "2025-01-01",
                "2025-01-02",
                "2025-01-02",
                "2025-01-03",
                "2025-01-03",
            ],
            "carrier": [
                "AA",
                "AA",
                "DL",
                "DL",
                "AA",
                "DL",
            ],
            "origin": [
                "JFK",
                "JFK",
                "ATL",
                "ATL",
                "JFK",
                "ATL",
            ],
            "scheduled_departure": [
                800,
                900,
                1400,
                1500,
                2400,
                2365,
            ],
            "departure_delay_minutes": [
                20.0,
                0.0,
                30.0,
                10.0,
                5.0,
                None,
            ],
            "cancelled": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
            ],
        }
    )


def test_overview_summary() -> None:
    """Overview calculates modeling population."""

    summary = overview_summary(
        example_frame()
    )

    assert summary["total_rows"] == 6
    assert summary["operated_rows"] == 5
    assert summary["cancelled_rows"] == 1
    assert summary["modeling_rows"] == 5
    assert summary["delayed_15min_rows"] == 2
    assert summary["delay_rate_15min"] == 0.4


def test_delay_by_group() -> None:
    """Grouped analysis computes carrier rates."""

    summary = delay_by_group(
        example_frame(),
        "carrier",
    )

    aa = summary[
        summary["carrier"] == "AA"
    ].iloc[0]

    assert aa["flights"] == 3
    assert aa["delayed_15min"] == 1
    assert aa["delay_rate_15min"] == 0.333333


def test_add_departure_hour() -> None:
    """Scheduled HHMM values convert to hours."""

    output = add_departure_hour(
        example_frame()
    )

    assert (
        output.loc[
            0,
            "scheduled_departure_hour",
        ]
        == 8
    )

    assert (
        output.loc[
            4,
            "scheduled_departure_hour",
        ]
        == 0
    )

    assert pd.isna(
        output.loc[
            5,
            "scheduled_departure_hour",
        ]
    )


def test_write_eda_outputs(
    tmp_path: Path,
) -> None:
    """EDA reporter writes expected artifacts."""

    input_path = (
        tmp_path / "flights.parquet"
    )

    output_dir = (
        tmp_path / "eda"
    )

    example_frame().to_parquet(
        input_path,
        index=False,
    )

    paths = write_eda_outputs(
        input_path,
        output_dir,
    )

    assert len(paths) == 6

    for path in paths:
        assert path.exists()

    overview_path = (
        output_dir
        / "flights.overview.json"
    )

    overview = json.loads(
        overview_path.read_text(
            encoding="utf-8"
        )
    )

    assert overview["total_rows"] == 6
    assert overview["modeling_rows"] == 5
    assert overview["delay_rate_15min"] == 0.4