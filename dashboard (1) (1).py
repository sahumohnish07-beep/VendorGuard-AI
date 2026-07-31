"""
dashboard.py — VendorGuard AI Control Room
--------------------------------------------
A Streamlit frontend that runs the live 4-agent pipeline
(Vendor Monitor -> Risk Analyzer -> Decision Agent -> Procurement Agent)
and renders the results as a supply-chain control-room view.

Run:
    pip install streamlit plotly
    streamlit run dashboard.py
"""

import sys
import os
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from agent1_vendor_monitor import run as run_vendor_monitor
from agent2_risk_analyzer import run as run_risk_analyzer
from agent3_decision_agent import run as run_decision_agent
from agent4_procurement_agent import run as run_procurement_agent
from data_loader import load_suppliers

# ─────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VendorGuard AI — Control Room",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────
BG = "#0B1220"
PANEL = "#121B2E"
PANEL_2 = "#16213A"
BORDER = "#24304A"
TEXT = "#F5F7FA"
TEXT_MUTED = "#7C8AA5"
HIGH = "#F0553A"
MED = "#F5A623"
LOW = "#2DD4BF"
NEUTRAL = "#4C5D7A"

SEVERITY_COLOR = {"HIGH": HIGH, "MEDIUM": MED, "LOW": LOW}

# ─────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG};
    color: {TEXT};
}}
.stApp {{ background-color: {BG}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; max-width: 1280px; }}

.mono {{ font-family: 'IBM Plex Mono', monospace; }}

/* ── Top bar ───────────────────────────────────── */
.vg-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}}
.vg-title {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.1rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: {TEXT};
    margin: 0;
}}
.vg-title span {{ color: {MED}; }}
.vg-subtitle {{
    color: {TEXT_MUTED};
    font-size: 0.92rem;
    margin-top: 0.3rem;
}}

/* ── Status pills row ──────────────────────────── */
.pillrow {{ display:flex; gap:10px; margin-top: 1.4rem; flex-wrap: wrap; }}
.pill {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 999px;
    padding: 6px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: {TEXT_MUTED};
    display:flex; align-items:center; gap:8px;
}}
.dot {{ width:7px; height:7px; border-radius:50%; display:inline-block; }}
.pulse {{ animation: pulse 1.6s ease-in-out infinite; }}
@keyframes pulse {{
    0%   {{ box-shadow: 0 0 0 0 rgba(240,85,58,0.55); }}
    70%  {{ box-shadow: 0 0 0 7px rgba(240,85,58,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(240,85,58,0); }}
}}

/* ── Section headers ───────────────────────────── */
.vg-section {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    border-bottom: 1px solid {BORDER};
    padding-bottom: 8px;
    margin: 2.4rem 0 1rem 0;
}}

/* ── Supplier cards ────────────────────────────── */
.vg-card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 16px 18px;
    height: 100%;
}}
.vg-card-top {{ display:flex; justify-content:space-between; align-items:flex-start; }}
.vg-card-name {{ font-weight: 600; font-size: 0.98rem; color: {TEXT}; }}
.vg-card-id {{ font-family:'IBM Plex Mono',monospace; font-size: 0.7rem; color:{TEXT_MUTED}; }}
.vg-badge {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    padding: 3px 9px;
    border-radius: 999px;
}}
.vg-metric-row {{ display:flex; gap:18px; margin-top:12px; }}
.vg-metric {{ font-family:'IBM Plex Mono',monospace; }}
.vg-metric-val {{ font-size: 1.05rem; font-weight:600; color:{TEXT}; }}
.vg-metric-lbl {{ font-size: 0.66rem; color:{TEXT_MUTED}; text-transform:uppercase; letter-spacing:0.05em; }}

/* ── Reasoning chain flow ──────────────────────── */
.chain-wrap {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-left: 3px solid var(--sev-color);
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
}}
.chain-head {{ display:flex; justify-content:space-between; align-items:center; margin-bottom: 14px; }}
.chain-title {{ font-weight:600; font-size: 1rem; color:{TEXT}; }}
.chain-sub {{ font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:{TEXT_MUTED}; }}
.chain-flow {{ display:flex; align-items:stretch; gap:0; flex-wrap: wrap; }}
.chain-step {{
    background: {PANEL_2};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    color: {TEXT};
    min-width: 140px;
}}
.chain-arrow {{
    display:flex; align-items:center; justify-content:center;
    color: {TEXT_MUTED}; font-size: 1rem; padding: 0 8px;
}}
.chain-impact {{
    margin-top: 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    color: var(--sev-color);
    font-weight: 600;
}}
.decision-line {{
    margin-top: 10px;
    font-size: 0.85rem;
    color: {TEXT_MUTED};
    border-top: 1px dashed {BORDER};
    padding-top: 10px;
}}
.decision-line b {{ color: {TEXT}; }}

