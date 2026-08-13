# NCLEX Commercial Bank Audit — Corrected Merge

Generated: 2026-08-13T00:45:36.515813+00:00

## Result

- Core MCQ source rows: **3,000**
- Active unique core MCQ after exact-stem dedupe: **2,999**
- NGN case studies: **75**
- NGN practice items: **525** (7 formats per case)
- NGN simulation items: **450** (6 per case)
- Stand-alone NGN items currently present: **0**
- Unified catalog rows: **3,525**
- Final SQLite integrity: **ok**

## Core blueprint distribution

| Category | Core | Core % | Range | Midpoint | NGN cases | NGN items |
|---|---:|---:|---:|---:|---:|---:|
| Management of Care | 540 | 18.00% | 15-21% | 18% | 6 | 42 |
| Safety & Infection Prevention and Control | 390 | 13.00% | 10-16% | 13% | 4 | 28 |
| Health Promotion and Maintenance | 270 | 9.00% | 6-12% | 9% | 2 | 14 |
| Psychosocial Integrity | 270 | 9.00% | 6-12% | 9% | 5 | 35 |
| Basic Care and Comfort | 270 | 9.00% | 6-12% | 9% | 2 | 14 |
| Pharmacological and Parenteral Therapies | 480 | 16.00% | 13-19% | 16% | 5 | 35 |
| Reduction of Risk Potential | 360 | 12.00% | 9-15% | 12% | 3 | 21 |
| Physiological Adaptation | 420 | 14.00% | 11-17% | 14% | 48 | 336 |

## Exact deduplication

- Exact core stem groups: **1**
- Groups: `[[1310, 2073]]`
- Duplicate source rows remain in `core_questions`; duplicates are `active=0` and point to `duplicate_of_uid`.
- NGN stems are **not** deduplicated across case studies because a generic stem can have different meaning under different case context.

## Ordering semantics

1. `unified_catalog.catalog_order` is a stable admin/import order: pool → Client Needs rank → case/sequence or source ID.
2. It is **not** the exam delivery order.
3. Core tests should be sampled using the blueprint weights/ranges stored in `test_blueprint_2026`.
4. NGN simulation keeps each selected case together and uses six items per case. All seven source formats remain available in practice mode.

## Important commercial gates

- Homepage-only core source URLs flagged for traceability review: **1,690**.
- All source rows carry an internal `verified` flag, but the merged DB deliberately labels independent clinical status as `NOT_VERIFIED` until answer/rationale review is performed independently.
- NGN `extended_drag_drop` and `bowtie` source scoring rules are flagged for scoring-model review before claiming exact NCLEX scoring behavior.
- Stand-alone NGN pool has **0** items, so the current bank should not yet be marketed as a complete replication of every current clinical-judgment delivery component.
- IP/licensing review remains required before commercial publication; source attribution is not the same as permission to reproduce copyrighted material.

## Release status

**STRUCTURALLY_MERGED__CLINICAL_AND_IP_REVIEW_REQUIRED**
