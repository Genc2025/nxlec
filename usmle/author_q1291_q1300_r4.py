#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'batch_specs_1201_1300'/'12_q1291_q1300_author_20260906.json'
# Rebuild the prior R3 candidate from source first, then replace only the blocked Q1293 construct.
runpy.run_path(str(ROOT/'author_q1291_q1300_r3.py'),run_name='__main__')
spec=importlib.util.spec_from_file_location('author_base',ROOT/'author_q1291_q1300.py')
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
q=base.make(
 n=1293,system=base.SOC,comp=base.COMM,
 path=['Research ethics','IRB composition for prisoner research'],disc=['Behavioral Sciences'],
 coverage='45 CFR 46.304 prisoner/prisoner-representative IRB composition safeguard',
 vignette='An HHS-supported prospective study will enroll adults incarcerated in a state prison to compare two counseling programs for opioid use disorder. The institutional review board meets the general Common Rule composition requirements, and a majority of the board has no association with the prison apart from board membership. However, none of the current members is a prisoner or has the background and experience to serve as a prisoner representative. The board is preparing to review the protocol under 45 CFR part 46, subpart C.',
 lead='Which change is required before this IRB can carry out its responsibilities for this prisoner-research protocol?',
 options={
  'A':'Add a correctional officer who is familiar with daily prison operations',
  'B':'Add a physician who provides clinical care at the prison',
  'C':'Add an unaffiliated bioethicist with no prior correctional-system experience',
  'D':'Add at least one prisoner or prisoner representative with appropriate background and experience',
  'E':'Require every nonprisoner IRB member to have no association with the prison'},
 key='D',
 tested='Under 45 CFR 46.304, an IRB carrying out responsibilities for HHS-regulated research involving prisoners must satisfy special composition safeguards: a majority of the Board, exclusive of prisoner members, must have no association with the involved prison apart from Board membership, and at least one member must be a prisoner or an appropriately experienced prisoner representative.',
 keyexp='The stem already satisfies the majority-unaffiliated requirement. The missing Subpart C safeguard is at least one IRB member who is a prisoner or a prisoner representative with appropriate background and experience. A prison employee or a generally unaffiliated expert does not automatically satisfy that specific representational requirement.',
 obj='Identify the special IRB composition requirement for HHS-supported research involving prisoners under 45 CFR 46.304.',
 anchor='HHS-supported prisoner research in which the majority-unaffiliated requirement is already satisfied but no prisoner or qualified prisoner representative serves on the IRB',
 refs=[
  base.O(1293,2,'Electronic Code of Federal Regulations','45 CFR 46.304 — Composition of Institutional Review Boards where prisoners are involved','https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-C/section-46.304','current eCFR; verified 2026-09-06','45 CFR 46.304(a)-(b)','For an IRB reviewing prisoner research under Subpart C, a majority of the Board exclusive of prisoner members must have no association with the involved prison apart from Board membership, and at least one Board member must be a prisoner or prisoner representative with appropriate background and experience.'),
  base.S(1293,3,'Conducting Ethical Research with Correctional Populations: Do Researchers and IRB Members Know the Federal Regulations?','26097498','2014','Research in correctional settings is governed by specific federal rules designed to protect incarcerated participants; the study surveyed IRB prisoner representatives, IRB members and chairs, and researchers and found important knowledge gaps regarding those federal requirements.')],
 fingerprint=['45 CFR 46.304','prisoner research','prisoner representative','IRB composition','Subpart C'],
 wrong={
  'A':'A correctional officer is not, by that role alone, a prisoner or an appropriately experienced prisoner representative, so adding one does not satisfy the specific Subpart C representation requirement.',
  'B':'A prison clinician may contribute medical expertise but is not automatically a prisoner or prisoner representative and therefore does not supply the missing required representation.',
  'C':'An unaffiliated bioethicist can strengthen ethical review, but general independence does not substitute for the regulation’s specific requirement for a prisoner or appropriately experienced prisoner representative.',
  'E':'The regulation requires a majority of the Board, exclusive of prisoner members, to lack prison association; it does not require every nonprisoner member to be unaffiliated, and the stem already states that the majority condition is met.'},steps=4)
b=json.loads(OUT.read_text())
items=b['items']; idx=[i for i,x in enumerate(items) if x['num']==1293]
if idx!=[2]: raise SystemExit(f'unexpected Q1293 position: {idx}')
items[2]=q
if ''.join(x['item']['intended_key'] for x in items)!='CADBEBDACE': raise SystemExit('key sequence changed')
if [x['num'] for x in items]!=list(range(1291,1301)): raise SystemExit('range changed')
b['repair_history']=[{'item':'Q1293','reason':'readonly audit found material canonical construct collision with Q1171 effective-communication item','repair':'replaced with clean 45 CFR 46.304 prisoner-research IRB-composition construct','canonical_pre_count':1290}]
OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':'PASS','repair':'Q1293_REPLACED','items':len(items),'keys':'CADBEBDACE','output':str(OUT.relative_to(ROOT.parent))},ensure_ascii=False))
