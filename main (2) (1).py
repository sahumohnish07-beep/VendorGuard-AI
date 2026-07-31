"""
main.py — VendorGuard AI orchestrator
Runs the full pipeline:
  Agent 1 (Vendor Monitor) -> Agent 2 (Risk Analyzer)
  -> Agent 3 (Decision Agent) -> Agent 4 (Procurement Agent)

Usage:
    python main.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from agent1_vendor_monitor import run as run_vendor_monitor
from agent2_risk_analyzer import run as run_risk_analyzer
from agent3_decision_agent import run as run_decision_agent
from agent4_procurement_agent import run as run_procurement_agent


def run_pipeline(verbose=True):
    if verbose:
        print("\n" + "#" * 60)
        print("# VendorGuard AI — Autonomous Procurement Workflow")
        print("#" * 60)

    # Step 1: Detect anomalies
    incidents = run_vendor_monitor()
    if verbose:
        print(f"\n[Step 1] Vendor Monitor found {len(incidents)} supplier(s) with issues.")

    # Step 2: Reason about business impact
    assessments = run_risk_analyzer(incidents)
    if verbose:
        high = sum(1 for a in assessments if a["severity"] == "HIGH")
        med = sum(1 for a in assessments if a["severity"] == "MEDIUM")
        low = sum(1 for a in assessments if a["severity"] == "LOW")
        print(f"[Step 2] Risk Analyzer classified: {high} HIGH, {med} MEDIUM, {low} LOW.")

    # Step 3: Decide what to do
    decisions = run_decision_agent(assessments)
    if verbose:
        actions = sum(1 for d in decisions if d["action"] != "MONITOR_ONLY")
        print(f"[Step 3] Decision Agent triggered action for {actions} case(s).")

    # Step 4: Execute simulated procurement actions
    results = run_procurement_agent(decisions)
    if verbose:
        prs = sum(1 for r in results if r.get("purchase_request"))
        print(f"[Step 4] Procurement Agent created {prs} purchase request(s).")
        print("\n" + "-" * 60)
        print("DETAILED RESULTS")
        print("-" * 60)
        for r in results:
            print(f"\nSupplier   : {r['supplier_name']} ({r['supplier_id']})")
            print(f"Severity   : {r['severity']}")
            print(f"Action     : {r['action']} -> {r['procurement_action']}")
            if r.get("estimated_impact_inr"):
                print(f"₹ Impact   : ₹{r['estimated_impact_inr']:,.0f}")
            if r.get("backup_supplier"):
                print(f"Backup     : {r['backup_supplier']}")
            if r.get("purchase_request"):
                print(f"PR ID      : {r['purchase_request']['pr_id']} "
                      f"[{r['purchase_request']['status']}]")

    return results


if __name__ == "__main__":
    run_pipeline()
