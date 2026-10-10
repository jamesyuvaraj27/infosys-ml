# Failure Prediction AI – Startup & Project Risk Analyzer

AI-powered Venture Market Intelligence & Risk Analysis Platform connecting project ingestion, market sizing, 5-factor risk scoring, automated SWOT analysis, strategic AI reasoning, executive assessment reporting, and PDF/JSON export.

---

## 🚀 System Architecture & Milestone Progression

Failure Prediction AI integrates 4 multi-stage milestones into a single unified platform:

1. **Milestone 1 — Data Ingestion & Market Sizing**:
   - Ingestion form for startups (industry, business model, budget, target market).
   - Automated TAM / SAM / SOM market sizing and competitor landscape analytics.
   - Relational database persistence with PostgreSQL & SQLite automatic failover.

2. **Milestone 2 — Risk Assessment & SWOT Analysis**:
   - 5-factor weighted risk engine: Market Competition, Team Expertise, Resource Availability, Innovation Level, Market Research.
   - Dynamic Success Probability and 4-factor Feasibility Rating.
   - Rule-based 4-quadrant SWOT Matrix generation (Strengths, Weaknesses, Opportunities, Threats).

3. **Milestone 3 — AI Recommendations & Strategic Reasoning**:
   - Multi-stage LangGraph workflow pipeline simulation.
   - Priority-ranked recommendation cards (Critical, High, Medium).
   - Categorized risk mitigation action plans.
   - Structured reasoning chains (Problem → Analysis → Decision → Expected Benefit).

4. **Milestone 4 — Centralized Dashboard, Reporting & Deployment**:
   - **Unified Analytics Dashboard** (`/dashboard` & `/dashboard/<id>`):
     - Section 1: Risk Analytics, Multi-Vector Risk Radar, Success Gauge, 6-Month Risk Trajectory Trend.
     - Section 2: Key Findings, TAM/SAM/SOM market sizing, Competitor Landscape, 4-Quadrant SWOT Matrix.
     - Section 3: Strategic Intelligence Pillars (Funding Strategy, Market Entry, Growth, Moat, Mitigation Priorities).
     - Section 4: 3-Tier Phased Action Plan (Immediate: 0-30d, Short-term: 1-3m, Long-term: 3-12m).
   - **Assessment Reporting Engine** (`/report/<id>` & `/reports`):
     - Publication-grade comprehensive evaluation reports.
     - Persistent storage in `assessment_reports` database table.
     - Historical report repository and versioning.
   - **Export Module**:
     - Server-side styled PDF generation via ReportLab with dynamic header/footer and page numbering (`/api/reports/download/<id>/pdf`).
     - Structured JSON export for integrations (`/api/reports/download/<id>/json`).
     - Browser print-optimized view (`window.print()`).
     - One-click share link generator with toast notifications.
   - **Full REST API Suite**: Complete endpoints for dashboard, analytics, report generation, and exports.
   - **Automated Test Suite**: End-to-end testing with unit and integration tests.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+ · Flask 3.0.3 · Gunicorn 21.2.0
- **Database**: PostgreSQL (Neon Cloud / Local) with automatic SQLite fallback (`sqlite3`, `psycopg2-binary`)
- **PDF Generation**: ReportLab 5.0+
- **Frontend**: Modern Vanilla CSS Design System · TailwindCSS (CDN) · Chart.js (CDN) · Google Fonts (Inter & JetBrains Mono)
- **Deployment**: Vercel / Render / Railway / Docker / Supabase / Neon

---

## 📂 Project Structure

