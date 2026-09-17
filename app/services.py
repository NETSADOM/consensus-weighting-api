from typing import List, Dict
from dataclasses import dataclass
from app.models import Allocation

@dataclass
class TargetAggregation:
    """
    Holds the aggregated allocation data for a single target.
    """
    target_id: str
    user_amounts: Dict[str, float]
    raw_total: float
    unique_user_count: int

def aggregate_allocations(allocations: List[Allocation]) -> Dict[str, TargetAggregation]:
    """
    Groups allocations by targetId and then aggregates the amounts by userId.
    """
    # Intermediate structure: mapping from target_id -> { user_id -> amount }
    grouped_data: Dict[str, Dict[str, float]] = {}
    
    for alloc in allocations:
        # 1. Group by targetId
        if alloc.target_id not in grouped_data:
            grouped_data[alloc.target_id] = {}
            
        # 2. Within each target, aggregate by userId
        if alloc.user_id not in grouped_data[alloc.target_id]:
            grouped_data[alloc.target_id][alloc.user_id] = 0.0
            
        # Sum the amount if the same user made multiple allocations to this target
        grouped_data[alloc.target_id][alloc.user_id] += alloc.amount
        
    # Build final summary objects
    result: Dict[str, TargetAggregation] = {}
    for target_id, user_amounts in grouped_data.items():
        # Calculate rawTotal and uniqueUserCount
        raw_total = sum(user_amounts.values())
        unique_user_count = len(user_amounts)
        
        result[target_id] = TargetAggregation(
            target_id=target_id,
            user_amounts=user_amounts,
            raw_total=raw_total,
            unique_user_count=unique_user_count
        )
        
    return result
