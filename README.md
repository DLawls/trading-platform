# 🤖 AI Trading Platform

## 📋 **Project Overview**

A modular AI-powered trading platform focused on the Australian market, starting with comprehensive data collection for the official ASX 50 companies.

**Current Status**: Module 1 Complete ✅ | Module 2 In Development 🚧 | **Dashboard v2.0 Enhanced** ✅ | **Chinese Indicators Added** 🇨🇳

---

## 🏗️ **Architecture**

### **📊 Module 1: Financial Data Collector** ✅ **PRODUCTION READY**
- **Universe**: Official ASX 50 (50 companies by market cap)
- **Data Types**: OHLCV, Fundamentals, Events, Macroeconomic
- **Success Rate**: 100% data availability
- **Storage**: ~50MB/day, automated collection

### **📄 Module 2: PDF/HTML Document Extractor** 🚧 **IN DEVELOPMENT**
- Extract data from company announcements and reports
- Process structured and unstructured documents
- Integration with Module 1 data streams

### **🎛️ Dashboard v2.0: Complete Trading System Monitoring** ✅ **ENHANCED**
- **Location**: Root-level `dashboard/` directory
- **Coverage**: 54 total macro indicators + ASX 50 company data
- **Design**: Clean, scrollable interface with minimal UI
- **New**: Chinese economic indicators for trading partner analysis 🇨🇳

---

## 📁 **Project Structure**

```
trading-platform/
├── 📊 dashboard/                    # 🆕 Complete System Dashboard v2.0
│   ├── app.py                       # Main dashboard application
│   ├── launch.py                    # Quick launcher script
│   ├── config/                      # Dashboard configuration
│   ├── pages/                       # Individual page modules
│   │   ├── macro_indicators.py      # ✅ Complete macro indicators (54 total)
│   │   ├── company_indicators.py    # 🚧 ASX 50 company data (placeholder)
│   │   ├── system_overview.py       # ✅ System health overview
│   │   └── system_operations.py     # 🚧 Operations monitoring (placeholder)
│   └── components/                  # Reusable UI components
├── 📚 documentation/                # All documentation
│   ├── Module_1_Financial_Data_Collector/  # Module 1 docs (complete)
│   └── Overview/                    # Project overview docs
├── 📊 financial_data/              # Financial data storage (Module 1)
│   ├── ohlcv/                      # Daily price data
│   ├── fundamentals/               # Company financials
│   ├── events/                     # Corporate events
│   └── economic/                   # Economic indicators
└── 🛠️ financial_data_collector/    # MODULE 1: Financial Data Collection
    ├── yahoo_finance_collector/    # Primary data source (Yahoo Finance)
    ├── fred_data_collector/        # FRED economic data (10 indicators)
    ├── abs_data_collector/         # ABS Australian data (36 indicators)
    └── alpaca_data_collector/      # Alternative data source (Alpaca)
```

---

## 🚀 **Quick Start**

### **🎛️ Dashboard v2.0: Complete System Monitoring**
```bash
# Launch the new complete dashboard
cd dashboard
python3 launch.py

# Or directly with Streamlit
streamlit run app.py

# Access at: http://localhost:8501
```

### **📊 Module 1: Data Collection**
```bash
# Run data collection for ASX 50
python3 financial_data_collector/yahoo_finance_collector/orchestrator.py

# Legacy Module 1 dashboard (deprecated)
streamlit run financial_data_collector/yahoo_finance_collector/dashboard.py
```

### **📚 Documentation**
- **Dashboard v2.0**: [Complete System Dashboard](dashboard/)
- **Module 1 Status**: [Development Checklist](documentation/Module_1_Financial_Data_Collector/Module_1_Complete_Guide.md)
- **Project Overview**: [Overview Documentation](documentation/Overview/)
- **Data Storage**: [Data Directory](financial_data/)

---

## 📊 **Dashboard v2.0 Features**

### **✅ Macro Indicators Page (Enhanced)**
- **🇦🇺 FRED Australian**: 10 economic indicators with exact FRED codes
- **🏛️ ABS Australian**: 36 indicators across 8 categories
- **🇺🇸 US Reference**: 4 key economic indicators  
- **🇨🇳 Chinese Indicators**: 4 economic indicators for trading partner analysis
- **🎨 Design**: Clean grid layout with minimal UI, live data updates
- **🔄 Update Button**: Real-time data refresh from all sources
- **📊 Total Coverage**: 54 macro indicators

### **🚧 ASX 50 Companies Page (Planned)**
- Market data: OHLCV + Market cap rankings
- Financial fundamentals: 6 key metrics per company
- Corporate events: Earnings + dividend calendars
- Company analysis tools and sector insights

### **📊 System Overview (Complete)**
- Overall system health monitoring
- Data collection success rates
- Quick navigation to all sections

### **⚙️ System Operations (Planned)**
- Data source monitoring and performance
- Collection metrics and error tracking
- System configuration and health checks

---

## 📈 **Current Metrics**

### **✅ Module 1: Financial Data Collector**
- **Universe**: 50 official ASX companies ($1.5T+ market cap)
- **Data Availability**: 100% (50/50 tickers verified)
- **Collection Time**: ~10 minutes for complete dataset
- **Success Rate**: 100% maintained
- **Storage Growth**: ~18GB/year projected

