"""Flask app: submission form -> PostgreSQL -> live market dashboard."""
from flask import Flask, jsonify, redirect, render_template, request, url_for

from database import (
    get_all_projects,
    get_project_by_id,
    get_project_count,
    init_db,
    insert_project,
)
from market_analysis import get_competitors, get_market_data

app = Flask(__name__)

# Create the projects table on startup if it doesn't already exist.
init_db()

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
    return render_template("placeholder.html", stage=stage)


if __name__ == "__main__":
    app.run(debug=True)
