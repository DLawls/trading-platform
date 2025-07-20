#!/usr/bin/env python3
"""
ABS Economic Data Web Scraper
Scrapes Australian economic indicators from the ABS Key Economic Indicators webpage.
"""

import requests
import pandas as pd
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
from bs4 import BeautifulSoup
import re

class ABSDataScraper:
    """ABS Key Economic Indicators web scraper"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent / 'config' / 'sources.yaml'
        self.requirements_path = Path(__file__).parent.parent / 'config' / 'abs_requirements.yaml'
        
        # ABS Key Economic Indicators URL
        self.target_url = "https://www.abs.gov.au/statistics/economy/key-indicators"
        
        # Output directory
        self.output_dir = Path(__file__).parent.parent.parent / 'financial_data' / 'economic' / 'abs'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup logging
        self._setup_logging()
        
        # Setup session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _load_config(self) -> Dict[str, Any]:
        """Load collector configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return config.get('abs', {})
            else:
                return {}
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {}
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.output_dir / 'abs_collector.log')
            ]
        )
        
        self.logger = logging.getLogger('ABSDataScraper')
    
    def scrape_key_indicators(self) -> pd.DataFrame:
        """Scrape all key economic indicators from the ABS webpage"""
        self.logger.info("🇦🇺 Starting ABS Key Economic Indicators scraping...")
        
        try:
            # Fetch the webpage
            response = self.session.get(self.target_url, timeout=30)
            response.raise_for_status()
            
            self.logger.info(f"✅ Successfully fetched ABS webpage (status: {response.status_code})")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all data tables
            all_data = []
            categories = [
                "National accounts",
                "International accounts", 
                "Consumption and investment",
                "Production",
                "Prices",
                "Labour force and demography",
                "Incomes",
                "Lending indicators"
            ]
            
            for category in categories:
                self.logger.info(f"📊 Scraping category: {category}")
                
                # Find the category heading and its associated table
                category_data = self._scrape_category_table(soup, category)
                if category_data:
                    all_data.extend(category_data)
                    self.logger.info(f"✅ Found {len(category_data)} indicators in {category}")
                else:
                    self.logger.warning(f"⚠️ No data found for category: {category}")
            
            if not all_data:
                self.logger.error("❌ No data scraped from any category")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(all_data)
            
            # Add metadata
            df['scrape_date'] = datetime.now().isoformat()
            df['source'] = 'ABS'
            df['source_url'] = self.target_url
            
            self.logger.info(f"🎯 Total indicators scraped: {len(df)}")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error scraping ABS data: {e}")
            return pd.DataFrame()
    
    def _scrape_category_table(self, soup: BeautifulSoup, category: str) -> List[Dict[str, Any]]:
        """Scrape data from a specific category table"""
        try:
            # Find the category heading
            heading = soup.find(lambda tag: tag.name in ['h3', 'h4', 'strong'] and 
                              category.lower() in tag.get_text().lower())
            
            if not heading:
                # Alternative: look for the category in table text
                tables = soup.find_all('table')
                for table in tables:
                    if category.lower() in table.get_text().lower():
                        return self._parse_table(table, category)
                return []
            
            # Find the next table after the heading
            table = heading.find_next('table')
            if not table:
                return []
            
            return self._parse_table(table, category)
            
        except Exception as e:
            self.logger.warning(f"Error scraping {category}: {e}")
            return []
    
    def _parse_table(self, table, category: str) -> List[Dict[str, Any]]:
        """Parse a data table into structured records"""
        try:
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need header + at least one data row
                return []
            
            # Get headers
            header_row = rows[0]
            headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
            
            data = []
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) < 5:  # Need at least indicator, period, unit, value, change
                    continue
                
                # Extract cell values
                cell_values = []
                for cell in cells:
                    # Get the link if it exists, otherwise get text
                    link = cell.find('a')
                    if link:
                        cell_values.append({
                            'text': cell.get_text().strip(),
                            'link': link.get('href', '')
                        })
                    else:
                        cell_values.append({'text': cell.get_text().strip(), 'link': ''})
                
                if len(cell_values) >= 5:
                    # Normalize period text for consistency
                    normalized_period = self._normalize_period_text(cell_values[1]['text'])
                    
                    indicator_text = cell_values[0]['text']
                    dataset_id = self._generate_dataset_id(indicator_text, category)
                    
                    record = {
                        'category': category,
                        'indicator': indicator_text,
                        'indicator_link': cell_values[0]['link'],
                        'period': normalized_period,
                        'unit': cell_values[2]['text'],
                        'value': self._parse_numeric_value(cell_values[3]['text']),
                        'value_raw': cell_values[3]['text'],
                        'change_previous_period': cell_values[4]['text'] if len(cell_values) > 4 else '',
                        'change_year_on_year': cell_values[5]['text'] if len(cell_values) > 5 else '',
                        'datetime': self._parse_period_to_datetime(normalized_period),
                        'frequency': self._detect_frequency(normalized_period),
                        'dataset_id': dataset_id
                    }
                    data.append(record)
            
            return data
            
        except Exception as e:
            self.logger.warning(f"Error parsing table for {category}: {e}")
            return []
    
    def _normalize_period_text(self, period_text: str) -> str:
        """Normalize period text for consistency"""
        if not period_text:
            return period_text
        
        # Normalize quarter case variations
        normalized = re.sub(r'\s+qtr\s+', ' Qtr ', period_text, flags=re.IGNORECASE)
        
        return normalized.strip()
    
    def _detect_frequency(self, period_text: str) -> str:
        """Detect data frequency from period text"""
        if not period_text:
            return 'unknown'
        
        period_lower = period_text.lower()
        
        # Quarterly indicators
        if any(keyword in period_lower for keyword in ['qtr', 'quarter']):
            return 'quarterly'
        
        # Monthly indicators  
        month_keywords = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                         'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'june']
        if any(keyword in period_lower for keyword in month_keywords):
            return 'monthly'
        
        # Annual indicators
        if re.match(r'^\d{4}$', period_text.strip()):
            return 'annual'
        
        return 'unknown'
    
    def _generate_dataset_id(self, indicator_text: str, category: str) -> str:
        """Generate a unique dataset ID from indicator name and category"""
        if not indicator_text:
            return 'unknown'
        
        # Clean and normalize the indicator text
        cleaned = re.sub(r'[^\w\s]', '', indicator_text.lower())
        
        # Extract key terms and abbreviate
        key_terms = []
        
        # Map common economic terms to abbreviations
        term_map = {
            'gross domestic product': 'gdp',
            'consumer price index': 'cpi', 
            'unemployment rate': 'unemploy_rate',
            'employed persons': 'employed',
            'participation rate': 'particip_rate',
            'retail turnover': 'retail',
            'building approvals': 'building_app',
            'wage price index': 'wpi',
            'dwelling': 'dwelling',
            'loan commitments': 'loans',
            'balance on goods': 'trade_balance',
            'current account': 'current_acc'
        }
        
        # Look for mapped terms first
        for term, abbrev in term_map.items():
            if term in cleaned:
                key_terms.append(abbrev)
                break
        
        # If no mapped terms, extract first few words
        if not key_terms:
            words = cleaned.split()[:3]  # Take first 3 words
            key_terms = [word[:4] for word in words if len(word) > 2]
        
        # Add category prefix
        category_abbrev = category.lower().replace(' ', '_')[:4]
        
        # Combine to create ID
        dataset_id = f"abs_{category_abbrev}_{'_'.join(key_terms)}"
        
        # Ensure reasonable length
        if len(dataset_id) > 50:
            dataset_id = dataset_id[:50]
        
        return dataset_id
    
    def _parse_numeric_value(self, value_text: str) -> Optional[float]:
        """Parse numeric values from text, handling various formats"""
        try:
            # Remove common non-numeric characters
            cleaned = re.sub(r'[,$%\s]', '', value_text)
            
            # Handle negative values
            if cleaned.startswith('-') or cleaned.startswith('−'):
                cleaned = '-' + cleaned.lstrip('-−')
            
            # Try to convert to float
            if cleaned and cleaned not in ['na', 'NP', '..', 'n/a']:
                return float(cleaned.replace(',', ''))
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _parse_period_to_datetime(self, period_text: str) -> Optional[str]:
        """Parse period text into ISO datetime string"""
        try:
            period_text = period_text.strip()
            
            # Normalize quarter case variations first
            period_text = re.sub(r'\s+qtr\s+', ' Qtr ', period_text, flags=re.IGNORECASE)
            
            # Handle quarterly periods (e.g., "Mar Qtr 2025")
            quarter_match = re.match(r'(\w{3})\s+(?:Qtr|Quarter)\s+(\d{4})', period_text, re.IGNORECASE)
            if quarter_match:
                month_abbr, year = quarter_match.groups()
                month_map = {'Mar': '03', 'Jun': '06', 'Sep': '09', 'Dec': '12'}
                month = month_map.get(month_abbr, '01')
                return f"{year}-{month}-01T00:00:00"
            
            # Handle monthly periods (e.g., "May 2025", "June 2025")
            month_match = re.match(r'(\w{3,4})\s+(\d{4})', period_text)
            if month_match:
                month_abbr, year = month_match.groups()
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'June': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                month = month_map.get(month_abbr, '01')
                return f"{year}-{month}-01T00:00:00"
            
            # Handle year-only periods
            year_match = re.match(r'(\d{4})', period_text)
            if year_match:
                year = year_match.group(1)
                return f"{year}-01-01T00:00:00"
            
            return None
            
        except Exception:
            return None
    
    def save_data(self, df: pd.DataFrame) -> bool:
        """Save scraped data with historical tracking"""
        try:
            if df.empty:
                self.logger.warning("No data to save")
                return False
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"abs_key_indicators_{timestamp}.parquet"
            filepath = self.output_dir / filename
            
            # Save current collection
            df.to_parquet(filepath, index=False)
            
            # Update historical tracking
            self._update_historical_data(df)
            
            # Save latest version
            latest_filepath = self.output_dir / "abs_key_indicators_latest.parquet"
            df.to_parquet(latest_filepath, index=False)
            
            self.logger.info(f"💾 Saved {len(df)} indicators to {filename}")
            self.logger.info(f"📁 Output directory: {self.output_dir}")
            
            # Print summary
            self._print_summary(df)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error saving data: {e}")
            return False
    
    def _update_historical_data(self, current_df: pd.DataFrame):
        """Update historical time series data"""
        try:
            historical_file = self.output_dir / "abs_historical_timeseries.parquet"
            
            # Load existing historical data if available
            if historical_file.exists():
                historical_df = pd.read_parquet(historical_file)
            else:
                historical_df = pd.DataFrame()
            
            # Prepare current data for historical tracking
            current_historical = current_df[[
                'dataset_id', 'category', 'indicator', 'period', 
                'value', 'unit', 'datetime', 'frequency', 'scrape_date'
            ]].copy()
            
            # Add collection timestamp
            collection_timestamp = datetime.now().isoformat()
            current_historical['collection_date'] = collection_timestamp
            
            # Append to historical data
            if not historical_df.empty:
                # Remove duplicates (same dataset_id + period + collection date)
                dataset_ids_list = current_historical['dataset_id'].tolist()
                periods_list = current_historical['period'].tolist()
                historical_df = historical_df[
                    ~((historical_df['dataset_id'].isin(dataset_ids_list)) & 
                      (historical_df['period'].isin(periods_list)) &
                      (historical_df['collection_date'] == collection_timestamp))
                ]
                combined_df = pd.concat([historical_df, current_historical], ignore_index=True)
            else:
                combined_df = current_historical
            
            # Sort by dataset_id, period, and collection_date
            if len(combined_df) > 0 and isinstance(combined_df, pd.DataFrame):
                combined_df = combined_df.sort_values(by=['dataset_id', 'period', 'collection_date'])
            
            # Save updated historical data
            combined_df.to_parquet(historical_file, index=False)
            
            self.logger.info(f"📈 Updated historical data: {len(combined_df)} total records")
            
            # Create indicator-specific time series files
            if isinstance(combined_df, pd.DataFrame):
                self._create_indicator_timeseries(combined_df)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error updating historical data: {e}")
    
    def _create_indicator_timeseries(self, historical_df: pd.DataFrame):
        """Create individual time series files for major indicators"""
        try:
            timeseries_dir = self.output_dir / 'timeseries'
            timeseries_dir.mkdir(exist_ok=True)
            
            # Key indicators to track individually
            key_indicators = ['gdp', 'cpi', 'unemploy_rate', 'employed', 'retail']
            
            for key_indicator in key_indicators:
                # Find matching datasets
                matching_data = historical_df[
                    historical_df['dataset_id'].str.contains(key_indicator, case=False, na=False)
                ]
                
                if not matching_data.empty:
                    # Sort by datetime
                    matching_data = matching_data.sort_values(by='datetime')
                    
                    # Save individual time series
                    ts_file = timeseries_dir / f"{key_indicator}_timeseries.parquet"
                    matching_data.to_parquet(ts_file, index=False)
                    
                    self.logger.debug(f"📊 Created time series for {key_indicator}: {len(matching_data)} records")
        
        except Exception as e:
            self.logger.warning(f"⚠️ Error creating indicator time series: {e}")
    
    def _print_summary(self, df: pd.DataFrame):
        """Print summary of scraped data"""
        print(f"\n🇦🇺 ABS KEY ECONOMIC INDICATORS SUMMARY")
        print(f"{'='*50}")
        print(f"📊 Total indicators: {len(df)}")
        print(f"📅 Scrape date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Source: {self.target_url}")
        
        if not df.empty:
            print(f"\n📋 Categories:")
            category_counts = df['category'].value_counts()
            for category, count in category_counts.items():
                print(f"  • {category}: {count} indicators")
            
            print(f"\n📈 Recent data sample:")
            sample_df = df[['category', 'indicator', 'period', 'value', 'unit']].head(5)
            for _, row in sample_df.iterrows():
                print(f"  • {row['indicator'][:50]}{'...' if len(row['indicator']) > 50 else ''}")
                print(f"    {row['period']} | {row['value']} {row['unit']}")
        
        print(f"{'='*50}\n")
    
    def run(self) -> bool:
        """Run the complete scraping process"""
        try:
            self.logger.info("🚀 Starting ABS Key Economic Indicators collection...")
            
            # Scrape data
            df = self.scrape_key_indicators()
            
            if df.empty:
                self.logger.error("❌ No data was scraped")
                return False
            
            # Validate data
            if not self._validate_data(df):
                self.logger.error("❌ Data validation failed")
                return False
            
            # Save data
            if not self.save_data(df):
                self.logger.error("❌ Failed to save data")
                return False
            
            self.logger.info("✅ ABS collection completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Collection failed: {e}")
            return False
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """Validate scraped data quality"""
        try:
            # Check if we have data
            if df.empty:
                return False
            
            # Check required columns
            required_cols = ['category', 'indicator', 'period', 'value']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                self.logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            # Check data quality
            valid_values = df['value'].notna().sum()
            total_rows = len(df)
            
            if valid_values < total_rows * 0.5:  # At least 50% should have valid values
                self.logger.warning(f"Low data quality: only {valid_values}/{total_rows} have valid values")
                return False
            
            self.logger.info(f"✅ Data validation passed: {valid_values}/{total_rows} valid values")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            return False

if __name__ == "__main__":
    collector = ABSDataScraper()
    success = collector.run()
    
    if not success:
        exit(1) 