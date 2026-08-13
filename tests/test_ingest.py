"""Tests for BTS monthly ingestion."""

import json
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from flightops.data.ingest import (
    ingest_month,
    read_bts_zip,
)


def write_bts_zip(
    path: Path,
    drop_column: str | None = None,
) -> None:
    """Create a synthetic BTS-style ZIP for testing."""

    frame = pd.DataFrame(
        {
            "FlightDate": [
                "2025-01-01",
                "2025-01-02",
            ],
            "Year": [
                2025,
                2025,
            ],
            "Month": [
                1,
                1,
            ],
            "Reporting_Airline": [
                "AA",
                "DL",
            ],
            "Origin": [
                "JFK",
                "ATL",
            ],
            "Dest": [
                "LAX",
                "BOS",
            ],
            "CRSDepTime": [
                800,
                930,
            ],
            "DepDelayMinutes": [
                20.0,
                0.0,
            ],
            "DepDel15": [
                1.0,
                0.0,
            ],
            "Cancelled": [
                0.0,
                0.0,
            ],
        }
    )

    if drop_column is not None:
        frame = frame.drop(
            columns=[drop_column]
        )

    csv_path = path.with_suffix(".csv")

    frame.to_csv(
        csv_path,
        index=False,
    )

    with zipfile.ZipFile(
        path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.write(
            csv_path,
            arcname="bts.csv",
        )

    csv_path.unlink()


def test_read_bts_zip_normalizes_columns(
    tmp_path: Path,
) -> None:
    source = tmp_path / "bts.zip"

    write_bts_zip(source)

    frame = read_bts_zip(source)

    assert "flight_date" in frame.columns
    assert "carrier" in frame.columns

    assert (
        frame[
            "departure_delay_minutes"
        ].tolist()
        == [20.0, 0.0]
    )


def test_read_bts_zip_rejects_missing_column(
    tmp_path: Path,
) -> None:
    source = tmp_path / "bts.zip"

    write_bts_zip(
        source,
        drop_column="Origin",
    )

    with pytest.raises(
        ValueError,
        match="origin",
    ):
        read_bts_zip(source)


def test_ingest_writes_parquet_and_manifest(
    tmp_path: Path,
) -> None:
    source = tmp_path / "bts.zip"

    output_dir = (
        tmp_path / "processed"
    )

    write_bts_zip(source)

    parquet_path, manifest_path = (
        ingest_month(
            source,
            2025,
            1,
            output_dir,
        )
    )

    assert parquet_path.exists()
    assert manifest_path.exists()

    output = pd.read_parquet(
        parquet_path
    )

    assert len(output) == 2

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert manifest["year"] == 2025
    assert manifest["month"] == 1
    assert manifest["rows"] == 2

    assert (
        len(
            manifest["source_sha256"]
        )
        == 64
    )