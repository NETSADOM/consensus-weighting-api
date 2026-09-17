import pytest
from pydantic import ValidationError
from app.models import Allocation

def test_valid_allocation():
    # Test valid creation using external API camelCase names
    alloc = Allocation(userId="user_1", targetId="A", amount=10000)
    assert alloc.user_id == "user_1"
    assert alloc.target_id == "A"
    assert alloc.amount == 10000.0

def test_valid_allocation_internal_names():
    # Test valid creation using internal snake_case names
    alloc = Allocation(user_id="user_2", target_id="B", amount=50.5)
    assert alloc.user_id == "user_2"

def test_user_id_validation():
    # Cannot be empty
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        Allocation(userId="", targetId="A", amount=10)
    
    # Cannot be just whitespace (strip_whitespace removes it, then min_length fails)
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        Allocation(userId="   ", targetId="A", amount=10)

def test_target_id_validation():
    # Cannot be empty
    with pytest.raises(ValidationError):
        Allocation(userId="u1", targetId="", amount=10)
    
    # Cannot be just whitespace
    with pytest.raises(ValidationError):
        Allocation(userId="u1", targetId=" \n\t", amount=10)

def test_amount_validation():
    # Cannot be zero
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        Allocation(userId="u1", targetId="A", amount=0)
    
    # Cannot be negative
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        Allocation(userId="u1", targetId="A", amount=-5)
    
    # Must be numeric (Pydantic handles basic coercion, but fails on invalid types)
    with pytest.raises(ValidationError):
        Allocation(userId="u1", targetId="A", amount="not-a-number")

def test_multiple_allocations_allowed_implicitly():
    # The model validation logic intrinsically allows multiple allocations
    # because it validates a single instance, and a List[Allocation] will happily
    # validate multiple instances with identical user/target IDs.
    alloc1 = Allocation(userId="user_1", targetId="A", amount=50)
    alloc2 = Allocation(userId="user_1", targetId="A", amount=100)
    
    assert alloc1.user_id == alloc2.user_id
    assert alloc1.target_id == alloc2.target_id
    assert alloc1.amount != alloc2.amount
