import pandas as pd
import numpy as np

def sma_crossover_signals(df: pd.DataFrame, fast: int = 10, slow: int = 30) -> pd.Series:
    if slow <= fast:
        raise ValueError("slow must be > fast")
    fast_ma = df["Close"].rolling(fast).mean()
    slow_ma = df["Close"].rolling(slow).mean()
    return (fast_ma > slow_ma).astype(int)

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1/period, adjust=False).mean()
    roll_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-12)
    return 100 - (100 / (1 + rs))

def rsi_band_signals(df: pd.DataFrame, period: int = 14, lower: float = 30, upper: float = 70) -> pd.Series:
    r = rsi(df["Close"], period)
    signal = pd.Series(index=df.index, dtype=int)
    signal.iloc[0] = 0
    for i in range(1, len(df)):
        if r.iloc[i] < lower:
            signal.iloc[i] = 1
        elif r.iloc[i] > upper:
            signal.iloc[i] = 0
        else:
            signal.iloc[i] = signal.iloc[i-1]
    return signal
