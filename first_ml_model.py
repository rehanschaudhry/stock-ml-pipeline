"""
Your First ML Model - Stock Price Direction Prediction
Goal: Predict if tomorrow's price will go UP or DOWN

This uses the features you just created!
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import psycopg2

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "database": "stock_ml_db",
    "user": "postgres",
    "password": "mmhy68mm"
}

def connect_db():
    return psycopg2.connect(**DB_CONFIG)


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
    
    # Moving averages
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # Volatility
    df['volatility_20'] = df['daily_return'].rolling(window=20).std()
    
    # Price momentum
    df['momentum_5'] = df['close'].pct_change(periods=5) * 100
    
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


def train_model(df, symbol='AAPL'):
    """
    Train a Random Forest model to predict price direction
    """
    print(f"\n🤖 Training ML Model...")
    
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
    # SPLIT: Train/Test
    # ========================================================================
    # Use 80% for training, 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        shuffle=False  # Don't shuffle! Time series data
    )
    
    print(f"\n   Train size: {len(X_train)} days")
    print(f"   Test size: {len(X_test)} days")
    
    # ========================================================================
    # TRAIN MODEL
    # ========================================================================
    print(f"\n   Training Random Forest...")
    
    model = RandomForestClassifier(
        n_estimators=100,      # 100 decision trees
        max_depth=10,          # Max depth of each tree
        random_state=42        # For reproducibility
    )
    
    model.fit(X_train, y_train)
    
    print(f"   ✅ Model trained!")
    
    # ========================================================================
    # EVALUATE MODEL
    # ========================================================================
    print(f"\n📈 Model Performance:")
    print("="*60)
    
    # Predictions on test set
    y_pred = model.predict(X_test)
    
    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n   Accuracy: {accuracy:.2%}")
    print(f"   (Random guessing would be ~50%)")
    
    # Detailed metrics
    print(f"\n   Classification Report:")
    print("-"*60)
    report = classification_report(y_test, y_pred, target_names=['DOWN', 'UP'])
    print(report)
    
    # Confusion Matrix
    print(f"\n   Confusion Matrix:")
    print("-"*60)
    cm = confusion_matrix(y_test, y_pred)
    print(f"                Predicted")
    print(f"              DOWN    UP")
    print(f"   Actual DOWN  {cm[0,0]:3d}   {cm[0,1]:3d}")
    print(f"          UP    {cm[1,0]:3d}   {cm[1,1]:3d}")
    
    # Feature Importance
    print(f"\n   Feature Importance:")
    print("-"*60)
    importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in importance_df.iterrows():
        print(f"   {row['feature']:20s}: {row['importance']:.4f}")
    
    return model, X_test, y_test, y_pred


def predict_tomorrow(model, df, feature_columns):
    """
    Predict tomorrow's direction for the latest data
    """
    print(f"\n🔮 Prediction for Tomorrow:")
    print("="*60)
    
    # Get latest data point
    latest = df[feature_columns].iloc[-1:].values
    
    # Predict
    prediction = model.predict(latest)[0]
    probability = model.predict_proba(latest)[0]
    
    latest_close = df['close'].iloc[-1]
    
    print(f"\n   Current Close Price: ${latest_close:.2f}")
    print(f"\n   Prediction: {'📈 UP' if prediction == 1 else '📉 DOWN'}")
    print(f"   Confidence: {probability[prediction]:.1%}")
    print(f"\n   Probabilities:")
    print(f"      DOWN: {probability[0]:.1%}")
    print(f"      UP:   {probability[1]:.1%}")
    
    return prediction, probability


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("         STOCK PRICE PREDICTION - ML MODEL")
    print("="*60)
    
    symbol = 'AAPL'
    
    # Step 1: Prepare data
    df = prepare_data(symbol)
    
    # Step 2: Train model
    feature_columns = [
        'daily_return', 'sma_5', 'sma_20', 'sma_50',
        'volatility_20', 'momentum_5', 'volume_change', 'hl_spread'
    ]
    
    model, X_test, y_test, y_pred = train_model(df, symbol)
    
    # Step 3: Predict tomorrow
    predict_tomorrow(model, df, feature_columns)
    
    print("\n" + "="*60)
    print("✅ YOUR FIRST ML MODEL IS COMPLETE!")
    print("="*60)
    
    print("\n📝 What you just did:")
    print("   1. Created features from stock data")
    print("   2. Defined prediction target (UP/DOWN)")
    print("   3. Split data into train/test sets")
    print("   4. Trained Random Forest model")
    print("   5. Evaluated model performance")
    print("   6. Made predictions!")
    
    print("\n💡 Key Learnings:")
    print("   - ML models learn patterns from historical data")
    print("   - Feature engineering is crucial (you did this!)")
    print("   - Train/test split prevents overfitting")
    print("   - Accuracy shows how often model is correct")
    print("   - Feature importance shows what matters most")
    
    print("\n🎯 Next Steps:")
    print("   1. Try different stocks")
    print("   2. Add more features")
    print("   3. Try different models (XGBoost, Neural Networks)")
    print("   4. Save model and make daily predictions")
    
    print("\n" + "="*60)
    print("Great work! You're now doing REAL machine learning! 🚀")
    print("="*60)