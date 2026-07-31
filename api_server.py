"""
api_server.py — VendorGuard AI Flask API Server
-------------------------------------------------
Serves the HTML frontend and exposes the 4-agent pipeline
as JSON REST endpoints so the static dashboard can fetch live data.

Endpoints:
    GET  /                  → serves the HTML executive dashboard
    GET  /api/pipeline      → runs the full pipeline and returns results
    GET  /api/suppliers     → returns raw supplier data
    GET  /api/inventory     → returns raw inventory data
    GET  /api/deliveries    → returns delivery data
    GET  /api/export        → downloads a CSV report
    POST /api/pipeline/run  → force re-run the pipeline (clears cache)
    POST /api/approve/<id>  → approve a purchase request

Run:
    python api_server.py
"""

import sys
import os
import json
import csv
import io
from datetime import datetime

# Ensure the console can handle Unicode characters
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from flask import Flask, jsonify, send_from_directory, request, Response
from flask_cors import CORS

# Ensure local imports work
sys.path.insert(0, os.path.dirname(__file__))

from agent1_vendor_monitor import run as run_vendor_monitor
from agent2_risk_analyzer import run as run_risk_analyzer
from agent3_decision_agent import run as run_decision_agent
from agent4_procurement_agent import run as run_procurement_agent
from data_loader import load_suppliers, load_inventory, load_deliveries, load_purchase_orders

app = Flask(__name__, static_folder="stitch_vendorguard_ai_platform")
CORS(app)

# ─── In-memory cache for pipeline results ───────────────────────────────
_pipeline_cache = {
    "results": None,
    "timestamp": None,
}

QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "procurement_queue.json")


def _run_pipeline():
    """Execute the full 4-agent pipeline and cache results."""
    incidents = run_vendor_monitor()
    assessments = run_risk_analyzer(incidents)
    decisions = run_decision_agent(assessments)
    results = run_procurement_agent(decisions)

    _pipeline_cache["results"] = results
    _pipeline_cache["timestamp"] = datetime.now().isoformat(timespec="seconds")

    return results


def _ensure_pipeline():
    """Run the pipeline if not yet cached."""
    if _pipeline_cache["results"] is None:
        _run_pipeline()
    return _pipeline_cache["results"]


