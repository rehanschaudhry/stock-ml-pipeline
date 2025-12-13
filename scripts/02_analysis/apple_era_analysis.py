"""
Apple Era Analysis - Does company evolution break our model?
Testing hypothesis: Different Apple eras behave differently!

Author: Rehan Salim Chaudhry
Date: 2024-12-10
"""

from config.settings import config
import psycopg2
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns

print("="*70)
print("APPLE ERA ANALYSIS")
print("Testing: Does Apple's evolution break our predictions?")
print("="*70)

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
df['date'] = pd.to_datetime(df['date'])

# Create features
df['daily_return'] = df['close'].pct_change() * 100
df['sma_20'] = df['close'].rolling(window=20).mean()
df['volatility_20'] = df['daily_return'].rolling(window=20).std()
df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
df = df.dropna()

print(f"\n✅ Total data: {len(df)} days ({df['date'].min().year}-{df['date'].max().year})")

# ============================================
# DEFINE APPLE ERAS
# ============================================
print("\n" + "="*70)
print("APPLE'S EVOLUTION")
print("="*70)

eras = {
    'Early Apple (1980-1984)': ('1980-01-01', '1984-12-31'),
    'Jobs Fired (1985-1996)': ('1985-01-01', '1996-12-31'),
    'Jobs Returns (1997-2000)': ('1997-01-01', '2000-12-31'),
    'iPod Era (2001-2006)': ('2001-01-01', '2006-12-31'),
    'iPhone Era (2007-2010)': ('2007-01-01', '2010-12-31'),
    'Jobs Death (2011-2015)': ('2011-01-01', '2015-12-31'),
    'Modern Apple (2016-2020)': ('2016-01-01', '2020-12-31'),
    'Post-Pandemic (2021-2025)': ('2021-01-01', '2025-12-31')
}

# Analyze each era
era_stats = []

for era_name, (start, end) in eras.items():
    era_df = df[(df['date'] >= start) & (df['date'] <= end)]
    
    if len(era_df) > 0:
        avg_return = era_df['daily_return'].mean()
        avg_volatility = era_df['volatility_20'].mean()
        pct_up = (era_df['target'] == 1).sum() / len(era_df) * 100
        
        era_stats.append({
            'Era': era_name,
            'Days': len(era_df),
            'Avg Return': avg_return,
            'Volatility': avg_volatility,
            'UP %': pct_up
        })
        
        print(f"\n{era_name}:")
        print(f"  Days: {len(era_df):,}")
        print(f"  Avg Daily Return: {avg_return:+.3f}%")
        print(f"  Avg Volatility: {avg_volatility:.3f}%")
        print(f"  UP Days: {pct_up:.1f}%")

# ============================================
# EXPERIMENT 1: Traditional Approach
# Train on OLD data (1980-2010), Test on NEW data (2010-2025)
# ============================================
print("\n" + "="*70)
print("EXPERIMENT 1: Traditional Approach")
print("Train on: 1980-2010 (OLD Apple)")
print("Test on:  2010-2025 (NEW Apple)")
print("="*70)

train_df = df[df['date'] < '2010-01-01']
test_df = df[df['date'] >= '2010-01-01']

X_train = train_df[['daily_return', 'sma_20', 'volatility_20']]
y_train = train_df['target']
X_test = test_df[['daily_return', 'sma_20', 'volatility_20']]
y_test = test_df['target']

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

acc1 = accuracy_score(y_test, y_pred)
prec1 = precision_score(y_test, y_pred, zero_division=0)
rec1 = recall_score(y_test, y_pred)

print(f"\nTrain samples: {len(X_train):,} days (30 years of OLD Apple)")
print(f"Test samples:  {len(X_test):,} days (15 years of NEW Apple)")
print(f"\nResults:")
print(f"  Accuracy:  {acc1:.2%}")
print(f"  Precision: {prec1:.2%}")
print(f"  Recall:    {rec1:.2%}")
print(f"\n💡 Interpretation:")
print(f"  Training on Steve Jobs era, testing on Tim Cook era")
print(f"  Different company, different patterns!")

# ============================================
# EXPERIMENT 2: Modern Data Only
# Train on: 2010-2020, Test on: 2020-2025
# ============================================
print("\n" + "="*70)
print("EXPERIMENT 2: Modern Data Only")
print("Train on: 2010-2020 (iPhone/iPad era)")
print("Test on:  2020-2025 (Recent)")
print("="*70)

modern_df = df[df['date'] >= '2010-01-01']
split_date = '2020-01-01'

train_df = modern_df[modern_df['date'] < split_date]
test_df = modern_df[modern_df['date'] >= split_date]

X_train = train_df[['daily_return', 'sma_20', 'volatility_20']]
y_train = train_df['target']
X_test = test_df[['daily_return', 'sma_20', 'volatility_20']]
y_test = test_df['target']

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

