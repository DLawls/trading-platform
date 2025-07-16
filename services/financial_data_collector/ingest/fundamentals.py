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
    schema_path = Path(__file__).parent.parent / 'schema' / 'fundamentals.json'
    with open(schema_path, 'r') as f:
        return json.load(f)

def ensure_data_dir():
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'fundamentals'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def validate_fundamentals(df, schema, ticker):
    valid_rows = []
    for _, row in df.iterrows():
        record = row.to_dict()
        record['ticker'] = ticker
        try:
            validate(instance=record, schema=schema)
            valid_rows.append(record)
        except ValidationError as e:
            print(f"Validation error: {e.message} in row: {record}")
    return pd.DataFrame(valid_rows)

def fetch_and_store_fundamentals(ticker, fields, data_dir, schema):
    try:
        yf_ticker = yf.Ticker(ticker)
        # print(f"\n--- {ticker} ---")
        # print("financials columns:", yf_ticker.financials.T.columns)
        # print(yf_ticker.financials.T.head())
        # print("info keys:", list(yf_ticker.info.keys()))
        # print("trailingEps:", yf_ticker.info.get('trailingEps'))
        # print("trailingPE:", yf_ticker.info.get('trailingPE'))
        fin = yf_ticker.financials.T if hasattr(yf_ticker, 'financials') else pd.DataFrame()
        if fin.empty:
            print(f"No financials for {ticker}")
            return
        # Map yfinance columns to schema fields if possible
        column_map = {
            'Total Revenue': 'revenue',
            'Net Income': 'net_income',
            # Add more mappings as needed
        }
        fin.rename(columns=column_map, inplace=True)
        # Add latest eps and pe_ratio from info to every row
        eps = yf_ticker.info.get('trailingEps')
        pe_ratio = yf_ticker.info.get('trailingPE')
        fin['eps'] = eps
        fin['pe_ratio'] = pe_ratio
        # print("Available columns after renaming:", fin.columns)
        # print("Requested fields:", fields)
        # Only keep requested fields if present
        fin = fin[list(set(fields) & set(fin.columns))] if fields else fin
        fin['ticker'] = ticker
        fin.reset_index(inplace=True)
        if 'index' in fin.columns:
            fin.rename(columns={'index': 'date'}, inplace=True)
        if 'date' in fin.columns:
            fin['date'] = fin['date'].astype(str)
        # Validate each row
        fin = validate_fundamentals(fin, schema, ticker)
        if fin.empty:
            print(f"No valid rows for {ticker} after schema validation.")
            return
        filename = f"{ticker.replace('.', '_')}_fundamentals.parquet"
        fin.to_parquet(data_dir / filename, index=False)
        print(f"Saved fundamentals for {ticker} to {filename} [{len(fin)} rows]")
    except Exception as e:
        print(f"Error fetching fundamentals for {ticker}: {e}")

def main():
    config = load_config()
    schema = load_schema()
    tickers = config.get('fundamentals', {}).get('tickers', [])
    fields = config.get('fundamentals', {}).get('fields', [])
    data_dir = ensure_data_dir()
    for ticker in tickers:
        fetch_and_store_fundamentals(ticker, fields, data_dir, schema)

if __name__ == '__main__':
    main()
