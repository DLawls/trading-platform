#!/usr/bin/env python3
"""
Status Monitor Component
Displays real-time status of all collectors and system health.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import yaml
import sys

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'shared'))

from monitoring.health_check import generate_health_report, check_collector_status
from utils.data_validation import check_data_freshness, check_data_completeness

def load_dashboard_config() -> dict:
    """Load dashboard configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'dashboard_config.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def get_status_color(status: str) -> str:
    """Get color for status indicator"""
    colors = {
        'active': '#28a745',      # Green
        'healthy': '#28a745',     # Green
        'configured': '#ffc107',  # Yellow
        'degraded': '#ffc107',    # Yellow
        'warning': '#ffc107',     # Yellow
        'incomplete': '#fd7e14',  # Orange
        'error': '#dc3545',       # Red
        'critical': '#dc3545',    # Red
        'not_found': '#6c757d',   # Gray
        'planned': '#6c757d'      # Gray
    }
    return colors.get(status.lower(), '#6c757d')

def display_collector_status(collector_name: str, status_info: dict):
    """Display status for a single collector"""
    config = load_dashboard_config()
    collector_config = config.get('collectors', {}).get(collector_name, {})
    
    # Get display info
    display_name = collector_config.get('name', collector_name.replace('_', ' ').title())
    icon = collector_config.get('icon', '📊')
    description = collector_config.get('description', 'Data collector service')
    
    # Status color and icon
    status = status_info.get('status', 'unknown')
    color = get_status_color(status)
    
    status_icons = {
        'active': '🟢',
        'healthy': '🟢',
        'configured': '🟡',
        'degraded': '🟡',
        'warning': '🟡',
        'incomplete': '🟠',
        'error': '🔴',
        'critical': '🔴',
        'not_found': '🔴',
        'planned': '⚪'
    }
    status_icon = status_icons.get(status, '❓')
    
    # Create status card
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"<h2 style='text-align: center; margin: 0;'>{icon}</h2>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{display_name}**")
            st.markdown(f"<small>{description}</small>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<div style='font-size: 24px;'>{status_icon}</div>"
                f"<div style='color: {color}; font-weight: bold; font-size: 12px;'>{status.upper()}</div>"
                f"</div>", 
                unsafe_allow_html=True
            )

def display_sidebar_status():
    """Display condensed status in sidebar"""
    base_path = Path(__file__).parent.parent.parent
    
    try:
        # Quick health check
        health_report = generate_health_report(base_path)
        overall_status = health_report.get('overall_status', 'unknown')
        
        # Overall status indicator
        status_colors = {
            'healthy': '🟢',
            'degraded': '🟡', 
            'critical': '🔴'
        }
        status_icon = status_colors.get(overall_status, '❓')
        
        st.markdown(f"**Overall: {status_icon} {overall_status.upper()}**")
        
        # Collector summary
        collectors = health_report.get('collectors', {})
        active_count = sum(1 for c in collectors.values() if c.get('status') == 'active')
        total_count = len(collectors)
        
        st.markdown(f"Active Collectors: {active_count}/{total_count}")
        
        # Data summary
        data_info = health_report.get('data', {})
        total_files = data_info.get('total_files', 0)
        total_size = data_info.get('total_size_mb', 0)
        
        st.markdown(f"Data Files: {total_files}")
        st.markdown(f"Data Size: {total_size:.1f} MB")
        
    except Exception as e:
        st.error(f"Status check failed: {e}")

def display_system_overview():
    """Display comprehensive system overview"""
    st.subheader("🏥 System Health Overview")
    
    base_path = Path(__file__).parent.parent.parent
    
    try:
        health_report = generate_health_report(base_path)
        
        # Overall status
        overall_status = health_report.get('overall_status', 'unknown')
        status_color = get_status_color(overall_status)
        
        st.markdown(
            f"<h3 style='color: {status_color};'>Overall Status: {overall_status.upper()}</h3>", 
            unsafe_allow_html=True
        )
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Collectors", "💾 Data", "💻 System", "🌐 APIs"])
        
        with tab1:
            st.subheader("Collector Status")
            collectors = health_report.get('collectors', {})
            
            for collector_name, status_info in collectors.items():
                display_collector_status(collector_name, status_info)
                st.markdown("---")
        
        with tab2:
            st.subheader("Data Health")
            data_info = health_report.get('data', {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Files", data_info.get('total_files', 0))
            with col2:
                st.metric("Total Size (MB)", f"{data_info.get('total_size_mb', 0):.1f}")
            with col3:
                st.metric("Data Types", len(data_info.get('data_types', {})))
            
            # Data type breakdown
            data_types = data_info.get('data_types', {})
            if data_types:
                st.subheader("Data Type Breakdown")
                for data_type, type_info in data_types.items():
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{data_type.upper()}**")
                    with col2:
                        st.write(f"{type_info['file_count']} files, {type_info['size_mb']:.1f} MB")
        
        with tab3:
            st.subheader("System Resources")
            system_info = health_report.get('system', {})
            
            if system_info.get('status') != 'error':
                col1, col2, col3 = st.columns(3)
                with col1:
                    cpu_percent = system_info.get('cpu_percent', 0)
                    st.metric("CPU Usage", f"{cpu_percent}%")
                    st.progress(cpu_percent / 100)
                
                with col2:
                    memory_percent = system_info.get('memory_percent', 0)
                    st.metric("Memory Usage", f"{memory_percent}%")
                    st.progress(memory_percent / 100)
                
                with col3:
                    disk_percent = system_info.get('disk_percent', 0)
                    st.metric("Disk Usage", f"{disk_percent}%")
                    st.progress(disk_percent / 100)
                
                # System issues
                issues = system_info.get('issues', [])
                if issues:
                    st.subheader("⚠️ System Issues")
                    for issue in issues:
                        st.warning(issue)
            else:
                st.error(f"System check failed: {system_info.get('message', 'Unknown error')}")
        
        with tab4:
            st.subheader("API Connectivity")
            api_info = health_report.get('apis', {})
            
            apis = api_info.get('apis', {})
            for api_name, api_status in apis.items():
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    st.write(f"**{api_name.upper()}**")
                
                with col2:
                    status = api_status.get('status', 'unknown')
                    color = get_status_color(status)
                    st.markdown(f"<span style='color: {color}; font-weight: bold;'>{status.upper()}</span>", unsafe_allow_html=True)
                
                with col3:
                    if 'http_code' in api_status:
                        st.write(f"HTTP {api_status['http_code']}")
                    elif 'error' in api_status:
                        st.write(f"Error: {api_status['error']}")
    
    except Exception as e:
        st.error(f"Failed to load system overview: {e}")
        st.exception(e)

def display_data_freshness_summary():
    """Display data freshness summary"""
    st.subheader("📅 Data Freshness Summary")
    
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / 'financial_data'
    
    if not data_path.exists():
        st.error("Data directory not found")
        return
    
    freshness_data = []
    
    for data_type_dir in data_path.iterdir():
        if data_type_dir.is_dir():
            freshness = check_data_freshness(data_type_dir)
            freshness_data.append({
                'Data Type': data_type_dir.name.upper(),
                'Status': '✅ Fresh' if freshness['is_fresh'] else '⚠️ Stale',
                'Age (Hours)': f"{freshness.get('age_hours', 0):.1f}",
                'Last Updated': freshness.get('last_modified', 'Unknown')
            })
    
    if freshness_data:
        df = pd.DataFrame(freshness_data)
        st.dataframe(df, use_container_width=True) 