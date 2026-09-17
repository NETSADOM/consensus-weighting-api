import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# ---------------------------------------------------------
# 1. Concentrated vs Distributed Participation & 3, 4, 5
# ---------------------------------------------------------
def test_concentrated_vs_distributed_weighting():
    """
    REQUIRED MATHEMATICAL SCENARIO:
    Target A: 1 unique user, 10,000 allocation.
    Target B: 100 unique users, 100 allocation each.
    """
    # Target A
    payload_a = [{"userId": "whale_user", "targetId": "A", "amount": 10000}]
    
    # Target B
    payload_b = [{"userId": f"user_{i}", "targetId": "B", "amount": 100} for i in range(100)]
    
    # 3. Multiple targets in one request
    response = client.post("/weights", json=payload_a + payload_b)
    
    # 12. API Endpoint Returns Successful Status
    assert response.status_code == 200
    data = response.json()
    
    target_a = next(t for t in data if t["targetId"] == "A")
    target_b = next(t for t in data if t["targetId"] == "B")
    
    weight_a = target_a["weight"]
    weight_b = target_b["weight"]
    
    # 4. Verify rawTotal
    assert target_a["rawTotal"] == 10000.0
    assert target_b["rawTotal"] == 10000.0
    
    # 5. Verify uniqueUserCount
    assert target_a["uniqueUserCount"] == 1
    assert target_b["uniqueUserCount"] == 100
    
    # Mathematical Printout for review
    print(f"\n[OUTPUT] weight_A = {weight_a}")
    print(f"[OUTPUT] weight_B = {weight_b}")
    print(f"[OUTPUT] Ratio (B / A) = {weight_b / weight_a}")
    
    # 1. Programmatic Assertion: weight_B >= 2 * weight_A
    assert weight_b >= 2 * weight_a
    
    # Exact verification (10000 vs 1000000)
    assert weight_a == 10000.0
    assert weight_b == 1000000.0


# ---------------------------------------------------------
# 2. Duplicate Allocations from the SAME User
# ---------------------------------------------------------
def test_duplicate_allocations_aggregation():
    """
    user_1 -> A -> 50
    user_1 -> A -> 50
    Verify rawTotal=100, uniqueUserCount=1, weight=100
    """
    payload = [
        {"userId": "user_1", "targetId": "A", "amount": 50},
        {"userId": "user_1", "targetId": "A", "amount": 50}
    ]
    response = client.post("/weights", json=payload)
    assert response.status_code == 200
    
    data = response.json()[0]
    
    # Verify proper aggregation
    assert data["rawTotal"] == 100.0
    assert data["uniqueUserCount"] == 1
    
    # Verify math (sqrt(100)^2 = 100) vs non-aggregated (sqrt(50)+sqrt(50))^2 = 200
    assert data["weight"] == 100.0


# ---------------------------------------------------------
# 11. Decimal Amount
# ---------------------------------------------------------
def test_valid_decimal_amount():
    payload = [{"userId": "user_1", "targetId": "C", "amount": 10.5}]
    response = client.post("/weights", json=payload)
    assert response.status_code == 200
    
    data = response.json()[0]
    assert data["rawTotal"] == 10.5
    # sqrt(10.5)^2 is precisely 10.5
    assert data["weight"] == pytest.approx(10.5)


# ---------------------------------------------------------
# Validation Rejections (6, 7, 8, 9, 10, 12)
# ---------------------------------------------------------
def test_validation_errors():
    # 6. Invalid zero amount
    resp_zero = client.post("/weights", json=[{"userId": "u", "targetId": "A", "amount": 0}])
    assert resp_zero.status_code == 422
    
    # 7. Invalid negative amount
    resp_neg = client.post("/weights", json=[{"userId": "u", "targetId": "A", "amount": -100}])
    assert resp_neg.status_code == 422
    
    # 8. Empty/whitespace userId
    resp_empty_user = client.post("/weights", json=[{"userId": "", "targetId": "A", "amount": 10}])
    assert resp_empty_user.status_code == 422
    resp_ws_user = client.post("/weights", json=[{"userId": "   ", "targetId": "A", "amount": 10}])
    assert resp_ws_user.status_code == 422
    
    # 9. Empty/whitespace targetId
    resp_empty_target = client.post("/weights", json=[{"userId": "u", "targetId": "", "amount": 10}])
    assert resp_empty_target.status_code == 422
    
    # 10. Missing required fields
    resp_missing = client.post("/weights", json=[{"targetId": "A", "amount": 10}])
    assert resp_missing.status_code == 422
