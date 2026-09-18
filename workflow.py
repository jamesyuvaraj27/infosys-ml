"""Milestone 3 – Strategic Reasoning Workflow.

Simulates a LangGraph-style multi-stage pipeline.
Real AI agents are NOT required; this is a deterministic workflow
representation as specified in the Milestone 3 documentation.

Pipeline stages:
    1. data_ingestion
    2. risk_analysis
    3. strategic_reasoning
    4. validation
    5. report_generation

Each stage receives the full accumulated state dict and returns an
updated copy. Run the full pipeline with run_workflow().
"""
from __future__ import annotations

from recommendation_engine import generate_recommendations
from risk_mitigation import generate_mitigation


# ---------------------------------------------------------------------------
# Stage 1 – Data Ingestion
# ---------------------------------------------------------------------------

def data_ingestion(
    project: dict,
    risk_scores: dict,
    swot: dict | None = None,
    feasibility_score: float = 0,
) -> dict:
    """Ingest all Milestone 1 & 2 outputs into a unified state dict.

    Parameters
    ----------
    project        : Milestone 1 project row (dict from database.py)
    risk_scores    : dict of risk scores (0-100 scale)
    swot           : dict with Strengths/Weaknesses/Opportunities/Threats lists
    feasibility_score : 0-100 feasibility percentage from feasibility.py

    Returns
    -------
    state dict ready for the next stage
    """
    return {
        "stage": "data_ingestion",
        "status": "completed",
        "project": project,
        "risk_scores": risk_scores,
        "swot": swot or {},
        "feasibility_score": feasibility_score,
        "recommendations": [],
        "mitigations": [],
        "reasoning": [],
        "validation_passed": False,
        "report": {},
    }


# ---------------------------------------------------------------------------
# Stage 2 – Risk Analysis
# ---------------------------------------------------------------------------

def risk_analysis(state: dict) -> dict:
    """Derive individual risk facts and generate mitigation cards."""
    state = dict(state)
    state["stage"] = "risk_analysis"

    mitigations = generate_mitigation(state["risk_scores"])
    state["mitigations"] = mitigations

    # Classify overall risk level
    overall = state["risk_scores"].get("overall_risk", 0)
    if overall >= 70:
        state["overall_risk_level"] = "HIGH RISK"
    elif overall >= 40:
        state["overall_risk_level"] = "MEDIUM RISK"
    else:
        state["overall_risk_level"] = "LOW RISK"

    state["status"] = "completed"
    return state


# ---------------------------------------------------------------------------
# Stage 3 – Strategic Reasoning
# ---------------------------------------------------------------------------

def strategic_reasoning(state: dict) -> dict:
    """Generate recommendations and build the reasoning chain."""
    state = dict(state)
    state["stage"] = "strategic_reasoning"

    budget = float((state["project"] or {}).get("budget", 0) or 0)
    recommendations = generate_recommendations(state["risk_scores"], budget)
    state["recommendations"] = recommendations

    # Build structured reasoning entries:
    # Problem → Analysis → Decision → Expected Benefit
    reasoning = []
    for rec in recommendations:
        reasoning.append(_build_reasoning(rec, state["risk_scores"]))
    state["reasoning"] = reasoning

    state["status"] = "completed"
    return state


def _build_reasoning(rec: dict, risk_scores: dict) -> dict:
    """Map a recommendation back to a Problem/Analysis/Decision/Benefit block."""
    title = rec["title"]

    _reasoning_map = {
        "Secure Additional Funding": {
            "problem": "High Financial Risk",
            "analysis": (
                "Financial resources are insufficient to sustain full project "
                "execution. Budget constraints may block key milestones."
            ),
            "decision": "Secure additional funding through investors, grants or partnerships.",
            "expected_benefit": "Stable cash flow and uninterrupted project delivery.",
        },
        "Build Differentiation Strategy": {
            "problem": "High Competition Risk",
            "analysis": (
                "Many existing competitors hold market share. Entering without a "
                "clear differentiator will result in slow adoption and margin pressure."
            ),
            "decision": "Build a differentiation strategy focusing on unique value and niche targeting.",
            "expected_benefit": "Improved market positioning and reduced competitive pressure.",
        },
        "Reduce Operational Costs": {
            "problem": "High Operational Risk",
            "analysis": (
                "Operational inefficiencies increase burn rate and slow execution. "
                "Processes lack automation and clear accountability."
            ),
            "decision": "Audit and streamline operations; introduce automation tooling.",
            "expected_benefit": "Reduced overhead and faster, more predictable delivery cycles.",
        },
        "Prototype and Validate Technology": {
            "problem": "High Technical Risk",
            "analysis": (
                "Core technology has not been proven at scale. Technical failures "
                "could derail the timeline and require costly re-architecture."
            ),
            "decision": "Build a focused prototype to validate feasibility before full development.",
            "expected_benefit": "Early detection of blockers and reduced development rework.",
        },
        "Develop MVP First": {
            "problem": "High Investment with Unvalidated Market Fit",
            "analysis": (
                "Large budgets increase financial exposure if market fit is not "
                "confirmed early. A full build-out before validation is high risk."
            ),
            "decision": "Release an MVP to real users and iterate based on feedback.",
            "expected_benefit": "Reduced financial exposure and faster product-market fit discovery.",
        },
    }

    entry = _reasoning_map.get(
        title,
        {
            "problem": "Identified Risk",
            "analysis": "Risk factors require attention based on Milestone 2 analysis.",
            "decision": rec["title"],
            "expected_benefit": "Improved project resilience and success probability.",
        },
    )
    return entry


