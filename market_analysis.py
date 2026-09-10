"""TAM / SAM / SOM and competitor estimates for a submitted project.

These are simplified, deterministic-ish formulas for a Milestone-1 demo —
not real market research. Milestone 3 is expected to replace this with a
Gemini-backed analysis.
"""
import random


def _format_currency(value):
    """Format a raw number as $X.XB / $X.XM / $X.XK."""
    value = float(value)
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def get_market_data(industry, budget):
    """Return TAM/SAM/SOM, growth rate and a 6-year market trend."""
    budget = float(budget or 0)

    tam_raw = budget * 200
    sam_raw = budget * 70
    som_raw = budget * 0.024

    fractions = [0.40, 0.52, 0.64, 0.76, 0.88, 1.00]
    market_trend = [
        {"year": year, "value": round(sam_raw * frac, 2)}
        for year, frac in zip(range(2021, 2027), fractions)
    ]

    return {
        "industry": industry,
        "tam": _format_currency(tam_raw),
        "sam": _format_currency(sam_raw),
        "som": _format_currency(som_raw),
        "growth_rate": round(random.uniform(8, 15), 1),
        "market_trend": market_trend,
    }


def get_competitors(industry):
    """Return a fixed 3-competitor snapshot (placeholder data)."""
    return [
        {"name": "Competitor A", "market_share": 28, "revenue": "$45M", "growth": "+12%"},
        {"name": "Competitor B", "market_share": 22, "revenue": "$38M", "growth": "+8%"},
        {"name": "Competitor C", "market_share": 15, "revenue": "$25M", "growth": "+5%"},
    ]
