import yaml
import os
from pathlib import Path
import yfinance as yf
import pandas as pd
import json
from jsonschema import validate, ValidationError


def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_schema():
    schema_path = Path(__file__).parent.parent / 'schema' / 'ohlcv.json'
    with open(schema_path, 'r') as f:
        return json.load(f)

def ensure_data_dir():
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'ohlcv'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def validate_ohlcv(df, schema):
    valid_rows = []
    for _, row in df.iterrows():
        record = row.to_dict()
        try:
            validate(instance=record, schema=schema)
            valid_rows.append(record)
        except ValidationError as e:
            print(f"Validation error: {e.message} in row: {record}")
    return pd.DataFrame(valid_rows)

def fetch_and_store_ohlcv(ticker, interval, data_dir, schema):
    # Map config interval to yfinance interval
    yf_interval = {'daily': '1d', 'hourly': '1h'}.get(interval, '1d')
    try:
        df = yf.download(ticker, interval=yf_interval, progress=False)
        if df.empty:
            print(f"No data for {ticker} ({interval})")
            return
        df.reset_index(inplace=True)
        # Validate each row
        df = validate_ohlcv(df, schema)
        if df.empty:
            print(f"No valid rows for {ticker} ({interval}) after schema validation.")
            return
        # Save as Parquet
        filename = f"{ticker.replace('.', '_')}_{interval}.parquet"
        df.to_parquet(data_dir / filename, index=False)
        print(f"Saved {ticker} ({interval}) to {filename} [{len(df)} rows]")
    except Exception as e:
        print(f"Error fetching {ticker} ({interval}): {e}")

def main():
    config = load_config()
    schema = load_schema()
    tickers = config.get('ohlcv', {}).get('tickers', [])
    intervals = config.get('ohlcv', {}).get('intervals', [])
    data_dir = ensure_data_dir()
    for ticker in tickers:
        for interval in intervals:
            fetch_and_store_ohlcv(ticker, interval, data_dir, schema)

if __name__ == '__main__':
    main()
