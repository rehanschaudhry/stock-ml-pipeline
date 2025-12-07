"""
Stock Price Prediction - Model Comparison
Random Forest vs XGBoost

Uses secure configuration from config/settings.py
No hardcoded passwords!

Author: Rehan Salim Chaudhry
Date: 2024-11-28
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
import psycopg2

# Import secure configuration
from config.settings import config

def connect_db():
    """
    Connect to database using secure config.
    Uses environment variables from .env file.
    """
    return psycopg2.connect(**config.DB_CONFIG)


def prepare_data(symbol='AAPL'):
    """
    Get data and create features for ML
    """
    print(f"📊 Preparing data for {symbol}...")
    
    conn = connect_db()
    
    # Get all data for the symbol
    query = f"""
        SELECT date, open, high, low, close, volume
        FROM stock_prices 
        WHERE symbol = '{symbol}'
        ORDER BY date
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"   Retrieved {len(df)} days of data")
    
    # ========================================================================
    # CREATE FEATURES (using what you learned!)
    # ========================================================================
    
    # Daily returns
    df['daily_return'] = df['close'].pct_change() * 100
    
    # Moving averages (using config windows!)
    df['sma_5'] = df['close'].rolling(window=config.SMA_WINDOWS[0]).mean()
    df['sma_20'] = df['close'].rolling(window=config.SMA_WINDOWS[1]).mean()
    df['sma_50'] = df['close'].rolling(window=config.SMA_WINDOWS[2]).mean()
    
    # Volatility (using config window!)
    df['volatility_20'] = df['daily_return'].rolling(window=config.VOLATILITY_WINDOW).std()
    
    # Price momentum (using config window!)
    df['momentum_5'] = df['close'].pct_change(periods=config.MOMENTUM_WINDOW) * 100
    
    # Volume change
    df['volume_change'] = df['volume'].pct_change() * 100
    
    # High-Low spread
    df['hl_spread'] = (df['high'] - df['low']) / df['close'] * 100
    
    # ========================================================================
    # CREATE TARGET: Will price go UP tomorrow?
    # ========================================================================
    
    # Shift close price to get "tomorrow's price"
    df['tomorrow_close'] = df['close'].shift(-1)
    
    # Target: 1 if price goes up, 0 if down
    df['target'] = (df['tomorrow_close'] > df['close']).astype(int)
    
    # Drop NaN values (from rolling calculations)
    df = df.dropna()
    
    print(f"   After feature engineering: {len(df)} days")
    print(f"   Features created: {len([col for col in df.columns if col not in ['date', 'target', 'tomorrow_close']])}")
    
    return df


