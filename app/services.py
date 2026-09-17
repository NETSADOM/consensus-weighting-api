import math
from typing import List, Dict, Collection
from dataclasses import dataclass
from app.models import Allocation

@dataclass
class TargetAggregation:
    """
    Holds the aggregated allocation data and computed weight for a single target.
    """
    target_id: str
    user_amounts: Dict[str, float]
    raw_total: float
    unique_user_count: int
    weight: float

def calculate_consensus_weight(user_amounts: Collection[float]) -> float:
    """
    Calculates the consensus weight from a collection of pre-aggregated user totals.
    Purpose: Prioritizes broad participation over concentrated capital by 
    taking the square of the sum of the square roots of individual totals.
    """
    return sum(math.sqrt(amt) for amt in user_amounts) ** 2

def aggregate_allocations(allocations: List[Allocation]) -> Dict[str, TargetAggregation]:
    """
    Groups allocations by targetId, aggregates the amounts by userId, 
    and calculates the consensus weight based on quadratic voting principles.
    """
    grouped_data: Dict[str, Dict[str, float]] = {}
    
    for alloc in allocations:
        if alloc.target_id not in grouped_data:
            grouped_data[alloc.target_id] = {}
            
        if alloc.user_id not in grouped_data[alloc.target_id]:
            grouped_data[alloc.target_id][alloc.user_id] = 0.0
            
        grouped_data[alloc.target_id][alloc.user_id] += alloc.amount
        
    result: Dict[str, TargetAggregation] = {}
    for target_id, user_amounts in grouped_data.items():
        raw_total = sum(user_amounts.values())
        unique_user_count = len(user_amounts)
        weight = calculate_consensus_weight(user_amounts.values())
        
        result[target_id] = TargetAggregation(
            target_id=target_id,
            user_amounts=user_amounts,
            raw_total=raw_total,
            unique_user_count=unique_user_count,
            weight=weight
        )
        
    return result
