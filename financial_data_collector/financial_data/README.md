# 📊 Financial Data Storage

## 📁 **Directory Structure**

```
data/
├── ohlcv/              # Daily price data (OHLCV) - Parquet files
├── fundamentals/       # Company financial data - Parquet files  
├── events/             # Corporate events (earnings, dividends) - Parquet files
└── economic/           # Economic data from multiple sources
    ├── fred/           # US Federal Reserve economic indicators  
    └── abs/            # Australian Bureau of Statistics data
```

## 📈 **Data Coverage**

- **Universe**: Official ASX 50 (50 companies by market cap)
- **Format**: Parquet files for efficient storage and access
- **Update**: Daily collection via automated system
- **Retention**: See Module 1 Design Document for retention policies

## 🔧 **Data Collection**

Data is automatically collected by multiple specialized collectors:

### **Market Data (Yahoo Finance)**
```bash
# Run OHLCV, fundamentals, events collection
python3 financial_data_collector/yahoo_finance_collector/orchestrator.py

# Monitor collection
streamlit run financial_data_collector/yahoo_finance_collector/dashboard.py
```

### **Economic Data (FRED)**
```bash
# Run FRED economic indicators collection
python3 financial_data_collector/fred_data_collector/ingest/fred_economic_data.py
```

### **Centralized Configuration**
All API keys and settings are now centralized in:
```
financial_data_collector/shared/config/sources.yaml
```

## 📊 **Current Status**

- **Success Rate**: 100% (50/50 tickers available)
- **Data Volume**: ~50MB/day, ~18GB/year projected
- **Last Collection**: Check orchestrator logs

---

*For technical details, see: [Module 1 Design Document](../Docs/Module_1_Financial_Data_Collector/Module_1_Design_Document.md)* 