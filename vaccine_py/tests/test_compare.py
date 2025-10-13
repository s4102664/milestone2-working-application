from vaccine_py.app import app

def test_compare_ok():
    c = app.test_client()
    rv = c.get("/coverage/compare?country=AUS&year=2024")
    js = rv.get_json()
    assert rv.status_code == 200
    assert js["country"] == "AUS"
    assert "global_avg" in js and "local" in js

def test_compare_invalid_year():
    c = app.test_client()
    rv = c.get("/coverage/compare?country=AUS&year=abc")
    assert rv.status_code == 400
