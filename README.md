# gab_bookstore_api

This document provides a comprehensive guide to configuring, running and using the Bookstore API (gab_bookstore_api). It is intended as a production‑ready technical README with code examples and step‑by‑step instructions.

---

## 1. Environment Variable Configuration (.env)

To run with Docker Compose, create three environment files inside `docker/local/`:

- **python_api.env** (API)
- **python_admin.env** (Admin)
- **postgres.env** (Database)

> **Important:**  
> - Add all of them to `.gitignore`.  
> - Keep a `.env.example` with no sensitive values for reference.

### Example: `docker/local/postgres.env`
```env
# Database Settings (Postgres)
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_PORT=
DATABASE_HOST=

# Celery Broker (Redis)
CELERY_BROKER_URL=
```

### Example: `docker/local/python_api.env`
```env
# Django Settings (API)
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=

# Database Settings (Postgres)
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_PORT=
DATABASE_HOST=

# Celery Broker (Redis)
CELERY_BROKER_URL=
```

### Example: `docker/local/python_admin.env`
```env
# Django Settings (Admin)
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=0
DJANGO_SETTINGS_MODULE=

# Database (same values as API)
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_PORT=
DATABASE_HOST=

# Server type
SERVER_TYPE=

# Development config (e.g. debug toolbar)
DEBUG_TOOLBAR=
```

- **`DJANGO_SETTINGS_MODULE`** chooses which settings file to load.  
- **`SERVER_TYPE`** controls routing (API vs Admin).  
- The `POSTGRES_*` variables **must** be identical for `database`, `api`, and `admin` services.

---

## 2. Installing Docker & Docker Compose

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
# Optional: run Docker without sudo
sudo usermod -aG docker $USER
# Log out / log back in after adding yourself to the group
docker compose version
```

### Windows
1. Install **Docker Desktop** (includes Engine + Compose).  
2. Enable WSL2 or Hyper‑V as prompted by the installer.  
3. Verify installation:
```powershell
docker --version
docker compose version
```

> **Note:** This project uses the new `docker compose` (plugin v2). The legacy `docker‑compose` Python package still exists but should be avoided.

---

## 3. Running the Application with Docker Compose

1. **Build images** (project root):
   ```bash
   docker compose build
   ```

2. **Start containers**:
   ```bash
   docker compose up
   ```
   - `database` service (PostGIS)  
   - `redis` service  
   - `api` service (Django API, port 8000)  
   - `admin` service (Django Admin, port 9000)  
   - `celery`, `celery-beat`, `flower` (optional)

3. **Detached mode**:
   ```bash
   docker compose up -d
   ```

4. **Smoke test**:  
   - Swagger UI: http://localhost:8000/swagger/  
   - Django Admin: http://localhost:9000/admin/  
   - Flower: http://localhost:5555/

5. **Stop & remove containers**:
   ```bash
   docker compose down
   ```

> **Troubleshooting tips:**  
> - Run `docker compose logs <service>` if something fails.  
> - Double‑check your `.env` files for typos (no quotes).  
> - On Windows verify firewall rules and WSL2 integration.

---

## 4. JWT Authentication Flow (`/api/v1/auth/login/`)

The API relies on **djangorestframework‑simplejwt**.

### 4.1 Login
- **Endpoint:** `POST /api/v1/auth/login/`
- **Request Body**:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- **Response (200)**:
  ```json
  {
    "refresh": "<refresh_token>",
    "access":  "<access_token>"
  }
  ```
- **Usage**:
  ```http
  Authorization: Bearer <access_token>
  ```

### 4.2 Refresh Token
- **Endpoint:** `POST /api/v1/auth/refresh/`
- **Body**:
  ```json
  { "refresh": "<refresh_token>" }
  ```

### 4.3 Blacklist (Logout)
- **Endpoint:** `POST /api/v1/auth/blacklist/`
- **Body**:
  ```json
  { "refresh": "<refresh_token>" }
  ```

### 4.4 Swagger UI
1. Open `/swagger/`.  
2. Log in via `POST /auth/login/`.  
3. Click **Authorize**, paste `Bearer <access>`.

---

## 5. User System

The model `users.models.User` extends `AbstractUser` and adds one field:

- **`user_type`** (`CharField`):  
  - `"client"` (default)  
  - `"staff"`

- **`is_staff`** (standard Django) controls Admin access and permissions.

### 5.1 Creating Users
- **Endpoint:** `POST /api/v1/auth/create/`
- **Body**:
  ```json
  {
    "username": "new_user",
    "password": "password",
    "user_type": "client"  // optional
  }
  ```
- **Responses**:
  - `201 Created` → user created  
  - `200 OK` → already existed (`{"detail":"User already exists","id":<id>}`)

> **Permissions:**  
> - Anyone may create **client** users.  
> - To create **staff**, set `is_staff` manually (Admin panel).

---

## 6. Books API – Routes & Behaviour

Prefix: `/api/v1/books/books/`

### 6.1 List Books (GET)
- **GET** `/api/v1/books/books/`  
- **Access:** public  
- **Cache:** 1 hour  
- **Response 200**:
  ```json
  [
    {
      "id": 1,
      "isbn": "9780007458424",
      "title": "The Hobbit",
      "author": "J. R. R. Tolkien",
      "description": "...",
      "published_date": "2012-06-01",
      "cover_thumbnail": "...",
      "publisher": "...",
      "page_count": 368,
      "copies": 1
    }
  ]
  ```

### 6.2 Retrieve Book (GET)
- **GET** `/api/v1/books/books/{id}/`  
- **Access:** public  
- **Response 200**: book object or `404 Not Found`.

### 6.3 Create Book (POST)
- **POST** `/api/v1/books/books/`  
- **Access:** **staff**  
- **Minimal body**:
  ```json
  { "isbn": "9780007458424" }
  ```
- **Enrichment:** Google Books is queried to fill missing fields.  
- **Response 201**: created object  
- **Errors**:  
  - `400 Bad Request` (invalid ISBN or title not found)  
  - `403 Forbidden` (not staff)

### 6.5 Delete Book (DELETE)
- **DELETE** `/api/v1/books/books/{id}/`  
- **Access:** **staff**  
- **Response 204**: no content.

### 6.6 Borrow Book (POST)
- **POST** `/api/v1/books/books/{id}/borrow/`  
- **Access:** **client** (authenticated)  
- **Business logic:**  
  - Atomically decrement `copies`.  
  - Create `Borrow` with `due_date = today + 14 days`.  
- **Response 201**: borrow data  
- **Errors**:  
  - `400 Bad Request` (no copies left)  
  - `401/403`

### 6.7 Return Book (POST)
- **POST** `/api/v1/books/books/{id}/return_it/`  
- **Access:** **client**  
- **Business logic:**  
  - Mark `Borrow` as `returned`.  
  - Increment book `copies`.  
- **Response 200**: updated borrow data  
- **Errors**:  
  - `400 Bad Request` (no active borrow)  
  - `401/403`

---

## 7. Seed Data

- Run `docker compose exec api python manage.py populate_book` – a custom command that populates seed data using Faker.  
- Already included in the initial migration.

---

## 8. Pagination

The API supports limit‑offset pagination. The default page size is **20** items and can be overridden with `?limit=` and `?offset=`.

---


---

## 9. Automated Test Suite

The project ships with an extensive pytest/Django test suite covering **authentication**, **business logic** and **infrastructure helpers**.  
Running `pytest` (or `docker compose run --rm api python manage.py test`) should yield all tests passing.

| Area | Test focus | Key assertions |
|------|------------|----------------|
| **Auth JWT** (`tests/test_auth_jwt.py`) | Login, refresh, token‑protected routes, staff‑only book creation | `401/403/200` status codes, presence of `access` / `refresh` tokens |
| **Book CRUD** (`tests/test_book_crud.py`) | List, create, delete books | Public access to list, staff restriction for create/delete, DB side‑effects |
| **Borrow / Return** (`tests/test_borrow_return.py`) | Borrowing and returning flow | Successful borrow, 404 on non‑existent book, borrow → return lifecycle |
| **Caching & Enrichment** (`tests/test_caching_enrichment.py`) | Google Books enrichment, Redis caching | Single external call, correct enrichment mapping, error branch when enrichment fails |
| **Factory sanity** (`tests/test_factories.py`) | Factories for User, Staff, Book, Borrow | Object creation, password hashing, field defaults, future‑dated due dates |

**Quick start**

```bash
# run in API container
docker compose run --rm api python manage.py test
# or locally
pytest -q
```

A green test run ensures:

* JWT flow works end‑to‑end.
* Business rules around borrowing & copies remain intact.
* External API calls are cached and gracefully handled.
* Model factories stay valid as the schema evolves.

**Tip:** add `--cov=.` to see coverage metrics.


---

## 10. Data Enrichment & Performance

### 10.1 Google Books Enrichment

When a **staff** user creates a book with only an ISBN, the serializer invokes
`fetch_google_books_info(isbn)` to pull metadata from the public **Google Books API**.

```python
@redis_cached(ttl=60 * 60 * 24 * 7)  # 7 days
def fetch_google_books_info(isbn: str) -> dict[str, Any]:
    """Return a dict with title / author / cover / etc., or {} if not found."""
