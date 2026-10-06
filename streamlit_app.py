"""Streamlit unified application for Failure Prediction AI – Startup & Project Risk Analyzer.

Includes:
- Market Ingestion & Sizing: Project Submission, Database Explorer, TAM/SAM/SOM Market Sizing, Competitor Landscape.
- Risk & SWOT Assessment: 5-Factor Risk Scoring Engine, SWOT Analysis Matrix, Feasibility Assessment.
- Strategic Recommendations: AI Recommendations Engine, Risk Mitigation Action Cards, Reasoning Workflow, Final Assessment Report.
"""
import streamlit as st
import json
import pandas as pd

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
)
from market_analysis import get_competitors, get_market_data
from risk_engine import (
    calculate_risk,
    calculate_success_probability,
    get_risk_status,
)
from swot_analysis import generate_swot
from feasibility import calculate_feasibility
from recommendation_engine import generate_recommendations
from risk_mitigation import generate_mitigation
from workflow import run_workflow, WORKFLOW_STEPS

# Initialize Databases
init_db()
init_milestone3_tables()
init_milestone4_tables()

# Configure Page
st.set_page_config(
    page_title="Failure Prediction AI – Startup & Project Risk Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium SaaS Light Theme CSS matching the Vercel/Tailwind UI
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Top Brand Bar */
    .brand-header {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 24px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    .brand-title {
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .brand-badge {
        background: #2563eb;
        color: #ffffff;
        font-weight: 700;
        font-size: 12px;
        padding: 4px 8px;
        border-radius: 6px;
    }

    /* KPI Cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        margin-bottom: 12px;
    }
    .kpi-blue { border-left: 5px solid #2563eb; }
    .kpi-purple { border-left: 5px solid #7c3aed; }
    .kpi-amber { border-left: 5px solid #f59e0b; }
    .kpi-emerald { border-left: 5px solid #10b981; }
    .kpi-red { border-left: 5px solid #ef4444; }

    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #0f172a;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 4px;
    }
    .kpi-subtext {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Content Cards */
    .saas-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    /* SWOT Quadrants */
    .swot-card {
        border-radius: 10px;
        padding: 16px;
        height: 100%;
    }
    .swot-s { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
    .swot-w { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
    .swot-o { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; }
    .swot-t { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }

    /* Action Recommendation Card */
    .rec-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #7c3aed;
    }

    /* Tag badges */
    .tag-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
    }
    .tag-critical { background: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
    .tag-high { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
    .tag-medium { background: #eff6ff; color: #1e40af; border: 1px solid #93c5fd; }
    .tag-low { background: #f0fdf4; color: #166534; border: 1px solid #86efac; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    """
    <div class="brand-header">
        <div class="brand-title">
            <span class="brand-badge">AI</span>
            <span>Failure Prediction AI</span>
            <span style="font-size: 12px; color: #64748b; font-weight: 500;">— Startup &amp; Project Risk Analyzer</span>
        </div>
        <div style="font-size: 12px; color: #64748b; font-weight: 600;">
            <span style="color: #2563eb;">M1 Data</span> • 
            <span style="color: #059669;">M2 Risk/SWOT</span> • 
            <span style="color: #7c3aed;">M3 Recommendations</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch Data
all_projects = get_all_projects()
project_count = get_project_count()

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    nav_selection = st.radio(
        "Select Module:",
        [
            "📊 Dashboard & Market Intelligence",
            "➕ Submit Project",
            "🛡️ Risk Assessment & SWOT",
            "🎯 Recommendations & Reasoning",
        ],
        index=0,
    )
    
    st.divider()
    
    if all_projects:
        st.markdown("### 📁 Active Project")
        project_dict = {f"#{p['id']} - {p['startup_name']} ({p['industry']})": p["id"] for p in all_projects}
        selected_project_label = st.selectbox("Current Project:", list(project_dict.keys()), key="global_project_select")
        active_project_id = project_dict[selected_project_label]
        selected_project = get_project_by_id(active_project_id)
        
        st.write("")
        if st.button("🗑️ Delete This Project", type="secondary", use_container_width=True):
            delete_project(active_project_id)
            st.success(f"Project #{active_project_id} deleted permanently from database.")
            st.rerun()
    else:
        selected_project = None
        st.info("No projects in database yet. Use 'Submit Project' to create one.")

# ==============================================================================
# TAB 1: DASHBOARD & MARKET INTELLIGENCE
# ==============================================================================
if nav_selection == "📊 Dashboard & Market Intelligence":
    st.markdown("## 📊 Venture Dashboard & Market Intelligence")
    st.caption("Live project ingestion, PostgreSQL/SQLite storage, TAM/SAM/SOM market sizing, and competitor analysis.")
    
    # KPI Strip
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-blue">
                <div class="kpi-label">📁 Total Projects</div>
                <div class="kpi-value">{project_count}</div>
                <div class="kpi-subtext">Stored in Database</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi2:
        num_industries = len(set(p["industry"] for p in all_projects)) if all_projects else 0
        st.markdown(
            f"""
            <div class="kpi-card kpi-purple">
                <div class="kpi-label">🏭 Industries Analyzed</div>
                <div class="kpi-value">{num_industries}</div>
                <div class="kpi-subtext">Market Coverage</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi3:
        avg_budget = sum(float(p["budget"] or 0) for p in all_projects) / len(all_projects) if all_projects else 0
        st.markdown(
            f"""
            <div class="kpi-card kpi-amber">
                <div class="kpi-label">💰 Average Budget</div>
                <div class="kpi-value">₹{avg_budget:,.0f}</div>
                <div class="kpi-subtext">Across All Projects</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-emerald">
                <div class="kpi-label">✅ System Status</div>
                <div class="kpi-value" style="color: #10b981;">Active</div>
                <div class="kpi-subtext">All Modules Ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if selected_project:
        col_proj, col_market, col_comp = st.columns([1.2, 1.2, 1.2])
        
        market_data = get_market_data(selected_project["industry"], selected_project["budget"])
        competitors = get_competitors(selected_project["industry"])
        
        with col_proj:
            st.markdown(
                f"""
                <div class="saas-box" style="height: 100%;">
                    <div style="font-size: 11px; font-weight: 700; color: #2563eb; background: #eff6ff; padding: 2px 8px; border-radius: 4px; display: inline-block;">
                        Project #{selected_project['id']}
                    </div>
                    <h3 style="margin-top: 8px; margin-bottom: 4px; font-weight: 800;">{selected_project['startup_name']}</h3>
                    <p style="font-size: 12px; color: #64748b;"><strong>Industry:</strong> {selected_project['industry']} | <strong>Model:</strong> {selected_project['business_model']}</p>
                    <p style="font-size: 12px; color: #64748b;"><strong>Target Market:</strong> {selected_project.get('target_market') or '—'}</p>
                    <div style="font-size: 20px; font-weight: 800; color: #059669; font-family: monospace; margin: 10px 0;">
                        ₹{float(selected_project['budget'] or 0):,.0f}
                    </div>
                    <div style="font-size: 12px; color: #475569; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-top: 10px;">
                        <strong>Description:</strong><br>{selected_project.get('project_description') or 'No description provided.'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with col_market:
            st.markdown(
                f"""
                <div class="saas-box" style="height: 100%;">
                    <div style="font-size: 13px; font-weight: 700; text-transform: uppercase; color: #1e293b; margin-bottom: 12px;">
                        📊 Market Analysis (TAM/SAM/SOM)
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; text-align: center; margin-bottom: 16px;">
                        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 8px;">
                            <div style="font-size: 15px; font-weight: 800; color: #1e40af; font-family: monospace;">{market_data['tam']}</div>
                            <div style="font-size: 10px; font-weight: 700; color: #64748b;">TAM</div>
                        </div>
                        <div style="background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 8px; padding: 8px;">
                            <div style="font-size: 15px; font-weight: 800; color: #6d28d9; font-family: monospace;">{market_data['sam']}</div>
                            <div style="font-size: 10px; font-weight: 700; color: #64748b;">SAM</div>
                        </div>
                        <div style="background: #fdf2f8; border: 1px solid #fbcfe8; border-radius: 8px; padding: 8px;">
                            <div style="font-size: 15px; font-weight: 800; color: #be185d; font-family: monospace;">{market_data['som']}</div>
                            <div style="font-size: 10px; font-weight: 700; color: #64748b;">SOM</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            trend_data = market_data.get("market_trend", [])
            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                trend_df.rename(columns={"year": "Year", "value": "SAM Projection (₹)"}, inplace=True)
                st.line_chart(trend_df.set_index("Year"), height=160)
        
        with col_comp:
            st.markdown(
                """
                <div class="saas-box">
                    <div style="font-size: 13px; font-weight: 700; text-transform: uppercase; color: #1e293b; margin-bottom: 12px;">
                        🏢 Competitor Landscape
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            comp_df = pd.DataFrame([
                {"Competitor": c["name"], "Market Share (%)": c["market_share"], "Revenue": c["revenue"], "Growth": c["growth"]}
                for c in competitors
            ])
            st.dataframe(comp_df, hide_index=True)
            st.bar_chart(comp_df.set_index("Competitor")["Market Share (%)"], height=160)

    # All Projects Table
    st.markdown("### 📋 All Stored Projects")
    if all_projects:
        table_df = pd.DataFrame([
            {
                "ID": f"#{p['id']}",
                "Startup Name": p["startup_name"],
                "Industry": p["industry"],
                "Business Model": p["business_model"],
                "Budget": f"₹{float(p['budget'] or 0):,.0f}",
                "Target Market": p.get("target_market", "—"),
            }
            for p in all_projects
        ])
        st.dataframe(table_df, hide_index=True)

# ==============================================================================
# TAB 2: SUBMIT PROJECT
# ==============================================================================
elif nav_selection == "➕ Submit Project":
    st.markdown("## ➕ Submit New Project")
    st.caption("Enter your startup details below to save into the database and initialize risk analysis.")
    
    with st.form("new_project_form"):
        col1, col2 = st.columns(2)
        with col1:
            startup_name = st.text_input("Startup Name *", placeholder="e.g. HealthAI Diagnostics")
            industry = st.selectbox("Industry *", [
                "Technology", "Healthcare", "Education", "Finance",
                "E-commerce", "Food & Beverage", "Agriculture", "Other"
            ])
            business_model = st.selectbox("Business Model *", ["B2B", "B2C", "B2B2C", "Marketplace", "SaaS", "D2C"])
        
        with col2:
            target_market = st.text_input("Target Market", placeholder="e.g. Hospitals & Clinics in South Asia")
            budget = st.number_input("Project Budget (₹)", min_value=0.0, step=10000.0, value=200000.0)
            project_description = st.text_area("Project Description", placeholder="Brief description of the product, value proposition, and core capabilities...")
        
        submit_btn = st.form_submit_button("🚀 Submit Project")
        
        if submit_btn:
            if not startup_name.strip():
                st.error("Please provide a Startup Name.")
            else:
                new_project_data = {
                    "startup_name": startup_name.strip(),
                    "industry": industry,
                    "business_model": business_model,
                    "target_market": target_market.strip(),
                    "budget": budget,
                    "project_description": project_description.strip(),
                }
                new_id = insert_project(new_project_data)
                st.success(f"✅ Project #{new_id} '{startup_name}' successfully submitted and saved to Database!")
                st.info("Switch to the '📊 Dashboard & Market Intelligence' or '🛡️ Risk Assessment & SWOT' tab from the sidebar to inspect analysis.")

# ==============================================================================
# TAB 3: RISK ASSESSMENT & SWOT
# ==============================================================================
elif nav_selection == "🛡️ Risk Assessment & SWOT":
    if not selected_project:
        st.warning("Please submit a project first.")
        st.stop()
        
    st.markdown(f"## 🛡️ Risk Assessment & SWOT Analysis")
    st.caption(f"Analyzing: **{selected_project['startup_name']}** ({selected_project['industry']}) • Budget: ₹{float(selected_project['budget'] or 0):,.0f}")
    
    col_inputs, col_results = st.columns([1.1, 1.4])
    
    with col_inputs:
        st.markdown(
            """
            <div class="saas-box">
                <div style="font-size: 13px; font-weight: 700; text-transform: uppercase; color: #1e293b; margin-bottom: 8px;">
                    ⚙️ Risk Assessment Factors
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        market_competition = st.selectbox("1. Market Competition", ["Low", "Medium", "High"], index=1)
        team_expertise = st.selectbox("2. Team Technical Expertise", ["High", "Medium", "Low"], index=1)
        resource_availability = st.selectbox("3. Resource Availability", ["Good", "Moderate", "Limited"], index=1)
        innovation_level = st.selectbox("4. Innovation Level", ["High", "Medium", "Low"], index=1)
        market_research = st.selectbox("5. Market Research Depth", ["Comprehensive", "Moderate", "Limited"], index=1)
        
        st.markdown("---")
        st.caption("Feasibility Factors (0 - 100):")
        f_market = st.slider("Market Opportunity", 0, 100, 70)
        f_team = st.slider("Team Capability", 0, 100, 65)
        f_comp = st.slider("Competitive Advantage", 0, 100, 60)
        f_res = st.slider("Resource Readiness", 0, 100, 55)
        
        # Calculate Risk and Feasibility using exact signatures
        risk_score = calculate_risk(
            market_competition=market_competition,
            team_expertise=team_expertise,
            resource_availability=resource_availability,
            innovation_level=innovation_level,
            market_research=market_research,
        )
        risk_status = get_risk_status(risk_score)
        success_prob = calculate_success_probability(risk_score)
        
        feasibility_score = calculate_feasibility(
            market_opportunity=f_market,
            team_capability=f_team,
            competitive_advantage=f_comp,
            resource_availability=f_res,
        )
        
        if feasibility_score >= 80:
            feasibility_label = "Highly Feasible"
        elif feasibility_score >= 60:
            feasibility_label = "Feasible"
        elif feasibility_score >= 40:
            feasibility_label = "Moderately Feasible"
        else:
            feasibility_label = "Not Feasible"
            
        swot = generate_swot(
            team_expertise=team_expertise,
            innovation_level=innovation_level,
            market_competition=market_competition,
            resource_availability=resource_availability,
            market_research=market_research,
        )
    
    with col_results:
        # Score KPIs
        r_kpi1, r_kpi2, r_kpi3 = st.columns(3)
        with r_kpi1:
            st.markdown(
                f"""
                <div class="kpi-card kpi-amber">
                    <div class="kpi-label">Overall Risk</div>
                    <div class="kpi-value">{risk_score} <span style="font-size: 14px; color: #64748b;">/ 100</span></div>
                    <div class="kpi-subtext" style="font-weight: 700; color: #d97706;">{risk_status}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with r_kpi2:
            st.markdown(
                f"""
                <div class="kpi-card kpi-emerald">
                    <div class="kpi-label">Success Probability</div>
                    <div class="kpi-value">{success_prob:.0f}%</div>
                    <div class="kpi-subtext">Statistical Projection</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with r_kpi3:
            st.markdown(
                f"""
                <div class="kpi-card kpi-purple">
                    <div class="kpi-label">Feasibility Score</div>
                    <div class="kpi-value">{feasibility_score:.0f}%</div>
                    <div class="kpi-subtext" style="font-weight: 700; color: #7c3aed;">{feasibility_label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        # Risk Breakdown chart
        factors_df = pd.DataFrame({
            "Dimension": ["Market Opportunity", "Team Capability", "Competitive Adv.", "Resource Readiness"],
            "Score (0-100)": [f_market, f_team, f_comp, f_res]
        })
        st.bar_chart(factors_df.set_index("Dimension"), height=180)

    # 4-Quadrant SWOT Matrix
    st.markdown("### 🧩 4-Quadrant SWOT Analysis Matrix")
    swot_c1, swot_c2 = st.columns(2)
    with swot_c1:
        st.markdown(
            f"""
            <div class="swot-card swot-s">
                <h4 style="margin: 0 0 8px 0; font-weight: 800;">💪 STRENGTHS (Internal)</h4>
                <ul>{''.join(f'<li>{item}</li>' for item in swot.get('Strengths', []))}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="swot-card swot-o">
                <h4 style="margin: 0 0 8px 0; font-weight: 800;">🚀 OPPORTUNITIES (External)</h4>
                <ul>{''.join(f'<li>{item}</li>' for item in swot.get('Opportunities', []))}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with swot_c2:
        st.markdown(
            f"""
            <div class="swot-card swot-w">
                <h4 style="margin: 0 0 8px 0; font-weight: 800;">⚠️ WEAKNESSES (Internal)</h4>
                <ul>{''.join(f'<li>{item}</li>' for item in swot.get('Weaknesses', []))}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="swot-card swot-t">
                <h4 style="margin: 0 0 8px 0; font-weight: 800;">🛑 THREATS (External)</h4>
                <ul>{''.join(f'<li>{item}</li>' for item in swot.get('Threats', []))}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==============================================================================
# TAB 4: RECOMMENDATIONS & REASONING
# ==============================================================================
elif nav_selection == "🎯 Recommendations & Reasoning":
    if not selected_project:
        st.warning("Please submit a project first.")
        st.stop()
        
    st.markdown(f"## 🎯 AI Recommendations & Strategic Reasoning")
    st.caption(f"Decision Support Layer for: **{selected_project['startup_name']}**")
    
    budget = float(selected_project.get("budget") or 0)
    industry = (selected_project.get("industry") or "").lower()
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

    # Run workflow
    workflow_state = run_workflow(
        project=selected_project,
        risk_scores=risk_scores,
        swot=None,
        feasibility_score=max(0, 100 - overall_risk),
    )

    existing_recs = workflow_state["recommendations"]
    existing_mits = workflow_state["mitigations"]

    # KPI Row
    m3_k1, m3_k2, m3_k3, m3_k4 = st.columns(4)
    with m3_k1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-purple">
                <div class="kpi-label">🎯 Recommendations</div>
                <div class="kpi-value">{len(existing_recs)}</div>
                <div class="kpi-subtext">Generated Actions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3_k2:
        critical_count = sum(1 for r in existing_recs if r.get("priority") in ["Critical", "High"])
        st.markdown(
            f"""
            <div class="kpi-card kpi-red">
                <div class="kpi-label">🚨 High/Critical Actions</div>
                <div class="kpi-value" style="color: #dc2626;">{critical_count}</div>
                <div class="kpi-subtext">Immediate Attention</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3_k3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-amber">
                <div class="kpi-label">⚠️ Risk Score</div>
                <div class="kpi-value">{overall_risk} <span style="font-size: 14px; color: #64748b;">/ 100</span></div>
                <div class="kpi-subtext">Automated Index</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3_k4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-emerald">
                <div class="kpi-label">🏆 Feasibility</div>
                <div class="kpi-value" style="color: #059669;">{max(0, 100 - overall_risk):.0f}%</div>
                <div class="kpi-subtext">Feasibility Projection</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2-Column Layout
    m3_left, m3_right = st.columns([1.3, 1.1])
    
    with m3_left:
        sub_tab = st.radio("View Decisions:", ["🎯 AI Recommendations", "🛡️ Risk Mitigations"], horizontal=True)
        
        if sub_tab == "🎯 AI Recommendations":
            for r in existing_recs:
                p_class = "tag-critical" if r.get("priority") == "Critical" else ("tag-high" if r.get("priority") == "High" else "tag-medium")
                st.markdown(
                    f"""
                    <div class="rec-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span class="tag-badge {p_class}">{r.get('priority', 'Medium')} Priority</span>
                        </div>
                        <h4 style="margin: 4px 0 6px 0; font-weight: 800; color: #0f172a;">{r.get('title')}</h4>
                        <p style="font-size: 13px; color: #334155; margin-bottom: 0;">{r.get('description')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            for m in existing_mits:
                st.markdown(
                    f"""
                    <div class="rec-card" style="border-left-color: #2563eb;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span class="tag-badge tag-high">{m.get('risk')}</span>
                            <span style="font-size: 11px; color: #64748b;">Impact: <strong>{m.get('impact')}</strong></span>
                        </div>
                        <p style="font-size: 13px; color: #334155; margin-bottom: 0;">{m.get('mitigation')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
    with m3_right:
        st.markdown(
            """
            <div class="saas-box">
                <div style="font-size: 13px; font-weight: 700; text-transform: uppercase; color: #1e293b; margin-bottom: 8px;">
                    🧠 5-Stage Reasoning &amp; Advisory Pipeline
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        for step in WORKFLOW_STEPS:
            with st.expander(f"{step['icon']} {step['name']}", expanded=True):
                st.write(step['description'])
                if step['name'] == "Strategic Reasoning" and workflow_state.get("reasoning"):
                    for chain in workflow_state["reasoning"]:
                        st.info(f"**Trigger:** {chain.get('trigger')} → **Strategy:** {chain.get('strategy')}")
                elif step['name'] == "Validation":
                    st.success(f"Validation Status: {'PASSED' if workflow_state.get('validation_passed') else 'PENDING'}")
                elif step['name'] == "Report Generation" and workflow_state.get("report"):
                    rep = workflow_state["report"]
                    st.write(f"**Executive Verdict:** {rep.get('verdict')}")
                    st.write(f"**Summary:** {rep.get('summary')}")

    # Downloadable Final Assessment Report
    st.divider()
    st.markdown("### 📄 Final Assessment Report")
    
    report_content = f"""# FAILURE PREDICTION AI — STARTUP & PROJECT RISK ANALYZER — ASSESSMENT REPORT
Project Name: {selected_project['startup_name']}
Industry: {selected_project['industry']}
Business Model: {selected_project['business_model']}
Budget: ₹{budget:,.0f}
Target Market: {selected_project.get('target_market', 'N/A')}

--- RISK & FEASIBILITY ANALYSIS ---
Overall Risk Index: {overall_risk} / 100
Feasibility Score: {max(0, 100 - overall_risk)}%

--- STRATEGIC RECOMMENDATIONS ---
Total Recommended Actions: {len(existing_recs)}
High/Critical Priority Items: {critical_count}

Executive Verdict: {workflow_state.get('report', {}).get('verdict', 'Feasible')}
Summary: {workflow_state.get('report', {}).get('summary', 'Standard implementation trajectory.')}
"""
    st.text_area("Executive Summary:", report_content, height=180)
    st.download_button(
        label="📥 Download Executive Assessment Report (.txt)",
        data=report_content,
        file_name=f"Failure_Prediction_AI_Report_{selected_project['startup_name'].replace(' ', '_')}.txt",
        mime="text/plain",
    )
