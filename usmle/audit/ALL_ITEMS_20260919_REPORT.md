# USMLE bank audit — 19 September 2026

**BLOCKED — full clinical re-audit is incomplete. This branch is not ready for production promotion.**

The source snapshot is main commit `0ac9fe92`, database blob `92a3aeb4588fa3a1677c2edf5f79a611fdccd8ed`. SQLite contains 1,635 canonical item rows, Q0001–Q1635, and 1,635 associated reviews. Q1636–Q1640 are staged separately. No questions were added or deleted.

## Completed work

- Screened every canonical row for stored structure, source metadata, explanation fields, evidence bindings and hashes. Both historical review-hash formats were recomputed successfully before repairs.
- Manually compared the original 17 lexical-similarity pairs and the one exact-construct pair. Fourteen pairs are substantive duplicates; 28 records now have a review hold in this branch. Three pairs test distinct constructs; one pair uses a similar scenario for a different diagnostic/localization task.
- Replaced Q0021 option D's invented bacterial-toxin explanation for spongiform change with a real prion-pathology distractor. Updated its dependent explanation and evidence reference.
- Added the verified missing DailyMed SetIDs to Q0667 and Q0669.
- Preserved the exact prior item and review rows for all 30 affected records. New review records are explicitly `BLOCKED_PENDING_FULL_REAUDIT`; prior FINAL claims were not carried forward onto changed payloads.
- Repaired the audit program: hierarchical blueprint paths are retained, direct evidence may support distractor exclusion, option order is not treated as a content defect, missing keys do not crash the audit, and a stored self-hash cannot bypass recomputation. Findings are no longer truncated to 500 items. Automatic checks cannot return a clinical PASS.

## Findings requiring further work

| Finding | Scope |
|---|---:|
| Confirmed semantic duplicate pairs | 14 pairs / 28 items |
| Generic source locators needing exact sections | 299 items |
| Boilerplate difficulty justification needing individual assessment | 1,107 items |
| Examination sources labeled as government sources | 575 items |
| Government-hosted StatPearls material labeled as government-authored | 91 items |

These counts overlap. Missing stored evidence and generic metadata are not proof that a medical answer is wrong. Conversely, a hash or an earlier 10/10 label is not proof that an answer is correct.

Duplicate pairs: Q0009/Q0306, Q0020/Q0317, Q0264/Q0966, Q0744/Q1102, Q0010/Q0403, Q0018/Q0318, Q0797/Q1124, Q0771/Q1065, Q0193/Q0799, Q0703/Q1184, Q0053/Q0791, Q1418/Q1511, Q0263/Q0965, Q0021/Q0323. Their item-specific comparisons are in `ALL_ITEMS_20260919_COVERAGE.json`. Similarity below the scan threshold does not establish originality; all other pairwise semantic relationships remain unadjudicated.

## Evidence for limited corrections

