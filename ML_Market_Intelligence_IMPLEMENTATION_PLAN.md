# 🚀 ML Market Intelligence — Milestone 1 Implementation Plan
> **Project**: ML Market Intelligence System (Failure Prediction AI — Phase 1)  
> **Stack**: Python · Flask · PostgreSQL · Chart.js · Tailwind CSS (via CDN)  
> **Milestone Goal**: Form → Flask → PostgreSQL → Live Dashboard  
> **Estimated build time**: 3–4 hours in one sitting  

---

## 📦 Top 3 Reference Repos — Evaluation

| # | Repo | Stars | Why Consider It | Why Not Best |
|---|------|-------|-----------------|--------------|
| 1 | [app-generator/flask-material-dashboard](https://github.com/app-generator/flask-material-dashboard) | 500+ | Production-grade, PostgreSQL + SQLAlchemy, Blueprints, Docker | Overkill for M1; has auth/pro paywall overhead |
| 2 | [fr33dz/flask-chartjs](https://github.com/fr33dz/flask-chartjs) | 80+ | Minimal Flask + Chart.js dashboard, clean separation | Too minimal — no DB, no forms, just charts |
| 3 | [datahappy1/flask_chartjs_drilldown_example_project](https://github.com/datahappy1/flask_chartjs_drilldown_example_project) | 120+ | Flask + Chart.js drilldown, live data from backend | SQLite-only, no PostgreSQL, UI is plain |

### ✅ Decision: **Build from Mentor's ZIP structure** (best fit)
The mentor's `ML_Market_Intelligence_Project.zip` (Drive link) already has the correct project skeleton (`app.py`, `database.py`, `market_analysis.py`, `templates/`, `static/`). Reference `flask-chartjs` for Chart.js patterns and `flask-material-dashboard` for layout inspiration. **Do not clone any repo — start from the ZIP.**

---

## 🗂️ Final Project Structure (What You're Building)

```
ML_Market_Intelligence_Project/
│
├── app.py                    ← Flask routes (form submit + dashboard data)
├── database.py               ← PostgreSQL connection (psycopg2 + .env)
├── market_analysis.py        ← TAM/SAM/SOM + competitor calc logic
├── requirements.txt          ← pip dependencies
├── .env                      ← DB credentials (gitignored)
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html             ← Navbar + shared layout (Tailwind CDN)
│   ├── dashboard.html        ← Main landing: stats + charts
│   ├── project.html          ← Project submission form
│   └── placeholder.html      ← "Coming Soon" for M2/M3 placeholders
│
└── static/
    ├── css/
    │   └── style.css         ← Custom overrides (minimal)
    └── js/
        └── dashboard.js      ← Chart.js init code
```

---

## 🛠️ Phase 0 — Prerequisites (Do Once)

### Step 1: Install Python 3.10+
```
https://www.python.org/downloads/
```
> ⚠️ Tick **"Add Python to PATH"** during Windows setup.

Verify:
```bash
python --version
# Expected: Python 3.10.x or higher
```

### Step 2: Install VS Code + Extensions
```
https://code.visualstudio.com/
```
Extensions to install (Ctrl+Shift+X):
- `Python` (Microsoft)
- `Pylance`
- `SQLTools` (for PostgreSQL inspection inside VS Code)

### Step 3: Install PostgreSQL 16
```
https://www.postgresql.org/download/windows/
```
During install:
- Username: `postgres`
- Password: **choose your own, write it down**
- Port: `5432` (default, keep it)
- pgAdmin 4: **install it** (bundled)

---

## 🗄️ Phase 1 — Database Setup (pgAdmin)

### Step 4: Create Database
Open **pgAdmin 4** → right-click `Databases` → **Create → Database**:
```
Database name: ml_project
```

### Step 5: Create Table
Open `ml_project` → **Tools → Query Tool** → paste and run:

```sql
CREATE TABLE IF NOT EXISTS projects (
    id               SERIAL PRIMARY KEY,
    startup_name     VARCHAR(150) NOT NULL,
    industry         VARCHAR(100) NOT NULL,
    business_model   VARCHAR(100) NOT NULL,
    target_market    VARCHAR(150),
    budget           NUMERIC(15, 2),
    project_description TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Verify:
```sql
SELECT * FROM projects;
-- Should return: (0 rows)  ← empty table, that's correct
```

---

## 💻 Phase 2 — VS Code Project Setup

### Step 6: Download the ZIP from Drive
```
https://drive.google.com/file/d/1BiD4phzET-2gHsfGrtWwJd5Xhw498GUm/view
```
Extract to: `C:\Projects\ML_Market_Intelligence_Project\`

Open in VS Code:
```
File → Open Folder → ML_Market_Intelligence_Project
```

### Step 7: Create Virtual Environment
Open terminal in VS Code (**Terminal → New Terminal**):

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Prompt should now show:
# (venv) PS C:\Projects\ML_Market_Intelligence_Project>
```

### Step 8: Install Dependencies
```bash
pip install flask psycopg2-binary python-dotenv pandas
```

Verify:
```bash
pip freeze
# Must see: Flask, psycopg2-binary, python-dotenv, pandas
```

Save to requirements.txt:
```bash
pip freeze > requirements.txt
```

---

## 🔑 Phase 3 — Configure Database Connection

### Step 9: Create `.env` File
Create a new file `.env` in the project root:

```env
DB_HOST=localhost
DB_NAME=ml_project
DB_USER=postgres
DB_PASSWORD=YOUR_ACTUAL_POSTGRES_PASSWORD
DB_PORT=5432
```
> Replace `YOUR_ACTUAL_POSTGRES_PASSWORD` with your real password.

### Step 10: Create `.gitignore`
```
venv/
.env
__pycache__/
*.pyc
```

---

## 🏗️ Phase 4 — Build the Files (Paste Into Claude Code)

> **HOW TO USE THIS PLAN IN CLAUDE**: Open Claude Code (`claude` in terminal). For each file below, say:  
> *"Create [filename] with this exact spec: [paste the spec block]"*  
> Claude Code will write the file. Then move to the next.

---

### FILE 1: `database.py`
**Spec for Claude Code:**
```
Create database.py that:
- Loads .env using python-dotenv
- Has get_connection() that returns a psycopg2 connection using DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT from env
- Has init_db() that runs CREATE TABLE IF NOT EXISTS for projects table with columns: id SERIAL PK, startup_name VARCHAR(150) NOT NULL, industry VARCHAR(100) NOT NULL, business_model VARCHAR(100) NOT NULL, target_market VARCHAR(150), budget NUMERIC(15,2), project_description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- Has get_all_projects() that returns all rows as list of dicts
- Has get_project_count() that returns total count integer
```

---

### FILE 2: `market_analysis.py`
**Spec for Claude Code:**
```
Create market_analysis.py that:
- Has get_market_data(industry, budget) function that returns a dict with:
  - tam: Total Addressable Market (budget * 200 formatted as $X.XB or $X.XM)
  - sam: Serviceable Addressable Market (budget * 70 formatted)
  - som: Serviceable Obtainable Market (budget * 0.024 formatted)
  - growth_rate: random between 8-15 with 1 decimal
  - market_trend: list of 6 dicts with year (2021-2026) and value (ascending market size numbers)
- Has get_competitors(industry) function that returns list of 3 dicts each with:
  - name: "Competitor A/B/C"
  - market_share: 28, 22, 15
  - revenue: "$45M", "$38M", "$25M"
  - growth: "+12%", "+8%", "+5%"
```

---

### FILE 3: `app.py`
**Spec for Claude Code:**
```
Create app.py Flask application that:
- Imports Flask, render_template, request, jsonify, redirect, url_for from flask
- Imports get_connection, init_db, get_all_projects, get_project_count from database
- Imports get_market_data, get_competitors from market_analysis
- Calls init_db() on startup
- Route GET / → renders dashboard.html with: projects=get_all_projects(), count=get_project_count(), latest=first project or None
- Route GET /submit → renders project.html (empty form)
- Route POST /submit → reads form fields (startup_name, industry, business_model, target_market, budget, project_description), inserts into PostgreSQL projects table, redirects to /dashboard/[new_id]
- Route GET /dashboard/<int:project_id> → gets project by id from DB, gets market_data=get_market_data(industry, budget), gets competitors=get_competitors(industry), renders dashboard.html with all this data
- Route GET /api/market-data/<int:project_id> → returns JSON with market_data and competitors for that project (used by Chart.js)
- if __name__ == "__main__": app.run(debug=True)
```

---

### FILE 4: `templates/base.html`
**Spec for Claude Code:**
```
Create templates/base.html that:
- Uses Tailwind CSS via CDN (https://cdn.tailwindcss.com)
- Uses Chart.js via CDN (https://cdn.jsdelivr.net/npm/chart.js)
- Has a top navbar with:
  - Left: "ML Intelligence" logo text in gradient (blue to purple)
  - Center nav links: Dashboard (/), Submit Project (/submit), Risk Assessment (#), AI Advisor (#)
  - Right: "Milestone 1" badge in blue
- Dark theme: bg-gray-900 overall, text-white
- Has {% block content %}{% endblock %} in main section
- Footer: "ML Market Intelligence System | Milestone 1 - Data Collection"
- Includes {% block scripts %}{% endblock %} before closing body
```

---

### FILE 5: `templates/project.html`
**Spec for Claude Code:**
```
Create templates/project.html that extends base.html with:
- Page title: "Submit Your Project"
- Card-style form (bg-gray-800 rounded-xl p-8) centered max-w-2xl
- Form action="/submit" method="POST"
- Fields with labels, dark input styling (bg-gray-700 border-gray-600 text-white rounded-lg p-3 w-full):
  1. startup_name (text, required, placeholder "e.g. EduTech India")
  2. industry (select dropdown: Technology, Healthcare, Education, Finance, E-commerce, Food & Beverage, Agriculture, Other)
  3. business_model (select: B2B, B2C, B2B2C, Marketplace, SaaS, D2C)
  4. target_market (text, placeholder "e.g. College students in Tier-2 cities")
  5. budget (number, placeholder "50000")
  6. project_description (textarea rows=4, placeholder "Describe your startup idea...")
- Submit button: full width, gradient bg-gradient-to-r from-blue-600 to-purple-600, text-white, py-3, rounded-lg, "Analyze My Project →"
- Left side stats panel (on md: grid 2 cols) showing "Why Submit?" with 3 icon+text items: Market Size Analysis, Competitor Landscape, Risk Assessment
```

---

### FILE 6: `templates/dashboard.html`
**Spec for Claude Code:**
```
Create templates/dashboard.html that extends base.html with:

SECTION 1 - Hero stats row (4 cards, grid-cols-4):
- Total Projects (from count variable)
- Market Analyzed (count + " Industries")
- Avg Budget (calculate from projects or show "₹50K avg")
- System Status ("Active ✓" in green)
Each card: bg-gray-800 rounded-xl p-6 with colored icon, big number, subtitle

SECTION 2 - If 'project' variable exists (after form submit):
Three column grid:
  COL 1 - "Project Details" card: show startup_name, industry, business_model, target_market, budget
  COL 2 - "Market Analysis" card:
    - TAM / SAM / SOM as three colored stat rows
    - Line chart canvas id="marketTrendChart" showing 2021-2026 trend
  COL 3 - "Competitor Landscape" card:
    - For each competitor: name, market_share bar (CSS width %), revenue, growth badge
    - Doughnut chart canvas id="competitorChart"

SECTION 3 - Milestone roadmap (4 steps):
- M1: Data Collection (green - active), M2: Risk Assessment (gray), M3: AI Advisor (gray), M4: Deployment (gray)

If no project variable: show "No project submitted yet" with link to /submit

Data for charts comes from: {{ market_data | tojson }} and {{ competitors | tojson }} passed to JS
```

---

### FILE 7: `static/js/dashboard.js`
**Spec for Claude Code:**
```
Create static/js/dashboard.js that:
- Checks if window.marketData and window.competitors exist (set by inline script in dashboard.html)
- If marketTrendChart canvas exists:
  Creates Chart.js line chart with:
  - Labels: years from marketData.market_trend
  - Dataset: values from marketData.market_trend, color blue (#3B82F6), fill gradient
  - Options: dark theme (no grid lines, white labels), tension 0.4
- If competitorChart canvas exists:
  Creates Chart.js doughnut chart with:
  - Labels: competitor names
  - Data: market_share values
  - Colors: blue, purple, pink
  - Options: dark theme, legend bottom
- Chart defaults: Chart.defaults.color = '#9CA3AF', Chart.defaults.font.family = 'Inter'
```

---

## ✅ Phase 5 — Run & Test

### Step 11: First Run
```bash
# In VS Code terminal, venv activated:
python app.py
```

Expected output:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

Open Chrome: **http://127.0.0.1:5000**

---

### Step 12: Test With Sample Data
Go to `http://127.0.0.1:5000/submit` and enter:

| Field | Value |
|-------|-------|
| Startup Name | EduTech Andhra |
| Industry | Education |
| Business Model | B2C |
| Target Market | College students in Andhra Pradesh |
| Budget | 50000 |
| Description | A platform helping engineering students get industry-ready skills through project-based learning and mentorship. |

Click **"Analyze My Project →"**

Expected: Redirect to `/dashboard/1` showing:
- TAM: ~$10.0B, SAM: ~$3.5B, SOM: ~$1.2M  
- Market trend line chart (2021–2026)
- Competitor A/B/C doughnut chart

---

### Step 13: Verify PostgreSQL
Open pgAdmin → `ml_project` → Query Tool:
```sql
SELECT id, startup_name, industry, budget, created_at
FROM projects
ORDER BY created_at DESC;
```
You should see your submitted project row. ✅

---

## 🔴 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `psycopg2.OperationalError: password auth failed` | Wrong password in `.env` | Open `.env`, fix `DB_PASSWORD` |
| `ModuleNotFoundError: No module named 'flask'` | venv not activated | Run `venv\Scripts\activate` first |
| `could not connect to server` | PostgreSQL not running | Open Services → start `postgresql-x64-16` |
| `TemplateNotFound: dashboard.html` | Wrong folder structure | Ensure `templates/` is at root level |
| Port 5000 already in use | Another Flask app running | Change port: `app.run(debug=True, port=5001)` |
| Chart not rendering | JS error in console | Check `{{ market_data \| tojson }}` in HTML source |

---

## 📋 VS Code Run Commands — Full Reference

```bash
# 1. Open project
cd C:\Projects\ML_Market_Intelligence_Project

# 2. Activate venv (every new terminal session)
venv\Scripts\activate

# 3. Install deps (first time only)
pip install -r requirements.txt

# 4. Run app
python app.py

# 5. Stop app
Ctrl + C

# 6. Deactivate venv
deactivate
```

---

## 🎨 What Makes This UI Unique

- **Dark glassmorphism theme** — `bg-gray-900` base with `bg-gray-800` cards
- **Gradient brand accent** — blue-to-purple on logo, CTA buttons, active badges
- **Real-time Chart.js** — Line chart for market trend + doughnut for competitor share
- **Milestone progress tracker** — Visual roadmap showing M1→M4 pipeline
- **Indian context** — Budget in ₹, target markets named Indian cities/regions
- **Responsive grid** — 4-col stats on desktop, stacks on mobile (Tailwind responsive)

---

## 🗺️ What Comes in Later Milestones

| Milestone | Feature | New Packages |
|-----------|---------|--------------|
| **M2** | Risk scoring (1–100) + SWOT analysis table | `scikit-learn` |
| **M3** | AI recommendations via Gemini API + LangGraph agents | `google-generativeai`, `langgraph` |
| **M4** | Full dashboard polish + deployment to Render | `gunicorn` |

> M2/M3/M4 routes already exist as placeholders via `placeholder.html` — clicking them shows "Coming Soon".

---

## 📁 Source References

| Resource | URL | Used For |
|----------|-----|----------|
| Mentor ZIP | [Drive Link](https://drive.google.com/file/d/1BiD4phzET-2gHsfGrtWwJd5Xhw498GUm/view) | Base project structure |
| Flask docs | https://flask.palletsprojects.com/en/3.0.x/ | Route + template patterns |
| Chart.js docs | https://www.chartjs.org/docs/latest/ | Line + Doughnut charts |
| Tailwind CDN | https://cdn.tailwindcss.com | UI styling |
| psycopg2 docs | https://www.psycopg.org/docs/ | PostgreSQL connection |
| python-dotenv | https://pypi.org/project/python-dotenv/ | .env config |
| pgAdmin guide | https://www.pgadmin.org/docs/ | DB management |
| Flask+Chart.js ref | https://github.com/fr33dz/flask-chartjs | Chart integration pattern |

---

## ✅ Milestone 1 Completion Checklist

```
☐ Python 3.10+ installed, added to PATH
☐ VS Code + Python extension installed
☐ PostgreSQL installed, pgAdmin working
☐ ml_project database created
☐ projects table created (7 columns + id + timestamp)
☐ ZIP extracted and opened in VS Code
☐ venv created and activated
☐ pip install -r requirements.txt successful
☐ .env file created with correct DB_PASSWORD
☐ python app.py runs without errors
☐ http://127.0.0.1:5000 loads dashboard
☐ /submit form visible with all 6 fields
☐ One project submitted successfully
☐ Redirected to /dashboard/1 with charts visible
☐ pgAdmin SELECT * FROM projects shows the row
☐ Market trend line chart renders
☐ Competitor doughnut chart renders
```

**When all 16 boxes are checked → Milestone 1 complete. Ready for Milestone 2.**

---

*Plan generated for: VLITS B.Tech CSE (AI/ML) — ML Market Intelligence capstone project*
