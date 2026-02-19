import streamlit as st
import yfinance as yf
import quantstats as qs
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import plotly.express as px
import tempfile
import os

# Logic - Mean Variance Optimization
def optimize_portfolio(returns):
    """Mencari bobot optimal untuk memaksimalkan Sharpe Ratio."""
    num_assets = len(returns.columns)
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    def objective(weights):
        # minimize -Sharpe Ratio = Maximize Sharpe
        p_return = np.sum(mean_returns * weights) * 252
        p_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        if p_std == 0: return 0
        return -(p_return / p_std)

    # Total bobot harus 100%
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # Batas tiap saham 0% - 100%
    bounds = tuple((0, 1) for _ in range(num_assets))
    init_guess = num_assets * [1. / num_assets]
    
    result = minimize(objective, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x

def main():
    # Konfigurasi Halaman - Streamlit
    st.set_page_config(
        page_title="Portfolio Analytics Dashboard", 
        layout="wide"
    )
    st.title("Portfolio Analytics Dashboard")

    st.sidebar.header("Portofolio Configuration")

    # ticker - US Stock
    us_ticker = [ 
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", 
        "META", "TSLA", "JPM", "V", "BRK-B"
    ]

    # Selector 
    tickers = st.sidebar.multiselect(
        "Select US Stock",
        options=us_ticker,
        default=["AAPL", "AMZN", "TSLA", "GOOGL"]
    )

    # Input bobot portofolio 
    weights = []
    if tickers:
        st.sidebar.markdown("### Assign Portfolio Weights")
        st.sidebar.info("Pastikan bobot saham anda 1.0")
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
            
            # warning: user input > 1.0
            if round(total_weight, 2) != 1.0:
                st.sidebar.info(f"Note: Total input {total_weight:.2f} otomatis dinormalisasi ke 1.0")
                
        else:
            # Kalau user nge-set semua slider ke 0
            st.error("Total bobot tidak boleh nol.")
            st.stop()

    # Input tanggal
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=(pd.to_datetime("2024-01-01"), pd.to_datetime("today"))
    )

    generate_btn = st.sidebar.button("Generate Analysis")


    # Main Logic
    if generate_btn:

        # Validasi input
        if not tickers:
            st.error("Please select at least one stock.")
            st.stop()

        with st.spinner("Taking Data & Performing Analysis..."):

            # Ambil data harga penutupan
            price_data = yf.download(tickers, start=start_date, end=end_date)["Close"]
            
            # Hitung return harian
            returns = price_data.pct_change().dropna()

            # Hitung return portofolio manual
            port_returns = (returns * weights).sum(axis=1)

            # Hitung bobot optimal menggunakan MVO logic
            opt_weights = optimize_portfolio(returns)
            opt_returns = (returns * opt_weights).sum(axis=1)

            # Extend quantstats ke pandas
            qs.extend_pandas()


            # VISUALISASI
            # ------------
            # Key Matric
            st.subheader("Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Sharpe Ratio", f"{qs.stats.sharpe(port_returns):.2f}")
            col2.metric("Max Drawdown", f"{qs.stats.max_drawdown(port_returns)*100:.2f}%")
            col3.metric("CAGR", f"{qs.stats.cagr(port_returns)*100:.2f}%")
            col4.metric("Volatility", f"{qs.stats.volatility(port_returns)*100:.2f}%")

            # Alokasi stock manual vs optimization
            st.markdown("---")
            st.subheader("Portfolio Allocation")
            col_pie_1, col_pie_2 = st.columns(2)

            with col_pie_1:
                st.markdown("**Your Allocation**")
                fig_pie = px.pie(names=tickers, values=weights, hole=0.4)
                fig_pie.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_pie_2:
                st.markdown("**Optimized (Mean Veriance Optimization)**")
                fig_opt = px.pie(names=tickers, values=opt_weights, hole=0.4, 
                                 color_discrete_sequence=px.colors.sequential.RdBu)
                fig_opt.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_opt, use_container_width=True)

            # Perbandingan portofolio manual vs hasil optimasi
            st.markdown("---")
            st.subheader("Cumulative Returns Comparison")

            comparison_df = pd.DataFrame({
                "Your Portfolio": (1 + port_returns).cumprod(),
                "Optimized Portfolio": (1 + opt_returns).cumprod()
            })
            st.line_chart(comparison_df)

            # Visual - Heatmap
            st.markdown("---")
            st.subheader("Monthly Return Heatmap")
            st.dataframe(
                port_returns.monthly_returns().style.format("{:.2%}"), 
                use_container_width=True
            )

            # Visual - Yearly Return
            st.subheader("End-of-Year Returns")
            yearly_returns = port_returns.resample('YE').apply(lambda x: (x + 1).prod() - 1)
            st.bar_chart(yearly_returns)
            

            # Generate Report/laporan ke HTML
            with tempfile.TemporaryDirectory() as tmpdir:
                report_path = os.path.join(tmpdir, "portofolio_report.html")
                qs.reports.html(port_returns, output=report_path, title="Portfolio Performance Report")
                
                with open(report_path, "r", encoding="utf-8") as file:
                    html_content = file.read()

                st.download_button(
                    label="📥 Download Full Report (HTML)",
                    data=html_content,
                    file_name="portofolio_report.html",
                    mime="text/html",
                    use_container_width=True
                )

        st.success("Analysis Successful!")

if __name__ == "__main__":
    main()