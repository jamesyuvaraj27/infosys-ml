"""Milestone 2 — Project feasibility score (simple average of four 0-100 factors)."""


def calculate_feasibility(
    market_opportunity,
    team_capability,
    competitive_advantage,
    resource_availability,
):
    score = (
        market_opportunity
        + team_capability
        + competitive_advantage
        + resource_availability
    ) / 4

    return round(score)
