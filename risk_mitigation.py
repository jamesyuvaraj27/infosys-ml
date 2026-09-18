"""Milestone 3 – Risk Mitigation Module.

Maps each identified risk to an impact level and mitigation strategy.
Operates on the same 0-100 risk scores produced by risk_engine.py and
normalises to 1-5 internally.

Output structure per item:
    {"risk": str, "impact": str, "mitigation": str, "category": str}
"""


# ---------------------------------------------------------------------------
# Mitigation catalogue
# ---------------------------------------------------------------------------
_MITIGATION_CATALOGUE = {
    "Financial Risk": {
        "category": "financial",
        "mitigation": (
            "Revenue Acceleration: diversify income streams, pursue strategic "
            "partnerships, apply for grants and investor funding, and tighten "
            "cash-flow forecasting."
        ),
    },
    "Competition Risk": {
        "category": "market",
        "mitigation": (
            "Differentiation Strategy: define a unique value proposition, invest "
            "in brand identity, focus on underserved niches, and build network "
            "effects that create switching costs."
        ),
    },
    "Technical Risk": {
        "category": "technical",
        "mitigation": (
            "Prototype Validation: run structured proof-of-concept sprints, hire "
            "specialist consultants, use open-source proven components, and add "
            "technical debt review to the development process."
        ),
    },
    "Team Skill Risk": {
        "category": "operational",
        "mitigation": (
            "Strategic Hiring: identify critical skill gaps, recruit experienced "
            "specialists, launch an upskilling programme, and consider contracting "
            "domain experts in the short term."
        ),
    },
    "Operational Risk": {
        "category": "operational",
        "mitigation": (
            "Automation & Process Optimisation: audit workflows, automate "
            "repetitive tasks, adopt lean project management practices, and "
            "establish clear SLAs across all operational units."
        ),
    },
    "Market Risk": {
        "category": "market",
        "mitigation": (
            "Market Intelligence: conduct regular competitor analysis, track "
            "industry trends, gather continuous customer feedback, and maintain "
            "a flexible product roadmap."
        ),
    },
}

# Mapping from risk_scores dict keys → catalogue entries
_SCORE_KEY_MAP = {
    "financial_risk": "Financial Risk",
    "competition_risk": "Competition Risk",
    "technical_risk": "Technical Risk",
    "operational_risk": "Operational Risk",
    "market_risk": "Market Risk",
    "team_skill_risk": "Team Skill Risk",
}


def _normalize_score(score_0_100: float) -> float:
    """Convert a 0-100 risk engine score to a 1-5 scale."""
    return 1 + (score_0_100 / 100) * 4


def calculate_impact(score_1_5: float) -> str:
    """Return an impact label for a 1-5 score per the Milestone 3 spec.

    1-2 → Medium Impact
    3-4 → High Impact
    5   → Critical Impact
    """
    if score_1_5 >= 4.5:
        return "Critical"
    elif score_1_5 >= 2.5:
        return "High"
    else:
        return "Medium"


def get_risk_category(risk_name: str) -> str:
    """Return the filter category for a named risk."""
    entry = _MITIGATION_CATALOGUE.get(risk_name, {})
    return entry.get("category", "operational")


def generate_mitigation(risk_scores: dict) -> list:
    """Generate a mitigation card list from Milestone 2 risk scores.

    Parameters
    ----------
    risk_scores : dict
        Keys (values in 0-100 scale): financial_risk, competition_risk,
        technical_risk, operational_risk, market_risk, team_skill_risk, …

    Returns
    -------
    list of dict – each with keys: risk, impact, mitigation, category
    """
    mitigations = []

    for key, risk_name in _SCORE_KEY_MAP.items():
        raw = risk_scores.get(key)
        if raw is None:
            continue

        score_1_5 = _normalize_score(float(raw))
        impact = calculate_impact(score_1_5)
        catalogue_entry = _MITIGATION_CATALOGUE[risk_name]

        mitigations.append(
            {
                "risk": risk_name,
                "impact": impact,
                "mitigation": catalogue_entry["mitigation"],
                "category": catalogue_entry["category"],
                "score": round(score_1_5, 1),
            }
        )

    # Sort by impact severity
    _order = {"Critical": 0, "High": 1, "Medium": 2}
    mitigations.sort(key=lambda m: _order.get(m["impact"], 3))

    return mitigations
