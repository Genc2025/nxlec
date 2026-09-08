#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import author_q1451_q1475 as a

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908.json'
OUT=ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908_collision_repaired.json'


def replacements():
    r={}
    r[1454]=a.mk(1454,'suzetrigine','Behavioral Health & Nervous Systems/Special Senses',['Pharmacology','Physiology'],
        'Human dorsal-root-ganglion sensory neurons are exposed to suzetrigine. Action-potential firing falls while assays of other major voltage-gated sodium-channel subtypes show substantially less inhibition. The effect occurs in peripheral sensory neurons before any change in neurotransmitter release from the spinal cord.',
        'Which ion channel is directly blocked by the drug?',
        {'A':'NaV1.5 voltage-gated sodium channels','B':'CaV2.2 voltage-gated calcium channels','C':'TRPV1 nonselective cation channels','D':'NaV1.8 voltage-gated sodium channels','E':'NaV1.7 voltage-gated sodium channels'},'D',
        'Selective NaV1.8 blockade in peripheral sensory neurons','moderate',
        'Suzetrigine selectively blocks the NaV1.8 voltage-gated sodium channel, which is expressed in peripheral sensory neurons including dorsal-root-ganglion neurons and contributes to pain-signal action potentials.',
        {'A':'NaV1.5 is the predominant cardiac sodium-channel subtype and is not the selective target identified for suzetrigine.','B':'CaV2.2 blockade can reduce nociceptive neurotransmitter release, but it is not the direct labeled target of suzetrigine.','C':'TRPV1 participates in nociceptor transduction but is not the voltage-gated sodium channel selectively inhibited by this drug.','D':'Suzetrigine selectively blocks the NaV1.8 voltage-gated sodium channel, which is expressed in peripheral sensory neurons including dorsal-root-ganglion neurons and contributes to pain-signal action potentials.','E':'NaV1.7 is another sensory-neuron sodium channel, but the current label identifies selective blockade of NaV1.8.'},
        'Identify NaV1.8 as a peripheral sensory-neuron sodium-channel target distinct from other nociceptive ion channels.',
        [a.src(1454,'LABEL','JOURNAVX- suzetrigine tablet, film coated','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f0976da4-1d20-4517-945c-b60ed2f41c12','f0976da4-1d20-4517-945c-b60ed2f41c12','12.1 Mechanism of Action','2026-01-26','Current DailyMed label checked 2026-09-08; the cited 12.1 mechanism section carries SPL section date 2026-01-26, not asserted as a PI revision date.')],
        'E','NaV1.7 is a plausible nociceptive sodium-channel alternative, but the current label specifically identifies selective NaV1.8 blockade.')

    r[1460]=a.mk(1460,'imetelstat','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Biochemistry','Genetics'],
        'Malignant myeloid progenitor cells are exposed to imetelstat. Telomerase activity falls, telomeres shorten over serial passages, and proliferation decreases. The drug is an oligonucleotide and does not reduce expression of the catalytic telomerase protein.',
        'Which direct molecular interaction best explains these findings?',
        {'A':'Irreversible inhibition of DNA polymerase alpha','B':'RNA-interference-mediated degradation of TERT messenger RNA','C':'Disruption of TRF2 binding at telomeric DNA','D':'Activation of transcription of the telomerase RNA gene','E':'Binding to the template region of the RNA component of human telomerase'},'E',
        'Oligonucleotide binding to the telomerase RNA template inhibits telomerase','moderate-hard',
        'Imetelstat is an oligonucleotide telomerase inhibitor that binds the template region of the RNA component of human telomerase (hTR), inhibiting telomerase enzymatic activity and preventing telomere binding.',
        {'A':'DNA polymerase alpha is required for DNA replication but is not the direct target identified for imetelstat.','B':'The drug does not work by degrading TERT messenger RNA; the labeled direct interaction is with the telomerase RNA template region.','C':'TRF2 is a shelterin protein at telomeres, but imetelstat is not described as a TRF2 inhibitor.','D':'Increasing telomerase RNA transcription would oppose, rather than explain, the observed reduction in telomerase activity.','E':'Imetelstat is an oligonucleotide telomerase inhibitor that binds the template region of the RNA component of human telomerase (hTR), inhibiting telomerase enzymatic activity and preventing telomere binding.'},
        'Distinguish direct oligonucleotide blockade of the telomerase RNA template from gene silencing and shelterin disruption.',
        [a.src(1460,'LABEL','RYTELO- imetelstat sodium injection, powder, lyophilized, for solution','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b0fab7ca-e578-43c5-9df6-bdaff4182257','b0fab7ca-e578-43c5-9df6-bdaff4182257','12.1 Mechanism of Action','2026-04-22','Current DailyMed label checked 2026-09-08; cited mechanism section carries SPL section date 2026-04-22.')],
        'B','Both are oligonucleotide mechanisms, but the current label specifies direct binding to the hTR template region rather than RNAi-mediated TERT-mRNA degradation.')

    r[1473]=a.mk(1473,'fitusiran','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Biochemistry','Genetics'],
        'Hepatocytes are exposed to fitusiran. Antithrombin messenger RNA decreases, plasma antithrombin activity subsequently falls, and thrombin-generating capacity increases without replacement of factor VIII or factor IX.',
        'Which direct molecular mechanism produces the decrease in antithrombin?',
        {'A':'Competitive inhibition of circulating antithrombin protein','B':'CRISPR-mediated disruption of the SERPINC1 gene','C':'Degradation of antithrombin messenger RNA through RNA interference','D':'Increased hepatic transcription of tissue factor','E':'AAV-mediated expression of factor IX Padua'},'C',
        'RNA interference degrades antithrombin mRNA','moderate',
        'Fitusiran is a double-stranded small interfering RNA that causes degradation of antithrombin messenger RNA through RNA interference, thereby reducing plasma antithrombin levels.',
        {'A':'Direct protein inhibition would not explain the observed fall in antithrombin messenger RNA.','B':'The therapy does not edit the SERPINC1 genomic locus; its labeled action is post-transcriptional RNA interference.','C':'Fitusiran is a double-stranded small interfering RNA that causes degradation of antithrombin messenger RNA through RNA interference, thereby reducing plasma antithrombin levels.','D':'Increasing tissue-factor transcription is not the labeled mechanism and does not directly explain selective loss of antithrombin mRNA.','E':'Factor IX Padua gene delivery is a different hemophilia gene-therapy strategy and does not reduce antithrombin mRNA.'},
        'Recognize antithrombin-mRNA RNA interference as a hemostatic rebalancing strategy distinct from clotting-factor replacement or gene addition.',
        [a.src(1473,'LABEL','QFITLIA- fitusiran injection, solution','https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6dd2f8ac-6f90-4cbf-b197-97d74964135c','6dd2f8ac-6f90-4cbf-b197-97d74964135c','12.1 Mechanism of Action','2025-09-15','Current DailyMed label checked 2026-09-08; cited mechanism section carries SPL section date 2025-09-15.')],
        'B','Gene disruption could lower antithrombin expression, but the current label identifies reversible post-transcriptional RNA interference rather than genome editing.')
    return r


