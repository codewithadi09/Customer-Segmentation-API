import io
import pytest


# -------------------------
# CSV UPLOAD TESTS
# -------------------------

def test_upload_csv_success(client, auth_headers, sample_csv_content):
    """A valid CSV upload triggers the pipeline and returns segmentation results."""
    response = client.post(
        "/upload-csv",
        files={"file": ("customers.csv", io.BytesIO(sample_csv_content), "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "optimal_clusters" in data
    assert "silhouette_score" in data
    assert "total_customers" in data
    assert data["total_customers"] == 10
    assert "upload_batch_id" in data


def test_upload_csv_unauthenticated(client, sample_csv_content):
    """Uploading without a token returns 401."""
    response = client.post(
        "/upload-csv",
        files={"file": ("customers.csv", io.BytesIO(sample_csv_content), "text/csv")}
    )
    assert response.status_code == 401


def test_upload_csv_missing_columns(client, auth_headers):
    """A CSV missing required columns returns 400 with a clear message."""
    bad_csv = b"name,age\nAlice,30\nBob,25"
    response = client.post(
        "/upload-csv",
        files={"file": ("bad.csv", io.BytesIO(bad_csv), "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]


def test_upload_wrong_file_type(client, auth_headers):
    """Uploading a non-CSV file returns 400."""
    response = client.post(
        "/upload-csv",
        files={"file": ("data.json", io.BytesIO(b'{"key": "value"}'), "application/json")},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_upload_empty_file(client, auth_headers):
    """Uploading an empty file returns 400."""
    response = client.post(
        "/upload-csv",
        files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_upload_csv_file_too_large(client, auth_headers):
    """Uploading a file over 5MB returns 413."""
    large_content = b"customer_name,spending_score,annual_income\n"
    large_content += b"Alice,85,120000\n" * 400000  # well over 5MB
    response = client.post(
        "/upload-csv",
        files={"file": ("large.csv", io.BytesIO(large_content), "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 413


# -------------------------
# CUSTOMER RETRIEVAL TESTS
# -------------------------

def test_get_customers_authenticated(client, auth_headers, sample_csv_content):
    """Authenticated user can retrieve all customers after an upload."""
    client.post(
        "/upload-csv",
        files={"file": ("customers.csv", io.BytesIO(sample_csv_content), "text/csv")},
        headers=auth_headers
    )
    response = client.get("/customers", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_customers" in data
    assert data["total_customers"] == 10


def test_get_customers_unauthenticated(client):
    """Accessing /customers without a token returns 401."""
    response = client.get("/customers")
    assert response.status_code == 401