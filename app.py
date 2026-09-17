from __future__ import annotations

from datetime import datetime

import plotly.express as px
import streamlit as st

from src.analytics import dashboard_summary, merchant_summary, review_queue
from src.config import APP_NAME, APP_TAGLINE
from src.database import (
    add_transaction,
    clear_transactions,
    get_settings,
    init_db,
    load_transactions,
    save_settings,
    seed_demo_data,
)
from src.risk_engine import estimate_mdr, evaluate_transaction
from src.ui import format_inr, hero, inject_css, metric_card, risk_badge

st.set_page_config(page_title=APP_NAME, page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
init_db()
inject_css()
settings = get_settings()

with st.sidebar:
    st.markdown("## 🛡️ PayGuard")
    st.caption("UPI Payment Intelligence")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "💳 Smart Payment Analyzer",
            "📡 Transaction Monitor",
            "🧠 Fraud Intelligence",
            "🏪 Merchant Analytics",
            "⚙️ Settings",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Academic simulation only")
    st.write("No live UPI, NPCI, bank or payment-gateway connection.")

hero("🛡️ PayGuard UPI Intelligence", APP_TAGLINE)

if page == "🏠 Dashboard":
    df = load_transactions()
    summary = dashboard_summary(df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Payment Volume", format_inr(float(summary["total_volume"])), f'{summary["total_txns"]} transactions')
    with c2:
        metric_card("Estimated MDR", format_inr(float(summary["total_mdr"])), "configured demo rules")
    with c3:
        metric_card("High-Risk Transactions", str(summary["high_risk"]), "priority review")
    with c4:
        metric_card("Average Ticket Size", format_inr(float(summary["avg_ticket"])), "average transaction value")

    if df.empty:
        st.info("No transaction data yet. Generate demo data or add a transaction from Smart Payment Analyzer.")
        if st.button("✨ Generate Demo Data", width="stretch"):
            seed_demo_data()
            st.rerun()
    else:
        left, right = st.columns([1.35, 1])
        temp = df.copy()
        temp["date"] = temp["txn_time"].dt.date
        with left:
            daily = temp.groupby("date", as_index=False)["amount"].sum()
            fig = px.area(daily, x="date", y="amount", title="Transaction Volume Trend", labels={"amount": "Volume (₹)", "date": "Date"})
            fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dbeafe")
            st.plotly_chart(fig, width="stretch")
        with right:
            risk_counts = df["risk_level"].value_counts().reindex(["Low", "Medium", "High"], fill_value=0).reset_index()
            risk_counts.columns = ["Risk", "Count"]
            fig = px.pie(risk_counts, names="Risk", values="Count", title="Risk Distribution", hole=0.62)
            fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", font_color="#dbeafe")
            st.plotly_chart(fig, width="stretch")

        a, b = st.columns(2)
        with a:
            top_merchants = df.groupby("merchant_id", as_index=False)["amount"].sum().sort_values("amount", ascending=False).head(8)
            fig = px.bar(top_merchants, x="merchant_id", y="amount", title="Top Merchants by Volume", labels={"merchant_id": "Merchant", "amount": "Volume (₹)"})
            fig.update_layout(height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dbeafe")
            st.plotly_chart(fig, width="stretch")
        with b:
            by_category = df.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
            fig = px.bar(by_category, x="amount", y="category", orientation="h", title="Spend by Category", labels={"amount": "Volume (₹)", "category": "Category"})
            fig.update_layout(height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dbeafe")
            st.plotly_chart(fig, width="stretch")

        st.markdown("### Recent Transactions")
        recent = df.head(8)[["txn_time", "customer_id", "merchant_id", "txn_type", "amount", "estimated_mdr", "risk_level", "risk_score"]].copy()
        recent.columns = ["Time", "Customer", "Merchant", "Type", "Amount", "Estimated MDR", "Risk", "Score"]
        st.dataframe(recent, width="stretch", hide_index=True)

elif page == "💳 Smart Payment Analyzer":
    st.markdown("### Analyze a New Payment")
    st.caption("The app estimates simulated merchant cost and calculates a review risk score before saving the transaction.")

    left, right = st.columns(2)
    with left:
        customer_id = st.text_input("Customer ID", "CUST001")
        merchant_id = st.text_input("Merchant ID", "MER001")
        txn_type = st.selectbox("Payment Type", ["P2M", "P2P"])
        category = st.selectbox("Category", ["Retail", "Food", "Electronics", "Travel", "Services", "Education", "Healthcare", "Personal", "Other"])
    with right:
        amount = st.number_input("Amount (₹)", min_value=1.0, value=2500.0, step=1.0)
        txn_date = st.date_input("Transaction Date", datetime.now().date())
        txn_clock = st.time_input("Transaction Time", datetime.now().time().replace(microsecond=0))
        txn_dt = datetime.combine(txn_date, txn_clock)

    history = load_transactions()
    mdr = estimate_mdr(txn_type, amount, settings)
    score, level, reason = evaluate_transaction(history, customer_id.strip(), merchant_id.strip(), txn_type, amount, txn_dt, settings)

    st.markdown("### Live Analysis")
    a, b, c = st.columns(3)
    with a:
        metric_card("Payment Amount", format_inr(amount), f"{txn_type} transaction")
    with b:
        metric_card("Estimated MDR", format_inr(mdr), f'{float(settings["mdr_rate"]):.2f}% demo rate')
    with c:
        metric_card("Configured Threshold", format_inr(float(settings["threshold"])), "editable in Settings")

    st.markdown("#### Risk Assessment")
    risk_badge(level, score)
    st.markdown(f'<div class="info-box" style="margin-top:12px;"><b>Reason:</b> {reason}</div>', unsafe_allow_html=True)
    st.progress(score / 100.0, text=f"Risk score: {score}/100")

    if level == "High":
        st.error("High-risk pattern detected. A real system could send this transaction for manual review.")
    elif level == "Medium":
        st.warning("Some unusual behavior was detected. Additional verification may be appropriate.")
    else:
        st.success("No major suspicious pattern detected by the demo rules.")

    if st.button("💾 Save Transaction", type="primary", width="stretch"):
        if not customer_id.strip() or not merchant_id.strip():
            st.error("Customer ID and Merchant ID are required.")
        else:
            add_transaction({
                "txn_time": txn_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "customer_id": customer_id.strip(),
                "merchant_id": merchant_id.strip(),
                "txn_type": txn_type,
                "category": category,
                "amount": amount,
                "estimated_mdr": mdr,
                "risk_score": score,
                "risk_level": level,
                "risk_reason": reason,
            })
            st.success("Transaction saved to the local SQLite database.")

    st.markdown("#### Quick Demo")
    st.write("Use the same customer for **₹1,500** and then **₹1,000** within the configured time window. The second payment can be flagged as a possible threshold-splitting pattern.")

elif page == "📡 Transaction Monitor":
    st.markdown("### Transaction Monitor")
    df = load_transactions()
    if df.empty:
        st.info("No transactions available.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            search = st.text_input("Search Customer / Merchant", "")
        with f2:
            type_filter = st.multiselect("Type", ["P2M", "P2P"], default=["P2M", "P2P"])
        with f3:
            risk_filter = st.multiselect("Risk", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])

        filtered = df[df["txn_type"].isin(type_filter) & df["risk_level"].isin(risk_filter)].copy()
        if search.strip():
            q = search.strip().lower()
            filtered = filtered[
                filtered["customer_id"].str.lower().str.contains(q, na=False)
                | filtered["merchant_id"].str.lower().str.contains(q, na=False)
            ]
        st.caption(f"Showing {len(filtered)} of {len(df)} transactions")
        display = filtered[["id", "txn_time", "customer_id", "merchant_id", "txn_type", "category", "amount", "estimated_mdr", "risk_level", "risk_score", "risk_reason"]].copy()
        display.columns = ["ID", "Time", "Customer", "Merchant", "Type", "Category", "Amount", "Estimated MDR", "Risk", "Score", "Reason"]
        st.dataframe(display, width="stretch", hide_index=True, height=520)
        st.download_button("⬇️ Download Filtered CSV Report", data=display.to_csv(index=False).encode("utf-8"), file_name="payguard_transactions.csv", mime="text/csv", width="stretch")

elif page == "🧠 Fraud Intelligence":
    st.markdown("### Fraud & Pattern Intelligence")
    df = load_transactions()
    if df.empty:
        st.info("No transactions available.")
    else:
        queue = review_queue(df)
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("High-Risk Cases", str(int((df["risk_level"] == "High").sum())), "priority review")
        with c2:
            metric_card("Medium-Risk Cases", str(int((df["risk_level"] == "Medium").sum())), "watchlist")
        with c3:
            metric_card("Average Risk Score", f'{float(df["risk_score"].mean()):.1f}/100', "all transactions")

        a, b = st.columns([1.2, 1])
        with a:
            temp = df.copy()
            temp["date"] = temp["txn_time"].dt.date
            trend = temp.groupby("date", as_index=False)["risk_score"].mean()
            fig = px.line(trend, x="date", y="risk_score", markers=True, title="Average Risk Score Over Time")
            fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dbeafe")
            st.plotly_chart(fig, width="stretch")
        with b:
            suspects = df.groupby("customer_id", as_index=False).agg(transactions=("id", "count"), total_amount=("amount", "sum"), avg_risk=("risk_score", "mean"), high_risk_cases=("risk_level", lambda s: int((s == "High").sum()))).sort_values(["high_risk_cases", "avg_risk"], ascending=False).head(10)
            fig = px.scatter(suspects, x="transactions", y="avg_risk", size="total_amount", hover_name="customer_id", title="Customer Risk Map")
            fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dbeafe")
            st.plotly_chart(fig, width="stretch")

        st.markdown("### Priority Review Queue")
        if queue.empty:
            st.success("No Medium or High risk transactions in the current dataset.")
        else:
            st.dataframe(queue[["txn_time", "customer_id", "merchant_id", "amount", "risk_level", "risk_score", "risk_reason"]], width="stretch", hide_index=True, height=430)

elif page == "🏪 Merchant Analytics":
    st.markdown("### Merchant Performance & Cost Analytics")
    df = load_transactions()
    merchants = merchant_summary(df)
    if merchants.empty:
        st.info("No merchant data available.")
    else:
        selected = st.selectbox("Select Merchant", merchants["merchant_id"].tolist())
        row = merchants[merchants["merchant_id"] == selected].iloc[0]
        a, b, c, d = st.columns(4)
        with a:
            metric_card("Total Volume", format_inr(float(row["total_volume"])), selected)
        with b:
            metric_card("Transactions", str(int(row["transaction_count"])), "processed in demo")
        with c:
            metric_card("Estimated MDR", format_inr(float(row["estimated_mdr"])), "simulated merchant cost")
        with d:
            metric_card("Average Risk", f'{float(row["avg_risk"]):.1f}/100', f'{int(row["high_risk_cases"])} high-risk cases')

        merchant_df = df[df["merchant_id"] == selected].copy()
        merchant_df["date"] = merchant_df["txn_time"].dt.date
        x, y = st.columns(2)
        with x:
            trend = merchant_df.groupby("date", as_index=False)["amount"].sum()
            fig = px.bar(trend, x="date", y="amount", title=f"{selected} — Daily Payment Volume")
            fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dbeafe")
            st.plotly_chart(fig, width="stretch")
        with y:
            cat = merchant_df.groupby("category", as_index=False)["amount"].sum()
            fig = px.pie(cat, names="category", values="amount", hole=0.55, title="Category Mix")
            fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", font_color="#dbeafe")
            st.plotly_chart(fig, width="stretch")
        st.markdown("### All Merchant Summary")
        st.dataframe(merchants, width="stretch", hide_index=True)

elif page == "⚙️ Settings":
    st.markdown("### Simulation Settings")
    st.warning("These values are configurable academic simulation settings, not a live UPI pricing or fraud-policy feed.")

    left, right = st.columns(2)
    with left:
        threshold = st.number_input("Configured threshold (₹)", min_value=0.0, value=float(settings["threshold"]), step=100.0)
        mdr_rate = st.number_input("Demo MDR rate (%)", min_value=0.0, value=float(settings["mdr_rate"]), step=0.05, format="%.2f")
        window = st.number_input("Velocity window (minutes)", min_value=1, value=int(settings["velocity_window_min"]), step=1)
    with right:
        medium_risk = st.slider("Medium-risk score starts at", 1, 98, int(settings["medium_risk_score"]))
        default_high = max(int(settings["high_risk_score"]), medium_risk + 1)
        high_risk = st.slider("High-risk score starts at", medium_risk + 1, 100, default_high)

    if st.button("💾 Save Settings", type="primary", width="stretch"):
        save_settings({
            "threshold": threshold,
            "mdr_rate": mdr_rate,
            "velocity_window_min": window,
            "medium_risk_score": medium_risk,
            "high_risk_score": high_risk,
        })
        st.success("Settings saved.")
        st.rerun()

    a, b = st.columns(2)
    with a:
        if st.button("✨ Generate Demo Data", width="stretch"):
            if seed_demo_data():
                st.success("Demo transactions created.")
            else:
                st.warning("Transactions already exist. Clear them first for a fresh demo dataset.")
    with b:
        if st.button("🗑️ Clear All Transactions", width="stretch"):
            clear_transactions()
            st.success("All local transactions cleared.")

    st.markdown("### Project Purpose")
    st.write("PayGuard demonstrates fintech analytics, configurable merchant-cost simulation, transaction monitoring, rule-based fraud detection, risk scoring, merchant analytics and CSV reporting using Python, Streamlit, SQLite, Pandas and Plotly.")
