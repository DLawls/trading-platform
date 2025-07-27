#!/usr/bin/env python3
"""
Alpaca OHLCV Data Collector
Fetches price data from Alpaca Markets API following the established architecture pattern.
"""

import yaml
import os
from pathlib import Path
import pandas as pd
import json
from jsonschema import validate, ValidationError
from datetime import datetime, timedelta
import logging
import sys

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("Warning: alpaca-trade-api not installed. Run: pip install alpaca-trade-api")

def setup_logging():
    """Setup logging for this module"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def load_config():
    """Load data requirements configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_sources_config():
    """Load API sources configuration"""
    sources_path = Path(__file__).parent.parent / 'config' / 'sources.yaml'
    with open(sources_path, 'r') as f:
        return yaml.safe_load(f)

def load_schema():
    """Load OHLCV validation schema"""
    # Use the shared schema from the Yahoo Finance collector
    schema_path = Path(__file__).parent.parent.parent / 'yahoo_finance_collector' / 'schema' / 'ohlcv.json'
    with open(schema_path, 'r') as f:
        return json.load(f)

def ensure_data_dir():
    """Ensure data directory exists"""
    data_dir = Path(__file__).parent.parent.parent / 'financial_data' / 'ohlcv'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_alpaca_client():
    """Initialize Alpaca client with API credentials"""
    if not ALPACA_AVAILABLE:
        raise ImportError("Alpaca API library not available. Install with: pip install alpaca-trade-api")
    
    sources_config = load_sources_config()
    alpaca_config = sources_config['alpaca']
    
    # Check if API keys are configured
    api_key = alpaca_config['api_key']
    secret_key = alpaca_config['secret_key']
    
    if api_key == 'YOUR_ALPACA_API_KEY' or secret_key == 'YOUR_ALPACA_SECRET':
        raise ValueError("Alpaca API keys not configured. Please update config/sources.yaml")
    
    # Initialize the data client (for market data)
    client = StockHistoricalDataClient(api_key=api_key, secret_key=secret_key)
    return client

def validate_ohlcv(df, schema, ticker):
    """Validate OHLCV data against schema"""
    valid_rows = []
    logger = setup_logging()
    
    for idx, row in df.iterrows():
        try:
            # Convert timestamp to proper format
            if isinstance(idx, pd.Timestamp):
                datetime_str = idx.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                datetime_str = pd.to_datetime(idx).strftime('%Y-%m-%dT%H:%M:%S')
            
            record = {
                'ticker': ticker,
                'datetime': datetime_str,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']) if pd.notna(row['volume']) else 0.0
            }
            
            validate(instance=record, schema=schema)
            valid_rows.append(record)
            
        except (ValidationError, KeyError, ValueError, TypeError) as e:
            logger.warning(f"Validation error for {ticker} on row {idx}: {e}")
            continue
            
    return pd.DataFrame(valid_rows)

def fetch_and_store_ohlcv(ticker, interval, data_dir, schema):
    """Fetch OHLCV data from Alpaca and store it"""
    logger = setup_logging()
    
    try:
        client = get_alpaca_client()
        
        # Map interval to Alpaca TimeFrame
        if interval == 'daily':
            timeframe = TimeFrame.Day
            # Get 2 years of daily data
            start_date = datetime.now() - timedelta(days=730)
        elif interval == 'hourly':
            timeframe = TimeFrame.Hour
            # Get 1 month of hourly data
            start_date = datetime.now() - timedelta(days=30)
        else:
            logger.error(f"Unsupported interval: {interval}")
            return False
        
        end_date = datetime.now()
        
        logger.info(f"Fetching {ticker} ({interval}) from {start_date.date()} to {end_date.date()}")
        
        # Create request
        request_params = StockBarsRequest(
            symbol_or_symbols=[ticker],
            timeframe=timeframe,
            start=start_date,
            end=end_date
        )
        
        # Fetch data
        bars = client.get_stock_bars(request_params)
        
        if not bars or ticker not in bars:
            logger.warning(f"No data returned for {ticker} ({interval})")
            return False
        
        # Convert to DataFrame
        df = bars[ticker].df
        
        if df.empty:
            logger.warning(f"Empty dataset for {ticker} ({interval})")
            return False
        
        logger.info(f"Retrieved {len(df)} records for {ticker} ({interval})")
        
        # Validate data
        validated_df = validate_ohlcv(df, schema, ticker)
        
        if validated_df.empty:
            logger.error(f"No valid data after validation for {ticker} ({interval})")
            return False
        
        # Generate filename
        today = datetime.now().strftime('%Y%m%d')
        filename = f"{ticker.replace('.', '_')}_{interval}_ohlcv_{today}.parquet"
        filepath = data_dir / filename
        
        # Save to parquet
        validated_df.to_parquet(filepath, index=False)
        logger.info(f"✅ Saved {len(validated_df)} records to {filepath}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fetching {ticker} ({interval}): {str(e)}")
        return False

def collect_ohlcv():
    """Main function to collect all OHLCV data"""
    logger = setup_logging()
    logger.info("🚀 Starting Alpaca OHLCV data collection...")
    
    if not ALPACA_AVAILABLE:
        logger.error("❌ Alpaca API library not available")
        return False
    
    try:
        # Load configuration
        config = load_config()
        schema = load_schema()
        data_dir = ensure_data_dir()
        
        # Get all tickers from config
        all_tickers = []
        
        if 'ohlcv' in config:
            # Add US stocks
            if 'us_stocks' in config['ohlcv']:
                all_tickers.extend(config['ohlcv']['us_stocks'])
            
            # Add ASX ADRs
            if 'asx_adrs' in config['ohlcv']:
                all_tickers.extend(config['ohlcv']['asx_adrs'])
            
            # Add crypto (if enabled)
            if 'crypto' in config['ohlcv']:
                all_tickers.extend(config['ohlcv']['crypto'])
        
        if not all_tickers:
            logger.warning("No tickers found in configuration")
            return False
        
        # Get intervals
        intervals = config['ohlcv'].get('intervals', ['daily'])
        
        logger.info(f"Processing {len(all_tickers)} tickers across {len(intervals)} intervals")
        
        # Track results
        total_success = 0
        total_attempts = 0
        
        # Process each ticker and interval
        for ticker in all_tickers:
            for interval in intervals:
                total_attempts += 1
                if fetch_and_store_ohlcv(ticker, interval, data_dir, schema):
                    total_success += 1
        
        # Summary
        success_rate = (total_success / total_attempts * 100) if total_attempts > 0 else 0
        logger.info(f"🎯 OHLCV Collection Complete: {total_success}/{total_attempts} successful ({success_rate:.1f}%)")
        
        return success_rate > 80  # Consider successful if >80% success rate
        
    except Exception as e:
        logger.error(f"❌ Critical error in OHLCV collection: {str(e)}")
        return False

if __name__ == "__main__":
    success = collect_ohlcv()
    sys.exit(0 if success else 1)

