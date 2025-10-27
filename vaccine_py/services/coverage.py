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
    "USA": "United States",
    "CAN": "Canada",
    "JPN": "Japan",
    "DEU": "Germany",
    "FRA": "France",
    "ITA": "Italy",
    "ESP": "Spain",
}
NAME_TO_ISO: Dict[str, str] = {v.upper(): k for k, v in ISO_TO_NAME.items()}


def country_name(code: str) -> str:
    return ISO_TO_NAME.get((code or "").upper(), code or "")


def resolve_country(query: Optional[str]) -> Optional[str]:
    if not query:
        return None
    q = query.strip()
    if not q:
        return None

    up = q.upper()
    if up in ISO_TO_NAME:
        return up
    if up in NAME_TO_ISO:
        return NAME_TO_ISO[up]
    if len(up) == 3 and up.isalpha():
        return up
    return None


def _norm_country(x: Optional[str]) -> Optional[str]:
    return resolve_country(x)


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
        raise FileNotFoundError(f"SQL file not found: {SQL_PATH}")

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
    """
    Сравнение локального показателя со средним по миру (для того же вакцины/года).
    """
    c = _norm_country(country)
    y = _norm_year(year)
    if not y:
        return {"error": "Invalid year parameter"}
    if not c:
        return {"error": f"Unknown country: {country}"}

    local_sql = """
        SELECT country, vaccine, year, coverage
        FROM coverage
        WHERE country = ? AND year = ?
        ORDER BY vaccine
        LIMIT 1;
    """
    local_rows = _select(local_sql, (c, y))
    if not local_rows:
        return {"error": f"No data for {country_name(c)} ({c}) in {y}"}

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
        "country": c,       
        "country_code": c,
        "country_name": country_name(c),
        "year": y,
        "vaccine": vac,
        "local": round(float(local["coverage"]), 1),
        "global_avg": round(float(avg), 1),
    }


def get_trends(
    vaccine: Optional[str],
    countries: Optional[List[str]],
    latest_only: bool = True,
) -> Dict[str, Any]:
    v = _norm_vaccine(vaccine)
    raw_list = countries or []
    cs = [_norm_country(x) for x in raw_list if _norm_country(x)]

    if raw_list and not cs:
        return {"vaccine": v, "countries": [], "points": [], "count": 0}

    where = ["1=1"]
    params: List[Any] = []
    if v:
        where.append("vaccine = ?"); params.append(v)
    if cs:
        placeholders = ",".join("?" for _ in cs)
        where.append(f"country IN ({placeholders})"); params.extend(cs)

    if latest_only:
        inner_where = " AND ".join(where)
        outer_where = (
            inner_where
            .replace("country", "t.country")
            .replace("vaccine", "t.vaccine")
            .replace("year", "t.year")
        )
        sql = f"""
            SELECT t.country, t.vaccine, t.year, t.coverage
            FROM coverage t
            JOIN (
                SELECT country, MAX(year) AS max_year
                FROM coverage
                WHERE {inner_where}
                GROUP BY country
            ) m ON m.country = t.country AND m.max_year = t.year
            WHERE {outer_where}
            ORDER BY t.country;
        """
        points = _select(sql, tuple(params * 2))
    else:
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
