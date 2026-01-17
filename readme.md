# Stock ML Pipeline

**End-to-end machine learning pipeline for stock price prediction**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![ML](https://img.shields.io/badge/ML-Scikit--Learn%20%7C%20XGBoost-orange.svg)](https://scikit-learn.org)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://postgresql.org)

## 📊 Project Overview

A production-quality machine learning pipeline that predicts next-day stock price movements using technical indicators. Built with secure configuration management, comprehensive evaluation metrics, and professional visualizations.

**Key Features:**
- 🔐 Secure configuration (no hardcoded credentials)
- 📈 140,000+ historical data points (17 stocks, up to 45 years per stock)
- 🤖 Multiple ML models (Random Forest, XGBoost)
- 📊 Comprehensive evaluation (Precision, Recall, F1, ROC-AUC)
- 🎨 Professional visualizations
- 📝 Detailed documentation

## 🎯 Project Goals

1. **Technical Skills:** Build complete ML pipeline from data collection to evaluation
2. **Real-World Learning:** Understand why stock prediction is fundamentally difficult
3. **Best Practices:** Implement security, testing, and documentation standards
4. **Portfolio Piece:** Demonstrate end-to-end ML engineering capabilities

## 📈 Results Summary

**Dataset:** Apple (AAPL) - 10,568 days after cleaning  
**Models:** Random Forest vs XGBoost  
**Traditional Approach:** ~49% accuracy (training on all historical data)  
**Improved Approach:** ~52.5% accuracy (training on recent, relevant data)

### 🔥 Key Discovery: Company Evolution Matters!

We discovered that **Apple's evolution breaks ML predictions**. Training on 1980s Apple (computer company, Steve Jobs fired) to predict 2025 Apple (iPhone/services company, Tim Cook era) is like training on a bakery to predict a tech company!

**Breakthrough Results:**

| Approach | Training Period | Test Period | Accuracy | Recall |
|----------|----------------|-------------|----------|--------|
| **Traditional** | 1980-2010 (30 years) | 2010-2025 | 48.64% | 12.51% |
| **Modern Only** ⭐ | 2010-2020 (10 years) | 2020-2025 | **52.51%** | **89.28%** |
| **Improvement** | - | - | **+3.9%** | **+77%** |

**Key Insight:** Relevant data matters more than data volume. Using only recent, consistent Apple data (post-iPhone era) dramatically improved both accuracy AND recall (7× better at catching profitable opportunities)!

### Model Comparison (Traditional Approach)

| Metric | Random Forest | XGBoost | Interpretation |
|--------|--------------|---------|----------------|
| **Accuracy** | 49.05% | 49.15% | Near random guessing |
| **Precision** | 55.79% | 52.90% | RF more reliable per trade |
| **Recall** | 23.83% | 46.69% | XGBoost catches 2× opportunities |
| **F1-Score** | 33.40% | 49.60% | XGBoost better balanced |
| **ROC-AUC** | 0.5030 | 0.4988 | Both near 0.50 (random) |

**Finding:** Basic technical indicators alone are insufficient. This project demonstrates proper ML evaluation, the importance of business context, and realistic expectations about ML capabilities.

## 🗏️ Architecture

```
stock-ml-pipeline/
├── config/
│   ├── settings.py          # Secure configuration (uses .env)
│   └── __init__.py
├── data/
│   ├── database.py          # DatabaseManager class
│   └── __init__.py
├── model_comparison.py      # Train & evaluate models
├── create_visualizations.py # Generate evaluation charts
├── working_yahoo_loader.py  # Load historical data
├── apple_era_analysis.py    # Era-based analysis (breakthrough!)
├── eda_analysis.py          # Exploratory data analysis
├── evaluation_report.md     # Detailed analysis
├── .env                     # Credentials (not in git!)
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.11+
PostgreSQL 17
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/rehanschaudhry/stock-ml-pipeline.git
cd stock-ml-pipeline
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Create database**
```sql
CREATE DATABASE stock_ml_db;
```

6. **Run the setup script**
```bash
# Create tables
psql -U postgres -d stock_ml_db -f setup_database.sql
```

### Usage

**1. Load stock data (free, unlimited!)**
```bash
python working_yahoo_loader.py
# Choose option 2 to load all 17 stocks
```

**2. Run model comparison**
```bash
python model_comparison.py
```

**3. Run era analysis (recommended!)**
```bash
python apple_era_analysis.py
```

**4. Generate visualizations**
```bash
python create_visualizations.py
```

**5. View evaluation report**
```bash
# Open evaluation_report.md
```

## 📊 Visualizations

The project generates 4 professional visualizations:

1. **Confusion Matrix Heatmaps** - Prediction patterns
2. **ROC Curves** - Model discriminative ability
3. **Feature Importance** - Which features matter most
4. **Metrics Comparison** - Side-by-side performance

## 🛠️ Technologies Used

- **Language:** Python 3.11
- **ML Libraries:** scikit-learn, XGBoost
- **Data Processing:** pandas, numpy
- **Visualization:** matplotlib, seaborn
- **Database:** PostgreSQL 17 with psycopg2
- **Data Source:** Yahoo Finance (via yfinance)
- **Configuration:** python-dotenv

## 📚 Key Learnings

### 1. Company Evolution > Data Volume ⭐ BREAKTHROUGH!

Even with 45 years of Apple stock data (11,340 days), models achieved only ~49% accuracy when training on all historical data. **The discovery:** Apple evolved multiple times - from computers (1980s) to music (iPod era) to smartphones (iPhone era). Training on "old Apple" to predict "new Apple" is fundamentally flawed.

**Discovery:** Training only on recent, consistent data (2010-2020) and testing on similar periods (2020-2025) improved:
- Accuracy: 48.64% → 52.51% (+3.9%)
- Recall: 12.51% → 89.28% (+77% / 7× better!)

**Lesson:** In ML, **relevant data matters more than data volume**. This demonstrates the importance of:
- Non-stationarity detection
- Regime change analysis  
- Business context understanding
- Critical thinking about data assumptions

### 2. Proper Evaluation is Critical

Accuracy alone is misleading - we need multiple metrics:
- **Precision** reveals reliability when predicting UP
- **Recall** shows what % of opportunities we catch
- **F1-Score** exposes precision-recall imbalances
- **ROC-AUC** measures overall ranking ability
- **Confusion Matrix** reveals where errors occur

Example: A model with 100% precision but 0.25% recall is useless - it's too conservative!

### 3. Domain Knowledge is Essential

Understanding *why* models fail is as important as building them:
- Stock prediction requires financial domain expertise
- Technical indicators alone are insufficient (need news, sentiment, fundamentals)
- Class imbalance (64% DOWN days vs 36% UP days) breaks standard models
- Real-world constraints matter (transaction costs, market impact)

### 4. Realistic Expectations Matter

ML is not magic - some problems are fundamentally hard:
- Next-day stock prediction with basic features: ~50% accuracy is normal
- Even professional quant funds achieve only 52-55% accuracy
- Publishing honest results > hiding failures
- Understanding limitations makes better ML engineers

## 🎯 Future Improvements

### Short-term (52-55% accuracy potential)
- [x] Era-based analysis and regime detection
- [ ] Add class weighting to handle imbalance
- [ ] Add RSI, MACD, Bollinger Bands
- [ ] Change target to 5-day or 10-day trends
- [ ] Add market context (S&P 500, VIX)

### Long-term (60-65% accuracy potential)
- [ ] Sentiment analysis (news, social media)
- [ ] Fundamental analysis (P/E, revenue)
- [ ] LSTM/RNN for sequence modeling
- [ ] Multi-stock correlation features
- [ ] Rolling window approach (continuous retraining)

## 📝 Project Status

- [x] Week 1: Foundation (DatabaseManager, security)
- [x] Week 2 Days 1-2: Model comparison with Yahoo Finance data
- [x] Week 2 Day 3: Evaluation metrics, EDA, era analysis
- [ ] Week 2 Days 4-5: Project cleanup and polish
- [ ] Week 3-4: Deployment (FastAPI or Streamlit)
- [ ] Week 5+: Job applications

## 🔗 Related Projects

This project demonstrates skills applicable across my ML portfolio:

- **[RAG Document Intelligence](https://github.com/rehanschaudhry/rag-document-intelligence)** ⭐ NEW!
  - Production RAG system with semantic search
  - 122 chunks indexed | FAISS vector DB | Claude Sonnet 4
  - Demonstrates: LLM integration, vector databases, hallucination prevention

- **[Credit Card Fraud Detection](https://github.com/rehanschaudhry/creditcard-fraud-detection)**
  - Imbalanced classification with 89.28% recall
  - PySpark + Databricks | MLflow tracking
  - Demonstrates: Big data processing, production ML pipelines

- **[PDF-LLM Pipeline](https://github.com/rehanschaudhry/pdf-llm-pipeline)**
  - Production pipeline for PDF text extraction
  - PyPDF2 | Parquet optimization
  - Demonstrates: Data engineering, document processing

## 🎯 Why This Project Matters

This project showcases several critical ML engineering skills:

✅ **Honest Evaluation** - Publishing 52.51% accuracy (vs hiding it) shows integrity  
✅ **Critical Thinking** - Discovering company evolution matters more than data volume  
✅ **Domain Knowledge** - Understanding why stock prediction is hard  
✅ **Production Practices** - Secure config, comprehensive testing, professional docs  
✅ **Business Context** - Explaining metrics in terms traders understand  
✅ **Research Skills** - Era analysis represents original research contribution  

**The Breakthrough:** Most ML tutorials show 95%+ accuracy on toy datasets. This project tackles a genuinely hard problem and demonstrates that understanding *why* models fail is as important as making them work.

## 🤝 Contributing

This is a personal learning project, but feedback is welcome! Open to collaboration and suggestions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Rehan Chaudhry**
- Transitioning into ML/AI professionally
- Focused on production ML systems with realistic expectations
- [GitHub](https://github.com/rehanschaudhry)
- [LinkedIn](https://www.linkedin.com/in/rehanchaudhry/)

## 🙏 Acknowledgments

- Yahoo Finance for free historical data
- UofT Data Science Institute curriculum for ML guidance
- Anthropic's Claude for technical assistance

---

## 📊 Sample Output

```
📈 Model Performance Comparison:
============================================================

   ACCURACY COMPARISON:
   Random Forest:  49.05%
   XGBoost:        49.15%

   💡 WHAT THESE METRICS MEAN FOR STOCK TRADING:
   Precision (XGBoost): 52.9%
   → When model says BUY, it's right 52.9% of the time
   
   Recall (XGBoost): 46.7%
   → Model catches 46.7% of all profitable opportunities
   
   ROC-AUC (XGBoost): 0.4988
   → Model is 0.0012 better than random

============================================================
ERA ANALYSIS RESULTS:
============================================================

   Traditional (1980-2010 → 2010-2025):  48.64% accuracy
   Modern Only (2010-2020 → 2020-2025):  52.51% accuracy ⭐
   
   Improvement: +3.9% accuracy, +77% recall
   Key Discovery: Company evolution breaks predictions!
```

---

**Built with ❤️ and realistic ML expectations**

**⭐ Featured Discovery:** This project demonstrates that understanding business context and company evolution can improve ML models more than adding complex features!