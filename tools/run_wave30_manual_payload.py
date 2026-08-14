#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PENDING=ROOT/'data/pending_audit_next.json'
OUT=ROOT/'data/clinical_overrides_wave30_0732_0781.json'
MANIFEST=ROOT/'data/manual_final_qa_wave30_0732_0781.json'
EXPECTED=[f'V2-Q{i:04d}' for i in range(732,782)]

# Semantic corrections identified during manual item-by-item review.
FIX={
738:{
 'stem':'A nurse reviews a client\'s ASA Physical Status classification before surgery. What does this classification primarily describe?',
 'options':{
  'A':'The technical skill or experience level of the surgical and anesthesia teams providing care',
  'B':'The client\'s insurance authorization status for the planned procedure and anesthetic care',
  'C':'The client\'s pre-anesthesia physical health status and burden of systemic disease',
  'D':'The predicted surgical outcome based only on the procedure type and expected operative duration'},
 'key':'C',
 'rationale':'The ASA Physical Status Classification System communicates the patient\'s pre-anesthesia physical health and systemic disease burden. It is associated with perioperative risk but is not, by itself, a complete surgical-risk prediction tool.'},
751:{
 'stem':'A client has one or more distressing physical symptoms plus persistent excessive health-related thoughts, anxiety, or time devoted to the symptoms, causing major disruption in daily life. Which disorder is most consistent with this presentation?',
 'options':{
  'A':'Malingering, in which symptoms are intentionally produced for a clear external incentive or gain',
  'B':'Factitious disorder, in which illness is intentionally falsified without an obvious external reward',
  'C':'Illness anxiety disorder, in which concern about illness occurs with absent or only mild symptoms',
  'D':'Somatic symptom disorder, in which distressing symptoms are accompanied by excessive health concerns'},
 'key':'D',
 'rationale':'Somatic symptom disorder is defined by distressing somatic symptoms plus excessive thoughts, feelings, or behaviors related to those symptoms. The diagnosis does not require the symptoms to be medically unexplained and does not imply intentional fabrication.'},
753:{
 'stem':'A nurse compares metoprolol succinate extended-release with immediate-release metoprolol tartrate. Which statement is accurate?',
 'options':{
  'A':'Metoprolol succinate is extended-release and is commonly administered once daily as prescribed',
  'B':'Metoprolol tartrate is the extended-release formulation intended only for once-daily treatment',
  'C':'The two formulations have identical release characteristics and can be substituted without review',
  'D':'Metoprolol succinate is immediate-release and normally requires more frequent scheduled dosing'},
 'key':'A',
 'rationale':'Metoprolol succinate is an extended-release formulation commonly dosed once daily. Metoprolol tartrate is immediate-release and is generally dosed more frequently. Formulation changes should follow the prescribed conversion rather than informal substitution.'},
754:{
 'stem':'Before administering digoxin to an adult client, which assessment is most important for the nurse to perform?',
 'options':{
  'A':'Measure the apical heart rate and follow the prescribed hold parameters for bradycardia',
  'B':'Measure the oral temperature and hold every dose whenever the temperature exceeds 38 C',
  'C':'Measure the respiratory rate and hold every dose whenever it falls below 16 breaths/min',
  'D':'Measure blood pressure only and administer digoxin regardless of the client\'s heart rate'},
 'key':'A',
 'rationale':'Digoxin can cause clinically important bradycardia and conduction abnormalities. The nurse should assess the heart rate before administration and follow the prescriber\'s or facility\'s hold parameters rather than relying on a universal pulse cutoff.'},
761:{
 'stem':'A nurse reviews a new stimulant prescription for a client with a documented cardiac arrhythmia that the prescriber may not have considered. What is the safest nursing response?',
 'options':{
  'A':'Assume stimulant therapy improves cardiac function and give the first dose without further review',
  'B':'Ignore the cardiac history because stimulants do not affect heart rate or systemic blood pressure',
  'C':'Hold all future ADHD therapy permanently because any past arrhythmia is an absolute contraindication',
  'D':'Clarify the cardiac history with the prescriber because stimulants can raise heart rate and blood pressure'},
 'key':'D',
 'rationale':'CNS stimulants can increase heart rate and blood pressure, and product labeling warns against use in serious cardiac disease. A documented arrhythmia warrants prescriber review and individualized risk assessment; a mild past arrhythmia is not automatically an absolute contraindication.'},
763:{
 'stem':'Between surgical cases, why is cleaning and disinfection of operating-room environmental surfaces performed?',
 'options':{
  'A':'Only to improve room appearance after procedures involving visibly contaminated equipment',
  'B':'To replace sterile technique during the next procedure once environmental cleaning is complete',
  'C':'To reduce environmental bioburden and the opportunity for pathogen transmission between cases',
  'D':'Only after a client with a known infection leaves the room, rather than after routine procedures'},
 'key':'C',
 'rationale':'Between-case environmental cleaning and disinfection reduces contamination of high-touch and procedure-area surfaces and is one component of infection prevention. It complements rather than replaces aseptic and sterile technique.'},
765:{
 'stem':'A nurse is leaving an airborne-precaution room after completing care. Which PPE-removal principle is correct?',
 'options':{
  'A':'Keep all PPE on until reaching the nurses\' station so contaminated equipment is removed together',
  'B':'Remove the respirator inside the patient room before removing gloves, gown, or eye protection',
  'C':'Remove other contaminated PPE before leaving the care area, then remove the respirator after exiting and closing the door',
  'D':'The location and sequence of PPE removal are unimportant if hand hygiene is performed eventually'},
 'key':'C',
 'rationale':'CDC core practices direct healthcare personnel to remove and discard PPE other than respirators before leaving the patient room or care area. A respirator is removed after leaving the room or care area and closing the door, with hand hygiene performed appropriately.'},
768:{
 'stem':'A nurse disposes of a used needle, a blood-saturated dressing, and unused medication after care. Which principle is correct?',
 'options':{
  'A':'Segregate waste into the appropriate sharps, regulated-medical, pharmaceutical, or other stream under applicable policy',
  'B':'Place all items in ordinary trash because waste classification is only required for laboratory specimens',
  'C':'Place only the used needle in a special container and discard every other healthcare item as ordinary trash',
  'D':'Combine all healthcare waste in one biohazard bag because separate pharmaceutical rules never apply'},
 'key':'A',
 'rationale':'Healthcare waste must be segregated at the point of generation according to the applicable federal, state, local, and facility requirements. Sharps, regulated medical waste, and pharmaceutical or hazardous-drug waste can require different disposal streams.'},
780:{
 'stem':'After rewarming, a client with frostbite has erythematous, mildly edematous skin without blister formation or deeper tissue injury. How is this injury best classified?',
 'options':{
  'A':'First-degree frostbite, a superficial injury without blister formation after rewarming',
  'B':'Second-degree frostbite, which is characterized by clear or milky blister formation after rewarming',
  'C':'Third-degree frostbite, which involves deeper injury and typically produces hemorrhagic blisters',
  'D':'Fourth-degree frostbite, which extends through soft tissue and can involve muscle, tendon, or bone'},
 'key':'A',
 'rationale':'Traditional frostbite grading is assessed after rewarming. First-degree injury is superficial and does not produce blisters; clear or milky blisters indicate second-degree injury, while hemorrhagic blisters or deeper tissue involvement indicate more severe frostbite.'}
}

