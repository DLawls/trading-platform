# 📊 FRED Economic Data Collector

## 🎯 Purpose
Collects macroeconomic indicators from the Federal Reserve Economic Data (FRED) API for economic context and analysis.

## 📈 Data Sources
- **Primary**: FRED API (Federal Reserve Economic Data)
- **Coverage**: Australian and US economic indicators
- **Update Frequency**: Daily collection of latest data

## 📊 Collected Indicators

### Australian Economic Data
- **CPALTT01AUQ657N**: Australia CPI (Consumer Price Index)
- **LRHUTTTTAUM156S**: Australia Unemployment Rate  
- **IR3TIB01AUM156N**: Australia Interest Rates (3-month)

### Data Format
- **Storage**: Parquet files in `/data/macro/`
- **Schema**: JSON validation with ISO datetime format
- **Retention**: Full historical data available

## 🚀 Usage

```bash
# Run FRED data collection
python3 financial_data_collector/fred_data_collector/ingest/fred_economic_data.py

# Output files
data/macro/
├── CPALTT01AUQ657N.parquet  # Australian CPI
├── LRHUTTTTAUM156S.parquet  # Unemployment Rate
└── IR3TIB01AUM156N.parquet  # Interest Rates
```

## ⚙️ Configuration
- **Requirements**: `config/fred_requirements.yaml`
- **API Keys**: `config/sources.yaml`
- **Schema**: `schema/fred_economic.json`

## 📊 Data Quality
- Validates against JSON schema
- Handles missing values gracefully
- Provides collection success metrics
- ISO datetime format compliance 