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

## 🤖 AI Disclosure & Methodology

In alignment with the assessment requirements, this project utilized AI collaboration to accelerate development velocity while maintaining senior-level architectural oversight.

* **Tools Used**: Gemini 1.5 Pro, ChatGPT (GPT-4o), and Claude 3.5 Sonnet.
* **Role of AI**: 
    * **Boilerplate & Templates**: AI was used to generate initial scaffoldings for the `Makefile`, Docker Compose configurations, and standard Django management command templates.
    * **Documentation Shells**: Initial drafts for `TESTING.md` and `DECISIONS.md` were generated to ensure comprehensive coverage of industry standards.
* **Human Oversight (The "Senior" Layer)**:
    * **System Architecture**: The high-level design—including the choice of Celery for async processing, Redis for the caching layer, and the specific database indexing strategy—was architected entirely by the developer.
    * **Logic Refinement**: AI-generated code was manually audited and heavily edited to implement specific business logic, such as the `JSONB` audit trail for raw responses and the specialized Parquet chunking strategy to prevent OOM (Out of Memory) errors during 1M-row ingestion.
    * **Networking & Integration**: Debugging cross-container communication and ensuring strict DRF permission classes were handled manually to ensure production-grade security.

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

1.  **[schema.md](schema.md)**: Database indexing strategy and audit trail design.
2.  **[DECISIONS.md](DECISIONS.md)**: Rationale for Celery, Redis, and idempotency.
3.  **[TESTING.md](TESTING.md)**: Pytest strategy and mocking details.

---

## 🔧 Environment Variables

Configure these in your `.env` file:

* `POSTGRES_PASSWORD`: Database authentication.
* `SECRET_KEY`: Django security key.
* `CELERY_BROKER_URL`: Connection string for Redis.
* `NEXT_PUBLIC_API_URL`: Backend endpoint for the frontend.

---

## 📝 License

MIT License