# Module 1: Financial Data Collector – Design Document

**Update:** As of [date], Yahoo (yfinance) and Alpaca data ingestion are split into separate Poetry-managed microservices in the monorepo. This service focuses on Yahoo, FRED, ABS, and similar sources. Alpaca-specific ingestion will be handled by a new `alpaca_data_collector` service, each with its own dependencies and environment.

**Purpose & Scope:** This module ingests all structured financial data needed by the trading system – including **price (OHLCV)** data, **macroeconomic indicators**, **fundamentals**, and **scheduled events** (e.g. earnings, dividends, central bank meetings) from Yahoo, FRED, ABS, etc. It provides a unified, clean data layer for downstream feature pipelines and strategies. In practice, we target the instruments in our *Initial Trading Universe* (ASX large-cap stocks, ASX ETFs, etc.).

**Asset Universe:** We focus on highly liquid assets as specified in [*Initial Universe*] – e.g. ASX 50/200 equities (BHP, CBA, WES, etc.) and broad-sector ETFs (IOZ, STW, etc.). If the broker/permissions allow, we may include US market ETFs (SPY, QQQ) and fixed-income ETFs (IAF, VGB) for broader coverage. This ensures our data feeds cover the instruments the system will trade.

---

## Data Sources & Ingestion

- **Market (Price) Data:** Retrieve OHLCV data for each ticker. We will use broker APIs and finance data APIs: for example, Interactive Brokers API (via TWS socket) provides real-time/intraday ASX and global equity data, and Alpaca API or Yahoo Finance can supply US stock/ETF and delayed EOD data. We may also use free services like Alpha Vantage or Marketstack as backups (noting API rate limits). Data will be fetched at required intervals (daily closing prices, hourly/daily candles, or tick data as needed).

- **Macroeconomic Data:** Collect economic indicators for Australia and global markets. Key sources include the Australian Bureau of Statistics (ABS) and the Reserve Bank of Australia (RBA) for AUS GDP, CPI, unemployment, interest rates, etc. (available via ABS API or RBA releases), and global sources like FRED (Federal Reserve) or OECD for US/other-country indicators. We will poll these APIs on their release schedules (e.g. weekly RBA updates, monthly ABS releases, etc.) and store time series for use in feature pipelines.

- **Fundamental Data:** Obtain company financials and ratios. We will use services like Yahoo Finance (via `yfinance`), Alpha Vantage, or FinancialModelingPrep to pull balance sheets, income statements, earnings, P/E, and other fundamentals on a quarterly basis. Tickers of interest (our universe stocks) are specified in a config file. This data is typically fetched after quarterly filings and stored per-company.

- **Event (Calendar) Data:** Fetch structured event calendars for corporate actions and macro events. Examples include dividend and earnings calendars from Alpha Vantage or FMP (which list upcoming dates), and central bank meeting dates (RBA/Fed) via public calendars or scraping. These feeds are updated frequently (daily checks for new entries) and stored as event tables.

Each data category has its own ingestion service – e.g. `macro.py`, `ohlcv.py`, `fundamentals.py`, `events.py`. Ingestion modules read from a **centralized config** (`data_requirements.yaml`) that lists exactly which tickers, indicators, and calendars to fetch. Source credentials and endpoints are managed via a `sources.yaml` config.

---

## Processing & Data Flow

Data ingestion follows an **ETL/ELT pipeline** pattern:

1. **Fetch & Validate:** Scheduler (cron or Prefect) triggers each ingestion script. Script fetches raw data from its API, checks for errors or missing fields, and normalizes formats.
2. **Transform:** Apply transformations (e.g. timezone conversion, derived fields). Validate each record against a schema (`schema/*.json`).
3. **Store Raw:** Cleaned data is saved to Parquet (time-series) or SQL (structured series). Partitioned for efficient access. Metadata (record count, last fetch time) tracked.
4. **Publish/Notify:** On success, update metrics and logs. On failure, log and alert.
5. **Ingestion Log:** Maintain logs of each run to prevent duplication and track history.

Automation is handled via cron or Prefect. The scheduler controls retry logic and triggers dependent jobs when required.

---

## Storage & Organization

- **Parquet Files:** Used for large time-series like OHLCV and event logs. Partitioned by ticker/date.
- **SQL Database:** Used for structured macro data, fundamentals, and earnings/dividends.
- **Metadata Catalog:** Tracks last fetch date, coverage, schema version, and errors.
- **Data Contracts:** All output is validated against strict schemas for consistency.

---

## Architecture & Interfaces

- **Inputs:** `data_requirements.yaml` and `sources.yaml` define scope and credentials.
- **Outputs:** Stored data (Parquet, SQL), ingestion logs, and Prometheus-friendly metrics.
- **Communication:** Other modules (feature pipelines, dashboards) read data directly from storage.
- **Scheduler:** Cron or Prefect orchestrates jobs, controls flow, and manages failure handling.

---

## Data Flow Summary

1. Define assets/indicators to fetch in `data_requirements.yaml`
2. Scheduler triggers `*.py` scripts on defined intervals
3. Scripts fetch, clean, and validate data
4. Data is written to storage (Parquet/SQL)
5. Logs and metrics are updated
6. Downstream modules consume data for features and models

---

## Final Notes

This module is modular, testable, and scalable. Adding new sources means:
- Writing/extending an ingestion script
- Updating `data_requirements.yaml`
- Defining schema in `schema/*.json`

By following this pipeline, we ensure the system has complete, clean, and timely data to power models and strategies.
