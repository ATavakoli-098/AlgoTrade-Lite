# AlgoTrade Lite

![CI](https://github.com/ATavakoli-098/AlgoTrade-Lite/actions/workflows/ci.yml/badge.svg)

> **Status:** MVP complete — FastAPI backend + backtesting engine with tests & CI.

---

## Overview
**AlgoTrade Lite** is a lightweight algorithmic trading backtesting framework designed to demonstrate data handling, API integration, and financial computation skills.

It features a clean FastAPI backend capable of fetching market data, running trading strategies, computing performance metrics, and returning results via JSON or dashboard integration.

---

## Features
- FastAPI backend with `/backtest` endpoint
- SMA crossover strategy (next-bar execution, costs, slippage)
- Data fetched via `yfinance` and cached locally
- Performance metrics: annual return, volatility, Sharpe, drawdown, win rate
- Unit tests and GitHub Actions CI workflow

---

## Example API Request
```bash
POST /backtest
Content-Type: application/json
```

```json
{
  "symbol": "AAPL",
  "strategy": "sma_crossover",
  "params": {"fast": 10, "slow": 30},
  "cost_bps": 5,
  "slippage_bps": 2,
  "rf_rate_pct": 3.0
}
```

---

## Project Layout
```
backend/
 ├── api/
 │    ├── routes.py
 │    └── schemas.py
 ├── engine/
 │    ├── data.py
 │    ├── metrics.py
 │    ├── backtester.py
 │    └── strategies/
 │         └── sma.py
tests/
 ├── test_backtester.py
 ├── test_metrics.py
 ├── test_signals.py
 └── test_api.py
.github/workflows/
 └── ci.yml
```

---

## Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend
uvicorn backend.main:app --reload

# Run tests
pytest -q
```

---

## Next Steps
- Add Streamlit dashboard for visualization  
- Add RSI mean-reversion strategy  
- Deploy API on Render or Railway
