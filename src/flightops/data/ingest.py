"""Utilities for ingesting BTS monthly flight data."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import pandas as pd

from flightops.data.columns import BTS_COLUMN_MAP
from flightops.data.schema import validate_columns


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a local file."""

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()

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

def validate_period(
    frame: pd.DataFrame,
    year: int,
    month: int,
) -> None:
    """Ensure source period matches the requested period."""

    if not 1 <= month <= 12:
        raise ValueError(
            "month must be between 1 and 12"
        )

    if "year" in frame.columns:
        years = set(
            frame["year"]
            .dropna()
            .astype(int)
            .unique()
        )

        if years and years != {year}:
            raise ValueError(
                f"Expected year {year}, "
                f"found {sorted(years)}"
            )

    if "month" in frame.columns:
        months = set(
            frame["month"]
            .dropna()
            .astype(int)
            .unique()
        )

        if months and months != {month}:
            raise ValueError(
                f"Expected month {month}, "
                f"found {sorted(months)}"
            )

def write_staging_outputs(
    frame: pd.DataFrame,
    source_path: Path,
    output_dir: Path,
    year: int,
    month: int,
) -> tuple[Path, Path]:
    """Write canonical parquet data and provenance manifest."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stem = f"flights_{year}_{month:02d}"

    parquet_path = (
        output_dir / f"{stem}.parquet"
    )

    manifest_path = (
        output_dir / f"{stem}.manifest.json"
    )

    frame.to_parquet(
        parquet_path,
        index=False,
    )

    manifest = {
        "source_file": source_path.name,
        "source_sha256": sha256_file(
            source_path
        ),
        "year": year,
        "month": month,
        "rows": len(frame),
        "columns": frame.columns.tolist(),
        "output_file": parquet_path.name,
    }

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return parquet_path, manifest_path

def ingest_month(
    input_path: Path,
    year: int,
    month: int,
    output_dir: Path = Path(
        "data/processed/staging"
    ),
) -> tuple[Path, Path]:
    """Run the monthly BTS ingestion pipeline."""

    if not 1 <= month <= 12:
        raise ValueError(
            "month must be between 1 and 12"
        )

    frame = read_bts_zip(input_path)

    validate_period(
        frame,
        year=year,
        month=month,
    )

    return write_staging_outputs(
        frame,
        input_path,
        output_dir,
        year,
        month,
    )

def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to BTS monthly ZIP",
    )

    parser.add_argument(
        "--year",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--month",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "data/processed/staging"
        ),
        help="Directory for staging outputs",
    )

    return parser


def main() -> None:
    """CLI entry point."""

    args = build_parser().parse_args()

    parquet_path, manifest_path = (
        ingest_month(
            input_path=args.input,
            year=args.year,
            month=args.month,
            output_dir=args.output_dir,
        )
    )

    print(f"Wrote {parquet_path}")
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()