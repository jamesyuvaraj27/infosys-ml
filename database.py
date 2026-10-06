"""Database access layer supporting PostgreSQL (local or Neon) with SQLite fallback."""
import os
import json
import decimal
import datetime
import sqlite3
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml_project.db")
_USE_SQLITE = False


def _pg_connect(connect_timeout=3):
    """Open a PostgreSQL connection.

    If DATABASE_URL is set (e.g. a Neon connection string), use it directly.
    Otherwise fall back to the discrete DB_HOST/DB_NAME/... vars (local Postgres).
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        timeout_val = connect_timeout or 3
        # Handle connection timeout for libpq
        return psycopg2.connect(database_url, connect_timeout=timeout_val)

    kwargs = dict(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "ml_project"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        port=os.getenv("DB_PORT", "5432"),
        connect_timeout=connect_timeout or 3,
    )
    return psycopg2.connect(**kwargs)


def _check_db_engine():
    """Detect whether PostgreSQL is reachable or if SQLite should be used."""
    global _USE_SQLITE
    db_engine_override = os.getenv("DB_ENGINE", "").lower()
    if db_engine_override == "sqlite":
        _USE_SQLITE = True
        return

    try:
        conn = _pg_connect(connect_timeout=2)
        conn.close()
        _USE_SQLITE = False
    except Exception as exc:
        print(f"[WARN] PostgreSQL unreachable, falling back to SQLite: {exc}")
        _USE_SQLITE = True


def get_connection():
    """Return a database connection (PostgreSQL if available, SQLite otherwise)."""
    global _USE_SQLITE
    db_engine_override = os.getenv("DB_ENGINE", "").lower()
    if db_engine_override == "sqlite" or _USE_SQLITE:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    try:
        return _pg_connect(connect_timeout=2)
    except Exception as exc:
        print(f"[WARN] PostgreSQL connection failed, falling back to SQLite: {exc}")
        _USE_SQLITE = True
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    """Create the projects table if it doesn't exist yet."""
    _check_db_engine()
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            print(f"[INFO] Using SQLite database at: {SQLITE_DB_PATH}")
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS projects (
                        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                        startup_name        TEXT NOT NULL,
                        industry            TEXT NOT NULL,
                        business_model      TEXT NOT NULL,
                        target_market       TEXT,
                        budget              REAL DEFAULT 0,
                        project_description TEXT,
                        created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        else:
            db_source = "Neon" if os.getenv("DATABASE_URL") else "local PostgreSQL"
            print(f"[INFO] Using PostgreSQL database ({db_source})")
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS projects (
                        id                  SERIAL PRIMARY KEY,
                        startup_name        VARCHAR(150) NOT NULL,
                        industry            VARCHAR(100) NOT NULL,
                        business_model      VARCHAR(100) NOT NULL,
                        target_market       VARCHAR(150),
                        budget              NUMERIC(15, 2) DEFAULT 0,
                        project_description TEXT,
                        created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            conn.commit()
    finally:
        conn.close()


def _clean_project_row(row):
    """Normalize a database row into JSON-serializable primitives."""
    if not row:
        return None
    d = dict(row)
    if "budget" in d and d["budget"] is not None:
        try:
            d["budget"] = float(d["budget"])
        except Exception:
            d["budget"] = 0.0
    if "created_at" in d and d["created_at"] is not None:
        if hasattr(d["created_at"], "strftime"):
            d["created_at"] = d["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            d["created_at"] = str(d["created_at"])
    return d


def get_all_projects():
    """Return all projects, newest first, as a list of dicts."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
            rows = cur.fetchall()
            return [_clean_project_row(row) for row in rows]
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
                return [_clean_project_row(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_project_count():
    """Return the total number of submitted projects."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM projects")
            row = cur.fetchone()
            return row[0] if row else 0
        else:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM projects")
                row = cur.fetchone()
                return row[0] if row else 0
    finally:
        conn.close()


def get_project_by_id(project_id):
    """Return a single project as a dict, or None if it doesn't exist."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cur.fetchone()
            return _clean_project_row(row)
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
                row = cur.fetchone()
                return _clean_project_row(row)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# recommendations & mitigations tables
# ---------------------------------------------------------------------------

def init_milestone3_tables():
    """Create recommendations and mitigations tables if they don't exist."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS recommendations (
                        id         INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER,
                        title      TEXT,
                        priority   VARCHAR(50),
                        description TEXT
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS mitigations (
                        id         INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER,
                        risk_name  TEXT,
                        impact     VARCHAR(50),
                        mitigation TEXT
                    )
                    """
                )
        else:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS recommendations (
                        id          SERIAL PRIMARY KEY,
                        project_id  INT,
                        title       VARCHAR(255),
                        priority    VARCHAR(50),
                        description TEXT
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS mitigations (
                        id          SERIAL PRIMARY KEY,
                        project_id  INT,
                        risk_name   VARCHAR(255),
                        impact      VARCHAR(50),
                        mitigation  TEXT
                    )
                    """
                )
            conn.commit()
    finally:
        conn.close()


def save_recommendations(project_id: int, recommendations: list):
    """Delete existing recommendations for a project and insert fresh ones."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            with conn:
                conn.execute(
                    "DELETE FROM recommendations WHERE project_id = ?", (project_id,)
                )
                for rec in recommendations:
                    conn.execute(
                        """
                        INSERT INTO recommendations (project_id, title, priority, description)
                        VALUES (?, ?, ?, ?)
                        """,
                        (project_id, rec["title"], rec["priority"], rec["description"]),
                    )
        else:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM recommendations WHERE project_id = %s", (project_id,)
                )
                for rec in recommendations:
                    cur.execute(
                        """
                        INSERT INTO recommendations (project_id, title, priority, description)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (project_id, rec["title"], rec["priority"], rec["description"]),
                    )
            conn.commit()
    finally:
        conn.close()


