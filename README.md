# Stock Market ML Pipeline

## Status: Phase 1 COMPLETE ✅

### What's Working (Day 1):
- ✅ Alpha Vantage API integration
- ✅ PostgreSQL database (stock_ml_db)
- ✅ Automated data extraction and loading
- ✅ 9 tech stocks tracked (NVDA, IBM, TSLA, INTC, AAPL, GOOGL, META, MSFT, AMZN)
- ✅ 900 records (100 days × 9 stocks)

### Tech Stack:
- **API:** Alpha Vantage
- **Database:** PostgreSQL 17
- **Languages:** Python, SQL
- **Libraries:** requests, pandas, psycopg2

### Data Schema:
```sql
stock_prices (
  id, symbol, date, open, high, low, close, volume, created_at
)
```

### Next Steps:
- [ ] Add NFLX (correct ticker)
- [ ] Feature engineering (technical indicators)
- [ ] SQL analytics queries
- [ ] ML models for forecasting
- [ ] Airflow orchestration
