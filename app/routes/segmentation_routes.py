from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import pandas as pd
from sklearn.cluster import KMeans
from typing import List

from app.dependencies import get_db
from app.models.segmentation_model import SegmentationResult
from app.schemas.segmentation_schema import CustomerListResponse, SegmentationResponse
from app.services.segmentation_service import segment_customers, get_all_customers_service, get_customer_by_code_service, get_all_segmentation_runs_service, get_statistics_service
from app.routes.auth_routes import get_current_user
from app.models.user_model import User
from app.schemas.customer_schema import CustomerResponse
from app.schemas.segmentation_run_schema import SegmentationRunResponse


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
    response_model=list[CustomerResponse]
)
def get_all_customers(

    skip: int = Query(
        default=0,
        ge=0
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    segment: str | None = Query(
        default=None
    ),

    search: str | None = Query(
        default=None
    ),

    sort_by: str | None = Query(
    default=None
    ),

    order: str = Query(
    default="asc"
    ),

    db: Session = Depends(get_db)

):

    return get_all_customers_service(

        skip=skip,

        limit=limit,

        segment=segment,

        search=search,

        sort_by=sort_by,

        order=order,

        db=db

    )

    



@router.get(
    "/customer/{customer_code}",
     response_model=CustomerListResponse
)
def get_customer_by_id(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_customer_by_code_service(customer_code=customer_id, db=db)
    

@router.get(
    "/runs",
    response_model=list[SegmentationRunResponse]
)
def get_all_segmentation_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_all_segmentation_runs_service(
        db=db
    )


@router.get(
    "/stats"
)
def get_statistics(
    db: Session = Depends(
        get_db
    )
):

    return get_statistics_service(
        db=db
    )