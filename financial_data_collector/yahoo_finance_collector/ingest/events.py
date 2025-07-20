import yaml
import os
from pathlib import Path
import yfinance as yf
import pandas as pd
import numpy as np

def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def ensure_data_dir():
    data_dir = Path(__file__).parent.parent.parent / 'financial_data' / 'events'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def clean_earnings_data(earnings_df, ticker):
    """Clean and validate earnings data"""
    if earnings_df is None or earnings_df.empty:
        return pd.DataFrame()
    
    try:
        # Reset index to make date a column
        earnings_df = earnings_df.reset_index()
        
        # Clean column names
        earnings_df.columns = [col.strip() for col in earnings_df.columns]
        
        # Add ticker
        earnings_df['ticker'] = ticker
        
        # Handle null values - convert to None for consistency
        for col in ['EPS Estimate', 'Reported EPS', 'Surprise(%)']:
            if col in earnings_df.columns:
                earnings_df[col] = earnings_df[col].replace([np.nan, 'nan', ''], None)
        
        # Ensure Event Type exists
        if 'Event Type' not in earnings_df.columns:
            earnings_df['Event Type'] = 'Earnings'
        
        return earnings_df
        
    except Exception as e:
        print(f"Error cleaning earnings data for {ticker}: {e}")
        return pd.DataFrame()

def clean_dividends_data(dividends_series, ticker):
    """Clean and validate dividends data"""
    if dividends_series is None or dividends_series.empty:
        return pd.DataFrame()
    
    try:
        # Convert to DataFrame
        dividends_df = dividends_series.reset_index()
        dividends_df.columns = ['date', 'dividend']
        
        # Add ticker
        dividends_df['ticker'] = ticker
        
        # Remove any null or zero dividends
        dividends_df = dividends_df.dropna(subset=['dividend'])
        dividends_df = dividends_df[dividends_df['dividend'] > 0]
        
        # Convert date to string format
        dividends_df['date'] = pd.to_datetime(dividends_df['date']).dt.strftime('%Y-%m-%d')
        
        return dividends_df
        
    except Exception as e:
        print(f"Error cleaning dividends data for {ticker}: {e}")
        return pd.DataFrame()

def fetch_and_store_events(ticker, data_dir):
    try:
        print(f"\nFetching events for {ticker}...")
        yf_ticker = yf.Ticker(ticker)
        
        events_saved = 0
        
        # Earnings events
        try:
            earnings = getattr(yf_ticker, 'earnings_dates', None)
            earnings_df = clean_earnings_data(earnings, ticker)
            
            if not earnings_df.empty:
                earnings_file = f"{ticker.replace('.', '_')}_earnings.parquet"
                earnings_df.to_parquet(data_dir / earnings_file, index=False)
                print(f"✅ Saved earnings events for {ticker} to {earnings_file} [{len(earnings_df)} rows]")
                events_saved += 1
            else:
                print(f"📭 No earnings events for {ticker}")
                
        except Exception as e:
            print(f"⚠️  Error fetching earnings for {ticker}: {e}")
            
        # Dividends events
        try:
            dividends = getattr(yf_ticker, 'dividends', None)
            dividends_df = clean_dividends_data(dividends, ticker)
            
            if not dividends_df.empty:
                dividends_file = f"{ticker.replace('.', '_')}_dividends.parquet"
                dividends_df.to_parquet(data_dir / dividends_file, index=False)
                print(f"✅ Saved dividends for {ticker} to {dividends_file} [{len(dividends_df)} rows]")
                print(f"   📅 Date range: {dividends_df['date'].min()} to {dividends_df['date'].max()}")
                events_saved += 1
            else:
                print(f"📭 No dividends for {ticker}")
                
        except Exception as e:
            print(f"⚠️  Error fetching dividends for {ticker}: {e}")
            
        # Additional events: stock splits, actions
        try:
            actions = getattr(yf_ticker, 'actions', None)
            if actions is not None and not actions.empty:
                # Filter for stock splits
                splits = actions[actions['Stock Splits'] > 0]
                if not splits.empty:
                    splits = splits.reset_index()
                    splits['ticker'] = ticker
                    splits['event_type'] = 'Stock Split'
                    splits_file = f"{ticker.replace('.', '_')}_splits.parquet"
                    splits.to_parquet(data_dir / splits_file, index=False)
                    print(f"✅ Saved stock splits for {ticker} to {splits_file} [{len(splits)} rows]")
                    events_saved += 1
                    
        except Exception as e:
            print(f"⚠️  Error fetching stock actions for {ticker}: {e}")
            
        if events_saved == 0:
            print(f"❌ No events data available for {ticker}")
            
    except Exception as e:
        print(f"❌ Error fetching events for {ticker}: {e}")

def main():
    config = load_config()
    events = config.get('events', {})
    tickers = set()
    for event_type in ['earnings', 'dividends']:
        tickers.update(events.get(event_type, {}).get('tickers', []))
    data_dir = ensure_data_dir()
    for ticker in tickers:
        fetch_and_store_events(ticker, data_dir)

if __name__ == '__main__':
    main()
