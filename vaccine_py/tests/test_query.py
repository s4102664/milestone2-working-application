from vaccine_py.app import app

def test_query_filter_ok():
    client = app.test_client()
    payload = {"country": "AUS", "vaccine": "MMR", "year": 2024, "sort": "coverage_desc"}
    rv = client.post("/coverage/query", json=payload)
    js = rv.get_json()
    assert rv.status_code == 200
    assert js["count"] >= 1
    assert js["rows"][0]["country"] == "AUS"