def get_recommendations(project_id: int) -> list:
    """Return all recommendation rows for a project as a list of dicts."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM recommendations WHERE project_id = ?", (project_id,)
            )
            return [dict(row) for row in cur.fetchall()]
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM recommendations WHERE project_id = %s", (project_id,)
                )
                return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def save_mitigations(project_id: int, mitigations: list):
    """Delete existing mitigations for a project and insert fresh ones."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            with conn:
                conn.execute(
                    "DELETE FROM mitigations WHERE project_id = ?", (project_id,)
                )
                for mit in mitigations:
                    conn.execute(
                        """
                        INSERT INTO mitigations (project_id, risk_name, impact, mitigation)
                        VALUES (?, ?, ?, ?)
                        """,
                        (project_id, mit["risk"], mit["impact"], mit["mitigation"]),
                    )
        else:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM mitigations WHERE project_id = %s", (project_id,)
                )
                for mit in mitigations:
                    cur.execute(
                        """
                        INSERT INTO mitigations (project_id, risk_name, impact, mitigation)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (project_id, mit["risk"], mit["impact"], mit["mitigation"]),
                    )
            conn.commit()
    finally:
        conn.close()


def get_mitigations(project_id: int) -> list:
    """Return all mitigation rows for a project as a list of dicts."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM mitigations WHERE project_id = ?", (project_id,)
            )
            return [dict(row) for row in cur.fetchall()]
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM mitigations WHERE project_id = %s", (project_id,)
                )
                return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Milestone 4 – Assessment Reports Table & Operations
# ---------------------------------------------------------------------------

def init_milestone4_tables():
    """Create assessment_reports table if it doesn't exist yet."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS assessment_reports (
                        id             INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id     INTEGER,
                        report_title   TEXT NOT NULL,
                        report_content TEXT NOT NULL,
                        generated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by     VARCHAR(100) DEFAULT 'AI Risk Intelligence Engine'
                    )
                    """
                )
        else:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS assessment_reports (
                        id             SERIAL PRIMARY KEY,
                        project_id     INT,
                        report_title   VARCHAR(255) NOT NULL,
                        report_content TEXT NOT NULL,
                        generated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by     VARCHAR(100) DEFAULT 'AI Risk Intelligence Engine'
                    )
                    """
                )
            conn.commit()
    finally:
        conn.close()


def _safe_json_default(obj):
    """Serialize Decimals, datetimes, and other non-standard objects to JSON primitives."""
    if isinstance(obj, (decimal.Decimal, float)):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    return str(obj)


def save_assessment_report(project_id: int, report_title: str, report_content: dict | str, created_by: str = "AI Risk Intelligence Engine") -> int:
    """Save a comprehensive assessment report and return the new report_id."""
    if isinstance(report_content, (dict, list)):
        content_str = json.dumps(report_content, default=_safe_json_default)
    else:
        content_str = str(report_content)

    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO assessment_reports (project_id, report_title, report_content, created_by)
                    VALUES (?, ?, ?, ?)
                    """,
                    (project_id, report_title, content_str, created_by),
                )
                return cur.lastrowid
        else:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO assessment_reports (project_id, report_title, report_content, created_by)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (project_id, report_title, content_str, created_by),
                )
                new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    finally:
        conn.close()


