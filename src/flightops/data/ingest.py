"""Utilities for ingesting BTS monthly flight data."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

from flightops.data.columns import BTS_COLUMN_MAP
from flightops.data.schema import validate_columns


def read_bts_zip(path: Path) -> pd.DataFrame:
    """Read a BTS monthly ZIP and normalize known source columns."""

    if not path.exists():
        raise FileNotFoundError(f"BTS ZIP not found: {path}")

    if path.suffix.lower() != ".zip":
        raise ValueError(f"Expected a .zip file, got: {path.name}")

    with zipfile.ZipFile(path) as archive:
        csv_members = [
            name
            for name in archive.namelist()
            if name.lower().endswith(".csv")
        ]

        if not csv_members:
            raise ValueError(
                f"No CSV file found inside {path.name}"
            )

        if len(csv_members) > 1:
            raise ValueError(
                f"Expected one CSV inside {path.name}, "
                f"found {len(csv_members)}"
            )

        with archive.open(csv_members[0]) as csv_file:
            frame = pd.read_csv(
                csv_file,
                low_memory=False,
            )

    frame.columns = [
        str(column).strip()
        for column in frame.columns
    ]

    known_source_columns = [
        column
        for column in BTS_COLUMN_MAP
        if column in frame.columns
    ]

    frame = frame.loc[:, known_source_columns].rename(
        columns=BTS_COLUMN_MAP
    )

    validation = validate_columns(
        frame.columns.tolist()
    )

    if not validation.ok:
        missing = ", ".join(
            validation.missing_columns
        )

        raise ValueError(
            "Missing required canonical columns "
            f"after ingestion: {missing}"
        )

    return frame