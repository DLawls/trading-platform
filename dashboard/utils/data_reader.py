"""
Data Reader Utilities
Fetch real data from Module 1 collectors for dashboard display
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MacroDataReader:
    """Read macro economic data from Module 1 collectors"""
    
    def __init__(self):
        # Base paths to data files
        self.project_root = Path(__file__).parent.parent.parent
        self.fred_data_path = self.project_root / "financial_data_collector" / "financial_data" / "economic" / "fred"
        self.abs_data_path = self.project_root / "financial_data_collector" / "financial_data" / "economic" / "abs"
        self.alpaca_data_path = self.project_root / "financial_data_collector" / "financial_data"
        
    def get_fred_indicator(self, indicator_code: str) -> Tuple[Optional[float], Optional[str], Optional[str]]:
        """
        Get the latest value for a FRED indicator
        Returns: (value, units, last_updated)
        """
        try:
            file_path = self.fred_data_path / f"{indicator_code}.parquet"
            if not file_path.exists():
                logger.warning(f"FRED file not found: {file_path}")
                return None, None, None
                
            df = pd.read_parquet(file_path)
            if df.empty:
                return None, None, None
                
            # Get the latest row
            latest = df.iloc[-1]
            value = latest.get('value')
            units = latest.get('units', '')
            datetime_val = latest.get('datetime')
            
            # Format the date
            last_updated = "Unknown"
            if datetime_val:
                try:
                    if isinstance(datetime_val, str):
                        dt = pd.to_datetime(datetime_val)
                    else:
                        dt = datetime_val
                    last_updated = dt.strftime("%Y-%m-%d")
                except:
                    pass
                    
            return value, units, last_updated
            
        except Exception as e:
            logger.error(f"Error reading FRED indicator {indicator_code}: {e}")
            return None, None, None
    
    def get_abs_data(self) -> pd.DataFrame:
        """Get all ABS indicators data"""
        try:
            file_path = self.abs_data_path / "abs_key_indicators_latest.parquet"
            if not file_path.exists():
                logger.warning(f"ABS file not found: {file_path}")
                return pd.DataFrame()
                
            df = pd.read_parquet(file_path)
            return df
            
        except Exception as e:
            logger.error(f"Error reading ABS data: {e}")
            return pd.DataFrame()
    
    def get_abs_indicator(self, indicator_name: str) -> Tuple[Optional[float], Optional[str], Optional[str], Optional[str]]:
        """
        Get specific ABS indicator by name
        Returns: (value, units, change, last_updated)
        """
        try:
            df = self.get_abs_data()
            if df.empty:
                return None, None, None, None
                
            # Multiple search strategies for better matching
            row = None
            
            # Strategy 1: Exact match
            exact_mask = df['indicator'] == indicator_name
            if exact_mask.any():
                row = df[exact_mask].iloc[0]
            else:
                # Strategy 2: Case insensitive partial match
                partial_mask = df['indicator'].str.contains(indicator_name, case=False, na=False)
                if partial_mask.any():
                    row = df[partial_mask].iloc[0]
                else:
                    # Strategy 3: Key words search
                    keywords = indicator_name.lower().split()
                    for keyword in keywords:
                        if len(keyword) > 3:  # Only search meaningful words
                            keyword_mask = df['indicator'].str.contains(keyword, case=False, na=False)
                            if keyword_mask.any():
                                row = df[keyword_mask].iloc[0]
                                break
            
            if row is None:
                logger.warning(f"ABS indicator not found: {indicator_name}")
                return None, None, None, None
                
            value = row.get('value')
            units = row.get('unit', '')
            change = row.get('change_year_on_year', '')
            
            # Parse value if it's a string
            if isinstance(value, str):
                try:
                    # Remove any non-numeric characters except decimal points
                    import re
                    clean_value = re.sub(r'[^\d.-]', '', str(value))
                    value = float(clean_value) if clean_value else None
                except:
                    value = None
            
            # Format the date
            last_updated = "Unknown"
            datetime_val = row.get('datetime') or row.get('period')
            if datetime_val:
                try:
                    if isinstance(datetime_val, str):
                        dt = pd.to_datetime(datetime_val)
                    else:
                        dt = datetime_val
                    last_updated = dt.strftime("%Y-%m-%d")
                except:
                    pass
                    
            return value, units, change, last_updated
            
        except Exception as e:
            logger.error(f"Error reading ABS indicator {indicator_name}: {e}")
            return None, None, None, None
    
    def get_abs_indicator_by_index(self, index: int) -> Tuple[Optional[float], Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Get ABS indicator by index position
        Returns: (value, units, change, last_updated, name)
        """
        try:
            df = self.get_abs_data()
            if df.empty or index >= len(df):
                return None, None, None, None, None
                
            row = df.iloc[index]
            value = row.get('value')
            units = row.get('unit', '')
            change = row.get('change_year_on_year', '')
            name = row.get('indicator', '')
            
            # Parse value if it's a string
            if isinstance(value, str):
                try:
                    import re
                    clean_value = re.sub(r'[^\d.-]', '', str(value))
                    value = float(clean_value) if clean_value else None
                except:
                    value = None
            
            # Format the date
            last_updated = "Unknown"
            datetime_val = row.get('datetime') or row.get('period')
            if datetime_val:
                try:
                    if isinstance(datetime_val, str):
                        dt = pd.to_datetime(datetime_val)
                    else:
                        dt = datetime_val
                    last_updated = dt.strftime("%Y-%m-%d")
                except:
                    pass
                    
            return value, units, change, last_updated, name
            
        except Exception as e:
            logger.error(f"Error reading ABS indicator at index {index}: {e}")
            return None, None, None, None, None
    
    def get_alpaca_stock(self, symbol: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Get latest stock price from Alpaca data
        Returns: (price, change, last_updated)
        """
        try:
            # Look for OHLCV data files
            ohlcv_path = self.alpaca_data_path / "ohlcv"
            if not ohlcv_path.exists():
                return None, None, None
                
            # Find the stock file
            stock_files = list(ohlcv_path.glob(f"*{symbol}*.parquet"))
            if not stock_files:
                return None, None, None
                
            df = pd.read_parquet(stock_files[0])
            if df.empty:
                return None, None, None
                
            # Get latest price and calculate change
            latest = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else latest
            
            price = latest.get('close')
            prev_price = previous.get('close')
            change = price - prev_price if price and prev_price else None
            
            # Format date
            last_updated = "Unknown"
            datetime_val = latest.get('datetime') or latest.get('date')
            if datetime_val:
                try:
                    if isinstance(datetime_val, str):
                        dt = pd.to_datetime(datetime_val)
                    else:
                        dt = datetime_val
                    last_updated = dt.strftime("%Y-%m-%d")
                except:
                    pass
                    
            return price, change, last_updated
            
        except Exception as e:
            logger.error(f"Error reading Alpaca stock {symbol}: {e}")
            return None, None, None
    
    def get_crypto_price(self, symbol: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Get latest crypto price
        Returns: (price, change, last_updated)
        """
        try:
            # Look for crypto data - similar to stocks but in crypto folder
            crypto_path = self.alpaca_data_path / "crypto"
            if not crypto_path.exists():
                # Might be in ohlcv folder
                return self.get_alpaca_stock(symbol)
                
            # Find the crypto file
            crypto_files = list(crypto_path.glob(f"*{symbol}*.parquet"))
            if not crypto_files:
                return self.get_alpaca_stock(symbol)  # Fallback
                
            df = pd.read_parquet(crypto_files[0])
            if df.empty:
                return None, None, None
                
            # Get latest price and calculate change
            latest = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else latest
            
            price = latest.get('close')
            prev_price = previous.get('close')
            change = price - prev_price if price and prev_price else None
            
            # Format date
            last_updated = "Unknown"
            datetime_val = latest.get('datetime') or latest.get('date')
            if datetime_val:
                try:
                    if isinstance(datetime_val, str):
                        dt = pd.to_datetime(datetime_val)
                    else:
                        dt = datetime_val
                    last_updated = dt.strftime("%Y-%m-%d")
                except:
                    pass
                    
            return price, change, last_updated
            
        except Exception as e:
            logger.error(f"Error reading crypto {symbol}: {e}")
            return None, None, None
    
    def format_value(self, value: Optional[float], units: str = "") -> str:
        """Format a value for display with improved units and precision"""
        if value is None:
            return "No Data"
        
        units_clean = units.strip().lower()
        
        # Special cases for specific unit formats
        if units.strip() == '$m':
            # Value is already in millions, convert to appropriate scale
            if abs(value) >= 1e6:
                return f"${value/1e6:+.1f}T" if value < 0 else f"${value/1e6:.1f}T"
            elif abs(value) >= 1e3:
                return f"${value/1e3:+.1f}B" if value < 0 else f"${value/1e3:.1f}B"
            else:
                return f"${value:+.1f}M" if value < 0 else f"${value:.1f}M"
        elif units.strip() == '$b':
            # Value is already in billions
            if abs(value) >= 1e3:
                return f"${value/1e3:+.1f}T" if value < 0 else f"${value/1e3:.1f}T"
            else:
                return f"${value:+.1f}B" if value < 0 else f"${value:.1f}B"
        elif units.strip() == "'000":
            # Value is in thousands
            if value >= 1e6:
                return f"{value/1e6:.1f}M"
            elif value >= 1e3:
                return f"{value/1e3:.1f}M"
            else:
                return f"{value:,.0f}K"
        elif units.strip() == "Billions of Dollars":
            # Value is already in billions of dollars
            if abs(value) >= 1e3:
                return f"${value/1e3:+.1f}T" if value < 0 else f"${value/1e3:.1f}T"
            else:
                return f"${value:+.1f}B" if value < 0 else f"${value:.1f}B"
        
        # Handle different unit types with improved formatting
        if units_clean in ['percent', '%'] or 'percent' in units_clean:
            return f"{value:.1f}%"
            
        elif 'exchange' in units_clean or ('australian dollar' in units_clean and value < 10):
            # Handle exchange rates - show as decimal without currency symbol
            return f"{value:.4f}"
            
        elif 'exports' in units_clean or 'volume' in units_clean or 'index' in units_clean or (value > 1e11 and 'australian dollar' in units_clean):
            # Handle volume indices, export data, and very large dollar amounts (likely exports/trade)
            if value >= 1e12:
                return f"{value/1e12:.1f}T"
            elif value >= 1e9:
                return f"{value/1e9:.1f}B"
            elif value >= 1e6:
                return f"{value/1e6:.1f}M"
            elif value >= 100:
                return f"{value:.0f}"
            else:
                return f"{value:.1f}"
            
        elif 'persons' in units_clean or 'people' in units_clean or 'population' in units_clean or (units_clean == '' and value > 1e6):
            # Handle population/employment numbers - large raw numbers are likely people
            if value >= 1e6:
                return f"{value/1e6:.1f}M"
            elif value >= 1e3:
                return f"{value/1e3:.0f}K"
            else:
                return f"{value:,.0f}"
                
        elif 'thousands' in units_clean or (units_clean == '' and 1e3 <= value < 1e6):
            # Handle values in thousands
            if value >= 1e6:
                return f"{value/1e6:.1f}M"
            elif value >= 1e3:
                return f"{value/1e3:.1f}K"
            else:
                return f"{value:.0f}"
                
        elif ('dollar' in units_clean or '$' in units or 'aud' in units_clean or 'usd' in units_clean or 'u.s. dollars' in units_clean) and 'exchange' not in units_clean and 'rate' not in units_clean and 'export' not in units_clean and 'volume' not in units_clean:
            # Handle currency values - but check for very large values that might be in wrong scale
            abs_val = abs(value)
            if abs_val >= 1e15:  # Very large values, probably in wrong units
                formatted = f"${value/1e12:+.1f}T" if value < 0 else f"${value/1e12:.1f}T"
            elif abs_val >= 1e12:
                formatted = f"${value/1e12:+.1f}T" if value < 0 else f"${value/1e12:.1f}T"
            elif abs_val >= 1e9:
                formatted = f"${value/1e9:+.1f}B" if value < 0 else f"${value/1e9:.1f}B"
            elif abs_val >= 1e6:
                formatted = f"${value/1e6:+.1f}M" if value < 0 else f"${value/1e6:.1f}M"
            elif abs_val >= 1e3:
                formatted = f"${value/1e3:+.1f}K" if value < 0 else f"${value/1e3:.1f}K"
            else:
                formatted = f"${value:+.0f}" if value < 0 else f"${value:.0f}"
            return formatted
            
        elif 'million' in units_clean or 'millions' in units_clean:
            # Value is already in millions, convert to appropriate scale
            abs_val = abs(value)
            if abs_val >= 1e6:
                return f"${value/1e6:+.1f}T" if value < 0 else f"${value/1e6:.1f}T"
            elif abs_val >= 1e3:
                return f"${value/1e3:+.1f}B" if value < 0 else f"${value/1e3:.1f}B"
            else:
                return f"${value:+.1f}M" if value < 0 else f"${value:.1f}M"
                
        elif 'billion' in units_clean:
            # Already in billions
            if abs(value) >= 1e3:
                return f"${value/1e3:+.1f}T" if value < 0 else f"${value/1e3:.1f}T"
            else:
                return f"${value:+.1f}B" if value < 0 else f"${value:.1f}B"
                
        elif 'rate' in units_clean and 'percent' not in units_clean:
            # Interest rates, unemployment rates, etc.
            return f"{value:.1f}%"
            
        elif 'index' in units_clean:
            # Price indices, etc.
            return f"{value:.1f}"
            
        elif 'units' in units_clean or 'number' in units_clean:
            # Handle dwelling units, etc.
            if value >= 1e6:
                return f"{value/1e6:.1f}M"
            elif value >= 1e3:
                return f"{value/1e3:.0f}K"
            else:
                return f"{value:,.0f}"
        
        # Default formatting for unknown units
        else:
            if value >= 1e12:
                return f"{value/1e12:.1f}T"
            elif value >= 1e9:
                return f"{value/1e9:.1f}B"
            elif value >= 1e6:
                return f"{value/1e6:.1f}M"
            elif value >= 1e3:
                return f"{value/1e3:.0f}K"
            elif value >= 1:
                return f"{value:.1f}"
            else:
                return f"{value:.3f}"
    
    def format_change(self, change: Optional[float], units: str = "") -> str:
        """Format a change value for display"""
        if change is None:
            return ""
            
        sign = "+" if change >= 0 else ""
        if units.lower() in ['percent', '%']:
            return f"{sign}{change:.2f}%"
        else:
            return f"{sign}{change:.2f}"

# Global instance
data_reader = MacroDataReader() 