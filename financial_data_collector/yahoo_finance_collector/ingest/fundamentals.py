import yaml
import os
from pathlib import Path
import yfinance as yf
import pandas as pd
import json
from jsonschema import validate, ValidationError
import numpy as np

def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'data_requirements.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_schema():
    schema_path = Path(__file__).parent.parent / 'schema' / 'fundamentals.json'
    with open(schema_path, 'r') as f:
        return json.load(f)

def ensure_data_dir():
    data_dir = Path(__file__).parent.parent.parent / 'financial_data' / 'fundamentals'
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
        print(f"\nFetching fundamentals for {ticker}...")
        
        # Get multiple sources of financial data
        try:
            # Annual financials (income statement)
            income_stmt = yf_ticker.financials.T if hasattr(yf_ticker, 'financials') and not yf_ticker.financials.empty else pd.DataFrame()
            
            # Balance sheet
            balance_sheet = yf_ticker.balance_sheet.T if hasattr(yf_ticker, 'balance_sheet') and not yf_ticker.balance_sheet.empty else pd.DataFrame()
            
            # Quarterly financials for more recent data
            quarterly_income = yf_ticker.quarterly_financials.T if hasattr(yf_ticker, 'quarterly_financials') and not yf_ticker.quarterly_financials.empty else pd.DataFrame()
            
        except Exception as e:
            print(f"Error fetching financial statements for {ticker}: {e}")
            income_stmt = pd.DataFrame()
            balance_sheet = pd.DataFrame()
            quarterly_income = pd.DataFrame()

        # Combine annual and quarterly data (prefer quarterly for recent periods)
        combined_data = []
        
        # Process annual data
        if not income_stmt.empty:
            annual_data = process_financial_data(income_stmt, balance_sheet, yf_ticker, 'annual')
            combined_data.append(annual_data)
        
        # Process quarterly data (last 8 quarters)
        if not quarterly_income.empty:
            quarterly_data = process_financial_data(quarterly_income.head(8), pd.DataFrame(), yf_ticker, 'quarterly')
            combined_data.append(quarterly_data)
        
        if not combined_data:
            print(f"No financial data available for {ticker}")
            return
            
        # Combine all data
        fin = pd.concat(combined_data, ignore_index=True)
        
        if fin.empty:
            print(f"No financial data for {ticker}")
            return
            
        # Remove duplicates and sort by date
        fin = fin.drop_duplicates(subset=['date'])
        fin['date'] = pd.to_datetime(fin['date'])
        fin = fin.sort_values('date', ascending=False)
        fin['date'] = fin['date'].dt.strftime('%Y-%m-%d')
        
        # Add ticker
        fin['ticker'] = ticker
        
        # Only keep requested fields if specified
        if fields:
            available_fields = list(set(fields) & set(fin.columns))
            fin = fin[available_fields + ['ticker', 'date']]
        
        # Validate each row
        fin = validate_fundamentals(fin, schema, ticker)
        
        if fin.empty:
            print(f"No valid rows for {ticker} after schema validation.")
            return
            
        filename = f"{ticker.replace('.', '_')}_fundamentals.parquet"
        fin.to_parquet(data_dir / filename, index=False)
        
        print(f"✅ Saved fundamentals for {ticker} to {filename} [{len(fin)} rows]")
        print(f"   📅 Date range: {fin['date'].min()} to {fin['date'].max()}")
        
    except Exception as e:
        print(f"❌ Error fetching fundamentals for {ticker}: {e}")

def process_financial_data(income_data, balance_data, yf_ticker, period_type):
    """Process financial data and extract key metrics"""
    results = []
    
    # Get current valuation metrics for latest available period
    try:
        info = yf_ticker.info
        current_eps = info.get('trailingEps')
        current_pe = info.get('trailingPE')
        current_book_value = info.get('bookValue')
        current_pb_ratio = info.get('priceToBook')
    except:
        current_eps = current_pe = current_book_value = current_pb_ratio = None
    
    for date_idx, row in income_data.iterrows():
        try:
            # Map common financial statement items
            revenue = None
            net_income = None
            total_assets = None
            total_debt = None
            debt_to_equity = None
            
            # Extract revenue (try multiple column names)
            for rev_col in ['Total Revenue', 'Revenue', 'Net Sales']:
                if rev_col in income_data.columns:
                    revenue = row.get(rev_col)
                    break
            
            # Extract net income
            for income_col in ['Net Income', 'Net Income Common Stockholders']:
                if income_col in income_data.columns:
                    net_income = row.get(income_col)
                    break
            
            # Extract balance sheet data if available
            if not balance_data.empty and date_idx in balance_data.index:
                balance_row = balance_data.loc[date_idx]
                
                for assets_col in ['Total Assets', 'Total Capitalization']:
                    if assets_col in balance_data.columns:
                        total_assets = balance_row.get(assets_col)
                        break
                
                for debt_col in ['Total Debt', 'Net Debt']:
                    if debt_col in balance_data.columns:
                        total_debt = balance_row.get(debt_col)
                        break
                        
                # Calculate debt-to-equity
                equity_cols = ['Total Equity Gross Minority Interest', 'Stockholders Equity']
                for eq_col in equity_cols:
                    if eq_col in balance_data.columns:
                        equity = balance_row.get(eq_col)
                        if total_debt is not None and equity is not None and equity != 0:
                            debt_to_equity = total_debt / equity
                        break
            
            # For historical periods, try to calculate historical EPS
            historical_eps = None
            if net_income is not None:
                try:
                    shares_outstanding = info.get('sharesOutstanding') if info else None
                    if shares_outstanding:
                        historical_eps = net_income / shares_outstanding
                except:
                    pass
            
            # Use current EPS if historical calculation failed
            if historical_eps is None:
                historical_eps = current_eps
            
            # For PE ratio, use current for now (historical PE calculation requires historical prices)
            pe_ratio = current_pe
            
            # Clean up None values and convert to proper types
            def clean_value(val):
                if val is None or pd.isna(val) or np.isinf(val):
                    return None
                return float(val)
            
            record = {
                'date': date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx),
                'revenue': clean_value(revenue),
                'net_income': clean_value(net_income),
                'eps': clean_value(historical_eps),
                'pe_ratio': clean_value(pe_ratio),
                'total_assets': clean_value(total_assets),
                'debt_to_equity': clean_value(debt_to_equity)
            }
            
            results.append(record)
            
        except Exception as e:
            print(f"Error processing {period_type} data for {date_idx}: {e}")
            continue
    
    return pd.DataFrame(results)

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
