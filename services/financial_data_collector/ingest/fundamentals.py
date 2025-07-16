import yaml
import os
from pathlib import Path
import yfinance as yf
import pandas as pd

def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def ensure_data_dir():
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'fundamentals'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def fetch_and_store_fundamentals(ticker, fields, data_dir):
    try:
        yf_ticker = yf.Ticker(ticker)
        fin = yf_ticker.financials.T if hasattr(yf_ticker, 'financials') else pd.DataFrame()
        if fin.empty:
            print(f"No financials for {ticker}")
            return
        # Only keep requested fields if present
        fin = fin[list(set(fields) & set(fin.columns))] if fields else fin
        fin['ticker'] = ticker
        fin.reset_index(inplace=True)
        filename = f"{ticker.replace('.', '_')}_fundamentals.parquet"
        fin.to_parquet(data_dir / filename, index=False)
        print(f"Saved fundamentals for {ticker} to {filename} [{len(fin)} rows]")
    except Exception as e:
        print(f"Error fetching fundamentals for {ticker}: {e}")

def main():
    config = load_config()
    tickers = config.get('fundamentals', {}).get('tickers', [])
    fields = config.get('fundamentals', {}).get('fields', [])
    data_dir = ensure_data_dir()
    for ticker in tickers:
        fetch_and_store_fundamentals(ticker, fields, data_dir)

if __name__ == '__main__':
    main()
