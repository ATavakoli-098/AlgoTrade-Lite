import pandas as pd
import yfinance as yf
from typing import Optional
from datetime import date

STD_FIELDS = ["Open", "High", "Low", "Close", "Volume"]

def _force_ohlcv_order(cols_len: int):
    # yfinance.history default order is: Open, High, Low, Close, Volume, (Dividends, Stock Splits)
    return STD_FIELDS[: min(cols_len, 5)]

def _normalize(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        # If multiindex, prefer the level that contains OHLC names
        level0 = set(map(str, df.columns.get_level_values(0)))
        level1 = set(map(str, df.columns.get_level_values(1)))
        if set(STD_FIELDS) & level0:
            df.columns = [str(c).title() for c in df.columns.get_level_values(0)]
        elif set(STD_FIELDS) & level1:
            df.columns = [str(c).title() for c in df.columns.get_level_values(1)]
        else:
            # fall back to first level
            df = df.droplevel(0, axis=1)

    # Flatten simple columns
    df.columns = [str(c).strip().title() for c in df.columns]

    # Edge case: all columns named the ticker (e.g., ['Aapl', 'Aapl', ...])
    uniq = {c.lower() for c in df.columns}
    if len(uniq) == 1 and (symbol.lower() in uniq or list(uniq)[0] in {symbol.lower()}):
        df.columns = _force_ohlcv_order(df.shape[1])

    # If still no Close, try Adj Close, else fail
    if "Close" not in df.columns:
        if "Adj Close" in df.columns:
            df["Close"] = df["Adj Close"]
        else:
            raise ValueError(f"Downloaded data has no 'Close' column. Got: {list(df.columns)}")

    # Keep just the standard fields we have
    keep = [c for c in STD_FIELDS if c in df.columns]
    df = df[keep].copy()
    return df.dropna(subset=["Close"])

def fetch_ohlc(
    symbol: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
    interval: str = "1d",
) -> pd.DataFrame:
    tk = yf.Ticker(symbol)
    if start is None and end is None:
        # get enough bars for MAs/RSI to actually warm up
        df = tk.history(period="5y", interval=interval, auto_adjust=True, actions=False)
    else:
        df = tk.history(start=start, end=end, interval=interval, auto_adjust=True, actions=False)

    if df is None or df.empty:
        df = yf.download(
            symbol,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,
            progress=False,
            group_by="column",
        )
    if df is None or df.empty:
        raise ValueError(f"No data returned for {symbol}.")
    return _normalize(df, symbol)

