from __future__ import annotations

from datetime import date
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---- Strategy enum -----------------------------------------------------------
StrategyName = Literal["sma_crossover", "rsi"]


# ---- Request ----------------------------------------------------------------
class BacktestRequest(BaseModel):
    """
    Input contract for POST /backtest
    """
    symbol: str = Field(..., examples=["AAPL", "MSFT", "EURUSD=X"])
    start: Optional[date] = Field(None, description="Inclusive start date (YYYY-MM-DD)")
    end: Optional[date] = Field(None, description="Exclusive end date (YYYY-MM-DD)")
    strategy: StrategyName
    params: Dict[str, float] = Field(
        default_factory=dict,
        description="Strategy-specific params e.g. {'fast':10,'slow':30} or {'period':14,...}",
    )

    # Trading frictions / config
    cost_bps: float = Field(0.0, ge=0, description="Per trade cost in basis points (0.05% = 5)")
    slippage_bps: float = Field(0.0, ge=0, description="Assumed slippage in bps applied on fills")
    rf_rate_pct: float = Field(
        0.0, description="Annualized risk-free rate in percent (e.g. 3.5 for 3.5%)"
    )

    @field_validator("end")
    @classmethod
    def _validate_dates(cls, v: Optional[date], info):
        start = info.data.get("start")
        if v and start and v <= start:
            raise ValueError("end must be after start (note: end is exclusive).")
        return v


# ---- Trade log item ----------------------------------------------------------
class Trade(BaseModel):
    ts: str = Field(..., description="Timestamp (ISO 8601) of execution")
    side: Literal["buy", "sell"] = Field(..., description="Trade side")
    price: float = Field(..., ge=0)
    qty: float = Field(..., gt=0)
    fees: float = Field(0.0, ge=0, description="Transaction cost paid on this fill")
    slippage: float = Field(0.0, ge=0, description="Slippage cost realized on this fill")


# ---- Summary metrics ---------------------------------------------------------
class BacktestSummary(BaseModel):
    ann_return_pct: float
    ann_vol_pct: float
    sharpe: float
    max_drawdown_pct: float
    win_rate_pct: Optional[float] = None
    trades: int


# ---- Benchmarks --------------------------------------------------------------
class Benchmarks(BaseModel):
    buy_and_hold_return_pct: float
    rf_rate_pct: float = 0.0  # echo what was used
    reference_symbol: Optional[str] = None  # usually same as request symbol


# ---- Echo of config used (handy for reproducibility) ------------------------
class ConfigEcho(BaseModel):
    symbol: str
    start: Optional[str] = None
    end: Optional[str] = None
    strategy: StrategyName
    params: Dict[str, float]
    cost_bps: float
    slippage_bps: float
    rf_rate_pct: float


# ---- Response ----------------------------------------------------------------
class BacktestResponse(BaseModel):
    summary: BacktestSummary
    equity_curve: List[float] = Field(..., description="Cumulative equity series, 1.0 = start")
    trades: List[Trade] = Field(default_factory=list)
    benchmarks: Benchmarks
    config: ConfigEcho
