# Alpaca Data Collector

This microservice ingests financial data from the Alpaca API for the trading platform, including:
- Price (OHLCV) data
- Scheduled events (earnings, dividends, etc.)

## Structure

- `ingest/` — Data fetchers for each type (ohlcv, events)
- `config/` — YAML configs for sources, requirements, and schedules
- `storage/` — Handlers for file and database output
- `schema/` — JSON schemas for validation
- `logs/` — Ingestion and error logs

## Usage

- Config-driven: edit `config/data_requirements.yaml` and `config/sources.yaml`
- Run individual scripts or schedule via cron/Prefect
- Outputs versioned Parquet files and/or SQL tables

This service is managed independently from the Yahoo/FRED/ABS collector to avoid dependency conflicts and enable modular scaling. 