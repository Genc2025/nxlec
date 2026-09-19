# Independent USMLE Step 1 Bank

**Review branch audit status (2026-09-19): BLOCKED.** See [the audit report](audit/ALL_ITEMS_20260919_REPORT.md). The branch contains limited corrections and 30 records held for further review; the full clinical re-audit is incomplete. Do not treat historical FINAL labels as a new certification.

Authoritative production database: `data/usmle-step1.db`.

The production workflow uses fresh isolated model executions for Author, blind Auditor Pass A, and Auditor Pass B. The Author and Auditor use different model families. Each execution receives a unique context namespace and no session resume. The model executions have only web-search/web-fetch tools and an allowlist of official examination and U.S. government domains; they have no file, shell, GitHub MCP, or repository-reading tools.

Only the deterministic `TRUSTED_IMPORTER` subprocess can insert `PRODUCTION_READY`. Frozen candidates, blind audits, evidence audits, decisions, and hash-chained history are immutable in SQLite through no-update/no-delete triggers. Rejections remain preserved. Production count is always queried directly from SQLite, never inferred from IDs.

NPOST is outside this pipeline and must never be accessed or modified.
