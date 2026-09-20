# Q0005 — clinical and evidence follow-up, 20 September 2026

Status: **BLOCKED_PENDING_FULL_REAUDIT**, not FINAL_QA_PASS. Baseline commit `6e7ec962`, payload `70b44381cb254e368f8366c0720e18ed8df2382bed45999cf099489aab0a2d38`.

The keyed G6PD/NADPH mechanism was correct, but FADH2, acetyl-CoA, cAMP and UDP-glucose were remote distractors. The two G6PD sources were also reused as if they separately proved every alternative. The revised item compares five genuine red-cell mechanisms and binds each to its own inspected source.

## Verified evidence

- [MedlinePlus Genetics — G6PD deficiency](https://medlineplus.gov/genetics/condition/glucose-6-phosphate-dehydrogenase-deficiency/), Description and Causes, updated April 12, 2023; raw SHA-256 `0e9d6665f1a7172dd61d74c8b149bb71a3ea7928aa500caf203f8b2df5fa3167`.
- [MedlinePlus Genetics — G6PD gene](https://medlineplus.gov/genetics/gene/g6pd/), Normal Function and G6PD deficiency, updated April 12, 2023; explicitly identifies the first pentose-phosphate-pathway step, NADPH production and the erythrocyte dependence on that protection; raw SHA-256 `b31e0bb0d06a46cad15f93eb8e5218b1c8920f4f53f50b8d8851df7b7d2ca655`.
- [Pyruvate kinase deficiency](https://medlineplus.gov/genetics/condition/pyruvate-kinase-deficiency/), Description and Causes, updated April 1, 2012; raw SHA-256 `0b2756033de6150735f3d74d6fc00fafdb2242ba1ff4dd4e547a38dd29df8f4d`.
- [Hereditary spherocytosis](https://medlineplus.gov/genetics/condition/hereditary-spherocytosis/), Description and Causes, updated September 1, 2013; raw SHA-256 `78cd6ffb0c0c749c8ce700acd1a8278af5f9b3d039ef6cf5b90560368505ad8b`.
- [Beta thalassemia](https://medlineplus.gov/genetics/condition/beta-thalassemia/), Description and Causes, updated May 1, 2023; raw SHA-256 `fec84384950309227187bb141987dbde036646c10cbf1e0462d44bd17ff78ec9`.
- [Sickle cell disease](https://medlineplus.gov/genetics/condition/sickle-cell-disease/), Description and Causes, updated March 14, 2024; raw SHA-256 `7ae0662873da2af18d2714ee9ea953b3b8a4b1008d58d11882d268bc345b833c`.
- [USMLE Content Outline (2026)](https://www.usmle.org/sites/default/files/2022-01/USMLE_Content_Outline_0.pdf), page 5: Blood & Lymphoreticular System → Anemia, cytopenias, and polycythemia anemias → Hemolysis → glucose 6-phosphate dehydrogenase deficiency. Raw SHA-256 `3d793f7c80655e364ed4216dcc5b5e4d14e6331225d97ecdf6ccbcb372fb21a9`. No NCJMM metadata is present.

Every source title, canonical URL, revision date, locator, authorship class and option-level claim was checked separately. SetID is not applicable because no drug label is used as evidence.

## Clinical and adversarial review

Oxidant exposure followed by jaundice and dark urine establishes acute hemolysis. Bite cells arise after splenic removal of oxidized hemoglobin aggregates; specifying supravital staining for Heinz bodies avoids implying that the aggregates are reliably visible on an ordinary Wright-stained smear.

A is a genuine erythrocyte enzymopathy, but pyruvate kinase failure produces ATP depletion and chronic nonspherocytic hemolysis. C causes membrane instability and spherocytes. D reduces beta-globin synthesis. E produces HbS polymerization and sickling. Only B explains the complete oxidant/Heinz-body/bite-cell pattern. The key does not rely on ancestry, a named drug, or an unstated laboratory value, and no second answer is defensible.

The official outline separately lists G6PD and pyruvate kinase deficiency under hemolysis; the stored generic “red blood cell disorders → enzymopathies” hierarchy was not the exact outline. Difficulty is now an easy two-step author estimate, not a psychometric result.

A targeted canonical-bank search found no second item testing G6PD-dependent oxidant defense. Q0011 mentions NADPH but tests phagocyte NADPH oxidase and respiratory burst, a distinct construct. This targeted screen does not prove exhaustive semantic uniqueness.

A fresh same-reviewer adversarial reread found no further content defect after repair. The required isolated different-family audit was not performed, so the item remains blocked.