# ---------------------------------------------------------------------------
# Stage 4 – Validation
# ---------------------------------------------------------------------------

def validation(state: dict) -> dict:
    """Validate that the pipeline produced usable outputs."""
    state = dict(state)
    state["stage"] = "validation"

    issues = []
    if not state.get("recommendations"):
        issues.append("No recommendations generated.")
    if not state.get("mitigations"):
        issues.append("No mitigations generated.")
    if not state.get("project"):
        issues.append("Project data missing.")

    state["validation_issues"] = issues
    state["validation_passed"] = len(issues) == 0
    state["status"] = "completed"
    return state


# ---------------------------------------------------------------------------
# Stage 5 – Report Generation
# ---------------------------------------------------------------------------

def report_generation(state: dict) -> dict:
    """Compile the final assessment report."""
    state = dict(state)
    state["stage"] = "report_generation"

    project = state.get("project") or {}
    feasibility = state.get("feasibility_score", 0)

    if feasibility >= 80:
        verdict = "Highly Feasible"
    elif feasibility >= 60:
        verdict = "Feasible"
    elif feasibility >= 40:
        verdict = "Moderately Feasible"
    else:
        verdict = "Not Feasible"

    critical_count = sum(
        1 for r in state["recommendations"] if r["priority"] == "Critical"
    )
    high_count = sum(
        1 for r in state["recommendations"] if r["priority"] == "High"
    )

    state["report"] = {
        "startup_name": project.get("startup_name", "Unknown"),
        "overall_risk_level": state.get("overall_risk_level", "UNKNOWN"),
        "feasibility_score": feasibility,
        "verdict": verdict,
        "total_recommendations": len(state["recommendations"]),
        "critical_recommendations": critical_count,
        "high_recommendations": high_count,
        "summary": (
            f"{project.get('startup_name', 'This project')} has been assessed as "
            f"'{verdict}' with an overall risk profile of "
            f"'{state.get('overall_risk_level', 'Unknown')}'. "
            f"{len(state['recommendations'])} strategic recommendation(s) have been generated, "
            f"including {critical_count} critical and {high_count} high-priority action(s)."
        ),
    }

    state["status"] = "completed"
    return state


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_workflow(
    project: dict,
    risk_scores: dict,
    swot: dict | None = None,
    feasibility_score: float = 0,
) -> dict:
    """Execute the full 5-stage Milestone 3 pipeline and return the final state.

    Parameters
    ----------
    project           : Milestone 1 project dict
    risk_scores       : dict with risk score keys (0-100 scale)
    swot              : SWOT dict (optional)
    feasibility_score : feasibility percentage (optional)

    Returns
    -------
    Fully populated state dict including recommendations, mitigations,
    reasoning, validation result, and final report.
    """
    state = data_ingestion(project, risk_scores, swot, feasibility_score)
    state = risk_analysis(state)
    state = strategic_reasoning(state)
    state = validation(state)
    state = report_generation(state)
    return state


# ---------------------------------------------------------------------------
# Workflow step metadata (used for UI rendering)
# ---------------------------------------------------------------------------

WORKFLOW_STEPS = [
    {
        "name": "Data Ingestion",
        "icon": "📥",
        "description": "Load project data from Milestone 1 & 2 outputs.",
    },
    {
        "name": "Risk Analysis",
        "icon": "🔍",
        "description": "Evaluate risk scores and assign impact levels.",
    },
    {
        "name": "Strategic Reasoning",
        "icon": "🧠",
        "description": "Generate recommendations and reasoning chains.",
    },
    {
        "name": "Validation",
        "icon": "✅",
        "description": "Verify outputs are complete and consistent.",
    },
    {
        "name": "Report Generation",
        "icon": "📊",
        "description": "Compile the final assessment report.",
    },
]
