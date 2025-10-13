from typing import List, Dict

_FAKE = [
  {"country":"AUS","vaccine":"MMR","year":2022,"coverage_pct":93.1},
  {"country":"AUS","vaccine":"MMR","year":2023,"coverage_pct":93.7},
  {"country":"NZL","vaccine":"MMR","year":2023,"coverage_pct":95.2},
  {"country":"GBR","vaccine":"MMR","year":2023,"coverage_pct":90.4},
]

def query_filter_sort(country: str|None, year_from: int|None, year_to: int|None,
                      vaccine: str|None, sort: str|None) -> List[Dict]:
    rows = [r for r in _FAKE if
            (country is None or r["country"]==country) and
            (year_from is None or r["year"]>=year_from) and
            (year_to is None or r["year"]<=year_to) and
            (vaccine is None or r["vaccine"]==vaccine)]
    if sort == "coverage_asc":
        rows.sort(key=lambda x: (x["coverage_pct"], x["year"]))
    elif sort == "coverage_desc":
        rows.sort(key=lambda x: (x["coverage_pct"], x["year"]), reverse=True)
    else:  # newest by default
        rows.sort(key=lambda x: (x["year"], x["country"]), reverse=True)
    return rows

def global_avg(year: int) -> float:
    vals = [r["coverage_pct"] for r in _FAKE if r["year"]==year]
    return round(sum(vals)/len(vals), 2) if vals else 0.0
