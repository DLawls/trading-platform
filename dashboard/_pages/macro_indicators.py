"""
🌍 Macro Indicators Page
All non-company specific economic indicators in a simple, scrollable grid layout
Complete coverage: FRED (10) + ABS (36) + US Reference (4) = 50 total indicators
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import subprocess
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_reader import data_reader

def run_data_collection():
    """Run Module 1 data collection scripts to fetch fresh data"""
    
    # Show progress indicator
    with st.spinner("🔄 Updating data from all sources..."):
        progress_placeholder = st.empty()
        
        try:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent
            
            # Update FRED Economic Data
            progress_placeholder.info("📊 Updating FRED economic indicators...")
            fred_script = project_root / "financial_data_collector" / "fred_data_collector" / "ingest" / "fred_economic_data.py"
            if fred_script.exists():
                result = subprocess.run([sys.executable, str(fred_script)], 
                                      capture_output=True, text=True, cwd=str(project_root))
                if result.returncode != 0:
                    st.warning(f"⚠️ FRED update warning: {result.stderr[:200]}...")
            
            # Update ABS Economic Data  
            progress_placeholder.info("🏛️ Updating ABS Australian indicators...")
            abs_script = project_root / "financial_data_collector" / "abs_data_collector" / "ingest" / "abs_economic_data.py"
            if abs_script.exists():
                result = subprocess.run([sys.executable, str(abs_script)], 
                                      capture_output=True, text=True, cwd=str(project_root))
                if result.returncode != 0:
                    st.warning(f"⚠️ ABS update warning: {result.stderr[:200]}...")
            
            # Update Yahoo Finance Data (optional - can be heavy)
            # progress_placeholder.info("📈 Updating Yahoo Finance data...")
            # yahoo_script = project_root / "financial_data_collector" / "yahoo_finance_collector" / "ingest" / "yahoo_finance_data.py"
            # if yahoo_script.exists():
            #     result = subprocess.run([sys.executable, str(yahoo_script)], 
            #                           capture_output=True, text=True, cwd=str(project_root))
            
            progress_placeholder.success("✅ Data collection completed! Refreshing dashboard...")
            
        except Exception as e:
            progress_placeholder.error(f"❌ Data collection error: {str(e)}")
            
        # Clear progress after a moment
        import time
        time.sleep(1)
        progress_placeholder.empty()

def show_page(config):
    """Display all macro indicators with real data in a minimal grid"""
    
    # Header with update button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🌍 Macro Economic Indicators")
    with col2:
        if st.button("Update", use_container_width=False):
            run_data_collection()
            st.rerun()
    
    # ============ FRED AUSTRALIAN INDICATORS (10) ============
    
    # Row 1-4: FRED indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Australia CPI
        cpi_value, cpi_units, cpi_date = data_reader.get_fred_indicator("CPALTT01AUQ657N")
        st.metric(
            label="🇦🇺 Consumer Price Index",
            value=data_reader.format_value(cpi_value, cpi_units),
            delta=f"Updated: {cpi_date}" if cpi_date else "No data",
            help="CPALTT01AUQ657N - CPI Total, All Items for Australia"
        )
    
    with col2:
        # Australia Core CPI
        core_cpi_value, core_cpi_units, core_cpi_date = data_reader.get_fred_indicator("CORESTICKM159SFRBATL")
        st.metric(
            label="🇦🇺 Core CPI",
            value=data_reader.format_value(core_cpi_value, core_cpi_units),
            delta=f"Updated: {core_cpi_date}" if core_cpi_date else "No data",
            help="CORESTICKM159SFRBATL - Core Consumer Price Index for Australia"
        )
    
    with col3:
        # Australia Unemployment Rate
        unemployment_value, unemployment_units, unemployment_date = data_reader.get_fred_indicator("LRHUTTTTAUM156S")
        st.metric(
            label="🇦🇺 Unemployment Rate",
            value=data_reader.format_value(unemployment_value, unemployment_units),
            delta=f"Updated: {unemployment_date}" if unemployment_date else "No data",
            help="LRHUTTTTAUM156S - Unemployment Rate for Australia"
        )
    
    with col4:
        # Australia Youth Unemployment Rate (using different indicator)
        youth_unemp_value, youth_unemp_units, youth_unemp_date = data_reader.get_fred_indicator("LRHU24TTAUM156S")
        st.metric(
            label="🇦🇺 Youth Unemployment Rate",
            value=data_reader.format_value(youth_unemp_value, youth_unemp_units),
            delta=f"Updated: {youth_unemp_date}" if youth_unemp_date else "No data",
            help="LRHU24TTAUM156S - Youth Unemployment Rate for Australia"
        )
    
    # Row 2: More FRED indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Australia 3-Month Interest Rate
        interest_3m_value, interest_3m_units, interest_3m_date = data_reader.get_fred_indicator("IR3TIB01AUM156N")
        st.metric(
            label="🇦🇺 3-Month Interest Rate",
            value=data_reader.format_value(interest_3m_value, interest_3m_units),
            delta=f"Updated: {interest_3m_date}" if interest_3m_date else "No data",
            help="IR3TIB01AUM156N - 3-Month Interest Rate for Australia"
        )
    
    with col2:
        # Australia 10-Year Government Bond Rate
        bond_10y_value, bond_10y_units, bond_10y_date = data_reader.get_fred_indicator("IRLTLT01AUM156N")
        st.metric(
            label="🇦🇺 10-Year Government Bond Rate",
            value=data_reader.format_value(bond_10y_value, bond_10y_units),
            delta=f"Updated: {bond_10y_date}" if bond_10y_date else "No data",
            help="IRLTLT01AUM156N - Long-Term Government Bond Yield for Australia"
        )
    
    with col3:
        # Australia Real GDP (using working indicator)
        gdp_value, gdp_units, gdp_date = data_reader.get_fred_indicator("NGDPRSAXDCAUQ")
        st.metric(
            label="🇦🇺 Real GDP",
            value=data_reader.format_value(gdp_value, gdp_units),
            delta=f"Updated: {gdp_date}" if gdp_date else "No data",
            help="NGDPRSAXDCAUQ - Real GDP for Australia"
        )
    
    with col4:
        # Australia Real GDP per Capita (using working indicator)
        gdp_per_capita_value, gdp_per_capita_units, gdp_per_capita_date = data_reader.get_fred_indicator("NYGDPPCAPKDAUS")
        st.metric(
            label="🇦🇺 Real GDP per Capita",
            value=data_reader.format_value(gdp_per_capita_value, gdp_per_capita_units),
            delta=f"Updated: {gdp_per_capita_date}" if gdp_per_capita_date else "No data",
            help="NYGDPPCAPKDAUS - Real GDP per Capita for Australia"
        )
    
    # Row 3: Final FRED indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Australia Current Account Balance
        current_account_value, current_account_units, current_account_date = data_reader.get_fred_indicator("AUSBCABP6USD")
        st.metric(
            label="🇦🇺 Current Account Balance",
            value=data_reader.format_value(current_account_value, current_account_units),
            delta=f"Updated: {current_account_date}" if current_account_date else "No data",
            help="AUSBCABP6USD - Current Account Balance for Australia"
        )
    
    with col2:
        # Australia USD/AUD Exchange Rate
        exchange_rate_value, exchange_rate_units, exchange_rate_date = data_reader.get_fred_indicator("DEXUSAL")
        st.metric(
            label="🇦🇺 USD/AUD Exchange Rate",
            value=data_reader.format_value(exchange_rate_value, exchange_rate_units),
            delta=f"Updated: {exchange_rate_date}" if exchange_rate_date else "No data",
            help="DEXUSAL - USD to AUD Exchange Rate"
        )
    
    with col3:
        # Australia Exports Volume (using working indicator)
        exports_value, exports_units, exports_date = data_reader.get_fred_indicator("XTEXVA01AUA664N")
        st.metric(
            label="🇦🇺 Exports Volume",
            value=data_reader.format_value(exports_value, exports_units),
            delta=f"Updated: {exports_date}" if exports_date else "No data",
            help="XTEXVA01AUA664N - Exports Volume for Australia"
        )
    
    with col4:
        # ABS GDP Chain Volume (first ABS indicator to fill row 3)
        val, units, change, date, name = data_reader.get_abs_indicator_by_index(0)
        st.metric(
            label="🇦🇺 GDP Chain Volume",
            value=data_reader.format_value(val, units),
            delta=f"YoY: {change}" if change else f"Updated: {date}",
            help=f"{name}"
        )
    
    # ============ ABS AUSTRALIAN INDICATORS (35 remaining) ============
    # Continue with remaining 35 ABS indicators (36 total - 1 already shown)
    
    # Continue with remaining 35 ABS indicators  
    abs_start_index = 1  # We already did index 0 (GDP Chain Volume) in row 3 col 4
    abs_indicators_remaining = 35  # 36 total - 1 already shown
    
    for row_start in range(abs_start_index, abs_start_index + abs_indicators_remaining, 4):
        col1, col2, col3, col4 = st.columns(4)
        for col_idx, col in enumerate([col1, col2, col3, col4]):
            abs_idx = row_start + col_idx
            if abs_idx < abs_start_index + abs_indicators_remaining:
                with col:
                    val, units, change, date, name = data_reader.get_abs_indicator_by_index(abs_idx)
                    short_name = name.split(',')[0] if name else f"ABS Indicator {abs_idx}"
                    if len(short_name) > 30:
                        short_name = short_name[:27] + "..."
                    st.metric(
                        label=f"🇦🇺 {short_name}",
                        value=data_reader.format_value(val, units),
                        delta=f"YoY: {change}" if change else f"Updated: {date}",
                        help=f"{name}"
                    )
    
    # ============ US REFERENCE INDICATORS (4) ============
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # US Federal Funds Rate
        us_ffr_value, us_ffr_units, us_ffr_date = data_reader.get_fred_indicator("FEDFUNDS")
        st.metric(
            label="🇺🇸 Federal Funds Rate",
            value=data_reader.format_value(us_ffr_value, us_ffr_units),
            delta=f"Updated: {us_ffr_date}" if us_ffr_date else "No data",
            help="FEDFUNDS - Federal Funds Rate for United States"
        )
    
    with col2:
        # US CPI
        us_cpi_value, us_cpi_units, us_cpi_date = data_reader.get_fred_indicator("CPIAUCSL")
        st.metric(
            label="🇺🇸 Consumer Price Index",
            value=data_reader.format_value(us_cpi_value, us_cpi_units),
            delta=f"Updated: {us_cpi_date}" if us_cpi_date else "No data",
            help="CPIAUCSL - Consumer Price Index for All Urban Consumers"
        )
    
    with col3:
        # US Unemployment Rate
        us_unemp_value, us_unemp_units, us_unemp_date = data_reader.get_fred_indicator("UNRATE")
        st.metric(
            label="🇺🇸 Unemployment Rate",
            value=data_reader.format_value(us_unemp_value, us_unemp_units),
            delta=f"Updated: {us_unemp_date}" if us_unemp_date else "No data",
            help="UNRATE - Unemployment Rate for United States"
        )
    
    with col4:
        # US GDP
        us_gdp_value, us_gdp_units, us_gdp_date = data_reader.get_fred_indicator("GDP")
        st.metric(
            label="🇺🇸 Gross Domestic Product",
            value=data_reader.format_value(us_gdp_value, us_gdp_units),
            delta=f"Updated: {us_gdp_date}" if us_gdp_date else "No data",
            help="GDP - Gross Domestic Product for United States"
        )
    
    # ============ CHINESE INDICATORS (4) ============
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # China Interest Rate
        cn_interest_value, cn_interest_units, cn_interest_date = data_reader.get_fred_indicator("INTDSRCNM193N")
        st.metric(
            label="🇨🇳 Interest Rate",
            value=data_reader.format_value(cn_interest_value, cn_interest_units),
            delta=f"Updated: {cn_interest_date}" if cn_interest_date else "No data",
            help="INTDSRCNM193N - Interest Rates, Discount Rate for China"
        )
    
    with col2:
        # China Consumer Price Index
        cn_cpi_value, cn_cpi_units, cn_cpi_date = data_reader.get_fred_indicator("CHNCPIALLMINMEI")
        st.metric(
            label="🇨🇳 Consumer Price Index",
            value=data_reader.format_value(cn_cpi_value, cn_cpi_units),
            delta=f"Updated: {cn_cpi_date}" if cn_cpi_date else "No data",
            help="CHNCPIALLMINMEI - Consumer Price Index: Total for China"
        )
    
    with col3:
        # China Gross Domestic Product
        cn_gdp_value, cn_gdp_units, cn_gdp_date = data_reader.get_fred_indicator("MKTGDPCNA646NWDB")
        st.metric(
            label="🇨🇳 Gross Domestic Product",
            value=data_reader.format_value(cn_gdp_value, cn_gdp_units),
            delta=f"Updated: {cn_gdp_date}" if cn_gdp_date else "No data",
            help="MKTGDPCNA646NWDB - Gross Domestic Product for China"
        )
    
    with col4:
        # China GDP per Capita
        cn_gdp_per_capita_value, cn_gdp_per_capita_units, cn_gdp_per_capita_date = data_reader.get_fred_indicator("NYGDPPCAPKDCHN")
        st.metric(
            label="🇨🇳 GDP per Capita",
            value=data_reader.format_value(cn_gdp_per_capita_value, cn_gdp_per_capita_units),
            delta=f"Updated: {cn_gdp_per_capita_date}" if cn_gdp_per_capita_date else "No data",
            help="NYGDPPCAPKDCHN - GDP per capita for China"
        )
        
         