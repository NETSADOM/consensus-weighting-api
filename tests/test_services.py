import pytest
from app.models import Allocation
from app.services import aggregate_allocations

def test_aggregate_allocations():
    # Example input from requirements
    allocations = [
        Allocation(userId="user_1", targetId="A", amount=40),
        Allocation(userId="user_1", targetId="A", amount=60),
        Allocation(userId="user_2", targetId="A", amount=50),
        Allocation(userId="user_1", targetId="B", amount=25)
    ]
    
    result = aggregate_allocations(allocations)
    
    # Assertions for Target A
    assert "A" in result
    target_a = result["A"]
    assert target_a.user_amounts == {"user_1": 100.0, "user_2": 50.0}
    assert target_a.raw_total == 150.0
    assert target_a.unique_user_count == 2
    
    # Assertions for Target B
    assert "B" in result
    target_b = result["B"]
    assert target_b.user_amounts == {"user_1": 25.0}
    assert target_b.raw_total == 25.0
    assert target_b.unique_user_count == 1

def test_aggregate_multiple_targets_same_user():
    allocations = [
        Allocation(userId="u1", targetId="T1", amount=10),
        Allocation(userId="u1", targetId="T2", amount=20),
    ]
    
    result = aggregate_allocations(allocations)
    
    assert result["T1"].unique_user_count == 1
    assert result["T1"].user_amounts["u1"] == 10.0
    
    assert result["T2"].unique_user_count == 1
    assert result["T2"].user_amounts["u1"] == 20.0
