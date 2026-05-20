from fastapi import APIRouter, UploadFile, File
import pandas as pd
from sklearn.cluster import KMeans

router = APIRouter()

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    features = df[["spending_score", "annual_income"]]

    kmeans = KMeans(n_clusters=3, random_state=42)

    df["cluster"] = kmeans.fit_predict(features)

    return {
        "filename": file.filename,
        "total_customers": len(df),
        "segmented_customers": df.to_dict(orient="records")
    }