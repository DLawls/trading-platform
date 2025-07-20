#!/usr/bin/env python3
"""
Shared Data Validation Utilities
Common validation functions for all financial data collectors.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

def validate_dataframe_schema(df: pd.DataFrame, schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate DataFrame against JSON schema
    
    Args:
        df: DataFrame to validate
        schema: JSON schema dictionary
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required columns
    required_columns = schema.get('required', [])
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
    
    # Check column types
    properties = schema.get('properties', {})
    for column, column_schema in properties.items():
        if column in df.columns:
            expected_type = column_schema.get('type')
            
            if expected_type == 'number':
                if not pd.api.types.is_numeric_dtype(df[column]):
                    errors.append(f"Column '{column}' should be numeric")
            elif expected_type == 'string':
                if not pd.api.types.is_string_dtype(df[column]) and not pd.api.types.is_object_dtype(df[column]):
                    errors.append(f"Column '{column}' should be string/object")
            elif expected_type == 'date':
                try:
                    pd.to_datetime(df[column])
                except:
                    errors.append(f"Column '{column}' should be valid datetime")
    
    return len(errors) == 0, errors

def check_data_freshness(data_path: Path, max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Check if data files are fresh (not too old)
    
    Args:
        data_path: Path to data file or directory
        max_age_hours: Maximum age in hours before data is considered stale
    
    Returns:
        Dictionary with freshness information
    """
    if not data_path.exists():
        return {
            'is_fresh': False,
            'reason': 'Data path does not exist',
            'age_hours': None,
            'last_modified': None
        }
    
    if data_path.is_file():
        files_to_check = [data_path]
    else:
        files_to_check = list(data_path.glob('*.parquet'))
    
    if not files_to_check:
        return {
            'is_fresh': False,
            'reason': 'No data files found',
            'age_hours': None,
            'last_modified': None
        }
    
    # Find most recent file
    most_recent_file = max(files_to_check, key=lambda f: f.stat().st_mtime)
    last_modified = datetime.fromtimestamp(most_recent_file.stat().st_mtime)
    age_hours = (datetime.now() - last_modified).total_seconds() / 3600
    
    is_fresh = age_hours <= max_age_hours
    
    return {
        'is_fresh': is_fresh,
        'reason': 'Fresh' if is_fresh else f'Data is {age_hours:.1f} hours old',
        'age_hours': age_hours,
        'last_modified': last_modified,
        'most_recent_file': str(most_recent_file)
    }

def check_data_completeness(
    data_dir: Path, 
    expected_files: List[str], 
    file_pattern: str = "*.parquet"
) -> Dict[str, Any]:
    """
    Check if all expected data files are present
    
    Args:
        data_dir: Directory containing data files
        expected_files: List of expected file names (without extension)
        file_pattern: Pattern to match files
    
    Returns:
        Dictionary with completeness information
    """
    if not data_dir.exists():
        return {
            'is_complete': False,
            'missing_files': expected_files,
            'found_files': [],
            'completion_rate': 0.0
        }
    
    # Get actual files
    actual_files = [f.stem for f in data_dir.glob(file_pattern)]
    missing_files = list(set(expected_files) - set(actual_files))
    found_files = list(set(expected_files) & set(actual_files))
    
    completion_rate = len(found_files) / len(expected_files) if expected_files else 1.0
    
    return {
        'is_complete': len(missing_files) == 0,
        'missing_files': missing_files,
        'found_files': found_files,
        'completion_rate': completion_rate,
        'total_expected': len(expected_files),
        'total_found': len(found_files)
    }

def validate_ohlcv_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate OHLCV data for common issues
    
    Args:
        df: OHLCV DataFrame
    
    Returns:
        Validation results
    """
    issues = []
    
    # Check required columns
    required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        issues.append(f"Missing columns: {missing_columns}")
    
    if not missing_columns:  # Only check data if columns exist
        # Check for null values
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            issues.append(f"Null values found: {dict(null_counts[null_counts > 0])}")
        
        # Check OHLC logic (High >= Low, Close/Open between High/Low)
        if 'High' in df.columns and 'Low' in df.columns:
            invalid_high_low = (df['High'] < df['Low']).sum()
            if invalid_high_low > 0:
                issues.append(f"Invalid High < Low in {invalid_high_low} rows")
        
        # Check for negative prices
        price_columns = ['Open', 'High', 'Low', 'Close']
        for col in price_columns:
            if col in df.columns:
                negative_prices = (df[col] < 0).sum()
                if negative_prices > 0:
                    issues.append(f"Negative prices in {col}: {negative_prices} rows")
        
        # Check date continuity
        if 'Date' in df.columns:
            try:
                dates = pd.to_datetime(df['Date']).sort_values()
                date_gaps = (dates.diff() > timedelta(days=7)).sum()  # More than a week gap
                if date_gaps > 0:
                    issues.append(f"Large date gaps found: {date_gaps} instances")
            except:
                issues.append("Date column contains invalid datetime values")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'row_count': len(df),
        'column_count': len(df.columns)
    }

def validate_economic_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate economic indicator data
    
    Args:
        df: Economic data DataFrame
    
    Returns:
        Validation results
    """
    issues = []
    
    # Check required columns
    required_columns = ['date', 'value']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        issues.append(f"Missing columns: {missing_columns}")
    
    if not missing_columns:
        # Check for null values in critical columns
        if df['value'].isnull().any():
            null_count = df['value'].isnull().sum()
            issues.append(f"Null values in 'value' column: {null_count} rows")
        
        # Check date format
        try:
            pd.to_datetime(df['date'])
        except:
            issues.append("Invalid date format in 'date' column")
        
        # Check for reasonable value ranges (not too extreme)
        if df['value'].dtype in ['float64', 'int64']:
            extreme_values = ((df['value'].abs() > 1e6) | (df['value'].abs() < 1e-6)).sum()
            if extreme_values > 0:
                issues.append(f"Potentially extreme values: {extreme_values} rows")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'row_count': len(df),
        'date_range': f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else None
    }

def load_schema(schema_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load JSON schema from file
    
    Args:
        schema_path: Path to JSON schema file
    
    Returns:
        Schema dictionary or None if loading fails
    """
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load schema from {schema_path}: {e}")
        return None

def generate_validation_report(validation_results: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate a formatted validation report
    
    Args:
        validation_results: Dictionary of validation results by data type
    
    Returns:
        Formatted report string
    """
    report_lines = ["📊 Data Validation Report", "=" * 50]
    
    total_checks = len(validation_results)
    passed_checks = sum(1 for result in validation_results.values() if result.get('is_valid', False))
    
    report_lines.append(f"Overall Status: {passed_checks}/{total_checks} checks passed")
    report_lines.append("")
    
    for data_type, result in validation_results.items():
        status = "✅ PASS" if result.get('is_valid', False) else "❌ FAIL"
        report_lines.append(f"{data_type.upper()}: {status}")
        
        if not result.get('is_valid', False) and 'issues' in result:
            for issue in result['issues']:
                report_lines.append(f"  - {issue}")
        
        report_lines.append("")
    
    return "\n".join(report_lines) 