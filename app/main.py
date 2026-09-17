from typing import List
from fastapi import FastAPI
from app.models import Allocation, TargetResponse
from app.services import aggregate_allocations

app = FastAPI(title="Consensus Weighting API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/weights", response_model=List[TargetResponse])
def calculate_weights(allocations: List[Allocation]):
    """
    Accepts a list of allocations, groups them by target, 
    and applies consensus weighting to calculate each target's final weight.
    """
    aggregated_data = aggregate_allocations(allocations)
    
    response = [
        TargetResponse(
            targetId=target_agg.target_id,
            rawTotal=target_agg.raw_total,
            uniqueUserCount=target_agg.unique_user_count,
            weight=target_agg.weight
        )
        for target_agg in aggregated_data.values()
    ]
    
    # Sort deterministically by targetId
    response.sort(key=lambda x: x.target_id)
    return response
