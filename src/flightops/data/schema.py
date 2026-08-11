"""Minimal schema contract for flight records."""

from dataclasses import dataclass

REQUIRED_COLUMNS = {
    "flight_date",
    "carrier",
    "origin",
    "destination",
    "scheduled_departure",
    "departure_delay_minutes",
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    missing_columns: tuple[str, ...]


def validate_columns(columns: list[str]) -> ValidationResult:
    """Check whether required source columns are present."""
    missing = tuple(sorted(REQUIRED_COLUMNS.difference(columns)))
    return ValidationResult(ok=not missing, missing_columns=missing)
