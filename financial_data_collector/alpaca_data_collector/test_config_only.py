#!/usr/bin/env python3
"""
Alpaca Configuration Test (No Dependencies Required)
Tests Alpaca collector configuration and shows what data would be collected.
"""

import yaml
import json
from pathlib import Path

def test_api_configuration():
    """Test API configuration setup"""
    print("🧪 Testing Alpaca API Configuration...")
    
    try:
        # Load sources config
        sources_path = Path(__file__).parent / 'config' / 'sources.yaml'
        with open(sources_path, 'r') as f:
            sources = yaml.safe_load(f)
        
        alpaca_config = sources['alpaca']
        
        print(f"📡 Endpoint: {alpaca_config['endpoint']}")
        print(f"📊 Data Endpoint: {alpaca_config['data_endpoint']}")
        print(f"⏱️  Rate Limit: {alpaca_config['rate_limit']} requests/minute")
        print(f"🔄 Retry Attempts: {alpaca_config['retry_attempts']}")
        
        # Check API key status
        api_key = alpaca_config['api_key']
        secret_key = alpaca_config['secret_key']
        
        if api_key == 'YOUR_ALPACA_API_KEY' or secret_key == 'YOUR_ALPACA_SECRET':
            print("❌ API Keys: Not configured (placeholders detected)")
            return False
        else:
            print("✅ API Keys: Configured")
            print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
            return True
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def show_data_collection_plan():
    """Show what data would be collected"""
    print("\n📊 Data Collection Plan...")
    
    try:
        # Load data requirements
        config_path = Path(__file__).parent / 'config' / 'data_requirements.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # OHLCV Data
        if 'ohlcv' in config:
            print(f"\n📈 OHLCV Collection:")
            
            if 'us_stocks' in config['ohlcv']:
                us_stocks = config['ohlcv']['us_stocks']
                print(f"   🇺🇸 US Stocks: {len(us_stocks)} tickers")
                print(f"      Examples: {', '.join(us_stocks[:5])}")
            
            if 'asx_adrs' in config['ohlcv']:
                asx_adrs = config['ohlcv']['asx_adrs']
                print(f"   🇦🇺 ASX ADRs: {len(asx_adrs)} tickers")
                print(f"      Examples: {', '.join(asx_adrs)}")
            
            if 'crypto' in config['ohlcv']:
                crypto = config['ohlcv']['crypto']
                print(f"   🪙 Crypto: {len(crypto)} assets")
                print(f"      Examples: {', '.join(crypto)}")
            
            intervals = config['ohlcv'].get('intervals', ['daily'])
            print(f"   ⏰ Intervals: {', '.join(intervals)}")
        
        # Events Data
        if 'events' in config:
            print(f"\n📅 Events Collection:")
            
            total_tickers = set()
            for event_type in ['earnings', 'dividends', 'splits']:
                if event_type in config['events']:
                    event_config = config['events'][event_type]
                    if 'us_stocks' in event_config:
                        total_tickers.update(event_config['us_stocks'])
                    if 'asx_adrs' in event_config:
                        total_tickers.update(event_config['asx_adrs'])
            
            print(f"   📊 Total Event Tickers: {len(total_tickers)}")
            print(f"   🎯 Event Types: Earnings, Dividends, Splits")
        
        return True
        
    except Exception as e:
        print(f"❌ Data plan error: {e}")
        return False

def estimate_data_output():
    """Estimate data output and storage"""
    print("\n💾 Data Output Estimation...")
    
    try:
        config_path = Path(__file__).parent / 'config' / 'data_requirements.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Count total tickers
        total_tickers = 0
        if 'ohlcv' in config:
            if 'us_stocks' in config['ohlcv']:
                total_tickers += len(config['ohlcv']['us_stocks'])
            if 'asx_adrs' in config['ohlcv']:
                total_tickers += len(config['ohlcv']['asx_adrs'])
            if 'crypto' in config['ohlcv']:
                total_tickers += len(config['ohlcv']['crypto'])
        
        intervals = config['ohlcv'].get('intervals', ['daily']) if 'ohlcv' in config else ['daily']
        
        print(f"📊 Total Tickers: {total_tickers}")
        print(f"⏰ Intervals: {len(intervals)}")
        print(f"📁 Total OHLCV Files: {total_tickers * len(intervals)} per collection")
        print(f"📅 Events Files: ~3 consolidated files per collection")
        
        # Estimate file sizes (rough estimates)
        daily_size_mb = total_tickers * 0.1  # ~100KB per ticker for 2 years daily data
        hourly_size_mb = total_tickers * 0.5  # ~500KB per ticker for 1 month hourly data
        
        print(f"💽 Estimated Daily Collection: ~{daily_size_mb:.1f} MB")
        if 'hourly' in intervals:
            print(f"💽 Estimated Hourly Collection: ~{hourly_size_mb:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Estimation error: {e}")
        return False

def show_next_steps():
    """Show next steps for full testing"""
    print("\n🚀 Next Steps for Full Testing:")
    print("="*50)
    
    print("1. 🔑 Configure API Keys:")
    print("   → Get free paper trading keys from https://app.alpaca.markets/")
    print("   → Update config/sources.yaml with your actual keys")
    print()
    
    print("2. 📦 Install Dependencies:")
    print("   → Run: sudo apt install python3-pip  # If needed")
    print("   → Run: pip3 install alpaca-trade-api pandas pyyaml jsonschema pyarrow")
    print("   → Or: poetry install  # If network issues resolved")
    print()
    
    print("3. 🧪 Test Collection:")
    print("   → Run: python3 ingest/orchestrator.py")
    print("   → Check: ../financial_data/ohlcv/ for output files")
    print()
    
    print("4. 📊 Monitor via Dashboard:")
    print("   → Run: streamlit run ../dashboard/main.py")
    print("   → View Alpaca collector status")

def main():
    """Run configuration tests"""
    print("🚀 Alpaca Collector Configuration Test")
    print("=" * 50)
    
    tests = [
        ("API Configuration", test_api_configuration),
        ("Data Collection Plan", show_data_collection_plan),
        ("Data Output Estimation", estimate_data_output)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        results.append(test_func())
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Configuration Tests: {passed}/{total} passed")
    
    if results[0]:  # If API config passed
        print("✅ Alpaca collector is properly configured!")
    else:
        print("⚠️  Alpaca collector needs API key configuration")
    
    show_next_steps()
    
    return all(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 