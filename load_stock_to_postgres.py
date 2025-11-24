"""
Load Stock Data from Alpha Vantage to PostgreSQL
YOUR PASSWORD IS ALREADY SET!
"""

import requests
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# API Configuration
API_KEY = "KWKABB96U8N31TO4"

# Database Configuration - YOUR ACTUAL PASSWORD
DB_CONFIG = {
    "host": "localhost",
    "database": "stock_ml_db",
    "user": "postgres",
    "password": "mmhy68mm"
}

def fetch_stock_data(symbol, outputsize="compact"):
    """Fetch stock data from Alpha Vantage"""
    print(f"\n📈 Fetching {symbol} data from Alpha Vantage...")
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY,
        "outputsize": outputsize
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "Error Message" in data:
            print(f"  ❌ Error: {data['Error Message']}")
            return None
        
        if "Note" in data:
            print(f"  ⚠️  API Limit: {data['Note']}")
            return None
        
        if "Time Series (Daily)" not in data:
            print(f"  ❌ Unexpected response")
            return None
        
        # Convert to DataFrame
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df = df.sort_index()
        df['symbol'] = symbol
        
        print(f"  ✅ Retrieved {len(df)} days ({df.index[0].date()} to {df.index[-1].date()})")
        return df
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return None


def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


def insert_stock_data(df, symbol):
    """Insert stock data into PostgreSQL using UPSERT"""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Prepare data for insertion
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
        
        # UPSERT query
        insert_query = """
            INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
            VALUES %s
            ON CONFLICT (symbol, date) 
            DO UPDATE SET 
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                created_at = CURRENT_TIMESTAMP
        """
        
        execute_values(cur, insert_query, records)
        conn.commit()
        
        print(f"  ✅ Inserted {len(records)} records for {symbol}")
        
        # Show summary
        cur.execute("""
            SELECT 
                symbol,
                COUNT(*) as days,
                MIN(date) as first_date,
                MAX(date) as last_date
            FROM stock_prices 
            WHERE symbol = %s
            GROUP BY symbol
        """, (symbol,))
        
        result = cur.fetchone()
        if result:
            print(f"  📊 Now in DB: {result[1]} days ({result[2]} to {result[3]})")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


def get_database_summary():
    """Show what's in the database"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                symbol,
                COUNT(*) as days,
                MIN(date) as first_date,
                MAX(date) as last_date,
                ROUND(AVG(close::numeric), 2) as avg_close,
                ROUND(MIN(close::numeric), 2) as min_close,
                ROUND(MAX(close::numeric), 2) as max_close
            FROM stock_prices 
            GROUP BY symbol
            ORDER BY symbol
        """)
        
        results = cur.fetchall()
        
        print("\n" + "="*90)
        print(" " * 30 + "DATABASE SUMMARY")
        print("="*90)
        
        if not results:
            print("No data in database yet.")
        else:
            print(f"\n{'Symbol':<10} {'Days':<8} {'Date Range':<30} {'Avg Close':<12} {'Price Range':<20}")
            print("-"*90)
            
            for row in results:
                symbol, days, first, last, avg, min_p, max_p = row
                date_range = f"{first} to {last}"
                price_range = f"${min_p} - ${max_p}"
                print(f"{symbol:<10} {days:<8} {date_range:<30} ${avg:<11.2f} {price_range:<20}")
        
        # Total records
        cur.execute("SELECT COUNT(*) FROM stock_prices")
        total = cur.fetchone()[0]
        print("-"*90)
        print(f"Total records in database: {total:,}")
        print("="*90)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error getting summary: {e}")
        if conn:
            conn.close()


def load_multiple_stocks(symbols):
    """Load data for multiple stock symbols"""
    print("\n" + "="*90)
    print(" " * 25 + "STOCK DATA PIPELINE: API → POSTGRESQL")
    print("="*90)
    print(f"\nStocks to load: {', '.join(symbols)}")
    print(f"API: Alpha Vantage")
    print(f"Database: {DB_CONFIG['database']} on {DB_CONFIG['host']}")
    
    success_count = 0
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        
        # Fetch from API
        df = fetch_stock_data(symbol, outputsize="compact")
        
        if df is not None:
            # Insert to database
            if insert_stock_data(df, symbol):
                success_count += 1
            
            # Rate limiting: Alpha Vantage allows 25 calls/day on free tier
            # Add small delay between requests
            if i < len(symbols):
                print("  ⏱️  Waiting 15 seconds (API rate limit)...")
                import time
                time.sleep(15)
    
    print("\n" + "="*90)
    print(f" ✅ Successfully loaded {success_count}/{len(symbols)} stocks")
    print("="*90)
    
    # Show database summary
    get_database_summary()


# Main execution
if __name__ == "__main__":
    print("="*90)
    print(" " * 30 + "STOCK DATA LOADER")
    print("="*90)
    
    # List of stocks to track (start with just 3 to avoid API limits)
    stocks = ["NFLX", "AMZN", "NLFX", "GOOGL", "MSFT","TSLA", "AAPL", "META", "IBM", "INTC"]
    
    # Test database connection first
    print("\nTesting database connection...")
    conn = connect_db()
    if conn:
        print("✅ Database connection successful!")
        print(f"   Connected to: {DB_CONFIG['database']}")
        conn.close()
        
        # Load the data
        load_multiple_stocks(stocks)
        
        print("\n" + "="*90)
        print(" " * 35 + "NEXT STEPS")
        print("="*90)
        print("\n1. Open psql and run:")
        print("   SELECT * FROM stock_prices ORDER BY date DESC LIMIT 10;")
        print("\n2. Query specific stocks:")
        print("   SELECT symbol, date, close FROM stock_prices WHERE symbol = 'AAPL';")
        print("\n3. Tomorrow: Feature engineering and ML models!")
        print("\n" + "="*90)
        print(" " * 25 + "🚀 YOUR DATA PIPELINE IS LIVE! 🚀")
        print("="*90)
    else:
        print("\n❌ Could not connect to database.")
        print("Check your password and database settings.")