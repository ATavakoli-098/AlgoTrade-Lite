from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
from backend.main import app

client = TestClient(app)

def _stub_df(n=200, seed=0):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0002, 0.01, n)
    price = 100 * (1 + pd.Series(rets)).cumprod()
    df = pd.DataFrame({"Close": price})
    df.index = pd.date_range("2020-01-01", periods=n, freq="B")
    return df

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_backtest_endpoint_with_stub(monkeypatch):
    # patch the fetcher used INSIDE backend.main
    import backend.main as main_mod

    def fake_fetch(symbol, start=None, end=None, interval="1d"):
        return _stub_df()

    monkeypatch.setattr(main_mod, "fetch_ohlc", fake_fetch)

    payload = {
        "symbol": "FAKE",
        "strategy": "sma_crossover",
        "params": {"fast": 5, "slow": 20}
    }
    r = client.post("/backtest", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "metrics" in body and "equity_curve" in body
