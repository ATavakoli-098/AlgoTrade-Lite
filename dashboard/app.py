import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="AlgoTrade Lite", layout="wide")
st.title("AlgoTrade Lite")

with st.form("backtest"):
    c1, c2, c3 = st.columns(3)

    with c1:
        symbol = st.text_input("Symbol", "AAPL")
        strategy = st.selectbox("Strategy", ["sma_crossover", "rsi"])

    with c2:
        start = st.text_input("Start date (YYYY-MM-DD)", "")
        end = st.text_input("End date (YYYY-MM-DD)", "")

    with c3:
        params = {}
        if strategy == "sma_crossover":
            params["fast"] = st.number_input("fast", min_value=2, max_value=400, value=10, step=1)
            params["slow"] = st.number_input("slow", min_value=3, max_value=500, value=30, step=1)
        else:
            params["period"] = st.number_input("period", min_value=5, max_value=100, value=14, step=1)
            params["lower"] = st.number_input("lower", min_value=5, max_value=50, value=30, step=1)
            params["upper"] = st.number_input("upper", min_value=50, max_value=95, value=70, step=1)

        # optional trading cost in bps (0.05% = 5 bps)
        params["cost_bps"] = st.number_input("cost_bps (per trade)", min_value=0, max_value=200, value=0, step=1)

    submitted = st.form_submit_button("Run backtest")

if submitted:
    payload = {"symbol": symbol, "strategy": strategy, "params": params}
    if start.strip():
        payload["start"] = start.strip()
    if end.strip():
        payload["end"] = end.strip()

    with st.spinner("Running backtest..."):
        try:
            r = requests.post(f"{API}/backtest", json=payload, timeout=60)
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    if not r.ok:
        st.error(r.text)
        st.stop()

    data = r.json()

    # ---- Metrics summary ----
    st.subheader("Metrics")
    m = data["metrics"]
    cols = st.columns(5)
    cols[0].metric("Return %", m["return_pct"])
    cols[1].metric("Sharpe", m["sharpe"])
    cols[2].metric("Max DD %", m["max_drawdown_pct"])
    cols[3].metric("Trades", data["n_trades"])
    cols[4].write(f"**Period:** {data['start']} → {data['end']}")

    # ---- Equity curve plot ----
    eq = pd.Series(data["equity_curve"])
    fig = plt.figure()
    plt.plot(eq.index, eq.values)
    plt.title("Equity Curve")
    plt.xlabel("Bars")
    plt.ylabel("Equity")
    st.pyplot(fig)

    # ---- Price + indicator plot (for SMA only) ----
    if strategy == "sma_crossover":
        # fetch for visualization only (backend already did the official calc)
        if not (start.strip() or end.strip()):
            hist = yf.Ticker(symbol).history(period="5y", auto_adjust=True, actions=False)
        else:
            hist = yf.Ticker(symbol).history(start=start or None, end=end or None, auto_adjust=True, actions=False)

        if not hist.empty and "Close" in hist.columns:
            fast = int(params.get("fast", 10))
            slow = int(params.get("slow", 30))
            fast_ma = hist["Close"].rolling(fast).mean()
            slow_ma = hist["Close"].rolling(slow).mean()

            st.subheader("Price with Moving Averages")
            fig2 = plt.figure()
            plt.plot(hist.index, hist["Close"].values, label="Close")
            plt.plot(hist.index, fast_ma.values, label=f"MA {fast}")
            plt.plot(hist.index, slow_ma.values, label=f"MA {slow}")
            plt.legend()
            plt.xlabel("Date")
            plt.ylabel("Price")
            st.pyplot(fig2)
        else:
            st.info("Could not fetch price history for the MA overlay.")
