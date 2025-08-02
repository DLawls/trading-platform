#!/usr/bin/env python3
"""
🚀 AI Trading Platform Dashboard Launcher
Quick launcher for the redesigned dashboard system
"""

import subprocess
import sys
from pathlib import Path

def main():
    dashboard_dir = Path(__file__).parent
    print("🚀 Launching AI Trading Platform Dashboard...")
    print(f"📁 Dashboard location: {dashboard_dir}/app.py")
    print("🌐 The dashboard will open in your browser")
    print("🛑 Press Ctrl+C to stop the dashboard")
    print("=" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py"
        ], cwd=dashboard_dir)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped.")

if __name__ == "__main__":
    main() 