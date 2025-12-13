"""
Model Evaluation Visualizations
Creates beautiful charts for model comparison

Author: Rehan Salim Chaudhry
Date: 2024-12-10
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    roc_auc_score
)
from xgboost import XGBClassifier
import psycopg2

from config.settings import config

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def connect_db():
    """Connect to database"""
    return psycopg2.connect(**config.DB_CONFIG)


def prepare_data(symbol='AAPL'):
    """Prepare data (same as model_comparison.py)"""
    print(f"📊 Loading data for {symbol}...")
    
    conn = connect_db()
    query = f"""
        SELECT date, open, high, low, close, volume
        FROM stock_prices 
        WHERE symbol = '{symbol}'
        ORDER BY date
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Feature engineering
    df['daily_return'] = df['close'].pct_change() * 100
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['volatility_20'] = df['daily_return'].rolling(window=20).std()
    df['momentum_5'] = df['close'].pct_change(periods=5) * 100
    df['volume_change'] = df['volume'].pct_change() * 100
    df['hl_spread'] = (df['high'] - df['low']) / df['close'] * 100
    df['tomorrow_close'] = df['close'].shift(-1)
    df['target'] = (df['tomorrow_close'] > df['close']).astype(int)
    
    # Clean data
    df = df.replace([float('inf'), float('-inf')], float('nan'))
    df = df.dropna()
    
    # Remove outliers
    numeric_columns = ['daily_return', 'volatility_20', 'momentum_5', 'volume_change', 'hl_spread']
    for col in numeric_columns:
        if col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            df = df[(df[col] >= mean - 3*std) & (df[col] <= mean + 3*std)]
    
    print(f"   ✅ Prepared {len(df)} days of clean data")
    return df


def train_models(df):
    """Train both models"""
    print(f"\n🤖 Training models...")
    
    feature_columns = [
        'daily_return', 'sma_5', 'sma_20', 'sma_50',
        'volatility_20', 'momentum_5', 'volume_change', 'hl_spread'
    ]
    
    X = df[feature_columns]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=config.TRAIN_TEST_SPLIT,
        shuffle=False,
        random_state=config.RANDOM_STATE
    )
    
    # Train Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=config.RF_N_ESTIMATORS,
        max_depth=config.RF_MAX_DEPTH,
        random_state=config.RANDOM_STATE
    )
    rf_model.fit(X_train, y_train)
    
    # Train XGBoost
    xgb_model = XGBClassifier(
        n_estimators=config.RF_N_ESTIMATORS,
        max_depth=config.RF_MAX_DEPTH,
        random_state=config.RANDOM_STATE,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train, y_train)
    
    print(f"   ✅ Both models trained!")
    
    return rf_model, xgb_model, X_test, y_test, feature_columns


def plot_confusion_matrices(rf_model, xgb_model, X_test, y_test):
    """Create confusion matrix heatmaps"""
    print(f"\n📊 Creating confusion matrix heatmaps...")
    
    rf_pred = rf_model.predict(X_test)
    xgb_pred = xgb_model.predict(X_test)
    
    rf_cm = confusion_matrix(y_test, rf_pred)
    xgb_cm = confusion_matrix(y_test, xgb_pred)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Random Forest
    sns.heatmap(rf_cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
                xticklabels=['DOWN', 'UP'], yticklabels=['DOWN', 'UP'])
    axes[0].set_title('Random Forest\nConfusion Matrix', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Actual', fontsize=12)
    axes[0].set_xlabel('Predicted', fontsize=12)
    
    # XGBoost
    sns.heatmap(xgb_cm, annot=True, fmt='d', cmap='Greens', ax=axes[1],
                xticklabels=['DOWN', 'UP'], yticklabels=['DOWN', 'UP'])
    axes[1].set_title('XGBoost\nConfusion Matrix', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Actual', fontsize=12)
    axes[1].set_xlabel('Predicted', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('confusion_matrices.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: confusion_matrices.png")
    plt.close()


def plot_roc_curves(rf_model, xgb_model, X_test, y_test):
    """Create ROC curves"""
    print(f"\n📈 Creating ROC curves...")
    
    # Get probability predictions
    rf_proba = rf_model.predict_proba(X_test)[:, 1]
    xgb_proba = xgb_model.predict_proba(X_test)[:, 1]
    
    # Calculate ROC curves
    rf_fpr, rf_tpr, _ = roc_curve(y_test, rf_proba)
    xgb_fpr, xgb_tpr, _ = roc_curve(y_test, xgb_proba)
    
    rf_auc = roc_auc_score(y_test, rf_proba)
    xgb_auc = roc_auc_score(y_test, xgb_proba)
    
    # Plot
    plt.figure(figsize=(10, 8))
    
    # Random Forest
    plt.plot(rf_fpr, rf_tpr, color='blue', lw=2, 
             label=f'Random Forest (AUC = {rf_auc:.4f})')
    
    # XGBoost
    plt.plot(xgb_fpr, xgb_tpr, color='green', lw=2,
             label=f'XGBoost (AUC = {xgb_auc:.4f})')
    
    # Random baseline
    plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--',
             label='Random Guessing (AUC = 0.5000)')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curves: Model Comparison', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.savefig('roc_curves.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: roc_curves.png")
    plt.close()


def plot_feature_importance(rf_model, xgb_model, feature_columns):
    """Create feature importance comparison"""
    print(f"\n📊 Creating feature importance chart...")
    
    # Get importances
    rf_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=True)
    
    xgb_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': xgb_model.feature_importances_
    }).sort_values('importance', ascending=True)
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Random Forest
    axes[0].barh(rf_importance['feature'], rf_importance['importance'], color='skyblue')
    axes[0].set_xlabel('Importance', fontsize=12)
    axes[0].set_title('Random Forest\nFeature Importance', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='x')
    
    # XGBoost
    axes[1].barh(xgb_importance['feature'], xgb_importance['importance'], color='lightgreen')
    axes[1].set_xlabel('Importance', fontsize=12)
    axes[1].set_title('XGBoost\nFeature Importance', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: feature_importance.png")
    plt.close()


def plot_metrics_comparison(rf_model, xgb_model, X_test, y_test):
    """Create metrics comparison bar chart"""
    print(f"\n📊 Creating metrics comparison chart...")
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    
    rf_pred = rf_model.predict(X_test)
    xgb_pred = xgb_model.predict(X_test)
    
    rf_proba = rf_model.predict_proba(X_test)[:, 1]
    xgb_proba = xgb_model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'Accuracy': [accuracy_score(y_test, rf_pred), accuracy_score(y_test, xgb_pred)],
        'Precision': [precision_score(y_test, rf_pred), precision_score(y_test, xgb_pred)],
        'Recall': [recall_score(y_test, rf_pred), recall_score(y_test, xgb_pred)],
        'F1-Score': [f1_score(y_test, rf_pred), f1_score(y_test, xgb_pred)],
        'ROC-AUC': [roc_auc_score(y_test, rf_proba), roc_auc_score(y_test, xgb_proba)]
    }
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    rf_values = [metrics[m][0] for m in metrics]
    xgb_values = [metrics[m][1] for m in metrics]
    
    ax.bar(x - width/2, rf_values, width, label='Random Forest', color='skyblue')
    ax.bar(x + width/2, xgb_values, width, label='XGBoost', color='lightgreen')
    
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Model Metrics Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics.keys(), fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, 1])
    
    # Add value labels on bars
    for i, (rf_val, xgb_val) in enumerate(zip(rf_values, xgb_values)):
        ax.text(i - width/2, rf_val + 0.02, f'{rf_val:.3f}', ha='center', fontsize=9)
        ax.text(i + width/2, xgb_val + 0.02, f'{xgb_val:.3f}', ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('metrics_comparison.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: metrics_comparison.png")
    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("MODEL EVALUATION VISUALIZATIONS")
    print("="*60)
    
    # Prepare data
    df = prepare_data('AAPL')
    
    # Train models
    rf_model, xgb_model, X_test, y_test, feature_columns = train_models(df)
    
    # Create visualizations
    print("\n" + "="*60)
    print("CREATING VISUALIZATIONS")
    print("="*60)
    
    plot_confusion_matrices(rf_model, xgb_model, X_test, y_test)
    plot_roc_curves(rf_model, xgb_model, X_test, y_test)
    plot_feature_importance(rf_model, xgb_model, feature_columns)
    plot_metrics_comparison(rf_model, xgb_model, X_test, y_test)
    
    print("\n" + "="*60)
    print("✅ ALL VISUALIZATIONS CREATED!")
    print("="*60)
    print("\nFiles created:")
    print("  📊 confusion_matrices.png")
    print("  📈 roc_curves.png")
    print("  📊 feature_importance.png")
    print("  📊 metrics_comparison.png")
    print("\n" + "="*60)
    print("🎨 Check your project folder for beautiful charts!")
    print("="*60)
