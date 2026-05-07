# The Paper Project — Backend API

**Subject:** Internet Technologies (Practical)  
**Semester:** II  
**Project Title:** The Paper Project — Campus Stationery Shop  
**Submitted By:** Lakshya  
**Repository Component:** Backend (REST API)

---

## 1. Introduction

This document describes the backend component of *The Paper Project*, a full-stack web application developed as a semester end-term project. The backend is a RESTful API built using **Python (Flask)** that manages product inventory and customer orders for a campus stationery shop. It connects to a **Supabase (PostgreSQL)** cloud database and is consumed by a vanilla HTML/CSS/JavaScript frontend.

---

## 2. Objective

The objective of this backend is to:

- Expose a clean REST API that the frontend can consume via HTTP requests.
- Manage stationery products (create, read, update, delete).
- Record and persist customer checkout orders.
- Act as the single source of truth for all product data, replacing any client-side hardcoding.

---

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Programming language |
| Flask | Web framework for building the REST API |
| flask-cors | Handles Cross-Origin Resource Sharing (CORS) for browser requests |
| Supabase | Cloud-hosted PostgreSQL database + client SDK |
| supabase-py | Python client library to interact with Supabase |
| python-dotenv | Loads environment variables from a `.env` file |
| Gunicorn | Production-grade WSGI server |

---

## 4. System Architecture

The backend sits between the frontend (browser) and the database (Supabase). All data passes through the Flask API — the frontend never talks to the database directly.

```
┌─────────────────────────────┐
│  Frontend (Browser)         │
│  HTML / CSS / JavaScript    │
│  fetch() API calls          │
└────────────┬────────────────┘
             │ HTTP Requests (JSON)
             ▼
┌─────────────────────────────┐
│  Flask REST API             │
│  app.py — port 5001 (dev)   │
│  Gunicorn (production)      │
│  CORS enabled via           │
│  flask-cors                 │
└────────────┬────────────────┘
             │ supabase-py SDK
             ▼
┌─────────────────────────────────────────┐
│   Supabase (PostgreSQL)                 │
│   ┌──────────────┐  ┌───────────────┐   │
│   │   products   │  │  order_table  │   │
│   └──────────────┘  └───────────────┘   │
└─────────────────────────────────────────┘
```

### How it works:

1. The frontend sends an HTTP request (e.g., `GET /products`) to the Flask API.
2. Flask receives the request, validates input where necessary, and calls the Supabase SDK.
3. Supabase executes the query on the PostgreSQL database and returns data.
4. Flask formats the result as a JSON response and sends it back to the frontend.
5. The frontend renders the data on screen.

---

## 5. Project File Structure

```
backend-PT/
│
├── app.py            # Main application file — all route handlers defined here
├── data.sql          # SQL reference notes for database schema
├── requirements.txt  # List of Python packages required to run the project
├── .env              # Environment variables (not committed to version control)
├── .gitignore        # Specifies files to exclude from Git
└── .venv/            # Python virtual environment (not committed)
```

---

## 6. Database Schema

The project uses two tables hosted on Supabase.

### Table 1: `products`

Stores all stationery items available in the shop.

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | integer | Primary Key, Auto-increment | Unique product identifier |
| `title` | text | NOT NULL | Name of the product |
| `price` | float | Must be > 0 | Price in ₹ |
| `rating` | float | NOT NULL | Product rating out of 5 |
| `thumbnail` | text | Optional | URL of product image |

> If `thumbnail` is not provided when creating a product, a default placeholder image URL is used automatically.

### Table 2: `order_table`

Stores customer orders placed during checkout.

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | integer | Primary Key, Auto-increment | Unique order identifier |
| `name` | text | NOT NULL | Customer's name |
| `room_no` | text | NOT NULL | Customer's room number |
| `building_number` | text | NOT NULL | Customer's hostel/building |
| `order_items` | jsonb | NOT NULL | JSON array of items in the order |
| `payable_amount` | float | Defaults to 0 | Total amount payable |

---

## 7. API Endpoints

The base URL for all endpoints:
- **Development:** `http://localhost:5001`
- **Production:** `https://backend-pt-nr2g.onrender.com`

---

### 7.1 Health Check

**`GET /`**

Checks if the server is running.

**Response:**
```json
{ "status": "App is running..." }
```

---

### 7.2 Get All Products

