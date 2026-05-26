from app.database import engine, Base
from app.models.segmentation_model import SegmentationResult

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")