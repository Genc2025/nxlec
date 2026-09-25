"""Reproducible limited repairs in an isolated review branch; never assigns FINAL."""
import copy, hashlib, json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data/usmle-step1.db'
sys.path.insert(0,str(ROOT))
from audit_all_items_20260919 import PAIRS
DUPLICATES={}
for a,b,status,reason in PAIRS:
 if status=='DUPLICATE':DUPLICATES[a]=(b,reason);DUPLICATES[b]=(a,reason)
EXPECTED='92a3aeb4588fa3a1677c2edf5f79a611fdccd8ed'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 assert blob(DB)==EXPECTED,'Source changed; rebase and re-audit before applying'
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
 before=[];changes=[]
 for row in c.execute('select * from step2_final_items order by candidate_id').fetchall():
  cid=row['candidate_id'];q=int(cid.split('-')[2])
  if q not in {21,667,669}|set(DUPLICATES):continue
  old=dict(row);review=dict(c.execute('select * from step2_final_reviews where candidate_id=?',(cid,)).fetchone())
  p=json.loads(row['payload_json']);before.append({'item_row':old,'review_row':review})
  details=[]
  if q in (667,669):
   source=p['sources'][2];assert not source.get('setid')
   setid={667:'e5c21813-4714-4f23-be8b-765bd58f63b3',669:'3c5101a0-0c7e-4078-8dc3-a57beb9a0e92'}[q]
   assert setid in source['url'];source['setid']=setid
   details.append({'field':'sources[2].setid','before':None,'after':setid,'evidence_url':source['url'],'verification_scope':'Label identity and SetID only; not full item revalidation','verified_on':'2026-09-19'})
  elif q==21:
   old_option=p['item']['options']['D'];assert old_option=='Spongiform change caused by bacterial toxin'
   p['item']['options']['D']='Spongiform change associated with misfolded prion protein'
   rat='Incorrect. Prion disease causes spongiform change and usually progresses over months; the five-year progressive amnestic course is more consistent with Alzheimer disease.'
   p['explanation']['distractor_explanations']['D']=rat
   source={'source_id':'AUDIT-20260919-CDC-CJD','title':'Classic Creutzfeldt-Jakob Disease','agency':'Centers for Disease Control and Prevention','url':'https://www.cdc.gov/creutzfeldt-jakob/about/index.html','section_locator':'Overview; How it affects your body','publication_or_revision_date':'2026-01-21','retrieved_at':'2026-09-19','supporting_passage':'Misfolded prion proteins cause CJD; the illness typically progresses to death within a year.','verification_scope':'D distractor mechanism and tempo only; complete item re-audit pending'}
   p['sources'].append(source)
   for e in p['evidence_map']:
    if e.get('option')=='D':
     e['claim']='Prion-associated spongiform change is a real pathology but is less consistent with this five-year clinical course.'
     e['rationale']=rat;e['source_ids']=[source['source_id']]
     e.pop('fresh_item_audit_verified',None)
   details.append({'field':'item.options.D and dependent rationale/evidence','before':old_option,'after':p['item']['options']['D'],'evidence_url':source['url'],'reason':'Replace fabricated bacterial-toxin mechanism with a real, clinically plausible distractor.'})
  if q in DUPLICATES:
   other,reason=DUPLICATES[q]
   details.append({'field':'current_duplicate_hold','duplicate_with':other,'reason':reason,'action':'BLOCKED; retained for rewrite or adjudication, not deleted'})
  p['current_reaudit']={'audit_id':'ALL-ITEMS-20260919','status':'BLOCKED_PENDING_FULL_REAUDIT','limited_repairs':details,'prior_final_certification_applies_to_prior_payload_only':True}
  new_review={'candidate_id':cid,'verdict':'BLOCKED_PENDING_FULL_REAUDIT','review_scope':'Limited evidence-backed correction; not a full clinical audit','prior_review_sha256':review['review_sha256'],'payload_sha256':digest(p),'reviewed_at':'2026-09-19','repairs':details,'defects':['Full independent claim-by-claim re-audit and remaining source verification not completed']+(['Confirmed semantic duplicate'] if q in DUPLICATES else []),'scores':None}
  changes.append({'candidate_id':cid,'before_payload_sha256':row['payload_sha256'],'after_payload_sha256':digest(p),'changes':details})
  c.execute('update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(p),digest(p),digest(new_review),'BLOCKED_PENDING_FULL_REAUDIT','2026-09-19',cid))
  c.execute('update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(new_review),digest(new_review),'BLOCKED_PENDING_FULL_REAUDIT','2026-09-19',cid))
 assert len(changes)==30
 c.commit();assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
 assert c.execute('select count(*) from step2_final_items').fetchone()[0]==1635
 c.close()
 (ROOT/'remediation/ALL_ITEMS_20260919_BEFORE_ROWS.json').write_text(json.dumps(before,indent=2)+'\n')
 (ROOT/'remediation/ALL_ITEMS_20260919_REPAIRS.json').write_text(json.dumps({'base_db_blob':EXPECTED,'candidate_db_blob':blob(DB),'status':'BLOCKED_PENDING_FULL_REAUDIT','production_promotion_ready':False,'changes':changes},indent=2)+'\n')
 print(json.dumps({'limited_content_or_metadata_repairs':3,'duplicate_holds':28,'total_changed_records':30,'new_final_certifications':0,'candidate_db_blob':blob(DB)}))
if __name__=='__main__':main()
