# FlightOps ML

End-to-end machine learning system for predicting U.S. flight delays and demonstrating production-grade Data Science, Machine Learning, and MLOps skills.

## Why this project exists

This repository is designed as a portfolio project for Data Scientist, Applied Scientist, and ML Engineer roles.

The project grows through small, meaningful engineering and research commits rather than disconnected toy notebooks.

The goal is to build a complete machine learning workflow covering:

**raw data → validation → EDA → feature engineering → modeling → deployment → monitoring**

## What the finished system will contain

* Reproducible ingestion of public U.S. flight data
* Data validation and automated data-quality reporting
* Exploratory Data Analysis (EDA)
* SQL/DuckDB analytical layer
* Leakage-safe feature engineering
* Time-aware train/validation/test splitting
* Baseline and tree-based ML models
* Hyperparameter tuning
* Probability calibration
* Explainability and error analysis
* ML experiment tracking
* FastAPI prediction service
* Docker packaging
* Automated tests
* GitHub Actions CI
* Model and data drift monitoring
* Technical report
* System-design documentation

## Repository structure

```text
flightops-ml/
├── configs/                  # Project/model configuration
├── data/
│   ├── raw/                  # Local raw BTS data (not committed)
│   └── processed/            # Staging/modeling data (not committed)
├── docs/                     # Design notes and technical documentation
├── notebooks/                # Exploration only; reusable logic belongs in src/
├── reports/
│   ├── data_quality/         # Data-quality reports
│   └── eda/                  # Reproducible EDA outputs
├── scripts/                  # Utility scripts / CLI entry points
├── src/
│   └── flightops/
│       ├── analysis/         # Reusable EDA logic
│       ├── api/              # Prediction API
│       ├── data/             # Ingestion and validation
│       ├── features/         # Feature engineering and dataset construction
│       └── models/           # Training and evaluation
├── tests/                    # Unit and integration tests
├── .github/
│   └── workflows/            # Continuous Integration
├── DAY1.md
├── DAY2.md
├── DAY3.md
├── DAY4.md
├── DAY5.md
├── DAY6.md
├── pyproject.toml
├── Makefile
└── README.md
```

## Data

FlightOps ML uses the U.S. Department of Transportation Bureau of Transportation Statistics (BTS) **Reporting Carrier On-Time Performance** dataset.

The initial benchmark uses the complete **2025 calendar year**.

The current development workflow begins with **January 2025** and will expand to additional months as the pipeline matures.

The primary target is:

`departure_delay_15min`

It indicates whether an operated flight departed at least **15 minutes after its scheduled departure time**.

See:

* [`docs/data_source.md`](docs/data_source.md)
* [`docs/data_dictionary.md`](docs/data_dictionary.md)

for the data source, field definitions, target definition, and leakage policy.

## Prediction task

The primary modeling task is:

> Predict whether an operated U.S. domestic flight will depart at least 15 minutes late using only information that could reasonably be available before scheduled departure.

Cancelled flights are excluded from the primary departure-delay classification population because they do not have an observed departure-delay outcome.

Cancellation may later be modeled as a separate prediction task.

## Leakage policy

The project follows a strict prediction-time contract.

For a flight scheduled to depart at time `T`, a feature is eligible only if its value is available at or before `T`.

Post-departure information is prohibited from model inputs.

Examples of prohibited fields include:

* actual departure time
* departure delay
* taxi-out time
* wheels-off time
* actual arrival time
* arrival delay
* delay-cause fields

The final modeling dataset uses a **feature whitelist** rather than attempting to drop known leakage fields after the fact.

---

## Monthly ingestion

Monthly BTS ZIP files can be ingested with:

```bash
python -m flightops.data.ingest \
  --input data/raw/bts/2025/01/<source-file>.zip \
  --year 2025 \
  --month 1
```

The ingestion pipeline:

1. reads the BTS ZIP archive;
2. extracts the monthly CSV;
3. selects known source fields;
4. normalizes BTS field names to canonical snake_case names;
5. validates the required schema;
6. verifies the requested year and month;
7. writes a Parquet staging dataset;
8. generates a SHA-256 provenance manifest.

