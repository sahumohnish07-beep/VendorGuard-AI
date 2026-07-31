"""
Agent 2 — Risk Assessment Agent
---------------------------------
Takes the incidents from Agent 1 and reasons about *business impact*:
delay + current inventory + daily usage -> time-to-stockout -> ₹ impact.

This is the "explainability" agent: every risk score comes with a
step-by-step chain the demo can show on screen.
"""

from data_loader import load_inventory

# Rough cost-per-unit multiplier used to translate a stockout into ₹ impact.
# In a real system this would come from ERP data; here it's a simple
# illustrative constant tied to purchase order value per unit.
IMPACT_PER_UNIT_SHORTFALL = 1050  # ₹ per unit of unmet daily demand


def _inventory_for_supplier(inventory_rows, supplier_id):
    return [row for row in inventory_rows if row["supplier"] == supplier_id]


def _hours_to_stockout(current_stock, daily_usage):
    if daily_usage <= 0:
        return None
    days = current_stock / daily_usage
    return round(days * 24, 1)


def _severity(delay_days, hours_to_stockout, quality_score):
    """Simple weighted rule -> LOW / MEDIUM / HIGH."""
    score = 0
    if delay_days >= 7:
        score += 2
    elif delay_days >= 3:
        score += 1

    if hours_to_stockout is not None:
        if hours_to_stockout <= 24:
            score += 2
        elif hours_to_stockout <= 72:
            score += 1

    if quality_score < 70:
        score += 1

    if score >= 4:
        return "HIGH"
    elif score >= 2:
        return "MEDIUM"
    return "LOW"


def run(incidents):
    inventory_rows = load_inventory()
    assessments = []

    for inc in incidents:
        sid = inc["supplier_id"]
        inv_rows = _inventory_for_supplier(inventory_rows, sid)

        for inv in inv_rows or [None]:
            if inv is None:
                # No inventory line for this supplier's product — skip stock math
                assessments.append({
                    **inc,
                    "product": None,
                    "current_stock": None,
                    "safety_stock": None,
                    "daily_usage": None,
                    "hours_to_stockout": None,
                    "estimated_impact_inr": None,
                    "severity": _severity(inc["max_delay_days"], None, inc["quality_score"]),
                    "reasoning_chain": [
                        f"Delay = {inc['max_delay_days']} day(s)",
                        "No linked inventory record found for this supplier",
                    ],
                })
                continue

            hours = _hours_to_stockout(inv["current_stock"], inv["daily_usage"])
            below_safety = inv["current_stock"] < inv["safety_stock"]
            shortfall_units = max(inv["safety_stock"] - inv["current_stock"], 0)
            impact = round(shortfall_units * IMPACT_PER_UNIT_SHORTFALL, 2)

            severity = _severity(inc["max_delay_days"], hours, inc["quality_score"])

            reasoning_chain = [
                f"Delay = {inc['max_delay_days']} day(s)",
                f"Inventory = {inv['current_stock']} units (safety stock {inv['safety_stock']})",
                f"Daily demand = {inv['daily_usage']} units",
                f"-> Time to stockout ≈ {hours} hours" if hours is not None else "-> Daily usage unknown",
                f"-> Below safety stock: {'YES' if below_safety else 'no'}",
                f"-> Estimated business impact ≈ ₹{impact:,.0f}" if impact else "-> No immediate ₹ impact",
            ]

            assessments.append({
                **inc,
                "product": inv["product"],
                "current_stock": inv["current_stock"],
                "safety_stock": inv["safety_stock"],
                "daily_usage": inv["daily_usage"],
                "hours_to_stockout": hours,
                "estimated_impact_inr": impact,
                "severity": severity,
                "reasoning_chain": reasoning_chain,
            })

    # Highest risk first
    assessments.sort(key=lambda a: (
        {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[a["severity"]],
        -(a["estimated_impact_inr"] or 0),
    ))
    return assessments


def _print_report(assessments):
    print("=" * 60)
    print("AGENT 2 — RISK ASSESSMENT AGENT")
    print("=" * 60)
    if not assessments:
        print("No incidents to assess.")
        return
    for a in assessments:
        print(f"\nSupplier: {a['supplier_name']} ({a['supplier_id']})"
              f"{' — ' + a['product'] if a.get('product') else ''}")
        print(f"  Severity: {a['severity']}")
        print("  Reasoning:")
        for step in a["reasoning_chain"]:
            print(f"    {step}")


if __name__ == "__main__":
    from agent1_vendor_monitor import run as run_agent1
    _print_report(run(run_agent1()))
