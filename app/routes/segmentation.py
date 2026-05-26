from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
from sklearn.cluster import KMeans

from app.dependencies import get_db
from app.models.segmentation_model import SegmentationResult

router = APIRouter()


@router.post("/upload-csv")
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:

        df = pd.read_csv(file.file)

        required_columns = ["spending_score", "annual_income"]

        # Check if required columns exist
        for column in required_columns:
            if column not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required column: {column}"
                )

        # Remove rows with missing values
        df = df.dropna(subset=required_columns)

        # Convert columns to numeric
        for column in required_columns:
            try:
                df[column] = pd.to_numeric(df[column])

            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{column}' contains invalid non-numeric values"
                )

        # Check if dataframe became empty after cleaning
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="No valid data remaining after preprocessing"
            )

        # Select features for clustering
        features = df[["spending_score", "annual_income"]]

        # Create KMeans model
        kmeans = KMeans(n_clusters=3, random_state=42)

        # Generate cluster predictions
        df["cluster"] = kmeans.fit_predict(features)

        # Calculate average spending score for each cluster
        cluster_averages = (
            df.groupby("cluster")["spending_score"]
            .mean()
            .sort_values()
        )

        # Map cluster numbers to business-friendly labels
        cluster_mapping = {
            cluster_averages.index[0]: "low_value",
            cluster_averages.index[1]: "mid_value",
            cluster_averages.index[2]: "high_value"
        }

        # Create readable customer segment column
        df["customer_segment"] = df["cluster"].map(cluster_mapping)

                # Save customers into PostgreSQL
        for _, row in df.iterrows():

            customer = SegmentationResult(
                customer_name=row["customer_name"],
                spending_score=int(row["spending_score"]),
                annual_income=int(row["annual_income"]),
                cluster=int(row["cluster"]),
                customer_segment=row["customer_segment"]
            )

            db.add(customer)

        db.commit()

        return {
            "filename": file.filename,
            "total_customers": len(df),
            "segmented_customers": df.to_dict(orient="records")
        }

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    