Example outputs:

```text
data/processed/staging/flights_2025_01.parquet
data/processed/staging/flights_2025_01.manifest.json
```

The provenance manifest records information such as:

* source filename
* SHA-256 checksum
* year
* month
* row count
* canonical columns
* generated output file

Raw and processed datasets are intentionally excluded from Git.

---

## Data quality

Monthly staging datasets can be validated with:

```bash
python -m flightops.data.quality_report \
  --input data/processed/staging/flights_2025_01.parquet \
  --output-dir reports/data_quality
```

The quality pipeline checks:

* missing values
* duplicate rows
* invalid airport codes
* invalid scheduled departure times
* cancellation outcomes
* missing delay outcomes
* consistency between the independently derived target and BTS `DepDel15`

The pipeline generates both JSON and Markdown reports.

Example:

```text
reports/data_quality/
├── flights_2025_01.quality.json
└── flights_2025_01.quality.md
```

The target is independently derived from:

```python
departure_delay_15min = (
    departure_delay_minutes >= 15
).astype(int)
```

The BTS-provided `DepDel15` field is used only as a data-quality consistency check and is never included as a model feature.

---

## Exploratory analysis

Reproducible EDA can be generated with:

```bash
python -m flightops.analysis.eda_report \
  --input data/processed/staging/flights_2025_01.parquet \
  --output-dir reports/eda
```

The EDA pipeline analyzes:

* target prevalence and class imbalance
* departure-delay distribution
* carrier-level delay rates
* origin-airport delay rates
* scheduled departure-hour patterns
* daily temporal variation

Example outputs:

```text
reports/eda/
├── flights_2025_01.overview.json
├── flights_2025_01.by_carrier.csv
├── flights_2025_01.by_origin.csv
├── flights_2025_01.by_departure_hour.csv
├── flights_2025_01.by_date.csv
└── flights_2025_01.eda.md
```

### January 2025 snapshot

The January 2025 source data contains:

* **539,747** total flight records
* **523,435** operated flights
* **16,312** cancelled flights
* **523,435** rows eligible for the primary classification task
* **95,432** flights delayed at least 15 minutes
* **18.23%** positive-class prevalence

Departure-delay statistics:

* mean delay: **14.03 minutes**
* median delay: **0 minutes**
* 90th percentile: **37 minutes**

The difference between the mean and median indicates a strongly right-skewed delay distribution.

### Carrier patterns

Several carriers showed noticeably different January 2025 delay rates.

Examples:

| Carrier | Flights | Delay Rate |
| ------- | ------: | ---------: |
| G4      |   9,226 |     23.57% |
| F9      |  15,134 |     23.20% |
| OH      |  19,195 |     23.13% |
| B6      |  17,595 |     22.40% |
| DL      |  74,169 |     19.58% |

Carrier identity is therefore retained as a categorical modeling feature.

### Airport patterns

Some origin airports exhibited high observed delay rates.

Examples:

| Origin | Flights | Delay Rate |
| ------ | ------: | ---------: |
| ASE    |     971 |     35.94% |
| XWA    |     177 |     33.33% |
| HDN    |     331 |     32.02% |
| LNK    |     160 |     30.00% |
| EGE    |     724 |     29.83% |

Because some airports have relatively small sample sizes, future historical airport statistics will require minimum-support rules or smoothing.

### Time-of-day pattern

One of the clearest EDA patterns is increasing delay risk later in the day.

For example:

| Scheduled Hour | Flights | Delay Rate |
| -------------: | ------: | ---------: |
|             06 |  35,288 |      8.07% |
|             08 |  37,751 |     11.86% |
|             12 |  32,072 |     19.62% |
|             15 |  30,865 |     22.15% |
|             18 |  32,518 |     23.16% |
|             20 |  22,380 |     25.01% |

This motivates explicit scheduled-time features and later historical operational features.

See [`DAY5.md`](DAY5.md) for the full exploratory-analysis notes.