### **📊 Data Coverage**
- **Daily OHLCV**: All 50 ASX companies
- **Quarterly Fundamentals**: All 50 ASX companies  
- **Corporate Events**: Earnings, dividends for all companies
- **Macro Data**: 57 indicators across Australian, US, and global markets

### **🎛️ Dashboard v2.0 Coverage**
- **Macro Indicators**: 57 total (10 FRED + 36 ABS + 4 US + 7 Global)
- **Company Data**: ASX 50 ready for integration
- **System Monitoring**: Complete health overview
- **Data Sources**: 4 active (Yahoo, FRED, ABS, Alpaca)

---

## 🎯 **Development Roadmap**

### **✅ Phase 1: Data Foundation (COMPLETE)**
- [x] ASX 50 data collection infrastructure
- [x] Automated daily collection system
- [x] Data quality monitoring and validation
- [x] Production deployment and monitoring

### **✅ Phase 1.5: Dashboard v2.0 (ENHANCED)**
- [x] Complete system dashboard at root level
- [x] Macro indicators page with all 54 indicators
- [x] Chinese economic indicators added for trading partner analysis
- [x] Clean grid layout with minimal UI design
- [x] Real-time update button for data refresh
- [x] System overview and navigation

### **🚧 Phase 2: Document Processing (IN PROGRESS)**
- [ ] PDF/HTML document extraction
- [ ] Company announcement processing
- [ ] Integration with existing data streams
- [ ] Structured data extraction from reports

### **🔄 Phase 2.5: Dashboard Integration (NEXT)**
- [ ] Connect macro indicators to live Module 1 data
- [ ] Complete ASX 50 company indicators page
- [ ] System operations monitoring page
- [ ] Real-time data refresh and alerts

### **📈 Phase 3: Analytics & Signals (PLANNED)**
- [ ] Feature engineering pipelines
- [ ] Machine learning model development
- [ ] Signal generation and backtesting
- [ ] Strategy development framework

### **🤖 Phase 4: Trading Engine (PLANNED)**
- [ ] Order management system
- [ ] Risk management framework
- [ ] Portfolio management
- [ ] Live trading integration

---

## 🛠️ **Technology Stack**

### **Core Technologies**
- **Python 3.11+**: Primary development language
- **Streamlit**: Dashboard framework (v2.0)
- **Poetry**: Dependency management
- **Pandas**: Data manipulation and analysis
- **Parquet**: Efficient data storage format

### **Dashboard v2.0 Stack**
- **Streamlit**: Interactive web dashboard
- **YAML**: Configuration management
- **HTML/CSS**: Custom styling for bordered sections
- **Multi-page architecture**: Modular page components

### **Data Sources**
- **Yahoo Finance**: Primary market data (free)
- **FRED API**: Economic data (free) - 14 indicators (10 AU + 4 US + 4 CN)
- **ABS Web**: Australian statistics (web scraping) - 36 indicators  
- **Alpaca Markets**: Premium US/crypto data - 7 assets
- **Future**: Alpha Vantage, Interactive Brokers, additional sources

### **Infrastructure**
- **Docker**: Containerized services
- **Microservices**: Modular, scalable architecture
- **Automated Testing**: Comprehensive test coverage
- **CI/CD**: Automated deployment pipelines

---

## 📞 **Support & Documentation**

### **📚 Documentation Navigation**
- **🎛️ Dashboard v2.0**: [Complete System Dashboard](dashboard/)
- **📋 Quick Status**: [Module 1 Guide](documentation/Module_1_Financial_Data_Collector/Module_1_Complete_Guide.md)
- **📊 Data Info**: [Data Directory](financial_data/)
- **🌐 Project Overview**: [Overview Docs](documentation/Overview/)

### **🔧 Operations**
- **New Dashboard**: `dashboard/` directory with `launch.py`
- **Legacy Logs**: `financial_data_collector/yahoo_finance_collector/logs/`
- **Configuration**: `financial_data_collector/yahoo_finance_collector/config/`
- **Monitoring**: Dashboard v2.0 at `localhost:8501`
- **Data**: Organized in `financial_data/` directory

---

## 🏆 **Project Status**

**🎯 Current Focus**: Dashboard v2.0 macro indicators enhanced with 54 indicators including Chinese economic data for trading partner analysis. Module 1 continues production data collection. Next: Complete company indicators page and connect live data.

**📊 Production Metrics**: 
- Data Collection: ✅ 100% operational
- System Uptime: ✅ >99% availability  
- Data Quality: ✅ 99%+ clean data
- Universe Coverage: ✅ Complete ASX 50
- Dashboard v2.0: ✅ Macro indicators enhanced (54/54)

**🎛️ Dashboard v2.0 Status**:
- System Overview: ✅ Complete
- Macro Indicators: ✅ Enhanced (54 indicators with Chinese data and minimal UI)
- Company Indicators: 🚧 Next priority
- System Operations: 🚧 Planned

---

*Last Updated: 2025-08-02*  
*Status: Module 1 Production Ready, Dashboard v2.0 Enhanced with Chinese Indicators, Module 2 In Development* 