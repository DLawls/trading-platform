# 🚀 Alpaca Data Collector

## 🎯 Purpose
Premium financial data collection from Alpaca Markets API, providing US stock market data and ASX ADRs for the AI Trading Platform.

## 📊 Data Sources
- **Primary**: Alpaca Markets API (Premium)
- **Coverage**: US stocks, ASX ADRs, cryptocurrency
- **Update Frequency**: Real-time during market hours

## 📈 Current Implementation

### ✅ **IMPLEMENTED FEATURES**
- **OHLCV Data Collection**: Daily and hourly price data
- **Events Collection**: Corporate actions (dividends, splits, earnings framework)
- **Data Validation**: JSON schema validation and quality checks
- **Error Handling**: Robust error handling with retry logic
- **Logging**: Comprehensive logging with unified format
- **Configuration**: YAML-based configuration management

### 📋 **Data Coverage**
- **US Stocks**: 10 major S&P 500 components (AAPL, MSFT, GOOGL, etc.)
- **ASX ADRs**: 2 major Australian companies (BHP, RIO)
- **Crypto**: 3 major cryptocurrencies (BTC, ETH, SOL)
- **Intervals**: Daily and hourly data collection
- **History**: 2 years daily, 1 month hourly

## 🏗️ **Architecture**

### **Directory Structure**
```
alpaca_data_collector/
├── config/
│   ├── sources.yaml              # API configuration
│   ├── data_requirements.yaml    # Data collection requirements
│   └── cron_schedule.yaml        # Automated scheduling
├── ingest/
│   ├── ohlcv.py                 # OHLCV data collector
│   ├── events.py                # Events data collector
│   └── orchestrator.py          # Main collection orchestrator
├── logs/                        # Collection logs
└── pyproject.toml              # Python dependencies
```

### **Integration Points**
- **Shared Data Storage**: Uses centralized `financial_data/` directory
- **Unified Dashboard**: Integrated into Module 1 monitoring dashboard
- **Common Schemas**: Reuses validation schemas from Yahoo Finance collector
- **Shared Utilities**: Compatible with shared logging and monitoring framework

## 🚀 **Setup & Usage**

### **1. Install Dependencies**
```bash
cd financial_data_collector/alpaca_data_collector
poetry install
```

### **2. Configure API Keys**
1. Sign up for Alpaca account: https://app.alpaca.markets/
2. Get your API keys (paper trading recommended for testing)
3. Update `config/sources.yaml`:
```yaml
alpaca:
  api_key: 'YOUR_ACTUAL_API_KEY'
  secret_key: 'YOUR_ACTUAL_SECRET_KEY'
```

### **3. Run Data Collection**
```bash
# Run full data collection
python3 ingest/orchestrator.py

# Run individual modules
python3 ingest/ohlcv.py      # OHLCV data only
python3 ingest/events.py     # Events data only
```

### **4. Monitor via Dashboard**
The Alpaca collector is integrated into the unified Module 1 dashboard:
```bash
# Launch unified dashboard (from parent directory)
streamlit run ../dashboard/main.py
```

## 📊 **Data Output**

### **File Formats**
- **Format**: Parquet files for efficient storage and processing
- **Naming**: `{ticker}_{interval}_{datatype}_{date}.parquet`
- **Location**: `../financial_data/{datatype}/`

### **Example Files**
```
financial_data/
├── ohlcv/
│   ├── AAPL_daily_ohlcv_20250720.parquet
│   ├── MSFT_daily_ohlcv_20250720.parquet
│   └── BHP_daily_ohlcv_20250720.parquet
└── events/
    ├── alpaca_dividends_20250720.parquet
    ├── alpaca_earnings_20250720.parquet
    └── alpaca_splits_20250720.parquet
```

## ⚙️ **Configuration**

### **Customization Options**
- **Tickers**: Modify `data_requirements.yaml` to add/remove symbols
- **Intervals**: Configure daily/hourly collection frequency
- **Date Ranges**: Adjust historical data collection periods
- **API Limits**: Configure rate limiting and timeout settings

### **Scheduling**
- **Manual**: Run orchestrator script manually
- **Cron**: Use provided `cron_schedule.yaml` for automation
- **Integration**: Aligns with main Module 1 collection schedule

## 🔧 **Technical Details**

### **Dependencies**
- `alpaca-trade-api`: Official Alpaca API client
- `pandas`: Data manipulation and analysis
- `pyarrow`: Parquet file support
- `jsonschema`: Data validation
- `pyyaml`: Configuration management

### **Error Handling**
- **Rate Limiting**: Automatic retry with exponential backoff
- **API Errors**: Graceful handling of API failures
- **Data Validation**: Schema validation with detailed error logging
- **Network Issues**: Timeout and retry mechanisms

### **Performance**
- **Concurrent Requests**: Optimized for Alpaca's rate limits (200/min)
- **Data Efficiency**: Parquet format for fast I/O
- **Memory Management**: Streaming data processing for large datasets

## 🚦 **Status & Roadmap**

### **Current Status**: ✅ **PRODUCTION READY**
- Core OHLCV collection implemented and tested
- Events framework ready for API key activation
- Dashboard integration complete
- Documentation and configuration complete

### **Next Steps**
1. **API Key Activation**: Configure production API keys
2. **Testing**: Validate data collection with live API
3. **Optimization**: Fine-tune collection schedules and parameters
4. **Enhancement**: Add fundamentals data collection

## 🔗 **Resources**
- **Alpaca Documentation**: https://alpaca.markets/docs/
- **API Reference**: https://alpaca.markets/docs/api-references/
- **Python SDK**: https://github.com/alpacahq/alpaca-trade-api-python
- **Dashboard**: Access via unified Module 1 monitoring system

---

**Note**: This collector requires an Alpaca Markets account and API keys. Paper trading mode is recommended for development and testing. 