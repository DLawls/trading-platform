import yaml
import os
from pathlib import Path
import pandas as pd
from fredapi import Fred
import json
from jsonschema import validate, ValidationError

def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_sources():
    sources_path = Path(__file__).parent.parent / 'config' / 'sources.yaml'
    with open(sources_path, 'r') as f:
        return yaml.safe_load(f)

def load_schema():
    schema_path = Path(__file__).parent.parent / 'schema' / 'macro.json'
    with open(schema_path, 'r') as f:
        return json.load(f)

def ensure_data_dir():
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'macro'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def validate_macro(df, schema, indicator):
    valid_rows = []
    for _, row in df.iterrows():
        record = {
            'indicator': indicator,
            'date': str(row['date']),
            'value': row['value'],
            'source': 'FRED'
        }
        try:
            validate(instance=record, schema=schema)
            valid_rows.append(record)
        except ValidationError as e:
            print(f"Validation error: {e.message} in row: {record}")
    return pd.DataFrame(valid_rows)

def fetch_and_store_macro(indicator, fred, data_dir, schema):
    try:
        series = fred.get_series(indicator)
        if series is None or series.empty:
            print(f"No data for macro indicator: {indicator}")
            return
        df = series.reset_index()
        df.columns = ['date', 'value']
        df = validate_macro(df, schema, indicator)
        if df.empty:
            print(f"No valid rows for macro indicator {indicator} after schema validation.")
            return
        filename = f"{indicator}.parquet"
        df.to_parquet(data_dir / filename, index=False)
        print(f"Saved macro indicator {indicator} to {filename} [{len(df)} rows]")
    except Exception as e:
        print(f"Error fetching macro indicator {indicator}: {e}")

def main():
    config = load_config()
    sources = load_sources()
    schema = load_schema()
    indicators = config.get('macro', {}).get('indicators', [])
    fred_api_key = sources.get('fred', {}).get('api_key', None)
    if not fred_api_key:
        print("FRED API key not found in sources.yaml. Please add it.")
        return
    fred = Fred(api_key=fred_api_key)
    data_dir = ensure_data_dir()
    for indicator in indicators:
        fetch_and_store_macro(indicator, fred, data_dir, schema)

if __name__ == '__main__':
    main()
