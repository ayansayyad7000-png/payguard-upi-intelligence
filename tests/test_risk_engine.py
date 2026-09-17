from datetime import datetime, timedelta

import pandas as pd

from src.risk_engine import estimate_mdr, evaluate_transaction


SETTINGS = {
    "threshold": 2000.0,
    "mdr_rate": 0.40,
    "velocity_window_min": 10,
    "medium_risk_score": 35,
    "high_risk_score": 70,
}


def test_mdr_zero_below_threshold():
    assert estimate_mdr("P2M", 1999.0, SETTINGS) == 0.0


def test_mdr_above_threshold():
    assert estimate_mdr("P2M", 2500.0, SETTINGS) == 10.0


def test_split_pattern_gets_flagged():
    now = datetime.now()
    history = pd.DataFrame([
        {
            "txn_time": now - timedelta(minutes=3),
            "customer_id": "CUST1",
            "merchant_id": "MER1",
            "txn_type": "P2M",
            "amount": 1500.0,
        }
    ])
    score, level, reason = evaluate_transaction(
        history, "CUST1", "MER1", "P2M", 1000.0, now, SETTINGS
    )
    assert score >= 45
    assert "threshold-splitting" in reason
