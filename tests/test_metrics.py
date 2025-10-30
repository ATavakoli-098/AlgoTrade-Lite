import numpy as np
import pandas as pd
from backend.engine.metrics import compute_metrics

def test_compute_metrics_basic():
    eq = pd.Series(np.linspace(1, 1.5, 252))
    m = compute_metrics(eq, rf_rate_pct=0.0)
    for k in ["ann_return_pct","ann_vol_pct","sharpe","max_drawdown_pct","win_rate_pct"]:
        assert k in m
        assert isinstance(m[k], float)
