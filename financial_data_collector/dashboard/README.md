# 📊 Unified Financial Data Collector Dashboard

## 🎯 **Overview**
Centralized monitoring and visualization system for all Module 1 financial data collectors.

## 🚀 **Quick Start**

### **Launch Dashboard**
```bash
# From the dashboard directory
cd financial_data_collector/dashboard
python3 launch_dashboard.py

# Or directly with Streamlit
streamlit run app.py
```

### **Access Dashboard**
- **URL**: http://localhost:8501
- **Auto-opens in your browser**

## 📁 **Structure**

```
dashboard/
├── app.py                    # Main dashboard application
├── launch_dashboard.py       # Convenient launcher script
├── config/
│   └── dashboard_config.yaml # Dashboard configuration
├── pages/                    # Individual monitoring pages
│   ├── overview.py           # System overview
│   ├── yahoo_finance.py      # Yahoo Finance monitoring
│   ├── fred_economic.py      # FRED economic data
│   ├── abs_australian.py     # ABS Australian data
│   └── alpaca_alternative.py # Alpaca premium data
└── components/               # Reusable UI components
    ├── status_monitor.py     # Status monitoring widgets
    ├── data_visualizer.py    # Chart components
    └── quality_reports.py    # Data quality displays
```

## 📊 **Features**

### **System Overview**
- **🏥 Health monitoring** for all collectors
- **📊 Real-time metrics** and KPIs
- **🚨 Alert notifications** and system status
- **📈 Data freshness** tracking

### **Collector-Specific Monitoring**
- **📈 Yahoo Finance**: OHLCV charts, fundamentals, events
- **🏛️ FRED Economic**: Economic indicator time series
- **🇦🇺 ABS Australian**: Australian statistics (planned)
- **🚀 Alpaca Premium**: Premium market data (planned)

### **Data Visualization**
- **📊 Interactive charts** with Plotly
- **📈 Candlestick charts** for OHLC data
- **📉 Time series plots** for economic data
- **📋 Data tables** with filtering and search

### **System Management**
- **🔄 Collection controls** for each collector
- **🔍 Data quality checks** and validation
- **📊 Comprehensive reporting** and metrics
- **⚡ Quick actions** for common tasks

## ⚙️ **Configuration**

### **Dashboard Settings**
Edit `config/dashboard_config.yaml`:
```yaml
dashboard:
  title: "Module 1 - Financial Data Collector"
  refresh_interval: 30
  auto_refresh: false

collectors:
  yahoo_finance:
    status: "active"
    name: "Yahoo Finance"
    icon: "📈"
```

### **Shared Configuration**
Uses centralized config from `../shared/config/sources.yaml`:
- **API keys** and endpoints
- **Global settings** and paths
- **Logging configuration**

## 🔧 **Dependencies**

### **Required Packages**
```bash
pip install streamlit plotly pandas pyyaml
```

### **Optional Packages**
```bash
pip install psutil  # For system monitoring
```

## 📈 **Usage Examples**

### **Monitor System Health**
1. Navigate to **📊 System Overview**
2. Check overall system status
3. Review collector health metrics
4. Monitor data freshness

### **Analyze Market Data**
1. Go to **📈 Yahoo Finance**
2. Select OHLCV data tab
3. Choose ticker from dropdown
4. View candlestick charts and volume

### **Track Economic Indicators**
1. Visit **🏛️ FRED Economic**
2. Select economic indicator
3. View time series charts
4. Analyze recent data trends

### **Run Data Collection**
1. Use **⚡ Quick Actions** in sidebar
2. Click **🔄 Collect** for all collectors
3. Monitor progress in real-time
4. Check completion status

## 🚨 **Troubleshooting**

### **Dashboard Won't Start**
```bash
# Check Streamlit installation
pip install --upgrade streamlit

# Run directly
streamlit run app.py --server.port 8502
```

### **Import Errors**
```bash
# Ensure shared utilities are accessible
export PYTHONPATH="${PYTHONPATH}:/path/to/financial_data_collector"
```

### **No Data Displayed**
- **Check data directory**: `../financial_data/`
- **Verify collector status**: Run individual collectors
- **Check permissions**: Ensure read access to data files

## 🔄 **Updates & Maintenance**

### **Adding New Collectors**
1. Create new page in `pages/`
2. Add collector to `config/dashboard_config.yaml`
3. Update `app.py` routing
4. Add status monitoring to `components/status_monitor.py`

### **Customizing Visualizations**
1. Edit `components/data_visualizer.py`
2. Add new chart types
3. Update page-specific plotting functions

## 📚 **Related Documentation**
- **[Module 1 Design Document](../../Docs/Module_1_Financial_Data_Collector/)**
- **[Shared Utilities Documentation](../shared/)**
- **[Individual Collector READMEs](../*/README.md)**

---

**🏛️ Module 1 - Financial Data Collector Dashboard**  
*Unified monitoring for all data collection services* 