from config.settings import config
import psycopg2
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

db_conn = psycopg2.connect(**config.DB_CONFIG)

# ============================================
# FIX #1: Order by date ASC (oldest first)
# ============================================
query = f"""
        select date, open, high, low, close, volume
        from stock_prices
        where symbol = 'AAPL'
        order by date ASC
        """

df = pd.read_sql_query(query, db_conn)
print("First 5 rows (oldest dates):")
print(df.head())
print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")

# Create features
df['daily_returns'] = df['close'].pct_change()
df['sma_5'] = df['close'].rolling(window=5).mean()

# ============================================
# FIX #2: Correct target logic
# Target = 1 if tomorrow > today (UP)
#        = 0 if tomorrow < today (DOWN)
# ============================================
df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

# Clean data
df = df.dropna()

print(f"\nTotal samples: {len(df)}")
print(f"UP days: {df['target'].sum()} ({df['target'].sum()/len(df)*100:.1f}%)")
print(f"DOWN days: {(1-df['target']).sum()} ({(1-df['target']).sum()/len(df)*100:.1f}%)")

# Prepare features
X = df[['daily_returns', 'sma_5']]
y = df['target']

# ============================================
# EXPERIMENT 1: Random Split (shuffle=True)
# ============================================
print("\n" + "="*60)
print("EXPERIMENT 1: Random Split (shuffle=True)")
print("="*60)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.2%}")
print("Interpretation: Tests if patterns exist in the data")
print("Expected: 55-65% (patterns exist but weak)")

# ============================================
# EXPERIMENT 2: Time Series Split (shuffle=False)
# ============================================
print("\n" + "="*60)
print("EXPERIMENT 2: Time Series Split (shuffle=False)")
print("="*60)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

print(f"Train period: {df.iloc[:int(len(df)*0.8)]['date'].min()} to {df.iloc[:int(len(df)*0.8)]['date'].max()}")
print(f"Test period: {df.iloc[int(len(df)*0.8):]['date'].min()} to {df.iloc[int(len(df)*0.8):]['date'].max()}")

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nAccuracy: {accuracy:.2%}")
print("Interpretation: Tests if we can predict the FUTURE")
print("Expected: 48-52% (predicting future is hard!)")

# ============================================
# SUMMARY
# ============================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("✅ Random Split (shuffle=True):")
print("   - Tests: Can model find patterns?")
print("   - Good for: Understanding if signal exists")
print("")
print("✅ Time Series Split (shuffle=False):")
print("   - Tests: Can model predict future?")
print("   - Good for: Real-world trading simulation")
print("")
print("💡 Key Learning:")
print("   - How you split data dramatically affects results!")
print("   - Always use time series split for stock prediction")
print("="*60)