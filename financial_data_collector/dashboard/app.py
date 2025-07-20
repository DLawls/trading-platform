#!/usr/bin/env python3
"""
Unified Financial Data Collector Dashboard
Centralized monitoring system for all data collectors in Module 1.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent / 'shared'))

# Import page modules
from pages import overview, yahoo_finance, fred_economic, abs_australian, alpaca_alternative
from components import status_monitor, data_visualizer, quality_reports

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Module 1 - Financial Data Collector Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def create_sidebar():
    """Create navigation sidebar"""
    st.sidebar.title("🏛️ Module 1 Dashboard")
    st.sidebar.markdown("**Financial Data Collector**")
    st.sidebar.markdown("---")
    
    # Navigation
    pages = {
        "📊 System Overview": "overview",
        "📈 Yahoo Finance": "yahoo_finance", 
        "🏛️ FRED Economic": "fred_economic",
        "🇦🇺 ABS Australian": "abs_australian",
        "🚀 Alpaca Premium": "alpaca_alternative"
    }
    
    selected_page = st.sidebar.selectbox(
        "📋 Select Monitor:",
        list(pages.keys())
    )
    
    st.sidebar.markdown("---")
    
    # Quick Actions
    st.sidebar.subheader("⚡ Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Collect", key="collect_all"):
            st.info("🚀 Triggering data collection...")
    
    with col2:
        if st.button("🔍 Validate", key="validate_all"):
            st.info("🔍 Running data validation...")
    
    if st.sidebar.button("📊 Full Report", key="full_report"):
        st.info("📊 Generating comprehensive report...")
    
    st.sidebar.markdown("---")
    
    # System Status Summary
    st.sidebar.subheader("🚥 System Status")
    status_monitor.display_sidebar_status()
    
    return pages[selected_page]

def main():
    """Main dashboard application"""
    setup_page_config()
    
    # Create sidebar and get selected page
    selected_page = create_sidebar()
    
    # Route to appropriate page
    if selected_page == "overview":
        overview.show_page()
    elif selected_page == "yahoo_finance":
        yahoo_finance.show_page()
    elif selected_page == "fred_economic":
        fred_economic.show_page()
    elif selected_page == "abs_australian":
        abs_australian.show_page()
    elif selected_page == "alpaca_alternative":
        alpaca_alternative.show_page()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🏛️ **Module 1 - Financial Data Collector** | "
        "📊 Unified monitoring for all data collection services"
    )

if __name__ == "__main__":
    main() 