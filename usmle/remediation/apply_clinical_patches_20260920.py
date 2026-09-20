"""Apply reviewed corrections without inheriting a previous FINAL verdict."""
import hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def main():
 package=json.loads((ROOT/'remediation/CLINICAL_Q0001_Q0050_PATCHES_20260919.json').read_text())
 c=sqlite3.connect(ROOT/'data/usmle-step1.db');c.row_factory=sqlite3.Row
 archive=[];summary=[]
 try:
  c.execute('BEGIN IMMEDIATE')
  for change in package['patches']:
   cid=change['candidate_id'];old=c.execute('select * from step2_final_items where candidate_id=?',(cid,)).fetchone();review=c.execute('select * from step2_final_reviews where candidate_id=?',(cid,)).fetchone()
   assert old and review,cid
   assert old['payload_sha256']==change['expected_payload_sha256']==digest(json.loads(old['payload_json'])),cid
   p=change['replacement_payload'];assert p['candidate_id']==cid
   assert p['item']['intended_key']==json.loads(old['payload_json'])['item']['intended_key']
   assert set(p['item']['options'])==set('ABCDE')
   archive.append({'item_row':dict(old),'review_row':dict(review)})
   rh={'candidate_id':cid,'verdict':'BLOCKED_PENDING_FULL_REAUDIT','review_scope':'Specific clinical and metadata corrections; complete evidence gate remains open','repairs':change['reasons'],'prior_review_sha256':review['review_sha256'],'payload_sha256':digest(p),'reviewed_at':'2026-09-20','defects':['Complete live source binding, independent second pass and full-bank duplicate review remain pending']}
   c.execute('update step2_final_items set payload_json=?,payload_sha256=?,audit_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(p),digest(p),digest(rh),rh['verdict'],'2026-09-20',cid))
   c.execute('update step2_final_reviews set review_json=?,review_sha256=?,final_status=?,finalized_at=? where candidate_id=?',(canon(rh),digest(rh),rh['verdict'],'2026-09-20',cid))
   summary.append({'candidate_id':cid,'before_sha256':old['payload_sha256'],'after_sha256':digest(p),'corrections':change['reasons']})
  assert len(summary)==8
  assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
  c.commit()
 except:
  c.rollback();raise
 assert c.execute('select count(*) from step2_final_items').fetchone()[0]==1635
 for cid,pj,ph,ah in c.execute('select candidate_id,payload_json,payload_sha256,audit_sha256 from step2_final_items'):
  assert digest(json.loads(pj))==ph
 c.close()
 (ROOT/'remediation/CLINICAL_Q0001_Q0050_BEFORE_ROWS_20260920.json').write_text(json.dumps(archive,indent=2)+'\n')
 report={'status':'LIMITED_CORRECTIONS_APPLIED_FULL_AUDIT_PENDING','corrected_items':8,'new_FINAL_QA_PASS_count':0,'changes':summary,'sqlite_integrity':'ok','item_count':1635}
 (ROOT/'audit/CLINICAL_Q0001_Q0050_CORRECTIONS_20260920.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='changes'}))
if __name__=='__main__':main()