```

* **Caching:** Results are stored in Redis for **7 days**, shrinking latency and
  external quota usage. A miss or API error returns `{}` so the request can be
  rejected gracefully with `400 Bad Request`.
* **Fields included**: `title`, `author(s)`, `description`, `published_date`,
  `publisher`, `page_count`, `cover_thumbnail`.

### 10.2 Query Optimisation

To keep response times low as data grows, the project follows two rules:

| Pattern | Usage example | Benefit |
|---------|---------------|---------|
| `select_related()` | `Borrow.objects.select_related("user", "book")` | Joins FK rows in one query (no N+1) when the relation is **one‑to‑one / many‑to‑one** |
| `prefetch_related()` | `Book.objects.prefetch_related("borrow_set")` | Batches extra queries for **reverse FK / many‑to‑many** relations |

> **Tip:** add `django‑debug‑toolbar` in `DEBUG=True` to verify query counts.

### 10.3 Consistency with `transaction.atomic`

Operations that modify multiple tables (e.g. **borrow / return**) run inside
`@transaction.atomic` blocks. If any step fails (e.g. no copies left),
the entire transaction rolls back, ensuring **copies** and **Borrow** rows
never drift out of sync.

```python
from django.db import transaction

@transaction.atomic
def borrow_book(user: User, book: Book) -> Borrow:
    book.copies = F("copies") - 1
    book.save(update_fields=["copies"])
    return Borrow.objects.create(user=user, book=book, due_date=now()+timedelta(days=14))
```

Unit tests in **`tests/test_borrow_return.py`** assert that the book copy
count and borrow lifecycle remain correct under valid and edge‑case paths.

### Final Notes

- **ISBN Validation:** only `unique`; no checksum validation.  
- **Google Books Cache:** results are kept in Redis for **7 days**.  
- **Page Cache:** list & detail endpoints cached in Redis for **1 hour**.  
- **Examples:** use Swagger UI at `/swagger/` to exercise all endpoints.