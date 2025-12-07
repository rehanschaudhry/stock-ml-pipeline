"""
Configuration settings for stock ML pipeline.

This module centralizes all configuration to avoid hardcoding values
throughout the codebase. Uses environment variables for sensitive data.

Author: Rehan Salim Chaudhry
Date: 2024-11-26
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class for the stock ML pipeline application.
    
    This class stores all application settings including database credentials,
    API keys, and model parameters. It uses environment variables for
    sensitive information with fallback defaults for development.
    
    Attributes:
        DB_CONFIG: Database connection parameters
        API_KEY: Alpha Vantage API key
        API_BASE_URL: Base URL for Alpha Vantage API
        STOCKS: List of stock symbols to track
        TRAIN_TEST_SPLIT: Proportion of data for testing
        RANDOM_STATE: Random seed for reproducibility
        DATA_DIR: Directory for raw data files
        MODEL_DIR: Directory for saved models
        LOG_DIR: Directory for log files
    
    Example:
        >>> from config.settings import config
        >>> print(config.API_KEY)
        >>> print(config.STOCKS)
    """
    
    # =================================================================
    # DATABASE CONFIGURATION
    # =================================================================
    DB_CONFIG: Dict[str, str] = {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "stock_ml_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD")  # TODO: Move to env var in production!
    }
    
    # =================================================================
    # API CONFIGURATION
    # =================================================================
    API_KEY: str = os.getenv("ALPHA_VANTAGE_KEY")  # TODO: Move to env var!
    API_BASE_URL: str = "https://www.alphavantage.co/query"
    API_FUNCTION: str = "TIME_SERIES_DAILY"
    API_OUTPUT_SIZE: str = "full"  # 'compact' = 100 days, 'full' = 20+ years
    API_RATE_LIMIT_DELAY: int = 15  # Seconds between API calls
    
    # =================================================================
    # STOCK SYMBOLS TO TRACK
    # =================================================================
    STOCKS: List[str] = [
        # Semiconductors
        "NVDA",   # NVIDIA
        "AMD",    # AMD
        "INTC",   # Intel
        "AVGO",   # Broadcom
        "QCOM",   # Qualcomm
        
        # Cloud/Enterprise
        "MSFT",   # Microsoft
        "GOOGL",  # Google
        "AMZN",   # Amazon
        "ORCL",   # Oracle
        
        # Software/SaaS
        "ADBE",   # Adobe
        "CRM",    # Salesforce
        "IBM",    # IBM
        
        # Social/Streaming
        "META",   # Meta
        "NFLX",   # Netflix
        
        # Innovation
        "AAPL",   # Apple
        "TSLA",   # Tesla
        
        # Networking
        "CSCO",   # Cisco
    ]
    
    # =================================================================
    # MACHINE LEARNING CONFIGURATION
    # =================================================================
    TRAIN_TEST_SPLIT: float = 0.2  # 80% train, 20% test
    RANDOM_STATE: int = 42  # For reproducibility
    
    # Random Forest parameters
    RF_N_ESTIMATORS: int = 100  # Number of trees
    RF_MAX_DEPTH: int = 10  # Maximum tree depth
    
    # Feature engineering windows
    SMA_WINDOWS: List[int] = [5, 20, 50]  # Moving average windows
    VOLATILITY_WINDOW: int = 20  # Volatility calculation window
    MOMENTUM_WINDOW: int = 5  # Momentum calculation window
    
    # =================================================================
    # FILE PATHS
    # =================================================================
    DATA_DIR: str = "data/raw"
    MODEL_DIR: str = "models/saved"
    LOG_DIR: str = "logs"
    FEATURE_DIR: str = "data/features"
    
    # =================================================================
    # LOGGING CONFIGURATION
    # =================================================================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # =================================================================
    # VALIDATION
    # =================================================================
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise
            
        Raises:
            ValueError: If critical configuration is missing
        """
        # Check API key exists
        if not cls.API_KEY:
            raise ValueError("API_KEY is required")
        
        # Check database config
        required_db_keys = ["host", "database", "user", "password"]
        for key in required_db_keys:
            if key not in cls.DB_CONFIG or not cls.DB_CONFIG[key]:
                raise ValueError(f"Database configuration missing: {key}")
        
        # Check stocks list is not empty
        if not cls.STOCKS:
            raise ValueError("STOCKS list cannot be empty")
        
        return True
    
    @classmethod
    def get_api_url(cls, symbol: str, function: str = None, outputsize: str = None) -> str:
        """
        Generate complete API URL for a stock symbol.
        
        Args:
            symbol: Stock ticker symbol
            function: API function (default: TIME_SERIES_DAILY)
            outputsize: 'compact' or 'full' (default: from config)
            
        Returns:
            str: Complete API URL
            
        Example:
            >>> url = Config.get_api_url("AAPL")
            >>> print(url)
            https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=XXX
        """
        function = function or cls.API_FUNCTION
        outputsize = outputsize or cls.API_OUTPUT_SIZE
        
        return (
            f"{cls.API_BASE_URL}?"
            f"function={function}&"
            f"symbol={symbol}&"
            f"apikey={cls.API_KEY}&"
            f"outputsize={outputsize}"
        )
    
    @classmethod
    def display_config(cls) -> None:
        """Print configuration summary (without sensitive data)."""
        print("=" * 60)
        print("CONFIGURATION SUMMARY")
        print("=" * 60)
        print(f"Database: {cls.DB_CONFIG['host']}/{cls.DB_CONFIG['database']}")
        print(f"API Base URL: {cls.API_BASE_URL}")
        print(f"Stocks tracked: {len(cls.STOCKS)}")
        print(f"Train/Test split: {cls.TRAIN_TEST_SPLIT}")
        print(f"Random Forest trees: {cls.RF_N_ESTIMATORS}")
        print(f"Max tree depth: {cls.RF_MAX_DEPTH}")
        print(f"Data directory: {cls.DATA_DIR}")
        print(f"Model directory: {cls.MODEL_DIR}")
        print("=" * 60)


# =================================================================
# CREATE SINGLETON CONFIG INSTANCE
# =================================================================
config = Config()

# Validate on import
try:
    config.validate()
    print("✅ Configuration loaded and validated successfully!")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    raise


# =================================================================
# USAGE EXAMPLES (for testing)
# =================================================================
if __name__ == "__main__":
    # Display configuration
    config.display_config()
    
    # Test API URL generation
    print("\nExample API URLs:")
    print(f"AAPL: {config.get_api_url('AAPL')}")
    print(f"NVDA: {config.get_api_url('NVDA')}")
    
    # Show stocks
    print(f"\nTracking {len(config.STOCKS)} stocks:")
    for i, stock in enumerate(config.STOCKS, 1):
        print(f"  {i}. {stock}")