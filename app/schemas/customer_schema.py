from pydantic import BaseModel
from datetime import datetime


class CustomerResponse(BaseModel):

    id: int

    customer_code: str

    customer_name: str

    spending_score: int

    annual_income: int

    cluster: int

    customer_segment: str

    created_at: datetime


    class Config:

        from_attributes = True