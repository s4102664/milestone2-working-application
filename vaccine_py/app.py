from flask import Flask, jsonify, request

try:
    from vaccine_py.services.coverage import (
        get_filtered_data, compare_country, get_trends, ISO_TO_NAME
    )
except ImportError:
    from services.coverage import (
        get_filtered_data, compare_country, get_trends, ISO_TO_NAME
    )

app = Flask(__name__)

BOOTSTRAP = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<style>
:root{
  --bg-header:#0B1220;
  --bg:#FFFFFF;
  --panel:#FFFFFF;
  --ink:#0F172A;
  --muted:#475569;
  --line:#E5E7EB;
  --brand:#3B82F6;
  --brand-ink:#FFFFFF;
  --ok:#16A34A;
  --bad:#DC2626;
}
html,body{
  background:var(--bg);
  color:var(--ink);
  font:16px/1.55 system-ui,Segoe UI,Roboto,Arial,sans-serif;
  margin:0
}
.navbar{background:var(--bg-header)}
.navbar .navbar-brand,.navbar .nav-link{color:#E5E7EB!important}
.navbar .nav-link.active{color:#FFF!important;font-weight:700}
.card{
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:16px;
  padding:20px;
  box-shadow:0 6px 16px rgba(0,0,0,.06)
}
.form-control,.form-select{
  background:#FFF;
  color:var(--ink);
  border:1px solid var(--line);
  border-radius:12px;
  padding:12px 14px
}
.btn{border-radius:12px;font-weight:700}
.btn-primary{background:var(--brand);border-color:var(--brand)}
.btn-outline-secondary{color:var(--ink);border-color:var(--line);background:#FFF}

.result-box{
  border:1px solid var(--line);
  border-radius:14px;
  background:#F8FAFC;
  padding:16px
}
.kv{display:grid;grid-template-columns:180px 1fr;gap:8px 12px}
.kv .k{color:var(--muted);font-weight:600}
.kv .v{color:var(--ink)}

.callout{margin-top:14px;padding:12px 14px;border-radius:12px;font-weight:600}
.callout.good{background:#ECFDF5;border:1px solid #DCFCE7;color:#065F46}
.callout.bad{background:#FEF2F2;border:1px solid #FEE2E2;color:#7F1D1D}

.table{
  border-collapse:collapse;
  width:100%;
}
.table thead th{
  background:#0B1220;
  color:#FFFFFF;
  border-color:#0B1220;
  font-weight:600;
}
.table tbody td{
  background:#1C2433;
  color:#FFFFFF;
}
.table-striped>tbody>tr:nth-of-type(odd)>*{
  background:#161E2B;
}
.table tbody tr:hover td{
  background:#263144;
  color:#FFFFFF;
}
.table td,.table th{
  padding:12px 14px;
  vertical-align:middle;
}

.card.p-3 h5{color:#0F172A;font-weight:700}
.card.p-3 strong{color:#1E3A8A}
</style>
"""

def layout(page_title: str, active: str, body_html: str) -> str:
    nav = f"""
    <nav class="navbar navbar-expand-lg navbar-dark mb-4" style="background:#0E1628">
      <div class="container">
        <a class="navbar-brand fw-bold" href="/">Vaccine Intelligence</a>
        <span class="ms-2 text-success fw-semibold">● API is running</span>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navitems">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div id="navitems" class="collapse navbar-collapse">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item"><a class="nav-link {'active fw-semibold' if active=='compare' else ''}" href="/compare">Compare Country vs Global</a></li>
            <li class="nav-item"><a class="nav-link {'active fw-semibold' if active=='explorer' else ''}" href="/explorer">Filter & Sort Data</a></li>
            <li class="nav-item"><a class="nav-link {'active fw-semibold' if active=='trends' else ''}" href="/trends-ui">Trends (Multiple Countries)</a></li>
          </ul>
        </div>
      </div>
    </nav>
    """
    footer = """
    <div class="container my-5">
      <div class="text-secondary">Follows Nielsen heuristics: visibility, match, consistency, control, error prevention.</div>
    </div>
    """
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>{BOOTSTRAP}</head>
<body>{nav}<main class="container mb-5">{body_html}</main>{footer}</body></html>"""

@app.get("/")
def home():
    body = """
    <div class="card p-4">
      <h1 class="h3 mb-3">Home</h1>
      <p class="mb-4">Choose what you want to do:</p>
      <div class="d-flex gap-3 flex-wrap">
        <a class="btn btn-primary" href="/compare">Compare Country vs Global</a>
        <a class="btn btn-primary" href="/explorer">Filter & Sort Data</a>
        <a class="btn btn-primary" href="/trends-ui">Trends (Multiple Countries)</a>
      </div>
    </div>
    """
    return layout("Home — Vaccine Intelligence", "home", body)

@app.get("/compare")
def page_compare():
    body = """
    <div class="row g-4">
      <div class="col-lg-7">
        <div class="card">
          <h2 class="h4 mb-4">Compare Country vs Global Average</h2>
          <div class="row gy-3">
            <div class="col-md-6">
              <label>Country (ISO)</label>
              <input id="cmp-country" value="AUS" class="form-control">
            </div>
            <div class="col-md-6">
              <label>Year</label>
              <input id="cmp-year" type="number" value="2024" class="form-control">
            </div>
            <div class="col-12">
              <button class="btn btn-primary" onclick="doCompare()">Compare</button>
              <button class="btn btn-outline-secondary ms-2" onclick="resetCompare()">Reset</button>
            </div>
          </div>
        </div>
      </div>
      <div class="col-lg-5">
        <div class="card">
          <h3 class="h5 mb-3">Result</h3>
          <div id="cmp-result" class="result-box">
            <div class="text-muted">Run a comparison to see data here…</div>
          </div>
        </div>
      </div>
    </div>

    <script>
    async function doCompare(){
      const country = document.querySelector('#cmp-country').value.trim();
      const year = document.querySelector('#cmp-year').value.trim();
      const res = await fetch('/compare.json?country=' + encodeURIComponent(country) + '&year=' + encodeURIComponent(year));
      const js = await res.json();
      const box = document.querySelector('#cmp-result');

      if (js.error) {
        box.innerHTML = '<div class="callout bad">⚠️ ' + js.error + '</div>';
        return;
      }
      const diff = (js.local - js.global_avg).toFixed(1);
      const better = diff >= 0;
      const callClass = better ? 'good' : 'bad';
      const callText = better
        ? ('✅ ' + js.country_name + ' is ' + diff + ' pp above the global average')
        : ('❌ ' + js.country_name + ' is ' + Math.abs(diff) + ' pp below the global average');

      box.innerHTML =
        '<div class="kv">'
        + '<div class="k">Country</div><div class="v">' + js.country_name + ' (' + js.country_code + ')</div>'
        + '<div class="k">Year</div><div class="v">' + js.year + '</div>'
        + '<div class="k">Vaccine</div><div class="v">' + (js.vaccine || 'MMR') + '</div>'
        + '<div class="k">Local coverage</div><div class="v">' + js.local + '%</div>'
        + '<div class="k">Global average</div><div class="v">' + js.global_avg + '%</div>'
        + '<div class="k">Difference</div><div class="v">' + (better ? '+' : '') + diff + ' pp</div>'
        + '</div>'
        + '<div class="callout ' + callClass + '">' + callText + '</div>';
    }
    function resetCompare(){
      document.querySelector('#cmp-country').value = 'AUS';
      document.querySelector('#cmp-year').value = '2024';
      document.querySelector('#cmp-result').innerHTML = '<div class="text-muted">Run a comparison to see data here…</div>';
    }
    </script>
    """
    return layout("Compare — Vaccine Intelligence", "compare", body)

@app.get("/explorer")
def page_explorer():
    iso_map_js = "{" + ",".join([f"'{k}':'{v}'" for k,v in ISO_TO_NAME.items()]) + "}"
    body = f"""
    <div class="card p-4 mb-4">
      <h2 class="h4 mb-4">Data Explorer (Filter & Sort)</h2>
      <form class="row gy-3 align-items-end" onsubmit="return false;">
        <div class="col-sm-3"><label>Country (ISO)</label><input id="q_country" class="form-control" value="AUS"></div>
        <div class="col-sm-3"><label>Vaccine</label><input id="q_vaccine" class="form-control" value="MMR"></div>
        <div class="col-sm-2"><label>Year</label><input id="q_year" class="form-control" type="number" value="2024"></div>
        <div class="col-sm-3">
          <label>Sort</label>
          <select id="q_sort" class="form-select">
            <option value="coverage_desc" selected>Coverage (desc)</option>
            <option value="coverage_asc">Coverage (asc)</option>
          </select>
        </div>
        <div class="col-sm-1"><button class="btn btn-primary w-100" id="q_run">Run</button></div>
      </form>
    </div>

    <div class="card p-3">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <h3 class="h6 mb-0">Results</h3>
        <button class="btn btn-outline-light btn-sm" id="btn_csv">Export CSV</button>
      </div>
      <div class="table-responsive">
        <table class="table table-sm table-dark table-striped align-middle" id="q_table">
          <thead><tr><th>Country</th><th>Vaccine</th><th>Year</th><th>Coverage (%)</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
      <div class="small text-secondary">Rows: <span id="q_count">0</span></div>
    </div>

    <script>
    const ISO_TO_NAME = {iso_map_js};
    const isoToName = (c) => ISO_TO_NAME?.[String(c||'').toUpperCase()] || c;

    const TBody = document.querySelector('#q_table tbody');
    const Count = document.getElementById('q_count');

    async function runQuery(){{
      const payload = {{
        country: (document.getElementById('q_country').value || null),
        vaccine: (document.getElementById('q_vaccine').value || null),
        year:    (document.getElementById('q_year').value || '') ? parseInt(document.getElementById('q_year').value) : null,
        sort:    document.getElementById('q_sort').value || 'coverage_desc'
      }};
      const r = await fetch('/coverage/query', {{
        method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(payload)
      }});
      const js = await r.json();

      TBody.innerHTML = '';
      (js.rows||[]).forEach(row => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${{isoToName(row.country)}}</td><td>${{row.vaccine}}</td><td>${{row.year}}</td><td>${{row.coverage}}</td>`;
        TBody.appendChild(tr);
      }});
      Count.textContent = (js.rows||[]).length;
      window.__lastRows = js.rows || [];
    }}

    document.getElementById('q_run').addEventListener('click', runQuery);

    document.getElementById('btn_csv').addEventListener('click', () => {{
      const rows = window.__lastRows || [];
      const head = ['country','vaccine','year','coverage'];
      const all = [head].concat(rows.map(r => [r.country, r.vaccine, r.year, r.coverage]));
      const csv = all.map(a => a.map(x => `"${{String(x).replaceAll('"','""')}}"`).join(',')).join('\\n');
      const blob = new Blob([csv], {{type:'text/csv'}});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = 'coverage_export.csv'; a.click();
      URL.revokeObjectURL(url);
    }});

    runQuery();
    </script>
    """
    return layout("Explorer — Vaccine Intelligence", "explorer", body)

@app.get("/trends-ui")
def page_trends_ui():
    iso_map_js = "{" + ",".join([f"'{k}':'{v}'" for k,v in ISO_TO_NAME.items()]) + "}"
    body = f"""
    <div class="card p-4 mb-4">
      <h2 class="h4 mb-4">Trends (Multiple Countries)</h2>
      <form class="row gy-3 align-items-end" onsubmit="return false;">
        <div class="col-sm-4"><label>Vaccine</label><input id="t_vaccine" class="form-control" value="MMR"></div>
        <div class="col-sm-6"><label>Countries (CSV)</label><input id="t_countries" class="form-control" value="AUS,NZL,GBR"></div>
        <div class="col-sm-2"><button class="btn btn-primary w-100" id="t_run">Load</button></div>
      </form>
    </div>

    <div id="t_cards" class="row g-3"></div>

    <script>
    const ISO_TO_NAME = {iso_map_js};
    const isoToName = (c) => ISO_TO_NAME?.[String(c||'').toUpperCase()] || c;

    const Cards = document.getElementById('t_cards');

    async function loadTrends(){{
      const vaccine = document.getElementById('t_vaccine').value || 'MMR';
      const countries = document.getElementById('t_countries').value || 'AUS,NZL,GBR';
      const r = await fetch(`/trends?vaccine=${{encodeURIComponent(vaccine)}}&countries=${{encodeURIComponent(countries)}}`);
      const js = await r.json();

      Cards.innerHTML = '';
      (js.points||[]).forEach(p => {{
        Cards.insertAdjacentHTML('beforeend', `
          <div class="col-md-4">
            <div class="card p-3">
              <h5 class="mb-2">${{isoToName(p.country)}} (${{String(p.country||'').toUpperCase()}})</h5>
              <div>Year: <strong>${{p.year}}</strong></div>
              <div>Vaccine: <strong>${{p.vaccine}}</strong></div>
              <div>Coverage: <strong>${{p.coverage}}%</strong></div>
            </div>
          </div>
        `);
      }});
    }}

    document.getElementById('t_run').addEventListener('click', loadTrends);
    loadTrends();
    </script>
    """
    return layout("Trends — Vaccine Intelligence", "trends", body)

@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store, max-age=0"
    return resp

@app.get("/health")
def health():
    return jsonify({"ok": True, "message": "API is running", "version": "1.0.0"}), 200

@app.route("/coverage/query", methods=["GET", "POST"])
def query_coverage():
    if request.method == "GET":
        data = {
            "country": request.args.get("country"),
            "vaccine": request.args.get("vaccine"),
            "year": request.args.get("year", type=int),
            "sort": request.args.get("sort", "coverage_desc"),
        }
    else:
        data = request.get_json(silent=True) or {}

    rows = get_filtered_data(
        country=(data.get("country") or None),
        vaccine=(data.get("vaccine") or None),
        year=data.get("year"),
        sort=data.get("sort", "coverage_desc"),
    )
    return jsonify({"count": len(rows), "rows": rows}), 200

@app.get("/coverage/compare")
def compare_api():
    return compare_json()

@app.get("/compare.json")
def compare_json():
    code = (request.args.get("country", "AUS") or "AUS").upper()
    vaccine = request.args.get("vaccine", "MMR") or "MMR"
    try:
        year = int(request.args.get("year", 2024))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid year parameter"}), 400

    result = compare_country(code, year) 
    if "error" in result:
        return jsonify(result), 200

    result["country_code"] = code
    result["country_name"] = ISO_TO_NAME.get(code, code)
    result["vaccine"] = vaccine
    if isinstance(result.get("local"), (int, float)):
        result["local"] = round(result["local"], 1)
    if isinstance(result.get("global_avg"), (int, float)):
        result["global_avg"] = round(result["global_avg"], 1)

    return jsonify(result), 200

@app.get("/trends")
def trends():
    vaccine = request.args.get("vaccine", "MMR")
    countries = [c.strip().upper() for c in request.args.get("countries", "AUS,NZL,GBR").split(",")]
    return jsonify(get_trends(vaccine, countries)), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "path": request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    from services.coverage import init_db
    init_db()
    app.run(host="127.0.0.1", port=5055, debug=False, threaded=True)
