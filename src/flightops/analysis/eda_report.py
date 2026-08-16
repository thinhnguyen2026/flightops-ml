"""Generate reproducible exploratory reports for flight data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from flightops.analysis.eda import (
    daily_delay_summary,
    delay_by_group,
    departure_hour_summary,
    overview_summary,
)


def _render_group_table(
    frame: pd.DataFrame,
    group_column: str,
    limit: int = 10,
) -> list[str]:
    """Render grouped summary as Markdown rows."""

    lines = [
        "| Group | Flights | Delay rate | Mean delay |",
        "|---|---:|---:|---:|",
    ]

    for _, row in frame.head(
        limit
    ).iterrows():
        lines.append(
            "| "
            f"{row[group_column]} | "
            f"{int(row['flights']):,} | "
            f"{row['delay_rate_15min']:.2%} | "
            f"{row['mean_delay_minutes']:.2f} |"
        )

    return lines


def render_markdown_report(
    overview: dict,
    carrier: pd.DataFrame,
    origin: pd.DataFrame,
    departure_hour: pd.DataFrame,
    source_name: str,
) -> str:
    """Render the primary EDA report."""

    lines = [
        "# FlightOps Exploratory Data Analysis",
        "",
        f"Source: `{source_name}`",
        "",
        "## Dataset Overview",
        "",
        (
            f"- Total rows: "
            f"{overview['total_rows']:,}"
        ),
        (
            f"- Operated flights: "
            f"{overview['operated_rows']:,}"
        ),
        (
            f"- Cancelled flights: "
            f"{overview['cancelled_rows']:,}"
        ),
        (
            f"- Modeling rows: "
            f"{overview['modeling_rows']:,}"
        ),
        (
            f"- Flights delayed >=15 min: "
            f"{overview['delayed_15min_rows']:,}"
        ),
        (
            f"- Delay rate >=15 min: "
            f"{overview['delay_rate_15min']:.2%}"
        ),
        (
            "- Mean departure delay: "
            f"{overview['mean_departure_delay_minutes']} min"
        ),
        (
            "- Median departure delay: "
            f"{overview['median_departure_delay_minutes']} min"
        ),
        (
            "- 90th percentile departure delay: "
            f"{overview['p90_departure_delay_minutes']} min"
        ),
        "",
        "## Highest Delay-Rate Carriers",
        "",
    ]

    lines.extend(
        _render_group_table(
            carrier,
            "carrier",
        )
    )

    lines.extend(
        [
            "",
            "## Highest Delay-Rate Origin Airports",
            "",
        ]
    )

    lines.extend(
        _render_group_table(
            origin,
            "origin",
        )
    )

    hour_ranked = (
        departure_hour.sort_values(
            [
                "delay_rate_15min",
                "flights",
            ],
            ascending=[
                False,
                False,
            ],
        )
    )

    lines.extend(
        [
            "",
            "## Highest Delay-Rate Departure Hours",
            "",
        ]
    )

    lines.extend(
        _render_group_table(
            hour_ranked,
            "scheduled_departure_hour",
        )
    )

    lines.extend(
        [
            "",
            "## Modeling Implications",
            "",
            (
                "- Target prevalence should inform "
                "evaluation metric selection."
            ),
            (
                "- Carrier and airport variation supports "
                "categorical and historical aggregate features."
            ),
            (
                "- Time-of-day variation supports scheduled "
                "departure hour features."
            ),
            (
                "- Temporal variation supports time-aware "
                "validation instead of random splitting."
            ),
            "",
        ]
    )

    return "\n".join(lines)


def write_eda_outputs(
    input_path: Path,
    output_dir: Path,
) -> list[Path]:
    """Generate EDA JSON, CSV, and Markdown artifacts."""

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input parquet not found: {input_path}"
        )

    frame = pd.read_parquet(
        input_path
    )

    overview = overview_summary(
        frame
    )

    carrier = delay_by_group(
        frame,
        "carrier",
        min_flights=100,
    )

    origin = delay_by_group(
        frame,
        "origin",
        min_flights=100,
    )

    departure_hour = (
        departure_hour_summary(
            frame
        )
    )

    daily = daily_delay_summary(
        frame
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stem = input_path.stem

    overview_path = (
        output_dir
        / f"{stem}.overview.json"
    )

    carrier_path = (
        output_dir
        / f"{stem}.by_carrier.csv"
    )

    origin_path = (
        output_dir
        / f"{stem}.by_origin.csv"
    )

    hour_path = (
        output_dir
        / f"{stem}.by_departure_hour.csv"
    )

    date_path = (
        output_dir
        / f"{stem}.by_date.csv"
    )

    markdown_path = (
        output_dir
        / f"{stem}.eda.md"
    )

    overview_with_source = {
        "source_file": input_path.name,
        **overview,
    }

    overview_path.write_text(
        json.dumps(
            overview_with_source,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    carrier.to_csv(
        carrier_path,
        index=False,
    )

    origin.to_csv(
        origin_path,
        index=False,
    )

    departure_hour.to_csv(
        hour_path,
        index=False,
    )

    daily.to_csv(
        date_path,
        index=False,
    )

    markdown_path.write_text(
        render_markdown_report(
            overview,
            carrier,
            origin,
            departure_hour,
            input_path.name,
        ),
        encoding="utf-8",
    )

    return [
        overview_path,
        carrier_path,
        origin_path,
        hour_path,
        date_path,
        markdown_path,
    ]


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""

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
            "reports/eda"
        ),
    )

    return parser


def main() -> None:
    """CLI entry point."""

    args = build_parser().parse_args()

    paths = write_eda_outputs(
        args.input,
        args.output_dir,
    )

    for path in paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
