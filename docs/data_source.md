# Data Source

## Primary source

This project uses the U.S. Department of Transportation
Bureau of Transportation Statistics (BTS) Reporting Carrier
On-Time Performance dataset.

The dataset contains flight-level information for reported
U.S. domestic flights, including:

- flight date
- reporting carrier
- origin and destination airports
- scheduled departure and arrival times
- actual departure and arrival times
- departure and arrival delays
- cancellations and diversions
- flight distance
- delay causes

## Project data period

The initial benchmark dataset uses flights from:

January 1, 2025 through December 31, 2025.

A complete calendar year is used instead of the latest partial
year so that experiments are reproducible and seasonal patterns
are represented throughout the year.

The ingestion pipeline will later support arbitrary year/month
combinations.

## Unit of observation

One row represents one scheduled flight record.

## Prediction task

The primary modeling task is:

> Predict whether an operated flight will depart at least
> 15 minutes after its scheduled departure time.

Prediction is made using only information that could reasonably
be available before scheduled departure.

## Target

The canonical project target is:

departure_delay_15min

It is defined as:

departure_delay_15min = 1
    if departure_delay_minutes >= 15
else 0

The BTS dataset also provides the field `DepDel15`, which is a
departure-delay indicator for delays of 15 minutes or more.

During preprocessing, the project will derive the target from
departure delay minutes and compare it against the BTS indicator
as a data-quality check.

## Cancelled flights

Cancelled flights do not have an observed departure-delay target
because the aircraft never departs.

Therefore:

- cancelled flights are excluded from the departure-delay
  classification dataset;
- cancellation status is not used as a predictor;
- flight cancellation may be modeled as a separate task in a
  future extension.

## Leakage policy

Features are separated into three categories:

1. Pre-departure features
   Information available before scheduled departure and eligible
   for prediction.

2. Outcome fields
   Variables used to construct or validate the target.

3. Post-departure fields
   Information generated after the prediction time and therefore
   prohibited from model features.

Examples of prohibited features include actual departure time,
taxi-out time, wheels-off time, arrival delay, and reported delay
causes.

## Reproducibility

Raw BTS downloads are not committed to Git because the files can
be large.

Downloaded files will be stored locally under:

data/raw/

Processed analytical datasets will be stored under:

data/processed/

Both directories are excluded from normal Git tracking except for
placeholder files.