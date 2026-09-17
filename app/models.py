from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Annotated

# Type for a string that strips leading/trailing whitespace and requires at least 1 character
NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class Allocation(BaseModel):
    """
    Model representing a single allocation entry.
    """
    model_config = ConfigDict(populate_by_name=True)

    user_id: NonEmptyString = Field(alias="userId", description="The ID of the user submitting the allocation")
    target_id: NonEmptyString = Field(alias="targetId", description="The target entity receiving the allocation")
    amount: float = Field(gt=0, description="The allocation amount, must be strictly greater than zero")

class TargetResponse(BaseModel):
    """
    Response model for a single target's computed weight and aggregation data.
    """
    model_config = ConfigDict(populate_by_name=True)

    target_id: str = Field(alias="targetId")
    raw_total: float = Field(alias="rawTotal")
    unique_user_count: int = Field(alias="uniqueUserCount")
    weight: float
