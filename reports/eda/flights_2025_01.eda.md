# FlightOps Exploratory Data Analysis

Source: `flights_2025_01.parquet`

## Dataset Overview

- Total rows: 539,747
- Operated flights: 523,435
- Cancelled flights: 16,312
- Modeling rows: 523,435
- Flights delayed >=15 min: 95,432
- Delay rate >=15 min: 18.23%
- Mean departure delay: 14.029 min
- Median departure delay: 0.0 min
- 90th percentile departure delay: 37.0 min

## Highest Delay-Rate Carriers

| Group | Flights | Delay rate | Mean delay |
|---|---:|---:|---:|
| G4 | 9,226 | 23.57% | 21.69 |
| F9 | 15,134 | 23.20% | 19.69 |
| OH | 19,195 | 23.13% | 22.04 |
| B6 | 17,595 | 22.40% | 15.41 |
| DL | 74,169 | 19.58% | 16.44 |
| AA | 72,286 | 18.77% | 16.16 |
| OO | 63,693 | 18.70% | 17.59 |
| NK | 16,972 | 18.17% | 11.55 |
| WN | 102,291 | 17.47% | 9.91 |
| AS | 17,920 | 16.70% | 9.88 |

## Highest Delay-Rate Origin Airports

| Group | Flights | Delay rate | Mean delay |
|---|---:|---:|---:|
| ASE | 971 | 35.94% | 39.72 |
| XWA | 177 | 33.33% | 33.12 |
| HDN | 331 | 32.02% | 29.75 |
| LNK | 160 | 30.00% | 44.04 |
| EGE | 724 | 29.83% | 25.30 |
| MBS | 173 | 28.90% | 30.72 |
| HSV | 622 | 28.46% | 31.48 |
| CPR | 183 | 27.32% | 27.23 |
| BIS | 364 | 26.92% | 31.79 |
| PBI | 2,889 | 26.90% | 18.64 |

## Highest Delay-Rate Departure Hours

| Group | Flights | Delay rate | Mean delay |
|---|---:|---:|---:|
| 4 | 25 | 36.00% | 18.24 |
| 20 | 22,380 | 25.01% | 17.17 |
| 21 | 14,705 | 24.37% | 18.63 |
| 19 | 26,258 | 24.15% | 17.95 |
| 2 | 93 | 23.66% | 10.88 |
| 18 | 32,518 | 23.16% | 16.96 |
| 22 | 9,689 | 22.72% | 18.19 |
| 17 | 33,901 | 22.38% | 16.52 |
| 16 | 30,959 | 22.26% | 16.08 |
| 15 | 30,865 | 22.15% | 15.89 |

## Modeling Implications

- Target prevalence should inform evaluation metric selection.
- Carrier and airport variation supports categorical and historical aggregate features.
- Time-of-day variation supports scheduled departure hour features.
- Temporal variation supports time-aware validation instead of random splitting.
