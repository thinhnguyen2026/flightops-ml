# Day 5 — Exploratory Data Analysis

## Goal

Build a reproducible exploratory-analysis layer for the January
2025 BTS staging dataset and use the results to guide later
feature engineering and model evaluation.

## Dataset

Input:

`data/processed/staging/flights_2025_01.parquet`

The January 2025 dataset contains:

- 539,747 total flight records
- 523,435 operated flights
- 16,312 cancelled flights
- 523,435 rows eligible for the primary delay-classification task

## Target Distribution

The primary target is departure delay of at least 15 minutes.

Among modeling-eligible flights:

- 95,432 flights were delayed at least 15 minutes
- 428,003 flights were below the 15-minute threshold
- positive-class prevalence was 18.23%

This creates a moderately imbalanced classification problem.

Accuracy alone will therefore be insufficient for model
evaluation. Later modeling stages should emphasize metrics such
as precision, recall, F1, ROC-AUC, and PR-AUC.

## Delay Distribution

For operated flights:

- mean departure delay: 14.03 minutes
- median departure delay: 0 minutes
- 90th percentile departure delay: 37 minutes

The large difference between the median and mean indicates a
right-skewed delay distribution in which many flights have little
or no delay while a smaller group experiences large delays.

## Carrier Patterns

The highest observed carrier delay rates in January 2025 included:

| Carrier | Flights | Delay Rate |
|---|---:|---:|
| G4 | 9,226 | 23.57% |
| F9 | 15,134 | 23.20% |
| OH | 19,195 | 23.13% |
| B6 | 17,595 | 22.40% |
| DL | 74,169 | 19.58% |

Carrier-level variation supports retaining carrier identity as a
categorical model feature.

Raw delay rates must still be interpreted together with flight
volume.

For example, WN operated 102,291 flights in the dataset and had
a 17.47% delay rate, creating a large absolute number of delayed
flights despite a lower rate than several smaller carriers.

## Origin Airport Patterns

Several airports showed high observed delay rates.

Examples include:

| Origin | Flights | Delay Rate | Mean Delay |
|---|---:|---:|---:|
| ASE | 971 | 35.94% | 39.72 min |
| XWA | 177 | 33.33% | 33.12 min |
| HDN | 331 | 32.02% | 29.75 min |
| LNK | 160 | 30.00% | 44.04 min |
| EGE | 724 | 29.83% | 25.31 min |

However, several high-rate airports have relatively small sample
sizes.

This means future historical airport-rate features should use
minimum-support rules or smoothing rather than directly using
unstable raw rates.

## Time-of-Day Pattern

Scheduled departure hour shows one of the clearest patterns in
the exploratory analysis.

Examples:

| Hour | Flights | Delay Rate |
|---:|---:|---:|
| 05 | 13,432 | 8.90% |
| 06 | 35,288 | 8.07% |
| 08 | 37,751 | 11.86% |
| 12 | 32,072 | 19.62% |
| 15 | 30,865 | 22.15% |
| 18 | 32,518 | 23.16% |
| 19 | 26,258 | 24.15% |
| 20 | 22,380 | 25.01% |
| 21 | 14,705 | 24.37% |

Delay risk generally increases from the early morning through the
afternoon and evening.

This pattern motivates scheduled-departure-hour features and may
also reflect propagation of delays through airline and airport
operations during the day.

Hours between midnight and 04:00 contain relatively few flights,
so their raw rates should not be strongly interpreted.

## Modeling Decisions From EDA

The January analysis motivates several later modeling decisions:

1. Use metrics beyond accuracy because the target prevalence is
   only 18.23%.

2. Include carrier as a categorical feature.

3. Include origin and destination airport information.

4. Engineer scheduled departure hour and potentially cyclical
   time representations.

5. Build historical carrier and airport delay statistics using
   only information available before the prediction timestamp.

6. Apply smoothing or minimum-support thresholds to historical
   aggregate features.

7. Use time-aware validation because operational delay behavior
   varies over time.

## Reproducible EDA

Run:

```bash
python -m flightops.analysis.eda_report \
  --input data/processed/staging/flights_2025_01.parquet \
  --output-dir reports/eda