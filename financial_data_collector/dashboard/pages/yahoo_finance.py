#!/usr/bin/env python3
"""
Yahoo Finance Collector Monitoring Page
Specific monitoring and visualization for Yahoo Finance data collection.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import yaml
import sys
from datetime import datetime, timedelta

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'shared'))

def load_yahoo_config():
    """Load Yahoo Finance collector configuration"""
    config_path = Path(__file__).parent.parent.parent / 'yahoo_finance_collector' / 'config' / 'data_requirements.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Failed to load Yahoo Finance config: {e}")
        return {}

def load_data_files(data_type: str) -> dict:
    """Load data files for a specific type"""
    data_dir = Path(__file__).parent.parent.parent / 'financial_data' / data_type
    data_files = {}
    
    if data_dir.exists():
        for file_path in data_dir.glob('*.parquet'):
            try:
                df = pd.read_parquet(file_path)
                data_files[file_path.name] = df
            except Exception as e:
                st.error(f"Error loading {file_path.name}: {e}")
    
    return data_files

def show_collection_status():
    """Show Yahoo Finance collection status"""
    st.subheader("📊 Collection Status")
    
    config = load_yahoo_config()
    data_path = Path(__file__).parent.parent.parent / 'financial_data'
    
    # Check OHLCV data
    ohlcv_dir = data_path / 'ohlcv'
    ohlcv_files = len(list(ohlcv_dir.glob('*.parquet'))) if ohlcv_dir.exists() else 0
    expected_ohlcv = len(config.get('ohlcv', {}).get('tickers', []))
    
    # Check fundamentals data
    fundamentals_dir = data_path / 'fundamentals'
    fundamentals_files = len(list(fundamentals_dir.glob('*.parquet'))) if fundamentals_dir.exists() else 0
    expected_fundamentals = len(config.get('fundamentals', {}).get('tickers', []))
    
    # Check events data
    events_dir = data_path / 'events'
    events_files = len(list(events_dir.glob('*.parquet'))) if events_dir.exists() else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        completion_rate = (ohlcv_files / expected_ohlcv * 100) if expected_ohlcv > 0 else 0
        st.metric(
            label="📈 OHLCV Data",
            value=f"{ohlcv_files}/{expected_ohlcv}",
            delta=f"{completion_rate:.1f}% complete"
        )
    
    with col2:
        completion_rate = (fundamentals_files / expected_fundamentals * 100) if expected_fundamentals > 0 else 0
        st.metric(
            label="📊 Fundamentals",
            value=f"{fundamentals_files}/{expected_fundamentals}",
            delta=f"{completion_rate:.1f}% complete"
        )
    
    with col3:
        st.metric(
            label="📅 Events",
            value=events_files,
            delta="Earnings & Dividends"
        )

def plot_ohlcv_data():
    """Display OHLCV data visualization"""
    st.subheader("📈 OHLCV Data Visualization")
    
    data_files = load_data_files('ohlcv')
    
    if not data_files:
        st.warning("No OHLCV data found")
        return
    
    # Select ticker
    file_options = list(data_files.keys())
    selected_file = st.selectbox("Select ticker:", file_options)
    
    if selected_file and selected_file in data_files:
        df = data_files[selected_file]
        
        # Display basic info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Data Points", len(df))
        with col2:
            if 'Date' in df.columns:
                st.metric("Date Range", f"{df['Date'].min()} to {df['Date'].max()}")
        with col3:
            if 'Close' in df.columns:
                st.metric("Latest Close", f"${df['Close'].iloc[-1]:.2f}")
        
        # Create candlestick chart
        if all(col in df.columns for col in ['Date', 'Open', 'High', 'Low', 'Close']):
            fig = go.Figure(data=[go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="OHLC"
            )])
            
            fig.update_layout(
                title=f"OHLC Chart - {selected_file}",
                xaxis_title="Date",
                yaxis_title="Price (AUD)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            if 'Volume' in df.columns:
                vol_fig = px.bar(df, x='Date', y='Volume', title=f"Volume - {selected_file}")
                vol_fig.update_layout(height=300)
                st.plotly_chart(vol_fig, use_container_width=True)
        
        # Show recent data
        if st.checkbox("Show Recent Data"):
            st.dataframe(df.tail(10), use_container_width=True)

def plot_fundamentals_data():
    """Display fundamentals data"""
    st.subheader("📊 Fundamentals Data")
    
    data_files = load_data_files('fundamentals')
    
    if not data_files:
        st.warning("No fundamentals data found")
        return
    
    # Select ticker
    file_options = list(data_files.keys())
    selected_file = st.selectbox("Select fundamentals file:", file_options, key="fundamentals_select")
    
    if selected_file and selected_file in data_files:
        df = data_files[selected_file]
        
        # Display basic info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Data Points", len(df))
        with col2:
            st.metric("Available Fields", len(df.columns))
        
        # Show data table
        st.dataframe(df, use_container_width=True)

def plot_events_data():
    """Display events data"""
    st.subheader("📅 Events Data")
    
    data_files = load_data_files('events')
    
    if not data_files:
        st.warning("No events data found")
        return
    
    # Separate earnings and dividends
    earnings_files = [f for f in data_files.keys() if 'earnings' in f]
    dividend_files = [f for f in data_files.keys() if 'dividends' in f]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**📈 Earnings Events**: {len(earnings_files)} files")
        if earnings_files:
            selected_earnings = st.selectbox("Select earnings file:", earnings_files, key="earnings_select")
            if selected_earnings:
                df = data_files[selected_earnings]
                st.dataframe(df.head(), use_container_width=True)
    
    with col2:
        st.write(f"**💰 Dividend Events**: {len(dividend_files)} files")
        if dividend_files:
            selected_dividends = st.selectbox("Select dividends file:", dividend_files, key="dividends_select")
            if selected_dividends:
                df = data_files[selected_dividends]
                st.dataframe(df.head(), use_container_width=True)

def show_data_quality_metrics():
    """Show data quality metrics for Yahoo Finance data"""
    st.subheader("🔍 Data Quality Metrics")
    
    data_path = Path(__file__).parent.parent.parent / 'financial_data'
    
    quality_data = []
    
    for data_type in ['ohlcv', 'fundamentals', 'events']:
        data_dir = data_path / data_type
        if data_dir.exists():
            files = list(data_dir.glob('*.parquet'))
            total_files = len(files)
            
            # Check file sizes
            total_size_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
            avg_size_kb = (total_size_mb * 1024) / total_files if total_files > 0 else 0
            
            # Check file ages
            if files:
                newest_file = max(files, key=lambda f: f.stat().st_mtime)
                oldest_file = min(files, key=lambda f: f.stat().st_mtime)
                newest_age = (datetime.now().timestamp() - newest_file.stat().st_mtime) / 3600
                oldest_age = (datetime.now().timestamp() - oldest_file.stat().st_mtime) / 3600
            else:
                newest_age = oldest_age = 0
            
            quality_data.append({
                'Data Type': data_type.upper(),
                'File Count': total_files,
                'Total Size (MB)': f"{total_size_mb:.2f}",
                'Avg Size (KB)': f"{avg_size_kb:.1f}",
                'Newest Age (hrs)': f"{newest_age:.1f}",
                'Oldest Age (hrs)': f"{oldest_age:.1f}"
            })
    
    if quality_data:
        df = pd.DataFrame(quality_data)
        st.dataframe(df, use_container_width=True)

def show_page():
    """Main Yahoo Finance monitoring page"""
    st.title("📈 Yahoo Finance Collector")
    st.markdown("Monitoring ASX 50 market data collection")
    
    # Collection status
    show_collection_status()
    
    st.markdown("---")
    
    # Create tabs for different data types
    tab1, tab2, tab3, tab4 = st.tabs(["📈 OHLCV", "📊 Fundamentals", "📅 Events", "🔍 Quality"])
    
    with tab1:
        plot_ohlcv_data()
    
    with tab2:
        plot_fundamentals_data()
    
    with tab3:
        plot_events_data()
    
    with tab4:
        show_data_quality_metrics()
    
    # Action buttons
    st.markdown("---")
    st.subheader("⚡ Yahoo Finance Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Run OHLCV Collection"):
            st.info("🚀 Starting OHLCV data collection...")
    
    with col2:
        if st.button("📊 Run Fundamentals"):
            st.info("🚀 Starting fundamentals collection...")
    
    with col3:
        if st.button("📅 Run Events"):
            st.info("🚀 Starting events collection...") 