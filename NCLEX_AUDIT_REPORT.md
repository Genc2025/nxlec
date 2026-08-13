# NCLEX Commercial Bank Audit

Generated: 2026-08-13T00:38:25.421042+00:00

> Scope: structural/schema/deduplication/ordering audit. This does **not** certify clinical correctness or source licensing.

## Executive summary

- Recognized question rows: **3525**
- Structurally app-ready after exact dedupe: **2999**
- Held for review/duplicate: **526**
- Detected case-study groups: **75** (525 items)
- Exact duplicate stem groups: **20**
- Near-duplicate candidates: **231**

## Source databases

### ngn75 — `nclex ngn bank 75of75 ALL7formats FINAL.db`
- Size: 1,327,104 bytes
- SQLite integrity: `ok`
- Tables:
  - `case_studies` — 75 rows — support/raw
  - `case_study_items` — 525 rows — question-like
  - `categories` — 8 rows — support/raw
  - `standalone_ngn_items` — 0 rows — question-like

### v2 — `nclex question bank v2 inprogress 5.db`
- Size: 4,820,992 bytes
- SQLite integrity: `ok`
- Tables:
  - `categories` — 10 rows — support/raw
  - `category_progress` — 8 rows — support/raw
  - `questions` — 3,000 rows — question-like
  - `topic_fingerprints` — 3,000 rows — support/raw

## Item families

- multiple_choice: **3000**
- other: **150**
- multiple_response: **75**
- matrix: **75**
- highlight: **75**
- cloze: **75**
- bow_tie: **75**

## 2026 Client Needs mapping (structurally app-ready unique items)

- Unmapped: **2999** items; official midpoint target stored: **0.0%**

## Audit issue counts

- UNMAPPED_BLUEPRINT: **3525**
- MISSING_REFERENCE: **525**
- MISSING_ANSWER: **525**
- NEAR_DUPLICATE_CANDIDATE: **462**
- UNMAPPED_ITEM_FORMAT: **150**
- EXACT_DUPLICATE_STEM: **121**
- MISSING_OPTIONS: **75**

## Ordering and app usage

`question_catalog.commercial_order` is a stable catalog order, not an exam sequence. It groups by the 2026 Client Needs framework and keeps inferred NGN case-study item sets together. Commercial tests should sample from the catalog by blueprint weights, rather than simply taking consecutive rows.

## Safety gate

Every normalized item is marked `clinical_verification_status = NOT_VERIFIED`. A structural PASS means the record can be rendered by an app; it does not mean the medical answer/rationale has been independently verified.
