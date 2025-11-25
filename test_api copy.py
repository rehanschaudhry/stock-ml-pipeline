"""
Alpha Vantage Stock Data Extraction
Step 1: Test API and Extract Data

Run this script first to verify everything works!
"""

import requests
import pandas as pd
from datetime import datetime
import json

# Your API key
API_KEY = "KWKABB96U8N31TO4"

def fetch_stock_data(symbol, outputsize="compact"):
    """
    Fetch daily stock data from Alpha Vantage
    
    Args:
        symbol: Stock ticker (e.g., 'AAPL', 'MSFT', 'TSLA')
        outputsize: 'compact' (100 days) or 'full' (20+ years)
    
    Returns:
        pandas DataFrame with stock data
    """
    print(f"Fetching data for {symbol}...")
    
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
        
        # Check for errors
        if "Error Message" in data:
            print(f"Error: {data['Error Message']}")
            return None
        
        if "Note" in data:
            print(f"API Limit: {data['Note']}")
            return None
        
        if "Time Series (Daily)" not in data:
            print(f"Unexpected response: {data}")
            return None
        
        # Convert to DataFrame
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient='index')
        
        # Rename columns (remove the "1. ", "2. " prefix)
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Convert to proper types
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        
        # Sort by date (oldest first)
        df = df.sort_index()
        
        # Add symbol column
        df['symbol'] = symbol
        
        print(f"✓ Successfully retrieved {len(df)} days of data")
        print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
        
        return df
        
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None


def calculate_technical_indicators(df):
    """
    Calculate common technical indicators
    (Feature engineering for ML models)
    """
    df = df.copy()
    
    # Simple Moving Averages
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # Daily returns
    df['daily_return'] = df['close'].pct_change()
    
    # Volatility (20-day rolling std of returns)
    df['volatility'] = df['daily_return'].rolling(window=20).std()
    
    # Price momentum (rate of change)
    df['momentum_5'] = df['close'].pct_change(periods=5)
    df['momentum_20'] = df['close'].pct_change(periods=20)
    
    # Volume changes
    df['volume_change'] = df['volume'].pct_change()
    
    # High-Low spread (as % of close)
    df['hl_spread'] = (df['high'] - df['low']) / df['close']
    
    return df


def display_summary(df, symbol):
    """Display summary statistics"""
    print(f"\n{'='*60}")
    print(f"Summary for {symbol}")
    print(f"{'='*60}")
    
    latest = df.iloc[-1]
    print(f"\nLatest Close Price: ${latest['close']:.2f}")
    print(f"Latest Date: {df.index[-1].date()}")
    
    print(f"\nPrice Statistics:")
    print(f"  52-week High: ${df['close'].max():.2f}")
    print(f"  52-week Low: ${df['close'].min():.2f}")
    print(f"  Average: ${df['close'].mean():.2f}")
    print(f"  Std Dev: ${df['close'].std():.2f}")
    
    if 'daily_return' in df.columns:
        print(f"\nReturns Statistics:")
        print(f"  Mean Daily Return: {df['daily_return'].mean()*100:.2f}%")
        print(f"  Volatility: {df['daily_return'].std()*100:.2f}%")
    
    print(f"\nVolume Statistics:")
    print(f"  Average Daily Volume: {df['volume'].mean():,.0f}")
    print(f"  Max Volume: {df['volume'].max():,.0f}")


# Main execution
if __name__ == "__main__":
    print("="*60)
    print("Alpha Vantage Stock Data Pipeline - Test Script")
    print("="*60)
    
    # Test with a single stock
    symbol = "MSFT"  # Apple Inc.
    
    # Fetch data (compact = last 100 days)
    df = fetch_stock_data(symbol, outputsize="compact")
    
    if df is not None:
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Display summary
        display_summary(df, symbol)
        
        # Show last 5 days
        print(f"\n{'='*60}")
        print(f"Last 5 Trading Days:")
        print(f"{'='*60}")
        print(df[['open', 'high', 'low', 'close', 'volume']].tail())
        
        # Save to CSV
        filename = f"{symbol}_stock_data_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename)
        print(f"\n✓ Data saved to: {filename}")
        
        print("\n" + "="*60)
        print("SUCCESS! Your API is working!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run this script to confirm it works")
        print("2. Modify the 'symbol' variable to try other stocks")
        print("3. Then we'll set up PostgreSQL database")
        print("4. Then automate data extraction")
    else:
        print("\n❌ Failed to fetch data. Check your API key or internet connection.")