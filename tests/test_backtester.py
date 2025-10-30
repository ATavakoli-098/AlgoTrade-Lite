import numpy as np
import pandas as pd
from backend.engine.backtester import simulate_long_only

def make_df(n=200):
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    price = 100 * (1 + pd.Series(np.random.normal(0.0002, 0.01, n), index=idx)).cumprod()
    return pd.DataFrame({"Open": price, "Close": price})

def test_simulate_long_only_runs():
    df = make_df()
    sig = pd.Series(0, index=df.index)
    sig.iloc[20:100] = 1
    out = simulate_long_only(df, sig, cost_bps=5, slippage_bps=2)
    assert len(out.equity_curve) == len(df)
    assert isinstance(out.trades, list)
    # at least one entry and one exit
    sides = {t["side"] for t in out.trades}
    assert sides >= {"buy", "sell"}
