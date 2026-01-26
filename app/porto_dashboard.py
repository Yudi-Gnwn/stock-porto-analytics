from optparse import Values
from turtle import title, window_height
from altair.theme import names
import streamlit as st, yfinance as yf, quantstats as qs, pandas as pd, plotly.express as px
import tempfile, os

def main():
    st.set_page_config(page_title="Portofolio Analytics Dashboard", layout="wide")
    st.title("Portofolio Analytics Dashboard")

    st.sidebar.header("Portofolio Configuration")

    nse_ticker = [ "RELIANCE.NS", "HDFCBANK.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", 
                    "LT.NS", "KOTAKBANK.NS", "SBIN.NS", "HCLTECH.NS", "ITC.NS"]

    tickers = st.sidebar.multiselect(
        "Select NSE Stock", options=nse_ticker, default=["LT.NS", "TCS.NS", "INFY.NS", "ITC.NS"]
    )

    weights = []

    if tickers:
        st.sidebar.markdown("### Assign portofolio weights")
        for i in tickers:
            w = st.sidebar.slider(f"Weight for {i}", min_value=0.0, max_value=1.0, value=round(1/len(tickers), 2), step=0.01)
            weights.append(w)
        total = sum(weights)
        if total != 1 and total != 0:
            weights = (w / total for w in weights)

    # sidebar tanggal terpisah
    # start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2025-01-02"))
    # end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

    # sidebar tanggal nyatu
    start_date, end_date = st.sidebar.date_input(
        "Select date range: ", value=(pd.to_datetime("2022-01-01"), pd.to_datetime("today"))
    )

    generate_btn = st.sidebar.button("Generate Analysis")

    # Logic
    if generate_btn:
        if not tickers:
            st.error("Silahkan pilih minimal satu saham.")
            st.stop()
        if len(tickers) != len(weights):
            st.error("ticker and wight missmatch.")
            st.stop()

        with st.spinner("Mengambil data & Melakukan Analisis..."):
            price_data = yf.download(tickers, start=start_date, end=end_date)["Close"]
            returns = price_data.pct_change().dropna()

            portofolio_returns = (returns * weights).sum(axis=1)
            qs.extend_pandas()

            # Display matrix
            st.subheader("Key Matrix")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Sharpe Ratio", f"{qs.stats.sharpe(portofolio_returns):.2f}")
            col2.metric("Max Drawdown", f"{qs.stats.max_drawdown(portofolio_returns)*100:.2f}%")
            col3.metric("CAGR", f"{qs.stats.cagr(portofolio_returns)*100:.2f}%")
            col4.metric("Volatility", f"{qs.stats.volatility(portofolio_returns)*100:.2f}%")

            st.subheader("Portofolio Weight")
            fig_pie = px.pie(
                names=tickers,
                values=weights,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="Portofolio Allocation")
            st.plotly_chart(fig_pie, use_container_width=True)

            # mothly return
            st.subheader("Montly return heatmap")
            st.dataframe(portofolio_returns.monthly_returns().style.format("{:.2%}"))

            # cumulative returns plot
            st.subheader("cumulative returns")
            st.line_chart((1 + portofolio_returns).cumprod())

            # End of year returns chart
            st.subheader("End-of-year returns")
            eoy_returns = portofolio_returns.resample('Y').apply(lambda x: (x + 1).prod() - 1)
            st.bar_chart(eoy_returns)

            # generate HTML report
            with tempfile.TemporaryDirectory() as tmpdir:
                report_path = os.path.join(tmpdir, "portofolio_report.html")
                qs.reports.html(portofolio_returns, output=report_path, title="Portofolio performance report")
                with open(report_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                st.download_button(
                    label="Download Full report",
                    data=html_content,
                    file_name="portofolio_report.html",
                    mime="text/html"
                )
        st.success("Analisis berhasil!, Explore your portofolio metric above.")

# run
if __name__ == "__main__":
    main()
