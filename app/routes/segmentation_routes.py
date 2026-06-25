from fastapi import APIRouter, UploadFile, File, Depends, Request
from sqlalchemy.orm import Session
import io

from app.dependencies import get_db
from app.schemas.segmentation_schema import CustomerListResponse, SegmentationResponse
from app.services.segmentation_service import (
    segment_customers,
    get_all_customers_service,
    get_customer_by_code_service,
    get_all_segmentation_runs_service,
    get_statistics_service
)
from app.routes.auth_routes import get_current_user
from app.models.user_model import User
from app.utils.file_validator import validate_csv_file
from app.middleware.rate_limit import limiter

router = APIRouter()


@router.post("/upload-csv")
@limiter.limit("10/minute")  # prevent automated bulk upload abuse
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate before passing to the pipeline
    contents = await validate_csv_file(file)

    # Reset file pointer so the service can read it as a stream
    file.file = io.BytesIO(contents)

    return segment_customers(file=file, db=db)


@router.get("/customers", response_model=CustomerListResponse)
def get_customers(
    skip: int = 0,
    limit: int = 100,
    segment: str | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customers = get_all_customers_service(
        skip=skip,
        limit=limit,
        segment=segment,
        search=search,
        sort_by=sort_by,
        order=order,
        db=db
    )
    return {"total_customers": len(customers), "customers": customers}


@router.get("/high-value-customers", response_model=CustomerListResponse)
def get_high_value_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.services.segmentation_service import get_high_value_customers_service
    return get_high_value_customers_service(db=db)


@router.get("/customer/{customer_code}", response_model=SegmentationResponse)
def get_customer_by_code(
    customer_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_customer_by_code_service(customer_code=customer_code, db=db)