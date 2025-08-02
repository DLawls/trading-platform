#!/usr/bin/env python3
"""
🤖 AI Trading Platform Dashboard
Complete system monitoring for the AI Trading Platform

This is the main entry point for the redesigned dashboard that organizes
all indicators into logical groups: Macro vs Company-specific data.
"""

import streamlit as st
import yaml
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import page modules (renamed directory to avoid auto-tabs)
from _pages import system_overview, macro_indicators, company_indicators, system_operations

def load_config():
    """Load dashboard configuration"""
    config_path = Path(__file__).parent / "config" / "dashboard_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_page_config(config):
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=config['dashboard']['title'],
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def create_sidebar(config):
    """Create minimal navigation sidebar with just dropdown"""
    # Page selector only - no title, no buttons, no extra content
    page_options = {
        "overview": "📊 System Overview",
        "macro": "🌍 Macro Indicators", 
        "companies": "🏢 Company Data",
        "operations": "⚙️ Operations"
    }
    
    selected_page = st.sidebar.selectbox(
        "Select Page:",
        options=list(page_options.keys()),
        format_func=lambda x: page_options[x],
        index=1  # Default to macro indicators
    )
    
    return selected_page

def main():
    """Main dashboard application"""
    # Load configuration
    config = load_config()
    
    # Setup page
    setup_page_config(config)
    
    # Create sidebar and get selected page
    selected_page = create_sidebar(config)
    
    # NO MAIN HEADER - removed title and subtitle
    
    # Route to appropriate page
    if selected_page == "overview":
        system_overview.show_page(config)
    elif selected_page == "macro":
        macro_indicators.show_page(config)
    elif selected_page == "companies":
        company_indicators.show_page(config)
    elif selected_page == "operations":
        system_operations.show_page(config)
    else:
        st.error(f"Page '{selected_page}' not found!")

if __name__ == "__main__":
    main() 