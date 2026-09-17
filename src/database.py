from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from .config import DEFAULTS

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "payguard.db"


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            txn_time TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            merchant_id TEXT NOT NULL,
            txn_type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            estimated_mdr REAL NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            risk_reason TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    defaults = {
        "threshold": DEFAULTS.threshold,
        "mdr_rate": DEFAULTS.mdr_rate,
        "velocity_window_min": DEFAULTS.velocity_window_min,
        "medium_risk_score": DEFAULTS.medium_risk_score,
        "high_risk_score": DEFAULTS.high_risk_score,
    }
    for key, value in defaults.items():
        cur.execute("INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


def get_settings() -> dict[str, float | int]:
    conn = _connect()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    values = {row["key"]: row["value"] for row in rows}
    return {
        "threshold": float(values.get("threshold", DEFAULTS.threshold)),
        "mdr_rate": float(values.get("mdr_rate", DEFAULTS.mdr_rate)),
        "velocity_window_min": int(float(values.get("velocity_window_min", DEFAULTS.velocity_window_min))),
        "medium_risk_score": int(float(values.get("medium_risk_score", DEFAULTS.medium_risk_score))),
        "high_risk_score": int(float(values.get("high_risk_score", DEFAULTS.high_risk_score))),
    }


def save_settings(settings: dict[str, float | int]) -> None:
    conn = _connect()
    cur = conn.cursor()
    for key, value in settings.items():
        cur.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )
    conn.commit()
    conn.close()


def add_transaction(row: dict[str, Any]) -> None:
    conn = _connect()
    conn.execute("""
        INSERT INTO transactions (
            txn_time, customer_id, merchant_id, txn_type, category,
            amount, estimated_mdr, risk_score, risk_level, risk_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["txn_time"], row["customer_id"], row["merchant_id"], row["txn_type"],
        row["category"], float(row["amount"]), float(row["estimated_mdr"]),
        int(row["risk_score"]), row["risk_level"], row["risk_reason"],
    ))
    conn.commit()
    conn.close()


def load_transactions() -> pd.DataFrame:
    conn = _connect()
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY txn_time DESC, id DESC", conn)
    conn.close()
    if not df.empty:
        df["txn_time"] = pd.to_datetime(df["txn_time"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        df["estimated_mdr"] = pd.to_numeric(df["estimated_mdr"], errors="coerce").fillna(0.0)
        df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0).astype(int)
    return df


def clear_transactions() -> None:
    conn = _connect()
    conn.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()


def seed_demo_data() -> bool:
    conn = _connect()
    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    if count:
        conn.close()
        return False

    settings = get_settings()
    threshold = float(settings["threshold"])
    rate = float(settings["mdr_rate"])
    now = datetime.now() - timedelta(hours=5)
    rows = [
        ("CUST101", "MER001", "P2M", "Retail", 850.0, 5, "normal demo transaction"),
        ("CUST102", "MER001", "P2M", "Retail", 1999.0, 18, "amount close to configured threshold"),
        ("CUST103", "MER002", "P2M", "Electronics", 4500.0, 12, "normal demo transaction"),
        ("CUST104", "MER003", "P2P", "Personal", 1200.0, 5, "P2P demo transaction"),
        ("CUST105", "MER002", "P2M", "Electronics", 7600.0, 18, "normal demo transaction"),
        ("CUST777", "MER009", "P2M", "Services", 1500.0, 20, "normal demo transaction"),
        ("CUST777", "MER009", "P2M", "Services", 1000.0, 82, "possible threshold-splitting pattern"),
        ("CUST108", "MER004", "P2M", "Food", 650.0, 4, "normal demo transaction"),
        ("CUST109", "MER004", "P2M", "Food", 1200.0, 6, "normal demo transaction"),
        ("CUST110", "MER005", "P2M", "Travel", 18000.0, 38, "high-value transaction"),
    ]

    medium = int(settings["medium_risk_score"])
    high = int(settings["high_risk_score"])
    for i, (customer, merchant, txn_type, category, amount, score, reason) in enumerate(rows):
        txn_time = now + timedelta(minutes=i * 22)
        mdr = round(amount * rate / 100, 2) if txn_type == "P2M" and amount > threshold else 0.0
        level = "High" if score >= high else "Medium" if score >= medium else "Low"
        conn.execute("""
            INSERT INTO transactions (
                txn_time, customer_id, merchant_id, txn_type, category,
                amount, estimated_mdr, risk_score, risk_level, risk_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            txn_time.strftime("%Y-%m-%d %H:%M:%S"), customer, merchant,
            txn_type, category, amount, mdr, score, level, reason,
        ))
    conn.commit()
    conn.close()
    return True
