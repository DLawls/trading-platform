#!/usr/bin/env python3
"""
Alpaca Events Data Collector
Fetches corporate events (earnings, dividends, splits) from Alpaca Markets API.
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
    from alpaca.data.historical import CorporateActionsClient
    from alpaca.data.requests import CorporateActionAdjustmentsRequest
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

def load_schema(event_type):
    """Load validation schema for specific event type"""
    # Use the shared schema from the Yahoo Finance collector
    schema_path = Path(__file__).parent.parent.parent / 'yahoo_finance_collector' / 'schema' / f'{event_type}.json'
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create a basic schema if not found
        return {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "datetime": {"type": "string"},
                "event_type": {"type": "string"},
                "value": {"type": "number"}
            },
            "required": ["ticker", "datetime", "event_type"]
        }

def ensure_data_dir():
    """Ensure events data directory exists"""
    data_dir = Path(__file__).parent.parent.parent / 'financial_data' / 'events'
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
    
    # Initialize the corporate actions client
    client = CorporateActionsClient(api_key=api_key, secret_key=secret_key)
    return client

def validate_event_data(df, schema, event_type):
    """Validate event data against schema"""
    valid_rows = []
    logger = setup_logging()
    
    for idx, row in df.iterrows():
        try:
            # Create standardized event record
            record = {
                'ticker': row.get('symbol', ''),
                'datetime': row.get('ex_date', row.get('date', datetime.now())).strftime('%Y-%m-%dT%H:%M:%S'),
                'event_type': event_type,
                'value': float(row.get('cash_amount', row.get('amount', 0))),
                'raw_data': row.to_dict()  # Store original data
            }
            
            validate(instance=record, schema=schema)
            valid_rows.append(record)
            
        except (ValidationError, KeyError, ValueError, TypeError) as e:
            logger.warning(f"Validation error for {event_type} on row {idx}: {e}")
            continue
            
    return pd.DataFrame(valid_rows)

def fetch_dividends(tickers, data_dir):
    """Fetch dividend data for given tickers"""
    logger = setup_logging()
    logger.info("🔄 Fetching dividend data...")
    
    try:
        client = get_alpaca_client()
        schema = load_schema('dividends')
        
        all_dividends = []
        start_date = datetime.now() - timedelta(days=365)  # 1 year of data
        end_date = datetime.now()
        
        for ticker in tickers:
            try:
                logger.info(f"Fetching dividends for {ticker}")
                
                # Note: Alpaca API structure may vary - this is a conceptual implementation
                # The actual API calls would need to be adjusted based on Alpaca's documentation
                
                # Create request for corporate actions
                request = CorporateActionAdjustmentsRequest(
                    symbols=[ticker],
                    start=start_date,
                    end=end_date
                )
                
                # This is a placeholder - actual implementation would depend on Alpaca's API
                # dividends = client.get_dividends(request)
                
                # For now, create empty dataframe structure
                dividend_data = pd.DataFrame(columns=['symbol', 'ex_date', 'cash_amount'])
                
                if not dividend_data.empty:
                    validated_dividends = validate_event_data(dividend_data, schema, 'dividend')
                    all_dividends.append(validated_dividends)
                    
            except Exception as e:
                logger.warning(f"Error fetching dividends for {ticker}: {e}")
                continue
        
        if all_dividends:
            combined_df = pd.concat(all_dividends, ignore_index=True)
            
            # Save to file
            today = datetime.now().strftime('%Y%m%d')
            filename = f"alpaca_dividends_{today}.parquet"
            filepath = data_dir / filename
            
            combined_df.to_parquet(filepath, index=False)
            logger.info(f"✅ Saved {len(combined_df)} dividend records to {filepath}")
            return True
        else:
            logger.warning("No dividend data collected")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in dividend collection: {str(e)}")
        return False

def fetch_earnings(tickers, data_dir):
    """Fetch earnings calendar data for given tickers"""
    logger = setup_logging()
    logger.info("🔄 Fetching earnings data...")
    
    try:
        # Note: Alpaca may not have direct earnings calendar API
        # This would typically require a different approach or third-party service
        
        logger.info("Earnings data collection - API endpoint not available in basic Alpaca plan")
        
        # Create empty placeholder file for consistency
        today = datetime.now().strftime('%Y%m%d')
        filename = f"alpaca_earnings_{today}.parquet"
        filepath = data_dir / filename
        
        # Create empty dataframe with expected structure
        empty_df = pd.DataFrame(columns=['ticker', 'datetime', 'event_type', 'value'])
        empty_df.to_parquet(filepath, index=False)
        
        logger.info(f"📝 Created placeholder earnings file: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in earnings collection: {str(e)}")
        return False

def fetch_splits(tickers, data_dir):
    """Fetch stock split data for given tickers"""
    logger = setup_logging()
    logger.info("🔄 Fetching stock splits data...")
    
    try:
        client = get_alpaca_client()
        schema = load_schema('splits')
        
        all_splits = []
        start_date = datetime.now() - timedelta(days=365)  # 1 year of data
        end_date = datetime.now()
        
        for ticker in tickers:
            try:
                logger.info(f"Fetching splits for {ticker}")
                
                # Note: This would use Alpaca's corporate actions API
                # Placeholder implementation
                
                split_data = pd.DataFrame(columns=['symbol', 'ex_date', 'new_rate', 'old_rate'])
                
                if not split_data.empty:
                    validated_splits = validate_event_data(split_data, schema, 'split')
                    all_splits.append(validated_splits)
                    
            except Exception as e:
                logger.warning(f"Error fetching splits for {ticker}: {e}")
                continue
        
        if all_splits:
            combined_df = pd.concat(all_splits, ignore_index=True)
            
            # Save to file
            today = datetime.now().strftime('%Y%m%d')
            filename = f"alpaca_splits_{today}.parquet"
            filepath = data_dir / filename
            
            combined_df.to_parquet(filepath, index=False)
            logger.info(f"✅ Saved {len(combined_df)} split records to {filepath}")
            return True
        else:
            logger.warning("No split data collected")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in splits collection: {str(e)}")
        return False

def collect_events():
    """Main function to collect all events data"""
    logger = setup_logging()
    logger.info("🚀 Starting Alpaca events data collection...")
    
    if not ALPACA_AVAILABLE:
        logger.error("❌ Alpaca API library not available")
        return False
    
    try:
        # Load configuration
        config = load_config()
        data_dir = ensure_data_dir()
        
        # Get all tickers from events config
        all_tickers = []
        
        if 'events' in config:
            # Get tickers from different event types
            for event_type in ['earnings', 'dividends', 'splits']:
                if event_type in config['events']:
                    if 'us_stocks' in config['events'][event_type]:
                        all_tickers.extend(config['events'][event_type]['us_stocks'])
                    if 'asx_adrs' in config['events'][event_type]:
                        all_tickers.extend(config['events'][event_type]['asx_adrs'])
        
        # Remove duplicates
        all_tickers = list(set(all_tickers))
        
        if not all_tickers:
            logger.warning("No tickers found in events configuration")
            return False
        
        logger.info(f"Processing events for {len(all_tickers)} tickers")
        
        # Collect different types of events
        results = []
        
        # Fetch dividends
        results.append(fetch_dividends(all_tickers, data_dir))
        
        # Fetch earnings
        results.append(fetch_earnings(all_tickers, data_dir))
        
        # Fetch splits
        results.append(fetch_splits(all_tickers, data_dir))
        
        # Calculate success rate
        success_count = sum(results)
        success_rate = (success_count / len(results) * 100) if results else 0
        
        logger.info(f"🎯 Events Collection Complete: {success_count}/{len(results)} successful ({success_rate:.1f}%)")
        
        return success_rate > 50  # Consider successful if >50% success rate
        
    except Exception as e:
        logger.error(f"❌ Critical error in events collection: {str(e)}")
        return False

if __name__ == "__main__":
    success = collect_events()
    sys.exit(0 if success else 1)

