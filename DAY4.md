# Day 4 — Data Quality Pipeline

## Goal

Build an automated data-quality pipeline for the January 2025 BTS staging dataset.

The pipeline checks:

- missing values
- duplicate rows
- invalid airport codes
- invalid scheduled departure times
- cancellation behavior
- consistency between the derived delay target and BTS `DepDel15`
- machine-readable and human-readable quality reports

## Input

```text
data/processed/staging/flights_2025_01.parquet
```

## Pipeline

```text
January 2025 Parquet
        ↓
Basic quality checks
        ↓
Target/cancellation consistency checks
        ↓
JSON quality report
        ↓
Markdown quality report
```

## Planned Commits

```text
feat: add reusable flight data quality checks
feat: validate target consistency and cancellation outcomes
feat: add data quality reporting CLI
test: add data quality pipeline tests
docs: document January 2025 data quality results
```

## Expected CLI

```powershell
python -m flightops.data.quality_report `
    --input "data/processed/staging/flights_2025_01.parquet" `
    --output-dir "reports/data_quality"
```

## Expected Outputs

```text
reports/data_quality/flights_2025_01.quality.json
reports/data_quality/flights_2025_01.quality.md
```

## Quality Principles

A production ML pipeline should fail or warn before training when upstream data changes unexpectedly.

Day 4 establishes checks for structural and semantic data quality before feature engineering begins.

## Target Consistency

The project derives:

```python
departure_delay_15min = (
    departure_delay_minutes >= 15
).astype(int)
```

and compares it against the BTS-provided `bts_departure_delay_15min` indicator.

Only operated flights with both values available are compared.

## Cancellation Logic

Cancelled flights are counted separately from operated flights.

Because cancelled flights do not have an observed departure-delay outcome, they are not part of the primary departure-delay classification population.

## Outcome

At the end of Day 4, FlightOps ML can automatically inspect a monthly staging dataset and generate auditable data-quality reports before downstream feature engineering and model training.