/* ── PR queue table ────────────────────────────── */
.pr-row {{
    display:grid;
    grid-template-columns: 100px 1fr 1fr 120px 130px 150px;
    gap: 10px;
    padding: 12px 14px;
    border-bottom: 1px solid {BORDER};
    font-size: 0.84rem;
    align-items:center;
}}
.pr-row.head {{
    font-family:'IBM Plex Mono',monospace;
    font-size:0.68rem;
    text-transform:uppercase;
    letter-spacing:0.05em;
    color:{TEXT_MUTED};
    border-bottom: 1px solid {BORDER};
}}
.pr-id {{ font-family:'IBM Plex Mono',monospace; color:{MED}; }}
.status-chip {{
    font-family:'IBM Plex Mono',monospace;
    font-size:0.68rem;
    padding: 3px 8px;
    border-radius:6px;
    background: {PANEL_2};
    border: 1px solid {BORDER};
    color: {TEXT_MUTED};
    width: fit-content;
}}

/* Streamlit button restyle */
div.stButton > button {{
    background: {MED};
    color: #0B1220;
    border: none;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.04em;
    padding: 0.55rem 1.4rem;
    border-radius: 8px;
}}
div.stButton > button:hover {{ background: #ffbb4d; color: #0B1220; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────
def badge(text, color):
    return (f'<span class="vg-badge" style="background:{color}22;'
            f'color:{color};border:1px solid {color}55;">{text}</span>')


def dot(color, pulsing=False):
    cls = "dot pulse" if pulsing else "dot"
    return f'<span class="{cls}" style="background:{color};box-shadow:0 0 6px {color};"></span>'


@st.cache_data(show_spinner=False)
def get_supplier_count():
    return len(load_suppliers())


def run_pipeline():
    incidents = run_vendor_monitor()
    assessments = run_risk_analyzer(incidents)
    decisions = run_decision_agent(assessments)
    results = run_procurement_agent(decisions)
    return results


# ─────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────
left, right = st.columns([3, 1])
with left:
    st.markdown('<div class="vg-eyebrow">SUPPLY CHAIN // AUTONOMOUS AGENT PIPELINE</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="vg-title">VENDOR<span>GUARD</span> AI</h1>', unsafe_allow_html=True)
    st.markdown('<div class="vg-subtitle">Monitor → Assess → Decide → Act — a live procurement risk control room.</div>', unsafe_allow_html=True)
with right:
    st.write("")
    run_clicked = st.button("▶  RUN PIPELINE", use_container_width=True)

if "results" not in st.session_state or run_clicked:
    with st.spinner("Running agent pipeline..."):
        st.session_state["results"] = run_pipeline()
        st.session_state["ts"] = datetime.now().strftime("%H:%M:%S")

results = st.session_state["results"]
ts = st.session_state["ts"]

high_n = sum(1 for r in results if r["severity"] == "HIGH")
med_n = sum(1 for r in results if r["severity"] == "MEDIUM")
low_n = sum(1 for r in results if r["severity"] == "LOW")
pr_n = sum(1 for r in results if r.get("purchase_request"))
total_impact = sum(r.get("estimated_impact_inr") or 0 for r in results)

st.markdown(f"""
<div class="pillrow">
    <div class="pill">{dot(NEUTRAL)} SUPPLIERS TRACKED&nbsp;<b class="mono">{get_supplier_count()}</b></div>
    <div class="pill">{dot(HIGH, pulsing=high_n>0)} HIGH RISK&nbsp;<b class="mono">{high_n}</b></div>
    <div class="pill">{dot(MED)} MEDIUM RISK&nbsp;<b class="mono">{med_n}</b></div>
    <div class="pill">{dot(LOW)} LOW RISK&nbsp;<b class="mono">{low_n}</b></div>
    <div class="pill">{dot(TEXT_MUTED)} PRs GENERATED&nbsp;<b class="mono">{pr_n}</b></div>
    <div class="pill">{dot(TEXT_MUTED)} LAST RUN&nbsp;<b class="mono">{ts}</b></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────
# VENDOR OVERVIEW CARDS
# ─────────────────────────────────────────────────────────────────────────
st.markdown('<div class="vg-section">Vendor Overview</div>', unsafe_allow_html=True)

cols = st.columns(3)
for i, r in enumerate(results):
    color = SEVERITY_COLOR[r["severity"]]
    with cols[i % 3]:
        st.markdown(f"""
        <div class="vg-card">
            <div class="vg-card-top">
                <div>
                    <div class="vg-card-name">{r['supplier_name']}</div>
                    <div class="vg-card-id">{r['supplier_id']}</div>
                </div>
                {badge(r['severity'], color)}
            </div>
            <div class="vg-metric-row">
                <div class="vg-metric">
                    <div class="vg-metric-val">{r['quality_score']:.0f}%</div>
                    <div class="vg-metric-lbl">Quality</div>
                </div>
                <div class="vg-metric">
                    <div class="vg-metric-val">{r['on_time_rate']:.0f}%</div>
                    <div class="vg-metric-lbl">On-Time</div>
                </div>
                <div class="vg-metric">
                    <div class="vg-metric-val">{r['max_delay_days']}d</div>
                    <div class="vg-metric-lbl">Max Delay</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

# ─────────────────────────────────────────────────────────────────────────
# ACTIVE INCIDENTS — REASONING CHAIN
# ─────────────────────────────────────────────────────────────────────────
st.markdown('<div class="vg-section">Active Incidents — Agent Reasoning Chain</div>', unsafe_allow_html=True)

acted = [r for r in results if r["action"] != "MONITOR_ONLY"]

if not acted:
    st.markdown(f'<div style="color:{TEXT_MUTED};font-family:IBM Plex Mono,monospace;">No active incidents. All suppliers within tolerance.</div>', unsafe_allow_html=True)

for r in acted:
    color = SEVERITY_COLOR[r["severity"]]
    steps = r.get("reasoning_chain", [])
    step_html = ""
    for j, step in enumerate(steps):
        clean = step.replace("-> ", "")
        step_html += f'<div class="chain-step">{clean}</div>'
        if j < len(steps) - 1:
            step_html += '<div class="chain-arrow">→</div>'

    impact_line = ""
    if r.get("estimated_impact_inr"):
        impact_line = f'<div class="chain-impact">≈ ₹{r["estimated_impact_inr"]:,.0f} estimated exposure</div>'

    pr_line = ""
    if r.get("purchase_request"):
        pr_line = (f'<div class="decision-line">→ <b>{r["procurement_action"]}</b> · '
                    f'PR <b>{r["purchase_request"]["pr_id"]}</b> · backup: '
                    f'<b>{r["backup_supplier"]}</b> (score {r["backup_score"]})</div>')

    llm_line = ""
    if r.get("llm_explanation"):
        llm_line = (f'<div class="decision-line">🤖 <b>AI summary:</b> '
                    f'{r["llm_explanation"]}</div>')

    st.markdown(f"""
    <div class="chain-wrap" style="--sev-color:{color};">
        <div class="chain-head">
            <div class="chain-title">{r['supplier_name']} {f"— {r['product']}" if r.get('product') else ""}</div>
            <div class="chain-sub">{badge(r['severity'], color)}</div>
        </div>
        <div class="chain-flow">{step_html}</div>
        {impact_line}
        {pr_line}
        {llm_line}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────
# COST IMPACT CHART
# ─────────────────────────────────────────────────────────────────────────
if acted:
    st.markdown('<div class="vg-section">Estimated Exposure by Supplier</div>', unsafe_allow_html=True)

    names = [r["supplier_name"] for r in acted]
    impacts = [r.get("estimated_impact_inr") or 0 for r in acted]
    colors = [SEVERITY_COLOR[r["severity"]] for r in acted]

    fig = go.Figure(go.Bar(
        x=impacts, y=names, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"₹{v:,.0f}" for v in impacts],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", color=TEXT_MUTED, size=12),
    ))
    fig.update_layout(
        plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(family="Inter", color=TEXT_MUTED),
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(160, 60 * len(names)),
        xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, title=None),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────────────────────────────────
# PURCHASE REQUEST QUEUE
# ─────────────────────────────────────────────────────────────────────────
st.markdown('<div class="vg-section">Procurement Queue</div>', unsafe_allow_html=True)

prs = [r for r in results if r.get("purchase_request")]

if not prs:
    st.markdown(f'<div style="color:{TEXT_MUTED};font-family:IBM Plex Mono,monospace;">Queue is empty.</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="pr-row head">
        <div>PR ID</div><div>Original Supplier</div><div>Backup</div>
        <div>Severity</div><div>Impact</div><div>Status</div>
    </div>
    """, unsafe_allow_html=True)
    for r in prs:
        pr = r["purchase_request"]
        color = SEVERITY_COLOR[r["severity"]]
        st.markdown(f"""
        <div class="pr-row">
            <div class="pr-id">{pr['pr_id']}</div>
            <div>{pr['original_supplier']}</div>
            <div>{pr['backup_supplier']}</div>
            <div>{badge(r['severity'], color)}</div>
            <div class="mono">{'₹' + format(pr['estimated_impact_inr'], ',.0f') if pr.get('estimated_impact_inr') else '—'}</div>
            <div><span class="status-chip">{pr['status']}</span></div>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.markdown(f'<div style="color:{TEXT_MUTED};font-family:IBM Plex Mono,monospace;font-size:0.7rem;margin-top:2rem;">VendorGuard AI · agent pipeline demo · local simulation, no external calls</div>', unsafe_allow_html=True)
