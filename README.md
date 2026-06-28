# Trading Edge Analysis — 1,030 Live Trades

I've been trading a prop firm account for 8 months across Forex, 
Gold, Indices and Crypto. This project is my attempt to stop 
guessing and let the data tell me where I actually have edge.

**1,030 closed trades · 36 instruments · Oct 2025 – Jun 2026**

---

## The Question

Which instruments, sessions, and conditions produce consistent 
winning outcomes — and which ones are just noise?

---

## What I Found

- Metals (XAUUSD/XAGUSD) have the strongest edge at 55.9% win rate
- Wednesday and Thursday are my most consistent days
- Trading only high-edge instruments lifts win rate from 50.4% to 57%
- Holding trades longer than 1 day drops win rate to 27%

---

## What I Built

- `data/loader.py` — cleans the raw export and engineers features
- `notebooks/trading_analysis.ipynb` — full analysis with charts
- `sql/analysis.sql` — same analysis in PostgreSQL
- `sql/etl.py` — loads the data into a local database
- `dashboard/app.py` — interactive Streamlit dashboard with filters

---

## Stack

Python · Pandas · PostgreSQL · SQLAlchemy · Plotly · Streamlit · Jupyter

---

## Run It

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

---

*Neema Urassa · Finance Data Analyst*  
*[LinkedIn](https://www.linkedin.com/in/neema-urassa) · [GitHub](https://github.com/newissa1)*

