"""Tests for flight data-quality checks."""

import json
from pathlib import Path

import pandas as pd

from flightops.data.quality import (
    basic_quality_summary,
    target_consistency_summary,
)
from flightops.data.quality_report import (
    write_quality_reports,
)


def test_basic_quality_summary() -> None:
    """Structural checks detect bad values."""

    frame = pd.DataFrame(
        {
            "origin": [
                "JFK",
                "JFK",
                "BAD1",
                None,
            ],
            "destination": [
                "LAX",
                "LAX",
                "SEA",
                "BOS",
            ],
            "scheduled_departure": [
                800,
                800,
                2461,
                930,
            ],
            "value": [
                1.0,
                1.0,
                3.0,
                None,
            ],
        }
    )

    summary = basic_quality_summary(
        frame
    )

    assert summary["duplicate_rows"] == 1

    assert (
        summary[
            "invalid_airport_codes"
        ]["origin"]
        == 1
    )

    assert (
        summary[
            "invalid_scheduled_departure_times"
        ]
        == 1
    )

    assert (
        summary[
            "missing_by_column"
        ]["value"]
        == 1
    )


def test_target_consistency_summary() -> None:
    """Derived target is checked against BTS."""

    frame = pd.DataFrame(
        {
            "departure_delay_minutes": [
                20.0,
                0.0,
                20.0,
                None,
                None,
            ],
            "bts_departure_delay_15min": [
                1.0,
                0.0,
                0.0,
                None,
                1.0,
            ],
            "cancelled": [
                0.0,
                0.0,
                0.0,
                1.0,
                None,
            ],
        }
    )

    summary = (
        target_consistency_summary(
            frame
        )
    )

    assert summary["operated_rows"] == 3
    assert summary["cancelled_rows"] == 1

    assert (
        summary[
            "unknown_cancellation_rows"
        ]
        == 1
    )

    assert (
        summary[
            "comparable_target_rows"
        ]
        == 3
    )

    assert (
        summary["target_mismatches"]
        == 1
    )


def test_write_quality_reports(
    tmp_path: Path,
) -> None:
    """Reporter writes JSON and Markdown."""

    frame = pd.DataFrame(
        {
            "origin": [
                "JFK",
                "ATL",
            ],
            "destination": [
                "LAX",
                "BOS",
            ],
            "scheduled_departure": [
                800,
                930,
            ],
            "departure_delay_minutes": [
                20.0,
                0.0,
            ],
            "bts_departure_delay_15min": [
                1.0,
                0.0,
            ],
            "cancelled": [
                0.0,
                0.0,
            ],
        }
    )

    input_path = (
        tmp_path / "flights.parquet"
    )

    output_dir = (
        tmp_path / "reports"
    )

    frame.to_parquet(
        input_path,
        index=False,
    )

    json_path, markdown_path = (
        write_quality_reports(
            input_path,
            output_dir,
        )
    )

    assert json_path.exists()
    assert markdown_path.exists()

    report = json.loads(
        json_path.read_text(
            encoding="utf-8"
        )
    )

    assert report["row_count"] == 2

    assert (
        report[
            "target_consistency"
        ]["target_mismatches"]
        == 0
    )