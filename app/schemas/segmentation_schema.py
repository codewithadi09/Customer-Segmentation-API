from pydantic import BaseModel
from typing import List


class SegmentationResponse(BaseModel):

    id: int
    customer_code: str
    customer_name: str
    spending_score: int
    annual_income: int
    cluster: int
    customer_segment: str

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):

    total_customers: int
    customers: List[SegmentationResponse]