acc2 = accuracy_score(y_test, y_pred)
prec2 = precision_score(y_test, y_pred, zero_division=0)
rec2 = recall_score(y_test, y_pred)

print(f"\nTrain samples: {len(X_train):,} days (10 years)")
print(f"Test samples:  {len(X_test):,} days (5 years)")
print(f"\nResults:")
print(f"  Accuracy:  {acc2:.2%}")
print(f"  Precision: {prec2:.2%}")
print(f"  Recall:    {rec2:.2%}")
print(f"\n💡 Interpretation:")
print(f"  Same era, more consistent company behavior")
print(f"  Should perform better if hypothesis is correct!")

# ============================================
# EXPERIMENT 3: iPhone Era Only
# Train on: 2007-2018, Test on: 2018-2025
# ============================================
print("\n" + "="*70)
print("EXPERIMENT 3: iPhone Era Only")
print("Train on: 2007-2018 (iPhone dominance)")
print("Test on:  2018-2025 (Recent iPhone)")
print("="*70)

iphone_df = df[df['date'] >= '2007-01-01']
split_date = '2018-01-01'

train_df = iphone_df[iphone_df['date'] < split_date]
test_df = iphone_df[iphone_df['date'] >= split_date]

X_train = train_df[['daily_return', 'sma_20', 'volatility_20']]
y_train = train_df['target']
X_test = test_df[['daily_return', 'sma_20', 'volatility_20']]
y_test = test_df['target']

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

acc3 = accuracy_score(y_test, y_pred)
prec3 = precision_score(y_test, y_pred, zero_division=0)
rec3 = recall_score(y_test, y_pred)

print(f"\nTrain samples: {len(X_train):,} days")
print(f"Test samples:  {len(X_test):,} days")
print(f"\nResults:")
print(f"  Accuracy:  {acc3:.2%}")
print(f"  Precision: {prec3:.2%}")
print(f"  Recall:    {rec3:.2%}")
print(f"\n💡 Interpretation:")
print(f"  Most consistent era - iPhone-focused Apple")

# ============================================
# COMPARISON
# ============================================
print("\n" + "="*70)
print("RESULTS COMPARISON")
print("="*70)

print(f"\n{'Experiment':<40} {'Accuracy':<12} {'Precision':<12} {'Recall':<12}")
print("-"*76)
print(f"{'1. OLD → NEW (1980-2010 → 2010-2025)':<40} {acc1:<12.2%} {prec1:<12.2%} {rec1:<12.2%}")
print(f"{'2. Modern Only (2010-2020 → 2020-2025)':<40} {acc2:<12.2%} {prec2:<12.2%} {rec2:<12.2%}")
print(f"{'3. iPhone Era (2007-2018 → 2018-2025)':<40} {acc3:<12.2%} {prec3:<12.2%} {rec3:<12.2%}")

# ============================================
# CONCLUSION
# ============================================
print("\n" + "="*70)
print("HYPOTHESIS TEST")
print("="*70)

print("\n🎯 Your Hypothesis:")
print("   'Apple evolved multiple times - training on old Apple')")
print("   'won't predict new Apple behavior'")

if acc2 > acc1 or acc3 > acc1:
    print("\n✅ HYPOTHESIS CONFIRMED!")
    print(f"   Training on recent data performs better!")
    print(f"   Modern/iPhone era: {max(acc2, acc3):.2%}")
    print(f"   OLD → NEW: {acc1:.2%}")
    print(f"   Improvement: {(max(acc2, acc3) - acc1)*100:+.1f}%")
    print("\n💡 Key Insight:")
    print("   Company evolution DOES break predictions!")
    print("   Different eras = different patterns!")
    print("   Should only train on RECENT, relevant data!")
else:
    print("\n⚠️  HYPOTHESIS UNCLEAR")
    print(f"   Results are similar across eras")
    print(f"   Might be other factors at play")

print("\n" + "="*70)
print("KEY LEARNINGS")
print("="*70)

print("\n1. 📊 COMPANY CONTEXT MATTERS")
print("   - Apple in 1985 ≠ Apple in 2025")
print("   - Different products, different CEO, different market")
print("   - Historical data may not be relevant!")

print("\n2. ⚠️  MORE DATA ≠ BETTER")
print("   - 45 years of data seems good")
print("   - But includes irrelevant eras")
print("   - Better: Recent, relevant data")

print("\n3. 🎯 STATIONARITY ASSUMPTION")
print("   - ML assumes patterns stay constant")
print("   - But companies evolve!")
print("   - This breaks the assumption")

print("\n4. 💡 SOLUTION")
print("   - Use rolling window (e.g., last 5 years)")
print("   - Or detect regime changes")
print("   - Or train separate models per era")

print("\n" + "="*70)
print("✅ ANALYSIS COMPLETE!")
print("="*70)
