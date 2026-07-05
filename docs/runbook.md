# Runbook

## Incident 1: High query latency (P95 > 10s)
- **Check**: Jaeger traces for slow span. Redis memory usage and hit rate. Postgres pg_stat_statements.
- **Remediation**: Flush Redis cache, add db indexes, scale API replicas.

## Incident 2: Evaluation scores degrading
- **Check**: Which metric and pipeline. Recent ingested documents. MLflow for recent fine-tuning jobs.
- **Remediation**: Revert last fine-tuned model, inspect training data quality.

## Incident 3: LLM provider circuit breaker open
- **Check**: `GET /health`. Provider status page.
- **Remediation**: Wait for recovery timeout, or manually reset via `POST /admin/circuit-breaker/reset`.

## Incident 4: Ingestion queue depth > 100
- **Check**: `GET /health` for queue depth. Worker logs for errors.
- **Remediation**: Restart worker containers, clear stuck jobs in Redis.

## Incident 5: Database disk usage > 80%
- **Check**: Which table is growing fastest. Data retention jobs running?
- **Remediation**: Run data retention job manually.
