#!/usr/bin/env python3
"""
FRED Economic Data Collector
Collects macroeconomic indicators from the Federal Reserve Economic Data (FRED) API
"""

import yaml
import os
from pathlib import Path
import pandas as pd
from fredapi import Fred
import json
from jsonschema import validate, ValidationError
from datetime import datetime

def load_config():
    """Load FRED-specific configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'fred_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_sources():
    """Load FRED API configuration"""
    sources_path = Path(__file__).parent.parent / 'config' / 'sources.yaml'
    with open(sources_path, 'r') as f:
        return yaml.safe_load(f)

def load_schema():
    """Load FRED data validation schema"""
    schema_path = Path(__file__).parent.parent / 'schema' / 'fred_economic.json'
    with open(schema_path, 'r') as f:
        return json.load(f)

def ensure_data_dir():
    """Ensure macro data directory exists"""
    data_dir = Path(__file__).parent.parent.parent / 'financial_data' / 'economic' / 'fred'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def validate_fred_data(df, schema, indicator):
    """Validate FRED economic data against schema"""
    valid_rows = []
    for _, row in df.iterrows():
        try:
            # Convert to ISO datetime format
            date_value = pd.to_datetime(row['date'])
            
            record = {
                'indicator': indicator,
                'datetime': date_value.strftime('%Y-%m-%dT%H:%M:%S'),
                'value': float(row['value']) if pd.notna(row['value']) else None,
                'source': 'FRED',
                'units': row.get('units', 'Unknown'),
                'frequency': row.get('frequency', 'Unknown')
            }
            
            # Skip records with null values
            if record['value'] is None:
                continue
                
            validate(instance=record, schema=schema)
            valid_rows.append(record)
            
        except (ValidationError, KeyError, ValueError, TypeError) as e:
            print(f"Validation error for {indicator} on {row.get('date', 'unknown date')}: {e}")
            continue
            
    return pd.DataFrame(valid_rows)

def fetch_and_store_fred_indicator(indicator, fred, data_dir, schema):
    """Fetch and store a single FRED economic indicator"""
    try:
        print(f"Fetching FRED indicator: {indicator}")
        
        # Get the time series data
        series = fred.get_series(indicator)
        if series is None or series.empty:
            print(f"No data returned for FRED indicator: {indicator}")
            return False
            
        # Get series metadata for additional context
        try:
            series_info = fred.get_series_info(indicator)
            units = series_info.get('units', 'Unknown')
            frequency = series_info.get('frequency', 'Unknown')
            title = series_info.get('title', indicator)
        except:
            units = 'Unknown'
            frequency = 'Unknown'
            title = indicator
        
        # Convert to DataFrame
        df = series.reset_index()
        df.columns = ['date', 'value']
        
        # Add metadata
        df['units'] = units
        df['frequency'] = frequency
        
        print(f"Raw data for {indicator}: {len(df)} records")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Title: {title}")
        
        # Validate data
        df_validated = validate_fred_data(df, schema, indicator)
        
        if df_validated.empty:
            print(f"No valid rows for FRED indicator {indicator} after validation")
            return False
            
        # Save as Parquet
        filename = f"{indicator}.parquet"
        df_validated.to_parquet(data_dir / filename, index=False)
        
        print(f"✅ Saved FRED indicator {indicator} to {filename}")
        print(f"   📊 {len(df_validated)} valid records")
        print(f"   📅 {df_validated['datetime'].min()} to {df_validated['datetime'].max()}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching FRED indicator {indicator}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main FRED data collection function"""
    print("🚀 Starting FRED Economic Data Collection")
    print("=" * 50)
    
    try:
        # Load configuration
        config = load_config()
        sources = load_sources()
        schema = load_schema()
        
        indicators = config.get('fred', {}).get('indicators', [])
        fred_api_key = sources.get('fred', {}).get('api_key', None)
        
        print(f"📊 Configuration loaded:")
        print(f"   🎯 Indicators: {len(indicators)}")
        print(f"   🔑 API Key: {'✅ Configured' if fred_api_key else '❌ Missing'}")
        print()
        
        if not fred_api_key:
            print("❌ FRED API key not found in sources.yaml")
            print("Please add your FRED API key to the configuration")
            return
            
        if not indicators:
            print("❌ No FRED indicators configured")
            print("Please add indicators to fred_requirements.yaml")
            return
        
        # Initialize FRED API
        fred = Fred(api_key=fred_api_key)
        data_dir = ensure_data_dir()
        
        print(f"📁 Data directory: {data_dir}")
        print()
        
        # Collect each indicator
        success_count = 0
        total_count = len(indicators)
        
        for indicator in indicators:
            if fetch_and_store_fred_indicator(indicator, fred, data_dir, schema):
                success_count += 1
        
        # Summary
        print("=" * 50)
        print(f"📊 FRED Collection Summary:")
        print(f"   ✅ Successful: {success_count}/{total_count}")
        print(f"   📈 Success Rate: {success_count/total_count*100:.1f}%")
        print("=" * 50)
        
        if success_count == total_count:
            print("🎉 All FRED indicators collected successfully!")
        elif success_count > 0:
            print("⚠️ Partial success - some indicators failed")
        else:
            print("❌ Collection failed - no indicators collected")
            
    except Exception as e:
        print(f"❌ FRED collection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 