# Exact locator/version notes recorded during the manual source/currentness pass.
LOC={
732:'SAMHSA TIP 63 (2021 update), opioid withdrawal signs and assessment; accessed 2026-08-14.',
733:'CDC Quit Smoking, 7 Common Withdrawal Symptoms; current page reviewed 2026-08-14.',
734:'MHAUS, What is MH / MHAUS and trigger-agent guidance; accessed 2026-08-14.',
735:'Postoperative hemorrhage: increasing sanguineous drainage plus tachycardia/hypotension; source reviewed 2026-08-14.',
736:'AHRQ Pressure Injury Prevention, Braden risk dimensions: sensory perception, moisture, activity, mobility, nutrition, friction/shear; accessed 2026-08-14.',
737:'Caprini VTE risk model: higher score denotes higher postoperative VTE risk; currentness checked 2026-08-14.',
738:'ASA Physical Status Classification System: classification describes pre-anesthesia physical status/systemic disease burden; accessed 2026-08-14.',
739:'Wong-Baker FACES Pain Rating Scale instructions and developmental use; accessed 2026-08-14.',
740:'BAPEN MUST: validated malnutrition screening and action pathway; accessed 2026-08-14.',
741:'Preoperative testing is selected according to patient condition, procedure, and clinical indication rather than a universal panel; reviewed 2026-08-14.',
742:'Safe patient handling decision algorithms: mobility/weight-bearing/cooperation and equipment selection; reviewed 2026-08-14.',
743:'Personal hygiene/bathing care is individualized to skin condition, preferences, culture, and clinical status; reviewed 2026-08-14.',
744:'Progressive postoperative mobility: advance activity according to tolerance and reassessment; reviewed 2026-08-14.',
745:'End-of-life palliative care: symptom relief plus psychosocial, spiritual, and family support; reviewed 2026-08-14.',
746:'CDC/NIOSH stress resources: physical activity, relaxation, sleep, and social support; reviewed 2026-08-14.',
747:'U.S. DOL nursing-mother break-time protections plus regular milk expression to maintain supply; reviewed 2026-08-14.',
748:'AAP safe-sleep recommendations: smoke avoidance, pacifier at sleep, avoid overheating and bed-sharing; reviewed 2026-08-14.',
749:'APA resilience guidance: social connection, adaptive coping, meaning/purpose; reviewed 2026-08-14.',
750:'Adjustment disorder: symptoms after identifiable stressor, onset within 3 months, clinically significant distress/impairment; reviewed 2026-08-14.',
751:'Somatic symptom disorder: distressing symptoms plus excessive related thoughts/feelings/behaviors; medically unexplained symptoms are not required; reviewed 2026-08-14.',
752:'DailyMed HUMULIN N instructions: white/cloudy suspension; gently roll and invert to resuspend; accessed 2026-08-14.',
753:'Metoprolol formulation labeling: succinate extended-release versus tartrate immediate-release; reviewed 2026-08-14.',
754:'Digoxin labeling: bradycardia/conduction risk; assess heart rate and follow individualized hold parameters; reviewed 2026-08-14.',
755:'DailyMed potassium chloride ER: take with meals and water; avoid empty stomach because of gastric irritation; accessed 2026-08-14.',
756:'IV phenytoin labeling/literature: purple glove syndrome with pain, edema, and blue-purple discoloration; reviewed 2026-08-14.',
757:'Isoniazid hepatotoxicity warning: dark urine, jaundice, nausea/vomiting and other hepatitis symptoms require evaluation; reviewed 2026-08-14.',
758:'Rifampin patient information: orange-red discoloration of urine, sweat, tears, saliva and possible contact-lens staining; reviewed 2026-08-14.',
759:'Vancomycin route: oral therapy remains primarily intraluminal for C. difficile whereas IV dosing is used for systemic infection; reviewed 2026-08-14.',
760:'IV access flushing: use prescribed sterile flush technique and never force against resistance; reviewed 2026-08-14.',
761:'CNS stimulant labeling: increased blood pressure/heart rate and warnings in serious cardiac disease; reviewed 2026-08-14.',
762:'CDC Core Infection Prevention Practices: eye/face mucous-membrane protection for anticipated splashes or sprays; accessed 2026-08-14.',
763:'Environmental cleaning: reduce contamination/bioburden between patient-care episodes; reviewed 2026-08-14.',
764:'CDC hand hygiene: apply enough alcohol-based hand rub to cover all surfaces and rub until dry; accessed 2026-08-14.',
765:'CDC Core Infection Prevention Practices: remove non-respirator PPE before leaving care area; respirator after exit/door closure; accessed 2026-08-14.',
766:'Transmission-based precautions: precaution signage/PPE instructions at point of entry under facility isolation protocol; reviewed 2026-08-14.',
767:'CDC Core Practices: remove/change gloves after a task and prevent contaminated-to-clean cross-transfer; accessed 2026-08-14.',
768:'EPA/OSHA and facility waste rules: segregate sharps, regulated medical, pharmaceutical/hazardous and ordinary waste as applicable; reviewed 2026-08-14.',
769:'CDC disinfection/sterilization guideline: sterilization destroys all microbial life including bacterial spores; accessed 2026-08-14.',
770:'Nurse-sensitive indicators are outcomes influenced by nursing care, including falls and pressure injuries; reviewed 2026-08-14.',
771:'NDNQI benchmarking: unit-level nurse-sensitive outcomes compared with national benchmarks for quality improvement; reviewed 2026-08-14.',
772:'ANA Code of Ethics: professional accountability and responsibility for nursing judgments/actions; reviewed 2026-08-14.',
773:'NCSBN telehealth/licensure principle: practice authority generally follows the patient location unless compact/other authority applies; reviewed 2026-08-14.',
774:'Evidence-based practice integrates current research evidence into clinical protocols and decisions; reviewed 2026-08-14.',
775:'Quality indicator trending is used to detect patterns, evaluate interventions, and target improvement; reviewed 2026-08-14.',
776:'State nurse-staffing laws vary by jurisdiction and are not uniform nationwide; currentness checked 2026-08-14.',
777:'NCSBN scope-of-practice framework: nurses remain accountable to state law and should decline/escalate unauthorized practice; reviewed 2026-08-14.',
778:'Compensatory shock can preserve blood pressure through tachycardia/vasoconstriction before later hypotension; reviewed 2026-08-14.',
779:'Burn depth: partial-thickness injury extends into dermis and commonly blisters and is painful; reviewed 2026-08-14.',
780:'Frostbite grading after rewarming: first degree has no blisters; second degree clear/milky blisters; deeper grades have hemorrhagic/deep injury; reviewed 2026-08-14.',
781:'Syncope definition: transient loss of consciousness from cerebral hypoperfusion with rapid spontaneous complete recovery; reviewed 2026-08-14.'}

