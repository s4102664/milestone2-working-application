from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

try:
    from vaccine_py.services.coverage import get_filtered_data, compare_country, get_trends
except ImportError:
    from services.coverage import get_filtered_data, compare_country, get_trends

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@app.after_request
def add_common_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

# ---------- LEVEL 1 ----------
@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    """Level 1 - basic health check"""
    if request.method == "OPTIONS":
        return ("", 204)
    return jsonify({"ok": True, "message": "API is running", "version": "1.0.0"}), 200


# ---------- LEVEL 2 ----------
@app.route("/coverage/query", methods=["GET", "POST", "OPTIONS"])
def query_coverage():
    """Level 2 - filtering & sorting for Dr. Ahmed"""
    if request.method == "OPTIONS":
        return ("", 204)

    if request.method == "GET":
        country = request.args.get("country")
        vaccine = request.args.get("vaccine")
        year = request.args.get("year", type=int)
        sort = request.args.get("sort", "coverage_desc")
    else:
        data = request.get_json(silent=True) or {}
        country = data.get("country")
        vaccine = data.get("vaccine")
        year = data.get("year")
        sort = data.get("sort", "coverage_desc")

    rows = get_filtered_data(country=country, vaccine=vaccine, year=year, sort=sort)
    return jsonify({"count": len(rows), "rows": rows}), 200


# ---------- LEVEL 3 ----------
@app.route("/coverage/compare", methods=["GET", "OPTIONS"])
def compare():
    """Level 3 - compare local vs global average (Maria)"""
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        country = request.args.get("country", "AUS")
        year = int(request.args.get("year", 2024))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid year parameter"}), 400
    return jsonify(compare_country(country, year)), 200


@app.route("/trends", methods=["GET", "OPTIONS"])
def trends():
    """Level 3 - trends visualization (Liam)"""
    if request.method == "OPTIONS":
        return ("", 204)
    vaccine = request.args.get("vaccine", "MMR")
    countries = [c.strip() for c in request.args.get("countries", "AUS,NZL,GBR").split(",") if c.strip()]
    return jsonify(get_trends(vaccine, countries)), 200


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad Request", "detail": str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server Error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, debug=False, threaded=True)
