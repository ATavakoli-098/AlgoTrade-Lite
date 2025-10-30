from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd


@dataclass
class BacktestOutput:
    equity_curve: List[float]           # cumulative equity, starts at 1.0
    trades: List[Dict]                  # list of trade dicts (ts, side, price, qty, fees, slippage)


def _validate_inputs(df: pd.DataFrame, signal: pd.Series) -> None:
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Price dataframe index must be a DatetimeIndex.")
    if "Close" not in df.columns:
        raise ValueError("Price dataframe must contain a 'Close' column.")
    if not signal.index.equals(df.index):
        # try auto-align (common if user built signal from another copy)
        signal.index = pd.DatetimeIndex(signal.index)
        if not signal.index.equals(df.index):
            # last try: reindex to df and forward-fill
            signal = signal.reindex(df.index).fillna(method="ffill").fillna(0)
    if signal.isna().any():
        raise ValueError("Signal contains NaNs after alignment.")
    bad_vals = set(signal.unique()) - {0, 1}
    if bad_vals:
        raise ValueError(f"Signal must be binary {0,1}. Found values: {bad_vals}")


def simulate_long_only(
    df: pd.DataFrame,
    signal: pd.Series,
    cost_bps: float = 0.0,
    slippage_bps: float = 0.0,
) -> BacktestOutput:
    """
    Long-only backtest with next-bar execution and per-trade frictions.

    - Positions are 1 (long) or 0 (flat).
    - Execution: signal decided at bar t-1 is executed on bar t (next bar) -> we use signal.shift(1).
    - Costs/slippage: applied when signal changes (entry or exit); modeled as a negative return of
      (cost_bps + slippage_bps)/10000 on that execution bar.
    - Equity starts at 1.0. Qty for trade log is 1.0 (notionalized); prices are from 'Open' if available, else 'Close'.
    """
    signal = signal.astype(int)
    _validate_inputs(df, signal)

    # core returns
    r_close = df["Close"].pct_change().fillna(0.0)
    pos = signal.shift(1).fillna(0).astype(int)  # next-bar execution -> previous signal applies
    gross = r_close * pos

    # frictions on *changes* in signal (entries/exits)
    turnover = signal.diff().abs().fillna(0.0)  # 1 at entry/exit, else 0
    fric = (cost_bps + slippage_bps) / 10000.0
    net = gross - turnover * fric

    equity = (1.0 + net).cumprod()

    # ---- trade log (at next-bar open if available, else close) ----
    opens = df["Open"] if "Open" in df.columns else df["Close"]
    changes = signal.diff().fillna(0.0)
    trades: List[Dict] = []
    for ts, ch in changes.items():
        if ch == 0:
            continue
        side = "buy" if ch == 1 else "sell"
        price = float(opens.loc[ts])
        trade = {
            "ts": ts.isoformat(),
            "side": side,
            "price": price,
            "qty": 1.0,                               # notionalized
            "fees": round(cost_bps / 10000.0, 8),     # as fraction of equity
            "slippage": round(slippage_bps / 10000.0, 8),
        }
        trades.append(trade)

    return BacktestOutput(
        equity_curve=[float(x) for x in equity.tolist()],
        trades=trades,
    )
