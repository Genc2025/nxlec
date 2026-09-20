"""Guarded partial clinical correction; never promotes Q0007 to FINAL."""
import json, sqlite3
from pathlib import Path
from q0006_clinical_followup_20260920 import canon, digest

ROOT = Path(__file__).resolve().parents[1]
CID = 'S1-DIRECT-0007-20260827T020000Z'
EXPECTED = 'b30fd4fa3dd313f203771e2230e9d51d086f80804138b9b0ee56a6dc7a70dfa4'
AUDIT = 'Q0007_CLINICAL_FOLLOWUP_20260920'

def main():
    db = sqlite3.connect(ROOT / 'data/usmle-step1.db')
    db.row_factory = sqlite3.Row
    ap = ROOT / 'remediation' / (AUDIT + '_BEFORE_ROWS.json')
    with db:
        db.execute('BEGIN IMMEDIATE')
        old = dict(db.execute('select * from step2_final_items where candidate_id=?', (CID,)).fetchone())
        rev = dict(db.execute('select * from step2_final_reviews where candidate_id=?', (CID,)).fetchone())
        p = json.loads(old['payload_json'])
        if p.get('current_reaudit', {}).get('audit_id') == AUDIT:
            assert digest(p) == old['payload_sha256'] and ap.exists()
            print('Already applied; no rows changed')
            return
        assert EXPECTED == old['payload_sha256'] == digest(p)
        r = {
            'A': 'Incorrect as the most likely diagnosis. Hemophilia A is a factor VIII disorder that commonly produces deep-tissue or joint bleeding, particularly in severe disease. Women can have symptomatic hemophilia, so sex and mother-daughter transmission do not exclude it. The predominant mucocutaneous pattern favors von Willebrand disease among these choices.',
            'B': 'Incorrect. Active immune thrombocytopenia causes bleeding through a low platelet count; the normal platelet count argues against it as the explanation here.',
            'C': 'Incorrect. DIC is an acquired systemic coagulation disorder associated with an underlying illness or injury and consumption of platelets and clotting factors. It does not coherently explain recurrent similar bleeding in the patient and her mother. The stem does not establish lifelong symptoms, and DIC should not be defined solely by critical illness.',
            'D': 'Correct as the most likely diagnosis among these options. Recurrent nosebleeds, easy bruising and prolonged dental bleeding with an affected relative favor von Willebrand disease. A normal platelet count does not establish normal platelet adhesion. This pattern is suggestive rather than laboratory confirmation; the pedigree alone neither proves autosomal inheritance nor identifies a subtype.',
            'E': 'Incorrect. Factor V Leiden predisposes to venous thrombosis rather than explaining a primary mucocutaneous bleeding phenotype.'
        }
        p['explanation']['distractor_explanations'] = r
        p['explanation']['key_explanation'] = r['D']
        p['item'].update(difficulty='easy', reasoning_steps_count=2, difficulty_basis='Author estimate, not psychometrically calibrated: recognize the predominant mucocutaneous bleeding pattern, then use the family history and normal platelet count to rank the offered diagnoses. No calculation or definitive laboratory diagnosis is required.')
        p['semantic_fingerprint']['essential_clues'] = ['recurrent mucocutaneous and dental bleeding', 'mother with similar symptoms', 'normal platelet count']
        p['semantic_fingerprint']['reasoning_chain'] = ['Recognize a predominant mucocutaneous bleeding phenotype.', 'Rank von Willebrand disease highest among the offered diagnoses without treating sex or this limited pedigree as exclusionary proof.']
        data = [
            ('S1','Von Willebrand disease','https://medlineplus.gov/genetics/condition/von-willebrand-disease/','NLM/NIH — MedlinePlus Genetics','Description; Causes; Inheritance','Revision date not captured; live page inspected 2026-09-20','Nosebleeds, bruising and dental bleeding are typical; inheritance varies by subtype.'),
            ('S2','VWF gene','https://medlineplus.gov/genetics/gene/vwf/','NLM/NIH — MedlinePlus Genetics','Normal Function','December 1, 2012','VWF supports platelet adhesion and carries factor VIII.'),
            ('S3','Hemophilia','https://medlineplus.gov/genetics/condition/hemophilia/','NLM/NIH — MedlinePlus Genetics','Description; Inheritance','Revision date not captured; live page inspected 2026-09-20','Hemophilia can cause deep bleeding; women with F8 variants can bleed, including through skewed X-inactivation.'),
            ('S4','Platelet Disorders — Immune Thrombocytopenia (ITP)','https://www.nhlbi.nih.gov/health/immune-thrombocytopenia','NHLBI/NIH','What is ITP?; What causes ITP?','July 24, 2025','ITP involves immune-mediated platelet destruction and low platelet counts.'),
            ('S5','Blood Clotting Disorders — Disseminated Intravascular Coagulation (DIC)','https://www.nhlbi.nih.gov/health/disseminated-intravascular-coagulation','NHLBI/NIH','What is DIC?; What causes DIC?','March 24, 2022','Systemic coagulation activation consumes platelets and factors in association with an underlying disorder.'),
            ('S6','Factor V Leiden thrombophilia','https://medlineplus.gov/genetics/condition/factor-v-leiden-thrombophilia/','NLM/NIH — MedlinePlus Genetics','Description; Causes','Revision date not captured; live page inspected 2026-09-20','Activated-protein-C resistance increases venous thrombosis risk.')
        ]
        p['sources'] = [dict(source_id=i,title=t,url=u,agency=a,government_status_verified=True,section_locator=l,publication_or_revision_date=d,retrieved_at='2026-09-20',supporting_passage=s,passage_type='Reviewer paraphrase',set_id_applicability='NOT_APPLICABLE_NON_DRUG_SOURCE',rights_status='Federal educational source; facts paraphrased') for i,t,u,a,l,d,s in data]
        ids = {'A':['S3'],'B':['S4'],'C':['S5'],'D':['S1','S2'],'E':['S6']}
        p['evidence_map'] = [dict(option=o,claim=p['item']['options'][o],rationale=r[o],source_ids=ids[o],evidence_basis='LIVE_LIMITED_CLAIM_REVIEW_NOT_FULL_CERTIFICATION') for o in 'ABCDE']
        hist = p.setdefault('historical_audit_metadata', {})
        for field in ('author_self_audit','step2_final_audit','hashes'):
            if field in p: hist[field] = p.pop(field)
        p['current_reaudit'] = dict(audit_id=AUDIT,status='BLOCKED_PENDING_FULL_REAUDIT',full_clinical_certification=False,independent_blind_passes=0,corrections=['Remove sex-based exclusion of hemophilia','Remove unsupported autosomal and lifelong inferences','Bind alternatives to disease-specific federal sources','Replace boilerplate difficulty with an author estimate'],remaining_gates=['Strengthen weak factor-V-Leiden distractor and repeat full adversarial review','Verify exact current blueprint path','Complete revision-date and durable-source-capture evidence','Exhaustive semantic originality','Isolated different-family audit'])
        review = dict(candidate_id=CID,verdict='BLOCKED_PENDING_FULL_REAUDIT',payload_sha256=digest(p),prior_review_sha256=rev['review_sha256'],audit_record='audit/'+AUDIT+'.md',reviewed_at='2026-09-20',defects=p['current_reaudit']['remaining_gates'])
        archive = dict(item_row=old,review_row=rev)
        if ap.exists(): assert json.loads(ap.read_text()) == archive
        else: ap.write_text(json.dumps(archive,indent=2)+'\n')
        db.execute('update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(p),digest(p),digest(review),review['verdict'],'2026-09-20',CID))
        db.execute('update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(review),digest(review),review['verdict'],'2026-09-20',CID))
        assert db.execute('pragma integrity_check').fetchone()[0] == 'ok'
    (ROOT/'audit'/(AUDIT+'_RESULT.json')).write_text(json.dumps(dict(candidate_id=CID,before_sha256=EXPECTED,after_sha256=digest(p),new_final_passes=0,status=review['verdict']),indent=2)+'\n')
    print(digest(p))

if __name__ == '__main__': main()
