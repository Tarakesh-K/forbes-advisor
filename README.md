# Forbes Advisor - Financial Rates Dashboard

A production-grade financial rates ecosystem designed for scraping, storing, and visualizing 1M+ interest-rate records.

## 🚀 Quick Start (Docker)

The fastest way to get the stack running with all dependencies (PostgreSQL, Redis, Celery).

1.  **Setup Environment**:
    ```bash
    cp .env.example .env
    ```
2.  **Prepare Data**:
    Place your `rates_seed.parquet` file inside the `backend/seeds/` directory.
    *(Create the directory if it doesn't exist: `mkdir -p backend/seeds`)*.
3.  **One-Command Launch**:
    ```bash
    make quick-start
    ```
    *This builds the images, starts containers, runs database migrations, and triggers the automated ingestion worker.*

---

## 🏗️ Technical Stack

* **Backend**: Django REST Framework (Python 3.12)
* **Frontend**: Next.js 14+ (TypeScript, Tailwind, Recharts)
* **Database**: PostgreSQL 15 (Optimized for time-series queries)
* **Processing**: Celery + Redis (Asynchronous ingestion & scheduling)
* **Data Format**: Snappy-compressed Parquet (High-performance columnar storage)

---

## 🛠️ Operational Commands

Use the `Makefile` to simplify common development tasks.

| Command | Description |
| :--- | :--- |
| `make build` | Build all Docker containers |
| `make up` | Start the stack in the background |
| `make quick-start` | Full bootstrap (migrate + seed) |
| `make seed` | Manually trigger the Parquet ingestion worker |
| `make test` | Run the full test suite (Pytest + DRF) |
| `make logs` | Tail logs from the backend and celery worker |
| `make clean` | Stop services and remove database volumes |

---

## 📈 API Overview

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| `/api/rates/latest/` | GET | None | Latest rate per provider (Cached in Redis) |
| `/api/rates/history/` | GET | None | Time-series data for provider + type |
| `/api/rates/ingest/` | POST | Bearer | Authenticated webhook for new rate data |

---

## 🗄️ Documentation & Standards

To understand the engineering judgment behind this implementation:

1.  **[schema.md](schema.md)**: Database indexing strategy, choice of `DecimalField` for precision, and audit trail design.
2.  **[DECISIONS.md](DECISIONS.md)**: Rationale for Celery, Redis caching strategy, and handling 1M row idempotency.

---

## 🔧 Environment Variables

Configure these in your `.env` file:

* `POSTGRES_PASSWORD`: Database authentication.
* `SECRET_KEY`: Django security key.
* `CELERY_BROKER_URL`: Connection string for Redis (`redis://redis:6379/0`).
* `NEXT_PUBLIC_API_URL`: Backend endpoint for the frontend.

---

## 📝 License

MIT License