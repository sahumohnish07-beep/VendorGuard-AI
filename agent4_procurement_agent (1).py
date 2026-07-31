"""
Agent 4 — Procurement Agent
------------------------------
Takes decisions from Agent 3 and executes (simulated) procurement actions:
  - Create a purchase request for HIGH-risk/backup switches
  - Notify the warehouse
  - Update a local "procurement queue" (JSON file acts as a mini DB)
  - Generate an approval summary for the procurement manager

Nothing here calls a real ERP — it's a local simulation appropriate for
a hackathon demo, but the structure mirrors what a real integration
(e.g. SAP Ariba / Coupa API call) would look like.
"""

import json
import os
from datetime import datetime

QUEUE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "procurement_queue.json"
)

PR_COUNTER_START = 5000


def _load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)


def _next_pr_id(queue):
    return f"PR{PR_COUNTER_START + len(queue) + 1}"


def _create_purchase_request(decision, queue):
    pr_id = _next_pr_id(queue)
    pr = {
        "pr_id": pr_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "original_supplier": decision["supplier_name"],
        "backup_supplier": decision["backup_supplier"],
        "product": decision.get("product"),
        "severity": decision["severity"],
        "estimated_impact_inr": decision.get("estimated_impact_inr"),
        "status": "PENDING_APPROVAL",
    }
    queue.append(pr)
    return pr


def _notify_warehouse(decision):
    return (
        f"[WAREHOUSE ALERT] {decision['severity']} risk on "
        f"{decision.get('product') or 'incoming shipment'} from "
        f"{decision['supplier_name']}. Prepare for possible backup delivery "
        f"from {decision['backup_supplier']}."
    )


def _approval_summary(decision, pr):
    lines = [
        f"Purchase Request {pr['pr_id']} — awaiting manager approval",
        f"  Supplier flagged : {decision['supplier_name']}",
        f"  Reason           : {decision['decision_explanation']}",
        f"  Backup supplier  : {decision['backup_supplier']} "
        f"(score {decision.get('backup_score')})",
    ]
    if decision.get("estimated_impact_inr"):
        lines.append(f"  Estimated impact : ₹{decision['estimated_impact_inr']:,.0f} if unaddressed")
    return "\n".join(lines)


def run(decisions):
    queue = _load_queue()
    results = []

    for d in decisions:
        if d["action"] == "MONITOR_ONLY":
            results.append({
                **d,
                "procurement_action": "NONE",
                "notification": None,
                "purchase_request": None,
            })
            continue

        pr = _create_purchase_request(d, queue)
        notification = _notify_warehouse(d)
        summary = _approval_summary(d, pr)

        results.append({
            **d,
            "procurement_action": "PURCHASE_REQUEST_CREATED"
                if d["action"] == "EMERGENCY_PROCUREMENT" else "FLAGGED_WITH_BACKUP_READY",
            "notification": notification,
            "purchase_request": pr,
            "approval_summary": summary,
        })

    _save_queue(queue)
    return results


def _print_report(results):
    print("=" * 60)
    print("AGENT 4 — PROCUREMENT AGENT")
    print("=" * 60)
    for r in results:
        print(f"\nSupplier: {r['supplier_name']} ({r['supplier_id']})")
        print(f"  Procurement Action: {r['procurement_action']}")
        if r.get("notification"):
            print(f"  {r['notification']}")
        if r.get("purchase_request"):
            print(f"  Purchase Request : {r['purchase_request']['pr_id']} "
                  f"[{r['purchase_request']['status']}]")
        if r.get("approval_summary"):
            print("  --- Approval Summary ---")
            print("  " + r["approval_summary"].replace("\n", "\n  "))


if __name__ == "__main__":
    from agent1_vendor_monitor import run as run_agent1
    from agent2_risk_analyzer import run as run_agent2
    from agent3_decision_agent import run as run_agent3
    _print_report(run(run_agent3(run_agent2(run_agent1()))))
