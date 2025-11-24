"""
Add More Tech Stocks to Database
Quick script to expand your dataset
"""

import requests
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import time

# Configuration
API_KEY = "KWKABB96U8N31TO4"
DB_CONFIG = {
    "host": "localhost",
    "database": "stock_ml_db",
    "user": "postgres",
    "password": "mmhy68mm"
}

def fetch_and_load_stock(symbol):
    """Fetch stock data and load to database"""
    print(f"\n{'='*60}")
    print(f"Processing: {symbol}")
    print('='*60)
    
    # Fetch from API
    print(f"📥 Fetching data from Alpha Vantage...")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY,
        "outputsize": "compact"  # Last 100 days
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # Check for errors
        if "Error Message" in data:
            print(f"❌ Invalid ticker: {symbol}")
            return False
        
        if "Note" in data:
            print(f"⚠️  API rate limit hit. Wait a moment...")
            return False
        
        if "Time Series (Daily)" not in data:
            print(f"❌ No data returned for {symbol}")
            return False
        
        # Convert to DataFrame
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        
        print(f"✅ Retrieved {len(df)} days of data")
        print(f"   Date range: {df.index.min().date()} to {df.index.max().date()}")
        
        # Load to database
        print(f"💾 Loading to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        records = []
        for date, row in df.iterrows():
            records.append((
                symbol,
                date.date(),
                float(row['open']),
                float(row['high']),
                float(row['low']),
                float(row['close']),
                int(row['volume'])
            ))
        
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
        
        execute_values(cur, insert_query, records)
        conn.commit()
        
        # Verify
        cur.execute("""
            SELECT COUNT(*), MIN(date), MAX(date) 
            FROM stock_prices 
            WHERE symbol = %s
        """, (symbol,))
        
        count, min_date, max_date = cur.fetchone()
        print(f"✅ Loaded {len(records)} records")
        print(f"   Total in DB: {count} records ({min_date} to {max_date})")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def show_summary():
    """Show database summary"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                symbol,
                COUNT(*) as records,
                MIN(date) as first_date,
                MAX(date) as last_date,
                ROUND(AVG(close::numeric), 2) as avg_price
            FROM stock_prices 
            GROUP BY symbol
            ORDER BY symbol
        """)
        
        results = cur.fetchall()
        
        print("\n" + "="*80)
        print(" "*30 + "DATABASE SUMMARY")
        print("="*80)
        print(f"\n{'Symbol':<10} {'Records':<10} {'Date Range':<35} {'Avg Price':<12}")
        print("-"*80)
        
        total_records = 0
        for symbol, count, first, last, avg in results:
            date_range = f"{first} to {last}"
            print(f"{symbol:<10} {count:<10} {date_range:<35} ${avg:<11.2f}")
            total_records += count
        
        print("-"*80)
        print(f"Total Symbols: {len(results)}")
        print(f"Total Records: {total_records:,}")
        print("="*80)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error getting summary: {e}")


# Main execution
if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*25 + "ADD MORE TECH STOCKS")
    print("="*80)
    
    # Stocks to add - EDIT THIS LIST!
    new_stocks = [
        "NFLX",   # Netflix (fix the typo)
        "ORCL",   # Oracle
        "ADBE",   # Adobe
        "CRM",    # Salesforce
        "AMD",    # AMD
        "AVGO",   # Broadcom
        "QCOM",   # Qualcomm
        "CSCO",   # Cisco
    ]
    
    print(f"\nStocks to add: {', '.join(new_stocks)}")
    print(f"Total: {len(new_stocks)} stocks")
    print(f"\n⚠️  Note: Free tier = 25 API calls/day. You have room for all of these!")
    
    input("\nPress Enter to start loading...")
    
    success = 0
    failed = []
    
    for i, symbol in enumerate(new_stocks, 1):
        print(f"\n[{i}/{len(new_stocks)}]")
        
        if fetch_and_load_stock(symbol):
            success += 1
        else:
            failed.append(symbol)
        
        # Rate limiting - wait between requests
        if i < len(new_stocks):
            print(f"\n⏱️  Waiting 15 seconds (API rate limit)...")
            time.sleep(15)
    
    # Final summary
    print("\n" + "="*80)
    print(" "*30 + "LOADING COMPLETE")
    print("="*80)
    print(f"\n✅ Successfully added: {success}/{len(new_stocks)} stocks")
    
    if failed:
        print(f"❌ Failed: {', '.join(failed)}")
    
    print("\n" + "="*80)
    
    # Show full database summary
    show_summary()
    
    print("\n" + "="*80)
    print("🎉 Your tech stock database is now EXPANDED!")
    print("="*80)
    print("\nNext steps:")
    print("1. Verify data: SELECT symbol, COUNT(*) FROM stock_prices GROUP BY symbol;")
    print("2. Commit to GitHub")
    print("3. Start feature engineering tomorrow!")
    print("\nGood night! 🌙")