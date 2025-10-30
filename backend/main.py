from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import BacktestRequest, BacktestResult
from .engine.data import fetch_ohlc
from .engine.backtester import run_backtest

app = FastAPI(title="AlgoTrade Lite", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/backtest", response_model=BacktestResult)
def backtest(req: BacktestRequest):
    try:
        df = fetch_ohlc(req.symbol, start=req.start, end=req.end)
        bt = run_backtest(df, req.strategy, req.params or {})
        equity_list = [float(x) for x in bt.equity_curve.round(6).tolist()]
        return BacktestResult(
            symbol=req.symbol,
            strategy=req.strategy,
            params=req.params or {},
            start=str(df.index[0].date()),
            end=str(df.index[-1].date()),
            metrics=bt.metrics,
            n_trades=bt.n_trades,
            equity_curve=equity_list,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
