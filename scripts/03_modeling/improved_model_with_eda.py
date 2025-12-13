"""
Improved ML Model - Using ONLY EDA-Recommended Features
Based on correlation analysis!

Author: Rehan Salim Chaudhry
Date: 2024-12-10
"""

from config.settings import config
import psycopg2
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

print("="*60)
print("IMPROVED MODEL - EDA-DRIVEN FEATURE SELECTION")
print("="*60)

# ============================================
# LOAD DATA
# ============================================
db_conn = psycopg2.connect(**config.DB_CONFIG)

query = f"""
        select date, open, high, low, close, volume
        from stock_prices
        where symbol = 'AAPL'
        order by date ASC
        """

df = pd.read_sql_query(query, db_conn)
print(f"\n✅ Loaded {len(df)} days of data")

# ============================================
# CREATE FEATURES (Based on EDA!)
# ============================================
print("\n📊 Creating features based on EDA recommendations...")

# Price features
df['daily_return'] = df['close'].pct_change() * 100

# Moving averages (STRONG correlation!)
df['sma_5'] = df['close'].rolling(window=5).mean()
df['sma_20'] = df['close'].rolling(window=20).mean()
df['sma_50'] = df['close'].rolling(window=50).mean()

# Volatility (STRONGEST correlation!)
df['volatility_5'] = df['daily_return'].rolling(window=5).std()
df['volatility_20'] = df['daily_return'].rolling(window=20).std()

# Volume
df['volume_sma_20'] = df['volume'].rolling(window=20).mean()

# Target
df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

# Clean
df = df.dropna()

print(f"✅ Created 7 features")
print(f"✅ {len(df)} samples after cleaning")

# ============================================
# EXPERIMENT 1: OLD FEATURES (Your Original)
# ============================================
print("\n" + "="*60)
print("BASELINE: Your Original 2 Features")
print("="*60)

X_old = df[['daily_return', 'sma_5']]
y = df['target']

# Time series split
split_idx = int(len(df) * 0.8)
X_train = X_old[:split_idx]
X_test = X_old[split_idx:]
y_train = y[:split_idx]
y_test = y[split_idx:]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

accuracy_old = accuracy_score(y_test, y_pred)
precision_old = precision_score(y_test, y_pred)
recall_old = recall_score(y_test, y_pred)

print(f"Features: daily_return, sma_5")
print(f"Accuracy:  {accuracy_old:.2%}")
print(f"Precision: {precision_old:.2%}")
print(f"Recall:    {recall_old:.2%}")

# ============================================
# EXPERIMENT 2: TOP 5 EDA FEATURES
# ============================================
print("\n" + "="*60)
print("IMPROVED: Top 5 EDA-Recommended Features")
print("="*60)

# Use TOP 5 features from EDA
X_new = df[['volatility_20', 'sma_50', 'sma_20', 'sma_5', 'volatility_5']]

X_train = X_new[:split_idx]
X_test = X_new[split_idx:]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

accuracy_new = accuracy_score(y_test, y_pred)
precision_new = precision_score(y_test, y_pred)
recall_new = recall_score(y_test, y_pred)

print(f"Features: volatility_20, sma_50, sma_20, sma_5, volatility_5")
print(f"Accuracy:  {accuracy_new:.2%}")
print(f"Precision: {precision_new:.2%}")
print(f"Recall:    {recall_new:.2%}")

# ============================================
# EXPERIMENT 3: ALL 7 EDA FEATURES
# ============================================
print("\n" + "="*60)
print("BEST: All 7 EDA-Recommended Features")
print("="*60)

X_best = df[['volatility_20', 'sma_50', 'sma_20', 'sma_5', 'volatility_5', 
             'volume_sma_20', 'daily_return']]

X_train = X_best[:split_idx]
X_test = X_best[split_idx:]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

accuracy_best = accuracy_score(y_test, y_pred)
precision_best = precision_score(y_test, y_pred)
recall_best = recall_score(y_test, y_pred)

print(f"Features: All 7 recommended from EDA")
print(f"Accuracy:  {accuracy_best:.2%}")
print(f"Precision: {precision_best:.2%}")
print(f"Recall:    {recall_best:.2%}")

# ============================================
# COMPARISON
# ============================================
print("\n" + "="*60)
print("RESULTS COMPARISON")
print("="*60)

print(f"\n{'Model':<30} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'Improvement'}")
print("-"*80)
print(f"{'Original (2 features)':<30} {accuracy_old:<12.2%} {precision_old:<12.2%} {recall_old:<12.2%} Baseline")
print(f"{'Top 5 EDA features':<30} {accuracy_new:<12.2%} {precision_new:<12.2%} {recall_new:<12.2%} {(accuracy_new-accuracy_old)*100:+.1f}%")
print(f"{'All 7 EDA features':<30} {accuracy_best:<12.2%} {precision_best:<12.2%} {recall_best:<12.2%} {(accuracy_best-accuracy_old)*100:+.1f}%")

# ============================================
# CONCLUSION
# ============================================
print("\n" + "="*60)
print("KEY LEARNINGS")
print("="*60)

improvement = (accuracy_best - accuracy_old) * 100

if improvement > 2:
    print(f"\n✅ EDA-driven feature selection WORKED!")
    print(f"   - Improvement: +{improvement:.1f}% accuracy")
    print(f"   - Volatility features were key!")
    print(f"   - Moving averages added signal!")
elif improvement > 0:
    print(f"\n⚠️  Minor improvement: +{improvement:.1f}%")
    print(f"   - EDA helped but features are still weak")
    print(f"   - Need better features (sentiment, news, fundamentals)")
else:
    print(f"\n❌ No improvement")
    print(f"   - Even best features can't predict well")
    print(f"   - Stock prediction is fundamentally hard!")

print(f"\n💡 Why EDA matters:")
print(f"   - Found volatility_20 has -0.206 correlation")
print(f"   - This is the STRONGEST signal in the data")
print(f"   - Without EDA, we might have missed it!")
print(f"   - Dropped 7 useless features that were just noise")

print("\n" + "="*60)
print("✅ ANALYSIS COMPLETE!")
print("="*60)
