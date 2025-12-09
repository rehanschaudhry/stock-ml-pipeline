"""
WORKING Yahoo Finance Loader - Fixed Insert!
This bypasses DatabaseManager bug and inserts directly

Author: Rehan Salim Chaudhry  
Date: 2024-12-09
"""

import yfinance as yf
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from config.settings import config

def load_stock_yahoo(symbol: str, conn):
    """Load a single stock from Yahoo Finance - WORKING VERSION"""
    
    print(f"\n{'='*60}")
    print(f"LOADING: {symbol}")
    print(f"{'='*60}")
    
    try:
        # Fetch from Yahoo Finance
        print(f"📥 Fetching data...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="max")
        
        if len(df) == 0:
            print(f"❌ No data returned")
            return 0
        
        # Prepare data
        df.reset_index(inplace=True)
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        print(f"✅ Fetched {len(df)} days ({df['date'].min()} to {df['date'].max()})")
        
        # Prepare records for insertion
        records = []
        for _, row in df.iterrows():
            records.append((
                symbol,
                row['date'],
                float(row['open']),
                float(row['high']),
                float(row['low']),
                float(row['close']),
                int(row['volume'])
            ))
        
        # INSERT with UPSERT
        print(f"💾 Inserting {len(records)} rows...")
        
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
            VALUES %s
            ON CONFLICT (symbol, date)
            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
        """
        
        execute_values(cursor, insert_query, records)
        conn.commit()
        cursor.close()
        
        print(f"✅ Successfully loaded {len(records)} days!")
        
        return len(records)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("YAHOO FINANCE LOADER - WORKING VERSION!")
    print("="*60)
    print("This version ACTUALLY inserts all the data!")
    print("="*60)
    
    # Connect to database
    print("\n🔌 Connecting to database...")
    try:
        conn = psycopg2.connect(**config.DB_CONFIG)
        print(f"✅ Connected to: {config.DB_CONFIG['database']}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        exit()
    
    # Get all symbols
    symbols = config.STOCKS
    
    print(f"\n📊 Loading {len(symbols)} stocks:")
    print(f"{', '.join(symbols)}")
    
    confirm = input(f"\nContinue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        conn.close()
        exit()
    
    # Load all stocks
    total_days = 0
    success_count = 0
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] {symbol}")
        days = load_stock_yahoo(symbol, conn)
        
        if days > 0:
            success_count += 1
            total_days += days
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}/{len(symbols)}")
    print(f"📊 Total days: {total_days:,}")
    print(f"📈 Average: {total_days // success_count if success_count > 0 else 0:,} days per stock")
    
    # Verify
    print(f"\n{'='*60}")
    print("DATABASE VERIFICATION")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    for symbol in symbols:
        cursor.execute("""
            SELECT COUNT(*), MIN(date), MAX(date)
            FROM stock_prices
            WHERE symbol = %s
        """, (symbol,))
        
        count, min_date, max_date = cursor.fetchone()
        
        if count > 0:
            years = (max_date - min_date).days / 365.25
            print(f"{symbol:<6} {count:>5} days ({years:>4.1f} years)  {min_date} to {max_date}")
        else:
            print(f"{symbol:<6} No data")
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}")
    print("✅ ALL DATA LOADED!")
    print(f"{'='*60}")
    print("\nNext step: python model_comparison.py")
    print("You should now see 5000-10000+ days per stock!")
    print(f"{'='*60}")
