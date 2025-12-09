"""
Load Stock Data from Yahoo Finance (UNLIMITED FREE!)
Uses yfinance library - no API key needed!

Author: Rehan Salim Chaudhry
Date: 2024-12-09
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from config.settings import config
from data.database import DatabaseManager

def fetch_stock_data_yahoo(symbol: str, period: str = "max") -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance.
    
    Args:
        symbol: Stock ticker symbol
        period: Data period - "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    
    Returns:
        DataFrame with stock data
    """
    print(f"\n📥 Fetching data for {symbol} from Yahoo Finance...")
    print(f"   Period: {period}")
    
    try:
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Download historical data
        df = ticker.history(period=period)
        
        if len(df) == 0:
            print(f"   ❌ No data returned for {symbol}")
            return None
        
        # Reset index to make date a column
        df.reset_index(inplace=True)
        
        # Rename columns to match our database schema
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Keep only columns we need
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        
        # Convert date to date format (remove time)
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        print(f"   ✅ Fetched {len(df)} days of data!")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Calculate years
        date_range = df['date'].max() - df['date'].min()
        years = date_range.days / 365.25
        print(f"   📅 {years:.1f} years of history!")
        
        return df
        
    except Exception as e:
        print(f"   ❌ Error fetching {symbol}: {e}")
        return None


def load_single_stock(symbol: str, db: DatabaseManager, period: str = "max"):
    """
    Load a single stock's data into database.
    """
    print(f"\n{'='*60}")
    print(f"LOADING: {symbol}")
    print(f"{'='*60}")
    
    # Fetch data
    df = fetch_stock_data_yahoo(symbol, period)
    
    if df is None or len(df) == 0:
        print(f"   ❌ Failed to fetch {symbol}")
        return False
    
    # Insert into database
    print(f"\n💾 Inserting into database using UPSERT...")
    try:
        count = db.insert_stock_data(df, symbol)
        print(f"   ✅ Successfully loaded {count} days for {symbol}")
        return True
    except Exception as e:
        print(f"   ❌ Database insert failed: {e}")
        return False


def load_multiple_stocks(symbols: list, db: DatabaseManager, period: str = "max"):
    """
    Load multiple stocks (NO rate limiting needed with Yahoo!)
    """
    print(f"\n{'='*60}")
    print(f"LOADING {len(symbols)} STOCKS FROM YAHOO FINANCE")
    print(f"{'='*60}")
    print(f"⚡ NO rate limits! Loading as fast as possible!")
    print(f"📊 Period: {period}")
    
    success_count = 0
    fail_count = 0
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        
        success = load_single_stock(symbol, db, period)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
    
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
    
    # Calculate years
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    # Handle both datetime and date types
    if hasattr(min_date, 'date'):
        min_date = min_date.date()
        max_date = max_date.date()
    
    date_range = max_date - min_date
    years = date_range.days / 365.25
    
    print(f"\n   ✅ {len(df)} days of data")
    print(f"   📅 {years:.1f} years of history")
    print(f"   Date range: {min_date} to {max_date}")
    
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
    
    for symbol in config.STOCKS:
        try:
            df = db.get_stock_data(symbol)
            if len(df) > 0:
                min_date = df['date'].min()
                max_date = df['date'].max()
                
                # Handle both datetime and date types
                if hasattr(min_date, 'date'):
                    min_date = min_date.date()
                    max_date = max_date.date()
                
                date_range = max_date - min_date
                years = date_range.days / 365.25
                
                print(f"{symbol:<6} {len(df):>5} days ({years:>4.1f} years)  {min_date} to {max_date}")
        except:
            print(f"{symbol:<6} No data")
    
    print(f"{'='*60}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("YAHOO FINANCE DATA LOADER")
    print("✅ UNLIMITED FREE API - NO RATE LIMITS!")
    print("="*60)
    
    # Create database manager
    print("\n🔌 Connecting to database...")
    db = DatabaseManager()
    db.connect()
    print(f"✅ Connected to: {config.DB_CONFIG['database']}")
    
    # Menu
    print("\n" + "="*60)
    print("What would you like to load?")
    print("="*60)
    print("1. Load AAPL only (test - 30 sec)")
    print("2. Load all 17 stocks (~2-3 min) ⭐ RECOMMENDED")
    print("3. Load specific stocks (custom)")
    print("4. Show database summary")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        # Load AAPL only
        load_single_stock("AAPL", db, period="max")
        verify_data("AAPL", db)
        
        print("\n" + "="*60)
        print("✅ AAPL DATA LOADED FROM YAHOO FINANCE!")
        print("="*60)
        print("\nNext step: Run model_comparison.py")
        
    elif choice == "2":
        # Load all stocks
        symbols = config.STOCKS
        print(f"\nLoading {len(symbols)} stocks from config:")
        print(f"{', '.join(symbols)}")
        
        confirm = input(f"\nThis will take ~2-3 minutes. Continue? (y/n): ").strip().lower()
        
        if confirm == 'y':
            load_multiple_stocks(symbols, db, period="max")
            print("\n")
            show_database_summary(db)
            
            print("\n" + "="*60)
            print("✅ ALL DATA LOADED FROM YAHOO FINANCE!")
            print("="*60)
            print("\nNext step: Run model_comparison.py to see results!")
        else:
            print("Cancelled.")
        
    elif choice == "3":
        # Load specific stocks
        symbols_input = input("\nEnter stock symbols (comma-separated, e.g., AAPL,MSFT,NVDA): ").strip()
        symbols = [s.strip().upper() for s in symbols_input.split(",")]
        
        print(f"\nWill load: {', '.join(symbols)}")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm == 'y':
            load_multiple_stocks(symbols, db, period="max")
            
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
