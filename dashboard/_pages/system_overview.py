"""
📊 System Overview Page
High-level system health and key performance metrics
"""

import streamlit as st
import pandas as pd
from pathlib import Path

def show_page(config):
    """Display system overview page"""
    
    st.markdown("## 📊 System Overview")
    st.markdown("*High-level system health and key performance metrics*")
    st.markdown("---")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 Data Collection Success Rate",
            value="100%",
            delta="0% (Last 7 days)",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="🕐 Last Update",
            value="2 hours ago",
            delta="On schedule",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="🏢 ASX 50 Coverage",
            value="50/50",
            delta="Complete",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="🌍 Macro Indicators",
            value="50/50",
            delta="All active",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # System health summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 **System Health**")
        
        # Data source status
        st.markdown("**📊 Data Sources**")
        data_sources = [
            ("Yahoo Finance", "✅ Active", "ASX 50 companies"),
            ("FRED Economic", "✅ Active", "14 indicators"),
            ("ABS Australian", "✅ Active", "36 indicators")
        ]
        
        for source, status, coverage in data_sources:
            st.markdown(f"• **{source}**: {status} - *{coverage}*")
        
        st.markdown("**⚡ Collection Performance**")
        st.markdown("• Average collection time: ~10 minutes")
        st.markdown("• Data freshness: < 2 hours")
        st.markdown("• Storage usage: ~50MB/day")
        st.markdown("• Error rate: 0%")
    
    with col2:
        st.markdown("### 📋 **Data Coverage Summary**")
        
        # Macro indicators breakdown
        st.markdown("**🌍 Macro Indicators (50 total)**")
        st.markdown("• 🇦🇺 Australian Economy: 46 indicators")
        st.markdown("  - FRED API: 10 indicators")
        st.markdown("  - ABS Web: 36 key indicators")
        st.markdown("• 🇺🇸 US Reference: 4 indicators")
        
        # Company indicators breakdown  
        st.markdown("**🏢 Company Indicators (ASX 50)**")
        st.markdown("• 📈 Market Data: OHLCV + Market Cap")
        st.markdown("• 💰 Fundamentals: 6 key financial metrics")
        st.markdown("• 📅 Events: Earnings + Dividends")
        st.markdown("• 🏦 Sectors: All 11 GICS sectors covered")
    
    st.markdown("---")
    
    # Recent activity
    st.markdown("### 📝 **Recent Activity**")
    
    # Sample recent activity data
    recent_activity = pd.DataFrame({
        'Time': ['10:30 AM', '09:45 AM', '09:15 AM', '08:30 AM', '07:45 AM'],
        'Event': [
            'Daily OHLCV collection completed',
            'ABS economic indicators updated',
            'FRED API data refresh completed',
            'ASX 50 fundamentals updated',
            'System health check passed'
        ],
        'Status': ['✅ Success', '✅ Success', '✅ Success', '✅ Success', '✅ Success'],
        'Details': [
            '50/50 companies processed',
            '36/36 indicators collected',
            '14/14 indicators updated',
            '50/50 companies updated',
            'All systems operational'
        ]
    })
    
    st.dataframe(recent_activity, use_container_width=True, hide_index=True)
    
    # Quick navigation
    st.markdown("---")
    st.markdown("### 🚀 **Quick Navigation**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("🌍 View Macro Indicators", use_container_width=True, disabled=True, help="Use navigation sidebar")
    
    with col2:
        st.button("🏢 View ASX 50 Companies", use_container_width=True, disabled=True, help="Use navigation sidebar")
    
    with col3:
        st.button("⚙️ System Operations", use_container_width=True, disabled=True, help="Use navigation sidebar") 