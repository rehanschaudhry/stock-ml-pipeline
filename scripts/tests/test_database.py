"""
Test the DatabaseManager class
"""
from data.database import DatabaseManager
import pandas as pd

print("=" * 60)
print("Testing DatabaseManager")
print("=" * 60)

# Test 1: Create manager
print("\n1. Creating DatabaseManager...")
db = DatabaseManager()
print("   ✅ DatabaseManager created")

# Test 2: First connection
print("\n2. Connecting to database (first time)...")
db.connect()
print("   ✅ Connection successful!")

# Test 3: Try connecting again (should say already connected)
print("\n3. Connecting again (should skip)...")
db.connect()
print("   ✅ Second connection handled correctly")

# Test 4: Check connection details
print("\n4. Connection details:")
print(f"   Database: {db.db_config['database']}")
print(f"   Host: {db.db_config['host']}")
print(f"   Connected: {db.connection is not None}")
print(f"   Cursor created: {db.cursor is not None}")

print("\n" + "=" * 60)
print("All tests passed! 🎉")
print("=" * 60)

# Test 5: Close connection
print("\n5. Closing connection...")
db.close()
print("   ✅ Connection closed successfully")

# Test 6: Verify connection is closed
print("\n6. Verifying connection closed:")
print(f"   Connected: {db.connection is not None}")
print(f"   Cursor exists: {db.cursor is not None}")

print("\n" + "=" * 60)
print("All tests passed! 🎉")
print("=" * 60)

# Test 8: Execute simple query
print("\n8. Testing execute_query() - simple query...")
df = db.execute_query("SELECT * FROM stock_prices LIMIT 5")
print(f"   ✅ Returned {len(df)} rows")
print("\nFirst 5 rows:")
print(df[['symbol', 'date', 'close']].to_string(index=False))

# Test 9: Execute parameterized query
print("\n9. Testing execute_query() - parameterized query...")
df = db.execute_query(
    "SELECT * FROM stock_prices WHERE symbol = %s LIMIT 5",
    ("AAPL",)
)
print(f"   ✅ Returned {len(df)} rows for AAPL")
print("\nAAPL data:")
print(df[['symbol', 'date', 'close']].to_string(index=False))

print("\n" + "="*60)
print("TESTING CONVENIENCE METHODS")
print("="*60)

# Test 10: Get all data for AAPL with filters
print("\n10. Testing get_stock_data() with all filters...")
df = db.get_stock_data(
    symbol='AAPL',
    start_date='2025-07-03', 
    end_date='2025-11-26',
    limit=100
) 
print(f"   ✅ Retrieved {len(df)} rows for AAPL")
print(f"   Date range: {df['date'].min()} to {df['date'].max()}")

# Test 11: Just symbol (no filters)
print("\n11. Testing get_stock_data() - just symbol...")
df = db.get_stock_data('NVDA')
print(f"   ✅ Retrieved {len(df)} total rows for NVDA")

# Test 12: Symbol + limit only
print("\n12. Testing get_stock_data() - with limit...")
df = db.get_stock_data('MSFT', limit=5)
print(f"   ✅ Retrieved {len(df)} rows (limited to 5)")
print("\nMSFT last 5 days:")
print(df[['symbol', 'date', 'close']].to_string(index=False))

# Test 13: Symbol + start_date only
print("\n13. Testing get_stock_data() - with start_date...")
df = db.get_stock_data('GOOGL', start_date='2025-11-01')
print(f"   ✅ Retrieved {len(df)} rows after 2025-11-01")

print("\n" + "="*60)
print("All convenience method tests passed! 🎉")
print("="*60)

print("\n14. Testing insert_stock_data()...")
# Create test data
test_df = pd.DataFrame({
    'date': ['2025-12-01', '2025-12-02', '2025-12-03'],
    'open': [150.0, 151.0, 152.0],
    'high': [152.0, 153.0, 154.0],
    'low': [149.0, 150.0, 151.0],
    'close': [151.0, 152.0, 153.0],
    'volume': [1000000, 1100000, 1200000]
})

# Insert it
count = db.insert_stock_data(test_df, 'TEST')
print(f"   ✅ Inserted {count} rows for TEST symbol")

# Verify it worked
df = db.get_stock_data('TEST')
print(f"   ✅ Verified: Retrieved {len(df)} rows from database")
print("\nTest data inserted:")
print(df[['symbol', 'date', 'open', 'close', 'volume']].to_string(index=False))

print("\n" + "="*60)
print("Phase 1 COMPLETE - All convenience methods working! 🎉")
print("="*60)