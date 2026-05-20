from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "Server is running properly"}