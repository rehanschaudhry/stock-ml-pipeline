# Stock ML Pipeline - Progress Tracker

**Last Updated:** 2024-11-26  
**Current Week:** 1, Day 2  
**Phase:** Python Refactoring  
**GitHub:** https://github.com/rehanschaudhry/stock-ml-pipeline

---

## 🎯 MAIN GOAL
Get ML Engineer job in 3-4 months using speed-focused approach with strong Python skills (60% Python, 40% ML).

**Why:** Want to use math/stats again, money, eventually get into AI, EB-2 path with IE degree.

---

## ⏱️ TIME COMMITMENT
- **Weekdays:** 1 hour/day
- **Weekends:** 3 hours total
- **Total:** ~8 hours/week (sustainable!)

---

## 📊 CURRENT STATUS

### This Week (Week 1)
- [x] **Day 1:** API integration + PostgreSQL (17 stocks, 1,700 records) ✅
- [x] **Day 1:** Feature engineering + First ML model (Random Forest, 60% accuracy) ✅
- [x] **Day 1:** Learned about Random Forest vs Decision Tree ✅
- [x] **Day 1:** Understood why 80/20 split for time series ✅
- [ ] **Day 2:** Refactor into clean Python modules (TONIGHT - IN PROGRESS)

### Working On RIGHT NOW
- **Task:** Python refactoring - transforming scripts into professional modules
- **Current File:** Setting up project structure
- **Progress:** Created directory structure, ready to build modules
- **Blockers:** None
- **Next:** Create `config/settings.py`, then `data/database.py`, then `data/api_client.py`

---

## ✅ COMPLETED

### Infrastructure
- [x] Alpha Vantage API integration (API key: working)
- [x] PostgreSQL 17 database setup (stock_ml_db)
- [x] Database connection working (password: mmhy68mm)
- [x] 17 tech stocks loaded (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, NFLX, ADBE, CRM, AMD, AVGO, QCOM, CSCO, ORCL, IBM, INTC)
- [x] 1,700 records total (100 days × 17 stocks)

### Features Created
- [x] Daily returns calculation (`pct_change() * 100`)
- [x] Moving averages (5, 20, 50 day) (`rolling().mean()`)
- [x] Volatility (20-day) (`rolling().std()` on returns)
- [x] Momentum features (5-day price change)
- [x] Volume change
- [x] High-low spread

### ML Model
- [x] Random Forest model trained
- [x] 60% accuracy (baseline)
- [x] Feature importance: momentum_5 = 18.7% (most important)
- [x] Confusion matrix analyzed (model predicts DOWN for everything due to small data)
- [x] Understood WHY Random Forest over Decision Tree

### Code & Documentation
- [x] All code on GitHub: https://github.com/rehanschaudhry/stock-ml-pipeline
- [x] Working scripts in `old_scripts/`:
  - `test_api.py` - API testing
  - `load_stock_to_postgres.py` - Data loading
  - `add_more_stocks.py` - Adding stocks
  - `feature_engineering_challenge.py` - Features
  - `first_ml_model.py` - ML model
- [x] README.md created
- [x] Requirements tracked

---

## 🚧 IN PROGRESS (TONIGHT)

### Python Refactoring - Week 1, Day 2
Project structure transformation:
```
stock-ml-pipeline/
├── config/
│   ├── __init__.py          [TODO - Tonight]
│   └── settings.py          [TODO - Tonight]
├── data/
│   ├── __init__.py          [TODO - Tonight]
│   ├── database.py          [TODO - Tonight - DatabaseManager class]
│   └── api_client.py        [TODO - Tonight - AlphaVantageClient class]
├── features/
│   ├── __init__.py          [TODO - Later]
│   └── engineering.py       [TODO - Later]
├── models/
│   ├── __init__.py          [TODO - Later]
│   └── trainer.py           [TODO - Later]
├── utils/
│   ├── __init__.py          [TODO - Later]
│   └── logger.py            [TODO - Later]
├── old_scripts/             [DONE - Archived working scripts]
├── main.py                  [TODO - Later]
├── requirements.txt
├── progress.md              [THIS FILE - Just created!]
└── README.md
```

**Tonight's Goals (1 hour):**
1. Create directory structure (10 min) ✅
2. Create `config/settings.py` (10 min)
3. Create `data/database.py` with DatabaseManager class (20 min)
4. Create `data/api_client.py` with AlphaVantageClient class (20 min)

---

## 📋 NEXT STEPS

### Immediate (Tonight - 1 hour)
1. ✅ Create progress.md
2. Create `config/settings.py` - centralize configuration
3. Create `data/database.py` - DatabaseManager class with UPSERT
4. Create `data/api_client.py` - AlphaVantageClient with rate limiting
5. Test both modules work
6. Commit everything to GitHub

### Rest of Week 1
- **Day 3 (1 hour):** Feature engineering module (`features/engineering.py`)
- **Day 4 (1 hour):** Model training module (`models/trainer.py`)
- **Day 5 (1 hour):** Main orchestration script (`main.py`), test everything
- **Weekend (3 hours):** Polish, documentation, Python practice problems

