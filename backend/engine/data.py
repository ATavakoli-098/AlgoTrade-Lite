from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf


# ---------------------------------------------------------------------
# Local cache directory (.cache/)
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def _cache_path(symbol: str, interval: str) -> Path:
    """Return path for the symbol's cached parquet file."""
    fname = f"{symbol.replace('=', '_')}_{interval}.parquet"
    return CACHE_DIR / fname


def fetch_ohlc(
    symbol: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
    interval: str = "1d",
    force_download: bool = False,
) -> pd.DataFrame:
    """
    Fetch OHLCV data from yfinance and cache it locally in .cache/.
    """

    cache_file = _cache_path(symbol, interval)

    # Try cache first
    if cache_file.exists() and not force_download:
        df = pd.read_parquet(cache_file)
        if not df.empty:
            return df

    # Default range: 5 years
    if start is None or end is None:
        end = date.today()
        start = end - timedelta(days=5 * 365)

    data = yf.download(
        symbol,
        start=start,
        end=end,
        interval=interval,
        progress=False,
        auto_adjust=True,
        threads=True,
    )

    if data.empty:
        raise ValueError(f"No data for {symbol} ({start} to {end})")

    # Ensure columns are consistent
    data = data.rename(columns=str.capitalize)
    expected = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in data.columns for col in expected):
        raise ValueError(f"Downloaded data missing OHLC columns. Got: {list(data.columns)}")

    # Clean up index
    data = data.reset_index()
    if "Date" in data.columns:
        data = data.rename(columns={"Date": "Datetime"})
    data["Datetime"] = pd.to_datetime(data["Datetime"])
    data = data.set_index("Datetime").sort_index()

    # Cache it
    data.to_parquet(cache_file)

    return data


def get_price_series(symbol: str, **kwargs) -> pd.Series:
    """Shortcut: fetch OHLC and return Close only."""
    df = fetch_ohlc(symbol, **kwargs)
    return df["Close"].rename(symbol)
