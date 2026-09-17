from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_calculate_weights():
    payload = [
        {"userId": "user_1", "targetId": "A", "amount": 10000},
        {"userId": "user_2", "targetId": "B", "amount": 100}
    ]
    response = client.post("/weights", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Check Target A
    target_a = next(item for item in data if item["targetId"] == "A")
    assert target_a["rawTotal"] == 10000.0
    assert target_a["uniqueUserCount"] == 1
    assert target_a["weight"] == 10000.0
    
    # Check Target B
    target_b = next(item for item in data if item["targetId"] == "B")
    assert target_b["rawTotal"] == 100.0
    assert target_b["uniqueUserCount"] == 1
    assert target_b["weight"] == 100.0
