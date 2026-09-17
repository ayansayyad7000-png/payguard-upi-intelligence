# 🛡️ PayGuard UPI Intelligence

**Advanced UPI Payment Analytics, MDR Simulation & Fraud Detection System** built with **Python, Streamlit, SQLite, Pandas and Plotly**.

> Academic/demo project only. It does **not** connect to NPCI, banks, live UPI rails, or a real payment gateway, and it does not automatically split payments to avoid fees.

## ✨ What this project does

PayGuard simulates a fintech monitoring platform that can:

- analyze P2M and P2P payment records
- estimate merchant-side cost using configurable demo rules
- assign a transaction risk score from 0–100
- flag repeated small-payment / threshold-splitting patterns
- track payment velocity for customers and merchants
- show a live-style transaction monitor
- generate fraud review queues
- provide merchant volume, cost and risk analytics
- store data locally in SQLite
- export transaction reports as CSV
- generate demo data for presentations and viva

## 🧠 Project flow

```text
Customer Payment
      ↓
Transaction Input
      ↓
Configurable Rule Engine
      ↓
MDR Simulation + Risk Engine
      ↓
SQLite Database
      ↓
Transaction Monitor
      ↓
Fraud Intelligence + Merchant Analytics
```

## 🗂️ Project structure

```text
payguard-upi-intelligence/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── src/
│   ├── __init__.py
│   ├── analytics.py
│   ├── config.py
│   ├── database.py
│   ├── risk_engine.py
│   └── ui.py
├── tests/
│   └── test_risk_engine.py
└── .github/
    └── workflows/
        └── ci.yml
```

## 🚀 Run in VS Code

### 1. Clone the repository

```powershell
git clone https://github.com/ayansayyad7000-png/payguard-upi-intelligence.git
cd payguard-upi-intelligence
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

### 4. Run

```powershell
py -m streamlit run app.py
```

Open the Local URL shown by Streamlit, normally `http://localhost:8501`.

## 🎬 Best demo sequence

1. Open **Settings** and click **Generate Demo Data**.
2. Open **Dashboard** to show transaction KPIs and charts.
3. Open **Smart Payment Analyzer**.
4. Save a P2M transaction of **₹1,500** for customer `CUST500`.
5. Save another P2M transaction of **₹1,000** for the same customer within the configured time window.
6. Show the risk reason for the second transaction.
7. Open **Fraud Intelligence** and show the review queue.
8. Open **Merchant Analytics** to show merchant volume, simulated MDR and risk.
9. Export a CSV report from **Transaction Monitor**.

## 🧪 Tests

```powershell
py -m pip install pytest
py -m pytest -q
```

The repository also contains a GitHub Actions workflow that compiles the project and runs the tests on pushes and pull requests.

## 🧰 Tech stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- Pytest
- GitHub Actions

## ⚠️ Important note

The ₹ threshold and MDR percentage in this project are **configurable simulation values**. They should not be treated as current official UPI pricing rules. For a real payment product, rules would need to come from the relevant payment provider, regulator and network documentation.

## 👨‍💻 Author

**Ayan Sayyad**  
B.Tech Information Technology
