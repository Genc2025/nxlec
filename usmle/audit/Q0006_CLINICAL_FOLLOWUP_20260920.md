# Q0006 — duplicate resolution and clinical follow-up, 20 September 2026

Status: **BLOCKED_PENDING_FULL_REAUDIT**, not FINAL_QA_PASS. Baseline commit `bf3c12c9`, payload `f83cc8ead31d3dc785db46d7323accf9f85812168ccb86c39dad741a34284e2d`.

Q0006 and Q1111 both asked for the diagnosis of hereditary spherocytosis from an affected father, splenomegaly, jaundice/anemia and spherocytes. This is a confirmed semantic duplicate, not a merely related construct. Q0006 was therefore rewritten rather than deleted or relabeled: it now tests parvovirus B19 transient aplastic crisis in a child with hereditary spherocytosis, using exposure to a slapped-cheek illness, an abrupt hemoglobin decline and profound reticulocytopenia.

## Verified evidence

- [MedlinePlus Genetics — Hereditary spherocytosis](https://medlineplus.gov/genetics/condition/hereditary-spherocytosis/), Description and Causes, updated September 1, 2013; raw SHA-256 `78cd6ffb0c0c749c8ce700acd1a8278af5f9b3d039ef6cf5b90560368505ad8b`.
- [CDC — About Parvovirus B19](https://www.cdc.gov/parvovirus-b19/about/index.html), At a glance, Rashes and Complications, dated December 17, 2025; specifically names hereditary spherocytosis as a blood disorder in which B19 can cause a severe anemia drop; raw SHA-256 `e2766f1db03c965a37f613d5f0d70347ff9890002e7c9c9574ef0a166106f237`.
- Luo Y, Qiu J. [Human parvovirus B19: a mechanistic overview of infection and DNA replication](https://pmc.ncbi.nlm.nih.gov/articles/PMC4470565/), *Future Virology* 2015, Abstract and introductory clinical spectrum; B19V preferentially infects erythroid progenitor cells and causes transient aplastic crisis in high-erythropoiesis states; raw SHA-256 `9cf828c7c3bf5e7170696d628bc4876485483546def8686c6ff1876bd756671c`. This is a third-party article hosted by NCBI, not government-authored content.
- [Merck Manual — Autoimmune Hemolytic Anemia](https://www.merckmanuals.com/professional/hematology/anemias-caused-by-hemolysis/autoimmune-hemolytic-anemia), full review and last update April 2026, Warm antibody hemolytic anemia and Diagnosis; raw SHA-256 `10d6a3700ca4ac106b29f5c640c42307bf84fe45db7611ee115c7c1902316eac`.
- [MedlinePlus Genetics — G6PD gene](https://medlineplus.gov/genetics/gene/g6pd/), Normal Function and G6PD deficiency, updated April 12, 2023; raw SHA-256 `b31e0bb0d06a46cad15f93eb8e5218b1c8920f4f53f50b8d8851df7b7d2ca655`.
- [NIDDK — Anemia in Chronic Kidney Disease](https://www.niddk.nih.gov/health-information/kidney-disease/anemia), What causes anemia in CKD?, last reviewed September 2020; raw SHA-256 `ed0ce208ee4c573c109027ef9146b2d2eb28035d666b2f3c69e69c408001698c`.
- [Merck Manual — Megaloblastic Macrocytic Anemias](https://www.merckmanuals.com/professional/hematology/anemias-caused-by-deficient-erythropoiesis/megaloblastic-macrocytic-anemias), full review and last update March 2025, Etiology, Pathophysiology and Symptoms and Signs; raw SHA-256 `6749ccc20ca457a01448dfd99fb87aaaab9298d4936ecb9d12256f076c47a3f2`.
- [USMLE Content Outline (2026)](https://www.usmle.org/sites/default/files/2022-01/USMLE_Content_Outline_0.pdf), page 5: Blood & Lymphoreticular System → Anemia, cytopenias, and polycythemia anemias → disorders of hemoglobin, heme, or membrane → hereditary spherocytosis. Raw SHA-256 `3d793f7c80655e364ed4216dcc5b5e4d14e6331225d97ecdf6ccbcb372fb21a9`. No NCJMM metadata is used.

Every source title, canonical URL, revision date, locator, authorship class and option-level claim was checked separately. SetID is not applicable because no drug label is evidence.

## Clinical, originality and adversarial review

The very low reticulocyte count distinguishes abrupt marrow-production failure from an acceleration of hemolysis. The household fifth-disease exposure and B19 erythroid-progenitor tropism make C the single best answer. Warm IgG hemolysis and G6PD-related oxidant hemolysis generally stimulate reticulocytosis when marrow function is intact. Renal EPO deficiency and folate-deficient megaloblastosis are real production defects, but neither explains this abrupt exposure-linked deterioration; the latter is typically insidious.

No hidden assumption about an unnamed medication, renal disease or folate intake is needed. The stem does not rely on a numerical cutoff. A second-answer attack found no alternative that explains the full timing, exposure and reticulocytopenia pattern.

The old diagnosis construct is duplicated by Q1111; that duplication is now resolved through a full construct rewrite. Targeted searches across all 1,635 canonical payloads found no other item testing B19 aplastic crisis or erythroid-progenitor suppression. Q0405 still tests the hereditary-spherocytosis membrane mechanism and Q0782 tests ANK1 function, both distinct from the new complication construct. This targeted screen does not prove exhaustive semantic uniqueness.

Difficulty is a moderate two-step author estimate, not a psychometric result. A fresh same-reviewer adversarial reread found no further content defect after repair. The required isolated different-family audit was not performed, so the item remains blocked.
