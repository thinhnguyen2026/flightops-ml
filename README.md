# FlightOps ML

End-to-end machine learning system for predicting U.S. flight delays and demonstrating production-grade Data Science skills.

## Why this project exists
This repository is designed as a portfolio project for Data Scientist / Applied Scientist / ML Engineer roles. It grows through small, meaningful daily commits instead of disconnected toy notebooks.

## What the finished system will contain
- Reproducible ingestion of public U.S. flight data
- Data validation and exploratory analysis
- SQL/DuckDB analytical layer
- Time-aware feature engineering
- Baseline + tree-based ML models
- Hyperparameter tuning and calibration
- Explainability and error analysis
- ML experiment tracking
- FastAPI prediction service
- Docker packaging
- Automated tests and GitHub Actions CI
- Model/data drift monitoring
- Technical report and system-design documentation

## Repository structure
```text
flightops-ml/
├── configs/              # Project/model configuration
├── data/                 # Local raw/processed data (not committed)
├── docs/                 # Design notes and technical reports
├── notebooks/            # Exploration only; reusable logic belongs in src/
├── scripts/              # CLI entry points
├── src/flightops/
│   ├── api/              # Prediction API
│   ├── data/             # Ingestion + validation
│   ├── features/         # Feature engineering
│   └── models/           # Training + evaluation
├── tests/                # Unit/integration tests
├── .github/workflows/    # CI
├── pyproject.toml
└── Makefile
```
## Data

FlightOps ML uses the U.S. Department of Transportation Bureau
of Transportation Statistics Reporting Carrier On-Time
Performance dataset.

The initial benchmark uses the complete 2025 calendar year.

The primary target is:

`departure_delay_15min`

which indicates whether an operated flight departed at least
15 minutes after its scheduled departure time.

See:

- [`docs/data_source.md`](docs/data_source.md)
- [`docs/data_dictionary.md`](docs/data_dictionary.md)

for the data contract, field definitions, and leakage policy.
    
## Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest
```

## Portfolio rule
Every commit should answer one of these questions:
1. What real problem did I solve?
2. What engineering/research decision did I make?
3. How did I verify the result?

Avoid commits whose only purpose is to keep a GitHub streak alive.

## Roadmap
See [`docs/30_day_roadmap.md`](docs/30_day_roadmap.md).
