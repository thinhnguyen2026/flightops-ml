# Day 3 — BTS Monthly Data Ingestion

## Goal

Build a reproducible ingestion pipeline for monthly BTS Reporting Carrier On-Time Performance data.

The pipeline converts the raw BTS monthly ZIP into a canonical Parquet staging dataset while validating schema, period, and source provenance.

## Pipeline

```text
BTS monthly ZIP
      ↓
Read CSV inside archive
      ↓
Normalize BTS column names
      ↓
Validate required schema
      ↓
Validate requested year/month
      ↓
Write Parquet staging dataset
      ↓
Create SHA-256 provenance manifest
```

## Canonical Column Mapping

The project maps raw BTS field names to internal snake_case names.

Examples:

| BTS Field | Canonical Field |
|---|---|
| FlightDate | flight_date |
| Reporting_Airline | carrier |
| Origin | origin |
| Dest | destination |
| CRSDepTime | scheduled_departure |
| DepDelayMinutes | departure_delay_minutes |
| DepDel15 | bts_departure_delay_15min |
| Cancelled | cancelled |

The mapping is implemented in:

`src/flightops/data/columns.py`

## Monthly ZIP Reader

The ingestion reader:

1. verifies that the source file exists;
2. verifies that the input is a ZIP archive;
3. finds the CSV inside the archive;
4. loads the CSV with pandas;
5. selects known BTS fields;
6. renames them to canonical project names;
7. validates required columns using the project schema contract.

Implementation:

`src/flightops/data/ingest.py`

## Period Validation

The ingestion command receives an expected year and month.

The pipeline compares these values with the contents of the source dataset.

For example, if the command requests January 2025 but the ZIP contains February 2025 data, ingestion fails instead of silently creating an incorrectly labeled dataset.

## Parquet Staging Output

Successful ingestion writes the canonical dataset to:

```text
data/processed/staging/flights_YYYY_MM.parquet
```

For January 2025:

```text
data/processed/staging/flights_2025_01.parquet
```

Parquet is used as the staging format because it is compact, typed, and efficient for analytical workloads.

## Provenance Manifest

Each ingestion run also creates:

```text
data/processed/staging/flights_YYYY_MM.manifest.json
```

The manifest records:

- source filename
- SHA-256 source checksum
- requested year
- requested month
- row count
- canonical column list
- output filename

Example:

```json
{
  "source_file": "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_1.zip",
  "source_sha256": "<sha256>",
  "year": 2025,
  "month": 1,
  "rows": 0,
  "columns": [],
  "output_file": "flights_2025_01.parquet"
}
```

The row count and columns above are illustrative; the real manifest contains the values generated from the downloaded BTS file.

## Command-Line Interface

The ingestion pipeline can be run with:

```bash
python -m flightops.data.ingest \
  --input data/raw/bts/2025/01/<source-file>.zip \
  --year 2025 \
  --month 1
```

On PowerShell:

```powershell
python -m flightops.data.ingest `
    --input "data/raw/bts/2025/01/<source-file>.zip" `
    --year 2025 `
    --month 1
```

For the January 2025 BTS file used during development, the pipeline successfully produced:

```text
data\processed\staging\flights_2025_01.parquet
data\processed\staging\flights_2025_01.manifest.json
```

## Testing

Synthetic BTS-style ZIP files are generated inside the unit tests so that the ingestion pipeline can be tested without depending on external downloads.

The tests verify:

- canonical column normalization;
- rejection of missing required fields;
- creation of Parquet output;
- creation of the provenance manifest;
- SHA-256 checksum generation.

Run:

```bash
pytest -q
```

and:

```bash
ruff check src tests
```

## Data Storage Policy

Raw and processed datasets are not committed to Git.

Git tracks:

- source code
- tests
- configuration
- documentation

Large data artifacts remain local or can later be moved to external object storage.

## Day 3 Commits

Day 3 is intentionally divided into meaningful incremental commits:

```text
feat: add canonical BTS column mapping
feat: add monthly BTS zip ingestion pipeline
feat: add ingestion CLI and provenance manifest
test: add BTS ingestion pipeline tests
docs: document monthly ingestion workflow
```

## Outcome

At the end of Day 3, FlightOps ML can ingest a real monthly BTS ZIP file and transform it into a validated, canonical Parquet dataset with reproducible source provenance.
