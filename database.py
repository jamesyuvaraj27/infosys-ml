"""Database access layer supporting PostgreSQL (local or Neon) with SQLite fallback."""
import os
import sqlite3
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml_project.db")
_USE_SQLITE = False


def _pg_connect(connect_timeout=None):
    """Open a PostgreSQL connection.

    If DATABASE_URL is set (e.g. a Neon connection string), use it directly.
    Otherwise fall back to the discrete DB_HOST/DB_NAME/... vars (local Postgres).
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if connect_timeout:
            return psycopg2.connect(database_url, connect_timeout=connect_timeout)
        return psycopg2.connect(database_url)

    kwargs = dict(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "ml_project"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        port=os.getenv("DB_PORT", "5432"),
    )
    if connect_timeout:
        kwargs["connect_timeout"] = connect_timeout
    return psycopg2.connect(**kwargs)


def _check_db_engine():
    """Detect whether PostgreSQL is reachable or if SQLite should be used."""
    global _USE_SQLITE
    db_engine_override = os.getenv("DB_ENGINE", "").lower()
    if db_engine_override == "sqlite":
        _USE_SQLITE = True
        return

    try:
        # Neon's free-tier compute can be suspended and take a few seconds to
        # wake up on the first connection, so give it more room than a quick local check.
        conn = _pg_connect(connect_timeout=10)
        conn.close()
        _USE_SQLITE = False
    except Exception as exc:
        print(f"[WARN] PostgreSQL unreachable, falling back to SQLite: {exc}")
        _USE_SQLITE = True


def get_connection():
    """Return a database connection (PostgreSQL if available, SQLite otherwise)."""
    global _USE_SQLITE
    if _USE_SQLITE:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    return _pg_connect()


def init_db():
    """Create the projects table if it doesn't exist yet."""
    _check_db_engine()
    if _USE_SQLITE:
        print(f"[INFO] Using SQLite database at: {SQLITE_DB_PATH}")
        conn = get_connection()
        try:
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
        finally:
            conn.close()
    else:
        db_source = "Neon" if os.getenv("DATABASE_URL") else "local PostgreSQL"
        print(f"[INFO] Using PostgreSQL database ({db_source})")
        conn = get_connection()
        try:
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


def get_all_projects():
    """Return all projects, newest first, as a list of dicts."""
    conn = get_connection()
    try:
        if _USE_SQLITE:
            cur = conn.cursor()
            cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
                return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_project_count():
    """Return the total number of submitted projects."""
    conn = get_connection()
    try:
        if _USE_SQLITE:
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
        if _USE_SQLITE:
            cur = conn.cursor()
            cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
                row = cur.fetchone()
                return dict(row) if row else None
    finally:
        conn.close()


def insert_project(data):
    """Insert a new project row and return its new id."""
    conn = get_connection()
    try:
        budget_val = float(data.get("budget") or 0)
        if _USE_SQLITE:
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

