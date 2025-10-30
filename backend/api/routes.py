from __future__ import annotations

import traceback
from fastapi import APIRouter, HTTPException
import pandas as pd

from backend.api.schemas import (
    BacktestRequest,
    BacktestResponse,
    BacktestSummary,
    Benchmarks,
    ConfigEcho,
    Trade,
)

router = APIRouter()


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest) -> BacktestResponse:
    """Main backtest endpoint with internal error handling for debugging."""

    try:
        # Lazy imports so we can pinpoint if a submodule fails
        from backend.engine.data import fetch_ohlc
        from backend.engine.strategies.sma import generate_signals_sma
        from backend.engine.backtester import simulate_long_only
        from backend.engine.metrics import compute_metrics, compute_buy_and_hold
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Import failed: {e}\n{tb}")

    # --- 1. Fetch data
    try:
        df = fetch_ohlc(req.symbol, start=req.start, end=req.end)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data fetch failed: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="No data returned for symbol.")

    # --- 2. Build signals
    try:
        if req.strategy == "sma_crossover":
            fast = int(req.params.get("fast", 10))
            slow = int(req.params.get("slow", 30))
            signal = generate_signals_sma(df, fast=fast, slow=slow)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported strategy: {req.strategy}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signal generation failed: {e}")

    # --- 3. Run backtest
    try:
        out = simulate_long_only(
            df,
            signal,
            cost_bps=req.cost_bps,
            slippage_bps=req.slippage_bps,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Backtest simulation failed: {e}")

    # --- 4. Compute metrics
    try:
        equity = pd.Series(out.equity_curve, index=df.index[: len(out.equity_curve)])
        metrics = compute_metrics(equity, rf_rate_pct=req.rf_rate_pct)
        bh_return = compute_buy_and_hold(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Metrics computation failed: {e}")

    summary = BacktestSummary(**metrics, trades=len(out.trades))

    # --- 5. Build response
    return BacktestResponse(
        summary=summary,
        equity_curve=out.equity_curve,
        trades=[Trade(**t) for t in out.trades],
        benchmarks=Benchmarks(
            buy_and_hold_return_pct=bh_return,
            rf_rate_pct=req.rf_rate_pct,
            reference_symbol=req.symbol,
        ),
        config=ConfigEcho(
            symbol=req.symbol,
            start=str(req.start) if req.start else None,
            end=str(req.end) if req.end else None,
            strategy=req.strategy,
            params=req.params,
            cost_bps=req.cost_bps,
            slippage_bps=req.slippage_bps,
            rf_rate_pct=req.rf_rate_pct,
        ),
    )
