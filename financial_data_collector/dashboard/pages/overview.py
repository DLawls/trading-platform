#!/usr/bin/env python3
"""
System Overview Page
Main overview of all collectors and system health.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'shared'))

from components.status_monitor import display_system_overview, display_data_freshness_summary
from monitoring.health_check import generate_health_report
from utils.data_validation import check_data_completeness

def show_collection_summary():
    """Show summary of recent collection activities"""
    st.subheader("📊 Recent Collection Activity")
    
    base_path = Path(__file__).parent.parent.parent
    
    # Mock data for now - in real implementation, read from logs
    collection_data = [
        {
            'Collector': 'Yahoo Finance',
            'Data Type': 'OHLCV',
            'Last Run': datetime.now() - timedelta(hours=2),
            'Status': '✅ Success',
            'Files Collected': 50,
            'Duration': '45s'
        },
        {
            'Collector': 'Yahoo Finance', 
            'Data Type': 'Fundamentals',
            'Last Run': datetime.now() - timedelta(hours=3),
            'Status': '✅ Success',
            'Files Collected': 38,
            'Duration': '67s'
        },
        {
            'Collector': 'FRED Economic',
            'Data Type': 'Economic',
            'Last Run': datetime.now() - timedelta(hours=1),
            'Status': '✅ Success',
            'Files Collected': 3,
            'Duration': '12s'
        },
        {
            'Collector': 'ABS Australian',
            'Data Type': 'Economic',
            'Last Run': None,
            'Status': '⚪ Not Active',
            'Files Collected': 0,
            'Duration': '-'
        }
    ]
    
    df = pd.DataFrame(collection_data)
    st.dataframe(df, use_container_width=True)

def show_data_metrics():
    """Show key data metrics and KPIs"""
    st.subheader("📈 Key Metrics")
    
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / 'financial_data'
    
    if not data_path.exists():
        st.error("Data directory not found")
        return
    
    # Calculate metrics
    total_files = 0
    total_size_mb = 0
    data_types_info = {}
    
    for data_type_dir in data_path.iterdir():
        if data_type_dir.is_dir():
            files = list(data_type_dir.glob('*.parquet'))
            file_count = len(files)
            type_size_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
            
            data_types_info[data_type_dir.name] = {
                'files': file_count,
                'size_mb': type_size_mb
            }
            
            total_files += file_count
            total_size_mb += type_size_mb
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📁 Total Data Files",
            value=total_files,
            delta=None
        )
    
    with col2:
        st.metric(
            label="💾 Total Data Size",
            value=f"{total_size_mb:.1f} MB",
            delta=None
        )
    
    with col3:
        st.metric(
            label="📊 Data Types",
            value=len(data_types_info),
            delta=None
        )
    
    with col4:
        # Calculate average file size
        avg_size_kb = (total_size_mb * 1024) / total_files if total_files > 0 else 0
        st.metric(
            label="📏 Avg File Size",
            value=f"{avg_size_kb:.1f} KB",
            delta=None
        )

def show_quick_actions():
    """Show quick action buttons"""
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Run All Collections", type="primary"):
            st.info("🚀 Triggering all data collections...")
            # In real implementation, trigger orchestration scripts
    
    with col2:
        if st.button("🔍 Data Quality Check"):
            st.info("🔍 Running comprehensive data quality checks...")
    
    with col3:
        if st.button("📊 Generate Report"):
            st.info("📊 Generating comprehensive system report...")
    
    with col4:
        if st.button("🧹 Cleanup Old Data"):
            st.info("🧹 Starting data cleanup process...")

def show_alerts_notifications():
    """Show system alerts and notifications"""
    st.subheader("🚨 Alerts & Notifications")
    
    # Mock alerts - in real implementation, read from monitoring system
    alerts = [
        {
            'type': 'warning',
            'message': 'OHLCV data for 2 tickers is older than 24 hours',
            'timestamp': datetime.now() - timedelta(hours=1)
        },
        {
            'type': 'info',
            'message': 'FRED data collection completed successfully',
            'timestamp': datetime.now() - timedelta(minutes=30)
        }
    ]
    
    if alerts:
        for alert in alerts:
            if alert['type'] == 'warning':
                st.warning(f"⚠️ {alert['message']} ({alert['timestamp'].strftime('%H:%M')})")
            elif alert['type'] == 'error':
                st.error(f"❌ {alert['message']} ({alert['timestamp'].strftime('%H:%M')})")
            else:
                st.info(f"ℹ️ {alert['message']} ({alert['timestamp'].strftime('%H:%M')})")
    else:
        st.success("✅ No active alerts")

def show_page():
    """Main overview page function"""
    st.title("📊 Module 1 - System Overview")
    st.markdown("Comprehensive monitoring for all financial data collectors")
    
    # System status overview
    display_system_overview()
    
    st.markdown("---")
    
    # Key metrics
    show_data_metrics()
    
    st.markdown("---")
    
    # Recent activity
    show_collection_summary()
    
    st.markdown("---")
    
    # Data freshness
    display_data_freshness_summary()
    
    st.markdown("---")
    
    # Quick actions
    show_quick_actions()
    
    st.markdown("---")
    
    # Alerts
    show_alerts_notifications()
    
    # Auto-refresh option
    if st.checkbox("🔄 Auto-refresh (30s)", value=False):
        st.rerun() 