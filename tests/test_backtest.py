import pandas as pd
import numpy as np
from backend.engine.backtester import run_backtest

def toy_prices(n=300, drift=0.0003, vol=0.01, seed=42):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    price = 100 * (1 + pd.Series(rets)).cumprod()
    return pd.DataFrame({"Close": price})

def test_sma_runs():
    df = toy_prices()
    out = run_backtest(df, "sma_crossover", {"fast": 5, "slow": 20})
    assert "return_pct" in out.metrics
    assert out.equity_curve.iloc[-1] > 0

def test_rsi_runs():
    df = toy_prices()
    out = run_backtest(df, "rsi", {"period": 14, "lower": 30, "upper": 70})
    assert "sharpe" in out.metrics
