# FastAPI Customer Segmentation API

A production-style **machine learning pipeline wrapped inside a secure backend API**. Upload customer data, automatically segment it using K-Means clustering, persist the results to PostgreSQL, and retrieve business intelligence through JWT-protected endpoints — all over HTTP.

This is not a notebook experiment. The ML model is fully operationalized into a real backend service, meaning any external application can interact with the clustering pipeline through standard API requests, exactly the way production SaaS systems do.

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Core Architecture](#core-architecture)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [API Reference](#api-reference)
- [ML Pipeline Deep Dive](#ml-pipeline-deep-dive)
- [Authentication Flow](#authentication-flow)
- [Security](#security)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Overview

Most ML projects live inside Jupyter notebooks — isolated, static, and inaccessible to other systems. This project takes a different approach.

The customer segmentation engine is built as a **live backend service** using FastAPI. The full pipeline — from raw CSV ingestion to cluster prediction to database persistence — is triggered and consumed through HTTP requests, protected by JWT authentication.

What this project demonstrates simultaneously:

- Data preprocessing on real-world business data
- Unsupervised machine learning with K-Means clustering
- Backend API engineering with FastAPI
- Database integration via SQLAlchemy + PostgreSQL
- JWT-based authentication and protected route access
- Production-style modular backend architecture

---

## How It Works

```
User uploads CSV
      │
      ▼
Pandas preprocessing
(cleaning, normalization, feature selection)
      │
      ▼
K-Means clustering (scikit-learn)
(unsupervised grouping by behavior + spend patterns)
      │
      ▼
Cluster interpretation
(High Value / Average Spender / Low Engagement / etc.)
      │
      ▼
Results persisted to PostgreSQL via SQLAlchemy
      │
      ▼
Retrievable through JWT-protected API endpoints
```

---

## Features

### Machine Learning Pipeline

- CSV upload and ingestion via a dedicated API endpoint
- Pandas-based preprocessing: missing value handling, normalization, feature selection
- K-Means clustering via scikit-learn on numerical features (e.g. annual income, spending score)
- Automatic customer grouping based on behavioral and purchasing similarity
- Cluster-to-label interpretation (e.g. High Value, Low Engagement)
- Segmentation results persisted to PostgreSQL for long-term retrieval

### Authentication System

- User signup with bcrypt password hashing
- User login with JWT access token generation
- OAuth2 password bearer flow
- Token verification middleware on protected routes
- Plain text passwords are **never** stored

### Backend Architecture

- Modular FastAPI router structure
- SQLAlchemy ORM models for users and segmentation results
- Dependency injection for database sessions and auth context
- Environment variable based secret management
- Auto-generated Swagger UI and ReDoc documentation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI |
| ML / Data Processing | scikit-learn, pandas, numpy |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT, OAuth2 Password Flow, Passlib, bcrypt |
| Server | Uvicorn |
| Environment | python-dotenv |

---

## Prerequisites

- **Python** 3.10 or higher
- **PostgreSQL** 15 or higher (local or cloud)
- **pip** (comes with Python)
- A tool like **pgAdmin** or **psql** to create the database

---

## Project Structure

```
customer-segmentation-api/
│
├── app/
│   ├── main.py                    # App entry point, router registration
│   ├── database.py                # DB engine, session factory, Base ORM class
│   ├── auth.py                    # Password hashing, JWT creation and decoding
│   │
│   ├── models/
│   │   ├── user_model.py          # Users table ORM model
│   │   └── segmentation_model.py  # Customer segments ORM model (stores cluster results)
│   │
│   └── routes/
│       ├── auth_routes.py         # Signup, login, /me protected route
│       └── segmentation_routes.py # CSV upload, clustering trigger, results retrieval
│
├── .env                           # Secrets — never commit this
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Core Architecture

### `main.py` — Application Entry Point

Initializes the FastAPI app and registers all routers. Uvicorn targets this file on startup.

### `database.py` — Database Configuration

Manages the full SQLAlchemy connection lifecycle.

- Creates the PostgreSQL engine from `DATABASE_URL`
- Configures `SessionLocal` for per-request session management
- Defines the `Base` class that all ORM models inherit from
- Exposes `get_db()` as a FastAPI dependency for session injection into routes

### `auth.py` — Authentication Utilities

Pure utility module — no route logic, only reusable security functions.

- `hash_password(password)` — bcrypt hashing via Passlib
- `verify_password(plain, hashed)` — constant-time comparison
- `create_access_token(data)` — signed JWT with configurable expiry
- `decode_access_token(token)` — decodes and validates, raises `401` on failure

### `user_model.py` — User ORM Model

Defines the `users` table.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key, auto-incremented |
| `username` | String | Unique username |
| `hashed_password` | String | bcrypt hashed password |

### `segmentation_model.py` — Segmentation ORM Model

Defines the `customer_segments` table. Persists K-Means clustering results so that business intelligence is available beyond runtime.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `customer_id` | String / Integer | Reference to the customer record |
| `cluster_label` | Integer | Raw cluster number assigned by K-Means |
| `segment_name` | String | Human-readable label (e.g. High Value) |
| `annual_income` | Float | Feature used in clustering |
| `spending_score` | Float | Feature used in clustering |
| `created_at` | DateTime | Timestamp of segmentation |

### `auth_routes.py` — Authentication Routes

Handles all auth endpoints with database session injection.

### `segmentation_routes.py` — Segmentation Routes

Handles the ML pipeline exposure over HTTP.

- Accepts CSV file upload
- Triggers the preprocessing and clustering pipeline
- Persists results to PostgreSQL
- Returns segmentation output to the client
- Protected — requires valid JWT token

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/fastapi-customer-segmentation-api.git
cd fastapi-customer-segmentation-api
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL Database

```sql
CREATE DATABASE customer_segmentation_db;
```

---

## Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=postgresql://postgres:your_password@localhost/customer_segmentation_db
```

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> `.env` is already listed in `.gitignore`. Never commit it.

---

## Running the Server

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|---|---|
| `http://127.0.0.1:8000` | Base API |
| `http://127.0.0.1:8000/docs` | Swagger UI (interactive) |
| `http://127.0.0.1:8000/redoc` | ReDoc documentation |

---

## API Reference

### Authentication

---

#### `POST /signup`

Register a new user.

**Request Body:**
```json
{
  "username": "aditya",
  "password": "securepassword123"
}
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "username": "aditya"
}
```

---

#### `POST /login`

Authenticate and receive a JWT token.

**Request Body (`application/x-www-form-urlencoded`):**
```
username=aditya&password=securepassword123
```

**Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### `GET /me`

Returns the currently authenticated user. Requires Bearer token.

**Header:**
```
Authorization: Bearer <your_token>
```

**Response `200 OK`:**
```json
{
  "id": 1,
  "username": "aditya"
}
```

**Response `401 Unauthorized`:**
```json
{
  "detail": "Could not validate credentials"
}
```

---

### Customer Segmentation

---

#### `POST /segment`

Upload a CSV file and trigger the K-Means clustering pipeline. Returns segmented customer data with cluster labels.

**Header:**
```
Authorization: Bearer <your_token>
```

**Request:** `multipart/form-data` with a `.csv` file containing customer data.

**Expected CSV columns:**
```
customer_id, annual_income, spending_score, ...
```

**Response `200 OK`:**
```json
{
  "total_customers": 200,
  "clusters_found": 5,
  "segments": [
    {
      "customer_id": 1,
      "annual_income": 75000,
      "spending_score": 82,
      "cluster_label": 2,
      "segment_name": "High Value"
    },
    {
      "customer_id": 2,
      "annual_income": 32000,
      "spending_score": 24,
      "cluster_label": 0,
      "segment_name": "Low Engagement"
    }
  ]
}
```

---

#### `GET /segments`

Retrieve all previously computed segmentation results from PostgreSQL.

**Header:**
```
Authorization: Bearer <your_token>
```

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "segment_name": "High Value",
    "annual_income": 75000,
    "spending_score": 82,
    "created_at": "2024-11-01T10:30:00"
  }
]
```

---

## ML Pipeline Deep Dive

### Stage 1 — CSV Ingestion

The user uploads a raw customer dataset via `POST /segment`. The file is read into a Pandas DataFrame in memory.

### Stage 2 — Preprocessing

Real-world business data is messy. Before clustering can occur, the pipeline:

- Drops rows with missing values
- Selects relevant numerical features (e.g. `annual_income`, `spending_score`)
- Normalizes feature values using min-max or standard scaling so no single feature dominates the distance calculations

### Stage 3 — K-Means Clustering

The cleaned feature matrix is passed to scikit-learn's `KMeans`.

```python
from sklearn.cluster import KMeans

model = KMeans(n_clusters=5, init='k-means++', random_state=42)
model.fit(X_scaled)
labels = model.labels_
```

K-Means is an **unsupervised algorithm** — there are no pre-labeled outputs. Instead, the model:

1. Initializes `k` centroids using `k-means++` for stable convergence
2. Assigns each customer to the nearest centroid by Euclidean distance
3. Recalculates centroids as the mean of each cluster
4. Repeats until cluster assignments stop changing

### Stage 4 — Cluster Interpretation

Raw cluster numbers (0, 1, 2...) are mapped to business-meaningful segment names based on the centroid characteristics:

| Cluster Profile | Segment Label |
|---|---|
| High income, high spend | High Value |
| High income, low spend | Potential |
| Medium income, medium spend | Average Spender |
| Low income, high spend | Impulsive |
| Low income, low spend | Low Engagement |

### Stage 5 — Persistence

Results are written to PostgreSQL via SQLAlchemy so that clustered insights survive beyond the API call and can be queried at any time through `GET /segments`.

---

## Authentication Flow

### Signup
```
POST /signup ──► Hash password (bcrypt) ──► Store in PostgreSQL ──► Return user
```

### Login
```
POST /login ──► Verify password ──► Generate JWT (HS256 + expiry) ──► Return token
```

### Protected Route
```
Request + Bearer token ──► Decode JWT ──► Extract username ──► Fetch user ──► Grant access
```

---

## Security

| Practice | Implementation |
|---|---|
| Password hashing | bcrypt via Passlib |
| Token signing | HS256 JWT with expiry |
| Auth flow | OAuth2 Password Bearer |
| Route protection | FastAPI dependency injection |
| Secret management | `.env` via python-dotenv |
| No plaintext passwords | Hashed immediately on signup |
| ML endpoint protection | JWT required for all segmentation routes |

---

## Roadmap

- [ ] **Dockerization** — Docker Compose for app + PostgreSQL
- [ ] **Alembic migrations** — versioned schema management
- [ ] **Refresh tokens** — short-lived access + long-lived refresh token pair
- [ ] **Role-based access control** — admin vs standard user permissions
- [ ] **Dynamic K selection** — elbow method or silhouette scoring to auto-select optimal clusters
- [ ] **Additional ML models** — DBSCAN, Gaussian Mixture Models for comparison
- [ ] **Cluster visualization endpoint** — return 2D PCA-reduced plot data for frontend rendering
- [ ] **Automated clustering jobs** — scheduled re-segmentation as new data arrives
- [ ] **API testing suite** — pytest + HTTPX for full endpoint coverage
- [ ] **CI/CD pipeline** — GitHub Actions for automated testing and deployment

---

## Author

**Aditya Karmakar**

Backend developer focused on Python, FastAPI, data systems, and AI-powered backend applications.

---

*Not just a model in a notebook — a machine learning pipeline in production.*