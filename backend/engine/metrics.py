import numpy as np
import pandas as pd

def compute_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().fillna(0.0)

def equity_curve(returns: pd.Series) -> pd.Series:
    return (1 + returns).cumprod()

def sharpe_ratio(returns: pd.Series, periods_per_year: int = 252, risk_free: float = 0.0) -> float:
    excess = returns - (risk_free / periods_per_year)
    std = excess.std()
    if std == 0 or np.isnan(std):
        return 0.0
    return (excess.mean() / std) * np.sqrt(periods_per_year)

def max_drawdown(equity: pd.Series) -> float:
    peaks = equity.cummax()
    dd = (equity / peaks) - 1.0
    return float(dd.min())  # negative
