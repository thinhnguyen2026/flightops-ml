# FlightOps Data Dictionary

This document defines the initial fields selected from the BTS
Reporting Carrier On-Time Performance dataset.

The project uses snake_case canonical names internally so that
modeling code is independent of the original BTS column naming.

## Core identifiers and scheduled information

| BTS Field | Project Name | Description | Feature Status |
|---|---|---|---|
| FlightDate | flight_date | Calendar date of flight | FEATURE |
| Year | year | Calendar year | FEATURE |
| Month | month | Calendar month | FEATURE |
| DayofMonth | day_of_month | Day of month | FEATURE |
| DayOfWeek | day_of_week | Day of week | FEATURE |
| Reporting_Airline | carrier | Reporting carrier code | FEATURE |
| Flight_Number_Reporting_Airline | flight_number | Flight number | CANDIDATE |
| Origin | origin | Origin airport code | FEATURE |
| OriginAirportID | origin_airport_id | DOT origin airport identifier | FEATURE |
| Dest | destination | Destination airport code | FEATURE |
| DestAirportID | destination_airport_id | DOT destination airport identifier | FEATURE |
| CRSDepTime | scheduled_departure | Scheduled departure time | FEATURE |
| DepTimeBlk | departure_time_block | Scheduled departure time block | FEATURE |
| CRSArrTime | scheduled_arrival | Scheduled arrival time | FEATURE |
| CRSElapsedTime | scheduled_elapsed_minutes | Scheduled flight duration | FEATURE |
| Distance | distance_miles | Distance between airports | FEATURE |

## Target and outcome information

| BTS Field | Project Name | Description | Feature Status |
|---|---|---|---|
| DepDelay | departure_delay | Signed departure delay in minutes | OUTCOME |
| DepDelayMinutes | departure_delay_minutes | Non-negative departure delay | TARGET SOURCE |
| DepDel15 | bts_departure_delay_15min | BTS delay >=15 minute indicator | TARGET CHECK |
| Cancelled | cancelled | Cancellation indicator | OUTCOME |
| Diverted | diverted | Diversion indicator | OUTCOME |

## Post-departure fields

These fields must not be used as model inputs for the primary
prediction task.

| BTS Field | Reason |
|---|---|
| DepTime | Actual departure is observed after prediction |
| TaxiOut | Occurs after leaving the gate |
| WheelsOff | Occurs after departure process begins |
| ArrTime | Future information |
| ArrDelay | Future information |
| ArrDelayMinutes | Future information |
| ArrDel15 | Future information |
| TaxiIn | Future information |
| ActualElapsedTime | Future information |
| AirTime | Future information |
| CarrierDelay | Delay cause is known after the outcome |
| WeatherDelay | Delay cause is known after the outcome |
| NASDelay | Delay cause is known after the outcome |
| SecurityDelay | Delay cause is known after the outcome |
| LateAircraftDelay | Delay cause is known after the outcome |

## Canonical target

The project constructs:

`departure_delay_15min`

using:

`departure_delay_minutes >= 15`

The BTS-provided `DepDel15` field is retained only for validation.

It must never appear in the feature matrix.

## Prediction-time contract

For a flight scheduled to depart at time T:

A feature is eligible only if its value is available at or before T.

Historical aggregate features created later in the project must
also obey this contract.

For example, an airport's historical delay rate for a flight on
June 10 may only use flights occurring before that flight.

Future observations must never contribute to historical features.