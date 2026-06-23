from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database import Base


class SegmentationRun(Base):

    __tablename__ = "segmentation_runs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    optimal_clusters = Column(
        Integer
    )

    silhouette_score = Column(
        Float
    )

    total_customers = Column(
        Integer
    )