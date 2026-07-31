"""
Agent 3 — Decision Agent
--------------------------
Takes risk assessments from Agent 2 and decides what to do:
  HIGH   -> find backup supplier + trigger emergency procurement
  MEDIUM -> flag for manager review, suggest backup as precaution
  LOW    -> no action, log only

Backup supplier selection: among suppliers NOT the current one,
rank by a composite score of quality, on-time rate, and price.
"""

from data_loader import load_suppliers
import llm_client

# A supplier only qualifies as a "safe" backup if it clears this bar.
BACKUP_QUALITY_MIN = 85.0
BACKUP_ON_TIME_MIN = 90.0

# Set to True to have the LLM write the explanation shown to the manager.
# Falls back to the rule-based explanation automatically if the LLM is
# unavailable (no NVIDIA_API_KEY set, no network, etc.) — see llm_client.py.
USE_LLM_EXPLANATION = True


def _llm_explanation(a, severity, action, backup, rule_based_explanation):
    if not USE_LLM_EXPLANATION or not llm_client.is_available():
        return None

    prompt = (
        "You are a procurement risk analyst. Write a 2-3 sentence explanation "
        "for a procurement manager, in plain business English, no bullet points.\n\n"
        f"Supplier: {a['supplier_name']}\n"
        f"Severity: {severity}\n"
        f"Quality score: {a['quality_score']}%\n"
        f"On-time delivery rate: {a['on_time_rate']}%\n"
        f"Max delivery delay: {a['max_delay_days']} day(s)\n"
        f"Action being taken: {action}\n"
        + (f"Recommended backup supplier: {backup['name']}\n" if backup else "")
        + f"Rule-based summary: {rule_based_explanation}\n\n"
        "Explain why this action makes sense and what the manager should watch next."
    )
    return llm_client.generate_explanation(prompt)


def _composite_score(supplier):
    """Higher is better. Simple weighted formula — transparent & tunable."""
    return (
        supplier["quality_score"] * 0.4
        + supplier["on_time_rate"] * 0.4
        + (2 - supplier["price_index"]) * 100 * 0.2  # lower price_index is better
    )


def _qualifies_as_backup(supplier):
    return (
        supplier["quality_score"] >= BACKUP_QUALITY_MIN
        and supplier["on_time_rate"] >= BACKUP_ON_TIME_MIN
    )


def _find_backup_supplier(current_supplier_id, all_suppliers):
    candidates = [s for s in all_suppliers if s["supplier_id"] != current_supplier_id]
    if not candidates:
        return None

    qualified = [s for s in candidates if _qualifies_as_backup(s)]
    pool = qualified if qualified else candidates  # fall back if nobody clears the bar
    pool.sort(key=_composite_score, reverse=True)
    return pool[0]


def run(assessments):
    suppliers = load_suppliers()
    decisions = []

    for a in assessments:
        severity = a["severity"]

        if severity == "HIGH":
            backup = _find_backup_supplier(a["supplier_id"], suppliers)
            action = "EMERGENCY_PROCUREMENT"
            explanation = (
                f"{a['supplier_name']} is HIGH risk "
                f"(delay {a['max_delay_days']}d, quality {a['quality_score']}%). "
                f"Switching to backup supplier to avoid stockout."
            )
        elif severity == "MEDIUM":
            backup = _find_backup_supplier(a["supplier_id"], suppliers)
            action = "FLAG_FOR_REVIEW"
            explanation = (
                f"{a['supplier_name']} shows early warning signs "
                f"(delay {a['max_delay_days']}d). Recommend manager review; "
                f"backup supplier identified as precaution."
            )
        else:
            backup = None
            action = "MONITOR_ONLY"
            explanation = f"{a['supplier_name']} is within acceptable risk range. No action needed."

        llm_explanation = _llm_explanation(a, severity, action, backup, explanation)

        decisions.append({
            **a,
            "action": action,
            "backup_supplier": backup["name"] if backup else None,
            "backup_supplier_id": backup["supplier_id"] if backup else None,
            "backup_score": round(_composite_score(backup), 1) if backup else None,
            "decision_explanation": explanation,
            "llm_explanation": llm_explanation,  # None if LLM unavailable/disabled
        })

    return decisions


def _print_report(decisions):
    print("=" * 60)
    print("AGENT 3 — DECISION AGENT")
    print("=" * 60)
    if not decisions:
        print("No decisions to make.")
        return
    for d in decisions:
        print(f"\nSupplier: {d['supplier_name']} ({d['supplier_id']})")
        print(f"  Action: {d['action']}")
        print(f"  Explanation (rule-based): {d['decision_explanation']}")
        if d.get("llm_explanation"):
            print(f"  Explanation (LLM): {d['llm_explanation']}")
        if d["backup_supplier"]:
            print(f"  Recommended Backup: {d['backup_supplier']} (score {d['backup_score']})")


if __name__ == "__main__":
    from agent1_vendor_monitor import run as run_agent1
    from agent2_risk_analyzer import run as run_agent2
    _print_report(run(run_agent2(run_agent1())))
