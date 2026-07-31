"""
Agent 1 — Vendor Monitoring Agent
----------------------------------
Reads suppliers.csv, deliveries.csv and purchase_orders.csv.
Detects anomalies: late deliveries, high defect / low quality rate,
rising costs, missed deadlines, poor supplier rating.

Output: a list of "incident" dicts, one per supplier with an issue.
"""

from data_loader import load_suppliers, load_deliveries, load_purchase_orders, supplier_lookup

# --- Thresholds (tunable) ---------------------------------------------------
# Acceptable supplier bar: quality >= 85%, on-time delivery >= 90%.
# Anything below either line is flagged as an incident.
QUALITY_THRESHOLD = 85.0        # below this => quality risk
ON_TIME_THRESHOLD = 90.0        # below this => reliability risk
DELAY_DAYS_THRESHOLD = 3        # days late => delivery incident
PRICE_INDEX_THRESHOLD = 1.08    # above this => rising cost risk


def _delivery_delay_days(delivery):
    """Positive integer = days late. 0 if on time or not yet delivered."""
    if delivery["actual_date"] is None:
        return 0
    delta = (delivery["actual_date"] - delivery["expected_date"]).days
    return max(delta, 0)


def run():
    suppliers = load_suppliers()
    deliveries = load_deliveries()
    lookup = supplier_lookup(suppliers)

    incidents = []

    for supplier in suppliers:
        sid = supplier["supplier_id"]
        issues = []

        # Rule 1: Quality
        if supplier["quality_score"] < QUALITY_THRESHOLD:
            issues.append(f"Low quality score ({supplier['quality_score']}%)")

        # Rule 2: On-time rate
        if supplier["on_time_rate"] < ON_TIME_THRESHOLD:
            issues.append(f"Poor on-time rate ({supplier['on_time_rate']}%)")

        # Rule 3: Rising price
        if supplier["price_index"] > PRICE_INDEX_THRESHOLD:
            issues.append(f"Price index above baseline ({supplier['price_index']})")

        # Rule 4: Actual delivery delays from deliveries.csv
        supplier_deliveries = [d for d in deliveries if d["supplier"] == sid]
        max_delay = 0
        delayed_orders = []
        for d in supplier_deliveries:
            delay = _delivery_delay_days(d)
            if delay > max_delay:
                max_delay = delay
            if delay >= DELAY_DAYS_THRESHOLD:
                delayed_orders.append((d["order_id"], delay))

        if delayed_orders:
            issues.append(
                f"{len(delayed_orders)} delayed order(s), worst delay {max_delay} day(s)"
            )

        if issues:
            incidents.append({
                "supplier_id": sid,
                "supplier_name": supplier["name"],
                "quality_score": supplier["quality_score"],
                "on_time_rate": supplier["on_time_rate"],
                "max_delay_days": max_delay,
                "price_index": supplier["price_index"],
                "issues": issues,
            })

    return incidents


def _print_report(incidents):
    print("=" * 60)
    print("AGENT 1 — VENDOR MONITORING AGENT")
    print("=" * 60)
    if not incidents:
        print("No anomalies detected. All suppliers within normal range.")
        return
    for inc in incidents:
        print(f"\nSupplier: {inc['supplier_name']} ({inc['supplier_id']})")
        print(f"  Quality Score : {inc['quality_score']}%")
        print(f"  On-Time Rate  : {inc['on_time_rate']}%")
        print(f"  Max Delay     : {inc['max_delay_days']} day(s)")
        print(f"  Price Index   : {inc['price_index']}")
        print("  Issues Detected:")
        for issue in inc["issues"]:
            print(f"    - {issue}")


if __name__ == "__main__":
    _print_report(run())
