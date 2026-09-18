"""Milestone 3 – AI Recommendation Engine.

Converts Milestone 2 risk scores (0-100 scale from risk_engine.py) into
actionable recommendation cards structured as:
    {"title": str, "priority": str, "description": str}

Risk scores are normalized internally to a 1-5 scale before applying the
threshold rules defined in the Milestone 3 specification.
"""

# Budget threshold above which a "Develop MVP First" recommendation is added.
HIGH_BUDGET_THRESHOLD = 500_000


def _normalize_score(score_0_100: float) -> float:
    """Convert a 0-100 risk engine score to a 1-5 scale."""
    return 1 + (score_0_100 / 100) * 4


def calculate_priority(score_1_5: float) -> str:
    """Return a priority label based on a 1-5 risk score."""
    if score_1_5 >= 4.5:
        return "Critical"
    elif score_1_5 >= 3.5:
        return "High"
    else:
        return "Medium"


def build_recommendation_card(title: str, priority: str, description: str) -> dict:
    """Return a single recommendation card dict."""
    return {"title": title, "priority": priority, "description": description}


def generate_recommendations(risk_scores: dict, budget: float = 0) -> list:
    """Generate a list of recommendation cards from Milestone 2 outputs.

    Parameters
    ----------
    risk_scores : dict
        Keys (all optional, values in 0-100 scale):
            financial_risk, competition_risk, operational_risk, technical_risk,
            market_risk, overall_risk
    budget : float
        Project budget in monetary units.

    Returns
    -------
    list of dict  – each with keys: title, priority, description
    """
    recommendations = []

    # -------------------------------------------------------------------
    # Financial Risk  ≥ 4 on 1-5 scale  →  Secure Additional Funding
    # -------------------------------------------------------------------
    financial_raw = risk_scores.get("financial_risk", 0)
    financial_score = _normalize_score(financial_raw)
    if financial_score >= 4:
        recommendations.append(
            build_recommendation_card(
                title="Secure Additional Funding",
                priority="Critical",
                description=(
                    "Current budget is insufficient for full project execution. "
                    "Financial resources are at risk of running out before launch. "
                    "Seek investors, grants, or strategic partnerships immediately."
                ),
            )
        )

    # -------------------------------------------------------------------
    # Competition Risk  ≥ 4  →  Build Differentiation Strategy
    # -------------------------------------------------------------------
    competition_raw = risk_scores.get("competition_risk", 0)
    competition_score = _normalize_score(competition_raw)
    if competition_score >= 4:
        recommendations.append(
            build_recommendation_card(
                title="Build Differentiation Strategy",
                priority="High",
                description=(
                    "Market competition is intense. Existing players have significant "
                    "advantages. Identify a unique value proposition and build a clear "
                    "brand differentiation strategy to capture and defend market share."
                ),
            )
        )

    # -------------------------------------------------------------------
    # Operational Risk  ≥ 4  →  Reduce Operational Costs
    # -------------------------------------------------------------------
    operational_raw = risk_scores.get("operational_risk", 0)
    operational_score = _normalize_score(operational_raw)
    if operational_score >= 4:
        recommendations.append(
            build_recommendation_card(
                title="Reduce Operational Costs",
                priority="High",
                description=(
                    "Operational inefficiencies are likely to drain resources and slow "
                    "execution. Audit current workflows, introduce automation where "
                    "possible, and streamline team structures."
                ),
            )
        )

    # -------------------------------------------------------------------
    # Technical Risk  ≥ 4  →  Prototype and Validate Technology
    # -------------------------------------------------------------------
    technical_raw = risk_scores.get("technical_risk", 0)
    technical_score = _normalize_score(technical_raw)
    if technical_score >= 4:
        recommendations.append(
            build_recommendation_card(
                title="Prototype and Validate Technology",
                priority="High",
                description=(
                    "The core technology carries significant uncertainty. Build a focused "
                    "prototype to validate feasibility before committing full development "
                    "resources. Run structured proof-of-concept sprints."
                ),
            )
        )

    # -------------------------------------------------------------------
    # High Investment  →  Develop MVP First
    # -------------------------------------------------------------------
    if float(budget or 0) > HIGH_BUDGET_THRESHOLD:
        recommendations.append(
            build_recommendation_card(
                title="Develop MVP First",
                priority="Medium",
                description=(
                    "High-investment projects benefit from early market validation. "
                    "Release a Minimum Viable Product to real users before scaling "
                    "the full product, reducing financial exposure."
                ),
            )
        )

    # -------------------------------------------------------------------
    # Fallback – overall risk
    # -------------------------------------------------------------------
    if not recommendations:
        overall_raw = risk_scores.get("overall_risk", risk_scores.get("market_risk", 0))
        overall_score = _normalize_score(overall_raw)
        if overall_score >= 3:
            recommendations.append(
                build_recommendation_card(
                    title="Monitor and Review Risks Periodically",
                    priority="Medium",
                    description=(
                        "Risk levels are moderate. Establish a regular risk review cadence "
                        "and keep contingency plans ready for the most likely risk scenarios."
                    ),
                )
            )
        else:
            recommendations.append(
                build_recommendation_card(
                    title="Proceed with Structured Execution",
                    priority="Medium",
                    description=(
                        "Overall risk profile is favourable. Maintain current momentum, "
                        "track KPIs closely and adapt the roadmap as market conditions evolve."
                    ),
                )
            )

    return recommendations
