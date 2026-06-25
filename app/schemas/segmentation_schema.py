from pydantic import BaseModel, ConfigDict
from typing import List


class SegmentationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    spending_score: int
    annual_income: int
    cluster: int
    customer_segment: str


class CustomerListResponse(BaseModel):
    total_customers: int
    customers: List[SegmentationResponse]