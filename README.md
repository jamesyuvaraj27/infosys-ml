# ML Market Intelligence — Milestone 1

Form → Flask → PostgreSQL → live dashboard with Chart.js.

## Stack
Python · Flask · PostgreSQL (psycopg2) · Jinja2 · Tailwind CSS (CDN) · Chart.js (CDN)

## Project structure
```
app.py                 Flask routes
database.py             PostgreSQL access (psycopg2)
market_analysis.py      TAM/SAM/SOM + competitor calc (placeholder logic)
requirements.txt
.env.example             copy to .env and fill in your DB password
templates/               base.html, dashboard.html, project.html, placeholder.html
static/css/style.css
static/js/dashboard.js  Chart.js init
```

## One-time setup (Windows)

1. Install PostgreSQL 16 (with pgAdmin) if you haven't:
   https://www.postgresql.org/download/windows/

2. In pgAdmin, create a database named `ml_project`.
   (The `projects` table is created automatically the first time the app runs —
   no manual SQL needed.)

3. Open this folder in VS Code, then in its terminal:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your real PostgreSQL password:
   ```bash
   copy .env.example .env
   ```
   ```env
   DB_HOST=localhost
   DB_NAME=ml_project
   DB_USER=postgres
   DB_PASSWORD=your_actual_password
   DB_PORT=5432
   ```

## Run it

```bash
venv\Scripts\activate
python app.py
```

Open http://127.0.0.1:5000 — submit a project at `/submit`, get redirected to
`/dashboard/<id>` with TAM/SAM/SOM, a market-trend line chart and a
competitor doughnut chart.

## Notes
- `market_analysis.py` uses simplified placeholder formulas (budget * 200 for
  TAM, etc.) — not real market research. Swap in real logic for Milestone 3.
- M2 (Risk Assessment) and M3 (AI Advisor) nav links currently render a
  "Coming Soon" placeholder page.
