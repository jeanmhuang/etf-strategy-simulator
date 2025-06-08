
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="ETF Risk & Return Dashboard", layout="wide")

st.title("📈 ETF Risk & Return Dashboard")
st.markdown("Compare performance, volatility, and drawdowns of major ETFs since 2018.")

etfs = {
    "S&P 500 (SPY)": "SPY",
    "Nasdaq 100 (QQQ)": "QQQ",
    "Gold (GLD)": "GLD",
    "Long-Term Bonds (TLT)": "TLT",
    "Small Caps (IWM)": "IWM"
}

selected_etfs = st.multiselect("Select ETFs to compare:", list(etfs.keys()), default=list(etfs.keys()))

start_date = "2018-01-01"
end_date = pd.Timestamp.today().strftime("%Y-%m-%d")
data = yf.download([etfs[name] for name in selected_etfs], start=start_date, end=end_date, auto_adjust=True)["Close"]

# Drop rows with missing values
data.dropna(inplace=True)

# Calculate normalized price, cumulative returns, and drawdowns
norm_data = data / data.iloc[0]
returns = data.pct_change().dropna()
cumulative_returns = (1 + returns).cumprod()
volatility = returns.std() * np.sqrt(252)
drawdowns = (data / data.cummax()) - 1
max_drawdown = drawdowns.min()

# Line chart of normalized price
st.subheader("📉 Cumulative Performance")
fig = px.line(norm_data, title="Normalized Price (Since 2018)")
st.plotly_chart(fig, use_container_width=True)

# Scatter plot: Return vs Volatility
summary_df = pd.DataFrame({
    "Return": cumulative_returns.iloc[-1],
    "Volatility": volatility,
    "Max Drawdown": max_drawdown
})
summary_df = summary_df.rename(index={v: k for k, v in etfs.items() if v in summary_df.index})

st.subheader("📊 Risk vs Return")
fig2 = px.scatter(summary_df, x="Volatility", y="Return", text=summary_df.index,
                  size=[abs(x) for x in max_drawdown], title="Return vs. Volatility (Bubble = Max Drawdown)",
                  labels={"Volatility": "Volatility (Annualized)", "Return": "Total Return"})
st.plotly_chart(fig2, use_container_width=True)

# Drawdown chart
st.subheader("📉 Rolling Drawdowns")
fig3 = px.line(drawdowns, title="Drawdowns Since Peak")
st.plotly_chart(fig3, use_container_width=True)
