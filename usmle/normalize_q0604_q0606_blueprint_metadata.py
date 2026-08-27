#!/usr/bin/env python3
import hashlib, json, pathlib, re, sqlite3
from collections import Counter
from datetime import datetime, timezone

ROOT=pathlib.Path(__file__).resolve().parent
DB=ROOT/'data'/'usmle-step1.db'
AUDIT_DIR=ROOT/'audit'
STATE=ROOT/'state'/'step2_final_q0001_q0610.json'
FINAL_AUDIT=AUDIT_DIR/'STEP2_FINAL_10_10_Q0001_Q0610.json'
NOW=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

FIXES={
    604:('Reproductive & Endocrine Systems','Reproductive and Endocrine Systems'),
    605:('Respiratory & Renal/Urinary Systems','Respiratory and Renal/Urinary Systems'),
    606:('Behavioral Health, Nervous Systems & Special Senses','Behavioral Health, Nervous Systems and Special Senses'),
}

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def sha_text(s):
    return hashlib.sha256(s.encode()).hexdigest()

def hash_obj(o):
    return sha_text(canon(o))

def qnum(cid):
    m=re.search(r'DIRECT-(\d{4})',cid or '')
    if not m:
        raise SystemExit('bad candidate id '+str(cid))
    return int(m.group(1))

def load_audit(n):
    p=AUDIT_DIR/f'Q{n:04d}_FINAL_10_10_AUDIT.json'
    a=json.loads(p.read_text())
    if a.get('item')!=f'Q{n:04d}' or a.get('status')!='FINAL_10_10_PASS' or a.get('unresolved_conflicts')!=0:
        raise SystemExit(f'Q{n:04d}: audit precondition failure')
    return a,p

