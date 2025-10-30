from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(
    equity: pd.Series,
    rf_rate_pct: float = 0.0,
    freq: str = "D",
) -> dict:
    """
    Compute standard performance metrics for an equity curve.
    - equity: cumulative equity (starts at 1)
    - rf_rate_pct: annualized risk-free rate (e.g. 3.5)
    - freq: 'D' for daily, 'M' for monthly data
    """
    if not isinstance(equity, pd.Series):
        equity = pd.Series(equity)

    equity = equity.dropna()
    if equity.empty:
        raise ValueError("Equity series is empty.")

    rets = equity.pct_change().dropna()
    if rets.empty:
        raise ValueError("Not enough data for metrics.")

    # Determine periods per year
    periods_per_year = {"D": 252, "M": 12}.get(freq.upper(), 252)
    rf_rate = rf_rate_pct / 100.0

    # Annualized return and vol
    ann_return = (1 + rets.mean()) ** periods_per_year - 1
    ann_vol = rets.std() * np.sqrt(periods_per_year)

    # Sharpe ratio (risk-free adjustment)
    excess = rets - rf_rate / periods_per_year
    sharpe = np.sqrt(periods_per_year) * excess.mean() / (excess.std() + 1e-12)

    # Max drawdown
    roll_max = equity.cummax()
    dd = equity / roll_max - 1
    max_dd = dd.min()

    # Win rate (% of positive returns)
    win_rate = (rets > 0).mean() * 100

    return {
        "ann_return_pct": float(round(ann_return * 100, 2)),
        "ann_vol_pct": float(round(ann_vol * 100, 2)),
        "sharpe": float(round(sharpe, 2)),
        "max_drawdown_pct": float(round(max_dd * 100, 2)),
        "win_rate_pct": float(round(win_rate, 2)),
    }


def compute_buy_and_hold(df: pd.DataFrame) -> float:
    """Return total % return of buy-and-hold."""
    if "Close" not in df.columns:
        raise ValueError("Data must have 'Close' column for benchmark.")
    start, end = df["Close"].iloc[0], df["Close"].iloc[-1]
    return float(round((end / start - 1) * 100, 2))
    return round((end / start - 1) * 100, 2)

