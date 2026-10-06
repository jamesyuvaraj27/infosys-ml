"""Failure Prediction AI – Startup & Project Risk Analyzer — Centralized Flask Web Application.

Integrates:
- Milestone 1: Project Submission & TAM/SAM/SOM Market Sizing
- Milestone 2: Risk Scoring, SWOT Matrix & Feasibility Engine
- Milestone 3: AI Recommendations, Reasoning Chains & Mitigations
- Milestone 4: Centralized Analytics Dashboard, Comprehensive Assessment Reports,
              PDF/JSON Exports, and Production Deployment.
"""
from __future__ import annotations
import json
from flask import Flask, jsonify, redirect, render_template, request, url_for, Response

from database import (
    get_all_projects,
    get_project_by_id,
    get_project_count,
    init_db,
    insert_project,
    delete_project,
    init_milestone3_tables,
    init_milestone4_tables,
    save_recommendations,
    save_mitigations,
    get_recommendations,
    get_mitigations,
    save_assessment_report,
    get_assessment_report_by_id,
    get_assessment_reports_by_project,
    get_latest_report_for_project,
    get_all_reports,
    delete_assessment_report,
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
from dashboard_service import DashboardAnalyticsService
from pdf_generator import build_pdf_report

app = Flask(__name__)

# Initialize all database tables on startup
init_db()
init_milestone3_tables()
init_milestone4_tables()

INDUSTRY_CHOICES = [
    "Technology", "Healthcare", "Education", "Finance",
    "E-commerce", "Food & Beverage", "Agriculture", "Other",
]
BUSINESS_MODEL_CHOICES = ["B2B", "B2C", "B2B2C", "Marketplace", "SaaS", "D2C"]


# ---------------------------------------------------------------------------
# Milestone 1 & 4 – Centralized Dashboard Routes
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard_home():
    """Unified Analytics Dashboard root route."""
    projects = get_all_projects()
    count = get_project_count()
    
    if projects:
        latest = projects[0]
        analytics = DashboardAnalyticsService.get_dashboard_analytics(latest["id"])
        return render_template(
            "dashboard.html",
            projects=projects,
            count=count,
            latest=latest,
            project=latest,
            analytics=analytics,
            market_data=analytics["marketData"],
            competitors=analytics["competitors"],
        )
    
    return render_template(
        "dashboard.html",
        projects=[],
        count=0,
        latest=None,
        project=None,
        analytics=None,
        market_data=None,
        competitors=None,
    )


@app.route("/dashboard/<int:project_id>")
def project_dashboard(project_id):
    """Unified Analytics Dashboard for a specific project."""
    project = get_project_by_id(project_id)
    if project is None:
        return redirect(url_for("dashboard_home"))

    projects = get_all_projects()
    count = get_project_count()
    analytics = DashboardAnalyticsService.get_dashboard_analytics(project_id)

    return render_template(
        "dashboard.html",
        projects=projects,
        count=count,
        latest=projects[0] if projects else None,
        project=project,
        analytics=analytics,
        market_data=analytics["marketData"],
        competitors=analytics["competitors"],
    )


@app.route("/submit", methods=["GET"])
def submit_form():
    """Project ingestion submission form."""
    return render_template(
        "project.html",
        industries=INDUSTRY_CHOICES,
        business_models=BUSINESS_MODEL_CHOICES,
    )


@app.route("/submit", methods=["POST"])
def submit_project():
    """Handle new project creation and redirect to dashboard."""
    data = {
        "startup_name": request.form.get("startup_name", "").strip(),
        "industry": request.form.get("industry", "").strip(),
        "business_model": request.form.get("business_model", "").strip(),
        "target_market": request.form.get("target_market", "").strip(),
        "budget": request.form.get("budget") or 0,
        "project_description": request.form.get("project_description", "").strip(),
    }
    new_id = insert_project(data)
    # Auto-generate initial assessment report in the background
    try:
        DashboardAnalyticsService.generate_and_save_report(new_id)
    except Exception as e:
        print(f"[WARN] Initial report generation skipped: {e}")

    return redirect(url_for("project_dashboard", project_id=new_id))


# ---------------------------------------------------------------------------
# Milestone 4 – Assessment Reporting & History Routes
# ---------------------------------------------------------------------------

@app.route("/reports")
@app.route("/reports/history")
def reports_history():
    """View repository of all generated assessment reports."""
    reports = get_all_reports()
    projects = get_all_projects()
    return render_template(
        "report_history.html",
        reports=reports,
        projects=projects,
        count=len(reports),
    )


@app.route("/report/<int:project_id>")
def project_report(project_id):
    """View the latest report for a project, generating one if none exists."""
    project = get_project_by_id(project_id)
    if not project:
        return redirect(url_for("reports_history"))

    report_row = get_latest_report_for_project(project_id)
    if not report_row:
        # Generate fresh report
        gen_result = DashboardAnalyticsService.generate_and_save_report(project_id)
        report_row = get_assessment_report_by_id(gen_result["reportId"])

    content = report_row.get("content", {})
    return render_template(
        "report.html",
        report=report_row,
        metadata=content.get("metadata", {}),
        executiveSummary=content.get("executiveSummary", {}),
        riskAssessment=content.get("riskAssessment", {}),
        swotAnalysis=content.get("swotAnalysis", {}),
        competitorIntelligence=content.get("competitorIntelligence", {}),
        strategicRecommendations=content.get("strategicRecommendations", {}),
        actionPlan=content.get("actionPlan", {}),
    )


@app.route("/report/view/<int:report_id>")
def view_report_by_id(report_id):
    """View a specific historical assessment report by its report ID."""
    report_row = get_assessment_report_by_id(report_id)
    if not report_row:
        return redirect(url_for("reports_history"))

    content = report_row.get("content", {})
    return render_template(
        "report.html",
        report=report_row,
        metadata=content.get("metadata", {}),
        executiveSummary=content.get("executiveSummary", {}),
        riskAssessment=content.get("riskAssessment", {}),
        swotAnalysis=content.get("swotAnalysis", {}),
        competitorIntelligence=content.get("competitorIntelligence", {}),
        strategicRecommendations=content.get("strategicRecommendations", {}),
        actionPlan=content.get("actionPlan", {}),
    )


# ---------------------------------------------------------------------------
# Milestone 2 – Risk Assessment, SWOT & Feasibility Routes
# ---------------------------------------------------------------------------

@app.route("/risk-assessment")
def risk_assessment_home():
    """Redirect to latest project's risk assessment."""
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
# Milestone 3 – Recommendations & Strategic Reasoning Routes
# ---------------------------------------------------------------------------

@app.route("/recommendations")
def recommendations_home():
    """Redirect to the latest project's recommendations."""
    projects = get_all_projects()
    if not projects:
        return redirect(url_for("submit_form"))
    return redirect(url_for("recommendations_dashboard", project_id=projects[0]["id"]))


@app.route("/recommendations/<int:project_id>")
def recommendations_dashboard(project_id):
    """Render Milestone 3 recommendations & reasoning page."""
    project = get_project_by_id(project_id)
    if project is None:
        return redirect(url_for("dashboard_home"))

    budget = float(project.get("budget") or 0)
    industry = (project.get("industry") or "").lower()

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

    state = run_workflow(
        project=project,
        risk_scores=risk_scores,
        swot=None,
        feasibility_score=max(0, 100 - overall_risk),
    )

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
    """Compute and save Milestone 3 recommendations data."""
    project = get_project_by_id(project_id)
    if project is None:
        return jsonify({"error": "project not found"}), 404

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


# ---------------------------------------------------------------------------
# Milestone 4 – Backend APIs & Export Functionality
# ---------------------------------------------------------------------------

@app.route("/api/dashboard/<int:project_id>")
def api_dashboard(project_id):
    """Return complete dashboard analytics payload as JSON."""
    try:
        analytics = DashboardAnalyticsService.get_dashboard_analytics(project_id)
        return jsonify(analytics)
    except ValueError:
        return jsonify({"error": "project not found"}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/analytics/<int:project_id>")
def api_analytics(project_id):
    """Return simplified analytics response matching Phase 2 spec."""
    try:
        a = DashboardAnalyticsService.get_dashboard_analytics(project_id)
        return jsonify({
            "riskScore": a["riskScore"],
            "successProbability": a["successProbability"],
            "marketRisk": a["marketRisk"],
            "technicalRisk": a["technicalRisk"],
            "financialRisk": a["financialRisk"],
            "operationalRisk": a["operationalRisk"],
            "swot": a["swot"],
            "recommendations": a["recommendations"],
            "insights": a["strategicInsights"],
            "nextSteps": a["nextSteps"],
        })
    except ValueError:
        return jsonify({"error": "project not found"}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/reports/generate", methods=["POST"])
def api_generate_report_body():
    """Generate and store an assessment report from JSON body."""
    body = request.get_json(silent=True) or {}
    project_id = body.get("project_id") or body.get("projectId")
    if not project_id:
        return jsonify({"error": "project_id is required"}), 400

    try:
        res = DashboardAnalyticsService.generate_and_save_report(
            project_id=int(project_id),
            custom_factors=body.get("factors"),
            created_by=body.get("created_by", "AI Risk Intelligence Engine"),
        )
        return jsonify({
            "status": "success",
            "reportId": res["reportId"],
            "reportTitle": res["reportTitle"],
            "report": res["reportContent"],
        })
    except ValueError:
        return jsonify({"error": "project not found"}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/reports/generate/<int:project_id>", methods=["POST"])
def api_generate_report_for_project(project_id):
    """Generate and store an assessment report for project_id."""
    body = request.get_json(silent=True) or {}
    try:
        res = DashboardAnalyticsService.generate_and_save_report(
            project_id=project_id,
            custom_factors=body.get("factors"),
            created_by=body.get("created_by", "AI Risk Intelligence Engine"),
        )
        return jsonify({
            "status": "success",
            "reportId": res["reportId"],
            "reportTitle": res["reportTitle"],
            "report": res["reportContent"],
        })
    except ValueError:
        return jsonify({"error": "project not found"}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/reports/<int:project_id>")
def api_get_reports_for_project(project_id):
    """Return all historical assessment reports for a project."""
    reports = get_assessment_reports_by_project(project_id)
    return jsonify({
        "projectId": project_id,
        "count": len(reports),
        "reports": reports,
    })


@app.route("/api/reports/history/<int:project_id>")
def api_project_report_history(project_id):
    """Alias for report history of a project."""
    reports = get_assessment_reports_by_project(project_id)
    return jsonify(reports)


@app.route("/api/reports/download/<int:report_id>")
@app.route("/api/reports/download/<int:report_id>/pdf")
def api_download_report_pdf(report_id):
    """Download publication-quality PDF assessment report."""
    report_row = get_assessment_report_by_id(report_id)
    if not report_row:
        return jsonify({"error": "report not found"}), 404

    content = report_row.get("content", {})
    startup_name = content.get("metadata", {}).get("startupName", f"Project_{report_id}")
    safe_name = "".join(c if c.isalnum() else "_" for c in startup_name)
    filename = f"Risk_Assessment_Report_{safe_name}.pdf"

    pdf_bytes = build_pdf_report(content)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/api/reports/download-pdf/<int:project_id>")
def api_download_pdf_for_project(project_id):
    """Generate or retrieve latest report and stream PDF download."""
    report_row = get_latest_report_for_project(project_id)
    if not report_row:
        res = DashboardAnalyticsService.generate_and_save_report(project_id)
        report_row = get_assessment_report_by_id(res["reportId"])

    content = report_row.get("content", {})
    startup_name = content.get("metadata", {}).get("startupName", f"Project_{project_id}")
    safe_name = "".join(c if c.isalnum() else "_" for c in startup_name)
    filename = f"Risk_Assessment_Report_{safe_name}.pdf"

    pdf_bytes = build_pdf_report(content)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/api/reports/download/<int:report_id>/json")
def api_download_report_json(report_id):
    """Download full report content as JSON file."""
    report_row = get_assessment_report_by_id(report_id)
    if not report_row:
        return jsonify({"error": "report not found"}), 404

    content = report_row.get("content", {})
    startup_name = content.get("metadata", {}).get("startupName", f"Project_{report_id}")
    safe_name = "".join(c if c.isalnum() else "_" for c in startup_name)
    filename = f"Risk_Assessment_Report_{safe_name}.json"

    json_str = json.dumps(content, indent=2)
    return Response(
        json_str,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/api/reports/download-json/<int:project_id>")
def api_download_json_for_project(project_id):
    """Download full latest report for project as JSON file."""
    report_row = get_latest_report_for_project(project_id)
    if not report_row:
        res = DashboardAnalyticsService.generate_and_save_report(project_id)
        report_row = get_assessment_report_by_id(res["reportId"])

    content = report_row.get("content", {})
    startup_name = content.get("metadata", {}).get("startupName", f"Project_{project_id}")
    safe_name = "".join(c if c.isalnum() else "_" for c in startup_name)
    filename = f"Risk_Assessment_Report_{safe_name}.json"

    json_str = json.dumps(content, indent=2)
    return Response(
        json_str,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/api/market-data/<int:project_id>")
def api_market_data(project_id):
    """Milestone 1 Market Data API."""
    project = get_project_by_id(project_id)
    if project is None:
        return jsonify({"error": "project not found"}), 404

    market_data = get_market_data(project["industry"], project["budget"])
    competitors = get_competitors(project["industry"])
    return jsonify({"market_data": market_data, "competitors": competitors})


@app.route("/project/delete/<int:project_id>", methods=["POST"])
def delete_project_route(project_id):
    """Delete project and redirect to dashboard."""
    delete_project(project_id)
    return redirect(url_for("dashboard_home"))


@app.route("/api/projects/delete/<int:project_id>", methods=["POST", "DELETE"])
@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def api_delete_project(project_id):
    """API endpoint to permanently delete a project and all associated intelligence records."""
    deleted = delete_project(project_id)
    if deleted:
        return jsonify({
            "status": "success",
            "projectId": project_id,
            "message": "Project and all associated database records deleted permanently.",
        })
    return jsonify({"error": "project not found or already deleted"}), 404


@app.route("/api/reports/delete/<int:report_id>", methods=["POST", "DELETE"])
@app.route("/api/reports/<int:report_id>", methods=["DELETE"])
def api_delete_report(report_id):
    """API endpoint to permanently delete an assessment report."""
    deleted = delete_assessment_report(report_id)
    if deleted:
        return jsonify({
            "status": "success",
            "reportId": report_id,
            "message": "Assessment report deleted permanently.",
        })
    return jsonify({"error": "report not found or already deleted"}), 404


@app.route("/roadmap/<stage>")
def placeholder(stage):
    """Roadmap stages handler."""
    if stage in ("dashboard", "analytics"):
        return redirect(url_for("dashboard_home"))
    elif stage == "risk-assessment":
        return redirect(url_for("risk_assessment_home"))
    elif stage in ("ai-advisor", "recommendations"):
        return redirect(url_for("recommendations_home"))
    elif stage in ("reports", "reporting", "export"):
        return redirect(url_for("reports_history"))
    return render_template("placeholder.html", stage=stage)


if __name__ == "__main__":

    app.run(debug=True)
