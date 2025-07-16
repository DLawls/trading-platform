# Financial Data Collector

This module ingests structured financial data for the trading platform, including:
- Price (OHLCV) data
- Macroeconomic indicators
- Fundamentals
- Scheduled events (earnings, dividends, central bank meetings)

## Structure

- `ingest/` — Data fetchers for each type (macro, fundamentals, ohlcv, events)
- `config/` — YAML configs for sources, requirements, and schedules
- `storage/` — Handlers for file and database output
- `schema/` — JSON schemas for validation
- `logs/` — Ingestion and error logs

## Usage

- Config-driven: edit `config/data_requirements.yaml` and `config/sources.yaml`
- Run individual scripts or schedule via cron/Prefect
- Outputs versioned Parquet files and/or SQL tables

See the design docs in `Docs/Module_1_Financial_Data_Collector/` for full details.
