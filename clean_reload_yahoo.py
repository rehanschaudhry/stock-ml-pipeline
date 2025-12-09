"""
CLEAN RELOAD - Delete old data and load fresh from Yahoo Finance

This script will:
1. Delete ALL existing stock data
2. Load fresh data from Yahoo Finance (unlimited!)

Author: Rehan Salim Chaudhry
Date: 2024-12-09
"""

import yfinance as yf
import pandas as pd
from config.settings import config
from data.database import DatabaseManager

print("="*60)
print("CLEAN RELOAD FROM YAHOO FINANCE")
print("="*60)
print("\n⚠️  WARNING: This will DELETE all existing stock data!")
print("   Then load fresh data from Yahoo Finance\n")

confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()

if confirm != "yes":
    print("\n❌ Cancelled. No data was deleted.")
    exit()

# Connect to database
db = DatabaseManager()
db.connect()

# Delete all existing data
print("\n🗑️  Deleting all existing stock data...")
try:
    db.execute_query("DELETE FROM stock_prices")
    print("✅ All old data deleted!")
except Exception as e:
    print(f"❌ Error deleting data: {e}")
    db.close()
    exit()

# Verify deletion
count_query = "SELECT COUNT(*) FROM stock_prices"
result = db.execute_query(count_query)
count = result.iloc[0, 0]
print(f"   Database now has {count} rows (should be 0)")

if count != 0:
    print("❌ Data not fully deleted! Exiting...")
    db.close()
    exit()

print("\n" + "="*60)
print("LOADING FRESH DATA FROM YAHOO FINANCE")
print("="*60)

# Load all stocks
symbols = config.STOCKS
success_count = 0
total_days = 0

for i, symbol in enumerate(symbols, 1):
    print(f"\n[{i}/{len(symbols)}] Loading {symbol}...")
    
    try:
        # Fetch from Yahoo Finance
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="max")
        
        if len(df) == 0:
            print(f"   ❌ No data for {symbol}")
            continue
        
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
        
        print(f"   Fetched: {len(df)} days ({df['date'].min()} to {df['date'].max()})")
        
        # Insert into database
        count = db.insert_stock_data(df, symbol)
        total_days += len(df)
        success_count += 1
        print(f"   ✅ Loaded {len(df)} days for {symbol}")
        
    except Exception as e:
        print(f"   ❌ Error loading {symbol}: {e}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"✅ Successfully loaded: {success_count}/{len(symbols)} stocks")
print(f"📊 Total days loaded: {total_days:,}")
print(f"📈 Average per stock: {total_days // success_count if success_count > 0 else 0:,} days")

# Verify in database
print("\n" + "="*60)
print("DATABASE VERIFICATION")
print("="*60)

for symbol in symbols:
    df = db.get_stock_data(symbol)
    if len(df) > 0:
        min_date = df['date'].min()
        max_date = df['date'].max()
        if hasattr(min_date, 'date'):
            min_date = min_date.date()
            max_date = max_date.date()
        years = (max_date - min_date).days / 365.25
        print(f"{symbol:<6} {len(df):>5} days ({years:>4.1f} years)  {min_date} to {max_date}")

db.close()

print("\n" + "="*60)
print("✅ CLEAN RELOAD COMPLETE!")
print("="*60)
print("\nNext step: python model_comparison.py")
print("You should now see 5000-10000+ days per stock!")
print("="*60)