def train_models(df, symbol='AAPL'):
    """
    Train BOTH Random Forest and XGBoost models to compare!
    Uses hyperparameters from config.
    """
    print(f"\n🤖 Training ML Models...")
    
    # ========================================================================
    # SELECT FEATURES for ML
    # ========================================================================
    feature_columns = [
        'daily_return',
        'sma_5', 'sma_20', 'sma_50',
        'volatility_20',
        'momentum_5',
        'volume_change',
        'hl_spread'
    ]
    
    X = df[feature_columns]
    y = df['target']
    
    print(f"   Features: {len(feature_columns)}")
    print(f"   Samples: {len(X)}")
    print(f"   Target distribution: UP={y.sum()}, DOWN={len(y)-y.sum()}")
    
    # ========================================================================
    # SPLIT: Train/Test (using config split ratio!)
    # ========================================================================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=config.TRAIN_TEST_SPLIT,  # From config!
        shuffle=False,  # Don't shuffle! Time series data
        random_state=config.RANDOM_STATE  # From config!
    )
    
    print(f"\n   Train size: {len(X_train)} days")
    print(f"   Test size: {len(X_test)} days")
    
    # ========================================================================
    # TRAIN MODEL 1: RANDOM FOREST (using config params!)
    # ========================================================================
    print(f"\n   Training Random Forest...")
    
    rf_model = RandomForestClassifier(
        n_estimators=config.RF_N_ESTIMATORS,  # From config!
        max_depth=config.RF_MAX_DEPTH,        # From config!
        random_state=config.RANDOM_STATE      # From config!
    )
    
    rf_model.fit(X_train, y_train)
    print(f"   ✅ Random Forest trained!")
    
    # ========================================================================
    # TRAIN MODEL 2: XGBOOST
    # ========================================================================
    print(f"\n   Training XGBoost...")
    
    xgb_model = XGBClassifier(
        n_estimators=config.RF_N_ESTIMATORS,  # Same as RF for fair comparison
        max_depth=config.RF_MAX_DEPTH,        # Same as RF
        random_state=config.RANDOM_STATE,     # From config!
        eval_metric='logloss'                 # Suppress warnings
    )
    
    xgb_model.fit(X_train, y_train)
    print(f"   ✅ XGBoost trained!")
    
    # ========================================================================
    # EVALUATE BOTH MODELS
    # ========================================================================
    print(f"\n📈 Model Performance Comparison:")
    print("="*60)
    
    # Random Forest predictions
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    
    # XGBoost predictions
    xgb_pred = xgb_model.predict(X_test)
    xgb_accuracy = accuracy_score(y_test, xgb_pred)
    
    # COMPARISON TABLE
    print(f"\n   ACCURACY COMPARISON:")
    print("-"*60)
    print(f"   Random Forest:  {rf_accuracy:.2%}")
    print(f"   XGBoost:        {xgb_accuracy:.2%}")
    print(f"   Difference:     {(xgb_accuracy - rf_accuracy):+.2%}")
    
    if xgb_accuracy > rf_accuracy:
        print(f"\n   🏆 WINNER: XGBoost (better by {(xgb_accuracy - rf_accuracy):.2%})")
    elif rf_accuracy > xgb_accuracy:
        print(f"\n   🏆 WINNER: Random Forest (better by {(rf_accuracy - xgb_accuracy):.2%})")
    else:
        print(f"\n   🤝 TIE: Both models have same accuracy!")
    
    print(f"\n   (Random guessing would be ~50%)")
    
    # ========================================================================
    # DETAILED METRICS FOR BEST MODEL
    # ========================================================================
    best_model_name = "XGBoost" if xgb_accuracy >= rf_accuracy else "Random Forest"
    best_model = xgb_model if xgb_accuracy >= rf_accuracy else rf_model
    best_pred = xgb_pred if xgb_accuracy >= rf_accuracy else rf_pred
    
    print(f"\n   Detailed Report for {best_model_name}:")
    print("-"*60)
    report = classification_report(y_test, best_pred, target_names=['DOWN', 'UP'])
    print(report)
    
    # Confusion Matrix
    print(f"\n   Confusion Matrix ({best_model_name}):")
    print("-"*60)
    cm = confusion_matrix(y_test, best_pred)
    print(f"                Predicted")
    print(f"              DOWN    UP")
    print(f"   Actual DOWN  {cm[0,0]:3d}   {cm[0,1]:3d}")
    print(f"          UP    {cm[1,0]:3d}   {cm[1,1]:3d}")
    
    # FEATURE IMPORTANCE COMPARISON
    print(f"\n   Feature Importance Comparison:")
    print("-"*60)
    
    # Random Forest importance
    rf_importance = pd.DataFrame({
        'feature': feature_columns,
        'rf_importance': rf_model.feature_importances_
    }).sort_values('rf_importance', ascending=False)
    
    # XGBoost importance
    xgb_importance = pd.DataFrame({
        'feature': feature_columns,
        'xgb_importance': xgb_model.feature_importances_
    }).sort_values('xgb_importance', ascending=False)
    
    # Merge for comparison
    importance_comparison = rf_importance.merge(
        xgb_importance, on='feature'
    ).sort_values('rf_importance', ascending=False)
    
    print(f"\n   {'Feature':<20} {'Random Forest':>15} {'XGBoost':>15}")
    print("-"*60)
    for idx, row in importance_comparison.iterrows():
        print(f"   {row['feature']:<20} {row['rf_importance']:>15.4f} {row['xgb_importance']:>15.4f}")
    
    return rf_model, xgb_model, best_model, X_test, y_test, feature_columns


