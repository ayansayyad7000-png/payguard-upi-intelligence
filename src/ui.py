from __future__ import annotations

import streamlit as st


CSS = """
<style>
.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(45, 212, 191, 0.08), transparent 28%),
        radial-gradient(circle at 92% 0%, rgba(129, 140, 248, 0.09), transparent 30%),
        #07111f;
    color: #eef4ff;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1729 0%, #081321 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
.hero {
    padding: 28px 30px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(20,184,166,.16), rgba(99,102,241,.16));
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 18px 45px rgba(0,0,0,.22);
    margin-bottom: 22px;
}
.hero h1 { margin:0; font-size:2.15rem; letter-spacing:-.03em; }
.hero p { margin:8px 0 0 0; color:#b8c6dc; font-size:1.02rem; }
.metric-card {
    background: rgba(14,26,45,.86);
    border: 1px solid rgba(255,255,255,.09);
    border-radius:18px;
    padding:18px;
    min-height:112px;
    box-shadow:0 12px 30px rgba(0,0,0,.18);
}
.metric-label { color:#94a3b8; font-size:.87rem; margin-bottom:8px; }
.metric-value { font-size:1.72rem; font-weight:750; letter-spacing:-.03em; }
.metric-sub { color:#7dd3fc; font-size:.82rem; margin-top:4px; }
.info-box {
    padding:14px 16px; border-radius:14px;
    border:1px solid rgba(255,255,255,.08);
    background:rgba(15,23,42,.72); color:#c7d2fe;
}
.risk-low,.risk-medium,.risk-high {
    padding:7px 12px; border-radius:999px; display:inline-block; font-weight:700;
}
.risk-low { background:rgba(16,185,129,.14); border:1px solid rgba(16,185,129,.3); color:#6ee7b7; }
.risk-medium { background:rgba(245,158,11,.14); border:1px solid rgba(245,158,11,.3); color:#fcd34d; }
.risk-high { background:rgba(239,68,68,.14); border:1px solid rgba(239,68,68,.3); color:#fca5a5; }
footer, #MainMenu { visibility:hidden; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(level: str, score: int) -> None:
    css = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}[level]
    st.markdown(f'<span class="{css}">{level} Risk · {score}/100</span>', unsafe_allow_html=True)


def format_inr(value: float) -> str:
    return f"₹{value:,.2f}"
