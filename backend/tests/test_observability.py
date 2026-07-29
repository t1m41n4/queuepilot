def test_request_correlation_id_is_returned(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "demo-request-1"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "demo-request-1"


def test_invalid_request_id_is_replaced(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "bad value"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "bad value"


def test_liveness_readiness_and_metrics_endpoints(client):
    assert client.get("/api/v1/health/live").json() == {"status": "ok"}
    assert client.get("/api/v1/health/ready").json() == {"status": "ready"}
    metrics = client.get("/api/v1/metrics")
    assert metrics.status_code == 200
    assert "http_requests_total" in metrics.json()["metrics"]
