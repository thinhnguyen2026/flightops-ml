# Project Brief

## Problem
Predict whether a U.S. flight will depart at least 15 minutes late using information available before scheduled departure.

## Why this is a strong portfolio problem
The project supports realistic temporal validation, class imbalance, large tabular data, SQL analytics, feature pipelines, explainability, deployment, and monitoring.

## Primary ML task
Binary classification:

`departure_delay_15min = 1 if departure_delay_minutes >= 15 else 0`

## Evaluation
Primary: PR-AUC and ROC-AUC.
Secondary: F1, precision, recall, Brier score / calibration, plus operational performance by carrier and airport.

## Key methodological rule
No feature may use information that becomes available after the prediction timestamp. All rolling/history features must be computed from past observations only.

## Interview story
Be ready to explain:
- Why chronological splitting is necessary.
- How target leakage was prevented.
- Why PR-AUC matters under class imbalance.
- How you selected a threshold rather than blindly using 0.5.
- How the service is tested and deployed.
- How drift would be detected after deployment.
