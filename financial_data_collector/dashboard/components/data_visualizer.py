#!/usr/bin/env python3
"""
Data Visualization Components
Reusable chart and visualization functions for the dashboard.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def create_time_series_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str):
    """Create a time series line chart"""
    fig = px.line(df, x=x_col, y=y_col, title=title)
    fig.update_layout(height=400)
    return fig

def create_candlestick_chart(df: pd.DataFrame, title: str):
    """Create OHLC candlestick chart"""
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'], 
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(title=title, height=500)
    return fig

def display_metrics_grid(metrics: dict, columns: int = 4):
    """Display metrics in a grid layout"""
    cols = st.columns(columns)
    for i, (label, value) in enumerate(metrics.items()):
        with cols[i % columns]:
            st.metric(label, value) 