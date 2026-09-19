"""Complete per-record inventory and honest coverage ledger, not clinical certification."""
import collections, hashlib, json, re, sqlite3
from pathlib import Path
from urllib.parse import urlparse
from audit_full_canonical_compliance import criteria_defects, review_hash_valid, hobj
ROOT=Path(__file__).resolve().parent
PAIRS=[
(9,306,'DUPLICATE','Same menstrual blood loss, pica, iron studies, diagnostic task and iron-deficiency key.'),
(20,317,'DUPLICATE','Same postdiarrheal ascending areflexic weakness and Guillain-Barre diagnosis.'),
(264,966,'DUPLICATE','Both ask for CCK after a fatty meal with gallbladder contraction; extra secretory findings do not change the task.'),
(744,1102,'DUPLICATE','Same RYR2 exercise-triggered bidirectional ventricular tachycardia and diastolic SR calcium release mechanism.'),
(10,403,'DUPLICATE','Same B12-pattern megaloblastic anemia plus neurologic findings and elevated methylmalonic acid task.'),
(18,318,'DUPLICATE','Virtually same ocular fatigability vignette and postsynaptic nicotinic ACh-receptor target.'),
(89,90,'DISTINCT','Sensitivity in reference-positive patients versus specificity in reference-negative patients. Independently calculated 90/100=90% and 170/200=85%; these are different constructs.'),
(186,482,'DISTINCT','Corneal clouding versus its absence distinguishes MPS I/alpha-L-iduronidase from MPS II/iduronate-2-sulfatase; distinct keyed enzymes.'),
(1025,1116,'RELATED_DISTINCT_TASK','Same lateral-medullary syndrome context, but diagnosis versus nucleus-ambiguus localization. Shared stem remains a reuse concern for test assembly.'),
(135,230,'DISTINCT','Metaphyseal sunburst osteosarcoma versus diaphyseal onion-skin Ewing sarcoma; distinct diagnoses.'),
(797,1124,'DUPLICATE','Both ask how primary aldosterone excess increases ENaC-mediated potassium secretion.'),
(771,1065,'DUPLICATE','Both ask for the neonatal LA-over-RA pressure change closing the foramen ovale.'),
(193,799,'DUPLICATE','Same 20%-to-10% trial and NNT calculation. Independently calculated 1/(0.20-0.10)=10.'),
(703,1184,'DUPLICATE','Same BSND renal salt wasting/deafness phenotype and barttin-dependent ClC-Ka/Kb mechanism.'),
(53,791,'DUPLICATE','Same SLC12A1 Bartter phenotype and NKCC2 transporter-identification task.'),
(1418,1511,'DUPLICATE','Same concizumab plasma assay, TFPI reduction, FXa/thrombin increase and TFPI-antagonism key.'),
(263,965,'DUPLICATE','Same acidic duodenal chyme, bicarbonate response and secretin identification.'),
(21,323,'DUPLICATE','Same progressive amnestic dementia and extracellular amyloid/intracellular tau pathology task.')]
def main():
 db=ROOT/'data/usmle-step1.db';c=sqlite3.connect(f'file:{db}?mode=ro',uri=True)
 rows=c.execute('select candidate_id,payload_json,payload_sha256,audit_sha256,final_status from step2_final_items order by candidate_id').fetchall()
 reviews={cid:(json.loads(j),h) for cid,j,h in c.execute('select candidate_id,review_json,review_sha256 from step2_final_reviews')}
 dupmap=collections.defaultdict(list)
 for a,b,status,reason in PAIRS:
  if status=='DUPLICATE':dupmap[a].append(b);dupmap[b].append(a)
 records=[];counts=collections.Counter(); urls=set(); hostcounts=collections.Counter()
 for cid,j,sha,ah,status in rows:
  p=json.loads(j);q=int(cid.split('-')[2]);gaps=criteria_defects(p); flags=[]
  for s in p.get('sources',[]):
   u=s.get('url','');urls.add(u);host=(urlparse(u).hostname or '').lower();hostcounts[host]+=1
   loc=str(s.get('section_locator') or s.get('source_locator') or '')
   if re.search(r'relevant (disease|mechanism)|disease overview|relevant section',loc,re.I):flags.append('generic_locator_needs_exact_section')
   if s.get('government_status_verified') is True and host in ('www.usmle.org','usmle.org','www.nbme.org','nbme.org','www.fsmb.org','fsmb.org'):flags.append('exam_source_mislabeled_as_government')
   if 'statpearls' in str(s.get('title','')).lower() and s.get('government_status_verified') is True:flags.append('hosted_third_party_source_mislabeled_as_government')
  basis=p.get('item',{}).get('difficulty_basis','')
  if basis in ('Requires applied Step 1 foundational reasoning beyond simple recall.','Difficulty assigned during the documented fresh item-by-item clinical audit.','Requires linking vignette clues to a foundational mechanism, pathway, structure, or reaction.','Requires integrating multiple clinical clues to select a single best diagnosis.','Requires correct formula selection plus calculation/interpretation.'):flags.append('boilerplate_difficulty_basis_needs_item_specific_review')
  if q in dupmap:flags.append('confirmed_semantic_duplicate')
  if hobj(p)!=sha:flags.append('payload_hash_mismatch')
  rev,rsha=reviews[cid]
  if not review_hash_valid(rev,rsha) or rsha!=ah:flags.append('review_hash_mismatch')
  flags=sorted(set(flags));counts.update(flags)
  records.append({'q':q,'candidate_id':cid,'payload_sha256':sha,'stored_final_status':status,'automated_screen':'COMPLETE','stored_contract_gaps':gaps,'additional_findings':flags,'duplicate_with':dupmap[q],'full_live_clinical_reaudit':'NOT_COMPLETED','current_audit_verdict':'BLOCKED' if gaps or flags or status!='FINAL_10_10_PASS' else 'PENDING_CLINICAL_REVIEW'})
 assert len(records)==1635 and [r['q'] for r in records]==list(range(1,1636))
 out={'audit_id':'ALL-ITEMS-20260919','scope':'All 1635 canonical records plus inventory of the five staged Q1636-Q1640 candidates','status':'BLOCKED_INCOMPLETE_CLINICAL_REAUDIT','production_promotion_ready':False,'count':len(records),'sqlite_integrity':c.execute('pragma integrity_check').fetchone()[0],'automated_records_checked':len(records),'fully_reaudited_against_live_sources':0,'new_FINAL_QA_PASS_count':0,'review_branch_only':True,'source_url_count':len(urls),'source_host_counts':dict(hostcounts),'additional_finding_counts':dict(counts),'confirmed_duplicate_pairs':sum(x[2]=='DUPLICATE' for x in PAIRS),'manually_compared_pairs':[dict(q1=a,q2=b,verdict=v,reason=r) for a,b,v,r in PAIRS],'pair_review_limit':'Only the 17 lexical candidates plus one exact-construct pair were manually compared. This is not exhaustive semantic comparison of all pairs and does not certify clinical correctness.','batches':[{'start':i,'end':min(i+49,1635),'count':min(50,1636-i),'clinical_audit':'PENDING'} for i in range(1,1636,50)],'records':records,'staged_candidates':{'path':'usmle/batch_specs_1601_1700/08_q1636_q1640_author_20260919.json','status':'STAGED_NOT_INCLUDED_IN_CANONICAL_COUNT','full_clinical_reaudit':'NOT_COMPLETED'},'source_metadata_note':'Missing hashes document absent frozen evidence, not false medicine. Government hosting does not establish government authorship. Old review labels do not establish a current independent re-audit.'}
 (ROOT/'audit/ALL_ITEMS_20260919_COVERAGE.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k in ('count','status','automated_records_checked','fully_reaudited_against_live_sources','confirmed_duplicate_pairs','additional_finding_counts')}))
if __name__=='__main__':main()
