import io
import pytest


# -------------------------
# SECURITY HEADER TESTS
# -------------------------

def test_security_headers_present(client):
    """Every response must include the required security headers."""
    response = client.get("/")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("cache-control") == "no-store"
    assert response.headers.get("server") == "unknown"


def test_request_id_in_response(client):
    """Every response must include an X-Request-ID header."""
    response = client.get("/")
    assert "x-request-id" in response.headers
    # Verify it looks like a UUID
    request_id = response.headers["x-request-id"]
    assert len(request_id) == 36
    assert request_id.count("-") == 4


# -------------------------
# AUTH PROTECTION TESTS
# -------------------------

def test_upload_requires_auth(client, sample_csv_content):
    """The upload endpoint must reject unauthenticated requests."""
    response = client.post(
        "/upload-csv",
        files={"file": ("customers.csv", io.BytesIO(sample_csv_content), "text/csv")}
    )
    assert response.status_code == 401


def test_customers_requires_auth(client):
    """The customers endpoint must reject unauthenticated requests."""
    response = client.get("/customers")
    assert response.status_code == 401


def test_high_value_customers_requires_auth(client):
    """The high-value customers endpoint must reject unauthenticated requests."""
    response = client.get("/high-value-customers")
    assert response.status_code == 401


# -------------------------
# FILE VALIDATION TESTS
# -------------------------

def test_rejects_non_csv_extension(client, auth_headers):
    """Files with non-CSV extensions must be rejected."""
    response = client.post(
        "/upload-csv",
        files={"file": ("malicious.exe", io.BytesIO(b"some content"), "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Only .csv files" in response.json()["detail"]


def test_rejects_wrong_mime_type(client, auth_headers):
    """Files with wrong MIME types must be rejected even with .csv extension."""
    response = client.post(
        "/upload-csv",
        files={"file": ("data.csv", io.BytesIO(b"some content"), "application/octet-stream")},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_rejects_empty_file(client, auth_headers):
    """Empty files must be rejected."""
    response = client.post(
        "/upload-csv",
        files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()