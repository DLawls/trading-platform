#!/usr/bin/env python3
"""
Dashboard Launcher
Convenient script to launch the unified financial data collector dashboard.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit dashboard"""
    dashboard_app = Path(__file__).parent / 'app.py'
    
    print("🚀 Launching Financial Data Collector Dashboard...")
    print(f"📁 Dashboard location: {dashboard_app}")
    print("🌐 The dashboard will open in your browser")
    print("🛑 Press Ctrl+C to stop the dashboard")
    print("=" * 60)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            str(dashboard_app),
            '--server.address', '0.0.0.0',
            '--server.port', '8501',
            '--theme.base', 'light'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main() 