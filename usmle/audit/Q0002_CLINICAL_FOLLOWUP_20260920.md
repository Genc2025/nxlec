# Q0002 — clinical and evidence follow-up, 20 September 2026

Status: **BLOCKED_PENDING_FULL_REAUDIT**, not FINAL_QA_PASS. Baseline commit `5d2adc8f`, payload `e1ab2c64d3640a58093f2e31015e88b2e31cfc6f624e451274e7b9c2f6f18f25`.

The key and core mechanism were correct, but four alternatives were remote mechanisms (skeletal-muscle pump activity, ganglioside degradation, iron absorption and biliary copper excretion). They made the answer artificially easy without testing close respiratory/immunologic distinctions. The generic “moderate” difficulty claim was also unsupported. The options are now five real mechanisms: ciliary dynein, alpha-1 antitrypsin, CFTR, phagocyte NADPH oxidase and LYST-dependent lysosomal trafficking. The intended key remains C.

## Evidence reviewed

- [MedlinePlus Genetics — Cystic fibrosis](https://medlineplus.gov/genetics/condition/cystic-fibrosis/), “Description” and “Causes”, last updated July 6, 2021. Supports CF phenotype, chloride-channel function, water movement and thick mucus. Raw capture hash: `b00ff44712ef381f0130e161f6b50b44f18f402449f7b2ceb1d8314fd17ba53d`.
- [NHLBI — Cystic Fibrosis Causes](https://www.nhlbi.nih.gov/health/cystic-fibrosis/causes), “What causes cystic fibrosis?” and “How do CFTR mutations cause cystic fibrosis?”, last updated November 15, 2024. Supports reduced water in mucus and salty sweat. Raw capture hash: `9b051047d67debf63b8f73ae627c68bf08933548b40c69cb4f60adaab02b221f`.
- [MedlinePlus Genetics — Primary ciliary dyskinesia](https://medlineplus.gov/genetics/condition/primary-ciliary-dyskinesia/), “Description” and “Causes”, last updated September 22, 2025. Supports dynein-driven ciliary force and impaired airway clearance. Raw capture hash: `8d6c7de91f5c86d951fc7220f077e51dbd1587255c09c302257449abb0a365ae`.
- [MedlinePlus Genetics — Alpha-1 antitrypsin deficiency](https://medlineplus.gov/genetics/condition/alpha-1-antitrypsin-deficiency/), “Description” and “Causes”, last updated September 15, 2021. Supports loss of neutrophil-elastase restraint and alveolar injury. Raw capture hash: `e70924af821c4fba5dc5f1d4f5bf46da970814d99161babde6977be7ab083da7`.
- [MedlinePlus Genetics — Chronic granulomatous disease](https://medlineplus.gov/genetics/condition/chronic-granulomatous-disease/), “Description” and “Causes”, last updated January 1, 2016. Supports phagocyte NADPH oxidase, superoxide and microbial killing. Raw capture hash: `759610a1ee4a4998f8801f6b56e5fcd0619fa6880bf1d3e068a0a7bf0ace4371`.
- [MedlinePlus Genetics — Chediak-Higashi syndrome](https://medlineplus.gov/genetics/condition/chediak-higashi-syndrome/), “Description” and “Causes”, last updated January 1, 2014. Supports LYST-dependent lysosomal trafficking and immunodeficiency. Raw capture hash: `8e9cab2e151e91d36768d5bd6b3e6245b8201eadb150706745bc1f7f5e935cfb`.
- USMLE Content Outline (2026), Respiratory System → Genetic and developmental disorders → Cystic fibrosis. The Medical Knowledge: Applying Foundational Science Concepts competency and Genetics/Physiology/Biochemistry disciplines remain appropriate. No NCJMM field is present.

The hashes above bind the raw bytes captured by `SOURCE_AVAILABILITY.json`; HTTP success alone was not treated as clinical support. Titles, sections, dates and claims were separately read. SetID is not applicable to non-drug sources.

## Claim, assumption and second-answer review

No numeric threshold, dose, risk, conversion or treatment recommendation occurs in the item. “Several” infections and age 7 are vignette facts, not diagnostic criteria. Sweat chloride is described only as elevated, avoiding an unreferenced cutoff. Pathogenic CFTR variants plus pancreatic malabsorption and recurrent respiratory disease make CF explicit.

Option A can cause recurrent respiratory infections but not elevated sweat chloride or pancreatic insufficiency. B causes emphysema by unopposed elastase, not dehydrated mucus. D causes recurrent bacterial/fungal infection through failed oxidative killing, not CFTR transport failure. E causes recurrent infection but would require lysosomal/granule and pigmentation findings; it does not explain the named CFTR genotype. None is a second defensible answer to the cellular abnormality producing thick secretions.

The keyed wording now specifies **CFTR-mediated** chloride transport in **airway epithelial cells**, avoiding the overbroad implication that all epithelial chloride transport is reduced. An expert can solve this directly from the named gene and sweat result; difficulty is therefore an easy author estimate with two reasoning steps, not a psychometric claim.

Targeted bank screening found other CFTR-containing items at Q1013, Q1262, Q1385, Q1515 and Q1554. Their tasks concern ductal secretion, toxin-driven secretion, or modulator pharmacology rather than the airway-mucus mechanism. Q0548 and Q0755 assess primary ciliary dyskinesia. This candidate review does not prove exhaustive semantic originality, especially for the staged five.

After repair, the same reviewer restarted at the stem and reread every option, rationale, source, objective, blueprint, difficulty and hidden assumption. No further content defect was found in that pass. The README-required isolated different-family author/auditor executions were not performed, so no independent certification is claimed and the record remains blocked.
