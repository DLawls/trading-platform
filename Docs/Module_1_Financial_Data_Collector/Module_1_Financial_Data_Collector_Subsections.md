## 📈 Module 1: Financial Data Collector — Implementation Spec

**Update:** As of [date], Yahoo (yfinance) and Alpaca data ingestion are split into separate Poetry-managed microservices. This service will use yfinance, FRED, ABS, etc. Alpaca ingestion will be handled in a new `alpaca_data_collector` service.

## Purpose
Ingest macroeconomic, fundamental, OHLCV, and structured event data from multiple sources (excluding Alpaca). Provide a unified, clean, and extensible data ingestion layer for downstream modules.

Supports:
- Feature pipelines
- ML model training
- Strategy triggers
- Dashboards and alerts

---

## 🧩 Subsections & Responsibilities

### 1. `ingest/`: Data Fetchers

#### a. `macro.py`
- **Sources**: FRED, RBA, ABS
- **Data**: CPI, unemployment, interest rates
- **Challenges**: Different date granularities, missing periods

#### b. `fundamentals.py`
- **Sources**: Yahoo Finance, Alpaca
- **Data**: EPS, revenue, P/E, cash flow
- **Challenges**: API gaps, varying formats, derived fields

#### c. `ohlcv.py`
- **Sources**: Yahoo Finance, Alpaca
- **Data**: Daily and hourly price data (OHLCV)
- **Challenges**: Market closures, backfill logic, ticker errors

#### d. `events.py`
- **Sources**: Yahoo Finance, central bank calendars
- **Data**: Earnings dates, dividend schedules, central bank events
- **Challenges**: Format normalization, date prediction for upcoming events

---

### 2. `config/`: Dynamic Input Specs

#### a. `sources.yaml`
- Stores base URLs, API keys, and provider configs

#### b. `data_requirements.yaml`
- **Drives ingestion logic**
- Defines tickers, indicators, event types, frequency

#### c. `cron_schedule.yaml`
- Maps ingestion jobs to schedule times

---

### 3. `storage/`: Output Handlers

#### a. `file_io.py`
- Write/read Parquet or JSON
- Handles dynamic path building and file versioning

#### b. `db.py`
- (Optional) Write to Postgres
- Support for upserts, metadata logging

---

### 4. `schema/`: Validation Layer

- JSON schema per dataset type
- Used for testing and enforcing format integrity

---

### 5. `logs/`: Monitoring & Metrics

- Log structure: timestamp, module, result, row count
- Optional Prometheus exporters for ingestion success rates, runtime

---

## 🛠️ Technical Components

### 📦 Core System

- Written in Python, modular
- Config-driven (via YAML)
- Outputs versioned Parquet or database entries

### 🔁 Scheduler

- Cron for simplicity, Prefect for robustness
- Each `*.py` exposes `run()` or `main()` callable

---

## 📂 Directory Structure

```plaintext
services/
  financial_data_collector/
    ├── ingest/
    │    ├── macro.py
    │    ├── fundamentals.py
    │    ├── ohlcv.py
    │    └── events.py
    ├── config/
    │    ├── sources.yaml
    │    ├── cron_schedule.yaml
    │    └── data_requirements.yaml
    ├── storage/
    │    ├── db.py
    │    └── file_io.py
    ├── schema/
    │    └── *.json
    ├── logs/
    ├── Dockerfile
    ├── pyproject.toml
    └── README.md
```

---

## 🔌 External Dependencies

- `yfinance`, `fredapi`, `pandas-datareader`, `alpaca-trade-api`
- `pandas`, `pyyaml`, `sqlalchemy`, `fastparquet`
- `poetry` for dependency management
- `prefect` or `cron`
- Optional: Prometheus + Grafana

---

## 🔄 Interfaces

- **Input**: YAML configs
- **Output**: Parquet or Postgres DB

```plaintext
data/
  ohlcv/
    AAPL_2023-07-13.parquet
  macro/
    cpi_au.parquet
  fundamentals/
    MSFT_q1_2024.json
```

---

## ✅ Testing & Validation

- Unit tests for each ingestion module
- JSON schema validation
- Integration test with scheduler
- Alerts/logging for missing or failed jobs

---

## 📋 Data Requirements Spec

```yaml
ohlcv:
  tickers:
    - AAPL
    - MSFT
    - TSLA
  intervals:
    - daily
    - hourly

macro:
  indicators:
    - cpi_au
    - unemployment_rate_au
    - cash_rate_target

fundamentals:
  tickers:
    - AAPL
    - MSFT
  fields:
    - revenue
    - eps
    - pe_ratio

events:
  earnings:
    tickers:
      - AAPL
      - MSFT
  dividends:
    tickers:
      - AAPL
      - TSLA
  central_bank:
    sources:
      - RBA
      - FOMC
```

---

## 📈 Example Use Case

- `macro.py`: Weekly ABS/FRED ingestion
- `ohlcv.py`: Nightly daily/hourly candle ingestion
- `events.py`: Morning earnings/dividends refresh

---

## 🧪 Bonus: Future Extensions

- Web UI for ingestion status
- Historical backfill support
- Real-time webhook/Kafka streaming
- Auto-diffing + deduplication

---

## 🔄 Next Steps

1. Finalize JSON schemas
2. Scaffold `*.py` ingestors
3. Wire in config and scheduler
4. Validate outputs and logging
5. Connect to downstream pipelines
