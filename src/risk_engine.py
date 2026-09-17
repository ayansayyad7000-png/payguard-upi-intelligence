from __future__ import annotations

from datetime import datetime, timedelta
from typing import Mapping

import pandas as pd


def estimate_mdr(txn_type: str, amount: float, settings: Mapping[str, float | int]) -> float:
    """Academic MDR simulator; not a live UPI pricing rule engine."""
    threshold = float(settings["threshold"])
    rate = float(settings["mdr_rate"])
    if txn_type == "P2M" and amount > threshold:
        return round(amount * rate / 100.0, 2)
    return 0.0


def evaluate_transaction(
    history: pd.DataFrame,
    customer_id: str,
    merchant_id: str,
    txn_type: str,
    amount: float,
    txn_time: datetime,
    settings: Mapping[str, float | int],
) -> tuple[int, str, str]:
    """Return risk score, risk level, and explanation for a demo transaction."""
    if txn_type != "P2M":
        return 5, "Low", "P2P demo transaction"

    threshold = float(settings["threshold"])
    window = int(settings["velocity_window_min"])
    medium = int(settings["medium_risk_score"])
    high = int(settings["high_risk_score"])

    score = 0
    reasons: list[str] = []

    if threshold * 0.90 <= amount <= threshold:
        score += 15
        reasons.append("amount close to configured threshold")

    if not history.empty:
        working = history.copy()
        working["txn_time"] = pd.to_datetime(working["txn_time"], errors="coerce")
        cutoff = txn_time - timedelta(minutes=window)

        recent_customer = working[
            (working["customer_id"] == customer_id)
            & (working["txn_time"] >= cutoff)
            & (working["txn_time"] <= txn_time)
        ]

        if len(recent_customer) >= 2:
            score += min(25, 8 * len(recent_customer))
            reasons.append("high customer payment velocity")

        recent_small = recent_customer[
            (recent_customer["txn_type"] == "P2M")
            & (recent_customer["amount"] <= threshold)
        ]
        combined = float(recent_small["amount"].sum()) + float(amount)
        if len(recent_small) >= 1 and amount <= threshold and combined > threshold:
            score += 45
            reasons.append("possible threshold-splitting pattern")

        recent_merchant = working[
            (working["merchant_id"] == merchant_id)
            & (working["txn_time"] >= cutoff)
            & (working["txn_time"] <= txn_time)
        ]
        if len(recent_merchant) >= 8:
            score += 12
            reasons.append("merchant received many payments in a short window")

    if amount >= max(10000.0, threshold * 5):
        score += 15
        reasons.append("high-value transaction")

    score = min(score, 100)
    level = "High" if score >= high else "Medium" if score >= medium else "Low"
    return score, level, "; ".join(reasons or ["no major demo rule triggered"])