---

## Modeling dataset

The modeling dataset is constructed using only information available before scheduled departure.

Cancelled flights are excluded.

The binary target is:

```text
departure_delay_15min
```

and is derived from:

```text
departure_delay_minutes >= 15
```

### Initial feature set

The first leakage-safe modeling feature set contains:

* `carrier`
* `origin`
* `destination`
* `route`
* `day_of_week`
* `scheduled_departure_hour`
* `scheduled_departure_hour_sin`
* `scheduled_departure_hour_cos`
* `scheduled_arrival_hour`
* `scheduled_elapsed_minutes`
* `distance_miles`

Cyclical departure-hour features allow the model to represent the periodic nature of time-of-day.

Historical carrier and airport delay statistics are intentionally postponed until they can be implemented using strict past-only aggregation.

### Chronological train/validation/test split

The January 2025 development dataset uses a chronological split:

```text
January 1 ───────── January 21   TRAIN

January 22 ─ January 26          VALIDATION

January 27 ─ January 31          TEST
```

A chronological split is used instead of a random split because deployment requires predicting future flights from historical information.

Random splitting could mix future operational conditions into the training data and produce an unrealistically optimistic evaluation.

Build the modeling datasets with:

```bash
python -m flightops.features.build_dataset \
  --input data/processed/staging/flights_2025_01.parquet \
  --output-dir data/processed/modeling
```

Expected outputs:

```text
data/processed/modeling/
├── train.parquet
├── validation.parquet
├── test.parquet
└── split_manifest.json
```

See [`DAY6.md`](DAY6.md) for the modeling-data contract and split design.

---

## Quick start

### Windows PowerShell

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Run linting:

```powershell
python -m ruff check src tests
```

Run tests:

```powershell
python -m pytest -q
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m ruff check src tests
python -m pytest -q
```

---

## Reproducible workflow

The current workflow is:

```text
BTS monthly ZIP
        ↓
Data ingestion
        ↓
Canonical schema
        ↓
Parquet staging
        ↓
Data-quality validation
        ↓
Exploratory analysis
        ↓
Leakage-safe modeling population
        ↓
Scheduled feature engineering
        ↓
Chronological split
        ↓
Baseline ML model
```

---

## Testing and CI

The repository contains automated tests for:

* schema validation
* BTS ingestion
* provenance output
* data-quality checks
* target consistency
* EDA calculations
* EDA report generation
* modeling-population filtering
* leakage prevention
* target generation
* scheduled feature engineering
* chronological splitting
* modeling dataset materialization

GitHub Actions runs the project checks automatically on pushes and pull requests.

The standard local checks are:

```bash
python -m ruff check src tests
python -m pytest -q
```

---

## Development log

The repository records major development milestones in daily engineering notes:

* [`DAY1.md`](DAY1.md) — Project structure, testing, linting, and CI
* [`DAY2.md`](DAY2.md) — Data source, target definition, and leakage policy
* [`DAY3.md`](DAY3.md) — BTS monthly ingestion and provenance
* [`DAY4.md`](DAY4.md) — Automated data-quality validation
* [`DAY5.md`](DAY5.md) — Reproducible exploratory analysis
* [`DAY6.md`](DAY6.md) — Leakage-safe modeling dataset and chronological splitting

---

## Portfolio rule

Every commit should answer at least one of these questions:

1. What real problem did I solve?
2. What engineering or research decision did I make?
3. How did I verify the result?

Commits whose only purpose is to create GitHub activity are avoided.

The project favors small, meaningful, reviewable increments.

---

## Roadmap

The broader development roadmap is available at:

[`docs/30_day_roadmap.md`](docs/30_day_roadmap.md)

Upcoming milestones include:

* baseline Logistic Regression
* proper classification metrics
* categorical preprocessing
* tree-based models
* hyperparameter tuning
* probability calibration
* historical leakage-safe aggregate features
* SQL/DuckDB analytics
* model explainability
* error analysis
* experiment tracking
* FastAPI serving
* Docker
* drift monitoring
* production-oriented system design
