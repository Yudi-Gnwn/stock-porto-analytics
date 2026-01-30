import streamlit as st
import yfinance as yf
import quantstats as qs
import pandas as pd
import plotly.express as px
import tempfile
import os


def main():
    # Konfig Halaman Streamlit
    st.set_page_config(
        page_title="Portofolio Analytics Dashboard", 
        layout="wide"
    )
    st.title("Portofolio Analytics Dashboard")

    st.sidebar.header("Portofolio Configuration")

    # Daftar Saham US
    us_ticker = [ 
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", 
        "META", "TSLA", "JPM", "V", "BRK-B"
    ]

    # Pilih saham 
    tickers = st.sidebar.multiselect(
        "Select US Stock",
        options=us_ticker,
        default=["AAPL", "AMZN", "TSLA", "BRK-B"]
    )

    # Input bobot portofolio
    weights = []

    if tickers:
        st.sidebar.markdown("### Assign portofolio weights")

        # slider 
        for ticker in tickers:
            weight = st.sidebar.slider(
                f"Weight for {ticker}",
                min_value=0.0,
                max_value=1.0,
                value=round(1 / len(tickers), 2),
                step=0.01
            )
            weights.append(weight)

        # Normalisasi bobot agar total = 1
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]

    # Input range tanggal
    start_date, end_date = st.sidebar.date_input(
        "Select date range: ",
        value=(pd.to_datetime("2024-01-01"), pd.to_datetime("today"))
    )

    generate_btn = st.sidebar.button("Generate Analysis")

    # Logic
    if generate_btn:

        # Validasi input
        if not tickers:
            st.error("Please select at least one stock.")
            st.stop()

        if len(tickers) != len(weights):
            st.error("ticker and wight missmatch.")
            st.stop()

        with st.spinner("Taking Data & Performing Analysis..."):

            # Ambil harga penutupan
            price_data = yf.download(
                tickers,
                start=start_date,
                end=end_date
            )["Close"]

            # Hitung return harian
            returns = price_data.pct_change().dropna()

            # Hitung return portofolio
            portofolio_returns = (returns * weights).sum(axis=1)

            # Extend quantstats ke pandas
            qs.extend_pandas()


            # ----------------------
            # Matrix Utama
            st.subheader("Key Matrix")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Sharpe Ratio",
                f"{qs.stats.sharpe(portofolio_returns):.2f}")

            col2.metric(
                "Max Drawdown",
                f"{qs.stats.max_drawdown(portofolio_returns)*100:.2f}%")

            col3.metric(
                "CAGR",
                f"{qs.stats.cagr(portofolio_returns)*100:.2f}%")

            col4.metric(
                "Volatility",
                f"{qs.stats.volatility(portofolio_returns)*100:.2f}%")

            # Alokasi portofolio (pie chart)
            st.subheader("Portofolio Allocation")
            
            fig_pie = px.pie(
                names=tickers,
                values=weights,
            )
            fig_pie.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_pie, width="stretch")

            # Heatmap return bulanan
            st.subheader("Montly Return Heatmap")
            st.dataframe(
                portofolio_returns
                .monthly_returns()
                .style.format("{:.2%}")
            )

            # Cumulative returns
            st.subheader("Cumulative Returns")
            st.line_chart((1 + portofolio_returns).cumprod())

            # Return Tahunan
            st.subheader("End-of-Year Returns")
            yearly_returns = portofolio_returns.resample('YE').apply(
                lambda x: (x + 1).prod() - 1
            )
            st.bar_chart(yearly_returns)

            # Generate laporan HTMl
            with tempfile.TemporaryDirectory() as tmpdir:
                report_path = os.path.join(
                    tmpdir,
                    "portofolio_report.html"
                )

                qs.reports.html(
                    portofolio_returns,
                    output=report_path,
                    title="Portofolio Performance Report"
                )

                with open(report_path, "r", encoding="utf-8") as file:
                    html_content = file.read()

                st.download_button(
                    label="📥 Download Full Report (HTML)",
                    data=html_content,
                    file_name="portofolio_report.html",
                    mime="text/html"
                )

        st.success("Analysis Successful!, Explore your portfolio metric above.")

# run-
if __name__ == "__main__":
    main()
