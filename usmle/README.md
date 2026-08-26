# Independent USMLE Step 1 Bank

Authoritative production database: `data/usmle-step1.db`.

The production workflow uses fresh isolated model executions for Author, blind Auditor Pass A, and Auditor Pass B. The Author and Auditor use different model families. Each execution receives a unique context namespace and no session resume. The model executions have only web-search/web-fetch tools and an allowlist of official examination and U.S. government domains; they have no file, shell, GitHub MCP, or repository-reading tools.

Only the deterministic `TRUSTED_IMPORTER` subprocess can insert `PRODUCTION_READY`. Frozen candidates, blind audits, evidence audits, decisions, and hash-chained history are immutable in SQLite through no-update/no-delete triggers. Rejections remain preserved. Production count is always queried directly from SQLite, never inferred from IDs.

NPOST is outside this pipeline and must never be accessed or modified.
