"""Canonical column names for the BTS on-time performance dataset."""

BTS_COLUMN_MAP = {
    "FlightDate": "flight_date",
    "Year": "year",
    "Month": "month",
    "DayofMonth": "day_of_month",
    "DayOfWeek": "day_of_week",
    "Reporting_Airline": "carrier",
    "Flight_Number_Reporting_Airline": "flight_number",
    "Origin": "origin",
    "OriginAirportID": "origin_airport_id",
    "Dest": "destination",
    "DestAirportID": "destination_airport_id",
    "CRSDepTime": "scheduled_departure",
    "DepTimeBlk": "departure_time_block",
    "CRSArrTime": "scheduled_arrival",
    "CRSElapsedTime": "scheduled_elapsed_minutes",
    "Distance": "distance_miles",
    "DepDelay": "departure_delay",
    "DepDelayMinutes": "departure_delay_minutes",
    "DepDel15": "bts_departure_delay_15min",
    "Cancelled": "cancelled",
    "Diverted": "diverted",
}

CANONICAL_COLUMNS = tuple(BTS_COLUMN_MAP.values())