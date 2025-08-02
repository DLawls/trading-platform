#!/usr/bin/env python3
"""
Enhanced FRED Economic Data Collector
Collects comprehensive macroeconomic indicators from the Federal Reserve Economic Data (FRED) API
with advanced metadata, quality monitoring, and analytics capabilities.
"""

import yaml
import os
from pathlib import Path
import pandas as pd
from fredapi import Fred
import json
from jsonschema import validate, ValidationError
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, List, Optional, Any
import numpy as np

class FREDCollector:
    """Enhanced FRED Economic Data Collector"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent / 'config' / 'fred_requirements.yaml'
        self.sources_path = Path(__file__).parent.parent / 'config' / 'sources.yaml'
        self.schema_path = Path(__file__).parent.parent / 'schema' / 'fred_economic.json'
        
        # Data directory
        self.data_dir = Path(__file__).parent.parent.parent / 'financial_data' / 'economic' / 'fred'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configurations
        self.config = self._load_config()
        self.sources = self._load_sources()
        self.schema = self._load_schema()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize FRED API
        self.fred = self._initialize_fred_api()
        
        # Collection statistics
        self.stats = {
            'total_indicators': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'total_records': 0,
            'start_time': datetime.now()
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load FRED collector configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading FRED config: {e}")
            return {}
    
    def _load_sources(self) -> Dict[str, Any]:
        """Load FRED API configuration"""
        try:
            with open(self.sources_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading FRED sources: {e}")
            return {}
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load FRED data validation schema"""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading FRED schema: {e}")
            return {}
    
    def _setup_logging(self):
        """Setup enhanced logging"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'fred_collector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('FREDCollector')
    
    def _initialize_fred_api(self) -> Optional[Fred]:
        """Initialize FRED API client"""
        try:
            api_key = self.sources.get('fred', {}).get('api_key')
            if not api_key:
                self.logger.error("FRED API key not found in sources.yaml")
                return None
            
            fred = Fred(api_key=api_key)
            self.logger.info("✅ FRED API initialized successfully")
            return fred
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FRED API: {e}")
            return None
    
    def _get_indicators(self) -> List[Dict[str, Any]]:
        """Get enhanced indicator configuration"""
        indicators = self.config.get('fred', {}).get('indicators', [])
        
        # Handle both old and new configuration formats
        enhanced_indicators = []
        for indicator in indicators:
            if isinstance(indicator, str):
                # Old format - convert to new format
                enhanced_indicators.append({
                    'indicator': indicator,
                    'name': indicator,
                    'description': f"Economic indicator {indicator}",
                    'category': 'general',
                    'frequency': 'unknown',
                    'priority': 'medium'
                })
            elif isinstance(indicator, dict):
                # New enhanced format
                enhanced_indicators.append(indicator)
        
        return enhanced_indicators
    
    def _fetch_indicator_data(self, indicator_config: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Fetch data for a single FRED indicator with enhanced metadata"""
        indicator_id = indicator_config.get('indicator')
        indicator_name = indicator_config.get('name', indicator_id)
        
        try:
            self.logger.info(f"📊 Fetching: {indicator_name} ({indicator_id})")
            
            # Check if FRED API is available
            if not self.fred:
                self.logger.error(f"FRED API not available for {indicator_id}")
                return None
            
            # Get the time series data
            series = self.fred.get_series(indicator_id)
            if series is None or series.empty:
                self.logger.warning(f"No data returned for {indicator_id}")
                return None
            
            # Get enhanced metadata
            try:
                series_info = self.fred.get_series_info(indicator_id)
                units = series_info.get('units', 'Unknown')
                frequency = series_info.get('frequency', indicator_config.get('frequency', 'Unknown'))
                title = series_info.get('title', indicator_name)
                last_updated = series_info.get('last_updated', 'Unknown')
                
                self.logger.info(f"   📋 Title: {title}")
                self.logger.info(f"   📊 Frequency: {frequency}")
                self.logger.info(f"   📏 Units: {units}")
                self.logger.info(f"   🔄 Last Updated: {last_updated}")
                
            except Exception as e:
                self.logger.warning(f"Could not fetch metadata for {indicator_id}: {e}")
                units = indicator_config.get('units', 'Unknown')
                frequency = indicator_config.get('frequency', 'Unknown')
                title = indicator_name
            
            # Convert to DataFrame with enhanced metadata
            df = series.reset_index()
            df.columns = ['date', 'value']
            
            # Add comprehensive metadata
            df['indicator'] = indicator_id
            df['name'] = indicator_name
            df['description'] = indicator_config.get('description', title)
            df['category'] = indicator_config.get('category', 'general')
            df['priority'] = indicator_config.get('priority', 'medium')
            df['units'] = units
            df['frequency'] = frequency
            df['source'] = 'FRED'
            df['collection_date'] = datetime.now().isoformat()
            
            # Convert datetime
            df['datetime'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Data quality metrics
            total_records = len(df)
            null_records = df['value'].isnull().sum()
            quality_score = ((total_records - null_records) / total_records) * 100 if total_records > 0 else 0
            
            self.logger.info(f"   📈 Records: {total_records}")
            self.logger.info(f"   📅 Date Range: {df['date'].min()} to {df['date'].max()}")
            self.logger.info(f"   💎 Quality Score: {quality_score:.1f}%")
            
            if null_records > 0:
                self.logger.warning(f"   ⚠️ Null values: {null_records}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching {indicator_id}: {e}")
            return None
    
    def _validate_data(self, df: pd.DataFrame, indicator_config: Dict[str, Any]) -> pd.DataFrame:
        """Enhanced data validation with quality scoring"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        indicator_id = indicator_config.get('indicator')
        valid_rows = []
        
        for _, row in df.iterrows():
            try:
                # Skip records with null values
                try:
                    value = float(row['value'])
                except (ValueError, TypeError):
                    continue
                
                record = {
                    'indicator': row['indicator'],
                    'name': row['name'],
                    'description': row['description'],
                    'category': row['category'],
                    'priority': row['priority'],
                    'datetime': row['datetime'],
                    'value': float(row['value']),
                    'units': row['units'],
                    'frequency': row['frequency'],
                    'source': row['source'],
                    'collection_date': row['collection_date']
                }
                
                # Validate against schema
                validate(instance=record, schema=self.schema)
                valid_rows.append(record)
                
            except (ValidationError, KeyError, ValueError, TypeError) as e:
                self.logger.debug(f"Validation error for {indicator_id}: {e}")
                continue
        
        validated_df = pd.DataFrame(valid_rows)
        
        if not validated_df.empty:
            # Quality assessment
            original_count = len(df)
            validated_count = len(validated_df)
            quality_rate = (validated_count / original_count) * 100 if original_count > 0 else 0
            
            self.logger.info(f"   ✅ Validation: {validated_count}/{original_count} records ({quality_rate:.1f}%)")
            
            # Check for data quality issues
            min_records = self.config.get('fred', {}).get('quality', {}).get('min_records', 10)
            if validated_count < min_records:
                self.logger.warning(f"   ⚠️ Low record count: {validated_count} < {min_records}")
        
        return validated_df
    
    def _save_indicator_data(self, df: pd.DataFrame, indicator_config: Dict[str, Any]) -> bool:
        """Save validated indicator data"""
        if df is None or df.empty:
            return False
        
        try:
            indicator_id = indicator_config.get('indicator')
            filename = f"{indicator_id}.parquet"
            filepath = self.data_dir / filename
            
            # Save to parquet
            df.to_parquet(filepath, index=False)
            
            self.logger.info(f"   💾 Saved: {filename}")
            self.logger.info(f"   📁 Path: {filepath}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save {indicator_config.get('indicator')}: {e}")
            return False
    
    def _analyze_data_quality(self, df: pd.DataFrame, indicator_config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive data quality analysis"""
        if df is None or df.empty:
            return {'quality_score': 0, 'issues': ['No data']}
        
        analysis = {
            'total_records': len(df),
            'null_count': df['value'].isnull().sum(),
            'date_range': {
                'start': df['datetime'].min(),
                'end': df['datetime'].max()
            },
            'value_stats': {
                'min': df['value'].min(),
                'max': df['value'].max(),
                'mean': df['value'].mean(),
                'std': df['value'].std()
            },
            'issues': []
        }
        
        # Calculate quality score
        quality_factors = []
        
        # Completeness (no nulls)
        completeness = ((len(df) - analysis['null_count']) / len(df)) * 100
        quality_factors.append(completeness)
        
        # Freshness (recent data)
        try:
            latest_date = pd.to_datetime(analysis['date_range']['end'])
            days_old = (datetime.now() - latest_date).days
            freshness_threshold = self.config.get('fred', {}).get('quality', {}).get('freshness_days', 90)
            freshness = max(0, (freshness_threshold - days_old) / freshness_threshold * 100)
            quality_factors.append(freshness)
            
            if days_old > freshness_threshold:
                analysis['issues'].append(f"Data is {days_old} days old")
        except:
            quality_factors.append(50)  # Neutral score if can't determine
        
        # Coverage (sufficient records)
        min_records = self.config.get('fred', {}).get('quality', {}).get('min_records', 10)
        coverage = min(100, (len(df) / min_records) * 100)
        quality_factors.append(coverage)
        
        if len(df) < min_records:
            analysis['issues'].append(f"Low record count: {len(df)} < {min_records}")
        
        # Overall quality score
        analysis['quality_score'] = sum(quality_factors) / len(quality_factors)
        
        return analysis
    
    def collect_indicator(self, indicator_config: Dict[str, Any]) -> bool:
        """Collect data for a single indicator with comprehensive processing"""
        indicator_id = indicator_config.get('indicator')
        
        try:
            # Fetch data
            df = self._fetch_indicator_data(indicator_config)
            if df is None or df.empty:
                self.stats['failed_collections'] += 1
                return False
            
            # Validate data
            validated_df = self._validate_data(df, indicator_config)
            if validated_df.empty:
                self.logger.error(f"❌ Validation failed for {indicator_id}")
                # For Chinese indicators, try to save the original data even if validation fails
                if 'cn_' in indicator_config.get('category', ''):
                    self.logger.warning(f"⚠️ Attempting to save unvalidated data for Chinese indicator {indicator_id}")
                    if self._save_indicator_data(df, indicator_config):
                        self.stats['successful_collections'] += 1
                        self.stats['total_records'] += len(df)
                        self.logger.info(f"   ✅ Successfully collected {indicator_id} (unvalidated)")
                        return True
                self.stats['failed_collections'] += 1
                return False
            
            # Analyze quality
            quality_analysis = self._analyze_data_quality(validated_df, indicator_config)
            self.logger.info(f"   🎯 Quality Score: {quality_analysis['quality_score']:.1f}%")
            
            if quality_analysis['issues']:
                for issue in quality_analysis['issues']:
                    self.logger.warning(f"   ⚠️ {issue}")
            
            # Save data
            if self._save_indicator_data(validated_df, indicator_config):
                self.stats['successful_collections'] += 1
                self.stats['total_records'] += len(validated_df)
                self.logger.info(f"   ✅ Successfully collected {indicator_id}")
                return True
            else:
                self.stats['failed_collections'] += 1
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Unexpected error collecting {indicator_id}: {e}")
            self.stats['failed_collections'] += 1
            return False
    
    def run_collection(self) -> bool:
        """Run enhanced FRED data collection"""
        self.logger.info("🚀 Starting Enhanced FRED Economic Data Collection")
        self.logger.info("=" * 70)
        
        if not self.fred:
            self.logger.error("❌ FRED API not available")
            return False
        
        # Get indicators
        indicators = self._get_indicators()
        if not indicators:
            self.logger.error("❌ No indicators configured")
            return False
        
        self.stats['total_indicators'] = len(indicators)
        
        self.logger.info(f"📊 Configuration Summary:")
        self.logger.info(f"   🎯 Total Indicators: {len(indicators)}")
        self.logger.info(f"   📁 Data Directory: {self.data_dir}")
        
        # Group indicators by category for organized collection
        categories = {}
        for indicator in indicators:
            category = indicator.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(indicator)
        
        self.logger.info(f"   📋 Categories: {list(categories.keys())}")
        self.logger.info("")
        
        # Collect indicators by category
        for category, category_indicators in categories.items():
            self.logger.info(f"📈 Collecting {category.upper()} indicators ({len(category_indicators)}):")
            
            for indicator_config in category_indicators:
                self.collect_indicator(indicator_config)
                
                # Rate limiting
                time.sleep(0.5)  # Respect FRED API rate limits
            
            self.logger.info("")
        
        # Final summary
        self._print_collection_summary()
        
        success_rate = (self.stats['successful_collections'] / self.stats['total_indicators']) * 100
        return success_rate > 80  # Consider successful if > 80% success rate
    
    def _print_collection_summary(self):
        """Print comprehensive collection summary"""
        duration = datetime.now() - self.stats['start_time']
        success_rate = (self.stats['successful_collections'] / self.stats['total_indicators']) * 100 if self.stats['total_indicators'] > 0 else 0
        
        self.logger.info("=" * 70)
        self.logger.info("📊 FRED Collection Summary")
        self.logger.info("=" * 70)
        self.logger.info(f"🎯 Total Indicators: {self.stats['total_indicators']}")
        self.logger.info(f"✅ Successful: {self.stats['successful_collections']}")
        self.logger.info(f"❌ Failed: {self.stats['failed_collections']}")
        self.logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        self.logger.info(f"📊 Total Records: {self.stats['total_records']:,}")
        self.logger.info(f"⏱️ Duration: {duration}")
        self.logger.info(f"📁 Data Location: {self.data_dir}")
        self.logger.info("=" * 70)
        
        if success_rate >= 90:
            self.logger.info("🎉 Excellent collection performance!")
        elif success_rate >= 80:
            self.logger.info("✅ Good collection performance")
        else:
            self.logger.warning("⚠️ Collection performance needs attention")

def main():
    """Main FRED collection function"""
    collector = FREDCollector()
    success = collector.run_collection()
    
    if not success:
        exit(1)

if __name__ == '__main__':
    main() 