import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from limits.storage import MemoryStorage

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.middleware.rate_limit import limiter

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = override_get_db

    # Reset the rate limiter's counter storage before each test
    # so previous test requests don't bleed into the next test
    limiter.reset()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    client.post("/signup", json={
        "username": "testuser",
        "password": "securepassword123"
    })
    return {"username": "testuser", "password": "securepassword123"}


@pytest.fixture
def auth_token(client, registered_user):
    response = client.post("/login", data={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_csv_content():
    return (
        "customer_name,spending_score,annual_income\n"
        "Alice,85,120000\n"
        "Bob,23,45000\n"
        "Charlie,67,78000\n"
        "Diana,91,150000\n"
        "Eve,12,32000\n"
        "Frank,55,67000\n"
        "Grace,78,95000\n"
        "Henry,34,52000\n"
        "Iris,88,130000\n"
        "Jack,19,38000\n"
    ).encode("utf-8")