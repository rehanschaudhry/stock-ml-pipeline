"""
Reload Stock Data - Full Historical Data (20+ years)
Uses DatabaseManager and secure config

No hardcoded passwords!

Author: Rehan Salim Chaudhry
Date: 2024-11-28
"""

import requests
import time
import pandas as pd
from datetime import datetime
from config.settings import config
from data.database import DatabaseManager

def fetch_stock_data(symbol: str) -> pd.DataFrame:
    """
    Fetch stock data from Alpha Vantage API.
    Uses 'full' output size for 20+ years of data!
    """
    print(f"\n📥 Fetching FULL historical data for {symbol}...")
    
    # Build API URL using config (will use 'full' if you changed it!)
    url = config.get_api_url(symbol)
    
    print(f"   Output size: {config.API_OUTPUT_SIZE}")
    print(f"   API: Alpha Vantage")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if "Error Message" in data:
            print(f"   ❌ API Error: {data['Error Message']}")
            return None
        
        if "Note" in data:
            print(f"   ⚠️  API Limit: {data['Note']}")
            print(f"   (You've hit the 25 calls/day limit - try again tomorrow)")
            return None
        
        # Extract time series data
        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            print(f"   ❌ No time series data found")
            print(f"   Available keys: {list(data.keys())}")
            return None
        
        time_series = data[time_series_key]
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
        
        # Reset index to have date as column
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'date'}, inplace=True)
        
        print(f"   ✅ Fetched {len(df)} days of data!")
        print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        
        # Show how many years
        years = (df['date'].max() - df['date'].min()).days / 365.25
        print(f"   That's {years:.1f} years of history! 🎉")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return None


def load_single_stock(symbol: str, db: DatabaseManager):
    """
    Load a single stock's data into database.
    """
    print(f"\n{'='*60}")
    print(f"LOADING: {symbol}")
    print(f"{'='*60}")
    
    # Fetch data
    df = fetch_stock_data(symbol)
    
    if df is None or len(df) == 0:
        print(f"   ❌ Failed to fetch {symbol}")
        return False
    
    # Insert into database (using your DatabaseManager!)
    print(f"\n💾 Inserting into database using UPSERT...")
    try:
        count = db.insert_stock_data(df, symbol)
        print(f"   ✅ Successfully loaded {count} days for {symbol}")
        return True
    except Exception as e:
        print(f"   ❌ Database insert failed: {e}")
        return False


def load_multiple_stocks(symbols: list, db: DatabaseManager):
    """
    Load multiple stocks with rate limiting.
    """
    print(f"\n{'='*60}")
    print(f"LOADING {len(symbols)} STOCKS")
    print(f"{'='*60}")
    print(f"⚠️  Note: This will take ~{len(symbols) * 15 / 60:.0f} minutes")
    print(f"    (15 second delay between stocks for API rate limit)")
    
    success_count = 0
    fail_count = 0
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        
        success = load_single_stock(symbol, db)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # Rate limiting (except for last stock)
        if i < len(symbols):
            delay = config.API_RATE_LIMIT_DELAY
            print(f"\n⏳ Waiting {delay} seconds (API rate limit)...")
            time.sleep(delay)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"   ✅ Successful: {success_count}/{len(symbols)}")
    if fail_count > 0:
        print(f"   ❌ Failed: {fail_count}")
    print(f"   Total attempted: {len(symbols)}")


def verify_data(symbol: str, db: DatabaseManager):
    """
    Verify how much data we have for a symbol.
    """
    print(f"\n{'='*60}")
    print(f"VERIFICATION: {symbol}")
    print(f"{'='*60}")
    
    df = db.get_stock_data(symbol)
    
    if len(df) == 0:
        print(f"   ❌ No data found for {symbol}")
        return
    
    years = (df['date'].max() - df['date'].min()).days / 365.25
    
    print(f"\n   ✅ {len(df)} days of data")
    print(f"   📅 {years:.1f} years of history")
    print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    
    print(f"\n   First 3 days:")
    print(df[['date', 'open', 'close', 'volume']].head(3).to_string(index=False))
    
    print(f"\n   Last 3 days:")
    print(df[['date', 'open', 'close', 'volume']].tail(3).to_string(index=False))


def show_database_summary(db: DatabaseManager):
    """
    Show summary of all stocks in database.
    """
    print(f"\n{'='*60}")
    print(f"DATABASE SUMMARY")
    print(f"{'='*60}")
    
    # Get all stocks from config
    for symbol in config.STOCKS:
        try:
            df = db.get_stock_data(symbol)
            if len(df) > 0:
                years = (df['date'].max() - df['date'].min()).days / 365.25
                print(f"{symbol:<6} {len(df):>5} days ({years:>4.1f} years)  {df['date'].min().date()} to {df['date'].max().date()}")
        except:
            print(f"{symbol:<6} No data")
    
    print(f"{'='*60}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("STOCK DATA LOADER - FULL HISTORICAL DATA")
    print("="*60)
    print(f"Output size: {config.API_OUTPUT_SIZE}")
    
    if config.API_OUTPUT_SIZE == "full":
        print(f"✅ Expected: 5000+ days per stock (20+ years)")
    else:
        print(f"⚠️  WARNING: Using 'compact' mode (only 100 days)")
        print(f"   Change API_OUTPUT_SIZE to 'full' in config/settings.py")
        print(f"   for 20+ years of data!")
    
    print("="*60)
    
    # Create database manager
    print("\n🔌 Connecting to database...")
    db = DatabaseManager()
    db.connect()
    print(f"✅ Connected to: {config.DB_CONFIG['database']}")
    
    # Menu
    print("\n" + "="*60)
    print("What would you like to do?")
    print("="*60)
    print("1. Load AAPL only (quick - 1-2 min)")
    print("2. Load all 17 stocks (15-20 min)")
    print("3. Load specific stocks (custom)")
    print("4. Show database summary")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        # Load AAPL only
        load_single_stock("AAPL", db)
        verify_data("AAPL", db)
        
        print("\n" + "="*60)
        print("✅ AAPL DATA LOADED!")
        print("="*60)
        print("\nNext step: Run model_comparison.py to see improved results!")
        print("Command: python model_comparison.py")
        
    elif choice == "2":
        # Load all stocks from config
        symbols = config.STOCKS
        print(f"\nLoading {len(symbols)} stocks from config:")
        print(f"{', '.join(symbols)}")
        
        confirm = input(f"\nThis will take ~{len(symbols) * 15 / 60:.0f} minutes. Continue? (y/n): ").strip().lower()
        
        if confirm == 'y':
            load_multiple_stocks(symbols, db)
            print("\n")
            show_database_summary(db)
        else:
            print("Cancelled.")
        
    elif choice == "3":
        # Load specific stocks
        symbols_input = input("\nEnter stock symbols (comma-separated, e.g., AAPL,MSFT,NVDA): ").strip()
        symbols = [s.strip().upper() for s in symbols_input.split(",")]
        
        print(f"\nWill load: {', '.join(symbols)}")
        confirm = input(f"This will take ~{len(symbols) * 15 / 60:.0f} minutes. Continue? (y/n): ").strip().lower()
        
        if confirm == 'y':
            load_multiple_stocks(symbols, db)
            
            # Verify first one
            if symbols:
                verify_data(symbols[0], db)
        else:
            print("Cancelled.")
    
    elif choice == "4":
        # Show summary
        show_database_summary(db)
    
    elif choice == "5":
        print("Exiting...")
    
    else:
        print("Invalid choice!")
    
    # Close connection
    db.close()
    
    print("\n" + "="*60)
    print("✅ DONE!")
    print("="*60)
