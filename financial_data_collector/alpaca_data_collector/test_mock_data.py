#!/usr/bin/env python3
"""
Mock Alpaca Data Generator
Simulates Alpaca data collection for testing without API dependencies.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import random

def generate_mock_ohlcv_data(ticker, days=30):
    """Generate mock OHLCV data for a ticker"""
    data = []
    base_price = random.uniform(50, 500)  # Random starting price
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        
        # Simulate realistic price movement
        daily_change = random.uniform(-0.05, 0.05)  # ±5% daily change
        base_price *= (1 + daily_change)
        
        # Generate OHLC with realistic relationships
        open_price = base_price * random.uniform(0.995, 1.005)
        close_price = base_price * random.uniform(0.995, 1.005)
        high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
        low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
        volume = random.randint(100000, 10000000)
        
        record = {
            'ticker': ticker,
            'datetime': date.strftime('%Y-%m-%dT%H:%M:%S'),
            'open': round(open_price, 2),
            'high': round(high_price, 2), 
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        }
        data.append(record)
    
    return data

def generate_mock_events_data(tickers):
    """Generate mock events data"""
    events = []
    
    for ticker in tickers[:5]:  # Generate events for first 5 tickers
        # Mock dividend
        if random.random() > 0.7:  # 30% chance of dividend
            dividend_date = datetime.now() - timedelta(days=random.randint(1, 90))
            events.append({
                'ticker': ticker,
                'datetime': dividend_date.strftime('%Y-%m-%dT%H:%M:%S'),
                'event_type': 'dividend',
                'value': round(random.uniform(0.50, 3.00), 2),
                'raw_data': {'type': 'dividend', 'amount': 1.25}
            })
        
        # Mock earnings
        if random.random() > 0.6:  # 40% chance of earnings
            earnings_date = datetime.now() - timedelta(days=random.randint(1, 120))
            events.append({
                'ticker': ticker,
                'datetime': earnings_date.strftime('%Y-%m-%dT%H:%M:%S'),
                'event_type': 'earnings',
                'value': round(random.uniform(1.0, 5.0), 2),
                'raw_data': {'type': 'earnings', 'eps': 2.45}
            })
    
    return events

def save_mock_data(data, filename, data_type):
    """Save mock data to the expected location"""
    data_dir = Path(__file__).parent.parent / 'financial_data' / data_type
    data_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = data_dir / filename
    
    # Save as JSON (simulating what would be parquet)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filepath

def generate_all_mock_data():
    """Generate complete mock dataset"""
    print("🎭 Generating Mock Alpaca Data...")
    
    # Load configuration to get tickers
    try:
        config_path = Path(__file__).parent / 'config' / 'data_requirements.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Get all tickers
        all_tickers = []
        if 'ohlcv' in config:
            if 'us_stocks' in config['ohlcv']:
                all_tickers.extend(config['ohlcv']['us_stocks'])
            if 'asx_adrs' in config['ohlcv']:
                all_tickers.extend(config['ohlcv']['asx_adrs'])
            if 'crypto' in config['ohlcv']:
                all_tickers.extend(config['ohlcv']['crypto'])
        
        print(f"📊 Generating data for {len(all_tickers)} tickers...")
        
        # Generate OHLCV data
        total_records = 0
        today = datetime.now().strftime('%Y%m%d')
        
        for ticker in all_tickers:
            # Daily data
            daily_data = generate_mock_ohlcv_data(ticker, days=30)
            filename = f"mock_{ticker.replace('.', '_')}_daily_ohlcv_{today}.json"
            filepath = save_mock_data(daily_data, filename, 'ohlcv')
            print(f"   ✅ {ticker} daily: {len(daily_data)} records → {filepath.name}")
            total_records += len(daily_data)
            
            # Hourly data (smaller dataset)
            hourly_data = generate_mock_ohlcv_data(ticker, days=7)
            filename = f"mock_{ticker.replace('.', '_')}_hourly_ohlcv_{today}.json"
            filepath = save_mock_data(hourly_data, filename, 'ohlcv')
            print(f"   ✅ {ticker} hourly: {len(hourly_data)} records → {filepath.name}")
            total_records += len(hourly_data)
        
        # Generate events data
        events_data = generate_mock_events_data(all_tickers)
        events_filename = f"mock_alpaca_events_{today}.json"
        events_filepath = save_mock_data(events_data, events_filename, 'events')
        print(f"   ✅ Events: {len(events_data)} records → {events_filepath.name}")
        total_records += len(events_data)
        
        # Summary
        print(f"\n🎯 Mock Data Generation Complete!")
        print(f"   📊 Total Records: {total_records}")
        print(f"   📁 OHLCV Files: {len(all_tickers) * 2}")
        print(f"   📅 Events Files: 1")
        print(f"   💾 Data Location: ../financial_data/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating mock data: {e}")
        return False

def show_data_summary():
    """Show summary of generated data"""
    print(f"\n📈 Mock Data Summary:")
    
    # Check OHLCV files
    ohlcv_dir = Path(__file__).parent.parent / 'financial_data' / 'ohlcv'
    if ohlcv_dir.exists():
        ohlcv_files = list(ohlcv_dir.glob('mock_*.json'))
        print(f"   📊 OHLCV Files: {len(ohlcv_files)}")
        if ohlcv_files:
            print(f"      Example: {ohlcv_files[0].name}")
    
    # Check events files
    events_dir = Path(__file__).parent.parent / 'financial_data' / 'events'
    if events_dir.exists():
        events_files = list(events_dir.glob('mock_*.json'))
        print(f"   📅 Events Files: {len(events_files)}")
        if events_files:
            print(f"      Example: {events_files[0].name}")

def main():
    """Main function"""
    print("🎭 Alpaca Mock Data Generator")
    print("=" * 40)
    
    if generate_all_mock_data():
        show_data_summary()
        print(f"\n✅ Mock data generation successful!")
        print(f"📊 This simulates what the real Alpaca collector would produce")
        print(f"🔄 Data can be viewed in the unified dashboard")
        return True
    else:
        print(f"❌ Mock data generation failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 