from sqlalchemy import Column, Integer, String
from app.database import Base
from datetime import datetime
from sqlalchemy import DateTime




class SegmentationResult(Base):

    __tablename__ = "segmentation_results"

    id = Column(Integer, primary_key=True, index=True)

    customer_name = Column(String)

    spending_score = Column(Integer)

    annual_income = Column(Integer)

    cluster = Column(Integer)

    customer_segment = Column(String)

    created_at = Column(
    DateTime,
    default=datetime.utcnow
    )

