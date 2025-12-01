"""
Database operations for stock data.

This module handles all PostgreSQL interactions using a DatabaseManager class.

Author: Rehan Salim Chaudhry
Date: 2024-11-27
"""
import psycopg2
import pandas as pd
from typing import Optional
import logging
from config.settings import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database connections and operations.
    
    This class handles:
    - Opening/closing database connections
    - Executing SQL queries
    - Inserting and retrieving stock data
    
    Example:
        >>> db = DatabaseManager()
        >>> db.connect()
        >>> data = db.get_stock_data("AAPL")
        >>> db.close()
    """
    
    def __init__(self):
        """
        Initialize the database manager.
        
        This runs when you create a DatabaseManager object.
        Example: db = DatabaseManager()  ← __init__ runs here!
        """
        self.db_config = config.DB_CONFIG # Load DB config from settings
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None
    
    def connect(self):
        """
        Establish a connection to the PostgreSQL database.
        
        Example:
            >>> db = DatabaseManager()
            >>> db.connect()  # Connects to the database
        """
        try:
            if self.connection is not None:
                logger.info("Database connection already established.")
                return self.connection
            else:
                self.connection = psycopg2.connect(**self.db_config)
                self.cursor = self.connection.cursor()
                logger.info("Database connection established.")
                return self.connection
        
        except psycopg2.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
        
    def close(self):
        """
        Close database connection and cursor safely.
    
        Example:
            >>> db = DatabaseManager()
            >>> db.connect()
            >>> db.close()  # Clean up resources
        """
        # Close cursor
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
    
        # Close connection
        if self.connection is not None:
            self.connection.close()
            self.connection = None
    
        logger.info("Database connection closed")
        print("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Execute a SELECT query and return results as DataFrame.
    
        Args:
            query (str): SQL query to execute
            params (tuple): Optional parameters for parameterized queries
        
        Returns:
            pd.DataFrame: Query results as DataFrame
        
        Example:
            >>> db = DatabaseManager()
            >>> 
            >>> # Simple query
            >>> df = db.execute_query("SELECT * FROM stock_prices LIMIT 5")
            >>> 
            >>> # Parameterized query (safer!)
            >>> df = db.execute_query(
            ...     "SELECT * FROM stock_prices WHERE symbol = %s", 
            ...     ("AAPL",)
            ... )
        """
    
        # Guard: Auto-connect if not connected
        if self.connection is None or self.cursor is None:
            logger.info("Not connected, connecting now...")
            self.connect()
    
        try:
            # Execute query (with or without parameters)
            if params:
                self.cursor.execute(query, params)  # Parameterized (safer)
            else:
                self.cursor.execute(query)  # Simple query
        
            # Fetch all results
            results = self.cursor.fetchall()
        
            # Get column names
            columns = [desc[0] for desc in self.cursor.description]
        
            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
        
            # Log success
            logger.info(f"Query executed successfully: {len(df)} rows returned")
            print(f"✅ Query returned {len(df)} rows")
        
            return df
        
        except psycopg2.Error as e:
            error_msg = f"Query execution failed: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise
            
    def get_stock_data(
        self, 
        symbol: str, 
        start_date: str = None, 
        end_date: str = None,
        limit: int = None
        ) -> pd.DataFrame:
        """
        Get stock price data for a specific symbol.
    
        Args:
            symbol (str): Stock ticker symbol
            start_date (str): Optional start date (YYYY-MM-DD)
            end_date (str): Optional end date (YYYY-MM-DD)
            limit (int): Optional row limit
        
        Returns:
            pd.DataFrame: Stock price data
        """
        query = "SELECT * FROM stock_prices WHERE symbol = %s"
        params = [symbol]
    
        if start_date:
            query += " AND date >= %s"  
            params.append(start_date)
        
        if end_date:
            query += " AND date <= %s"  
            params.append(end_date)
        
        query += " ORDER BY date DESC"  
    
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        return self.execute_query(query, tuple(params))
    
    def insert_stock_data(self, df: pd.DataFrame, symbol: str) -> int:
        """
        Insert stock data into database with UPSERT logic.
    
        If a record already exists (same symbol + date), it will be updated.
        If it doesn't exist, it will be inserted.
    
        Args:
            df (pd.DataFrame): DataFrame with columns: date, open, high, low, close, volume
            symbol (str): Stock ticker symbol
        
        Returns:
            int: Number of rows inserted/updated
        
        Example:
            >>> df = pd.DataFrame({
            ...     'date': ['2025-01-01'],
            ...     'open': [100], 'high': [102], 'low': [99],
            ...     'close': [101], 'volume': [1000000]
            ... })
            >>> db.insert_stock_data(df, 'AAPL')
            1
        """
        if self.connection is None or self.cursor is None:
            logger.info("Not connected, connecting now...")
            self.connect()
        
        insert_query = """
            INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, date)
            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
            """
        
        row = list(df.itertuples(index=False, name=None))
        
        records = []
        for index, row in df.iterrows():
            record = (
            symbol,
            row['date'],
            float(row['open']),
            float(row['high']),
            float(row['low']),
            float(row['close']),
            int(row['volume'])
            )
        records.append(record)

        try:
            inserted_count = 0
            for record in records:
                self.cursor.execute(insert_query, record)
                inserted_count += 1
            
            self.connection.commit()
            logger.info(f"{inserted_count} rows inserted/updated for {symbol}")
            print(f"✅ {inserted_count} rows inserted/updated for {symbol}")
            return inserted_count
        
        except psycopg2.Error as e:
            self.connection.rollback()
            error_msg = f"Insert failed: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise