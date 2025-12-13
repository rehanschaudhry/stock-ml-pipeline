# Model Evaluation Report
## Stock Price Prediction: Random Forest vs XGBoost

**Project:** Stock ML Pipeline  
**Author:** Rehan Salim Chaudhry  
**Date:** December 10, 2024  
**Dataset:** Apple (AAPL) Stock - 45 years of historical data

---

## Executive Summary

This report presents a comprehensive evaluation of two machine learning models (Random Forest and XGBoost) for predicting next-day stock price movements. Despite having access to 10,568 days of clean historical data, both models achieved approximately 49% accuracy, effectively performing at random chance levels.

**Key Finding:** Basic technical indicators alone are insufficient for reliable stock price prediction.

---

## Dataset Overview

### Data Statistics
- **Total Records:** 11,340 days (1980-2025)
- **After Cleaning:** 10,568 days
- **Training Set:** 8,454 days (80%)
- **Test Set:** 2,114 days (20%)
- **Target Distribution:** 
  - UP days: 3,941 (37.3%)
  - DOWN days: 6,627 (62.7%)
  - **Imbalanced dataset** (more DOWN days)

### Features Used
1. **daily_return** - Daily percentage change
2. **sma_5** - 5-day simple moving average
3. **sma_20** - 20-day simple moving average
4. **sma_50** - 50-day simple moving average
5. **volatility_20** - 20-day rolling standard deviation
6. **momentum_5** - 5-day momentum
7. **volume_change** - Volume percentage change
8. **hl_spread** - High-low spread ratio

---

## Model Performance Comparison

### Overall Metrics

| Metric | Random Forest | XGBoost | Winner | Interpretation |
|--------|--------------|---------|--------|----------------|
| **Accuracy** | 49.05% | 49.15% | XGBoost ✅ | Both ≈ random guessing |
| **Precision** | 55.79% | 52.90% | RF ✅ | RF more reliable per trade |
| **Recall** | 23.83% | 46.69% | XGBoost ✅ | XGBoost catches 2× more opportunities |
| **F1-Score** | 33.40% | 49.60% | XGBoost ✅ | XGBoost better balanced |
| **ROC-AUC** | 0.5030 | 0.4988 | RF ✅ | Both near 0.50 (random) |

### Key Observations

1. **Random Forest Strategy: Conservative**
   - High precision (55.8%) but low recall (23.8%)
   - Only predicts UP when very confident
   - Misses 76% of profitable opportunities
   - Good for: Risk-averse trading, small portfolios

2. **XGBoost Strategy: Balanced**
   - Medium precision (52.9%) and recall (46.7%)
   - More aggressive in predictions
   - Catches twice as many opportunities as RF
   - Good for: High-volume trading, larger portfolios

3. **Both Models Near Random**
   - Accuracy ≈ 50% (coin flip)
   - ROC-AUC ≈ 0.50 (cannot rank UP vs DOWN days)
   - No model has found reliable predictive patterns

---

## Confusion Matrix Analysis

### XGBoost Confusion Matrix
```
                Predicted
              DOWN    UP
Actual DOWN   510    471    (981 total DOWN days)
       UP     604    529    (1,133 total UP days)
```

**Breakdown:**
- **True Negatives (510):** Correctly predicted DOWN - Avoided bad trades
- **False Positives (471):** Predicted UP but went DOWN - Lost money 💸
- **False Negatives (604):** Predicted DOWN but went UP - Missed opportunity 😢
- **True Positives (529):** Correctly predicted UP - Profitable trades! 💰

### Trading Implications

**For every 1000 predictions:**
- **529 profitable trades** (52.9% win rate when buying)
- **471 losing trades** (47.1% loss rate)
- **Net result:** Slightly better than random, but not enough for consistent profitability

**Cost Analysis:**
- If False Positive costs $100 (actual loss)
- If False Negative costs $50 (opportunity cost)
- **Total cost:** (471 × $100) + (604 × $50) = $77,300
- **Barely better than not trading at all!**

---

## Feature Importance Analysis

### Random Forest Top Features
1. **sma_5** (19.47%) - Short-term moving average
2. **sma_20** (18.06%) - Medium-term moving average
3. **sma_50** (16.42%) - Long-term moving average
4. **volatility_20** (10.96%)
5. **volume_change** (9.59%)

### XGBoost Top Features
1. **sma_5** (20.10%) - Short-term moving average
2. **sma_20** (14.36%) - Medium-term moving average
3. **hl_spread** (11.43%)
4. **volume_change** (10.99%)
5. **daily_return** (11.09%)

### Key Insights
- **Both models agree:** Moving averages are most important
- **Short-term signals matter more** than long-term trends
- **Volume and volatility** have moderate importance
- **Daily return alone** is weak predictor

---

## ROC-AUC Analysis

### Results
- **Random Forest AUC:** 0.5030 (0.3% better than random)
- **XGBoost AUC:** 0.4988 (0.1% worse than random)
- **Random Baseline AUC:** 0.5000

### Interpretation
ROC-AUC measures the model's ability to rank UP days higher than DOWN days:
- **AUC = 0.50** means if you pick a random UP day and random DOWN day, the model ranks them correctly 50% of the time (random)
- **AUC = 1.00** would mean perfect ranking
- **Our models ≈ 0.50** means no ranking ability

**Conclusion:** Models cannot distinguish between UP and DOWN days based on technical indicators alone.

---

## Why Models Failed: Root Cause Analysis

### 1. Efficient Market Hypothesis
- If basic technical indicators could predict stocks, everyone would use them
- Markets quickly incorporate publicly available information
- Technical indicators are "common knowledge" → no edge

### 2. Missing Critical Information
Our models don't have access to:
- **News events** (earnings reports, product launches, scandals)
- **Market sentiment** (fear/greed, social media trends)
- **Macroeconomic factors** (interest rates, inflation, GDP)
- **Company fundamentals** (revenue, profits, debt)
- **Sector trends** (tech sector movements affect Apple)
- **Global events** (recessions, pandemics, wars)

### 3. Short-Term Prediction is Noisy
- Next-day movements are highly random
- Influenced by countless unpredictable factors
- Signal-to-noise ratio is extremely low

### 4. Feature Engineering Limitations
- Only 8 simple technical indicators
- No advanced indicators (RSI, MACD, Bollinger Bands)
- No multi-stock correlation features
- No time-based features (day of week, month effects)

---

## Lessons Learned

### 1. More Data ≠ Better Predictions
- 45 years of data (11,340 days) didn't improve accuracy
- Quality and relevance of features matter more than quantity of data

### 2. Proper Evaluation is Critical
- Accuracy alone would miss the precision/recall tradeoff
- ROC-AUC revealed models have no discriminative power
- Confusion matrix showed where errors occur
- Multiple metrics needed for complete picture

### 3. Domain Knowledge is Essential
- Understanding *why* models fail is as important as building them
- Stock prediction requires financial domain expertise
- Technical skills must combine with business understanding

### 4. Realistic Expectations Matter
- ML is not magic - some problems are fundamentally hard
- Publishing ~50% accuracy is more honest than hiding failures
- Understanding limitations makes better ML engineers

---

## Recommendations for Improvement

### Short-Term (Could improve to 52-55% accuracy)
1. **Add technical indicators:**
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Bollinger Bands
   - Stochastic Oscillator

2. **Change prediction target:**
   - Predict 5-day or 10-day trends (less noisy)
   - Predict magnitude of change (regression instead of classification)
   - Predict probability of >2% gain (more meaningful threshold)

3. **Add market context:**
   - S&P 500 trend
   - Tech sector performance
   - VIX (volatility index)

### Long-Term (Could improve to 60-65% accuracy)
1. **Sentiment analysis:**
   - News article sentiment
   - Social media sentiment
   - Analyst ratings

2. **Fundamental analysis:**
   - P/E ratio
   - Revenue growth
   - Earnings surprises

3. **Advanced techniques:**
   - LSTM/RNN for sequence modeling
   - Ensemble with multiple timeframes
   - Feature selection algorithms

### Realistic Expectations
- Even professional quant funds achieve 52-55% accuracy
- 60%+ accuracy would be exceptional
- Consistent 70%+ accuracy is nearly impossible
- Focus should be on risk management, not just accuracy

---

## Conclusion

This project successfully demonstrates:
- ✅ **Complete ML pipeline:** Data collection, feature engineering, training, evaluation
- ✅ **Proper evaluation methodology:** Multiple metrics, visualizations, deep analysis
- ✅ **Production-quality code:** Secure, modular, documented
- ✅ **Critical thinking:** Understanding why models fail, not just building them
- ✅ **Realistic reporting:** Honest about limitations, no cherry-picking results

**Bottom Line:** While the models did not achieve high accuracy, the project successfully demonstrates end-to-end ML engineering skills and the importance of proper evaluation and realistic expectations. The ~49% accuracy is not a failure - it's a valuable lesson about the fundamental difficulty of stock prediction with basic technical indicators.

---

## Appendix: Technical Details

### Model Hyperparameters
**Random Forest:**
- n_estimators: 100
- max_depth: 10
- random_state: 42

**XGBoost:**
- n_estimators: 100
- max_depth: 10
- random_state: 42
- eval_metric: logloss

### Data Cleaning Process
1. Removed infinity values (from division by zero)
2. Removed NaN values (from rolling calculations)
3. Removed outliers beyond 3 standard deviations
4. Resulted in 10,568 clean samples from 11,340 raw samples (93.2% retention)

### Train/Test Split
- Method: Chronological split (no shuffle)
- Ratio: 80/20
- Rationale: Respects time series nature, prevents data leakage

---

## Files Generated

1. **confusion_matrices.png** - Visual comparison of prediction patterns
2. **roc_curves.png** - ROC curves showing discriminative ability
3. **feature_importance.png** - Feature importance rankings
4. **metrics_comparison.png** - Side-by-side metrics comparison
5. **model_comparison.py** - Enhanced with detailed metrics
6. **create_visualizations.py** - Visualization generation script

---

**Report End**
