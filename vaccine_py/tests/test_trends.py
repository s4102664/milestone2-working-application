from vaccine_py.app import app

def test_trends_ok():
    c = app.test_client()
    rv = c.get("/trends?vaccine=MMR&countries=AUS,NZL,GBR")
    js = rv.get_json()
    assert rv.status_code == 200
    assert js["count"] == 3
    assert "points" in js
