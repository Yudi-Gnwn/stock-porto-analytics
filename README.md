## 📊 Portfolio Analytics Dashboard

![Demo](assets/demo.gif)

Dashboard saham yang menampilkan alokasi portofolio, Sharpe Ratio, CAGR, volatilitas saham dan penurunan nilai aset. **Laporan performa portofolio dapat langsung diunduh dengan mudah**


### ✨ Fitur
---

- Data saham real time - **Yahoo Finance**
- Alokasi beban portofolio - **pie chart**
- Key performance metrics:
  - Sharpe Ratio
  - Compound Annual Growth Rate (CAGR)
  - Max Drawdown
  - Volatility
- Monthly returns - **heatmap**
- Cumulative & yearly return charts
- performance report **HTML** yang dapat diunduh


### 🛠️ Tools
---

- **Framework**: Streamlit
- **Library Data**: `yfinance`, `quantstats`  
- **Data Processing**: Pandas
- **Visualisasi**: Plotly Express


### 🚀 How to Run
---

1. **clone repository**

    ```bash
    git clone https://github.com/Yudi-Gnwn/stock-porto-analytics.git
    cd stock-porto-analytics
    ```

2. **create virtual environment**

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. **install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **run app**

    ```bash
    python -m streamlit run run.py
    ```

### Note:
---

- Projek ini dibuat untuk keperluan portofolio.
- keputusan investasi yang diambil adalah tanggung jawab individu.