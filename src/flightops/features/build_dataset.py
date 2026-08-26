"""Build leakage-safe chronological modeling datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from flightops.features.modeling import (
    MODEL_FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_modeling_dataset,
    chronological_split,
)


def split_summary(
    frame: pd.DataFrame,
) -> dict:
    """Summarize one dataset split."""

    dates = pd.to_datetime(
        frame["flight_date"]
    )

    return {
        "rows": len(frame),
        "start_date": (
            dates.min()
            .date()
            .isoformat()
        ),
        "end_date": (
            dates.max()
            .date()
            .isoformat()
        ),
        "positive_rows": int(
            frame[
                TARGET_COLUMN
            ].sum()
        ),
        "positive_rate": round(
            float(
                frame[
                    TARGET_COLUMN
                ].mean()
            ),
            6,
        ),
    }


def write_modeling_dataset(
    input_path: Path,
    output_dir: Path,
    train_end: str,
    validation_end: str,
) -> list[Path]:
    """Build and write chronological model splits."""

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input parquet not found: "
            f"{input_path}"
        )

    frame = pd.read_parquet(
        input_path
    )

    modeling = build_modeling_dataset(
        frame
    )

    splits = chronological_split(
        modeling,
        train_end=train_end,
        validation_end=validation_end,
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths: list[Path] = []

    for name, split in splits.items():
        path = (
            output_dir
            / f"{name}.parquet"
        )

        split.to_parquet(
            path,
            index=False,
        )

        paths.append(path)

    manifest = {
        "source_file": input_path.name,
        "target_column": TARGET_COLUMN,
        "feature_columns": list(
            MODEL_FEATURE_COLUMNS
        ),
        "train_end": train_end,
        "validation_end": validation_end,
        "splits": {
            name: split_summary(split)
            for name, split
            in splits.items()
        },
    }

    manifest_path = (
        output_dir
        / "split_manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    paths.append(manifest_path)

    return paths


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "data/processed/modeling"
        ),
    )

    parser.add_argument(
        "--train-end",
        default="2025-01-21",
    )

    parser.add_argument(
        "--validation-end",
        default="2025-01-26",
    )

    return parser


def main() -> None:
    """CLI entry point."""

    args = build_parser().parse_args()

    paths = write_modeling_dataset(
        input_path=args.input,
        output_dir=args.output_dir,
        train_end=args.train_end,
        validation_end=(
            args.validation_end
        ),
    )

    for path in paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()