```
├── app.py                     # Central Flask application routes & REST APIs
├── dashboard_service.py       # Milestone 4 Analytics Aggregation & Report Service
├── pdf_generator.py           # Publication-quality PDF generation engine (ReportLab)
├── database.py                # Database access layer (PostgreSQL + SQLite fallback)
├── market_analysis.py         # Milestone 1 TAM/SAM/SOM & competitor models
├── risk_engine.py             # Milestone 2 5-factor risk calculation engine
├── swot_analysis.py           # Milestone 2 4-quadrant SWOT matrix generator
├── feasibility.py             # Milestone 2 4-factor project feasibility calculator
├── recommendation_engine.py   # Milestone 3 AI recommendations generator
├── risk_mitigation.py         # Milestone 3 Risk mitigation catalogue & mapping
├── workflow.py                # Milestone 3 5-stage strategic reasoning pipeline
├── test_milestone4.py         # Milestone 4 automated test suite
├── requirements.txt           # Production dependencies
├── Procfile                   # Process file for Render / Railway / Heroku
├── render.yaml                # Infrastructure-as-code for Render deployment
├── vercel.json                # Serverless configuration for Vercel
├── .env.example               # Environment variables template
├── static/
│   ├── css/style.css          # Core design tokens, card styles, and print layout
│   └── js/dashboard.js        # Chart.js initializations (Radar, Gauge, Trend Line)
└── templates/
    ├── base.html              # Shared navigation, toast system, and layout
    ├── dashboard.html         # Milestone 4 Unified Analytics Dashboard
    ├── report.html            # Milestone 4 Comprehensive Assessment Report
    ├── report_history.html    # Milestone 4 Assessment Reports Repository
    ├── project.html           # Milestone 1 Project Ingestion Form
    ├── risk_assessment.html   # Milestone 2 Risk & SWOT Dashboard
    └── recommendations.html   # Milestone 3 AI Recommendations View
```

---

## ⚡ Quickstart & Local Setup

### 1. Clone & Setup Virtual Environment
```bash
git clone <repository_url>
cd infosys

# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Configure your database connection (Neon PostgreSQL or SQLite fallback):
```env
# Cloud PostgreSQL (e.g. Neon)
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Or force SQLite for local development:
# DB_ENGINE=sqlite
```

### 3. Run the Application
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🧪 Running Automated Tests

Run the complete Milestone 4 test suite validating calculations, database operations, PDF exports, and API routes:

```bash
# Run tests
python test_milestone4.py
```

---

## 📡 REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/:projectId` | Complete dashboard analytics payload (JSON) |
| `GET` | `/api/analytics/:projectId` | Simplified analytics response (Risk, SWOT, Insights) |
| `POST` | `/api/reports/generate` | Generate and persist assessment report from JSON body |
| `POST` | `/api/reports/generate/:projectId` | Generate and persist assessment report for project |
| `GET` | `/api/reports/:projectId` | List all stored assessment reports for project |
| `GET` | `/api/reports/download/:reportId/pdf` | Stream download styled assessment PDF |
| `GET` | `/api/reports/download-pdf/:projectId` | Stream download latest assessment PDF for project |
| `GET` | `/api/reports/download/:reportId/json` | Stream download structured assessment JSON |
| `GET` | `/api/reports/download-json/:projectId` | Stream download latest assessment JSON for project |
| `GET` | `/api/reports/history/:projectId` | Get report history metadata for project |
| `POST` | `/api/risk-assessment/:projectId` | Calculate dynamic risk & SWOT scores from factors |
| `POST` | `/api/recommendations/:projectId` | Calculate AI recommendations & mitigations |

---

## 🌐 Production Deployment

### 1. Deploy on Render / Railway
1. Push repository to GitHub.
2. Link repository on **Render** (as a Web Service) or **Railway**.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --workers 2 --threads 4 --timeout 120`
5. Environment Variables:
   - `DATABASE_URL`: Your Neon/Supabase PostgreSQL connection string
   - `FLASK_ENV`: `production`

### 2. Deploy on Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel --prod`
3. Set environment variable `DATABASE_URL` in Vercel project settings.


##  Contributors
* [S Dikshita](https://github.com/Dikshita191) - Added project environment configurations.
