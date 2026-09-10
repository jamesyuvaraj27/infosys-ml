# Milestone 2 — Implementation Plan
## Risk Assessment, SWOT Analysis & Feasibility Assessment

Builds directly on Milestone 1 (Flask + PostgreSQL/SQLite project database).
Milestone 2 ships as a **separate Streamlit app** in the same project folder —
it reads the projects you already submitted in Milestone 1 instead of asking
you to re-enter project data.

```
Milestone 1 (Flask, app.py)          Milestone 2 (Streamlit, app_milestone2.py)
  Project form -> projects table  ->   pick a project -> risk inputs
                                        -> risk_engine.py   -> risk score, status,
                                                                success probability
                                        -> swot_analysis.py -> Strengths / Weaknesses /
                                                                Opportunities / Threats
                                        -> feasibility.py   -> feasibility %, verdict
```

## Why a separate Streamlit app (not bolted onto Flask)

- Milestone 2's own class material is written in Streamlit (`st.*`), and a
  student build should follow the taught stack.
- Streamlit's `st.selectbox` / `st.slider` / `st.metric` widgets are a much
  faster way to build an interactive "what-if" risk dashboard than hand-rolled
  HTML forms — no new templates or JS needed.
- Both apps share `database.py`, so there's one source of truth for project
  data (same Neon/local Postgres, same SQLite fallback). Milestone 1 stays
  untouched.

## Files added

| File | Purpose |
|---|---|
| `risk_engine.py` | `calculate_risk()`, `get_risk_status()`, `calculate_success_probability()` — weighted 0–100 risk score from 5 categorical inputs |
| `swot_analysis.py` | `generate_swot()` — rule-based Strengths/Weaknesses/Opportunities/Threats from the same 5 inputs |
| `feasibility.py` | `calculate_feasibility()` — average of 4 slider scores (0–100) |
| `app_milestone2.py` | Streamlit UI: pick a Milestone‑1 project → set risk inputs → see risk score, success probability, SWOT, feasibility, final verdict |

`requirements.txt` gained one line: `streamlit==1.63.0` (confirmed to have
Python 3.14 wheels, same compatibility check we did for psycopg2-binary).

## Data flow (matches the class's own "Complete Milestone 2 Flow" diagram)

1. **Project Data** — chosen from the `projects` table (Milestone 1 submissions).
2. **Risk Assessment** — you set Market Competition / Team Expertise / Resource
   Availability / Innovation Level / Market Research; `risk_engine.py` turns
   that into a 0–100 score and a HIGH/MEDIUM/LOW label.
3. **SWOT Analysis** — the same 5 inputs feed `swot_analysis.py`, which is
   pure if/else logic (no ML) — deterministic and easy to explain in a viva.
4. **Feasibility Assessment** — 4 independent sliders (Market Opportunity,
   Team Capability, Competitive Advantage, Resources) averaged into a %.
5. **Final Recommendation** — a verdict (Highly Feasible / Feasible /
   Moderately Feasible / Not Feasible) using the same 80/60/40 thresholds the
   class teaches.

## Worked example used to validate this build

Project: **TestAI Diagnostics** (Healthcare, B2B, "Hospitals and Clinics",
$150,000 budget) — an existing row already in your Milestone 1 database from
earlier testing.

Inputs chosen to reflect that story honestly (crowded AI-diagnostics market,
capable but first-time-in-healthcare team, thin budget for a regulated
product, genuinely novel tech, no completed clinical validation yet):

| Input | Value |
|---|---|
| Market Competition | High |
| Team Expertise | Medium |
| Resource Availability | Limited |
| Innovation Level | High |
| Market Research | Limited |

**Computed output** (verified by running the actual functions):

- Risk Score: **75/100 → HIGH RISK**
- Success Probability: **25%**
- Strengths: High innovation potential
- Weaknesses: Limited market research; Limited resources
- Opportunities: Potential for market expansion; Partnership opportunities
- Threats: Strong competitors; Rapid technology changes; Market uncertainty
- Feasibility (Market Opportunity 78, Team Capability 55, Competitive
  Advantage 42, Resources 30): **51% → Moderately Feasible**

## How to run it

```powershell
cd F:\infosys
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app_milestone2.py
```

Opens automatically at `http://localhost:8501`. Milestone 1's Flask app
(`python app.py`, port 5000) can keep running at the same time — they're two
separate processes sharing one database.

## What's deliberately out of scope (matches the class, not gold-plating)

- No persistence of risk/SWOT/feasibility results back into the database —
  the class teaches this as a live, session-only assessment tool. Add a
  `risk_assessments` table later if you want history.
- No AI/ML behind the SWOT or risk logic — it's the same deterministic
  if/else scoring the class specifies, which is also what makes it trivial to
  explain and defend in a viva.
