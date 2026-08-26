"""Tests for leakage-safe modeling dataset construction."""

from pathlib import Path

import pandas as pd

from flightops.features.build_dataset import (
    write_modeling_dataset,
)
from flightops.features.modeling import (
    TARGET_COLUMN,
    build_modeling_dataset,
    build_modeling_population,
    chronological_split,
)


def example_flights() -> pd.DataFrame:
    """Create representative synthetic flight rows."""

    dates = pd.date_range(
        "2025-01-01",
        periods=31,
        freq="D",
    )

    return pd.DataFrame(
        {
            "flight_date": dates,
            "carrier": ["AA"] * 31,
            "origin": ["JFK"] * 31,
            "destination": ["LAX"] * 31,
            "day_of_week": [
                date.dayofweek + 1
                for date in dates
            ],
            "scheduled_departure": [
                800
            ] * 31,
            "scheduled_arrival": [
                1100
            ] * 31,
            "scheduled_elapsed_minutes": [
                360.0
            ] * 31,
            "distance_miles": [
                2475.0
            ] * 31,
            "cancelled": [
                0.0
            ] * 30
            + [1.0],
            "departure_delay_minutes": [
                0.0,
                20.0,
            ]
            * 15
            + [None],
            "bts_departure_delay_15min": [
                0.0
            ] * 31,
        }
    )


def test_cancelled_flights_are_excluded() -> None:
    """Cancelled flights do not enter modeling population."""

    population = (
        build_modeling_population(
            example_flights()
        )
    )

    assert len(population) == 30

    assert (
        population["cancelled"]
        .eq(0)
        .all()
    )


def test_target_is_derived_from_delay_minutes() -> None:
    """Binary target follows the 15-minute threshold."""

    population = (
        build_modeling_population(
            example_flights()
        )
    )

    assert (
        population[
            TARGET_COLUMN
        ].sum()
        == 15
    )


def test_modeling_dataset_excludes_outcomes() -> None:
    """Feature dataset does not expose outcome columns."""

    modeling = build_modeling_dataset(
        example_flights()
    )

    prohibited = {
        "cancelled",
        "departure_delay_minutes",
        "bts_departure_delay_15min",
    }

    assert prohibited.isdisjoint(
        modeling.columns
    )

    assert "route" in modeling.columns

    assert (
        "scheduled_departure_hour"
        in modeling.columns
    )


def test_chronological_split() -> None:
    """Train, validation, and test respect date boundaries."""

    modeling = build_modeling_dataset(
        example_flights()
    )

    splits = chronological_split(
        modeling,
        train_end="2025-01-21",
        validation_end="2025-01-26",
    )

    assert (
        splits["train"][
            "flight_date"
        ].max()
        <= pd.Timestamp(
            "2025-01-21"
        )
    )

    assert (
        splits["validation"][
            "flight_date"
        ].min()
        > pd.Timestamp(
            "2025-01-21"
        )
    )

    assert (
        splits["test"][
            "flight_date"
        ].min()
        > pd.Timestamp(
            "2025-01-26"
        )
    )


def test_write_modeling_dataset(
    tmp_path: Path,
) -> None:
    """Materialization writes all split artifacts."""

    input_path = (
        tmp_path
        / "flights.parquet"
    )

    output_dir = (
        tmp_path
        / "modeling"
    )

    example_flights().to_parquet(
        input_path,
        index=False,
    )

    paths = write_modeling_dataset(
        input_path=input_path,
        output_dir=output_dir,
        train_end="2025-01-21",
        validation_end="2025-01-26",
    )

    assert len(paths) == 4

    assert (
        output_dir
        / "train.parquet"
    ).exists()

    assert (
        output_dir
        / "validation.parquet"
    ).exists()

    assert (
        output_dir
        / "test.parquet"
    ).exists()

    assert (
        output_dir
        / "split_manifest.json"
    ).exists()