### Week 2 - Model Comparison
- Try XGBoost
- Try Logistic Regression
- Compare all 3 models
- Pick best one
- Document results

### Week 3-4 - Deployment
- FastAPI REST API
- Streamlit dashboard
- Basic deployment

### Week 5-8 - Airflow + Polish
- Airflow orchestration (KEY for MLOps roles!)
- Automated daily predictions
- Error handling & monitoring
- Portfolio-ready documentation

### Week 7+ - Job Applications
- Start applying (don't wait for perfect!)
- 20 applications/week
- Tailor resume for ML Engineer roles
- LinkedIn optimization

---

## 💡 TECHNICAL DECISIONS LOG

### Why Random Forest?
**Decision:** Use Random Forest as baseline model  
**Reasoning:**
- Easy to use, no feature scaling needed
- Shows feature importance (helps understand data)
- Handles non-linear relationships
- Good baseline before trying complex models
- Less prone to overfitting than single decision tree

### Why 80/20 Split (Not Cross-Validation)?
**Decision:** Use train_test_split with shuffle=False  
**Reasoning:**
- Time series data - must respect temporal order
- Cross-validation would mix past/future (data leakage!)
- 80/20 mimics real production: train on past, predict future
- Small dataset (50 samples after feature engineering) makes CV folds too small

### Why PostgreSQL?
**Decision:** Use PostgreSQL instead of CSV files  
**Reasoning:**
- Practice SQL skills (important for data roles)
- Production-ready database
- UPSERT logic prevents duplicates
- Scales better than flat files
- More impressive on resume

### Why Focus on Python (60/40 split)?
**Decision:** Learn Python deeply while building ML project  
**Reasoning:**
- Most ML candidates weak at Python fundamentals
- Strong coding = differentiation in interviews
- Python skills transferable to other roles
- Can learn deep ML concepts on the job
- Interview coding rounds test Python, not just ML theory

---

## 🤔 OPEN QUESTIONS / DECISIONS NEEDED

1. **Data validation:** Should we add validation before inserting to DB? (e.g., check for missing values, outliers)
2. **API rate limits:** How to handle in production? Current: 15 sec delay between calls
3. **Caching:** Should we cache API responses to avoid repeated calls?
4. **More data:** Should we switch to `outputsize="full"` for 20+ years of data?
5. **Second project:** Do we need manufacturing/IE project or is one amazing project enough?

---

## 📚 LEARNING FOCUS

### Python Topics (60% of time)
**Week 1-2: Fundamentals**
- [x] Variables, data types, functions
- [ ] Classes and OOP (IN PROGRESS - learning tonight!)
- [ ] Error handling - try/except, logging
- [ ] Type hints (`List[str]`, `Optional[int]`)
- [ ] Docstrings (Google style)
- [ ] Context managers (`with` statement)
- [ ] Module organization

**Week 3-4: Intermediate**
- [ ] List/dict comprehensions
- [ ] Decorators
- [ ] Testing with pytest
- [ ] Virtual environments
- [ ] Package management

**Week 5-8: Advanced**
- [ ] FastAPI framework
- [ ] Async/await
- [ ] API design patterns
- [ ] Production best practices

**Week 9+: Interview Prep**
- [ ] LeetCode Easy problems (target: 20-30 solved)
- [ ] String manipulation
- [ ] Array/List operations
- [ ] Dictionary operations
- [ ] Basic algorithms

### ML Topics (40% of time)
**Core Concepts:**
- [x] Train/test split ✅
- [x] Random Forest basics ✅
- [x] Feature engineering ✅
- [x] Feature importance ✅
- [ ] Model comparison (XGBoost, Logistic Regression)
- [ ] Evaluation metrics (precision, recall, F1, ROC-AUC)
- [ ] Overfitting vs underfitting
- [ ] Hyperparameter tuning (basic)

**When NOT to use techniques:**
- [x] Cross-validation ✅ (not for time series!)
- [ ] Feature scaling (when needed vs not)
- [ ] Deep learning (overkill for this problem)

---

## 🔧 TECHNICAL STACK

**Current:**
- Python 3.x
- PostgreSQL 17
- pandas, NumPy
- scikit-learn (RandomForestClassifier)
- psycopg2 (database)
- requests (API calls)

**To Add:**
- XGBoost
- FastAPI (deployment)
- Streamlit (dashboard)
- Airflow (orchestration)
- pytest (testing)
- logging (production)

---

## 🔗 IMPORTANT LINKS

- **GitHub Repo:** https://github.com/rehanschaudhry/stock-ml-pipeline
- **Alpha Vantage API Key:** KWKABB96U8N31TO4
- **Database:** localhost, stock_ml_db, user: postgres, password: 
- **UofT DSI Python Materials:** (will add when accessed)

---

## 📝 SESSION NOTES


### Session 1 (2024-11-26 Evening)
**Accomplished:**
- Built entire pipeline in one night! 🔥
- 17 stocks, 1,700 records loaded
- Feature engineering complete
- First ML model trained (60% accuracy)
- Learned Random Forest vs Decision Tree
- Understood 80/20 split for time series
- Decided on Python-focused approach (60/40)

**Key Learnings:**
- Random Forest = 100 decision trees voting (ensemble)
- Can't use cross-validation for time series (data leakage!)
- Feature importance shows momentum_5 most predictive (18.7%)
- Model needs more data (only 50 samples after features)

**Decisions Made:**
- ✅ Speed-focused plan (3-4 months)
- ✅ Learn Python deeply (60% time)
- ✅ ML basics (40% time) - learn rest on job
- ✅ One amazing project > two mediocre ones
- ✅ Start applying Week 7 (don't wait for perfect!)

### Session 2 (2024-11-26, Night) - COMPLETE! ✅

**Accomplished:**
- ✅ Created comprehensive configuration module (`config/settings.py`)
- ✅ Implemented environment variable security (`.env` + `.gitignore`)
- ✅ Changed database password for security
- ✅ Tested and validated - everything working!
- ✅ Learned: Classes, type hints, docstrings, environment variables, validation

**Python Concepts Learned:**
- Class-based configuration
- Type hints (Dict[str, str], List[str])
- Class methods (@classmethod)
- Docstrings (Google style)
- Environment variables (os.getenv, python-dotenv)
- Validation and error handling
- Singleton pattern
- Module testing (if __name__ == "__main__")

**Security Implemented:**
- .env file for secrets
- .gitignore to prevent commits
- python-dotenv for loading variables
- Database password changed
- Professional secret management

**Files Created:**
- config/settings.py ✅
- .env ✅
- .env.example ✅
- .gitignore ✅
- requirements.txt (updated) ✅

### This Week (Week 1)
- [x] **Day 1:** API integration + PostgreSQL (17 stocks, 1,700 records) ✅
- [x] **Day 1:** Feature engineering + First ML model (Random Forest, 60% accuracy) ✅
- [x] **Day 1:** Learned about Random Forest vs Decision Tree ✅
- [x] **Day 1:** Understood why 80/20 split for time series ✅
- [x] **Day 2:** Refactor into clean Python modules ✅
- [x] **Day 2:** Virtual environment setup ✅
- [x] **Day 2:** Security implementation (env vars) ✅


**Status:** Week 1, Day 2 COMPLETE! 🎉

### Working On NEXT
- **Task:** Create DatabaseManager class in `data/database.py`
- **Status:** Ready to start next session!
---

## 🎯 SUCCESS METRICS

**Week 4:**
- ✅ Clean, modular Python code
- ✅ Working ML pipeline end-to-end
- ✅ Can explain every line of code

**Week 8:**
- ✅ FastAPI deployment working
- ✅ Comfortable with Python fundamentals
- ✅ Can solve LeetCode Easy problems
- ✅ 20+ job applications sent

**Week 12:**
- ✅ Airflow orchestration complete
- ✅ Can solve LeetCode Easy-Medium
- ✅ 20-30 LeetCode problems solved
- ✅ 40+ applications sent
- ✅ 5+ phone screens

**Week 16:**
- ✅ Strong Python interview performance
- ✅ Can explain ML project confidently
- ✅ Multiple final round interviews
- ✅ 1-3 job offers
- ✅ $150K-$250K salary

---

## 💭 NOTES TO SELF

**Remember:**
- Don't wait for perfect - ship and iterate!
- Focus on Python fundamentals - this is my differentiator
- One amazing project > multiple mediocre ones
- Start applying Week 7 even if not "ready"
- 10 years experience is HUGE advantage over bootcamp grads
- I.E. degree + ML = unique positioning for manufacturing roles
- Speed > perfection (but quality > quantity)

**When feeling stuck:**
- Small progress > no progress
- Done > perfect
- Can always refactor later
- Learning happens through doing, not just reading

**Interview prep reminders:**
- Practice explaining project out loud
- "Walk me through your pipeline" - have 5-min version ready
- Know WHY you made each technical decision
- Be honest about what you don't know yet

---

## 🚀 HOW TO USE THIS FILE

**At START of each Claude conversation:**
```
Hi! Continuing ML job search project.

GitHub: rehanschaudhry/stock-ml-pipeline
Please read my progress.md file to see where we are.

Quick update:
- [What I completed since last time]
- [What I'm stuck on, if anything]  
- [What I want to work on today]

Let's continue!
```

**At END of each work session:**
```bash
# Update this file with progress
git add progress.md
git commit -m "Day X update: completed Y, next: Z"
git push
```

**When asking questions:**
- Reference specific sections of this file
- Mention what you've tried
- Claude will have full context!

---

**LAST UPDATED:** 2024-11-26, 11:30 PM  
**NEXT UPDATE:** After completing tonight's refactoring (DatabaseManager + AlphaVantageClient)