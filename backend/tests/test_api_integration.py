def token(client, email="cbd@test.local"):
    response = client.post("/api/v1/staff/login", json={"email": email, "password": "password123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_public_health_banks_and_branches(client):
    assert client.get("/api/v1/health").status_code == 200
    banks = client.get("/api/v1/banks")
    assert banks.status_code == 200
    branches = client.get(f"/api/v1/banks/{banks.json()[0]['id']}/branches")
    assert branches.status_code == 200
    assert len(branches.json()) == 2


def test_authentication_and_dashboard_scope(client):
    assert client.post("/api/v1/staff/login", json={"email": "cbd@test.local", "password": "wrong"}).status_code == 401
    cbd = client.get("/api/v1/staff/dashboard", headers={"Authorization": f"Bearer {token(client)}"})
    westlands = client.get("/api/v1/staff/dashboard", headers={"Authorization": f"Bearer {token(client, 'westlands@test.local')}"})
    assert cbd.status_code == westlands.status_code == 200
    assert cbd.json()["branch_id"] != westlands.json()["branch_id"]


def test_customer_join_and_cancel_workflow(client):
    join = client.post("/api/v1/queue/join", json={"branch_id": 2, "customer_name": "API Customer"})
    assert join.status_code == 200
    entry_id = join.json()["queue_entry_id"]
    assert client.get(f"/api/v1/queue/{entry_id}").status_code == 200
    cancel = client.post(f"/api/v1/queue/{entry_id}/cancel", json={})
    assert cancel.status_code == 200


def test_cross_branch_staff_operation_is_forbidden(client):
    join = client.post("/api/v1/queue/join", json={"branch_id": 2, "customer_name": "Protected Customer"})
    assert join.status_code == 200
    entry_id = join.json()["queue_entry_id"]
    response = client.post(
        "/api/v1/staff/start-service",
        headers={"Authorization": f"Bearer {token(client)}"},
        json={"queue_entry_id": entry_id},
    )
    assert response.status_code == 403
    client.post(f"/api/v1/queue/{entry_id}/cancel", json={})
