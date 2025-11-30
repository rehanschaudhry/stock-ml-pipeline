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
            
