---
title: Financial Data Sources, Storage, Frequency

**Update:** As of [date], Yahoo (yfinance) and Alpaca ingestion are split into separate Poetry-managed microservices. This document covers only Yahoo, FRED, ABS, etc. Alpaca will be handled in a new `alpaca_data_collector` service.

tags: [data, sources, ingestion, frequency, storage]
---

# 🤠 Financial Data Collector: Sources, Frequency, and Storage

This document defines optimal data sources, access methods, update frequencies, and storage formats for our modular AI trading system focused on ASX stocks, U.S. ETFs, and macroeconomic indicators.

---

## 📈 Price Data (OHLCV)

| Provider / API               | Coverage                          | Access (Method/Cost)                   | Update Frequency             | Storage Suggestion               | Notes (AU-specific)            |
|------------------------------|-----------------------------------|----------------------------------------|------------------------------|----------------------------------|-------------------------------|
| Interactive Brokers API      | Global incl. ASX (w/ sub.)        | TWS API (socket); live/hist            | Real-time/intraday           | Parquet (tick/bar), SQL (daily)  | Requires IB subscription        |
| Alpaca API                   | US equities & ETFs                | REST/WebSocket (free US broker)        | Real-time tick/minute        | Parquet (intraday), SQL (daily)  | US only                        |
| Yahoo Finance (yfinance)     | Global incl. ASX (via `.AX`)      | Python API (free, scraped)             | Daily (delayed EOD)          | SQL or Parquet                   | ASX supported                  |
| Alpha Vantage                | Global stocks/ETFs                | REST API (free key)                    | Intraday & daily             | Parquet (intraday), SQL (daily)  | API call limits apply          |
| Marketstack                  | Global markets                    | REST API (free limited)                | Real-time or EOD             | Parquet/SQL                      | Free tier limit                |

---

## 🌏 Macroeconomic Data

| Provider/API                | Data Covered                 | Access Method (Cost)       | Update Frequency              | Storage Suggestion               | Notes                   |
|-----------------------------|------------------------------|----------------------------|-------------------------------|----------------------------------|-------------------------|
| ABS Indicator API           | AUS GDP, CPI, labor, trade   | REST (free w/ key)         | On release (e.g. 11:30am AEST) | SQL (series/date), Parquet (bulk) | Key required            |
| RBA                         | Interest rates, credit, FX   | CSV download / scrape      | Weekly, monthly               | SQL or CSV imports               | No direct API           |
| FRED                        | Global macro (US focused)    | REST API (free)            | Daily/weekly/monthly          | SQL/Parquet                      | Extensive series        |
| IMF DataMapper              | Global indicators            | REST API (free)            | Quarterly/yearly              | SQL/Parquet                      | 13 core datasets        |
| OECD                        | Global economic data         | SDMX REST API (free)       | Daily as released             | SQL/Parquet                      | Country comparisons     |

---

## 🧾 Fundamental Data

| Provider/API                | Data Covered                         | Access Method (Cost)         | Update Frequency          | Storage Suggestion       | Notes                      |
|-----------------------------|--------------------------------------|------------------------------|---------------------------|--------------------------|----------------------------|
| Alpha Vantage               | Financials, earnings, ratios         | REST API (free)              | Quarterly on filing       | SQL (per-statement)       | Global                     |
| FinancialModelingPrep       | Statements, ratios, calendar         | REST API (free/paid)         | Real-time updates         | SQL or Parquet            | Good for earnings calendar |
| Yahoo Finance (yfinance)    | Basic financials                     | Python API (scraped)         | Quarterly                 | SQL                       | ASX supported              |
| Tiingo                      | US fundamentals                     | REST API (free tier)         | Quarterly                 | SQL                       | Limited calls              |
| EDGAR                       | US filings (10-K/Q)                  | Web scrape or bulk EDGAR     | As filed                  | SQL/Parquet               | For deeper US analysis     |

---

## 📅 Scheduled Events

| Provider/API               | Data Covered                  | Access Method (Cost)       | Update Frequency        | Storage Suggestion      | Notes                        |
|----------------------------|-------------------------------|----------------------------|-------------------------|-------------------------|------------------------------|
| Alpha Vantage – Dividends  | Historical & upcoming         | REST API (free key)        | On declaration          | Parquet or SQL          | CSV or JSON                  |
| Alpha Vantage – Earnings Cal. | Forward earnings calendar   | REST API (free key)        | Daily                   | Parquet or SQL          | Efficient CSV                |
| FinancialModelingPrep Cal. | Earnings, dividends, splits   | REST API (free/paid)       | Real-time               | SQL or Parquet          | Good corporate action source |
| RBA, Fed calendars         | Central bank meetings         | Web/CSV (manual/scrape)    | Published per year      | SQL                     | Manual extraction            |

---

## 🗂 Storage Model

- **SQL**: Ideal for structured data (macro, fundamentals, earnings dates)
- **Parquet**: Ideal for large time-series (OHLCV intraday, events feed)
- Use partitioning for Parquet (by ticker/date or event type/date)
- Prefer daily/hourly/weekly fetch scheduling (via cron or Prefect/Airflow)
