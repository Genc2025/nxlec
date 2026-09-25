"""Apply reviewed Q0003 corrections without granting a new FINAL verdict."""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CID = 'S1-DIRECT-0003-20260827T020000Z'
EXPECTED = '7bbcde9a0972d2410f26784a3ab69e8d1c921debaf4044111420f082d0a4fdc3'
AUDIT = 'Q0003_CLINICAL_FOLLOWUP_20260920'


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canon(value).encode()).hexdigest()


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
            assert digest(p) == old['payload_sha256'] and archive_path.exists()
            print('Already applied; no rows changed')
            return
        assert old['payload_sha256'] == EXPECTED == digest(p)
        assert db.execute('SELECT count(*) FROM step2_final_items').fetchone()[0] == 1635

        p['item'].update(
            vignette='A healthy 13-year-old girl begins breast development followed several months later by a rapid increase in height. She has no chronic illness and takes no medications.',
            difficulty='easy', reasoning_steps_count=2,
            difficulty_basis='Author estimate, not psychometrically calibrated: identify normal gonadarche and recall that pulsatile hypothalamic GnRH activates pituitary LH and FSH secretion. No calculation or diagnosis of abnormal puberty is required.',
            options={
                'A':'Increased adrenal dehydroepiandrosterone secretion without activation of pituitary gonadotropins',
                'B':'Increased pulsatile hypothalamic secretion of gonadotropin-releasing hormone',
                'C':'Sustained GnRH-receptor stimulation causing pituitary receptor downregulation',
                'D':'Increased prolactin-mediated inhibition of gonadotropin secretion',
                'E':'Gonadotropin-independent ovarian estrogen production'
            },
            tested_construct='Re-emergent pulsatile hypothalamic GnRH signaling activates pituitary LH/FSH secretion and gonadal sex-steroid production at gonadarche.'
        )
        p['blueprint'].update(
            coverage_deficit_addressed='Normal adolescent puberty: pulsatile GnRH activation of the hypothalamic-pituitary-gonadal axis.',
            official_outline_path=['Human Development','Normal age-related findings and care of the well patient','Adolescence (13–17 years)','Normal physical changes: puberty'],
            primary_system='Human Development', disciplines=['Physiology']
        )
        rationales={
            'A':'Incorrect. Increased adrenal androgen secretion is adrenarche. Adrenarche can produce pubic or axillary hair and acne, but it is distinct from gonadarche and does not activate pituitary LH/FSH or directly cause breast development.',
            'B':'Correct. Normal gonadarche reflects reactivation of the hypothalamic GnRH pulse generator. Pulsatile GnRH stimulates pituitary LH and FSH secretion, which drives gonadal sex-steroid production and secondary sexual development.',
            'C':'Incorrect. Sustained stimulation by long-acting GnRH agonists downregulates pituitary GnRH receptors and reduces gonadotropin and sex-steroid secretion; this suppresses rather than initiates the normal pubertal axis.',
            'D':'Incorrect. Elevated prolactin can inhibit gonadotropin release and cause hypogonadotropic hypogonadism, which delays or stalls pubertal progression rather than initiating normal gonadarche.',
            'E':'Incorrect. Autonomous ovarian estrogen production is gonadotropin-independent peripheral puberty; it does not represent normal hypothalamic-pituitary-gonadal axis activation.'
        }
        p['explanation']={'key_explanation':rationales['B'],'distractor_explanations':rationales,
            'educational_objective':'Distinguish normal gonadarche—reactivation of pulsatile GnRH followed by LH/FSH and gonadal steroid secretion—from adrenarche, suppressive GnRH exposure, hyperprolactinemia, and gonadotropin-independent estrogen production.'}
        source_ids={'A':['S3'],'B':['S2','S3'],'C':['S3'],'D':['S3'],'E':['S2','S3']}
        diagnoses={'A':'Adrenarche','B':'Normal gonadarche','C':'Pharmacologic HPG-axis suppression','D':'Hyperprolactinemic hypogonadism','E':'Peripheral gonadotropin-independent puberty'}
        p['evidence_map']=[{
            'option':o,'claim':t,'rationale':rationales[o],'source_ids':source_ids[o],
            'evidence_basis':'LIVE_SOURCE_REVIEW_SAME_REVIEWER_NOT_INDEPENDENT_CERTIFICATION',
            'audit_record':'audit/'+AUDIT+'.md','target_diagnosis_or_process':diagnoses[o],
            'target_mechanism':t
        } for o,t in p['item']['options'].items()]
        p['sources']=[
            {
                'source_id':'S1','title':'Puberty','url':'https://medlineplus.gov/puberty.html',
                'agency':'National Library of Medicine (NIH) — MedlinePlus','government_status_verified':True,
                'publication_or_revision_date':'Last updated June 9, 2026','retrieved_at':'2026-09-20',
                'section_locator':'Summary: normal age range, first sign in girls, and growth spurt',
                'supporting_passage':'The normal range in girls is 8–13 years; breast development is usually the first sign, and a growth spurt occurs during puberty.',
                'passage_type':'Reviewer paraphrase, not a verbatim quotation','raw_source_sha256':'ada22b7553bc55a6192481169cec64cfa1572d98da76817539f9aa2809089c59',
                'raw_capture_record':'audit/live_20260919/SOURCE_AVAILABILITY.json','set_id_applicability':'NOT_APPLICABLE_NON_DRUG_SOURCE',
                'rights_status':'Official U.S. federal health-information source; facts used for original synthesis.'
            },
            {
                'source_id':'S2','title':'What causes normal puberty, precocious puberty, & delayed puberty?',
                'url':'https://www.nichd.nih.gov/health/topics/puberty/conditioninfo/causes',
                'agency':'Eunice Kennedy Shriver National Institute of Child Health and Human Development (NIH)','government_status_verified':True,
                'publication_or_revision_date':'Last reviewed June 21, 2021','retrieved_at':'2026-09-20',
                'section_locator':'Normal Puberty; Peripheral Precocious Puberty',
                'supporting_passage':'Hypothalamic GnRH stimulates pituitary LH and FSH, which signal gonadal sex-hormone release. Gonadotropin-independent puberty can arise from ovarian, testicular, or adrenal sex-hormone overproduction.',
                'passage_type':'Reviewer paraphrase, not a verbatim quotation','raw_source_sha256':'e2ba514cfe0073081608a212270cda218caa592fa3cd386fcb5a60e25f6e84c9',
                'raw_capture_record':'audit/'+AUDIT+'.md','raw_capture_bytes':244813,'set_id_applicability':'NOT_APPLICABLE_NON_DRUG_SOURCE',
                'rights_status':'Official U.S. federal health-information source; facts used for original synthesis.'
            },
            {
                'source_id':'S3','title':'Normal and Abnormal Puberty','url':'https://www.ncbi.nlm.nih.gov/books/NBK279024/',
                'agency':'Krishna and Witchel, Endotext (MDText.com), hosted by NCBI Bookshelf','government_status_verified':False,
                'hosting_status':'Hosted by the U.S. National Library of Medicine; authored and published by non-federal third parties.',
                'publication_or_revision_date':'Last update April 9, 2024','retrieved_at':'2026-09-20',
                'section_locator':'Abstract; Introduction; Clinical Features of Normal Pubertal Development; Treatment of central precocious puberty — Gonadotropin-Releasing Hormone Analogs; Functional Hypogonadotropic Hypogonadism; Peripheral Precocious Puberty',
                'supporting_passage':'Pubertal onset involves re-emergent pulsatile GnRH signaling; adrenarche is distinct from gonadarche; long-acting GnRH agonists downregulate pituitary receptors; elevated prolactin inhibits gonadotropin release; peripheral puberty is gonadotropin-independent.',
                'passage_type':'Reviewer paraphrase, not a verbatim quotation','raw_source_sha256':'2d098d006e01cecd115739f0225830535778b081d8df2ef4e2b8087f90960d22',
                'raw_capture_record':'audit/live_20260919/SOURCE_AVAILABILITY.json','set_id_applicability':'NOT_APPLICABLE_NON_DRUG_SOURCE',
                'rights_status':'Third-party educational chapter; facts paraphrased into original item content.'
            }
        ]
        p['semantic_fingerprint'].update(
            correct_answer_concept=p['item']['options']['B'],mechanism=p['item']['tested_construct'],tested_construct=p['item']['tested_construct'],
            essential_clues=['age 13 years','breast development followed by growth acceleration','healthy adolescent without medication exposure'],
            reasoning_chain=['Recognize a normal adolescent sequence consistent with gonadarche.','Identify pulsatile hypothalamic GnRH as the signal that activates pituitary LH/FSH secretion.'],
            distractor_misconceptions=['equating adrenarche with HPG-axis activation','assuming sustained GnRH exposure stimulates the axis indefinitely','confusing prolactin-mediated suppression with initiation','confusing peripheral estrogen production with central gonadarche'])
        historical=p.setdefault('historical_audit_metadata',{})
        for field in ('author_self_audit','step2_final_audit','hashes'):
            if field in p: historical[field]=p.pop(field)
        p['current_reaudit']={
            'audit_id':AUDIT,'status':'BLOCKED_PENDING_FULL_REAUDIT','full_clinical_certification':False,
            'same_reviewer_content_passes':2,'independent_blind_passes':0,
            'corrections':['Replace noncanonical blueprint path and align age with its 13–17 year category','Replace generic/remote distractors with verified endocrine alternatives','Bind pulsatile GnRH claim to a source that actually states pulsatility','Correct federal-versus-hosted-third-party source attribution','Replace generic moderate difficulty with item-specific easy author estimate','Isolate obsolete PASS metadata as historical'],
            'remaining_gates':['Independent isolated author/auditor workflow required by README','Exhaustive semantic comparison beyond targeted candidate screening']
        }
        assert p['item']['intended_key']=='B' and set(p['item']['options'])==set('ABCDE')
        rh={'candidate_id':CID,'verdict':'BLOCKED_PENDING_FULL_REAUDIT','payload_sha256':digest(p),'prior_review_sha256':review['review_sha256'],
            'reviewed_at':'2026-09-20','audit_record':'audit/'+AUDIT+'.md','review_scope':'Live source review, clinical repair and same-reviewer adversarial reread; not independent certification','defects':p['current_reaudit']['remaining_gates']}
        archive={'item_row':old,'review_row':review}
        if archive_path.exists(): assert json.loads(archive_path.read_text())==archive
        else: archive_path.write_text(json.dumps(archive,indent=2)+'\n')
        db.execute('UPDATE step2_final_items SET payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? WHERE candidate_id=?',(canon(p),digest(p),digest(rh),rh['verdict'],'2026-09-20',CID))
        db.execute('UPDATE step2_final_reviews SET review_json=?,review_sha256=?,final_status=?,finalized_at=? WHERE candidate_id=?',(canon(rh),digest(rh),rh['verdict'],'2026-09-20',CID))
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    result={'candidate_id':CID,'before_sha256':EXPECTED,'after_sha256':digest(p),'status':rh['verdict'],'new_final_passes':0,'item_count':1635}
    (ROOT/'audit'/(AUDIT+'_RESULT.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
