from pydantic import BaseModel, Field
from typing import Dict, Optional, Literal
from datetime import date

StrategyName = Literal["sma_crossover", "rsi"]

class BacktestRequest(BaseModel):
    symbol: str = Field(..., examples=["AAPL", "EURUSD=X"])
    start: Optional[date] = None
    end: Optional[date] = None
    strategy: StrategyName
    params: Dict[str, float] = {}

class BacktestResult(BaseModel):
    symbol: str
    strategy: str
    params: Dict[str, float]
    start: Optional[str]
    end: Optional[str]
    metrics: Dict[str, float]
    n_trades: int
    equity_curve: Optional[list] = None
