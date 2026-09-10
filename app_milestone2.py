"""Milestone 2 — Risk Assessment & SWOT Analysis dashboard (Streamlit).

Reads a project submitted in Milestone 1 (same database.py / same DB as app.py),
then runs it through the risk engine, SWOT generator and feasibility engine.

Run with:
    streamlit run app_milestone2.py
"""
import streamlit as st

from database import get_all_projects, get_project_by_id, init_db
from risk_engine import (
    calculate_risk,
    calculate_success_probability,
    get_risk_status,
)
from swot_analysis import generate_swot
from feasibility import calculate_feasibility

st.set_page_config(
    page_title="Milestone 2 — Risk & SWOT",
    page_icon="\U0001F4CA",
    layout="wide",
)

init_db()

st.title("Milestone 2 • Risk Assessment & SWOT Analysis")
st.caption("AI-powered risk scoring and strategic evaluation, built on top of your Milestone 1 project data.")

# ---------------------------------------------------------------------------
# STEP 21 (adapted) — pick a Milestone-1 project instead of typing one blind
# ---------------------------------------------------------------------------
projects = get_all_projects()

if not projects:
    st.warning(
        "No projects found yet. Submit one at the Milestone 1 app (`python app.py` -> /submit) first."
    )
    st.stop()

project_options = {f'#{p["id"]} — {p["startup_name"]} ({p["industry"]})': p["id"] for p in projects}
selected_label = st.selectbox("Choose a Milestone 1 project", list(project_options.keys()))
project = get_project_by_id(project_options[selected_label])

with st.expander("Project details (from Milestone 1)", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Startup", project["startup_name"])
    col_b.metric("Industry", project["industry"])
    col_c.metric("Budget", f'${float(project["budget"]):,.0f}')
    st.write(f'**Business model:** {project["business_model"]}  •  **Target market:** {project["target_market"]}')
    st.write(project["project_description"])

st.divider()

# ---------------------------------------------------------------------------
# STEP 21 — Risk Assessment inputs
# ---------------------------------------------------------------------------
st.header("Risk Assessment")

col1, col2 = st.columns(2)

with col1:
    market_competition = st.selectbox("Market Competition", ["Low", "Medium", "High"])
    team_expertise = st.selectbox("Team Expertise", ["Low", "Medium", "High"])
    resource_availability = st.selectbox("Resource Availability", ["Limited", "Moderate", "Good"])

with col2:
    innovation_level = st.selectbox("Innovation Level", ["Low", "Medium", "High"])
    market_research = st.selectbox("Market Research", ["Limited", "Moderate", "Strong"])

# ---------------------------------------------------------------------------
# STEP 22 — Calculate Risk
# ---------------------------------------------------------------------------
risk_score = calculate_risk(
    market_competition,
    team_expertise,
    resource_availability,
    innovation_level,
    market_research,
)
risk_status = get_risk_status(risk_score)
success_probability = calculate_success_probability(risk_score)

# ---------------------------------------------------------------------------
# STEP 23 — Display Risk Score
# ---------------------------------------------------------------------------
st.subheader("Risk Score")
col1, col2 = st.columns(2)

with col1:
    st.metric("Overall Risk Score", risk_score)

with col2:
    if risk_status == "HIGH RISK":
        st.error(risk_status)
    elif risk_status == "MEDIUM RISK":
        st.warning(risk_status)
    else:
        st.success(risk_status)

# ---------------------------------------------------------------------------
# STEP 24 — Display Success Probability
# ---------------------------------------------------------------------------
st.subheader("Success Probability")
st.progress(success_probability / 100)
st.write(f"{success_probability}%")

st.divider()

# ---------------------------------------------------------------------------
# STEP 25 — Generate SWOT Automatically
# ---------------------------------------------------------------------------
swot = generate_swot(
    team_expertise,
    innovation_level,
    market_competition,
    resource_availability,
    market_research,
)

# ---------------------------------------------------------------------------
# STEP 26 — Display SWOT
# ---------------------------------------------------------------------------
st.header("SWOT Analysis")

col1, col2 = st.columns(2)

with col1:
    st.success("### Strengths")
    for item in swot["Strengths"]:
        st.write("•", item)
    if not swot["Strengths"]:
        st.caption("None flagged for the current inputs.")

with col2:
    st.error("### Weaknesses")
    for item in swot["Weaknesses"]:
        st.write("•", item)
    if not swot["Weaknesses"]:
        st.caption("None flagged for the current inputs.")

col3, col4 = st.columns(2)

with col3:
    st.info("### Opportunities")
    for item in swot["Opportunities"]:
        st.write("•", item)

with col4:
    st.warning("### Threats")
    for item in swot["Threats"]:
        st.write("•", item)

st.divider()

# ---------------------------------------------------------------------------
# STEP 27 — Feasibility Assessment
# ---------------------------------------------------------------------------
st.header("Project Feasibility")

market_opportunity = st.slider("Market Opportunity", 0, 100, 50)
team_capability = st.slider("Team Capability", 0, 100, 50)
competitive_advantage = st.slider("Competitive Advantage", 0, 100, 50)
resource_score = st.slider("Resource Availability", 0, 100, 50)

feasibility_score = calculate_feasibility(
    market_opportunity,
    team_capability,
    competitive_advantage,
    resource_score,
)

st.metric("Feasibility Score", f"{feasibility_score}%")

st.divider()

# ---------------------------------------------------------------------------
# STEP 28 — Final Milestone 2 summary
# ---------------------------------------------------------------------------
st.header("Final Recommendation")

if feasibility_score >= 80:
    verdict = "Highly Feasible"
elif feasibility_score >= 60:
    verdict = "Feasible"
elif feasibility_score >= 40:
    verdict = "Moderately Feasible"
else:
    verdict = "Not Feasible"

st.metric("Verdict", verdict)
st.write(
    f'Based on a **{risk_status.title()}** profile ({risk_score}/100, '
    f'{success_probability}% estimated success probability) and a '
    f'**{feasibility_score}%** feasibility score, **{project["startup_name"]}** is assessed as **{verdict}**.'
)
