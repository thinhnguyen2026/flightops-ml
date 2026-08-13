# Day 2 — Data Source and Target Definition

## Goal

Define the data source, modeling population, prediction target, feature eligibility rules, and leakage policy before building the ingestion and modeling pipeline.

## Primary Data Source

FlightOps ML uses the U.S. Department of Transportation Bureau of Transportation Statistics (BTS) Reporting Carrier On-Time Performance dataset.

The initial benchmark uses the complete 2025 calendar year so that experiments are reproducible and seasonal patterns are represented across a full year.

## Unit of Observation

One row represents one scheduled U.S. domestic flight record.

## Prediction Task

The primary task is:

> Predict whether an operated flight will depart at least 15 minutes after its scheduled departure time.

The prediction must use only information that could reasonably be available before scheduled departure.

## Canonical Target

The project constructs the binary target:

`departure_delay_15min`

using:

```python
departure_delay_15min = (
    departure_delay_minutes >= 15
).astype(int)
```

The BTS field `DepDel15` is retained only as a validation field.

It must never be included in the feature matrix.

## Modeling Population

The primary delay-classification dataset includes operated flights with an observed departure-delay outcome.

Cancelled flights are excluded because they do not have an observed departure time.

Cancellation may later be modeled as a separate prediction task.

## Leakage Policy

Features are grouped into three categories:

1. Pre-departure features
2. Outcome fields
3. Post-departure fields

Only pre-departure information is eligible for model input.

Examples of prohibited fields include:

- actual departure time
- departure delay
- taxi-out time
- wheels-off time
- actual arrival time
- arrival delay
- delay-cause fields

## Prediction-Time Contract

For a flight scheduled to depart at time `T`, a feature is eligible only if its value is available at or before `T`.

Historical aggregate features must also respect this rule.

For example, the historical delay rate for an airport on June 10 may only use flights occurring before the prediction timestamp for the June 10 flight.

Future observations must never contribute to historical features.

## Data Dictionary

The project maintains canonical snake_case names internally.

Important mappings include:

| BTS Field | Project Field | Role |
|---|---|---|
| FlightDate | flight_date | Feature |
| Reporting_Airline | carrier | Feature |
| Origin | origin | Feature |
| Dest | destination | Feature |
| CRSDepTime | scheduled_departure | Feature |
| CRSElapsedTime | scheduled_elapsed_minutes | Feature |
| Distance | distance_miles | Feature |
| DepDelayMinutes | departure_delay_minutes | Target source |
| DepDel15 | bts_departure_delay_15min | Target validation |
| Cancelled | cancelled | Outcome |

Full field definitions are documented in:

- `docs/data_source.md`
- `docs/data_dictionary.md`

## Engineering Decisions

Day 2 establishes several project-level rules:

- use a complete calendar year for the initial benchmark;
- derive the target independently instead of blindly trusting the source-provided indicator;
- explicitly exclude cancelled flights from the delay target;
- prohibit post-departure information from model features;
- document the prediction-time contract before feature engineering.

## Validation

No new modeling code was introduced on Day 2.

The existing repository quality checks remain:

```bash
ruff check src tests
pytest -q
```

## Git Commit

```text
docs: document flight data source and target definition
```

## Outcome

At the end of Day 2, the project has a clearly defined ML problem and a documented contract describing what the model is allowed to know at prediction time.