def predict_tomorrow(rf_model, xgb_model, df, feature_columns):
    """
    Predict tomorrow's direction using BOTH models
    """
    print(f"\n🔮 Predictions for Tomorrow:")
    print("="*60)
    
    # Get latest data point
    latest = df[feature_columns].iloc[-1:].values
    latest_close = df['close'].iloc[-1]
    
    print(f"\n   Current Close Price: ${latest_close:.2f}")
    
    # Random Forest prediction
    rf_pred = rf_model.predict(latest)[0]
    rf_prob = rf_model.predict_proba(latest)[0]
    
    # XGBoost prediction
    xgb_pred = xgb_model.predict(latest)[0]
    xgb_prob = xgb_model.predict_proba(latest)[0]
    
    print(f"\n   RANDOM FOREST:")
    print(f"      Prediction: {'📈 UP' if rf_pred == 1 else '📉 DOWN'}")
    print(f"      Confidence: {rf_prob[rf_pred]:.1%}")
    print(f"      Probabilities: DOWN={rf_prob[0]:.1%}, UP={rf_prob[1]:.1%}")
    
    print(f"\n   XGBOOST:")
    print(f"      Prediction: {'📈 UP' if xgb_pred == 1 else '📉 DOWN'}")
    print(f"      Confidence: {xgb_prob[xgb_pred]:.1%}")
    print(f"      Probabilities: DOWN={xgb_prob[0]:.1%}, UP={xgb_prob[1]:.1%}")
    
    # Consensus
    if rf_pred == xgb_pred:
        print(f"\n   🤝 CONSENSUS: Both models predict {'📈 UP' if rf_pred == 1 else '📉 DOWN'}")
    else:
        print(f"\n   ⚠️  DISAGREEMENT: Models predict different directions")
        print(f"      (Use the model with higher accuracy from above)")
    
    return rf_pred, xgb_pred


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("    STOCK PRICE PREDICTION - MODEL COMPARISON")
    print("         Random Forest vs XGBoost")
    print("="*60)
    print(f"Using secure configuration from config/settings.py")
    print(f"Database: {config.DB_CONFIG['database']}")
    print(f"Random Forest: {config.RF_N_ESTIMATORS} trees, max_depth={config.RF_MAX_DEPTH}")
    print("="*60)
    
    symbol = 'AAPL'
    
    # Step 1: Prepare data
    df = prepare_data(symbol)
    
    # Step 2: Train BOTH models
    feature_columns = [
        'daily_return', 'sma_5', 'sma_20', 'sma_50',
        'volatility_20', 'momentum_5', 'volume_change', 'hl_spread'
    ]
    
    rf_model, xgb_model, best_model, X_test, y_test, feature_columns = train_models(df, symbol)
    
    # Step 3: Predict tomorrow with BOTH models
    predict_tomorrow(rf_model, xgb_model, df, feature_columns)
    
    print("\n" + "="*60)
    print("✅ MODEL COMPARISON COMPLETE!")
    print("="*60)
    
    print("\n🔍 What you just did:")
    print("   1. Used secure config (no hardcoded passwords!)")
    print("   2. Trained TWO different ML models")
    print("   3. Compared their performance")
    print("   4. Identified which model works better")
    print("   5. Saw feature importance from both models")
    print("   6. Got predictions from both models")
    
    print("\n💡 Key Learnings:")
    print("   - Configuration management keeps code clean")
    print("   - XGBoost is often better than Random Forest")
    print("   - Different models can have different strengths")
    print("   - Comparing models helps find the best approach")
    
    print("\n🎯 Next Steps:")
    print("   1. Try different hyperparameters")
    print("   2. Add more evaluation metrics (precision, recall)")
    print("   3. Test on other stocks")
    print("   4. Save the best model for production")
    
    print("\n" + "="*60)
    print("Great work! You're now comparing ML models! 🚀")
    print("="*60)
