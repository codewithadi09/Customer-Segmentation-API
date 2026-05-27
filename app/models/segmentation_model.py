from sqlalchemy import Column, Integer, String
from app.database import Base


class SegmentationResult(Base):

    __tablename__ = "segmentation_results"

    id = Column(Integer, primary_key=True, index=True)

    customer_name = Column(String)

    spending_score = Column(Integer)

    annual_income = Column(Integer)

    cluster = Column(Integer)

    customer_segment = Column(String)

