import yaml
import os
from pathlib import Path
import yfinance as yf
import pandas as pd
import json
from jsonschema import validate, ValidationError
from datetime import datetime, timedelta


def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_schema():
    schema_path = Path(__file__).parent.parent / 'schema' / 'ohlcv.json'
    with open(schema_path, 'r') as f:
        return json.load(f)

def ensure_data_dir():
    data_dir = Path(__file__).parent.parent.parent / 'financial_data' / 'ohlcv'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def validate_ohlcv(df, schema, ticker):
    valid_rows = []
    for idx, row in df.iterrows():
        # Convert yfinance format to our schema format
        try:
            # Get the actual date value - fix the datetime column issue
            date_value = row['Date']
            
            # Ensure proper datetime formatting
            if pd.isna(date_value):
                continue
                
            # Convert to datetime if not already
            if isinstance(date_value, str):
                date_value = pd.to_datetime(date_value)
            elif not isinstance(date_value, (pd.Timestamp, datetime)):
                date_value = pd.to_datetime(date_value)
            
            # Format as ISO string for schema compliance
            datetime_str = date_value.strftime('%Y-%m-%dT%H:%M:%S')
            
            record = {
                'ticker': ticker,
                'datetime': datetime_str,
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': float(row['Volume']) if pd.notna(row['Volume']) else 0.0
            }
            validate(instance=record, schema=schema)
            valid_rows.append(record)
        except (ValidationError, KeyError, ValueError, TypeError) as e:
            print(f"Validation error for {ticker} on row {idx}: {e}")
            continue
    return pd.DataFrame(valid_rows)

def fetch_and_store_ohlcv(ticker, interval, data_dir, schema):
    # Map config interval to yfinance interval
    yf_interval = {'daily': '1d', 'hourly': '1h'}.get(interval, '1d')
    
    try:
        # Set period based on interval - 5 years for daily, 1 month for hourly
        if interval == 'hourly':
            period = '1mo'  # Keep short for hourly to avoid rate limits
        else:
            period = '5y'   # 5 years for daily data - handles leap years automatically
        
        print(f"Fetching {ticker} ({interval}) for period: {period}")
        
        # Fetch data from yfinance
        df = yf.download(ticker, interval=yf_interval, period=period, progress=False)
        
        if df is None or df.empty:
            print(f"No data returned for {ticker} ({interval})")
            return
            
        # Reset index to make Date a column 
        df.reset_index(inplace=True)
        
        # Fix column names - yfinance returns multi-level columns
        # Flatten the columns by taking the first level for OHLCV data
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if col[0] != '' else col[1] for col in df.columns]
        
        # Debug: Show what we got from yfinance
        print(f"Raw data shape for {ticker}: {df.shape}")
        if not df.empty:
            print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
            print(f"Columns: {list(df.columns)}")
        
        # Validate and clean each row
        df_validated = validate_ohlcv(df, schema, ticker)
        
        if df_validated.empty:
            print(f"No valid rows for {ticker} ({interval}) after schema validation.")
            return
            
        # Save as Parquet
        filename = f"{ticker.replace('.', '_')}_{interval}.parquet"
        df_validated.to_parquet(data_dir / filename, index=False)
        
        # Calculate actual date range from validated data
        df_validated['datetime'] = pd.to_datetime(df_validated['datetime'])
        start_date = df_validated['datetime'].min()
        end_date = df_validated['datetime'].max()
        total_days = (end_date - start_date).days
        
        print(f"✅ Saved {ticker} ({interval}) to {filename}")
        print(f"   📊 {len(df_validated)} rows | 📅 {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} | {total_days} days")
        
    except Exception as e:
        print(f"❌ Error fetching {ticker} ({interval}): {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🚀 Starting OHLCV Data Collection (5-year period)")
    print("=" * 60)
    
    config = load_config()
    schema = load_schema()
    tickers = config.get('ohlcv', {}).get('tickers', [])
    intervals = config.get('ohlcv', {}).get('intervals', ['daily'])
    
    print(f"📊 Configuration loaded:")
    print(f"   🎯 Tickers: {len(tickers)} companies")
    print(f"   ⏱️  Intervals: {intervals}")
    print(f"   📅 Period: 5 years (handles leap years automatically)")
    print()
    
    data_dir = ensure_data_dir()
    
    total_success = 0
    total_attempted = 0
    
    for ticker in tickers:
        for interval in intervals:
            total_attempted += 1
            try:
                fetch_and_store_ohlcv(ticker, interval, data_dir, schema)
                total_success += 1
            except Exception as e:
                print(f"❌ Failed to process {ticker} ({interval}): {e}")
    
    print()
    print("=" * 60)
    print(f"📊 OHLCV Collection Summary:")
    print(f"   ✅ Successful: {total_success}/{total_attempted}")
    print(f"   📈 Success Rate: {total_success/total_attempted*100:.1f}%")
    print("=" * 60)

if __name__ == '__main__':
    main()
