from flightops.data.schema import REQUIRED_COLUMNS, validate_columns


def test_valid_schema_passes():
    result = validate_columns(sorted(REQUIRED_COLUMNS))
    assert result.ok
    assert result.missing_columns == ()


def test_missing_column_is_reported():
    columns = sorted(REQUIRED_COLUMNS - {"origin"})
    result = validate_columns(columns)
    assert not result.ok
    assert result.missing_columns == ("origin",)
