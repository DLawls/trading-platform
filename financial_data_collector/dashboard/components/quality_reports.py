#!/usr/bin/env python3
"""
Data Quality Report Components
Functions for displaying data quality metrics and reports.
"""

import streamlit as st
import pandas as pd

def display_quality_summary(results: dict):
    """Display data quality summary"""
    st.subheader("📊 Data Quality Summary")
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r.get('is_valid', False))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Checks", total_checks)
    with col2:
        st.metric("Passed", passed_checks)
    with col3:
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")

def display_file_status_table(file_data: list):
    """Display file status in a table"""
    if file_data:
        df = pd.DataFrame(file_data)
        st.dataframe(df, use_container_width=True) 