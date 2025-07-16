# Module 1: Financial Data Collector — Development Checklist

## ✅ Completed
- [x] Design document, subsections, and data source/storage/frequency docs written
- [x] Monorepo structure and microservice split (Yahoo/FRED/ABS vs Alpaca)
- [x] Scaffolded `services/financial_data_collector` with modular folders and files
- [x] Folder structure confirmed clean (no redundant nesting)
- [x] Poetry environment initialized (Python 3.12)
- [x] All compatible dependencies installed (yfinance, fredapi, pandas, etc.)
- [x] Config templates created (`sources.yaml`, `data_requirements.yaml`, `cron_schedule.yaml`)
- [x] JSON schema templates created for all data types
- [x] All four ingestion scripts scaffolded with config loading and placeholders
- [x] OHLCV ingestion implemented and tested with yfinance (Parquet output)
- [x] Macro ingestion implemented and tested with fredapi (Parquet output, valid FRED series IDs)
- [x] Fundamentals ingestion implemented and tested with yfinance (Parquet output, schema validation, debug prints removed)
- [x] Events ingestion implemented and tested with yfinance (Parquet output, ETF handling)
- [x] Schema validation implemented and tested for OHLCV, macro, and fundamentals scripts
- [x] Changes committed and pushed to GitHub

## 🚧 To Do
- [ ] Add schema validation to events script
- [ ] Add logging and error handling
- [ ] Add unit tests for each ingestion module
- [ ] Add integration test for end-to-end ingestion
- [ ] Document usage and example runs in README
- [ ] (Optional) Add Dockerfile logic for running jobs
- [ ] (Optional) Add Prometheus metrics/logging hooks

---

*Update this checklist as you progress through development!* 