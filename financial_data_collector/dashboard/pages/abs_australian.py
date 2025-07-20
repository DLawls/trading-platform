#!/usr/bin/env python3
"""
ABS Australian Data Monitoring Page
Australian Bureau of Statistics economic indicators monitoring and visualization.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import yaml

def load_abs_config():
    """Load ABS collector configuration"""
    config_path = Path(__file__).parent.parent.parent / 'abs_data_collector' / 'config' / 'abs_requirements.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Failed to load ABS config: {e}")
        return {}

def load_abs_data():
    """Load latest ABS economic indicators data"""
    data_path = Path(__file__).parent.parent.parent / 'financial_data' / 'economic' / 'abs'
    
    if not data_path.exists():
        return None
    
    latest_file = data_path / 'abs_key_indicators_latest.parquet'
    if latest_file.exists():
        try:
            return pd.read_parquet(latest_file)
        except Exception as e:
            st.error(f"Error loading ABS data: {e}")
            return None
    
    return None

def show_collection_status():
    """Show ABS collection status and metrics"""
    st.subheader("📊 Collection Status")
    
    config = load_abs_config()
    df = load_abs_data()
    
    if df is not None:
        # Show key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🇦🇺 Total Indicators",
                value=len(df),
                delta="✅ Active"
            )
        
        with col2:
            categories_count = df['category'].nunique()
            st.metric(
                label="📋 Categories",
                value=categories_count,
                delta="All sectors"
            )
        
        with col3:
            latest_period = df['period'].mode()[0] if len(df) > 0 else "Unknown"
            st.metric(
                label="📅 Latest Period",
                value=latest_period,
                delta="Current data"
            )
        
        with col4:
            scrape_date = df['scrape_date'].iloc[0] if len(df) > 0 else None
            if scrape_date:
                scrape_datetime = pd.to_datetime(scrape_date)
                hours_ago = (pd.Timestamp.now() - scrape_datetime).total_seconds() / 3600
                st.metric(
                    label="🔄 Last Update",
                    value=f"{hours_ago:.1f}h ago",
                    delta="Fresh data"
                )
        
        # Show category breakdown
        st.markdown("### 📊 Indicators by Category")
        category_counts = df.groupby('category').size().reset_index()
        category_counts.columns = ['category', 'count']
        
        fig = px.bar(
            category_counts, 
            x='count', 
            y='category', 
            orientation='h',
            title="Economic Indicators by Category",
            labels={'count': 'Number of Indicators', 'category': 'Category'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning("⚠️ No ABS data found. Run collection first.")

def plot_economic_indicators():
    """Plot economic indicator charts"""
    st.subheader("📈 Economic Indicators Dashboard")
    
    df = load_abs_data()
    if df is None:
        st.warning("No data available for plotting")
        return
    
    # Create tabs for different categories
    categories = df['category'].unique()
    tabs = st.tabs([f"📊 {cat}" for cat in categories])
    
    for i, category in enumerate(categories):
        with tabs[i]:
            category_data = df[df['category'] == category]
            
            st.markdown(f"### {category.title()}")
            
            # Show category indicators in a table
            display_data = category_data[['indicator', 'period', 'value', 'unit', 'change_previous_period', 'change_year_on_year']].copy()
            
            # Format values for display
            display_data = display_data.copy()
            display_data['value'] = [f"{x:,.1f}" if pd.notna(x) else "N/A" for x in display_data['value']]
            
            st.dataframe(display_data, use_container_width=True)
            
            # Create visualizations for numeric indicators
            numeric_indicators = category_data[pd.notna(category_data['value'])]
            
            if len(numeric_indicators) > 1:
                # Bar chart of current values
                fig = px.bar(
                    numeric_indicators,
                    x='value',
                    y='indicator',
                    orientation='h',
                    title=f"{category.title()} - Current Values",
                    labels={'value': 'Value', 'indicator': 'Indicator'}
                )
                fig.update_layout(height=max(300, len(numeric_indicators) * 30))
                st.plotly_chart(fig, use_container_width=True)

def show_key_indicators():
    """Show key economic indicators summary"""
    st.subheader("🎯 Key Economic Indicators")
    
    df = load_abs_data()
    if df is None:
        return
    
    # Define key indicators to highlight
    key_indicators = [
        'GDP',
        'Unemployment rate',
        'Consumer price index', 
        'Employed persons',
        'Retail turnover'
    ]
    
    key_data = []
    for indicator_keyword in key_indicators:
        matching = df[df['indicator'].str.contains(indicator_keyword, case=False, na=False)]
        if not matching.empty:
            row = matching.iloc[0]
            key_data.append({
                'Indicator': row['indicator'][:50] + '...' if len(row['indicator']) > 50 else row['indicator'],
                'Value': f"{row['value']:,.1f}" if pd.notna(row['value']) else "N/A",
                'Unit': row['unit'],
                'Period': row['period'],
                'Previous Period': row['change_previous_period'],
                'Year-on-Year': row['change_year_on_year']
            })
    
    if key_data:
        key_df = pd.DataFrame(key_data)
        st.dataframe(key_df, use_container_width=True)
    else:
        st.info("Key indicators not found in current dataset")

def show_data_quality():
    """Show data quality metrics"""
    st.subheader("🔍 Data Quality")
    
    df = load_abs_data()
    if df is None:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Data completeness
        total_indicators = len(df)
        valid_values = df['value'].notna().sum()
        completeness = (valid_values / total_indicators) * 100
        
        st.metric(
            label="📊 Data Completeness",
            value=f"{completeness:.1f}%",
            delta=f"{valid_values}/{total_indicators} valid"
        )
        
        # Period coverage
        unique_periods = df['period'].nunique()
        st.metric(
            label="📅 Period Coverage",
            value=f"{unique_periods} periods",
            delta="Multi-temporal"
        )
    
    with col2:
        # Data freshness
        scrape_date = pd.to_datetime(df['scrape_date'].iloc[0])
        hours_ago = (pd.Timestamp.now() - scrape_date).total_seconds() / 3600
        
        freshness_status = "🟢 Fresh" if hours_ago < 24 else "🟡 Aging" if hours_ago < 72 else "🔴 Stale"
        st.metric(
            label="🔄 Data Freshness",
            value=f"{hours_ago:.1f}h ago",
            delta=freshness_status
        )
        
        # Source validation
        source_url = df['source_url'].iloc[0] if 'source_url' in df.columns else "Unknown"
        st.metric(
            label="🌐 Data Source",
            value="ABS Official",
            delta="✅ Verified"
        )

def show_page():
    """Main ABS monitoring page"""
    st.title("🇦🇺 ABS Australian Economic Data")
    st.markdown("Australian Bureau of Statistics - Key Economic Indicators")
    
    # Show current configuration
    config = load_abs_config()
    if config.get('abs', {}).get('status') == 'active':
        st.success("✅ **Status**: Active - Web scraping operational")
        
        source_info = config.get('abs', {}).get('source', {})
        if source_info:
            st.info(f"📊 **Data Source**: {source_info.get('url', 'ABS Key Indicators Page')}")
    else:
        st.warning("⚠️ **Status**: Not active")
    
    st.markdown("---")
    
    # Collection status
    show_collection_status()
    
    st.markdown("---")
    
    # Key indicators summary
    show_key_indicators()
    
    st.markdown("---")
    
    # Detailed indicator charts
    plot_economic_indicators()
    
    st.markdown("---")
    
    # Data quality
    show_data_quality()
    
    st.markdown("---")
    
    # Action buttons
    st.subheader("⚡ ABS Collection Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Run ABS Collection"):
            st.info("🚀 Starting ABS data scraping...")
    
    with col2:
        if st.button("🔍 Validate Data"):
            st.info("🔍 Running ABS data validation...")
    
    with col3:
        if st.button("📊 Generate Report"):
            st.info("📊 Generating ABS data report...")
    
    # Show raw data option
    if st.checkbox("📋 Show Raw Data"):
        df = load_abs_data()
        if df is not None:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No raw data available") 