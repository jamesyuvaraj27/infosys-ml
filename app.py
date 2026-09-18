"""Flask app: submission form -> PostgreSQL -> live market dashboard."""
from flask import Flask, jsonify, redirect, render_template, request, url_for

from database import (
    get_all_projects,
    get_project_by_id,
    get_project_count,
    init_db,
    insert_project,
    init_milestone3_tables,
    save_recommendations,
    save_mitigations,
    get_recommendations,
    get_mitigations,
)
from market_analysis import get_competitors, get_market_data
from risk_engine import (
    calculate_risk,
    calculate_success_probability,
    get_risk_status,
)
from swot_analysis import generate_swot
from feasibility import calculate_feasibility
from workflow import run_workflow, WORKFLOW_STEPS

app = Flask(__name__)

# Create the projects table on startup if it doesn't already exist.
init_db()
# Create Milestone 3 tables on startup.
init_milestone3_tables()

INDUSTRY_CHOICES = [
    "Technology", "Healthcare", "Education", "Finance",
    "E-commerce", "Food & Beverage", "Agriculture", "Other",
]
BUSINESS_MODEL_CHOICES = ["B2B", "B2C", "B2B2C", "Marketplace", "SaaS", "D2C"]


@app.route("/")
def dashboard_home():
    projects = get_all_projects()
    count = get_project_count()
    latest = projects[0] if projects else None
    return render_template(
        "dashboard.html",
        projects=projects,
        count=count,
        latest=latest,
        project=None,
        market_data=None,
        competitors=None,
    )


@app.route("/submit", methods=["GET"])
def submit_form():
    return render_template(
        "project.html",
        industries=INDUSTRY_CHOICES,
        business_models=BUSINESS_MODEL_CHOICES,
    )


@app.route("/submit", methods=["POST"])
def submit_project():
    data = {
        "startup_name": request.form.get("startup_name", "").strip(),
        "industry": request.form.get("industry", "").strip(),
        "business_model": request.form.get("business_model", "").strip(),
        "target_market": request.form.get("target_market", "").strip(),
        "budget": request.form.get("budget") or 0,
        "project_description": request.form.get("project_description", "").strip(),
    }
    new_id = insert_project(data)
    return redirect(url_for("project_dashboard", project_id=new_id))


@app.route("/dashboard/<int:project_id>")
def project_dashboard(project_id):
    project = get_project_by_id(project_id)
    if project is None:
        return redirect(url_for("dashboard_home"))

    market_data = get_market_data(project["industry"], project["budget"])
    competitors = get_competitors(project["industry"])

    projects = get_all_projects()
    count = get_project_count()

    return render_template(
        "dashboard.html",
        projects=projects,
        count=count,
        latest=projects[0] if projects else None,
        project=project,
        market_data=market_data,
        competitors=competitors,
    )


@app.route("/api/market-data/<int:project_id>")
def api_market_data(project_id):
    project = get_project_by_id(project_id)
    if project is None:
        return jsonify({"error": "project not found"}), 404

    market_data = get_market_data(project["industry"], project["budget"])
    competitors = get_competitors(project["industry"])
    return jsonify({"market_data": market_data, "competitors": competitors})


@app.route("/roadmap/<stage>")
def placeholder(stage):
    if stage == "risk-assessment":
        return redirect(url_for("risk_assessment_home"))
    elif stage in ("ai-advisor", "recommendations"):
        return redirect(url_for("recommendations_home"))
    return render_template("placeholder.html", stage=stage)


# ---------------------------------------------------------------------------
# Milestone 2 – Risk Assessment, SWOT & Feasibility
# ---------------------------------------------------------------------------

@app.route("/risk-assessment")
def risk_assessment_home():
    """Redirect to the latest project's risk assessment or submit form."""
    projects = get_all_projects()
    if not projects:
        return redirect(url_for("submit_form"))
    return redirect(url_for("project_risk_assessment", project_id=projects[0]["id"]))


@app.route("/risk-assessment/<int:project_id>")
def project_risk_assessment(project_id):
    """Render Milestone 2 Risk Assessment and SWOT Dashboard."""
    project = get_project_by_id(project_id)
    if project is None:
        return redirect(url_for("dashboard_home"))

    projects = get_all_projects()
    return render_template(
        "risk_assessment.html",
        project=project,
        projects=projects,
        count=len(projects),
    )


@app.route("/api/risk-assessment/<int:project_id>", methods=["POST"])
def api_risk_assessment(project_id):
    """Recalculate Risk, SWOT, and Feasibility dynamically."""
    project = get_project_by_id(project_id)
    if project is None:
        return jsonify({"error": "project not found"}), 404

    data = request.get_json(silent=True) or {}
    market_competition = data.get("market_competition", "Medium")
    team_expertise = data.get("team_expertise", "Medium")
    resource_availability = data.get("resource_availability", "Moderate")
    innovation_level = data.get("innovation_level", "Medium")
    market_research = data.get("market_research", "Moderate")

    risk_score = calculate_risk(
        market_competition,
        team_expertise,
        resource_availability,
        innovation_level,
        market_research,
    )
    risk_status = get_risk_status(risk_score)
    success_probability = calculate_success_probability(risk_score)

    swot = generate_swot(
        team_expertise,
        innovation_level,
        market_competition,
        resource_availability,
        market_research,
    )

    market_opp = int(data.get("market_opportunity", 70))
    team_cap = int(data.get("team_capability", 65))
    comp_adv = int(data.get("competitive_advantage", 60))
    res_avail = int(data.get("resource_readiness", 55))

    feasibility_score = calculate_feasibility(
        market_opp, team_cap, comp_adv, res_avail
    )

    if feasibility_score >= 80:
        verdict = "Highly Feasible"
    elif feasibility_score >= 60:
        verdict = "Feasible"
    elif feasibility_score >= 40:
        verdict = "Moderately Feasible"
    else:
        verdict = "Not Feasible"

    return jsonify({
        "risk_score": risk_score,
        "risk_status": risk_status,
        "success_probability": success_probability,
        "swot": swot,
        "feasibility_score": feasibility_score,
        "verdict": verdict,
    })


