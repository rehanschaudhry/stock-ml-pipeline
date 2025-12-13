"""
Exploratory Data Analysis (EDA) for Stock Prediction
Check which features correlate with target!

Author: Rehan Salim Chaudhry
Date: 2024-12-10
"""

from config.settings import config
import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*60)
print("EXPLORATORY DATA ANALYSIS (EDA)")
print("="*60)

# ============================================
# STEP 1: LOAD DATA
# ============================================
print("\n📊 Step 1: Loading data...")

db_conn = psycopg2.connect(**config.DB_CONFIG)

query = f"""
        select date, open, high, low, close, volume
        from stock_prices
        where symbol = 'AAPL'
        order by date ASC
        """

df = pd.read_sql_query(query, db_conn)
print(f"✅ Loaded {len(df)} days of data")

# ============================================
# STEP 2: CREATE ALL POSSIBLE FEATURES
# ============================================
print("\n📊 Step 2: Creating features...")

# Price-based features
df['daily_return'] = df['close'].pct_change() * 100
df['sma_5'] = df['close'].rolling(window=5).mean()
df['sma_20'] = df['close'].rolling(window=20).mean()
df['sma_50'] = df['close'].rolling(window=50).mean()

# Volatility
df['volatility_5'] = df['daily_return'].rolling(window=5).std()
df['volatility_20'] = df['daily_return'].rolling(window=20).std()

# Momentum
df['momentum_5'] = df['close'].pct_change(periods=5) * 100
df['momentum_20'] = df['close'].pct_change(periods=20) * 100

# Volume
df['volume_change'] = df['volume'].pct_change() * 100
df['volume_sma_20'] = df['volume'].rolling(window=20).mean()

# Price position relative to MAs
df['price_above_sma_5'] = (df['close'] > df['sma_5']).astype(int)
df['price_above_sma_20'] = (df['close'] > df['sma_20']).astype(int)
df['price_above_sma_50'] = (df['close'] > df['sma_50']).astype(int)

# High-low spread
df['hl_spread'] = (df['high'] - df['low']) / df['close'] * 100

# Target
df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

# Clean
df = df.dropna()

print(f"✅ Created {len(df.columns) - 6} features")
print(f"✅ {len(df)} samples after cleaning")

# ============================================
# STEP 3: CORRELATION ANALYSIS
# ============================================
print("\n📊 Step 3: Analyzing correlations with target...")

# Select feature columns
feature_cols = [
    'daily_return', 'sma_5', 'sma_20', 'sma_50',
    'volatility_5', 'volatility_20',
    'momentum_5', 'momentum_20',
    'volume_change', 'volume_sma_20',
    'price_above_sma_5', 'price_above_sma_20', 'price_above_sma_50',
    'hl_spread'
]

# Calculate correlations with target
correlations = df[feature_cols + ['target']].corr()['target'].drop('target').sort_values(ascending=False)

print("\n" + "="*60)
print("FEATURE-TARGET CORRELATIONS")
print("="*60)
print(f"{'Feature':<25} {'Correlation':<15} {'Strength':<15}")
print("-"*60)

for feature, corr in correlations.items():
    if abs(corr) > 0.1:
        strength = "Strong ✅"
    elif abs(corr) > 0.05:
        strength = "Medium ⚠️"
    else:
        strength = "Weak ❌"
    
    print(f"{feature:<25} {corr:>+.4f}          {strength}")

print("\n💡 Interpretation:")
print("   Correlation > 0.1: Strong positive relationship")
print("   Correlation < -0.1: Strong negative relationship")
print("   Correlation near 0: No relationship (useless feature!)")

# ============================================
# STEP 4: IDENTIFY BEST FEATURES
# ============================================
print("\n" + "="*60)
print("RECOMMENDED FEATURES")
print("="*60)

strong_features = correlations[abs(correlations) > 0.05].index.tolist()
weak_features = correlations[abs(correlations) <= 0.05].index.tolist()

print(f"\n✅ KEEP THESE ({len(strong_features)} features):")
for feat in strong_features:
    print(f"   - {feat} (correlation: {correlations[feat]:+.4f})")

print(f"\n❌ DROP THESE ({len(weak_features)} features):")
for feat in weak_features:
    print(f"   - {feat} (correlation: {correlations[feat]:+.4f})")