def _parse_report_row(row: dict | sqlite3.Row | None) -> dict | None:
    """Helper to parse report_content JSON string back to dict."""
    if not row:
        return None
    d = dict(row)
    if "budget" in d and d["budget"] is not None:
        try:
            d["budget"] = float(d["budget"])
        except Exception:
            d["budget"] = 0.0
    if "generated_at" in d and d["generated_at"] is not None:
        if hasattr(d["generated_at"], "strftime"):
            d["generated_at"] = d["generated_at"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            d["generated_at"] = str(d["generated_at"])
    if "report_content" in d and isinstance(d["report_content"], str):
        try:
            d["content"] = json.loads(d["report_content"])
        except Exception:
            d["content"] = {}
    return d


def get_assessment_report_by_id(report_id: int) -> dict | None:
    """Return a single assessment report by its report_id."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute("SELECT * FROM assessment_reports WHERE id = ?", (report_id,))
            row = cur.fetchone()
            return _parse_report_row(row)
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM assessment_reports WHERE id = %s", (report_id,))
                row = cur.fetchone()
                return _parse_report_row(row)
    finally:
        conn.close()


def get_assessment_reports_by_project(project_id: int) -> list:
    """Return all assessment reports for a given project, newest first."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM assessment_reports WHERE project_id = ? ORDER BY generated_at DESC, id DESC",
                (project_id,),
            )
            rows = cur.fetchall()
            return [_parse_report_row(row) for row in rows]
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM assessment_reports WHERE project_id = %s ORDER BY generated_at DESC, id DESC",
                    (project_id,),
                )
                rows = cur.fetchall()
                return [_parse_report_row(row) for row in rows]
    finally:
        conn.close()


def get_latest_report_for_project(project_id: int) -> dict | None:
    """Return the most recently generated report for a project, or None."""
    reports = get_assessment_reports_by_project(project_id)
    return reports[0] if reports else None


def get_all_reports() -> list:
    """Return all assessment reports across all projects with project name joined."""
    conn = get_connection()
    try:
        query = """
            SELECT r.*, p.startup_name, p.industry, p.budget, p.business_model
            FROM assessment_reports r
            LEFT JOIN projects p ON r.project_id = p.id
            ORDER BY r.generated_at DESC, r.id DESC
        """
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            return [_parse_report_row(row) for row in rows]
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [_parse_report_row(row) for row in rows]
    finally:
        conn.close()


def insert_project(data):
    """Insert a new project row and return its new id."""
    conn = get_connection()
    try:
        budget_val = float(data.get("budget") or 0)
        if isinstance(conn, sqlite3.Connection):
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO projects
                        (startup_name, industry, business_model, target_market,
                         budget, project_description)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["startup_name"],
                        data["industry"],
                        data["business_model"],
                        data["target_market"],
                        budget_val,
                        data["project_description"],
                    ),
                )
                return cur.lastrowid
        else:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO projects
                        (startup_name, industry, business_model, target_market,
                         budget, project_description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        data["startup_name"],
                        data["industry"],
                        data["business_model"],
                        data["target_market"],
                        budget_val,
                        data["project_description"],
                    ),
                )
                new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    finally:
        conn.close()


def delete_project(project_id: int) -> bool:
    """Permanently delete a project and all associated intelligence data from the database."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            with conn:
                conn.execute("DELETE FROM recommendations WHERE project_id = ?", (project_id,))
                conn.execute("DELETE FROM mitigations WHERE project_id = ?", (project_id,))
                conn.execute("DELETE FROM assessment_reports WHERE project_id = ?", (project_id,))
                cur = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                return cur.rowcount > 0
        else:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM recommendations WHERE project_id = %s", (project_id,))
                cur.execute("DELETE FROM mitigations WHERE project_id = %s", (project_id,))
                cur.execute("DELETE FROM assessment_reports WHERE project_id = %s", (project_id,))
                cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                deleted = cur.rowcount > 0
            conn.commit()
            return deleted
    finally:
        conn.close()


def delete_assessment_report(report_id: int) -> bool:
    """Permanently delete a single assessment report by ID."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            with conn:
                cur = conn.execute("DELETE FROM assessment_reports WHERE id = ?", (report_id,))
                return cur.rowcount > 0
        else:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM assessment_reports WHERE id = %s", (report_id,))
                deleted = cur.rowcount > 0
            conn.commit()
            return deleted
    finally:
        conn.close()


