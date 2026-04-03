# Database Schema Design

## Overview
Single-table design optimized for financial rate data with full audit history and efficient querying patterns.

## Table: rates

### Core Fields
- `rate_id` (UUID, PK): Internal surrogate key for Django ORM
- `provider` (VARCHAR(255)): Data source (e.g., 'federal_reserve', 'bloomberg')
- `rate_type` (VARCHAR(255), indexed): Rate category (e.g., 'fed_funds', 'prime')
- `rate_value` (DECIMAL(10,6)): The actual interest rate value
- `currency` (VARCHAR(10)): Currency code, defaults to 'USD'

### Temporal Fields
- `effective_date` (DATE, indexed): Business date when rate applies
- `ingestion_ts` (TIMESTAMP, indexed): Source system's timestamp
- `sys_ingested_ts` (TIMESTAMP, indexed): When our system ingested the data

### Uniqueness & Audit
- `raw_response_id` (UUID, unique): Source system's unique identifier
- `source_url` (URL): Link to original data source
- `raw_data_snapshot` (JSONB): Complete original record for audit

## Indexes

### Primary Index
- `rate_id` (implicit on PK)

### Functional Indexes
1. **provider_rate_lookup_idx**: `(provider, rate_type, -effective_date, -sys_ingested_ts)`
   - **Purpose**: Latest rate per provider query
   - **Why DESC on dates**: Gets most recent records first
   - **Coverage**: Handles "latest rate for X provider Y type"

2. **Individual field indexes**:
   - `rate_type`: Fast filtering by rate category
   - `effective_date`: Date range queries
   - `ingestion_ts`: Time-window ingestion queries
   - `sys_ingested_ts`: System processing time queries
   - `raw_response_id`: Uniqueness constraint enforcement

## Query Optimizations

### Latest Rate Per Provider
```sql
SELECT DISTINCT ON (provider, rate_type) *
FROM rates
WHERE provider = 'federal_reserve'
ORDER BY provider, rate_type, effective_date DESC, sys_ingested_ts DESC;
```
**Index used**: `provider_rate_lookup_idx` provides perfect ordering.

### Rate Change Over Last 30 Days
```sql
SELECT * FROM rates
WHERE rate_type = 'fed_funds'
  AND effective_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY effective_date DESC;
```
**Index used**: `effective_date` index for range scan.

### Records Ingested In 24-Hour Window
```sql
SELECT * FROM rates
WHERE sys_ingested_ts >= '2024-01-01 00:00:00'
  AND sys_ingested_ts < '2024-01-01 24:00:00';
```
**Index used**: `sys_ingested_ts` for timestamp range filtering.

## Tradeoffs Considered

### Single Table vs. Normalized Design
**Chose**: Single table with JSONB audit field
**Why**: Simpler queries, better performance for read-heavy workload, easier maintenance
**Alternative**: Separate `rate_versions` table would require JOINs for common queries

### UUID vs. Auto-Increment PK
**Chose**: UUID for `rate_id` (Django default)
**Why**: Distributed system compatibility, no collision risks
**Tradeoff**: Slightly larger storage vs. simpler integer keys

### Separate Timestamps
**Design**: `ingestion_ts` (source time) vs. `sys_ingested_ts` (our time)
**Benefit**: Audit trail shows when source published vs. when we processed
**Use case**: Detect ingestion delays or backdated source data

### No Partitioning
**Decision**: No table partitioning initially
**Rationale**: Expected data volume (millions of rows) fits in single table
**Future**: Could partition by `effective_date` if volume grows significantly
