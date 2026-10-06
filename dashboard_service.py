"""Milestone 4 – Analytics Aggregation & Assessment Report Service.

Aggregates outputs from:
- Milestone 1: Project Submission, TAM/SAM/SOM Market Sizing, Competitor Landscape
- Milestone 2: Risk Scoring Engine, SWOT Matrix, Feasibility Assessment
- Milestone 3: AI Recommendations, Risk Mitigations, Strategic Reasoning Pipeline

Produces centralized dashboard analytics and publication-grade assessment reports.
"""
from __future__ import annotations
import datetime
from typing import Any, Dict, List, Optional

from market_analysis import get_competitors, get_market_data
from risk_engine import calculate_risk, calculate_success_probability, get_risk_status
from swot_analysis import generate_swot
from feasibility import calculate_feasibility
from workflow import run_workflow, WORKFLOW_STEPS
from database import (
    get_project_by_id,
    save_assessment_report,
    get_latest_report_for_project,
    get_assessment_report_by_id,
)


class DashboardAnalyticsService:
    """Service to aggregate, calculate, and compile all project intelligence."""

    @classmethod
    def derive_risk_scores(cls, project: dict, custom_factors: Optional[dict] = None) -> dict:
        """Derive standard risk breakdown for a project with optional manual factor overrides."""
        factors = custom_factors or {}
        budget = float(project.get("budget") or 0)
        industry = (project.get("industry") or "").lower()
        bmodel = (project.get("business_model") or "").lower()

        # If custom factor parameters provided (from M2 inputs)
        market_comp = factors.get("market_competition", "Medium")
        team_exp = factors.get("team_expertise", "Medium")
        res_avail = factors.get("resource_availability", "Moderate")
        innov = factors.get("innovation_level", "Medium")
        mkt_res = factors.get("market_research", "Moderate")

        # Calculate base engine risk
        engine_risk = calculate_risk(market_comp, team_exp, res_avail, innov, mkt_res)

        # Calculate category specific risk metrics (0-100 scale)
        financial_risk = factors.get(
            "financial_risk",
            min(100, max(15, round(100 - (budget / 10000)))) if budget > 0 else 75,
        )
        if res_avail == "Limited":
            financial_risk = min(100, max(financial_risk, 70))
        elif res_avail == "Good":
            financial_risk = max(15, min(financial_risk, 40))

        competition_risk = factors.get(
            "competition_risk",
            80 if market_comp == "High" else (50 if market_comp == "Medium" else 25),
        )

        technical_risk = factors.get(
            "technical_risk",
            75 if innov == "High" and team_exp == "Low" else (
                55 if "tech" in industry or innov == "High" else 35
            ),
        )

        operational_risk = factors.get(
            "operational_risk",
            70 if team_exp == "Low" else (45 if team_exp == "Medium" else 25),
        )

        market_risk = factors.get(
            "market_risk",
            75 if mkt_res == "Limited" else (50 if mkt_res == "Moderate" else 25),
        )

        # Weighted Overall Risk
        overall_risk = factors.get(
            "overall_risk",
            round(
                financial_risk * 0.25
                + competition_risk * 0.25
                + technical_risk * 0.20
                + operational_risk * 0.15
                + market_risk * 0.15
            ),
        )
        overall_risk = min(100, max(0, overall_risk))

        return {
            "financial_risk": financial_risk,
            "competition_risk": competition_risk,
            "technical_risk": technical_risk,
            "operational_risk": operational_risk,
            "market_risk": market_risk,
            "overall_risk": overall_risk,
            "engine_risk": engine_risk,
            "factors": {
                "market_competition": market_comp,
                "team_expertise": team_exp,
                "resource_availability": res_avail,
                "innovation_level": innov,
                "market_research": mkt_res,
            },
        }

    @classmethod
    def get_dashboard_analytics(cls, project_id: int, custom_factors: Optional[dict] = None) -> dict:
        """Collect all project data, calculate risk metrics and build complete dashboard payload."""
        project = get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found.")

        # 1. Milestone 1 Market Intelligence
        industry = project.get("industry") or "Technology"
        budget = float(project.get("budget") or 0)
        market_data = get_market_data(industry, budget)
        competitors = get_competitors(industry)

        # 2. Milestone 2 Risk & SWOT & Feasibility
        risk_scores = cls.derive_risk_scores(project, custom_factors)
        overall_risk = risk_scores["overall_risk"]
        risk_level = get_risk_status(overall_risk)
        success_probability = calculate_success_probability(overall_risk)

        factors = risk_scores["factors"]
        swot = generate_swot(
            team_expertise=factors["team_expertise"],
            innovation_level=factors["innovation_level"],
            market_competition=factors["market_competition"],
            resource_availability=factors["resource_availability"],
            market_research=factors["market_research"],
        )

        market_opp = int((custom_factors or {}).get("market_opportunity", 70))
        team_cap = int((custom_factors or {}).get("team_capability", 65))
        comp_adv = int((custom_factors or {}).get("competitive_advantage", 60))
        res_read = int((custom_factors or {}).get("resource_readiness", 55))
        feasibility_score = calculate_feasibility(market_opp, team_cap, comp_adv, res_read)

        if feasibility_score >= 80:
            verdict = "Highly Feasible"
        elif feasibility_score >= 60:
            verdict = "Feasible"
        elif feasibility_score >= 40:
            verdict = "Moderately Feasible"
        else:
            verdict = "Not Feasible"

        # 3. Milestone 3 Recommendations & Workflow Reasoning
        workflow_state = run_workflow(
            project=project,
            risk_scores=risk_scores,
            swot=swot,
            feasibility_score=feasibility_score,
        )

        recommendations = workflow_state.get("recommendations", [])
        mitigations = workflow_state.get("mitigations", [])
        reasoning = workflow_state.get("reasoning", [])

        # 4. Milestone 4 Strategic Insights Generation
        strategic_insights = cls._generate_strategic_insights(
            project=project,
            risk_scores=risk_scores,
            swot=swot,
            recommendations=recommendations,
        )

        # 5. Milestone 4 3-Tier Phased Action Plan
        action_plan = cls._generate_action_plan(
            project=project,
            risk_scores=risk_scores,
            recommendations=recommendations,
            mitigations=mitigations,
        )

        # 6. Milestone 4 Monthly Risk Trend Trajectory
        risk_trend = cls._generate_risk_trend(overall_risk)

        # 7. Project Assessment Summary
        assessment_summary = {
            "key_findings": [
                f"Overall venture risk is evaluated at {overall_risk}/100 ({risk_level}).",
                f"Market viability indicates a {success_probability}% success probability with a '{verdict}' feasibility rating ({feasibility_score}%).",
                f"Identified {len(recommendations)} strategic recommendations, including {sum(1 for r in recommendations if r['priority'] == 'Critical')} critical priority action item(s).",
                f"Market opportunity in {industry} demonstrates a SAM of {market_data.get('sam')} with {market_data.get('growth_rate')}% annual growth rate.",
            ],
            "risk_summary": f"Primary risk vectors include Financial ({risk_scores['financial_risk']}%), Competition ({risk_scores['competition_risk']}%), and Technical ({risk_scores['technical_risk']}%).",
            "swot_summary": f"Key strength: {swot['Strengths'][0] if swot['Strengths'] else 'Operational readiness'}. Primary vulnerability: {swot['Weaknesses'][0] if swot['Weaknesses'] else 'Market volatility'}.",
            "competitor_insights": f"Top incumbent controls {competitors[0]['market_share']}% market share with {competitors[0]['revenue']} revenue.",
            "recommendation_summary": recommendations[0]["description"] if recommendations else "Maintain steady execution and monitor risk metrics.",
        }

        # Next Steps simple list for quick display
        next_steps = [item["action"] for item in action_plan["immediate"]]

        return {
            "projectId": project_id,
            "project": project,
            "riskScore": overall_risk,
            "riskLevel": risk_level,
            "successProbability": success_probability,
            "financialRisk": risk_scores["financial_risk"],
            "competitionRisk": risk_scores["competition_risk"],
            "technicalRisk": risk_scores["technical_risk"],
            "operationalRisk": risk_scores["operational_risk"],
            "marketRisk": risk_scores["market_risk"],
            "riskScores": risk_scores,
            "feasibilityScore": feasibility_score,
            "verdict": verdict,
            "swot": swot,
            "marketData": market_data,
            "competitors": competitors,
            "recommendations": recommendations,
            "mitigations": mitigations,
            "reasoning": reasoning,
            "strategicInsights": strategic_insights,
            "actionPlan": action_plan,
            "nextSteps": next_steps,
            "assessmentSummary": assessment_summary,
            "riskTrend": risk_trend,
            "workflowSteps": WORKFLOW_STEPS,
            "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def _generate_strategic_insights(
        cls,
        project: dict,
        risk_scores: dict,
        swot: dict,
        recommendations: list,
    ) -> List[Dict[str, str]]:
        """Generate high-level strategic intelligence pillars."""
        budget = float(project.get("budget") or 0)
        industry = project.get("industry") or "Technology"
        fin_risk = risk_scores.get("financial_risk", 50)
        comp_risk = risk_scores.get("competition_risk", 50)

        # 1. Funding Strategy
        if fin_risk >= 70 or budget < 100_000:
            funding_strategy = (
                f"Prioritize lean bootstrapping and angel seed rounds. Secure non-dilutive "
                f"grants or early customer pre-orders to extend runway past 12 months before expanding burn rate."
            )
        else:
            funding_strategy = (
                f"Leverage current capital of ₹{budget:,.0f} to build a defensible product. "
                f"Prepare Series-A institutional investment materials focusing on proven unit economics and user retention."
            )

        # 2. Market Entry Strategy
        if comp_risk >= 65:
            market_entry = (
                f"Niche Dominance (Beachhead Strategy): Infiltrate high-value sub-segments "
                f"within {industry} where incumbent solutions are bloated, overpriced, or underserved."
            )
        else:
            market_entry = (
                f"Fast-Mover Direct Capture: Deploy multi-channel digital acquisition and strategic "
                f"B2B partnerships to establish brand authority and capture initial market share."
            )

        # 3. Growth Opportunities
        opp_list = swot.get("Opportunities", [])
        opp_text = opp_list[0] if opp_list else f"Expansion in {industry} digital transformation"
        growth_opp = (
            f"Capitalize on {opp_text}. Integrate viral referral loops and self-serve onboarding "
            f"to reduce customer acquisition costs (CAC) by up to 35%."
        )

        # 4. Competitive Advantages
        str_list = swot.get("Strengths", [])
        str_text = str_list[0] if str_list else "Agile development and rapid iteration"
        competitive_advantage = (
            f"Build defensibility through {str_text}. Establish proprietary data flywheels, "
            f"superior user experience, and high switching costs."
        )

        # 5. Risk Mitigation Priorities
        top_rec = recommendations[0]["title"] if recommendations else "Continuous Risk Monitoring"
        risk_priority = (
            f"Immediate focus on '{top_rec}'. Establish weekly KPI checkpoints, automated cost "
            f"thresholds, and rapid sprint validation cycles."
        )

        return [
            {
                "category": "Funding Strategy",
                "icon": "💰",
                "title": "Capital Allocation & Runway",
                "description": funding_strategy,
                "badge": "Financial",
            },
            {
                "category": "Market Entry Strategy",
                "icon": "🎯",
                "title": "Beachhead Go-To-Market",
                "description": market_entry,
                "badge": "GTM",
            },
            {
                "category": "Growth Opportunities",
                "icon": "🚀",
                "title": "Scalability & Market Capture",
                "description": growth_opp,
                "badge": "Growth",
            },
            {
                "category": "Competitive Advantages",
                "icon": "🛡️",
                "title": "Moat & Defensibility",
                "description": competitive_advantage,
                "badge": "Moat",
            },
            {
                "category": "Risk Mitigation Priorities",
                "icon": "⚡",
                "title": "Executive Risk Controls",
                "description": risk_priority,
                "badge": "Risk",
            },
        ]

    @classmethod
    def _generate_action_plan(
        cls,
        project: dict,
        risk_scores: dict,
        recommendations: list,
        mitigations: list,
    ) -> Dict[str, List[Dict[str, str]]]:
        """Generate structured 3-tier action plan (Immediate, Short-Term, Long-Term)."""
        rec_titles = [r["title"] for r in recommendations]

        # Immediate Actions (0-30 Days)
        immediate = [
            {
                "phase": "0 - 30 Days",
                "action": "Executive Risk Alignment & MVP Scope Lockdown",
                "description": "Finalize minimum viable feature set based on high-risk constraints and validate with 10 target users.",
                "owner": "Founders / Product Lead",
                "status": "Priority 1",
            },
            {
                "phase": "0 - 30 Days",
                "action": rec_titles[0] if rec_titles else "Audit Cash Flow & Runway",
                "description": recommendations[0]["description"] if recommendations else "Establish 6-month burn rate limits and cost controls.",
                "owner": "Finance / Operations",
                "status": "Priority 1",
            },
            {
                "phase": "0 - 30 Days",
                "action": "Deploy Competitor Benchmark Tracking",
                "description": "Set up automated monitoring of direct competitor pricing, feature releases, and customer sentiment.",
                "owner": "Marketing / Strategy",
                "status": "Priority 2",
            },
        ]

        # Short-Term Actions (1-3 Months)
        short_term = [
            {
                "phase": "1 - 3 Months",
                "action": "Prototype & User Validation Sprints",
                "description": "Deploy core interactive prototype, conduct 30 structured customer interviews, and measure NPS.",
                "owner": "Engineering / Design",
                "status": "In Progress",
            },
            {
                "phase": "1 - 3 Months",
                "action": rec_titles[1] if len(rec_titles) > 1 else "Strategic Partnership Outreach",
                "description": recommendations[1]["description"] if len(rec_titles) > 1 else "Initiate pilot talks with 3 channel distribution partners.",
                "owner": "Business Development",
                "status": "Planned",
            },
            {
                "phase": "1 - 3 Months",
                "action": "Implement Lean Operational Automation",
                "description": "Automate billing, customer onboarding, and analytics pipeline to reduce team overhead.",
                "owner": "Operations",
                "status": "Planned",
            },
        ]

        # Long-Term Actions (3-12 Months)
        long_term = [
            {
                "phase": "3 - 12 Months",
                "action": "Market Expansion & Scale Deployment",
                "description": "Expand from primary beachhead market into adjacent target segments within the industry.",
                "owner": "Executive Team",
                "status": "Target",
            },
            {
                "phase": "3 - 12 Months",
                "action": "Institutional Capital Raise or Profitability Breakeven",
                "description": "Reach sustainable unit economics (LTV/CAC > 3.0) and prepare data room for institutional backing.",
                "owner": "CEO / CFO",
                "status": "Target",
            },
            {
                "phase": "3 - 12 Months",
                "action": "Build Proprietary Tech Moats & IP",
                "description": "File provisional trademarks/patents, build proprietary algorithms, and solidify switching barriers.",
                "owner": "CTO / Legal",
                "status": "Target",
            },
        ]

        return {
            "immediate": immediate,
            "shortTerm": short_term,
            "longTerm": long_term,
        }

    @classmethod
    def _generate_risk_trend(cls, current_risk: int) -> dict:
        """Generate projected 6-month risk reduction trajectory."""
        months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]
        
        # Unmitigated risk stays flat or worsens slightly
        unmitigated = [
            current_risk,
            min(100, current_risk + 2),
            min(100, current_risk + 5),
            min(100, current_risk + 7),
            min(100, current_risk + 9),
            min(100, current_risk + 12),
        ]

        # Mitigated risk steadily decreases as recommendations are executed
        mitigated = [
            current_risk,
            max(10, round(current_risk * 0.88)),
            max(10, round(current_risk * 0.74)),
            max(10, round(current_risk * 0.60)),
            max(10, round(current_risk * 0.48)),
            max(10, round(current_risk * 0.35)),
        ]

        return {
            "labels": months,
            "unmitigated": unmitigated,
            "mitigated": mitigated,
        }

    @classmethod
    def generate_and_save_report(
        cls,
        project_id: int,
        custom_factors: Optional[dict] = None,
        created_by: str = "AI Risk Intelligence Engine",
    ) -> dict:
        """Generate comprehensive assessment report and persist to database."""
        analytics = cls.get_dashboard_analytics(project_id, custom_factors)
        project = analytics["project"]
        startup_name = project.get("startup_name", f"Project #{project_id}")

        report_title = f"Comprehensive Risk & Strategy Assessment — {startup_name}"

        # Build full structured report payload
        report_content = {
            "metadata": {
                "reportTitle": report_title,
                "projectId": project_id,
                "startupName": startup_name,
                "industry": project.get("industry", "Technology"),
                "businessModel": project.get("business_model", "SaaS"),
                "targetMarket": project.get("target_market", "Not Specified"),
                "budget": float(project.get("budget") or 0),
                "generatedAt": analytics["generatedAt"],
                "createdBy": created_by,
                "version": "1.0 (Milestone 4 Production)",
            },
            "executiveSummary": {
                "overview": f"{startup_name} is an emerging {project.get('business_model')} enterprise operating in the {project.get('industry')} sector.",
                "marketPosition": f"Targeting {project.get('target_market') or 'general market'} with an allocated budget of ₹{float(project.get('budget') or 0):,.0f}.",
                "verdict": analytics["verdict"],
                "overallRiskLevel": analytics["riskLevel"],
                "riskScore": analytics["riskScore"],
                "feasibilityScore": analytics["feasibilityScore"],
                "successProbability": analytics["successProbability"],
                "summaryText": analytics["assessmentSummary"]["key_findings"],
            },
            "riskAssessment": {
                "overallRiskScore": analytics["riskScore"],
                "riskLevel": analytics["riskLevel"],
                "breakdown": {
                    "financialRisk": analytics["financialRisk"],
                    "competitionRisk": analytics["competitionRisk"],
                    "technicalRisk": analytics["technicalRisk"],
                    "operationalRisk": analytics["operationalRisk"],
                    "marketRisk": analytics["marketRisk"],
                },
                "criticalRisks": [
                    m for m in analytics["mitigations"] if m.get("impact") == "Critical"
                ],
            },
            "swotAnalysis": analytics["swot"],
            "competitorIntelligence": {
                "marketData": analytics["marketData"],
                "competitors": analytics["competitors"],
            },
            "successPrediction": {
                "successProbability": analytics["successProbability"],
                "feasibilityScore": analytics["feasibilityScore"],
                "verdict": analytics["verdict"],
            },
            "strategicRecommendations": {
                "recommendations": analytics["recommendations"],
                "mitigations": analytics["mitigations"],
                "strategicInsights": analytics["strategicInsights"],
                "reasoning": analytics["reasoning"],
            },
            "actionPlan": analytics["actionPlan"],
            "analyticsPayload": analytics,
        }

        # Save to database
        report_id = save_assessment_report(
            project_id=project_id,
            report_title=report_title,
            report_content=report_content,
            created_by=created_by,
        )

        return {
            "reportId": report_id,
            "reportTitle": report_title,
            "reportContent": report_content,
            "analytics": analytics,
        }


# Public module-level helper functions for direct access
def get_project_dashboard_analytics(project_id: int, custom_factors: Optional[dict] = None) -> dict:
    return DashboardAnalyticsService.get_dashboard_analytics(project_id, custom_factors)


def generate_project_assessment_report(project_id: int, custom_factors: Optional[dict] = None) -> dict:
    return DashboardAnalyticsService.generate_and_save_report(project_id, custom_factors)
