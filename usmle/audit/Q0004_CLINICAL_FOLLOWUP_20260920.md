# Q0004 — clinical and evidence follow-up, 20 September 2026

Status: **BLOCKED_PENDING_FULL_REAUDIT**, not FINAL_QA_PASS. Baseline commit `4ccbb5a8`, payload `46d491155b1452a3b2e9b03b09ba2d83cd2f8a19970f0d6ec6daa4c17cac4f86`.

The key was correct, but the evidence map falsely assigned the two sickle-cell sources to all four alternative disorders. The stored outline path also did not occur in the 2026 USMLE outline. Both defects required a new blocked payload.

## Verified evidence

- [MedlinePlus Genetics — Sickle cell disease](https://medlineplus.gov/genetics/condition/sickle-cell-disease/), Description and Causes, updated March 14, 2024; raw SHA-256 `7ae0662873da2af18d2714ee9ea953b3b8a4b1008d58d11882d268bc345b833c`.
- [MedlinePlus Genetics — HBB gene](https://medlineplus.gov/genetics/gene/hbb/), Normal Function and Sickle cell disease, updated March 14, 2024; confirms Glu6Val, rigid HbS assemblies, sickling and vaso-occlusion; raw SHA-256 `fbae7ccefbc91b9263dbe4b3bd067f32ca29a162afb1e7afa99192b2fb60aa2b`.
- [NHLBI — Sickle Cell Disease Causes and Risk Factors](https://www.nhlbi.nih.gov/health/sickle-cell-disease/causes), “What is a ‘sickled’ cell?”, updated August 20, 2024; explicitly connects low oxygen to stiff HbS strands and deformation. Fresh capture 85,872 bytes, SHA-256 `1cd09db6bc36ce18706f73a1a1cce108179956a90bdd0fcf6c65f3b5cbc0ba46`.
- [Alpha thalassemia](https://medlineplus.gov/genetics/condition/alpha-thalassemia/), Causes, updated December 2, 2022; raw SHA-256 `2b6f3fe4e9431046daa2b4fba236cb4226cf36a0f1a7bdf119fac69264530611`.
- [Hereditary spherocytosis](https://medlineplus.gov/genetics/condition/hereditary-spherocytosis/), Causes, updated September 1, 2013; raw SHA-256 `78cd6ffb0c0c749c8ce700acd1a8278af5f9b3d039ef6cf5b90560368505ad8b`.
- [G6PD gene](https://medlineplus.gov/genetics/gene/g6pd/), Normal Function and G6PD deficiency, updated April 12, 2023; raw SHA-256 `b31e0bb0d06a46cad15f93eb8e5218b1c8920f4f53f50b8d8851df7b7d2ca655`.
- [X-linked sideroblastic anemia](https://medlineplus.gov/genetics/condition/x-linked-sideroblastic-anemia/), Description and Causes, updated September 19, 2025. Fresh capture 37,889 bytes, SHA-256 `d54d5c90d3a0c3fd149c3e9e7c405cc121fcd671d2079661aa36f9e5ddce7501`.
- [USMLE Content Outline (2026)](https://www.usmle.org/sites/default/files/2022-01/USMLE_Content_Outline_0.pdf), Blood & Lymphoreticular System → Anemia, cytopenias, and polycythemia anemias → Disorders of hemoglobin, heme, or membrane → sickle cell disease. No NCJMM metadata is present.

Every source title, canonical URL, date, section, authorship class and claim was read separately from availability/hash checks. SetID is not applicable.

## Clinical and adversarial review

The stem gives a known diagnosis and a sickled smear. Exercise and dehydration are plausible contextual precipitants but are not presented as necessary diagnostic criteria. No dose, cutoff, risk percentage or calculation appears. The direct event asked for is red-cell deformation, not the upstream DNA substitution or the downstream vascular occlusion.

A produces alpha-globin underproduction and thalassemic hemoglobin imbalance. B causes membrane instability and spherical cells. C causes NADPH failure and oxidant hemolysis. D impairs heme production and produces sideroblastic anemia. E alone produces stiff intracellular HbS strands under low oxygen and directly changes cell shape. No second answer is defensible.

The key rationale does not overstate reversibility: early sickling can reverse with oxygenation, whereas repeated sickling damages membranes; neither additional claim is required to answer this item. “Acute” refers to the observed deformation during the episode and not to the origin of the inherited variant.

Targeted bank review found Q0895, which asks how increased fetal hemoglobin mediates a clinical benefit by reducing HbS polymerization. That treatment-effect task is related but distinct from Q0004's direct molecular cause of deformation. Other hits test sickle complications or different red-cell diseases. This candidate screen does not prove exhaustive uniqueness.

Difficulty is now an easy two-step author estimate, not a psychometric result. A fresh same-reviewer adversarial reread found no further content defect after repair. The required isolated different-family audit was not performed, so the item remains blocked.
