from __future__ import annotations

import pandas as pd


def dashboard_summary(df: pd.DataFrame) -> dict[str, float | int]:
    total_txns = int(len(df))
    total_volume = float(df["amount"].sum()) if not df.empty else 0.0
    total_mdr = float(df["estimated_mdr"].sum()) if not df.empty else 0.0
    high_risk = int((df["risk_level"] == "High").sum()) if not df.empty else 0
    avg_ticket = total_volume / total_txns if total_txns else 0.0
    return {
        "total_txns": total_txns,
        "total_volume": total_volume,
        "total_mdr": total_mdr,
        "high_risk": high_risk,
        "avg_ticket": avg_ticket,
    }


def merchant_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[
            "merchant_id", "transaction_count", "total_volume", "estimated_mdr",
            "avg_ticket", "avg_risk", "high_risk_cases",
        ])
    return (
        df.groupby("merchant_id", as_index=False)
        .agg(
            transaction_count=("id", "count"),
            total_volume=("amount", "sum"),
            estimated_mdr=("estimated_mdr", "sum"),
            avg_ticket=("amount", "mean"),
            avg_risk=("risk_score", "mean"),
            high_risk_cases=("risk_level", lambda s: int((s == "High").sum())),
        )
        .sort_values("total_volume", ascending=False)
    )


def review_queue(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    return (
        df[df["risk_level"].isin(["High", "Medium"])]
        .sort_values(["risk_score", "txn_time"], ascending=[False, False])
        .copy()
    )