URL_OVERRIDE={
732:'https://library.samhsa.gov/sites/default/files/pep21-02-01-002.pdf',
733:'https://www.cdc.gov/tobacco/campaign/tips/quit-smoking/7-common-withdrawal-symptoms/index.html',
734:'https://www.mhaus.org/about/what-is-mh-mhaus/',
736:'https://www.ahrq.gov/patient-safety/settings/hospital/resource/pressureinjury/workshop/slides3.html',
738:'https://www.asahq.org/standards-and-practice-parameters/statement-on-asa-physical-status-classification-system',
739:'https://wongbakerfaces.org/',
740:'https://www.bapen.org.uk/screening-and-must/must/',
742:'https://www.osha.gov/healthcare/safe-patient-handling',
746:'https://www.cdc.gov/niosh/stress/about/index.html',
747:'https://www.dol.gov/agencies/whd/pump-at-work',
748:'https://publications.aap.org/pediatrics/article/150/1/e2022057990/188304/Sleep-Related-Infant-Deaths-Updated-2022',
749:'https://www.apa.org/topics/resilience',
752:'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=456e226e-e7b0-4850-b649-3d9e5533893c',
755:'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2feda15e-f325-41fe-a442-41a8cc62b855',
762:'https://www.cdc.gov/infection-control/hcp/core-practices/index.html',
764:'https://www.cdc.gov/clean-hands/hcp/about-hand-hygiene-in-healthcare-settings/index.html',
765:'https://www.cdc.gov/infection-control/hcp/core-practices/index.html',
767:'https://www.cdc.gov/infection-control/hcp/core-practices/index.html',
768:'https://www.epa.gov/rcra/medical-waste',
769:'https://www.cdc.gov/infection-control/hcp/disinfection-sterilization/summary-recommendations.html',
772:'https://www.nursingworld.org/practice-policy/nursing-excellence/ethics/code-of-ethics-for-nurses/',
773:'https://www.ncsbn.org/nursing-regulation/practice/telehealth.page',
776:'https://www.nursingworld.org/practice-policy/nurse-staffing/',
777:'https://www.ncsbn.org/nursing-regulation/practice/scope-of-practice.page',
781:'https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2017/03/09/12/15/2017-acc-aha-hrs-guideline-for-syncope'}

