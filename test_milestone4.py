"""Failure Prediction AI – Startup & Project Risk Analyzer — Automated Test Suite.

Validates:
1. Dashboard Analytics Service aggregation logic and metrics calculations.
2. Report generation, persistence in SQLite/PostgreSQL, and retrieval.
3. PDF generation and byte validation.
4. Flask web routes and REST API endpoints.
5. End-to-end multi-layer integration workflow.
6. Permanent project and report deletion (cascading across all tables).
"""
import unittest
import json
import os

from app import app
from database import (
    init_db,
    init_milestone3_tables,
    init_milestone4_tables,
    insert_project,
    delete_project,
    get_all_projects,
    get_project_by_id,
    get_recommendations,
    get_mitigations,
    get_assessment_report_by_id,
    get_assessment_reports_by_project,
    get_latest_report_for_project,
    get_all_reports,
)
from dashboard_service import DashboardAnalyticsService
from pdf_generator import build_pdf_report


class VentureIntelligenceTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize database and test client."""
        init_db()
        init_milestone3_tables()
        init_milestone4_tables()
        cls.client = app.test_client()

        # Insert a sample project for testing if none exist
        projects = get_all_projects()
        if not projects:
            cls.test_project_id = insert_project({
                "startup_name": "HealthAI Pulse",
                "industry": "Healthcare",
                "business_model": "B2B",
                "target_market": "Hospitals and diagnostic clinics in Tier 1 & 2 cities",
                "budget": 250000,
                "project_description": "AI-assisted clinical triage and diagnostic risk scoring for hospitals.",
            })
        else:
            cls.test_project_id = projects[0]["id"]

    def test_01_dashboard_analytics_service(self):
        """Test DashboardAnalyticsService aggregates all outputs accurately."""
        analytics = DashboardAnalyticsService.get_dashboard_analytics(self.test_project_id)
        
        self.assertIn("riskScore", analytics)
        self.assertIn("successProbability", analytics)
        self.assertIn("financialRisk", analytics)
        self.assertIn("competitionRisk", analytics)
        self.assertIn("technicalRisk", analytics)
        self.assertIn("operationalRisk", analytics)
        self.assertIn("marketRisk", analytics)
        self.assertIn("swot", analytics)
        self.assertIn("marketData", analytics)
        self.assertIn("competitors", analytics)
        self.assertIn("recommendations", analytics)
        self.assertIn("strategicInsights", analytics)
        self.assertIn("actionPlan", analytics)
        self.assertIn("riskTrend", analytics)

        # Value range checks
        self.assertTrue(0 <= analytics["riskScore"] <= 100)
        self.assertTrue(0 <= analytics["successProbability"] <= 100)
        self.assertTrue(len(analytics["strategicInsights"]) >= 4)
        self.assertIn("immediate", analytics["actionPlan"])
        self.assertIn("shortTerm", analytics["actionPlan"])
        self.assertIn("longTerm", analytics["actionPlan"])

    def test_02_report_generation_and_db_storage(self):
        """Test assessment report generation and persistence in database."""
        res = DashboardAnalyticsService.generate_and_save_report(
            project_id=self.test_project_id,
            created_by="Automated Test Runner",
        )
        report_id = res["reportId"]
        self.assertIsInstance(report_id, int)
        self.assertTrue(report_id > 0)

        # Retrieve by ID
        saved = get_assessment_report_by_id(report_id)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["project_id"], self.test_project_id)
        self.assertIn("content", saved)
        self.assertEqual(saved["content"]["metadata"]["projectId"], self.test_project_id)

        # Retrieve by project
        project_reports = get_assessment_reports_by_project(self.test_project_id)
        self.assertTrue(len(project_reports) >= 1)

        # Retrieve all reports
        all_reps = get_all_reports()
        self.assertTrue(len(all_reps) >= 1)

    def test_03_pdf_generator(self):
        """Test PDF binary generation and header format."""
        analytics = DashboardAnalyticsService.get_dashboard_analytics(self.test_project_id)
        report_data = {
            "metadata": {
                "startupName": "Test Startup",
                "industry": "Tech",
                "businessModel": "SaaS",
                "budget": 100000,
                "generatedAt": "2026-10-06 12:00:00",
            },
            "executiveSummary": {
                "riskScore": analytics["riskScore"],
                "successProbability": analytics["successProbability"],
                "feasibilityScore": analytics["feasibilityScore"],
                "verdict": analytics["verdict"],
                "overallRiskLevel": analytics["riskLevel"],
                "summaryText": ["Finding 1", "Finding 2"],
            },
            "riskAssessment": {
                "breakdown": {
                    "financialRisk": 40,
                    "competitionRisk": 50,
                    "technicalRisk": 35,
                    "operationalRisk": 30,
                    "marketRisk": 40,
                }
            },
            "swotAnalysis": analytics["swot"],
            "competitorIntelligence": {
                "marketData": analytics["marketData"],
                "competitors": analytics["competitors"],
            },
            "strategicRecommendations": {
                "recommendations": analytics["recommendations"],
            },
            "actionPlan": analytics["actionPlan"],
        }
        pdf_bytes = build_pdf_report(report_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_04_flask_ui_routes(self):
        """Test UI pages render with HTTP 200."""
        # 1. Dashboard root
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

        # 2. Specific project dashboard
        res = self.client.get(f"/dashboard/{self.test_project_id}")
        self.assertEqual(res.status_code, 200)

        # 3. Report page
        res = self.client.get(f"/report/{self.test_project_id}")
        self.assertEqual(res.status_code, 200)

        # 4. Reports repository / history
        res = self.client.get("/reports")
        self.assertEqual(res.status_code, 200)

        # 5. Risk and Recommendations routes
        res = self.client.get(f"/risk-assessment/{self.test_project_id}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/recommendations/{self.test_project_id}")
        self.assertEqual(res.status_code, 200)

    def test_05_flask_api_endpoints(self):
        """Test REST API endpoints."""
        # 1. GET /api/dashboard/:projectId
        res = self.client.get(f"/api/dashboard/{self.test_project_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("riskScore", data)
        self.assertIn("recommendations", data)

        # 2. GET /api/analytics/:projectId
        res = self.client.get(f"/api/analytics/{self.test_project_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("riskScore", data)
        self.assertIn("insights", data)

        # 3. POST /api/reports/generate/:projectId
        res = self.client.post(f"/api/reports/generate/{self.test_project_id}", json={})
        self.assertEqual(res.status_code, 200)
        gen_data = res.get_json()
        self.assertEqual(gen_data["status"], "success")
        report_id = gen_data["reportId"]

        # 4. GET /api/reports/:projectId
        res = self.client.get(f"/api/reports/{self.test_project_id}")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["count"] >= 1)

        # 5. GET /api/reports/download/:reportId/pdf
        res = self.client.get(f"/api/reports/download/{report_id}/pdf")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "application/pdf")
        self.assertTrue(res.data.startswith(b"%PDF"))

        # 6. GET /api/reports/download/:reportId/json
        res = self.client.get(f"/api/reports/download/{report_id}/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "application/json")
        json_data = json.loads(res.data.decode("utf-8"))
        self.assertIn("metadata", json_data)

    def test_06_end_to_end_project_flow(self):
        """Test submitting a new project and verifying the entire pipeline runs seamlessly."""
        # 1. Submit Project
        res = self.client.post("/submit", data={
            "startup_name": "EcomBot Scaler",
            "industry": "E-commerce",
            "business_model": "SaaS",
            "target_market": "Online D2C brands",
            "budget": "150000",
            "project_description": "AI-powered customer conversion optimization bot.",
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Retrieve new project
        projects = get_all_projects()
        new_project = [p for p in projects if p["startup_name"] == "EcomBot Scaler"][0]
        new_id = new_project["id"]

        # 2. Check Dashboard API
        dash_res = self.client.get(f"/api/dashboard/{new_id}")
        self.assertEqual(dash_res.status_code, 200)
        dash_json = dash_res.get_json()
        self.assertEqual(dash_json["project"]["startup_name"], "EcomBot Scaler")
        self.assertTrue(len(dash_json["recommendations"]) > 0)

        # 3. Check PDF Export
        pdf_res = self.client.get(f"/api/reports/download-pdf/{new_id}")
        self.assertEqual(pdf_res.status_code, 200)
        self.assertTrue(pdf_res.data.startswith(b"%PDF"))

    def test_07_delete_project_cascades_entire_db(self):
        """Test deleting a project permanently removes it and all associated records from all tables."""
        # 1. Create a dedicated project to delete
        temp_id = insert_project({
            "startup_name": "Disposable Startup Corp",
            "industry": "Finance",
            "business_model": "B2B",
            "target_market": "Fintech users",
            "budget": 50000,
            "project_description": "Temporary project for deletion validation.",
        })
        self.assertIsNotNone(temp_id)

        # 2. Generate recommendations, mitigations, and assessment report
        DashboardAnalyticsService.generate_and_save_report(temp_id)

        # Verify data exists before delete
        self.assertIsNotNone(get_project_by_id(temp_id))
        self.assertTrue(len(get_assessment_reports_by_project(temp_id)) >= 1)

        # 3. Perform delete via API
        del_res = self.client.delete(f"/api/projects/{temp_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.get_json()["status"], "success")

        # 4. Verify permanent deletion across all database tables
        self.assertIsNone(get_project_by_id(temp_id))
        self.assertEqual(len(get_recommendations(temp_id)), 0)
        self.assertEqual(len(get_mitigations(temp_id)), 0)
        self.assertEqual(len(get_assessment_reports_by_project(temp_id)), 0)


if __name__ == "__main__":
    unittest.main()
