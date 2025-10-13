# Fake dataset for demo & testing
DATA = [
    {"country": "AUS", "vaccine": "MMR", "year": 2024, "coverage": 94.2},
    {"country": "NZL", "vaccine": "MMR", "year": 2024, "coverage": 91.8},
    {"country": "GBR", "vaccine": "MMR", "year": 2024, "coverage": 95.5},
    {"country": "AUS", "vaccine": "DTP", "year": 2023, "coverage": 92.0},
    {"country": "GBR", "vaccine": "DTP", "year": 2023, "coverage": 89.5},
]

# ---------- Level 2 ----------
def get_filtered_data(country=None, vaccine=None, year=None, sort="coverage_desc"):
    """Return filtered & sorted vaccine data."""
    rows = [
        r for r in DATA
        if (not country or r["country"] == country)
        and (not vaccine or r["vaccine"] == vaccine)
        and (not year or r["year"] == year)
    ]
    reverse = sort.endswith("desc")
    return sorted(rows, key=lambda r: r["coverage"], reverse=reverse)


# ---------- Level 3 ----------
def compare_country(country, year):
    """Compare local coverage vs global average."""
    local_rows = [r for r in DATA if r["country"] == country and r["year"] == year]
    if not local_rows:
        return {"error": f"No data for {country} in {year}"}

    global_avg = sum(r["coverage"] for r in DATA) / len(DATA)
    return {
        "country": country,
        "year": year,
        "local": local_rows[0]["coverage"],
        "global_avg": round(global_avg, 2),
    }


def get_trends(vaccine, countries):
    """Return trends for multiple countries (chart-ready)."""
    points = [
        r for r in DATA
        if r["vaccine"] == vaccine and r["country"] in countries
    ]
    return {
        "vaccine": vaccine,
        "countries": countries,
        "points": points,
        "count": len(points)
    }