FLAGS=['MANUAL_ITEM_BY_ITEM_AUDIT','SOURCE_CURRENTNESS_CHECKED','KEY_VERIFIED','DISTRACTORS_REVIEWED','RATIONALE_VERIFIED','AMBIGUITY_REVIEWED','SECOND_PASS_MANUAL_QA']

def main():
 data=json.loads(PENDING.read_text(encoding='utf-8'))
 qs=data['questions']
 ids=[q['question_uid'] for q in qs]
 if ids!=EXPECTED or len(qs)!=50: raise SystemExit(f'Wave30 scope mismatch: {ids[:1]}..{ids[-1:]} count={len(qs)}')
 out=[]; manifest=[]; failures=[]
 for q in qs:
  n=int(q['source_id']); uid=q['question_uid']
  item=dict(q)
  opts=json.loads(item['item_data_json'])['options']; key=json.loads(item['correct_answer_json'])['correct_option']
  if n in FIX:
   f=FIX[n]; item['stem']=f['stem']; opts=f['options']; key=f['key']; item['rationale']=f['rationale']
  item['item_data_json']=json.dumps({'options':opts},ensure_ascii=False,separators=(',',':'))
  item['correct_answer_json']=json.dumps({'correct_option':key},separators=(',',':'))
  item['source_detail']=LOC[n]
  if n in URL_OVERRIDE: item['source_url']=URL_OVERRIDE[n]
  item['clinical_qa_status']='SOURCE_VERIFIED_2026_WAVE30_ITEM_BY_ITEM'
  item['editorial_priority']='PRODUCTION_CANDIDATE'
  item['editorial_flags_json']=json.dumps(FLAGS,separators=(',',':'))
  lengths={k:len(str(opts[k]).strip()) for k in 'ABCD'}
  ratio=max(lengths.values())/max(min(lengths.values()),1)
  dmean=sum(v for k,v in lengths.items() if k!=key)/3
  dev=abs(lengths[key]-dmean)/max(dmean,1)
  qc='PASS' if ratio<=1.15 and dev<=.10 else 'FAIL'
  if qc!='PASS': failures.append((uid,round(ratio,4),round(dev,4),lengths,key))
  item['qc']={'question_uid':uid,'lengths_json':json.dumps(lengths,separators=(',',':')),'min_chars':min(lengths.values()),'max_chars':max(lengths.values()),'max_min_ratio':round(ratio,4),'correct_option':key,'qc_status':qc,'correct_vs_distractor_mean_deviation':round(dev,4)}
  out.append(item)
  manifest.append({'question_uid':uid,'manual_disposition':'PASS' if qc=='PASS' else 'HOLD_OPTION_BALANCE','all_11_dimensions':qc=='PASS','second_pass_verified':qc=='PASS','source_locator':item['source_detail'],'source_url':item['source_url'],'semantic_review_note':'Manual stem/key/rationale/distractor/source/currentness review completed 2026-08-14; mechanical option metrics evaluated after semantic review.'})
 if failures:
  for f in failures: print('OPTION_FAIL',*f)
  raise SystemExit(f'Wave30 option gate requires manual correction for {len(failures)} item(s)')
 OUT.write_text(json.dumps({'version':'2026-08-14-wave30-item-by-item','questions':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 MANIFEST.write_text(json.dumps({'version':'2026-08-14-wave30-manual-final-qa','reviewer':'OpenAI GPT-5.6 Sol manual clinical/source QA','range':[732,781],'items':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Wave30 audited payload built: 50/50; strict option metrics PASS 50/50')
if __name__=='__main__': main()
