# Engineering Decisions

## 1. Assumptions Made

**Data Quality & Source Reliability**: Assumed the Parquet file contains mostly clean financial data from reputable sources, with occasional null/NaN values that need sanitization. The `raw_response_id` field is assumed to be truly unique across all data sources and time periods.

**Ingestion Frequency**: Designed for periodic batch ingestion (every 15 minutes) rather than real-time streaming, assuming data sources provide daily/weekly updates rather than high-frequency ticks.

**Testing** So for testing I chose pytest as it is the industry standard and it allows me to write standard assertions leading to more cleaner, maintanable code.

**Celery** I chose Celery over a simple Cron job because it allows for retries, visibility into failure states, and scales better if we decide to add more scrapers in the future.

**Redis** Redis was chosen for the /latest endpoint to offload read-heavy traffic from PostgreSQL. I implemented a cache-aside pattern where the ingest worker invalidates keys upon new data arrival to ensure strong consistency.

**Environment**: Assumed Docker-based deployment with PostgreSQL and Redis available. Local development uses SQLite fallback but production requires PostgreSQL.

**Data Volume**: Expected 10K-100K records initially, growing to millions over time. Chose batch processing over individual inserts for efficiency.

## 2. Idempotency Strategy

The ingestion worker uses a **transaction-level upsert pattern** with `raw_response_id` as the unique constraint:

- **Uniqueness**: Each record is uniquely identified by `raw_response_id` (UUID from source system)
- **Conflict Resolution**: Uses Django's `bulk_create()` with `update_conflicts=True` and `unique_fields=['raw_response_id']`
- **Update Fields**: When duplicates are found, updates `sys_ingested_ts` (system timestamp) and `raw_data_snapshot` (audit trail)
- **Data Integrity**: Maintains full history - same effective date can have multiple versions with different ingestion timestamps
- **Atomicity**: Entire batch wrapped in database transaction - either all records of that batch succeed or all fail

This handles: duplicate ingestion attempts, source data corrections, and maintains complete audit trail while preventing data loss.

## 3. One Tradeoff Made Consciously

**Chose PostgreSQL over TimescaleDB**: Given the 48-hour constraint, I selected standard PostgreSQL with custom indexes rather than TimescaleDB for time-series optimization. PostgreSQL's B-tree indexes on `(provider, rate_type, -effective_date, -sys_ingested_ts)` provide excellent performance for the required queries while avoiding the complexity of learning/setup time for TimescaleDB. The tradeoff: slightly slower time-range queries vs. faster development velocity and simpler deployment.

## 4. One Thing I Would Change With More Time

**Replace polling refresh with WebSocket real-time updates**: The current frontend polls the seed file every 15 minutes for rate changes. With more time, I'd implement WebSocket connections using Django Channels + Redis pub/sub, pushing rate updates instantly to connected clients. This would eliminate unnecessary API calls, reduce server load by ~90%, and provide true real-time user experience for financial data that changes frequently.
