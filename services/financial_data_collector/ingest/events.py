import yaml
import os
from pathlib import Path
import yfinance as yf
import pandas as pd

# List of known ETF tickers (expand as needed)
ETF_TICKERS = {'IOZ.AX'}

def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def ensure_data_dir():
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'events'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def fetch_and_store_events(ticker, data_dir):
    try:
        yf_ticker = yf.Ticker(ticker)
        is_etf = ticker in ETF_TICKERS
        # Earnings events (skip for ETFs)
        if not is_etf:
            earnings = getattr(yf_ticker, 'earnings_dates', None)
            if earnings is not None and not earnings.empty:
                earnings['ticker'] = ticker
                earnings.reset_index(inplace=True)
                earnings_file = f"{ticker.replace('.', '_')}_earnings.parquet"
                earnings.to_parquet(data_dir / earnings_file, index=False)
                print(f"Saved earnings events for {ticker} to {earnings_file} [{len(earnings)} rows]")
            else:
                print(f"No earnings events for {ticker}")
        else:
            print(f"Skipping earnings fetch for ETF: {ticker}")
        # Dividends events (fetch for all)
        dividends = getattr(yf_ticker, 'dividends', None)
        if dividends is not None and not dividends.empty:
            dividends = dividends.reset_index()
            dividends.columns = ['date', 'dividend']
            dividends['ticker'] = ticker
            dividends_file = f"{ticker.replace('.', '_')}_dividends.parquet"
            dividends.to_parquet(data_dir / dividends_file, index=False)
            print(f"Saved dividends for {ticker} to {dividends_file} [{len(dividends)} rows]")
        else:
            print(f"No dividends for {ticker}")
    except Exception as e:
        print(f"Error fetching events for {ticker}: {e}")

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
