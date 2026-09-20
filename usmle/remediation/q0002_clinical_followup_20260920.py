"""Apply the reviewed Q0002 repair without inheriting a historical FINAL verdict."""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CID = 'S1-DIRECT-0002-20260827T013100'
EXPECTED = 'e1ab2c64d3640a58093f2e31015e88b2e31cfc6f624e451274e7b9c2f6f18f25'
AUDIT = 'Q0002_CLINICAL_FOLLOWUP_20260920'


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canon(value).encode()).hexdigest()


def source(source_id, title, url, date, locator, summary, raw_hash):
    return {
        'source_id': source_id,
        'title': title,
        'url': url,
        'agency': 'National Library of Medicine (NIH) — MedlinePlus Genetics' if 'medlineplus.gov' in url else 'National Heart, Lung, and Blood Institute (NIH)',
        'government_status_verified': True,
        'publication_or_revision_date': date,
        'retrieved_at': '2026-09-20',
        'section_locator': locator,
        'supporting_passage': summary,
        'passage_type': 'Reviewer paraphrase, not a verbatim quotation',
        'raw_source_sha256': raw_hash,
        'raw_capture_record': 'audit/live_20260919/SOURCE_AVAILABILITY.json',
        'set_id_applicability': 'NOT_APPLICABLE_NON_DRUG_SOURCE',
        'rights_status': 'Official U.S. federal health-information source; facts used for original synthesis.'
    }


