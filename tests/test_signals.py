import pandas as pd
from backend.engine.strategies.sma import generate_signals_sma

def test_sma_signal_shapes_and_values():
    idx = pd.date_range("2020-01-01", periods=100, freq="B")
    close = pd.Series(range(100), index=idx).astype(float)
    df = pd.DataFrame({"Close": close})
    sig = generate_signals_sma(df, fast=5, slow=10)
    assert len(sig) == len(df)
    assert set(sig.unique()) <= {0, 1}

    assert sig.iloc[:10].sum() <= 1  # only small warm-up activity