# ============================================
# STEP 5: VISUALIZATIONS
# ============================================
print("\n📊 Step 4: Creating visualizations...")

# 1. Correlation Heatmap
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Subplot 1: Correlation bar chart
ax1 = axes[0, 0]
correlations_sorted = correlations.sort_values()
colors = ['red' if x < 0 else 'green' for x in correlations_sorted.values]
correlations_sorted.plot(kind='barh', ax=ax1, color=colors)
ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
ax1.axvline(x=0.05, color='orange', linestyle='--', linewidth=0.8, label='Weak threshold')
ax1.axvline(x=-0.05, color='orange', linestyle='--', linewidth=0.8)
ax1.set_xlabel('Correlation with Target', fontsize=12)
ax1.set_title('Feature-Target Correlations', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Subplot 2: UP vs DOWN days feature comparison
ax2 = axes[0, 1]
up_days = df[df['target'] == 1]
down_days = df[df['target'] == 0]

feature_means_up = up_days[feature_cols].mean()
feature_means_down = down_days[feature_cols].mean()

x = np.arange(len(strong_features[:6]))  # Top 6 features
width = 0.35

bars1 = ax2.bar(x - width/2, [feature_means_up[f] for f in strong_features[:6]], 
                width, label='UP days', color='green', alpha=0.7)
bars2 = ax2.bar(x + width/2, [feature_means_down[f] for f in strong_features[:6]], 
                width, label='DOWN days', color='red', alpha=0.7)

ax2.set_xlabel('Feature', fontsize=12)
ax2.set_ylabel('Average Value', fontsize=12)
ax2.set_title('Feature Averages: UP vs DOWN days', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(strong_features[:6], rotation=45, ha='right')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# Subplot 3: Distribution of best feature
ax3 = axes[1, 0]
best_feature = correlations.abs().idxmax()
df[df['target'] == 1][best_feature].hist(bins=50, ax=ax3, alpha=0.6, 
                                           color='green', label='UP days', density=True)
df[df['target'] == 0][best_feature].hist(bins=50, ax=ax3, alpha=0.6, 
                                           color='red', label='DOWN days', density=True)
ax3.set_xlabel(best_feature, fontsize=12)
ax3.set_ylabel('Density', fontsize=12)
ax3.set_title(f'Distribution of Best Feature: {best_feature}', fontsize=14, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Subplot 4: Target distribution
ax4 = axes[1, 1]
target_counts = df['target'].value_counts()
colors_pie = ['red', 'green']
ax4.pie(target_counts, labels=['DOWN (0)', 'UP (1)'], autopct='%1.1f%%',
        colors=colors_pie, startangle=90)
ax4.set_title('Target Distribution (Class Imbalance)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('eda_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Saved: eda_analysis.png")
plt.close()

# ============================================
# STEP 6: FEATURE SELECTION RECOMMENDATION
# ============================================
print("\n" + "="*60)
print("FINAL RECOMMENDATIONS")
print("="*60)

print("\n🎯 Based on correlation analysis:")
print(f"   - {len(strong_features)} features show meaningful correlation")
print(f"   - {len(weak_features)} features are essentially noise")
print()
print("💡 For your model:")
print(f"   Use these features: {', '.join(strong_features[:5])}")
print()
print("⚠️  Warning:")
if len(strong_features) == 0:
    print("   ❌ NO features show strong correlation!")
    print("   ❌ This explains why model accuracy is ~50% (random)!")
    print("   ❌ Need better features (sentiment, news, fundamentals)")
elif max(abs(correlations)) < 0.1:
    print("   ⚠️  All correlations are WEAK!")
    print("   ⚠️  This explains poor model performance!")
    print("   ⚠️  Technical indicators alone are insufficient!")
else:
    print("   ✅ Some features show promise!")
    print("   ✅ Model should perform better than random!")

print("\n" + "="*60)
print("✅ EDA COMPLETE!")
print("="*60)
print("\nNext steps:")
print("1. Review eda_analysis.png")
print("2. Use only the recommended features")
print("3. Re-train model with selected features")
print("4. Compare new accuracy to baseline (47%)")
print("="*60)
