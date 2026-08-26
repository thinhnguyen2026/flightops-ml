Day 6 — Leakage-Safe Modeling Dataset and Time Split

Goal

Convert the January 2025 BTS staging dataset into a modeling-ready dataset using only pre-departure information, then create deterministic chronological train/validation/test splits.

Core Principles

The binary target is derived from departure_delay_minutes >= 15.

Cancelled flights are excluded from the primary delay-classification population.

Outcome and post-departure columns never enter the model feature matrix.

Time features are derived only from scheduled information.

Dataset splitting is chronological rather than random.

Input

data/processed/staging/flights_2025_01.parquet

Pipeline

Staging Parquet
      ↓
Modeling population filter
      ↓
Canonical binary target
      ↓
Leakage-safe scheduled features
      ↓
Chronological split
      ↓
Train / validation / test Parquet files
      ↓
Split manifest

Planned Commits

feat: build canonical modeling population and target
feat: add leakage-safe scheduled flight features
feat: add chronological dataset split pipeline
test: add modeling dataset and split tests
docs: document leakage-safe modeling dataset

Split Strategy

For January 2025:

Train: January 1–21

Validation: January 22–26

Test: January 27–31

Initial Feature Set

carrier

origin

destination

route

day of week

scheduled departure hour

scheduled departure hour sine/cosine

scheduled arrival hour

scheduled elapsed minutes

distance miles

Historical aggregate features are postponed until a later stage because they require strict past-only aggregation.

Expected CLI

python -m flightops.features.build_dataset `
    --input "data/processed/staging/flights_2025_01.parquet" `
    --output-dir "data/processed/modeling"

Expected Outputs

data/processed/modeling/train.parquet
data/processed/modeling/validation.parquet
data/processed/modeling/test.parquet
data/processed/modeling/split_manifest.json

Outcome

At the end of Day 6, FlightOps ML has a reproducible, leakage-safe modeling dataset and a chronological evaluation split ready for baseline model training.