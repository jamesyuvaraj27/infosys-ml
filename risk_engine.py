"""Milestone 2 — Risk scoring engine.

Weighted scoring across five inputs (0-100 total). Higher score = higher risk.
"""


def calculate_risk(
    market_competition,
    team_expertise,
    resource_availability,
    innovation_level,
    market_research,
):
    risk = 0

    # Market competition
    if market_competition == "High":
        risk += 25
    elif market_competition == "Medium":
        risk += 15
    else:
        risk += 5

    # Team expertise
    if team_expertise == "Low":
        risk += 20
    elif team_expertise == "Medium":
        risk += 10
    else:
        risk += 5

    # Resources
    if resource_availability == "Limited":
        risk += 20
    elif resource_availability == "Moderate":
        risk += 10
    else:
        risk += 5

    # Innovation
    if innovation_level == "Low":
        risk += 20
    elif innovation_level == "Medium":
        risk += 10
    else:
        risk += 5

    # Market research
    if market_research == "Limited":
        risk += 15
    elif market_research == "Moderate":
        risk += 8
    else:
        risk += 3

    return min(risk, 100)


def get_risk_status(score):
    if score >= 70:
        return "HIGH RISK"
    elif score >= 40:
        return "MEDIUM RISK"
    else:
        return "LOW RISK"


def calculate_success_probability(risk_score):
    return max(0, 100 - risk_score)
