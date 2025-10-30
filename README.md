# AlgoTrade Lite

A minimal backtesting tool that proves I can handle data, APIs, and financial metrics.

---

## What it does
- Fetches stock/FX data (yfinance)
- Runs strategies (SMA crossover, RSI)
- Reports metrics: Return %, Sharpe ratio, Max Drawdown
- Visualizes results in a small Streamlit app
- Exposes a clean FastAPI `/backtest` endpoint

---

## Stack
- **Backend:** FastAPI, Pydantic
- **Data/Compute:** pandas, numpy, scipy, yfinance
- **UI:** Streamlit
- **Tests:** pytest + GitHub Actions CI

---

## Run locally

```bash
# create venv and install
python -m venv .venv
# Windows:
. .venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt

# start backend
uvicorn backend.main:app --reload

# (new terminal) start dashboard
streamlit run dashboard/app.py
```
---

### Example API request

```bash
curl -X POST http://127.0.0.1:8000/backtest \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","strategy":"sma_crossover","params":{"fast":10,"slow":30,"cost_bps":5}}'
```

---

## Project layout
```bash
algotrade/
  backend/
    main.py
    models.py
    engine/
      data.py
      strategies.py
      metrics.py
      backtester.py
  dashboard/
    app.py
  tests/
  requirements.txt
  README.md
```
---

## Notes
```bash
-#end is exclusive in yfinance. Omit dates to fetch ~5y.

-#Optional param: "cost_bps": <int> to model trade costs (bps per entry/exit).
```
---