- Q0021: [CDC, Classic Creutzfeldt-Jakob Disease](https://www.cdc.gov/creutzfeldt-jakob/about/index.html), **Overview** and **How it affects your body**, dated January 21, 2026. Supports prion causation and rapid progression. [NIA, What Happens to the Brain in Alzheimer's Disease?](https://www.nia.nih.gov/health/alzheimers-causes-and-risk-factors/what-happens-brain-alzheimers-disease), **Amyloid plaques** and **Neurofibrillary tangles**, supports the retained key. This was a limited correction, not a new full-item certification.
- Q0667: [DailyMed, OCTREOTIDE ACETATE kit](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e5c21813-4714-4f23-be8b-765bd58f63b3), label identity, **12.1 Mechanism of Action** and **12.2 Pharmacodynamics**. SetID `e5c21813-4714-4f23-be8b-765bd58f63b3` was missing as an explicit field.
- Q0669: [DailyMed, GADAVIST](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=3c5101a0-0c7e-4078-8dc3-a57beb9a0e92), label identity and **5.2 Nephrogenic Systemic Fibrosis**. SetID `3c5101a0-0c7e-4078-8dc3-a57beb9a0e92` was missing as an explicit field.

Q1612's canonical text already contains the repaired CDC42–PAK mechanism. No new full revalidation is claimed: a subsequent live PMC request encountered a browser challenge.

## Coverage and remaining gate

**Fully completed live, claim-by-claim clinical re-audits in this run: 0/1,635.** All 1,635 have individual coverage records and are assigned to 33 batches (32 × 50 and a final 35). Every item still requires an independent assessment of the stem, all five options, every numeric/medical assertion, exact supporting passages, a second-answer attack, difficulty, blueprint and objective. The staged five questions also require this review.

The old finalization aggregate is historical and is not a certification of this changed branch. Do not promote this database until the blocked items are repaired and the complete required audit succeeds. This report records substantive initial findings and safe limited corrections; it does not represent completion of the user's requested full audit.

## Clinical corrections — 20 September 2026

Eight additional items were corrected: Q0001, Q0006, Q0012, Q0014, Q0015, Q0032, Q0036 and Q0045. Exact previous rows and reasoned changes are preserved in `CLINICAL_Q0001_Q0050_BEFORE_ROWS_20260920.json` and `CLINICAL_Q0001_Q0050_CORRECTIONS_20260920.json`. There are now 38 held records in the review branch. These specific corrections do not close each item's complete evidence gate. `CONTINUATION_STATE.json` records the remaining work. The full audit is still incomplete.

### Q0001 evidence follow-up

Live NIA review exposed an overstrong inference in Q0001's reasoning chain: preserved daily function does not by itself exclude mild cognitive impairment. Corrected this, replaced the generic difficulty assignment with an explicit easy author estimate, repaired source metadata, and separated obsolete PASS claims from current review status. A same-reviewer adversarial reread and option-by-option review are documented in [the Q0001 record](Q0001_EVIDENCE_FOLLOWUP_20260920.md). No independent blind execution or full certification is claimed; full completion remains 0/1,635 and 38 records remain held.

### Q0002 clinical follow-up

Q0002's key remained correct, but four remote distractors were replaced with verified real mechanisms involving ciliary dynein, alpha-1 antitrypsin, phagocyte NADPH oxidase and lysosomal trafficking. The keyed wording is now CFTR-specific, the generic moderate rating was replaced with an item-specific easy author estimate, and every option is bound to an inspected source and raw-capture hash. See [the Q0002 record](Q0002_CLINICAL_FOLLOWUP_20260920.md). Q0002 is newly held, bringing the review-branch total to 39; no new FINAL pass is claimed.

### Q0003 clinical follow-up

Q0003's key remained pulsatile GnRH, but its invented outline path, age-band mismatch and sources that did not establish pulsatility were corrected. Four real endocrine alternatives now replace generic negations; the exact USMLE 2026 adolescence path, current source dates, raw hashes, and hosted-third-party attribution are stored. See [the Q0003 record](Q0003_CLINICAL_FOLLOWUP_20260920.md). Q0003 is newly held, bringing the review-branch total to 40; no new FINAL pass is claimed.

### Q0004 clinical follow-up

Q0004's HbS-polymerization key remained correct, but its evidence map incorrectly reused sickle-cell citations for four unrelated red-cell mechanisms. Each option now has its own inspected source and raw hash, the low-oxygen mechanism is directly bound to NHLBI, and the exact USMLE 2026 blood-system hierarchy replaces the invented path. See [the Q0004 record](Q0004_CLINICAL_FOLLOWUP_20260920.md). Q0004 is newly held, bringing the review-branch total to 41; no new FINAL pass is claimed.

### Q0005 clinical follow-up

Q0005's G6PD/NADPH key remained correct, but four remote metabolite distractors were replaced with genuine red-cell mechanisms involving pyruvate kinase, membrane proteins, beta-globin synthesis and HbS polymerization. Heinz-body visualization is now stain-specific, every option has a separate inspected source and raw hash, and the exact USMLE 2026 hemolysis path replaces the generic stored hierarchy. See [the Q0005 record](Q0005_CLINICAL_FOLLOWUP_20260920.md). Q0005 is newly held, bringing the review-branch total to 42; no new FINAL pass is claimed.
