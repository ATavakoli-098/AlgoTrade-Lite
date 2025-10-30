from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
from backend.main import app

client = TestClient(app)

def _stub_df(n=200, seed=1):
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    price = 100 * (1 + pd.Series(np.random.default_rng(seed).normal(0.0002, 0.01, n), index=idx)).cumprod()
    return pd.DataFrame({"Open": price, "Close": price})

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_backtest_endpoint_stubbed(monkeypatch):
    import backend.api.routes as routes_mod
    def fake_fetch(symbol, start=None, end=None):
        return _stub_df()

    import backend.engine.data as data_mod
    monkeypatch.setattr(data_mod, "fetch_ohlc", fake_fetch)

    payload = {
        "symbol": "FAKE",
        "strategy": "sma_crossover",
        "params": {"fast": 5, "slow": 15},
        "cost_bps": 5,
        "slippage_bps": 2,
        "rf_rate_pct": 0.0
    }
    r = client.post("/backtest", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "summary" in body and "equity_curve" in body and "trades" in body