def main():
    db = sqlite3.connect(ROOT / 'data/usmle-step1.db')
    db.row_factory = sqlite3.Row
    archive_path = ROOT / 'remediation' / (AUDIT + '_BEFORE_ROWS.json')
    with db:
        db.execute('BEGIN IMMEDIATE')
        old = dict(db.execute('SELECT * FROM step2_final_items WHERE candidate_id=?', (CID,)).fetchone())
        review = dict(db.execute('SELECT * FROM step2_final_reviews WHERE candidate_id=?', (CID,)).fetchone())
        p = json.loads(old['payload_json'])
        if p.get('current_reaudit', {}).get('audit_id') == AUDIT:
            assert digest(p) == old['payload_sha256']
            assert archive_path.exists()
            print('Already applied; no rows changed')
            return
        assert old['payload_sha256'] == EXPECTED == digest(p)
        assert db.execute('SELECT count(*) FROM step2_final_items').fetchone()[0] == 1635

        p['item']['options'] = {
            'A': 'Decreased dynein-driven motility of respiratory cilia',
            'B': 'Decreased inhibition of neutrophil elastase by alpha-1 antitrypsin',
            'C': 'Decreased CFTR-mediated chloride transport across airway epithelial cells',
            'D': 'Decreased superoxide generation by phagocyte NADPH oxidase',
            'E': 'Disrupted lysosomal trafficking in leukocytes'
        }
        p['item'].update(
            difficulty='easy', reasoning_steps_count=2,
            difficulty_basis='Author estimate, not psychometrically calibrated: the stem names pathogenic CFTR variants and elevated sweat chloride; the examinee must identify CFTR chloride transport and connect it to airway-surface dehydration. No calculation or treatment decision is required.',
            tested_construct='Loss of CFTR-mediated epithelial chloride transport reduces water movement into airway secretions, producing dehydrated thick mucus.'
        )
        rationales = {
            'A': 'Incorrect. Impaired dynein-dependent ciliary movement causes defective mucociliary clearance in primary ciliary dyskinesia, but it does not cause elevated sweat chloride or the pancreatic manifestations produced by CFTR dysfunction.',
            'B': 'Incorrect. Alpha-1 antitrypsin deficiency permits neutrophil elastase–mediated alveolar injury and emphysema; it does not directly dehydrate airway mucus or explain elevated sweat chloride.',
            'C': 'Correct. CFTR is an epithelial chloride channel that regulates salt and water movement. Pathogenic CFTR variants reduce chloride transport and water movement across airway epithelium, producing thick, sticky secretions; the elevated sweat chloride, recurrent sinopulmonary infections, and pancreatic insufficiency support cystic fibrosis.',
            'D': 'Incorrect. Defective phagocyte NADPH oxidase reduces superoxide-dependent microbial killing in chronic granulomatous disease. It can cause recurrent infections but not elevated sweat chloride, pancreatic insufficiency, or CFTR-related mucus dehydration.',
            'E': 'Incorrect. LYST-related lysosomal-trafficking dysfunction causes Chediak-Higashi syndrome with recurrent infections and characteristic pigmentation and granule abnormalities; it does not cause the CFTR transport phenotype.'
        }
        p['explanation'] = {
            'key_explanation': rationales['C'],
            'distractor_explanations': rationales,
            'educational_objective': 'Explain that CFTR loss reduces epithelial chloride and coupled water movement, dehydrating airway and ductal secretions; distinguish this transport defect from real mechanisms that cause impaired clearance, emphysema, or immunodeficiency.'
        }
        source_ids = {'A':['S3'], 'B':['S4'], 'C':['S1','S2'], 'D':['S5'], 'E':['S6']}
        p['evidence_map'] = [{
            'option': option,
            'claim': text,
            'rationale': rationales[option],
            'source_ids': source_ids[option],
            'evidence_basis': 'LIVE_SOURCE_REVIEW_SAME_REVIEWER_NOT_INDEPENDENT_CERTIFICATION',
            'audit_record': 'audit/' + AUDIT + '.md',
            'target_diagnosis_or_process': {'A':'Primary ciliary dyskinesia','B':'Alpha-1 antitrypsin deficiency','C':'Cystic fibrosis','D':'Chronic granulomatous disease','E':'Chediak-Higashi syndrome'}[option],
            'target_mechanism': text
        } for option, text in p['item']['options'].items()]
        p['sources'] = [
            source('S1','Cystic fibrosis','https://medlineplus.gov/genetics/condition/cystic-fibrosis/','Last updated July 6, 2021','Description; Causes','CFTR encodes a chloride channel; disrupted chloride and water transport produces thick, sticky mucus.','b00ff44712ef381f0130e161f6b50b44f18f402449f7b2ceb1d8314fd17ba53d'),
            source('S2','Cystic Fibrosis Causes','https://www.nhlbi.nih.gov/health/cystic-fibrosis/causes','Last updated November 15, 2024','What causes cystic fibrosis?; How do CFTR mutations cause cystic fibrosis?','Faulty CFTR alters salt and water movement, yielding less-water-containing thick mucus and salty sweat.','9b051047d67debf63b8f73ae627c68bf08933548b40c69cb4f60adaab02b221f'),
            source('S3','Primary ciliary dyskinesia','https://medlineplus.gov/genetics/condition/primary-ciliary-dyskinesia/','Last updated September 22, 2025','Description; Causes','Dynein-containing ciliary structures generate motile force; disruption impairs airway clearance and causes recurrent respiratory infections.','8d6c7de91f5c86d951fc7220f077e51dbd1587255c09c302257449abb0a365ae'),
            source('S4','Alpha-1 antitrypsin deficiency','https://medlineplus.gov/genetics/condition/alpha-1-antitrypsin-deficiency/','Last updated September 15, 2021','Description; Causes','Alpha-1 antitrypsin restrains neutrophil elastase; deficiency permits alveolar destruction and emphysema.','e70924af821c4fba5dc5f1d4f5bf46da970814d99161babde6977be7ab083da7'),
            source('S5','Chronic granulomatous disease','https://medlineplus.gov/genetics/condition/chronic-granulomatous-disease/','Last updated January 1, 2016','Description; Causes','Phagocyte NADPH oxidase generates superoxide used for microbial killing; loss causes recurrent bacterial and fungal infections.','759610a1ee4a4998f8801f6b56e5fcd0619fa6880bf1d3e068a0a7bf0ace4371'),
            source('S6','Chediak-Higashi syndrome','https://medlineplus.gov/genetics/condition/chediak-higashi-syndrome/','Last updated January 1, 2014','Description; Causes','LYST variants disrupt lysosomal trafficking, producing enlarged dysfunctional lysosomes and impaired antimicrobial responses.','8e9cab2e151e91d36768d5bd6b3e6245b8201eadb150706745bc1f7f5e935cfb')
        ]
        p['semantic_fingerprint'].update(
            correct_answer_concept=p['item']['options']['C'],
            mechanism=p['item']['tested_construct'],
            tested_construct=p['item']['tested_construct'],
            reasoning_chain=['Recognize cystic fibrosis from the named genotype, sweat chloride, respiratory disease, and malabsorption.', 'Connect loss of epithelial CFTR chloride transport to reduced water movement and thick secretions.'],
            distractor_misconceptions=['confusing mucus dehydration with defective ciliary motility', 'confusing airway obstruction with protease-mediated emphysema', 'confusing recurrent infection due to abnormal secretions with phagocyte killing defects', 'confusing CFTR dysfunction with lysosomal-trafficking immunodeficiency']
        )
        historical = p.setdefault('historical_audit_metadata', {})
        for field in ('author_self_audit','step2_final_audit','hashes'):
            if field in p:
                historical[field] = p.pop(field)
        p['current_reaudit'] = {
            'audit_id': AUDIT,
            'status': 'BLOCKED_PENDING_FULL_REAUDIT',
            'full_clinical_certification': False,
            'same_reviewer_content_passes': 2,
            'independent_blind_passes': 0,
            'corrections': ['Replace four remote distractors with verified real mechanisms', 'Specify CFTR-mediated transport in the keyed option', 'Replace generic moderate rating with item-specific easy author estimate', 'Bind each option to inspected source metadata and captured raw-source hash', 'Isolate obsolete PASS metadata as historical'],
            'remaining_gates': ['Independent isolated author/auditor workflow required by README', 'Exhaustive semantic comparison beyond targeted candidate screening']
        }
        assert p['item']['intended_key'] == 'C' and set(p['item']['options']) == set('ABCDE')
        rh = {'candidate_id': CID, 'verdict': 'BLOCKED_PENDING_FULL_REAUDIT', 'payload_sha256': digest(p),
              'prior_review_sha256': review['review_sha256'], 'reviewed_at':'2026-09-20',
              'audit_record':'audit/' + AUDIT + '.md',
              'review_scope':'Live claim review, repaired alternatives and same-reviewer adversarial reread; not independent certification',
              'defects':p['current_reaudit']['remaining_gates']}
        archive = {'item_row':old,'review_row':review}
        if archive_path.exists():
            assert json.loads(archive_path.read_text()) == archive
        else:
            archive_path.write_text(json.dumps(archive, indent=2) + '\n')
        db.execute('UPDATE step2_final_items SET payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? WHERE candidate_id=?', (canon(p),digest(p),digest(rh),rh['verdict'],'2026-09-20',CID))
        db.execute('UPDATE step2_final_reviews SET review_json=?,review_sha256=?,final_status=?,finalized_at=? WHERE candidate_id=?', (canon(rh),digest(rh),rh['verdict'],'2026-09-20',CID))
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    result={'candidate_id':CID,'before_sha256':EXPECTED,'after_sha256':digest(p),'status':rh['verdict'],'new_final_passes':0,'item_count':1635}
    (ROOT/'audit'/(AUDIT+'_RESULT.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