**`GET /products`**

Fetches the complete list of products from the database.

**Response (200 OK):**
```json
{
  "products": [
    { "id": 1, "title": "Fountain Pen", "price": 1299.0, "rating": 4.5, "thumbnail": "https://..." }
  ]
}
```

---

### 7.3 Add a Product

**`POST /products`**

Creates a new product in the database.

**Request Body (JSON):**
```json
{
  "title": "Notebook",
  "price": 150.0,
  "rating": 4.2,
  "thumbnail": "https://example.com/notebook.jpg"
}
```

- `title` — required
- `price` — required, must be greater than 0
- `rating` — required
- `thumbnail` — optional (defaults to placeholder image)

**Response (201 Created):**
```json
{ "product": { "id": 5, "title": "Notebook", ... } }
```

---

### 7.4 Update a Product

**`PATCH /products/<id>`**

Updates one or more fields of an existing product.

**Request Body (JSON) — all fields optional:**
```json
{
  "title": "Premium Notebook",
  "price": 199.0
}
```

**Response (200 OK):**
```json
{ "message": "Product updated successfully", "data": [...] }
```

**Response (404 Not Found)** if the product ID does not exist.

---

### 7.5 Delete a Product

**`DELETE /products/<id>`**

Deletes a product permanently from the database.

**Response (200 OK):**
```json
{ "message": "Product deleted successfully", "data": [...] }
```

**Response (404 Not Found)** if the product ID does not exist.

---

### 7.6 Checkout / Place Order

**`POST /checkout`**

Saves a customer's order to the `order_table`.

**Request Body (JSON):**
```json
{
  "name": "Lakshya",
  "room_no": "204",
  "building_number": "B3",
  "order": [
    { "id": 1, "title": "Fountain Pen", "price": 1299 }
  ],
  "payable_amount": 1299.0
}
```

All fields except `payable_amount` are required.

**Response (201 Created):**
```json
{ "message": "Order saved successfully", "data": [...] }
```

---

## 8. How It Connects to the Frontend

The frontend is a vanilla HTML/CSS/JavaScript application (three static HTML pages). It does **not** use any framework — all API calls are made using the browser's built-in `fetch()` function.

### Connection Flow

| Frontend Page | User Action | API Call Made |
|---|---|---|
| `index.html` | Page loads | `GET /products` — loads all products into the catalogue |
| `index.html` | Admin clicks Delete | `DELETE /products/<id>` — removes the product |
| `index.html` | User submits checkout | `POST /checkout` — saves the order |
| `add-product.html` | Admin submits add form | `POST /products` — creates a new product |
| `edit-product.html` | Page loads | `GET /products` — fetches product data to pre-fill the form |
| `edit-product.html` | Admin submits edit form | `PATCH /products/<id>` — saves changes |

### CORS

Since the frontend and backend run on different origins (different ports locally, different domains in production), the browser enforces CORS. The `flask-cors` library is used to allow the frontend to communicate with the API:

```python
from flask_cors import CORS
CORS(app)   # Allows all origins (suitable for development)
```

For production, this should be restricted to the specific frontend domain.

---

## 9. Environment Configuration

Sensitive credentials are stored in a `.env` file and loaded at runtime using `python-dotenv`. This file is excluded from version control via `.gitignore`.

**`.env` format:**
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
```

These variables are accessed inside `app.py` as:
```python
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

---

## 10. How to Run the Project Locally

### Prerequisites
- Python 3.x installed
- A Supabase project with `products` and `order_table` tables created

### Steps

```bash
# Step 1 — Clone the repository and navigate to the backend folder
cd backend-PT

# Step 2 — Create a virtual environment
python3 -m venv .venv

# Step 3 — Activate the virtual environment
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# Step 4 — Install required packages
pip install -r requirements.txt

# Step 5 — Create the .env file with your Supabase credentials
# (See Section 9 above)

# Step 6 — Start the development server
python app.py
# Server will start at → http://localhost:5001
```

### Production Deployment (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

---

## 11. Conclusion

The backend for *The Paper Project* demonstrates the practical application of RESTful API design, cloud database integration, and full-stack communication between a Python server and a browser-based frontend. The use of Supabase as a managed PostgreSQL backend eliminates the need to host a separate database server, while Flask's simplicity keeps the codebase minimal and easy to understand.
