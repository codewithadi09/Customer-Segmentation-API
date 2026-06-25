import uuid
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from app.models.segmentation_model import SegmentationResult
from app.models.segmentation_run_model import SegmentationRun
from app.logger import logger


# -------------------------
# Determine optimal K
# -------------------------
def determine_best_k_using_silhouette_score(scaled_features):

    best_k = 2
    best_score = -1

    for k in range(2, 9):

        model = KMeans(
            n_clusters=k,
            init="k-means++",
            random_state=42,
            n_init=10
        )

        clusters = model.fit_predict(scaled_features)
        score = silhouette_score(scaled_features, clusters)

        if score > best_score:
            best_score = score
            best_k = k

    return best_k, best_score


# -------------------------
# Customer Segmentation
# -------------------------
def segment_customers(file, db: Session):

    try:
        logger.info("Starting segmentation pipeline", extra={"file_name": file.filename})

        df = pd.read_csv(file.file)

        required_columns = ["customer_name", "spending_score", "annual_income"]
        missing_columns = [c for c in required_columns if c not in df.columns]

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        df = df.dropna(subset=required_columns)

        for column in ["spending_score", "annual_income"]:
            try:
                df[column] = pd.to_numeric(df[column])
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{column}' contains invalid non-numeric values"
                )

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="No valid data remaining after preprocessing"
            )

        logger.info(
            "Preprocessing complete",
            extra={
                "file_name": file.filename,
                "total_rows": len(df),
            }
        )

        # -------------------------
        # Feature selection
        # -------------------------
        features = df[["spending_score", "annual_income"]]

        # -------------------------
        # Standardize features
        # -------------------------
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        # -------------------------
        # Find best K
        # -------------------------
        best_k, best_score = determine_best_k_using_silhouette_score(scaled_features)

        logger.info(
            "Clustering complete",
            extra={
                "file_name": file.filename,
                "optimal_clusters": best_k,
                "silhouette_score": round(best_score, 3),
            }
        )

        # -------------------------
        # Log segmentation run
        # -------------------------
        run = SegmentationRun(
            filename=file.filename,
            optimal_clusters=best_k,
            silhouette_score=round(best_score, 3),
            total_customers=len(df)
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        # -------------------------
        # Train KMeans
        # -------------------------
        kmeans = KMeans(
            n_clusters=best_k,
            init="k-means++",
            random_state=42,
            n_init=10
        )

        df["cluster"] = kmeans.fit_predict(scaled_features)

        # -------------------------
        # Cluster statistics
        # -------------------------
        cluster_summary = (
            df.groupby("cluster")
            .agg({
                "spending_score": "mean",
                "annual_income": "mean"
            })
        )

        cluster_mapping = {}

        for cluster, row in cluster_summary.iterrows():

            avg_spending = row["spending_score"]
            avg_income = row["annual_income"]

            if avg_spending >= 85 and avg_income >= 100000:
                segment = "champions"
            elif avg_spending >= 80:
                segment = "loyal_customers"
            elif avg_spending >= 60:
                segment = "potential_customers"
            elif avg_spending >= 40:
                segment = "average_customers"
            else:
                segment = "budget_customers"

            cluster_mapping[cluster] = segment

        df["customer_segment"] = df["cluster"].map(cluster_mapping)

        # -------------------------
        # Save to database
        # -------------------------
        batch_id = str(uuid.uuid4())
        customers = []

        for _, row in df.iterrows():

            customer = SegmentationResult(
                customer_code=f"CUST-{uuid.uuid4().hex[:8]}",
                customer_name=row["customer_name"],
                spending_score=int(row["spending_score"]),
                annual_income=int(row["annual_income"]),
                cluster=int(row["cluster"]),
                customer_segment=row["customer_segment"],
                upload_batch_id=batch_id,
            )

            customers.append(customer)

        db.add_all(customers)
        db.commit()

        logger.info(
            "Segmentation results saved",
            extra={
                "file_name": file.filename,
                "batch_id": batch_id,
                "total_customers": len(df),
            }
        )

        return {
            "file_name": file.filename,
            "upload_batch_id": batch_id,
            "optimal_clusters": best_k,
            "silhouette_score": round(best_score, 3),
            "total_customers": len(df),
            "segmented_customers": df.to_dict(orient="records")
        }

    except HTTPException as http_error:
        logger.warning(
            "Client error during segmentation",
            extra={
                "file_name": file.filename,
                "status_code": http_error.status_code,
                "detail": http_error.detail,
            }
        )
        raise http_error

    except Exception as e:
        logger.error(
            "Unexpected error during segmentation",
            extra={"file_name": file.filename, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# GET ALL CUSTOMERS
# -------------------------
def get_all_customers_service(
    skip: int,
    limit: int,
    segment: str | None,
    search: str | None,
    sort_by: str | None,
    order: str,
    db: Session
):

    query = db.query(SegmentationResult)

    if segment:
        query = query.filter(
            SegmentationResult.customer_segment == segment
        )

    if search:
        query = query.filter(
            or_(
                SegmentationResult.customer_name.ilike(f"%{search}%"),
                SegmentationResult.customer_code.ilike(f"%{search}%")
            )
        )

    if sort_by:
        column = getattr(SegmentationResult, sort_by)
        if order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    customers = query.offset(skip).limit(limit).all()

    return customers


# -------------------------
# GET CUSTOMER BY CODE
# -------------------------
def get_customer_by_code_service(customer_code: str, db: Session):

    customer = (
        db.query(SegmentationResult)
        .filter(SegmentationResult.customer_code == customer_code)
        .first()
    )

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


# -------------------------
# GET ALL SEGMENTATION RUNS
# -------------------------
def get_all_segmentation_runs_service(db: Session):

    runs = (
        db.query(SegmentationRun)
        .order_by(SegmentationRun.timestamp.desc())
        .all()
    )

    return {
        "total_runs": len(runs),
        "runs": runs
    }


# -------------------------
# CUSTOMER STATISTICS
# -------------------------
def get_statistics_service(db: Session):

    total_customers = (
        db.query(func.count(SegmentationResult.id))
        .scalar()
    )

    average_income = (
        db.query(func.avg(SegmentationResult.annual_income))
        .scalar()
    )

    average_spending_score = (
        db.query(func.avg(SegmentationResult.spending_score))
        .scalar()
    )

    customers_per_segment = (
        db.query(
            SegmentationResult.customer_segment,
            func.count(SegmentationResult.id)
        )
        .group_by(SegmentationResult.customer_segment)
        .all()
    )

    return {
        "total_customers": total_customers,
        "average_income": round(average_income, 2),
        "average_spending_score": round(average_spending_score, 2),
        "customers_per_segment": {
            segment: count
            for segment, count in customers_per_segment
        }
    }