def _serialize(obj):
    """Recursively make objects JSON-serializable."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    return obj


def _build_full_response(results):
    """Build a comprehensive API response including ALL suppliers."""
    all_suppliers = load_suppliers()
    all_inventory = load_inventory()
    all_deliveries = load_deliveries()
    all_purchase_orders = load_purchase_orders()

    # Build a map of flagged supplier IDs for quick lookup
    flagged_ids = {r["supplier_id"] for r in results}

    # Build supplier overview (ALL suppliers, not just flagged)
    supplier_overview = []
    for s in all_suppliers:
        sid = s["supplier_id"]
        # Find inventory for this supplier
        inv = next((i for i in all_inventory if i["supplier"] == sid), None)
        # Find deliveries for this supplier
        delivs = [d for d in all_deliveries if d["supplier"] == sid]
        # Find pipeline result if flagged
        pipeline_result = next((r for r in results if r["supplier_id"] == sid), None)

        severity = pipeline_result["severity"] if pipeline_result else "HEALTHY"
        action = pipeline_result["action"] if pipeline_result else "NO_ISSUES"

        supplier_overview.append({
            "supplier_id": sid,
            "supplier_name": s["name"],
            "quality_score": s["quality_score"],
            "on_time_rate": s["on_time_rate"],
            "avg_delivery_days": s["avg_delivery_days"],
            "price_index": s["price_index"],
            "severity": severity,
            "action": action,
            "product": inv["product"] if inv else None,
            "current_stock": inv["current_stock"] if inv else None,
            "safety_stock": inv["safety_stock"] if inv else None,
            "daily_usage": inv["daily_usage"] if inv else None,
            "total_deliveries": len(delivs),
            "estimated_impact_inr": pipeline_result.get("estimated_impact_inr") if pipeline_result else 0,
            "purchase_request": pipeline_result.get("purchase_request") if pipeline_result else None,
            "reasoning_chain": pipeline_result.get("reasoning_chain") if pipeline_result else None,
            "decision_explanation": pipeline_result.get("decision_explanation") if pipeline_result else None,
            "llm_explanation": pipeline_result.get("llm_explanation") if pipeline_result else None,
            "backup_supplier": pipeline_result.get("backup_supplier") if pipeline_result else None,
            "backup_score": pipeline_result.get("backup_score") if pipeline_result else None,
            "procurement_action": pipeline_result.get("procurement_action") if pipeline_result else None,
            "max_delay_days": pipeline_result.get("max_delay_days", 0) if pipeline_result else 0,
            "hours_to_stockout": pipeline_result.get("hours_to_stockout") if pipeline_result else None,
            "issues": pipeline_result.get("issues") if pipeline_result else [],
        })

    # Sort: HIGH first, then MEDIUM, LOW, HEALTHY
    sev_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "HEALTHY": 3}
    supplier_overview.sort(key=lambda x: sev_order.get(x["severity"], 4))

    # Count by severity
    high_n = sum(1 for s in supplier_overview if s["severity"] == "HIGH")
    med_n = sum(1 for s in supplier_overview if s["severity"] == "MEDIUM")
    low_n = sum(1 for s in supplier_overview if s["severity"] == "LOW")
    healthy_n = sum(1 for s in supplier_overview if s["severity"] == "HEALTHY")
    total_impact = sum(s["estimated_impact_inr"] or 0 for s in supplier_overview)
    pr_count = sum(1 for s in supplier_overview if s["purchase_request"])

    # Delivery timeline
    delivery_timeline = []
    for d in all_deliveries:
        supplier = next((s for s in all_suppliers if s["supplier_id"] == d["supplier"]), None)
        delivery_timeline.append({
            "order_id": d["order_id"],
            "supplier_id": d["supplier"],
            "supplier_name": supplier["name"] if supplier else d["supplier"],
            "expected_date": d["expected_date"].isoformat() if d["expected_date"] else None,
            "actual_date": d["actual_date"].isoformat() if d["actual_date"] else None,
            "status": d["status"],
            "delay_days": (d["actual_date"] - d["expected_date"]).days if d["actual_date"] and d["expected_date"] else 0,
        })

    # Purchase orders
    po_list = []
    for po in all_purchase_orders:
        supplier = next((s for s in all_suppliers if s["supplier_id"] == po["supplier"]), None)
        po_list.append({
            "order_id": po["order_id"],
            "supplier_id": po["supplier"],
            "supplier_name": supplier["name"] if supplier else po["supplier"],
            "quantity": po["quantity"],
            "amount": po["amount"],
            "order_date": po["order_date"].isoformat() if po["order_date"] else None,
        })

    return {
        "status": "ok",
        "timestamp": _pipeline_cache["timestamp"],
        "supplier_count": len(all_suppliers),
        "summary": {
            "high": high_n,
            "medium": med_n,
            "low": low_n,
            "healthy": healthy_n,
            "total_impact": total_impact,
            "pr_count": pr_count,
            "avg_on_time": round(sum(s["on_time_rate"] for s in all_suppliers) / len(all_suppliers), 1) if all_suppliers else 0,
            "avg_quality": round(sum(s["quality_score"] for s in all_suppliers) / len(all_suppliers), 1) if all_suppliers else 0,
        },
        "suppliers": supplier_overview,
        "results": _serialize(results),
        "deliveries": delivery_timeline,
        "purchase_orders": po_list,
    }


# ─── Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def serve_frontend():
    """Serve the executive dashboard HTML."""
    return send_from_directory("stitch_vendorguard_ai_platform", "code.html")


@app.route("/api/pipeline", methods=["GET"])
def get_pipeline():
    """Return cached pipeline results (runs once on first call)."""
    results = _ensure_pipeline()
    return jsonify(_build_full_response(results))


@app.route("/api/pipeline/run", methods=["POST"])
def run_pipeline_endpoint():
    """Force re-run the pipeline and return fresh results."""
    results = _run_pipeline()
    return jsonify(_build_full_response(results))


@app.route("/api/suppliers", methods=["GET"])
def get_suppliers():
    """Return raw supplier data."""
    suppliers = load_suppliers()
    return jsonify({"status": "ok", "suppliers": suppliers})


@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    """Return raw inventory data."""
    inventory = load_inventory()
    return jsonify({"status": "ok", "inventory": inventory})


@app.route("/api/deliveries", methods=["GET"])
def get_deliveries():
    """Return delivery data."""
    deliveries = load_deliveries()
    return jsonify({"status": "ok", "deliveries": _serialize(deliveries)})


@app.route("/api/export", methods=["GET"])
def export_report():
    """Generate and download a CSV report of all supplier risk data."""
    results = _ensure_pipeline()
    response_data = _build_full_response(results)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Supplier ID", "Supplier Name", "Severity", "Quality Score (%)",
        "On-Time Rate (%)", "Max Delay (days)", "Product", "Current Stock",
        "Safety Stock", "Daily Usage", "Hours to Stockout",
        "Estimated Impact (INR)", "Action", "Procurement Action",
        "Backup Supplier", "PR ID", "PR Status", "Issues", "Decision Explanation"
    ])

    for s in response_data["suppliers"]:
        pr = s.get("purchase_request") or {}
        writer.writerow([
            s["supplier_id"],
            s["supplier_name"],
            s["severity"],
            s["quality_score"],
            s["on_time_rate"],
            s.get("max_delay_days", 0),
            s.get("product", ""),
            s.get("current_stock", ""),
            s.get("safety_stock", ""),
            s.get("daily_usage", ""),
            s.get("hours_to_stockout", ""),
            s.get("estimated_impact_inr", 0),
            s.get("action", ""),
            s.get("procurement_action", ""),
            s.get("backup_supplier", ""),
            pr.get("pr_id", ""),
            pr.get("status", ""),
            "; ".join(s.get("issues") or []),
            s.get("decision_explanation", ""),
        ])

    csv_content = output.getvalue()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=vendorguard_report_{timestamp}.csv"}
    )


@app.route("/api/approve/<pr_id>", methods=["POST"])
def approve_pr(pr_id):
    """Approve a purchase request by ID."""
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            queue = json.load(f)
    else:
        return jsonify({"status": "error", "message": "No queue file found"}), 404

    found = False
    for pr in queue:
        if pr["pr_id"] == pr_id:
            pr["status"] = "APPROVED"
            pr["approved_at"] = datetime.now().isoformat(timespec="seconds")
            found = True
            break

    if not found:
        return jsonify({"status": "error", "message": f"PR {pr_id} not found"}), 404

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)

    # Also update cached results
    if _pipeline_cache["results"]:
        for r in _pipeline_cache["results"]:
            if r.get("purchase_request") and r["purchase_request"]["pr_id"] == pr_id:
                r["purchase_request"]["status"] = "APPROVED"

    return jsonify({"status": "ok", "message": f"{pr_id} approved", "pr_id": pr_id})


if __name__ == "__main__":
    # Load .env file if present (for NVIDIA_API_KEY)
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), value)

    print("\n" + "=" * 60)
    print("  VendorGuard AI — API Server")
    print("=" * 60)
    print(f"  Frontend : http://localhost:5000")
    print(f"  API Base : http://localhost:5000/api")
    print(f"  Pipeline : http://localhost:5000/api/pipeline")
    print(f"  Export   : http://localhost:5000/api/export")
    print("=" * 60 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
