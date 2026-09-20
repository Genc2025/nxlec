"""Complete the Q0007 content follow-up; preserve independent certification gates."""
import json, sqlite3
from pathlib import Path
from q0006_clinical_followup_20260920 import canon, digest, source

ROOT = Path(__file__).resolve().parents[1]
CID = 'S1-DIRECT-0007-20260827T020000Z'
EXPECTED = 'dea80c4e92d565a426bc5e171ed65d35d7f6d7bfd2ad9816787d15ea269e1d34'
AUDIT = 'Q0007_EVIDENCE_V2_20260920'

def main():
    db = sqlite3.connect(ROOT/'data/usmle-step1.db'); db.row_factory = sqlite3.Row
    archive_path = ROOT/'remediation'/(AUDIT+'_BEFORE_ROWS.json')
    with db:
        db.execute('BEGIN IMMEDIATE')
        old = dict(db.execute('select * from step2_final_items where candidate_id=?',(CID,)).fetchone())
        rev = dict(db.execute('select * from step2_final_reviews where candidate_id=?',(CID,)).fetchone())
        p = json.loads(old['payload_json'])
        if p.get('current_reaudit',{}).get('audit_id') == AUDIT:
            assert digest(p) == old['payload_sha256'] and archive_path.exists()
            print('Already applied; no rows changed'); return
        assert digest(p) == old['payload_sha256'] == EXPECTED
        p['blueprint'].update(primary_system='Blood & Lymphoreticular System', official_outline_path=['Blood & Lymphoreticular System','Coagulation disorders (hypocoagulable and hypercoagulable conditions)','hypocoagulable','von Willebrand disease'], coverage_deficit_addressed='Distinguish von Willebrand disease from competing bleeding disorders using phenotype and specific VWF assays.')
        p['item']['vignette'] = 'A 19-year-old woman has recurrent epistaxis, easy bruising, and prolonged bleeding after dental procedures. Her mother has similar symptoms. Platelet count is normal. On repeated testing when she is otherwise well, both von Willebrand factor antigen and platelet-dependent von Willebrand factor activity are markedly reduced.'
        p['item']['options']['E'] = 'Factor XI deficiency'
        p['item']['lead_in'] = 'Which diagnosis best explains the clinical and laboratory findings?'
        p['item']['tested_construct'] = 'VWF deficiency or dysfunction impairs primary hemostasis; repeated abnormalities in VWF antigen and platelet-dependent activity distinguish VWD from isolated coagulation-factor deficiencies.'
        p['item']['difficulty_basis'] = 'Author estimate, not psychometrically calibrated: identify the mucocutaneous bleeding phenotype and interpret specific repeated VWF abnormalities to distinguish the offered bleeding disorders. The laboratory clues are direct; no calculation or subtype assignment is required.'
        r = {
            'A': 'Incorrect. Hemophilia A involves factor VIII deficiency or dysfunction. Women can have symptomatic hemophilia, so sex does not exclude it. Isolated hemophilia A does not explain the marked reduction in both VWF antigen and platelet-dependent VWF activity.',
            'B': 'Incorrect. Active immune thrombocytopenia causes bleeding through a low platelet count. Neither the normal platelet count nor the specific VWF abnormalities support it as the explanation.',
            'C': 'Incorrect. DIC is an acquired systemic coagulation disorder with consumption of platelets and clotting factors in an underlying illness or injury. It does not explain this familial recurrent bleeding pattern and repeated VWF abnormalities when otherwise well.',
            'D': 'Correct. The mucocutaneous bleeding, affected relative and repeated marked reductions in VWF antigen and platelet-dependent activity support von Willebrand disease. A normal platelet count does not imply normal platelet adhesion. These findings do not by themselves establish a particular subtype or prove the inheritance pattern.',
            'E': 'Incorrect. Factor XI deficiency can cause nosebleeds, easy bruising and bleeding after dental procedures, and can run in families. However, isolated factor XI deficiency does not explain the specific repeated reduction in VWF antigen and activity.'
        }
        p['explanation'] = dict(key_explanation=r['D'], distractor_explanations=r, educational_objective='Distinguish VWD from hemophilia A, ITP, DIC and factor XI deficiency by combining the bleeding phenotype with VWF-specific laboratory findings; do not exclude hemophilia on the basis of sex.')
        dates = ['August 8, 2023','December 1, 2012','May 6, 2022','July 24, 2025','March 24, 2022']
        hashes = ['c15b6537a7588ce7001de9d4f01c28e51ee29216cd7c4dfdce3fe11eabfa8757','0c5f98e1f68691032730a819b84269e1aef8d545b7ccc23174cb9ad5a1a78613','3b5e6327b0564bf492c86c07e071616fff42430c985cca407e3ba77df909d23a','f5d496793c84f2d918eb727ad52bb5d7ea45cb8471af7bb3bc8d17e2cb9f0dfe','de6ab3e9b15a1bede65d78cedcd6f9d5786d59e6a422f89c92183d9cf6c79809']
        p['sources'] = p['sources'][:5]
        for s,d,h in zip(p['sources'],dates,hashes):
            s.update(publication_or_revision_date=d,raw_source_sha256=h)
        p['sources'].extend([
            dict(source_id='S6',title='Factor XI deficiency',url='https://medlineplus.gov/genetics/condition/factor-xi-deficiency/',agency='NLM/NIH — MedlinePlus Genetics',government_status_verified=True,publication_or_revision_date='August 1, 2018',section_locator='Description; Causes; Inheritance',supporting_passage='F11-related factor XI deficiency can cause nasal and procedural bleeding and has variable inheritance. It is a coagulation-factor defect, not a VWF defect.',raw_source_sha256='9ddf74a6db818ec8629b6144bc925f36ee9ff3be8abf5e576a22df569db5b193'),
            dict(source_id='S7',title='Diagnosing von Willebrand Disease',url='https://www.cdc.gov/von-willebrand/diagnosis/index.html',agency='CDC — National Center on Birth Defects and Developmental Disabilities',government_status_verified=True,publication_or_revision_date='May 15, 2024',section_locator='Screening tests > Complete blood count; Diagnostic tests > VWF antigen and VWF activity',supporting_passage='Specific antigen and activity testing evaluates VWF; repeat tests may be needed because levels vary. Screening counts can be normal.',raw_source_sha256='427cf623e655b6e432f2647c133bf8fd27a482ffc2bb4b65224afd95008f46fb')
        ])
        for s in p['sources']:
            s.update(retrieved_at='2026-09-20',set_id_applicability='NOT_APPLICABLE_NON_DRUG_SOURCE',passage_type='Reviewer paraphrase; diagnostic exclusion is a synthesis across the cited sources',rights_status='Federal educational source; facts paraphrased',evidence_record='audit/'+AUDIT+'.md',capture_status='Raw response hashed; full raw response not durably archived')
        bindings = {'A':['S3','S7'],'B':['S4','S7'],'C':['S5','S7'],'D':['S1','S2','S7'],'E':['S6','S7']}
        p['evidence_map'] = [dict(option=o,claim=p['item']['options'][o],rationale=r[o],source_ids=bindings[o],target_diagnosis_or_process=p['item']['options'][o],evidence_basis='LIVE_SOURCE_REVIEW_SAME_REVIEWER_NOT_INDEPENDENT_CERTIFICATION') for o in 'ABCDE']
        fp = p['semantic_fingerprint']
        fp.update(lead_in_task=p['item']['lead_in'],tested_construct=p['item']['tested_construct'],mechanism=p['item']['tested_construct'],essential_clues=['recurrent mucocutaneous and dental bleeding','affected mother','normal platelet count','repeated marked reduction in VWF antigen and platelet-dependent activity'],reasoning_chain=['Recognize a mucocutaneous bleeding phenotype.','Interpret repeated VWF-specific abnormalities to distinguish the offered disorders.'],distractor_misconceptions=['confusing isolated factor VIII deficiency with VWF abnormalities','confusing low platelet number with impaired adhesion','attributing a stable familial pattern to systemic consumption','recognizing factor XI bleeding but ignoring the VWF-specific laboratory findings'])
        p.setdefault('historical_audit_metadata',{})['q0007_partial_reaudit'] = p['current_reaudit']
        p['current_reaudit'] = dict(audit_id=AUDIT,status='BLOCKED_PENDING_FULL_REAUDIT',full_clinical_certification=False,same_reviewer_content_passes=2,independent_blind_passes=0,corrections=['Replace thrombophilia distractor with factor XI deficiency','Add discriminating repeated VWF testing to prevent a second defensible answer','Repair exact USMLE outline hierarchy','Verify all source revision dates and source-specific bindings','Align objective and semantic fingerprint with revised item'],remaining_gates=['Isolated different-family audit required by README','Exhaustive semantic originality beyond targeted screening','Durable raw-source archival beyond recorded hashes and claim summaries'])
        review = dict(candidate_id=CID,verdict='BLOCKED_PENDING_FULL_REAUDIT',payload_sha256=digest(p),prior_review_sha256=rev['review_sha256'],reviewed_at='2026-09-20',audit_record='audit/'+AUDIT+'.md',defects=p['current_reaudit']['remaining_gates'])
        archive = dict(item_row=old,review_row=rev)
        if archive_path.exists(): assert json.loads(archive_path.read_text()) == archive
        else: archive_path.write_text(json.dumps(archive,indent=2)+'\n')
        db.execute('update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(p),digest(p),digest(review),review['verdict'],'2026-09-20',CID))
        db.execute('update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(review),digest(review),review['verdict'],'2026-09-20',CID))
        assert db.execute('pragma integrity_check').fetchone()[0] == 'ok'
    result = dict(candidate_id=CID,before_sha256=EXPECTED,after_sha256=digest(p),new_final_passes=0,status=review['verdict'])
    (ROOT/'audit'/(AUDIT+'_RESULT.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__ == '__main__': main()
