#!/usr/bin/env python3
"""
Enhanced FRED Economic Data Monitoring Page
Comprehensive visualization and monitoring for Federal Reserve Economic Data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

def load_fred_data():
    """Load all FRED data with enhanced metadata"""
    data_path = Path(__file__).parent.parent.parent / 'financial_data' / 'economic' / 'fred'
    
    if not data_path.exists():
        return None, []
    
    files = list(data_path.glob('*.parquet'))
    
    if not files:
        return None, []
    
    all_data = []
    file_info = []
    
    for file in files:
        try:
            df = pd.read_parquet(file)
            if not df.empty:
                # Store file information
                file_info.append({
                    'file': file.name,
                    'indicator': df.iloc[0].get('indicator', file.stem),
                    'name': df.iloc[0].get('name', file.stem),
                    'description': df.iloc[0].get('description', 'No description'),
                    'category': df.iloc[0].get('category', 'general'),
                    'priority': df.iloc[0].get('priority', 'medium'),
                    'units': df.iloc[0].get('units', 'Unknown'),
                    'frequency': df.iloc[0].get('frequency', 'Unknown'),
                    'records': len(df),
                    'date_range': f"{df['datetime'].min()} to {df['datetime'].max()}",
                    'latest_value': df.iloc[-1]['value'],
                    'latest_date': df.iloc[-1]['datetime']
                })
                
                # Add metadata to the dataframe
                df['file'] = file.name
                all_data.append(df)
        except Exception as e:
            st.warning(f"Error loading {file.name}: {e}")
    
    combined_df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    return combined_df, file_info

def show_fred_overview(file_info):
    """Show FRED collection overview with enhanced metrics"""
    st.markdown("## 📊 Collection Overview")
    
    if not file_info:
        st.warning("No FRED data found")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📈 Total Indicators", len(file_info))
    
    with col2:
        total_records = sum(info['records'] for info in file_info)
        st.metric("📊 Total Records", f"{total_records:,}")
    
    with col3:
        categories = set(info['category'] for info in file_info)
        st.metric("📋 Categories", len(categories))
    
    with col4:
        # Calculate data freshness
        try:
            latest_dates = [datetime.fromisoformat(info['latest_date'].replace('T', ' ')) for info in file_info]
            most_recent = max(latest_dates)
            days_old = (datetime.now() - most_recent).days
            st.metric("🔄 Data Freshness", f"{days_old} days")
        except:
            st.metric("🔄 Data Freshness", "Unknown")
    
    # Category breakdown
    st.markdown("### 📋 Category Breakdown")
    category_counts = pd.DataFrame(file_info).groupby('category').size().reset_index()
    category_counts.columns = ['category', 'count']
    
    fig_cat = px.bar(
        category_counts, 
        x='category', 
        y='count',
        title="Indicators by Category",
        color='count',
        color_continuous_scale='viridis'
    )
    fig_cat.update_layout(height=400)
    st.plotly_chart(fig_cat, use_container_width=True)

def show_indicator_details(file_info):
    """Show detailed indicator information"""
    st.markdown("## 📈 Indicator Details")
    
    if not file_info:
        return
    
    # Create indicators DataFrame
    df_info = pd.DataFrame(file_info)
    
    # Filter by category
    categories = ['All'] + sorted(df_info['category'].unique().tolist())
    selected_category = st.selectbox("Filter by Category:", categories)
    
    if selected_category != 'All':
        df_info = df_info[df_info['category'] == selected_category]
    
    # Display indicators table
    st.markdown("### 📊 Indicators Summary")
    
    # Prepare display dataframe with renamed columns
    selected_cols = ['name', 'category', 'priority', 'units', 'frequency', 'records', 'latest_value']
    display_data = []
    for _, row in df_info.iterrows():
        display_data.append([
            row['name'], row['category'], row['priority'], 
            row['units'], row['frequency'], row['records'], 
            round(row['latest_value'], 4)
        ])
    
    display_df = pd.DataFrame(display_data, columns=[
        'Name', 'Category', 'Priority', 'Units', 'Frequency', 'Records', 'Latest Value'
    ])
    
    st.dataframe(display_df, use_container_width=True)

def show_time_series_analysis(combined_df, file_info):
    """Show comprehensive time series analysis"""
    st.markdown("## 📈 Time Series Analysis")
    
    if combined_df.empty:
        st.warning("No data available for analysis")
        return
    
    # Indicator selection
    indicators = [info for info in file_info]
    indicator_names = [f"{info['name']} ({info['indicator']})" for info in indicators]
    
    selected_indicators = st.multiselect(
        "Select indicators to analyze:",
        indicator_names,
        default=indicator_names[:3] if len(indicator_names) >= 3 else indicator_names
    )
    
    if not selected_indicators:
        st.warning("Please select at least one indicator")
        return
    
    # Get selected indicator data
    selected_files = []
    for sel in selected_indicators:
        for info in indicators:
            if f"{info['name']} ({info['indicator']})" == sel:
                selected_files.append(info['file'])
                break
    
    # Time series visualization
    st.markdown("### 📊 Time Series Comparison")
    
    # Individual charts option
    chart_type = st.radio("Chart Type:", ["Individual Charts", "Combined Chart"], horizontal=True)
    
    if chart_type == "Individual Charts":
        for file in selected_files:
            df_indicator = combined_df[combined_df['file'] == file].copy()
            if not df_indicator.empty:
                df_indicator['datetime'] = pd.to_datetime(df_indicator['datetime'])
                
                indicator_info = next(info for info in file_info if info['file'] == file)
                
                fig = px.line(
                    df_indicator, 
                    x='datetime', 
                    y='value',
                    title=f"{indicator_info['name']} - {indicator_info['description']}",
                    labels={'value': f"Value ({indicator_info['units']})", 'datetime': 'Date'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show recent statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Latest Value", f"{df_indicator.iloc[-1]['value']:.4f}")
                with col2:
                    st.metric("Mean", f"{df_indicator['value'].mean():.4f}")
                with col3:
                    st.metric("Std Dev", f"{df_indicator['value'].std():.4f}")
                with col4:
                    change = df_indicator.iloc[-1]['value'] - df_indicator.iloc[-2]['value'] if len(df_indicator) > 1 else 0
                    st.metric("Latest Change", f"{change:.4f}")
                
                st.markdown("---")
    
    else:  # Combined Chart
        fig = make_subplots(
            rows=len(selected_files), 
            cols=1,
            subplot_titles=[next(info['name'] for info in file_info if info['file'] == file) for file in selected_files],
            vertical_spacing=0.05
        )
        
        for i, file in enumerate(selected_files, 1):
            df_indicator = combined_df[combined_df['file'] == file].copy()
            if not df_indicator.empty:
                df_indicator['datetime'] = pd.to_datetime(df_indicator['datetime'])
                
                fig.add_trace(
                    go.Scatter(
                        x=df_indicator['datetime'],
                        y=df_indicator['value'],
                        mode='lines',
                        name=next(info['name'] for info in file_info if info['file'] == file),
                        showlegend=False
                    ),
                    row=i, col=1
                )
        
        fig.update_layout(height=300 * len(selected_files), title="Combined Time Series Analysis")
        st.plotly_chart(fig, use_container_width=True)

def show_correlation_analysis(combined_df, file_info):
    """Show correlation analysis between indicators"""
    st.markdown("## 🔗 Correlation Analysis")
    
    if combined_df.empty or len(file_info) < 2:
        st.warning("Need at least 2 indicators for correlation analysis")
        return
    
    # Prepare data for correlation
    correlation_data = {}
    
    for info in file_info:
        df_indicator = combined_df[combined_df['file'] == info['file']].copy()
        if not df_indicator.empty:
            df_indicator['datetime'] = pd.to_datetime(df_indicator['datetime'])
            df_indicator = df_indicator.set_index('datetime')['value']
            correlation_data[info['name']] = df_indicator
    
    if len(correlation_data) < 2:
        st.warning("Not enough data for correlation analysis")
        return
    
    # Create correlation DataFrame
    corr_df = pd.DataFrame(correlation_data)
    
    # Resample to common frequency (monthly) for correlation
    corr_df_monthly = corr_df.resample('M').last().dropna()
    
    if len(corr_df_monthly) < 10:
        st.warning("Not enough overlapping data points for meaningful correlation")
        return
    
    # Calculate correlation matrix
    correlation_matrix = corr_df_monthly.corr()
    
    # Display correlation heatmap
    fig_corr = px.imshow(
        correlation_matrix,
        title="Indicator Correlation Matrix",
        color_continuous_scale='RdBu',
        aspect='auto'
    )
    fig_corr.update_layout(height=600)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Display correlation table
    st.markdown("### 📊 Correlation Coefficients")
    st.dataframe(correlation_matrix.round(3), use_container_width=True)

def show_economic_dashboard(combined_df, file_info):
    """Show economic dashboard with key indicators"""
    st.markdown("## 🎯 Economic Dashboard")
    
    if not file_info:
        return
    
    # Key economic indicators
    key_indicators = {
        'Australian CPI': ['CPALTT01AUQ657N', 'CORESTICKM159SFRBATL'],
        'Unemployment': ['LRHUTTTTAUM156S', 'UNRATE'],
        'Interest Rates': ['IR3TIB01AUM156N', 'FEDFUNDS'],
        'Exchange Rate': ['DEXUSAL']
    }
    
    for category, indicator_codes in key_indicators.items():
        st.markdown(f"### {category}")
        
        available_indicators = [info for info in file_info if info['indicator'] in indicator_codes]
        
        if available_indicators:
            cols = st.columns(len(available_indicators))
            
            for i, info in enumerate(available_indicators):
                with cols[i]:
                    # Get recent data
                    df_indicator = combined_df[combined_df['file'] == info['file']].copy()
                    if not df_indicator.empty:
                        latest_value = info['latest_value']
                        
                        # Calculate change if possible
                        if len(df_indicator) > 1:
                            prev_value = df_indicator.iloc[-2]['value']
                            change = latest_value - prev_value
                            change_pct = (change / prev_value) * 100 if prev_value != 0 else 0
                            
                            st.metric(
                                info['name'],
                                f"{latest_value:.4f} {info['units']}",
                                delta=f"{change_pct:.2f}%"
                            )
                        else:
                            st.metric(
                                info['name'],
                                f"{latest_value:.4f} {info['units']}"
                            )

def show_data_quality_report(file_info):
    """Show comprehensive data quality report"""
    st.markdown("## 🎯 Data Quality Report")
    
    if not file_info:
        return
    
    # Quality metrics
    df_quality = pd.DataFrame(file_info)
    
    # Calculate quality scores
    quality_scores = []
    for info in file_info:
        # Completeness score (based on expected frequency)
        completeness = min(100, (info['records'] / 1000) * 100)  # Assume 1000 is good coverage
        
        # Freshness score
        try:
            latest_date = datetime.fromisoformat(info['latest_date'].replace('T', ' '))
            days_old = (datetime.now() - latest_date).days
            freshness = max(0, (90 - days_old) / 90 * 100)  # 90 days threshold
        except:
            freshness = 50  # Neutral score
        
        # Priority weight
        priority_weights = {'high': 1.0, 'medium': 0.8, 'low': 0.6}
        priority_weight = priority_weights.get(info['priority'], 0.8)
        
        # Overall quality score
        overall_score = (completeness * 0.4 + freshness * 0.6) * priority_weight
        
        quality_scores.append({
            'indicator': info['name'],
            'completeness': completeness,
            'freshness': freshness,
            'priority_weight': priority_weight * 100,
            'overall_score': overall_score
        })
    
    df_scores = pd.DataFrame(quality_scores)
    
    # Display quality metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_quality = df_scores['overall_score'].mean()
        st.metric("📊 Average Quality Score", f"{avg_quality:.1f}%")
    
    with col2:
        high_quality = (df_scores['overall_score'] >= 80).sum()
        st.metric("✅ High Quality Indicators", f"{high_quality}/{len(df_scores)}")
    
    with col3:
        data_coverage = df_quality['records'].sum()
        st.metric("📈 Total Data Points", f"{data_coverage:,}")
    
    # Quality score chart
    fig_quality = px.bar(
        df_scores.sort_values('overall_score', ascending=True),
        x='overall_score',
        y='indicator',
        orientation='h',
        title="Data Quality Scores by Indicator",
        color='overall_score',
        color_continuous_scale='RdYlGn'
    )
    fig_quality.update_layout(height=600)
    st.plotly_chart(fig_quality, use_container_width=True)
    
    # Detailed quality table
    st.markdown("### 📋 Detailed Quality Metrics")
    display_scores = df_scores.round(1)
    display_scores.columns = ['Indicator', 'Completeness %', 'Freshness %', 'Priority Weight %', 'Overall Score %']
    st.dataframe(display_scores, use_container_width=True)

def show_page():
    """Main FRED page function"""
    st.title("🏛️ Enhanced FRED Economic Data")
    st.markdown("""
    **Federal Reserve Economic Data** - Comprehensive monitoring of Australian, US, and global economic indicators
    with advanced analytics and quality monitoring.
    """)
    
    # Load data
    with st.spinner("Loading FRED data..."):
        combined_df, file_info = load_fred_data()
    
    if not file_info:
        st.error("No FRED data found. Please run the FRED collector first.")
        st.code("python3 financial_data_collector/fred_data_collector/ingest/fred_economic_data.py")
        return
    
    # Sidebar navigation
    st.sidebar.markdown("## 📋 Navigation")
    page_options = [
        "📊 Overview",
        "📈 Indicators",
        "📉 Time Series",
        "🔗 Correlations", 
        "🎯 Dashboard",
        "📋 Quality Report"
    ]
    
    selected_page = st.sidebar.selectbox("Select view:", page_options)
    
    # Show selected page
    if selected_page == "📊 Overview":
        show_fred_overview(file_info)
    elif selected_page == "📈 Indicators":
        show_indicator_details(file_info)
    elif selected_page == "📉 Time Series":
        show_time_series_analysis(combined_df, file_info)
    elif selected_page == "🔗 Correlations":
        show_correlation_analysis(combined_df, file_info)
    elif selected_page == "🎯 Dashboard":
        show_economic_dashboard(combined_df, file_info)
    elif selected_page == "📋 Quality Report":
        show_data_quality_report(file_info)
    
    # Footer with collection info
    st.markdown("---")
    st.markdown(f"""
    **Collection Status**: {len(file_info)} indicators active  
    **Data Range**: Historical coverage from 1940s to present  
    **Update Frequency**: Daily collection with automatic quality monitoring  
    **Categories**: {len(set(info['category'] for info in file_info))} economic categories covered
    """)

if __name__ == "__main__":
    show_page() 