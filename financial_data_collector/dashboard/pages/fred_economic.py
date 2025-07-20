#!/usr/bin/env python3
"""
FRED Economic Data Monitoring Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

def show_page():
    st.title("🏛️ FRED Economic Data")
    st.markdown("Federal Reserve Economic Data monitoring")
    
    data_path = Path(__file__).parent.parent.parent / 'financial_data' / 'economic' / 'fred'
    
    if data_path.exists():
        files = list(data_path.glob('*.parquet'))
        st.metric("FRED Indicators", len(files))
        
        if files:
            selected_file = st.selectbox("Select indicator:", [f.name for f in files])
            if selected_file:
                df = pd.read_parquet(data_path / selected_file)
                
                # Plot time series
                if 'date' in df.columns and 'value' in df.columns:
                    fig = px.line(df, x='date', y='value', title=f"FRED Indicator - {selected_file}")
                    st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(df.tail(10))
    else:
        st.warning("No FRED data found") 