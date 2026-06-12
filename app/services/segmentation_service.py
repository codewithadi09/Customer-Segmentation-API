import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from app.models.segmentation_model import SegmentationResult


# -------------------------
# Determine optimal K
# -------------------------
def determine_best_k_using_silhouette_score(
    scaled_features
):

    best_k = 2
    best_score = -1

    for k in range(2, 9):

        model = KMeans(
            n_clusters=k,
            init="k-means++",
            random_state=42,
            n_init=10
        )

        clusters = model.fit_predict(
            scaled_features
        )

        score = silhouette_score(
            scaled_features,
            clusters
        )

        if score > best_score:

            best_score = score
            best_k = k

    return best_k, best_score


# -------------------------
# Customer Segmentation
# -------------------------
def segment_customers(
    file,
    db: Session
):

    try:

        df = pd.read_csv(file.file)

        required_columns = [
            "customer_name",
            "spending_score",
            "annual_income"
        ]

        missing_columns = [

            column

            for column in required_columns

            if column not in df.columns

        ]

        if missing_columns:

            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        # Remove missing rows
        df = df.dropna(
            subset=required_columns
        )

        # Convert ONLY numeric columns
        numeric_columns = [
            "spending_score",
            "annual_income"
        ]

        for column in numeric_columns:

            try:

                df[column] = pd.to_numeric(
                    df[column]
                )

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

        # -------------------------
        # Feature selection
        # -------------------------
        features = df[
            ["spending_score", "annual_income"]
        ]

        # -------------------------
        # Standardize features
        # -------------------------
        scaler = StandardScaler()

        scaled_features = scaler.fit_transform(
            features
        )

        # -------------------------
        # Find best K
        # -------------------------
        best_k, best_score = (
            determine_best_k_using_silhouette_score(
                scaled_features
            )
        )

        # -------------------------
        # Train KMeans
        # -------------------------
        kmeans = KMeans(
            n_clusters=best_k,
            init="k-means++",
            random_state=42,
            n_init=10
        )

        df["cluster"] = kmeans.fit_predict(
            scaled_features
        )

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

            if (
                avg_spending >= 85
                and avg_income >= 100000
            ):

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

        # Assign labels
        df["customer_segment"] = (
            df["cluster"]
            .map(cluster_mapping)
        )

        # -------------------------
        # Save to database
        # -------------------------
        customers = []

        for _, row in df.iterrows():

            customer = SegmentationResult(

                customer_name=row["customer_name"],

                spending_score=int(
                    row["spending_score"]
                ),

                annual_income=int(
                    row["annual_income"]
                ),

                cluster=int(
                    row["cluster"]
                ),

                customer_segment=row[
                    "customer_segment"
                ]

            )

            customers.append(
                customer
            )

        db.add_all(
            customers
        )

        db.commit()

        return {

            "filename": file.filename,

            "optimal_clusters": best_k,

            "silhouette_score": round(
                best_score,
                3
            ),

            "total_customers": len(df),

            "segmented_customers": df.to_dict(
                orient="records"
            )

        }

    except HTTPException as http_error:

        raise http_error

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -------------------------
# GET ALL CUSTOMERS
# -------------------------
def get_all_customers_service(
    db: Session
):

    customers = (
        db.query(
            SegmentationResult
        )
        .all()
    )

    return {

        "total_customers": len(
            customers
        ),

        "customers": customers

    }


# -------------------------
# HIGH VALUE CUSTOMERS
# -------------------------
def get_high_value_customers_service(
    db: Session
):

    customers = (

        db.query(
            SegmentationResult
        )

        .filter(
            SegmentationResult.customer_segment == "champions"
        )

        .all()

    )

    return {

        "total_customers": len(
            customers
        ),

        "customers": customers

    }


# -------------------------
# GET CUSTOMER BY ID
# -------------------------
def get_customer_by_id_service(
    customer_id: int,
    db: Session
):

    customer = (

        db.query(
            SegmentationResult
        )

        .filter(
            SegmentationResult.id == customer_id
        )

        .first()

    )

    if customer is None:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer