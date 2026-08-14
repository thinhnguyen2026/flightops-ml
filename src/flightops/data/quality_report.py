"""Generate data-quality reports for staged flight data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from flightops.data.quality import (
    build_quality_report,
)


def render_markdown_report(
    report: dict,
    source_name: str,
) -> str:
    """Render quality metrics as Markdown."""

    target = report[
        "target_consistency"
    ]

    invalid_airports = report[
        "invalid_airport_codes"
    ]

    missing_counts = report[
        "missing_by_column"
    ]

    missing_rates = report[
        "missing_rate_by_column"
    ]

    top_missing = sorted(
        missing_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]

    lines = [
        "# FlightOps Data Quality Report",
        "",
        f"- Source: `{source_name}`",
        f"- Rows: {report['row_count']:,}",
        (
            "- Columns: "
            f"{report['column_count']}"
        ),
        (
            "- Duplicate rows: "
            f"{report['duplicate_rows']:,} "
            f"({report['duplicate_rate']:.4%})"
        ),
        "",
        "## Structural Checks",
        "",
        (
            "- Invalid origin airport codes: "
            f"{invalid_airports.get('origin', 0):,}"
        ),
        (
            "- Invalid destination airport codes: "
            f"{invalid_airports.get('destination', 0):,}"
        ),
        (
            "- Invalid scheduled departure times: "
            f"{report['invalid_scheduled_departure_times']}"
        ),
        "",
        "## Target Consistency",
        "",
        (
            "- Operated rows: "
            f"{target['operated_rows']:,}"
        ),
        (
            "- Cancelled rows: "
            f"{target['cancelled_rows']:,}"
        ),
        (
            "- Unknown cancellation rows: "
            f"{target['unknown_cancellation_rows']:,}"
        ),
        (
            "- Comparable target rows: "
            f"{target['comparable_target_rows']:,}"
        ),
        (
            "- Target mismatches: "
            f"{target['target_mismatches']:,}"
        ),
        (
            "- Target mismatch rate: "
            f"{target['target_mismatch_rate']:.4%}"
        ),
        (
            "- Operated rows missing delay: "
            f"{target['operated_rows_missing_delay']:,}"
        ),
        (
            "- Cancelled rows with delay value: "
            f"{target['cancelled_rows_with_delay_value']:,}"
        ),
        "",
        "## Top Missing Columns",
        "",
        "| Column | Missing | Rate |",
        "|---|---:|---:|",
    ]

    for column, count in top_missing:
        rate = missing_rates[column]

        lines.append(
            f"| {column} | "
            f"{count:,} | "
            f"{rate:.4%} |"
        )

    lines.append("")

    return "\n".join(lines)


def write_quality_reports(
    input_path: Path,
    output_dir: Path,
) -> tuple[Path, Path]:
    """Generate JSON and Markdown quality reports."""

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input parquet not found: "
            f"{input_path}"
        )

    frame = pd.read_parquet(
        input_path
    )

    report = build_quality_report(
        frame
    )

    report["source_file"] = (
        input_path.name
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stem = input_path.stem

    json_path = (
        output_dir
        / f"{stem}.quality.json"
    )

    markdown_path = (
        output_dir
        / f"{stem}.quality.md"
    )

    json_path.write_text(
        json.dumps(
            report,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    markdown_path.write_text(
        render_markdown_report(
            report,
            input_path.name,
        ),
        encoding="utf-8",
    )

    return json_path, markdown_path


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input staging parquet",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "reports/data_quality"
        ),
        help="Quality report directory",
    )

    return parser


def main() -> None:
    """CLI entry point."""

    args = build_parser().parse_args()

    json_path, markdown_path = (
        write_quality_reports(
            args.input,
            args.output_dir,
        )
    )

    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()