# ---------------------------------------------------------------------------
# Milestone 3 – Recommendations & Strategic Reasoning
# ---------------------------------------------------------------------------

@app.route("/recommendations")
def recommendations_home():
    """Redirect to the latest project's recommendations or submit form."""
    projects = get_all_projects()
    if not projects:
        return redirect(url_for("submit_form"))
    return redirect(url_for("recommendations_dashboard", project_id=projects[0]["id"]))


@app.route("/recommendations/<int:project_id>")
def recommendations_dashboard(project_id):
    """Render the Milestone 3 three-column recommendations page."""
    project = get_project_by_id(project_id)
    if project is None:
        return redirect(url_for("dashboard_home"))

    # Build risk scores from project data (derive reasonable proxies so the
    # page works out of the box without requiring Streamlit inputs to be
    # re-entered here).  The budget acts as a financial risk proxy;
    # users can refine via the Milestone 2 Streamlit app.
    budget = float(project.get("budget") or 0)
    industry = (project.get("industry") or "").lower()

    # Derive simple risk proxies from project fields
    financial_risk = min(100, max(0, 100 - (budget / 10000)))
    competition_risk = 60 if "tech" in industry or "finance" in industry else 40
    technical_risk = 55 if "tech" in industry else 35
    operational_risk = 45
    market_risk = 50
    overall_risk = round(
        (financial_risk * 0.3 + competition_risk * 0.25 + technical_risk * 0.2
         + operational_risk * 0.15 + market_risk * 0.1)
    )

    risk_scores = {
        "financial_risk": financial_risk,
        "competition_risk": competition_risk,
        "technical_risk": technical_risk,
        "operational_risk": operational_risk,
        "market_risk": market_risk,
        "overall_risk": overall_risk,
    }

    # Run the full Milestone 3 workflow
    state = run_workflow(
        project=project,
        risk_scores=risk_scores,
        swot=None,
        feasibility_score=max(0, 100 - overall_risk),
    )

    # Persist to DB
    save_recommendations(project_id, state["recommendations"])
    save_mitigations(project_id, state["mitigations"])

    return render_template(
        "recommendations.html",
        project=project,
        recommendations=state["recommendations"],
        mitigations=state["mitigations"],
        reasoning=state["reasoning"],
        report=state["report"],
        workflow_steps=WORKFLOW_STEPS,
        projects=get_all_projects(),
        count=get_project_count(),
    )


@app.route("/api/recommendations/<int:project_id>", methods=["POST"])
def api_recommendations(project_id):
    """Compute and save Milestone 3 data, returning JSON."""
    project = get_project_by_id(project_id)
    if project is None:
        return jsonify({"error": "project not found"}), 404

    # Allow caller to supply risk_scores via JSON body for richer results
    body = request.get_json(silent=True) or {}
    budget = float(project.get("budget") or 0)
    industry = (project.get("industry") or "").lower()

    financial_risk = body.get("financial_risk", min(100, max(0, 100 - (budget / 10000))))
    competition_risk = body.get("competition_risk", 60 if "tech" in industry or "finance" in industry else 40)
    technical_risk = body.get("technical_risk", 55 if "tech" in industry else 35)
    operational_risk = body.get("operational_risk", 45)
    market_risk = body.get("market_risk", 50)
    overall_risk = body.get(
        "overall_risk",
        round(financial_risk * 0.3 + competition_risk * 0.25 + technical_risk * 0.2
              + operational_risk * 0.15 + market_risk * 0.1),
    )

    risk_scores = {
        "financial_risk": financial_risk,
        "competition_risk": competition_risk,
        "technical_risk": technical_risk,
        "operational_risk": operational_risk,
        "market_risk": market_risk,
        "overall_risk": overall_risk,
    }

    state = run_workflow(
        project=project,
        risk_scores=risk_scores,
        swot=body.get("swot"),
        feasibility_score=body.get("feasibility_score", max(0, 100 - overall_risk)),
    )

    save_recommendations(project_id, state["recommendations"])
    save_mitigations(project_id, state["mitigations"])

    return jsonify({
        "recommendations": state["recommendations"],
        "mitigations": state["mitigations"],
        "reasoning": state["reasoning"],
        "report": state["report"],
        "workflow_steps": WORKFLOW_STEPS,
        "validation_passed": state["validation_passed"],
    })


if __name__ == "__main__":
    app.run(debug=True)
