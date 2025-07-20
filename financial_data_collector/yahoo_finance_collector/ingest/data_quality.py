#!/usr/bin/env python3
"""
Data Quality Monitor
Checks collected data for completeness, freshness, and validity.
"""

import yaml
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

def setup_logging():
    """Setup logging for data quality checks"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def check_data_freshness(data_dir: Path, data_type: str, max_age_hours: int = 24) -> Dict[str, Any]:
    """Check if data files are fresh (updated within max_age_hours)"""
    results = {
        'data_type': data_type,
        'files_checked': 0,
        'fresh_files': 0,
        'stale_files': 0,
        'missing_files': 0,
        'details': []
    }
    
    if not data_dir.exists():
        results['missing_files'] = 1
        return results
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    for file_path in data_dir.glob('*.parquet'):
        results['files_checked'] += 1
        file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        if file_age > cutoff_time:
            results['fresh_files'] += 1
            results['details'].append({
                'file': file_path.name,
                'status': 'fresh',
                'age_hours': (datetime.now() - file_age).total_seconds() / 3600
            })
        else:
            results['stale_files'] += 1
            results['details'].append({
                'file': file_path.name,
                'status': 'stale',
                'age_hours': (datetime.now() - file_age).total_seconds() / 3600
            })
    
    return results

def check_data_completeness(data_dir: Path, data_type: str, expected_files: List[str]) -> Dict[str, Any]:
    """Check if expected data files exist"""
    results = {
        'data_type': data_type,
        'expected_files': len(expected_files),
        'found_files': 0,
        'missing_files': [],
        'found_files_list': []
    }
    
    if not data_dir.exists():
        results['missing_files'] = expected_files
        return results
    
    existing_files = [f.name for f in data_dir.glob('*.parquet')]
    results['found_files'] = len(existing_files)
    results['found_files_list'] = existing_files
    
    for expected_file in expected_files:
        if expected_file not in existing_files:
            results['missing_files'].append(expected_file)
    
    return results

def check_ohlcv_completeness(data_dir: Path, config: Dict) -> Dict[str, Any]:
    """Check OHLCV data completeness based on config"""
    tickers = config.get('ohlcv', {}).get('tickers', [])
    intervals = config.get('ohlcv', {}).get('intervals', [])
    
    expected_files = []
    for ticker in tickers:
        for interval in intervals:
            expected_files.append(f"{ticker.replace('.', '_')}_{interval}.parquet")
    
    return check_data_completeness(data_dir, 'ohlcv', expected_files)

def check_macro_completeness(data_dir: Path, config: Dict) -> Dict[str, Any]:
    """Check macro data completeness based on config"""
    indicators = config.get('macro', {}).get('indicators', [])
    expected_files = [f"{indicator}.parquet" for indicator in indicators]
    
    return check_data_completeness(data_dir, 'macro', expected_files)

def check_fundamentals_completeness(data_dir: Path, config: Dict) -> Dict[str, Any]:
    """Check fundamentals data completeness based on config"""
    tickers = config.get('fundamentals', {}).get('tickers', [])
    expected_files = [f"{ticker.replace('.', '_')}_fundamentals.parquet" for ticker in tickers]
    
    return check_data_completeness(data_dir, 'fundamentals', expected_files)

def check_events_completeness(data_dir: Path, config: Dict) -> Dict[str, Any]:
    """Check events data completeness based on config"""
    events_config = config.get('events', {})
    expected_files = []
    
    # Check earnings events
    earnings_tickers = events_config.get('earnings', {}).get('tickers', [])
    for ticker in earnings_tickers:
        expected_files.append(f"{ticker.replace('.', '_')}_earnings.parquet")
    
    # Check dividend events
    dividend_tickers = events_config.get('dividends', {}).get('tickers', [])
    for ticker in dividend_tickers:
        expected_files.append(f"{ticker.replace('.', '_')}_dividends.parquet")
    
    return check_data_completeness(data_dir, 'events', expected_files)

def validate_data_schema(data_dir: Path, schema_dir: Path, data_type: str) -> Dict[str, Any]:
    """Validate data against JSON schemas"""
    results = {
        'data_type': data_type,
        'files_validated': 0,
        'valid_files': 0,
        'invalid_files': 0,
        'validation_errors': []
    }
    
    schema_file = schema_dir / f'{data_type}.json'
    if not schema_file.exists():
        results['validation_errors'].append(f"Schema file not found: {schema_file}")
        return results
    
    with open(schema_file, 'r') as f:
        schema = json.load(f)
    
    from jsonschema import validate, ValidationError
    
    for file_path in data_dir.glob('*.parquet'):
        results['files_validated'] += 1
        try:
            df = pd.read_parquet(file_path)
            for _, row in df.iterrows():
                record = row.to_dict()
                validate(instance=record, schema=schema)
            results['valid_files'] += 1
        except ValidationError as e:
            results['invalid_files'] += 1
            results['validation_errors'].append(f"{file_path.name}: {str(e)}")
        except Exception as e:
            results['invalid_files'] += 1
            results['validation_errors'].append(f"{file_path.name}: {str(e)}")
    
    return results

def generate_quality_report(quality_results: Dict[str, Any], logger: logging.Logger):
    """Generate a comprehensive data quality report"""
    logger.info("\n" + "="*60)
    logger.info("🔍 DATA QUALITY REPORT")
    logger.info("="*60)
    
    total_issues = 0
    
    for check_type, results in quality_results.items():
        logger.info(f"\n📊 {check_type.upper()}:")
        
        if 'freshness' in check_type:
            logger.info(f"  Files checked: {results['files_checked']}")
            logger.info(f"  Fresh files: {results['fresh_files']}")
            logger.info(f"  Stale files: {results['stale_files']}")
            if results['stale_files'] > 0:
                total_issues += results['stale_files']
                logger.warning(f"  ⚠️  {results['stale_files']} stale files found")
        
        elif 'completeness' in check_type:
            logger.info(f"  Expected files: {results['expected_files']}")
            logger.info(f"  Found files: {results['found_files']}")
            missing = len(results['missing_files'])
            if missing > 0:
                total_issues += missing
                logger.warning(f"  ⚠️  {missing} missing files: {results['missing_files']}")
        
        elif 'validation' in check_type:
            logger.info(f"  Files validated: {results['files_validated']}")
            logger.info(f"  Valid files: {results['valid_files']}")
            invalid = results['invalid_files']
            if invalid > 0:
                total_issues += invalid
                logger.warning(f"  ⚠️  {invalid} invalid files found")
                for error in results['validation_errors'][:3]:  # Show first 3 errors
                    logger.error(f"    Error: {error}")
    
    logger.info("\n" + "="*60)
    if total_issues == 0:
        logger.info("✅ All data quality checks passed!")
    else:
        logger.warning(f"⚠️  Found {total_issues} data quality issues")
    logger.info("="*60)

def main():
    """Main data quality monitoring function"""
    logger = setup_logging()
    config = load_config()
    
    logger.info("🔍 Starting Data Quality Monitoring")
    
    base_data_dir = Path(__file__).parent.parent.parent / 'financial_data'
    schema_dir = Path(__file__).parent.parent / 'schema'
    
    quality_results = {}
    
    # Check each data type
    data_types = ['ohlcv', 'macro', 'fundamentals', 'events']
    
    for data_type in data_types:
        data_dir = base_data_dir / data_type
        
        # Check freshness
        freshness_key = f"{data_type}_freshness"
        quality_results[freshness_key] = check_data_freshness(data_dir, data_type)
        
        # Check completeness
        if data_type == 'ohlcv':
            completeness_key = f"{data_type}_completeness"
            quality_results[completeness_key] = check_ohlcv_completeness(data_dir, config)
        elif data_type == 'macro':
            completeness_key = f"{data_type}_completeness"
            quality_results[completeness_key] = check_macro_completeness(data_dir, config)
        elif data_type == 'fundamentals':
            completeness_key = f"{data_type}_completeness"
            quality_results[completeness_key] = check_fundamentals_completeness(data_dir, config)
        elif data_type == 'events':
            completeness_key = f"{data_type}_completeness"
            quality_results[completeness_key] = check_events_completeness(data_dir, config)
        
        # Validate schema (if data exists)
        if data_dir.exists():
            validation_key = f"{data_type}_validation"
            quality_results[validation_key] = validate_data_schema(data_dir, schema_dir, data_type)
    
    # Generate comprehensive report
    generate_quality_report(quality_results, logger)

if __name__ == '__main__':
    main() 