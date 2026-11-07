from app.main import limiter
from app.utils import detect_device

GOOGLE = {"url": "https://www.google.com"}


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200


def test_shorten_creates_code(client):
    r = client.post("/shorten", json=GOOGLE)
    assert r.status_code == 200
    data = r.json()
    assert data["short_code"] == "1"
    assert data["original_url"] == "https://www.google.com/"


def test_shorten_rejects_invalid_url(client):
    r = client.post("/shorten", json={"url": "hello"})
    assert r.status_code == 422


def test_duplicate_url_returns_same_code(client):
    first = client.post("/shorten", json=GOOGLE).json()
    second = client.post("/shorten", json=GOOGLE).json()
    assert first["short_code"] == second["short_code"]


def test_redirect_goes_to_original_url(client):
    code = client.post("/shorten", json=GOOGLE).json()["short_code"]
    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "https://www.google.com/"


def test_unknown_code_returns_404(client):
    r = client.get("/zzzz", follow_redirects=False)
    assert r.status_code == 404


def test_stats_counts_clicks(client):
    code = client.post("/shorten", json=GOOGLE).json()["short_code"]
    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)
    stats = client.get(f"/stats/{code}").json()
    assert stats["click_count"] == 3
    assert len(stats["recent_clicks"]) == 3

def test_rate_limit_blocks_after_10_requests(client):
    limiter.enabled = True
    limiter.reset()
    statuses = []
    for i in range(11):
        r = client.post("/shorten", json={"url": f"https://example.com/{i}"})
        statuses.append(r.status_code)
    assert statuses[:10] == [200] * 10
    assert statuses[10] == 429

def test_detect_device():
    assert detect_device("Mozilla/5.0 (iPhone) Mobile Safari") == "Mobile"
    assert detect_device("Mozilla/5.0 (iPad) Safari") == "Tablet"
    assert detect_device("Mozilla/5.0 (Windows NT 10.0) Chrome") == "Desktop"
    assert detect_device(None) == "Unknown"


def test_analytics_summary(client):
    code = client.post("/shorten", json=GOOGLE).json()["short_code"]
    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)
    data = client.get("/api/analytics").json()
    assert data["total_links"] == 1
    assert data["total_clicks"] == 2
    assert data["top_links"][0]["clicks"] == 2