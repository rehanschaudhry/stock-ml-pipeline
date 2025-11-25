"""
Feature Engineering Challenge
YOUR TASK: Fill in the missing parts marked with ???

Goal: Calculate technical indicators for stock analysis
Time: 20-30 minutes
"""

import pandas as pd
import psycopg2
from datetime import datetime

# Database connection (you know this part!)
DB_CONFIG = {
    "host": "localhost",
    "database": "stock_ml_db",
    "user": "postgres",
    "password": "mmhy68mm"
}

def connect_db():
    """Connect to database"""
    return psycopg2.connect(**DB_CONFIG)


# ============================================================================
# CHALLENGE 1: Calculate Daily Returns
# ============================================================================
def calculate_daily_returns(symbol='AAPL'):
    """
    Calculate daily percentage change in stock price
    
    Formula: (today_close - yesterday_close) / yesterday_close * 100
    
    YOUR TASK: Fill in the ??? parts below
    """
    conn = connect_db()
    
    # Query to get stock prices (this is done for you)
    query = f"""
        SELECT date, close 
        FROM stock_prices 
        WHERE symbol = '{symbol}'
        ORDER BY date
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # TODO: Calculate daily returns
    # Hint 1: Use .pct_change() method
    # Hint 2: Multiply by 100 to get percentage
    # YOUR CODE HERE:
    df['daily_return'] = df['close'].pct_change() * 100 # Fill this in!
    
    # Show results
    print(f"\n{'='*60}")
    print(f"Daily Returns for {symbol}")
    print('='*60)
    print(df.tail(10))
    
    return df


# ============================================================================
# CHALLENGE 2: Calculate Moving Averages
# ============================================================================
def calculate_moving_averages(symbol='AAPL'):
    """
    Calculate 5-day, 20-day, and 50-day moving averages
    
    Moving Average = Average of last N days
    
    YOUR TASK: Fill in the ??? parts
    """
    conn = connect_db()
    
    query = f"""
        SELECT date, close 
        FROM stock_prices 
        WHERE symbol = '{symbol}'
        ORDER BY date
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # TODO: Calculate moving averages
    # Hint: Use .rolling(window=N).mean()
    # YOUR CODE HERE:
    df['sma_5'] = df['close'].rolling(window=5).mean()   # 5-day moving average
    df['sma_20'] = df['close'].rolling(window=20).mean()  # 20-day moving average
    df['sma_50'] = df['close'].rolling(window=50).mean()  # 50-day moving average
    
    # Show results
    print(f"\n{'='*60}")
    print(f"Moving Averages for {symbol}")
    print('='*60)
    print(df[['date', 'close', 'sma_5', 'sma_20', 'sma_50']].tail(10))
    
    return df


# ============================================================================
# CHALLENGE 3: Calculate Volatility
# ============================================================================
def calculate_volatility(symbol='AAPL', window=20):
    """
    Calculate rolling volatility (standard deviation of returns)
    
    Volatility = How much the price fluctuates
    Higher volatility = More risky
    
    YOUR TASK: Complete this function
    """
    conn = connect_db()
    
    query = f"""
        SELECT date, close 
        FROM stock_prices 
        WHERE symbol = '{symbol}'
        ORDER BY date
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Step 1: Calculate daily returns (you did this in Challenge 1!)
    df['daily_return'] = df['close'].pct_change() * 100
    
    # Step 2: Calculate rolling standard deviation of returns
    # TODO: Fill in the ??? 
    # Hint: Use .rolling(window=window).std()
    # YOUR CODE HERE:
    df['volatility'] = df['daily_return'].rolling(window=window).std()  # Fill this in!
    
    print(f"\n{'='*60}")
    print(f"Volatility for {symbol} ({window}-day window)")
    print('='*60)
    print(df[['date', 'close', 'daily_return', 'volatility']].tail(10))
    
    return df


# ============================================================================
# BONUS CHALLENGE: Create Complete Feature Set
# ============================================================================
def create_feature_set(symbol='AAPL'):
    """
    BONUS: Combine all features into one dataset
    
    This is what you'd use for ML models!
    
    Try to complete this using what you learned above
    """
    conn = connect_db()
    
    query = f"""
        SELECT date, open, high, low, close, volume 
        FROM stock_prices 
        WHERE symbol = '{symbol}'
        ORDER BY date
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # TODO: Add all features
    # Use what you learned in Challenges 1-3
    
    # Daily returns
    df['daily_return'] = df['close'].pct_change() * 100
    
    # Moving averages
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    
    # Volatility
    df['volatility_20'] = df['daily_return'].rolling(window=20).std() 
    
    # BONUS: Try adding these on your own!
    # Hint: Google "pandas calculate X" if stuck
    
    # Price momentum (5-day change)
    # df['momentum_5'] = df['close'].pct_change(periods=5) * 100
    
    # High-Low spread
    # df['hl_spread'] = (df['high'] - df['low']) / df['close']
    
    print(f"\n{'='*60}")
    print(f"Complete Feature Set for {symbol}")
    print('='*60)
    print(df.tail())
    
    # Save to CSV for later use
    filename = f"{symbol}_features.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Saved to {filename}")
    
    return df


# ============================================================================
# TEST YOUR CODE
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("FEATURE ENGINEERING CHALLENGES")
    print("="*60)
    print("\nYour task: Fill in the ??? parts in each function")
    print("Then run this script to test!")
    
    try:
        # Challenge 1
        print("\n\n🎯 CHALLENGE 1: Daily Returns")
        print("-" * 60)
        df1 = calculate_daily_returns('AAPL')
        
        # Challenge 2
        print("\n\n🎯 CHALLENGE 2: Moving Averages")
        print("-" * 60)
        df2 = calculate_moving_averages('AAPL')
        
        # Challenge 3
        print("\n\n🎯 CHALLENGE 3: Volatility")
        print("-" * 60)
        df3 = calculate_volatility('AAPL', window=20)
        
        # Bonus
        print("\n\n🎯 BONUS: Complete Feature Set")
        print("-" * 60)
        df4 = create_feature_set('AAPL')
        
        print("\n" + "="*60)
        print("🎉 ALL CHALLENGES COMPLETE!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNeed help? That's okay!")
        print("Common issues:")
        print("1. Forgot to fill in ??? parts")
        print("2. Syntax error in pandas code")
        print("3. Database connection issue")


"""
HINTS FOR EACH CHALLENGE:

Challenge 1 (Daily Returns):
- df['daily_return'] = df['close'].pct_change() * 100

Challenge 2 (Moving Averages):
- df['sma_5'] = df['close'].rolling(window=5).mean()
- df['sma_20'] = df['close'].rolling(window=20).mean()
- df['sma_50'] = df['close'].rolling(window=50).mean()

Challenge 3 (Volatility):
- df['volatility'] = df['daily_return'].rolling(window=window).std()

BONUS (Complete Feature Set):
- Use combinations of the above!

NEXT STEPS AFTER YOU COMPLETE:
1. Run this script
2. Check the output
3. Compare with hints if stuck
4. We'll review together!
"""