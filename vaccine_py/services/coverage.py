from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

def _detect_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "database.sql").exists() or (p / ".git").exists():
            return p
    return here.parents[2]

ROOT: Path = _detect_root()
DB_PATH: Path = ROOT / "database.db"
SQL_PATH: Path = ROOT / "database.sql"

ISO_TO_NAME: Dict[str, str] = {
    "AUS": "Australia",
    "NZL": "New Zealand",
    "GBR": "United Kingdom",
}

def country_name(code: str) -> str:
    return ISO_TO_NAME.get((code or "").upper(), code or "")

def _norm_country(x: Optional[str]) -> Optional[str]:
    return (x or "").strip().upper() or None

def _norm_vaccine(x: Optional[str]) -> Optional[str]:
    return (x or "").strip().upper() or None

def _norm_year(x: Any) -> Optional[int]:
    try:
        return int(x)
    except (TypeError, ValueError):
        return None

# ----------------------- db helpers -----------------------
def get_connection() -> sqlite3.Connection:
    """SQLite connection with row_factory -> dict-like rows."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db() -> None:
    """
    Инициализирует БД из database.sql, если:
    - файла БД нет, или
    - таблица coverage отсутствует.
    """
    needs_init = True
    if DB_PATH.exists():
        try:
            with get_connection() as c:
                c.execute("SELECT 1 FROM coverage LIMIT 1;")
            needs_init = False
        except sqlite3.Error:
            needs_init = True

    if not needs_init:
        return

    if not SQL_PATH.exists():
        raise FileNotFoundError(
            f"SQL file not found: {SQL_PATH}. Создай database.sql в корне проекта."
        )

    with sqlite3.connect(str(DB_PATH)) as conn, open(SQL_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

def _select(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

# ----------------------- Level 2 -----------------------
def get_filtered_data(
    country: Optional[str] = None,
    vaccine: Optional[str] = None,
    year: Optional[int] = None,
    sort: str = "coverage_desc",
) -> List[Dict[str, Any]]:
    c = _norm_country(country)
    v = _norm_vaccine(vaccine)
    y = _norm_year(year)

    where = ["1=1"]
    params: List[Any] = []
    if c:
        where.append("country = ?"); params.append(c)
    if v:
        where.append("vaccine = ?"); params.append(v)
    if y is not None:
        where.append("year = ?"); params.append(y)

    order_sql = {
        "coverage_desc": "coverage DESC",
        "coverage_asc": "coverage ASC",
        "year_desc": "year DESC",
        "year_asc": "year ASC",
        "country_desc": "country DESC",
        "country_asc": "country ASC",
    }.get((sort or "").lower(), "coverage DESC")

    sql = f"""
        SELECT country, vaccine, year, coverage
        FROM coverage
        WHERE {' AND '.join(where)}
        ORDER BY {order_sql};
    """
    rows = _select(sql, tuple(params))
    for r in rows:
        r["country_name"] = country_name(r["country"])
    return rows

# ----------------------- Level 3 -----------------------
def compare_country(country: str, year: Any) -> Dict[str, Any]:
    c = _norm_country(country)
    y = _norm_year(year)
    if not y:
        return {"error": "Invalid year parameter"}

    local_sql = """
        SELECT country, vaccine, year, coverage
        FROM coverage
        WHERE country = ? AND year = ?
        ORDER BY vaccine
        LIMIT 1;
    """
    local_rows = _select(local_sql, (c, y))
    if not local_rows:
        return {"error": f"No data for {c or country} in {y}"}

    local = local_rows[0]
    vac = local["vaccine"]

    avg_sql = """
        SELECT AVG(coverage) AS avg_cov
        FROM coverage
        WHERE vaccine = ? AND year = ?;
    """
    avg_row = _select(avg_sql, (vac, y))[0]
    avg = avg_row.get("avg_cov")
    if avg is None:
        return {"error": f"No global data for vaccine {vac} in {y}"}

    return {
        "country_code": c,
        "country_name": country_name(c),
        "year": y,
        "vaccine": vac,
        "local": round(float(local["coverage"]), 1),
        "global_avg": round(float(avg), 1),
    }

def get_trends(vaccine: Optional[str], countries: Optional[List[str]]) -> Dict[str, Any]:
    v = _norm_vaccine(vaccine)
    cs = [_norm_country(x) for x in (countries or []) if _norm_country(x)]

    where = ["1=1"]
    params: List[Any] = []
    if v:
        where.append("vaccine = ?"); params.append(v)
    if cs:
        placeholders = ",".join("?" for _ in cs)
        where.append(f"country IN ({placeholders})"); params.extend(cs)

    sql = f"""
        SELECT country, vaccine, year, coverage
        FROM coverage
        WHERE {' AND '.join(where)}
        ORDER BY country, year;
    """
    points = _select(sql, tuple(params))
    for p in points:
        p["country_name"] = country_name(p["country"])

    return {
        "vaccine": v,
        "countries": cs,
        "points": points,
        "count": len(points),
    }
