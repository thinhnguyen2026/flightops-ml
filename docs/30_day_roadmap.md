# 30-Day Build Roadmap

The goal is one meaningful, reviewable contribution per day. Keep commits small enough to explain in an interview.

| Day | Deliverable | Suggested commit |
|---|---|---|
| 1 | Repository scaffold, package structure, CI, schema contract | `chore: initialize production ML project structure` |
| 2 | Data-source research + data dictionary | `docs: document flight data source and target definition` |
| 3 | Download/ingestion CLI | `feat: add reproducible raw data ingestion` |
| 4 | Data validation checks | `feat: validate raw flight schema and ranges` |
| 5 | Convert raw files to Parquet | `feat: build parquet preprocessing pipeline` |
| 6 | DuckDB analytical layer + first SQL queries | `feat: add duckdb analytics layer` |
| 7 | EDA report: delay distribution, carriers, airports | `analysis: add reproducible delay EDA` |
| 8 | Leakage audit | `docs: identify and remove target leakage features` |
| 9 | Chronological train/val/test splitter | `feat: add time-aware dataset split` |
| 10 | Naive baseline | `feat: establish majority and historical-rate baselines` |
| 11 | Logistic regression baseline | `feat: train interpretable classification baseline` |
| 12 | Evaluation module: ROC-AUC, PR-AUC, F1, calibration | `feat: centralize model evaluation metrics` |
| 13 | Airport/carrier/time features | `feat: add operational feature engineering` |
| 14 | Historical rolling features without leakage | `feat: add lagged delay-rate features` |
| 15 | Tree model (HistGradientBoosting/XGBoost if added) | `feat: add nonlinear gradient boosting model` |
| 16 | Hyperparameter search | `feat: tune model with time-aware validation` |
| 17 | Feature importance / permutation importance | `analysis: explain model drivers` |
| 18 | Error slices by airport/carrier/time | `analysis: add model failure slice report` |
| 19 | Probability calibration + threshold policy | `feat: calibrate predictions and decision threshold` |
| 20 | Experiment tracking abstraction | `feat: add reproducible experiment logging` |
| 21 | Save/load model artifact + metadata | `feat: version trained model artifacts` |
| 22 | FastAPI `/health` and `/predict` | `feat: serve model through fastapi` |
| 23 | API validation + tests | `test: add prediction api contract tests` |
| 24 | Dockerfile | `build: containerize prediction service` |
| 25 | CI expansion: lint, test, coverage | `ci: enforce quality checks on pull requests` |
| 26 | Batch inference job | `feat: add batch prediction pipeline` |
| 27 | Drift metrics | `feat: detect feature and prediction drift` |
| 28 | System-design diagram + architecture notes | `docs: document end-to-end ml architecture` |
| 29 | Reproducible benchmark table | `analysis: benchmark models on frozen test set` |
| 30 | Portfolio-grade README, demo GIF/screenshots, results | `docs: publish project results and technical narrative` |

## After Day 30
Do not abandon the repo. Add one deeper feature each week: cloud deployment, orchestration, Spark, streaming, causal analysis, uncertainty, or model monitoring.
