#!/usr/bin/env python3
import importlib.util, json, pathlib, sqlite3
from collections import Counter

HERE=pathlib.Path(__file__).resolve().parent
TARGET=HERE/'step2_import_q1191_q1215.py'
spec=importlib.util.spec_from_file_location('q1191_q1215_strict',TARGET)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Derive aggregate expectations from the exact staged specs only after proving
# item-by-item concordance with the recorded FINAL_10_10 official-discipline audits.
specs=mod.load_specs()
for n,x in specs.items():
    ap=HERE/'audit'/f'Q{n:04d}_FINAL_10_10_AUDIT.json'
    a=json.loads(ap.read_text())
    audited=a['official_discipline_gate']['tags']
    assert sorted(x['disciplines'])==sorted(audited),(n,x['disciplines'],audited)
    assert a['official_discipline_gate']['status']=='PASS'
    assert a['official_discipline_gate']['all_tags_in_usmle_table3'] is True

con=sqlite3.connect(HERE/'data'/'usmle-step1.db')
rows=con.execute("SELECT payload_json FROM step2_final_items WHERE final_status='FINAL_10_10_PASS'").fetchall()
con.close()
assert len(rows)==1190
base_payloads=[json.loads(r[0]) for r in rows]
base_bp=Counter(p['blueprint']['primary_system'] for p in base_payloads)
base_cp=Counter(p['blueprint']['primary_competency'] for p in base_payloads)
add_bp=Counter(x['system'] for x in specs.values())
add_cp=Counter(x['primary_competency'] for x in specs.values())
new_disc=Counter()
for x in specs.values(): new_disc.update(x['disciplines'])

mod.EXPECTED_BLUEPRINT=dict(base_bp+add_bp)
mod.EXPECTED_COMPETENCIES=dict(base_cp+add_cp)
mod.EXPECTED_NEW_DISCIPLINES={d:new_disc.get(d,0) for d in mod.OFFICIAL_DISCIPLINES}

# Independent arithmetic guard against silently changing the staged competency mix.
assert mod.EXPECTED_COMPETENCIES=={
 'Medical Knowledge: Applying Foundational Science Concepts':821,
 'Patient Care: Diagnosis, including history and physical examination':243,
 'Practice-Based Learning and Improvement':66,
 'Communication and Interpersonal Skills':85,
},mod.EXPECTED_COMPETENCIES
assert mod.EXPECTED_NEW_DISCIPLINES=={
 'Pathology':10,
 'Physiology':14,
 'Nutrition':0,
 'Gross Anatomy & Embryology':1,
 'Microbiology':0,
 'Pharmacology':0,
 'Behavioral Sciences':5,
 'Biochemistry':9,
 'Histology & Cell Biology':2,
 'Immunology':0,
 'Genetics':20,
},mod.EXPECTED_NEW_DISCIPLINES

print(json.dumps({
 'derived_blueprint':mod.EXPECTED_BLUEPRINT,
 'derived_competencies':mod.EXPECTED_COMPETENCIES,
 'derived_new_disciplines':mod.EXPECTED_NEW_DISCIPLINES,
 'spec_audit_discipline_concordance':'PASS'
},sort_keys=True))
mod.main()
