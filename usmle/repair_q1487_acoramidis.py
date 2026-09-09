#!/usr/bin/env python3
import json
from pathlib import Path

P=Path('usmle/batch_specs_1401_1500/04_q1476_q1500_author_20260908.json')
b=json.loads(P.read_text())
replacement={
  "num": 1487,
  "drug": "acoramidis",
  "country_scope": "United States",
  "status": "AUTHOR_QA_PASS_PENDING_DETERMINISTIC_PREFLIGHT_AND_INDEPENDENT_AUDIT",
  "blueprint": {
    "primary_system": "Cardiovascular System",
    "primary_competency": "Medical Knowledge: Applying Foundational Science Concepts",
    "disciplines": ["Pharmacology", "Biochemistry"],
    "official_outline_path": ["Cardiovascular System"],
    "specification_source_id": "USMLE-SPEC"
  },
  "item": {
    "vignette": "Purified transthyretin tetramers from a patient with transthyretin-mediated cardiac amyloidosis are incubated with a small molecule. The compound occupies thyroxine-binding sites on transthyretin. The rate of tetramer breakup falls, but transthyretin gene transcription is unchanged.",
    "lead_in": "Which molecular step is directly slowed by this drug?",
    "options": {
      "A": "Hepatic transcription of the transthyretin gene",
      "B": "Dissociation of transthyretin tetramers into monomers",
      "C": "Proteolytic degradation of deposited amyloid fibrils",
      "D": "Endocytosis of transthyretin by cardiac macrophages",
      "E": "Binding of retinol-binding protein to circulating transthyretin"
    },
    "intended_key": "B",
    "tested_construct": "TTR tetramer stabilization slows dissociation into monomers, the rate-limiting step in amyloidogenesis",
    "difficulty": "moderate-hard",
    "difficulty_basis": "Author estimate based on mechanistic application and distractor discrimination; no empirical item statistics are claimed."
  },
  "explanation": {
    "key_explanation": "Acoramidis selectively stabilizes transthyretin by binding its thyroxine-binding sites and slowing dissociation of the TTR tetramer into monomers, the rate-limiting step in amyloidogenesis.",
    "distractor_explanations": {
      "A": "Acoramidis is a TTR protein stabilizer; the described direct action is not suppression of hepatic TTR gene transcription.",
      "B": "Acoramidis selectively stabilizes transthyretin by binding its thyroxine-binding sites and slowing dissociation of the TTR tetramer into monomers, the rate-limiting step in amyloidogenesis.",
      "C": "The labeled mechanism stabilizes soluble TTR tetramers rather than directly proteolyzing preexisting amyloid fibrils.",
      "D": "Cardiac macrophage endocytosis is not the labeled molecular target of acoramidis.",
      "E": "The label identifies binding at TTR thyroxine-binding sites and tetramer stabilization; it does not describe blockade of retinol-binding-protein association as the therapeutic mechanism."
    },
    "educational_objective": "Relate transthyretin tetramer stabilization to reduced tetramer dissociation, the rate-limiting step in TTR amyloidogenesis."
  },
  "sources": [{
    "source_id": "Q1487-LABEL",
    "title": "ATTRUBY- acoramidis hydrochloride tablet, film coated",
    "agency": "Manufacturer prescribing information hosted by NLM DailyMed",
    "url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=913552ef-875d-4cb7-bf05-a7d20a394c38",
    "setid": "913552ef-875d-4cb7-bf05-a7d20a394c38",
    "source_section_date": "2026-06",
    "date_basis": "Current DailyMed label displays Revised 06/2026; cited mechanism section checked 2026-09-09.",
    "retrieved_at": "2026-09-09",
    "section_locator": "12.1 Mechanism of Action",
    "verification": "Current label identity, SetID, cited locator, and mechanism claim checked before author-QA repair.",
    "rights_note": "Original educational item; prescribing-information facts paraphrased."
  }],
  "evidence_map": [
    {"claim_id":"Q1487-A","option":"A","claim_locator":"explanation.distractor_explanations.A","claim":"Acoramidis is a TTR protein stabilizer; the described direct action is not suppression of hepatic TTR gene transcription.","source_ids":["Q1487-LABEL"],"direct_or_inference":"inference","source_locator":"12.1 Mechanism of Action","scope":"Direct labeled mechanism for the key; distractor status is an item-specific inference from the documented mechanism and stipulated experimental conditions."},
    {"claim_id":"Q1487-B","option":"B","claim_locator":"explanation.distractor_explanations.B","claim":"Acoramidis selectively stabilizes transthyretin by binding its thyroxine-binding sites and slowing dissociation of the TTR tetramer into monomers, the rate-limiting step in amyloidogenesis.","source_ids":["Q1487-LABEL"],"direct_or_inference":"direct","source_locator":"12.1 Mechanism of Action","scope":"Direct labeled mechanism for the key; distractor status is an item-specific inference from the documented mechanism and stipulated experimental conditions."},
    {"claim_id":"Q1487-C","option":"C","claim_locator":"explanation.distractor_explanations.C","claim":"The labeled mechanism stabilizes soluble TTR tetramers rather than directly proteolyzing preexisting amyloid fibrils.","source_ids":["Q1487-LABEL"],"direct_or_inference":"inference","source_locator":"12.1 Mechanism of Action","scope":"Direct labeled mechanism for the key; distractor status is an item-specific inference from the documented mechanism and stipulated experimental conditions."},
    {"claim_id":"Q1487-D","option":"D","claim_locator":"explanation.distractor_explanations.D","claim":"Cardiac macrophage endocytosis is not the labeled molecular target of acoramidis.","source_ids":["Q1487-LABEL"],"direct_or_inference":"inference","source_locator":"12.1 Mechanism of Action","scope":"Direct labeled mechanism for the key; distractor status is an item-specific inference from the documented mechanism and stipulated experimental conditions."},
    {"claim_id":"Q1487-E","option":"E","claim_locator":"explanation.distractor_explanations.E","claim":"The label identifies binding at TTR thyroxine-binding sites and tetramer stabilization; it does not describe blockade of retinol-binding-protein association as the therapeutic mechanism.","source_ids":["Q1487-LABEL"],"direct_or_inference":"inference","source_locator":"12.1 Mechanism of Action","scope":"Direct labeled mechanism for the key; distractor status is an item-specific inference from the documented mechanism and stipulated experimental conditions."}
  ],
  "author_qa": {
    "status":"AUTHOR_QA_PASS","independent_audit":False,"key_correctness":"PASS","all_options_review":"PASS","single_best_answer":"PASS",
    "second_answer_attack":{"option":"A","resolution":"TTR-lowering therapies can reduce substrate production, but the stem explicitly stipulates unchanged transcription and occupancy of TTR thyroxine-binding sites; acoramidis directly slows tetramer dissociation.","status":"PASS"},
    "hidden_assumptions":"PASS — biochemical findings are stipulated; no treatment superiority, universal response, cure, or unsupported clinical efficacy claim is inferred.",
    "numerical_claims":"PASS — no invented dose, cutoff, response percentage, trial result, or empirical item statistic is used.",
    "fabricated_distractors":"PASS — distractors are biologically interpretable mechanisms and are not presented as invented clinical facts.",
    "source_identity_setid_url_locator":"PASS",
    "currentness":"PASS — current DailyMed label revised 06/2026 and mechanism section checked 2026-09-09.",
    "blueprint":"PASS against current Step 1 system/competency/discipline vocabulary.",
    "difficulty":"Author estimate only; not psychometrically calibrated.",
    "rationale":"PASS — keyed explanation plus A-E rationales present.",
    "educational_objective":"PASS",
    "adversarial_second_pass":"PASS",
    "unresolved_content_defects":[]
  }
}
items=b['items']
idx=next(i for i,x in enumerate(items) if x.get('num')==1487)
assert items[idx]['item']['intended_key']=='B'
items[idx]=replacement
counts={}
for x in items:
    s=x['blueprint']['primary_system']; counts[s]=counts.get(s,0)+1
old=list(b['systems'])
b['systems']={k:counts[k] for k in old if k in counts}
for k,v in counts.items():
    if k not in b['systems']: b['systems'][k]=v
assert sum(b['systems'].values())==25
assert [x['item']['intended_key'] for x in items]==list('ABCDEABCDEABCDEABCDEABCDE')
P.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
print('Q1487_REPAIRED_ACORAMIDIS')
