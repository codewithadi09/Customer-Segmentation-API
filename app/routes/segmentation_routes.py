from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
from sklearn.cluster import KMeans
from typing import List

from app.dependencies import get_db
from app.models.segmentation_model import SegmentationResult
from app.schemas.segmentation_schema import CustomerListResponse, SegmentationResponse
from app.services.segmentation_service import segment_customers, get_all_customers_service, get_high_value_customers_service, get_customer_by_id_service
from app.routes.auth_routes import get_current_user
from app.models.user_model import User

router = APIRouter()


@router.post("/upload-csv")
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return segment_customers(
        file=file,
        db=db
    )
    
@router.get(
    "/customers",
    response_model=CustomerListResponse
)
def get_customers(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return get_all_customers_service(db=db)

    

@router.get("/high-value-customers",
    response_model=CustomerListResponse
)

def get_high_value_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_high_value_customers_service(db=db)


@router.get(
    "/customer/{customer_id}",
    response_model=SegmentationResponse
)
def get_customer_by_id(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_customer_by_id_service(customer_id=customer_id, db=db)

    