def main():
    con=sqlite3.connect(DB)
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
        raise SystemExit('pre integrity failure')

    items=con.execute("SELECT candidate_id,payload_json,payload_sha256,audit_sha256 FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
    reviews=con.execute("SELECT candidate_id,review_json,review_sha256 FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchall()
    if len(items)!=610 or len(reviews)!=610:
        raise SystemExit(f'expected 610 finals/reviews, got {len(items)}/{len(reviews)}')
    if {qnum(r[0]) for r in items}!=set(range(1,611)):
        raise SystemExit('pre Q0001-Q0610 coverage failure')
    if con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_items GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]!=0:
        raise SystemExit('pre duplicate items')
    if con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_reviews GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]!=0:
        raise SystemExit('pre duplicate reviews')

    item_map={qnum(cid):(cid,pj,ps,ash) for cid,pj,ps,ash in items}
    changed=[]
    try:
        con.execute('BEGIN IMMEDIATE')
        for n,(old_label,new_label) in FIXES.items():
            cid,pj,ps,ash=item_map[n]
            payload=json.loads(pj)
            if hash_obj(payload)!=ps:
                raise SystemExit(f'Q{n:04d}: pre payload hash failure')

            bp=payload.get('blueprint',{})
            outline=bp.get('official_outline_path')
            if bp.get('primary_system')!=old_label:
                raise SystemExit(f'Q{n:04d}: expected stale primary_system {old_label!r}, got {bp.get("primary_system")!r}')
            if not isinstance(outline,list) or not outline or outline[0]!=old_label:
                raise SystemExit(f'Q{n:04d}: expected stale outline[0] {old_label!r}, got {outline!r}')

            rr=con.execute('SELECT review_json,review_sha256,final_status FROM step2_final_reviews WHERE candidate_id=?',(cid,)).fetchone()
            if not rr or rr[1]!=ash or rr[2]!='FINAL_10_10_PASS':
                raise SystemExit(f'Q{n:04d}: pre review link failure')
            review=json.loads(rr[0])
            if review.get('review_sha256')!=rr[1]:
                raise SystemExit(f'Q{n:04d}: embedded review hash mismatch')

            audit,audit_path=load_audit(n)
            if audit.get('blueprint',{}).get('system')!=new_label:
                raise SystemExit(f'Q{n:04d}: normalized audit label mismatch')
            audit_hash=hash_obj(audit)

            payload['blueprint']['primary_system']=new_label
            payload['blueprint']['official_outline_path'][0]=new_label
            payload.setdefault('step2_final_audit',{})['clinical_audit_sha256']=audit_hash

            review['clinical_audit']=audit
            review['clinical_audit_sha256']=audit_hash
            review['clinical_audit_path']=str(audit_path.relative_to(ROOT))
            review.pop('review_sha256',None)
            new_review_hash=hash_obj(review)
            review['review_sha256']=new_review_hash
            payload['step2_final_audit']['review_sha256']=new_review_hash

            new_payload_json=canon(payload)
            new_payload_hash=hash_obj(payload)

            con.execute(
                'UPDATE step2_final_items SET payload_json=?,payload_sha256=?,audit_sha256=?,finalized_at=? WHERE candidate_id=?',
                (new_payload_json,new_payload_hash,new_review_hash,NOW,cid)
            )
            con.execute(
                'UPDATE step2_final_reviews SET review_json=?,review_sha256=?,finalized_at=? WHERE candidate_id=?',
                (canon(review),new_review_hash,NOW,cid)
            )
            changed.append({
                'qnum':n,
                'candidate_id':cid,
                'from':old_label,
                'to':new_label,
                'clinical_audit_sha256':audit_hash,
                'review_sha256':new_review_hash,
                'payload_sha256':new_payload_hash
            })

        all_rows=con.execute("SELECT candidate_id,payload_json FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
        all_payloads=[json.loads(pj) for _,pj in all_rows]
        all_payloads.sort(key=lambda x:qnum(x['candidate_id']))
        key_hash=sha_text(''.join(c['item']['intended_key'] for c in all_payloads))
        rev_rows=con.execute("SELECT candidate_id,review_sha256 FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchall()
        aggregate_review_hash=sha_text(''.join(rh for cid,rh in sorted(rev_rows,key=lambda x:qnum(x[0]))))
        con.execute(
            'UPDATE step2_finalization SET key_schedule_sha256=?,aggregate_review_sha256=?,item_count=?,finalized_at=? WHERE id=1',
            (key_hash,aggregate_review_hash,610,NOW)
        )
        con.commit()
    except:
        con.rollback()
        raise

    if len(changed)!=3:
        raise SystemExit(f'expected exactly 3 changed records, got {len(changed)}')
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
        raise SystemExit('post integrity failure')
    if con.execute("SELECT COUNT(*) FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchone()[0]!=610:
        raise SystemExit('post item count failure')
    if con.execute("SELECT COUNT(*) FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'").fetchone()[0]!=610:
        raise SystemExit('post review count failure')
    if con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_items GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]!=0:
        raise SystemExit('post duplicate items')
    if con.execute('SELECT COUNT(*) FROM (SELECT candidate_id FROM step2_final_reviews GROUP BY candidate_id HAVING COUNT(*)>1)').fetchone()[0]!=0:
        raise SystemExit('post duplicate reviews')

    item_ids={r[0] for r in con.execute("SELECT candidate_id FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'")}
    review_ids={r[0] for r in con.execute("SELECT candidate_id FROM step2_final_reviews WHERE final_status='FINAL_10_10_PASS'")}
    if item_ids!=review_ids or {qnum(x) for x in item_ids}!=set(range(1,611)):
        raise SystemExit('post item/review/coverage mismatch')

    reread=0
    patched_reread=0
    payloads=[]
    for cid,pj,ps,ash in con.execute("SELECT candidate_id,payload_json,payload_sha256,audit_sha256 FROM step2_final_items WHERE final_status='FINAL_10_10_PASS' ORDER BY candidate_id"):
        obj=json.loads(pj)
        if hash_obj(obj)!=ps:
            raise SystemExit(cid+' payload reread hash failure')
        rr=con.execute('SELECT review_json,review_sha256,final_status FROM step2_final_reviews WHERE candidate_id=?',(cid,)).fetchone()
        if not rr or rr[1]!=ash or rr[2]!='FINAL_10_10_PASS':
            raise SystemExit(cid+' review reread link failure')
        rev=json.loads(rr[0])
        if rev.get('review_sha256')!=rr[1]:
            raise SystemExit(cid+' embedded review hash failure')
        if obj.get('step2_final_audit',{}).get('review_sha256')!=rr[1]:
            raise SystemExit(cid+' payload/review hash link failure')
        if len(obj.get('item',{}).get('options',{}))!=5 or len(set(obj['item']['options'].values()))!=5:
            raise SystemExit(cid+' option integrity failure')
        for src in obj.get('sources',[]):
            if not src.get('section_locator') or src.get('section_locator')=='Relevant claim-specific disease/mechanism section':
                raise SystemExit(cid+' source locator failure')
        n=qnum(cid)
        if n in FIXES:
            expected=FIXES[n][1]
            if obj.get('blueprint',{}).get('primary_system')!=expected:
                raise SystemExit(cid+' normalized primary_system reread failure')
            if obj.get('blueprint',{}).get('official_outline_path',[None])[0]!=expected:
                raise SystemExit(cid+' normalized outline reread failure')
            audit,_=load_audit(n)
            if rev.get('clinical_audit')!=audit:
                raise SystemExit(cid+' packaged clinical audit reread mismatch')
            if rev.get('clinical_audit_sha256')!=hash_obj(audit):
                raise SystemExit(cid+' clinical audit hash reread mismatch')
            patched_reread+=1
        payloads.append(obj)
        reread+=1

    if reread!=610 or patched_reread!=3:
        raise SystemExit(f'reread failure total={reread} patched={patched_reread}')

    blueprint_counts=dict(Counter(c['blueprint']['primary_system'] for c in payloads))
    stale=[k for k in blueprint_counts if ' & ' in k]
    if stale:
        raise SystemExit(f'stale blueprint categories remain: {stale}')

    competency_counts=dict(Counter(c['blueprint']['primary_competency'] for c in payloads))
    old_state=json.loads(STATE.read_text())
    result={
        'audit_id':old_state.get('audit_id','STEP2-FINAL-Q0001-Q0610-20260827'),
        'final_status':'FINAL_10_10_PASS',
        'item_count':610,
        'authoritative_final_table':'step2_final_items',
        'step2_final_review_count':610,
        'new_block':old_state.get('new_block',{
            'range':'Q0601-Q0610','item_count':10,'clinical_audit_files_verified':10,'fresh_item_by_item_audit':True
        }),
        'answer_position_new_block':old_state['answer_position_new_block'],
        'blueprint_counts':blueprint_counts,
        'competency_counts':competency_counts,
        'sqlite_integrity_check':'ok',
        'duplicate_candidate_id_count':0,
        'payload_review_consistency':'PASS',
        'reread_verified_count':610,
        'new_block_reread_verified_count':10,
        'metadata_normalization':{
            'status':'PASS',
            'changed_record_count':3,
            'records':changed,
            'stale_ampersand_category_count':0
        },
        'finalized_at':NOW
    }
    STATE.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    FINAL_AUDIT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
