"""
data_loader.py
Shared utility for loading VendorGuard AI's local CSV datasets.
No cloud / DB dependency required — keeps the hackathon demo self-contained.
"""

import csv
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _read_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_suppliers():
    rows = _read_csv("suppliers.csv")
    for r in rows:
        r["quality_score"] = float(r["quality_score"])
        r["on_time_rate"] = float(r["on_time_rate"])
        r["avg_delivery_days"] = float(r["avg_delivery_days"])
        r["price_index"] = float(r["price_index"])
    return rows


def load_deliveries():
    rows = _read_csv("deliveries.csv")
    for r in rows:
        r["expected_date"] = _parse_date(r["expected_date"])
        r["actual_date"] = _parse_date(r["actual_date"]) if r["actual_date"] else None
    return rows


def load_inventory():
    rows = _read_csv("inventory.csv")
    for r in rows:
        r["current_stock"] = int(r["current_stock"])
        r["safety_stock"] = int(r["safety_stock"])
        r["daily_usage"] = int(r["daily_usage"])
    return rows


def load_purchase_orders():
    rows = _read_csv("purchase_orders.csv")
    for r in rows:
        r["quantity"] = int(r["quantity"])
        r["amount"] = float(r["amount"])
        r["order_date"] = _parse_date(r["order_date"])
    return rows


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d")


def supplier_lookup(suppliers):
    """Return a dict keyed by supplier_id for quick access."""
    return {s["supplier_id"]: s for s in suppliers}
