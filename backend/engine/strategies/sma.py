from __future__ import annotations

import pandas as pd


def add_sma(df: pd.DataFrame, fast: int, slow: int) -> pd.DataFrame:
    """
    Adds SMA_fast and SMA_slow columns to a copy of df.
    Expects df with a 'Close' column and DatetimeIndex.
    """
    if "Close" not in df.columns:
        raise ValueError("Dataframe must contain 'Close' column.")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Index must be a DatetimeIndex (got %r)" % type(df.index))

    if fast < 1 or slow < 1:
        raise ValueError("fast/slow windows must be >= 1.")
    if slow <= fast:
        raise ValueError("slow must be strictly greater than fast.")

    out = df.copy()
    out["SMA_fast"] = out["Close"].rolling(int(fast)).mean()
    out["SMA_slow"] = out["Close"].rolling(int(slow)).mean()
    return out


def generate_signals_sma(df: pd.DataFrame, fast: int, slow: int) -> pd.Series:
    """
    Long-only SMA crossover signal:
      1 when SMA_fast > SMA_slow, else 0.
    NOTE: This returns the *signal state per bar*. To avoid look-ahead,
    execute trades on the NEXT bar (i.e., shift the signal by 1 when applying).
    """
    df_sma = add_sma(df, fast=fast, slow=slow)

    # Signal: hold long while fast above slow
    signal = (df_sma["SMA_fast"] > df_sma["SMA_slow"]).astype(int)

    # Warm-up region (before SMAs exist) -> flat
    signal = signal.where(df_sma[["SMA_fast", "SMA_slow"]].notna().all(axis=1), other=0)

    signal.name = "signal"
    return signal