def main():
    b=json.loads(BASE.read_text())
    repl=replacements()
    assert set(repl)=={1454,1460,1473}
    items=[]
    for x in b['items']:
        items.append(repl.get(x['num'],x))
    assert [x['num'] for x in items]==list(range(1451,1476))
    keys=''.join(x['item']['intended_key'] for x in items)
    assert keys=='ABCDEABCDEABCDEABCDEABCDE'
    assert Counter(keys)==Counter({'A':5,'B':5,'C':5,'D':5,'E':5})
    assert 'ncjmm' not in json.dumps(items,ensure_ascii=False).casefold()
    for x in items:
        assert len(x['evidence_map'])==5
        em={e['option']:e for e in x['evidence_map']}
        assert set(em)==set('ABCDE')
        key=x['item']['intended_key']
        for L in 'ABCDE':
            assert em[L]['claim']==x['explanation']['distractor_explanations'][L]
            assert em[L]['direct_or_inference']==('direct' if L==key else 'inference')
    b['items']=items
    b['systems']=dict(Counter(x['blueprint']['primary_system'] for x in items))
    b['status']='AUTHOR_QA_PASS_PENDING_DETERMINISTIC_PREFLIGHT_AND_INDEPENDENT_AUDIT'
    b['technical_integrity']['deterministic_live_source_preflight_complete']=False
    b['technical_integrity']['independent_auditor_a_complete']=False
    b['technical_integrity']['independent_auditor_b_complete']=False
    b['technical_integrity']['trusted_importer_complete']=False
    b['repair_metadata']={
        'reason':'Prior-workstream deterministic Jaccard collisions found in first Q1451-Q1475 preflight.',
        'blocked_candidate_git_blob':'1fb2d5ea9dd1b687555c6fbbe82281bb4476b9d0',
        'replaced_items':[1454,1460,1473],
        'replacement_constructs':{
            '1454':'Selective NaV1.8 blockade in peripheral sensory neurons',
            '1460':'Oligonucleotide binding to the telomerase RNA template inhibits telomerase',
            '1473':'RNA interference degrades antithrombin mRNA'
        },
        'repair_policy':'Construct replacement rather than wording-only repair; full deterministic preflight must restart from zero on the new candidate blob.'
    }
    OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'COLLISION_REPAIR_MATERIALIZED_PENDING_FULL_PREFLIGHT','path':str(OUT.relative_to(ROOT.parent)),'replaced':[1454,1460,1473],'keys':keys,'systems':b['systems']},sort_keys=True))

if __name__=='__main__':
    main()
