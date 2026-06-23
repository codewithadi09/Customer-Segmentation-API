from pydantic import BaseModel
from datetime import datetime


class SegmentationRunResponse(BaseModel):

    id: int

    filename: str

    timestamp: datetime

    optimal_clusters: int

    silhouette_score: float

    total_customers: int


    class Config:

        from_attributes = True