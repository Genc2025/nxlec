#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/batch_specs_1501_1600/12_q1556_q1560_author_20260912.json')
DB_BLOB='079d22bf170a3de66613ac5a895586744a3ddc7b'
TODAY='2026-09-12'

def make(*args, **kwargs):
    x=a.make(*args, **kwargs)
    x['sources'][0]['date_basis']=f'Current DailyMed SetID page checked {TODAY}; no unsupported revision date inferred.'
    x['sources'][0]['retrieved_at']=TODAY
    x['author_qa']['currentness']=f'PASS — current DailyMed SetID page reverified {TODAY}.'
    return x

def main():
    items=[]

    items.append(make(
        1556,'imetelstat','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Molecular Biology'],
        'Malignant hematopoietic progenitor cells are exposed to imetelstat. Telomerase activity falls, progressive telomere shortening occurs, and proliferation decreases after repeated cell divisions.',
        'Which molecular target is directly bound by this drug?',
        {'A':'The template region of the RNA component of human telomerase','B':'The catalytic ATP-binding site of telomerase reverse transcriptase','C':'Telomeric DNA repeat sequences at chromosome ends','D':'The shelterin protein TRF2','E':'The promoter region of the TERT gene'},
        'A','Oligonucleotide binding to the template region of telomerase RNA (hTR)',
        'Imetelstat is an oligonucleotide telomerase inhibitor that binds the template region of the RNA component of human telomerase (hTR). This inhibits telomerase enzymatic activity and prevents productive telomere binding, leading to telomere shortening in susceptible malignant progenitor cells.',
        {'A':'Correct. Imetelstat directly binds the template region of the telomerase RNA component.','B':'The drug is not a small-molecule inhibitor of the catalytic ATP-binding site of hTERT.','C':'Imetelstat does not directly hybridize to chromosomal telomeric DNA repeats as its primary labeled mechanism.','D':'TRF2 is a shelterin protein and is not the direct target of imetelstat.','E':'The drug does not act by binding the TERT gene promoter or suppressing transcription directly.'},
        'Recognize telomerase RNA-template binding as the direct molecular action of imetelstat.',
        'RYTELO- imetelstat sodium injection, powder, lyophilized, for solution','b0fab7ca-e578-43c5-9df6-bdaff4182257','B',
        'A catalytic-site inhibitor of hTERT would also reduce telomerase activity, but imetelstat is specifically an oligonucleotide that binds the telomerase RNA template region.'
    ))

    items.append(make(
        1557,'marstacimab-hncq','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Hematology'],
        'Plasma from a patient with hemophilia is incubated with marstacimab-hncq. Thrombin-generation assays show increased peak thrombin without replacement of factor VIII or factor IX.',
        'Which regulatory interaction is most directly reduced?',
        {'A':'Antithrombin inhibition of thrombin','B':'Tissue factor pathway inhibitor suppression of factor Xa/FVIIa-tissue-factor activity','C':'Activated protein C cleavage of factors Va and VIIIa','D':'Plasmin-mediated fibrin degradation','E':'Protein S cofactor activity for activated protein C'},
        'B','Neutralization of TFPI Kunitz-2 activity, relieving inhibition of the extrinsic coagulation pathway',
        'Marstacimab-hncq is a monoclonal antibody directed against the Kunitz domain 2 of tissue factor pathway inhibitor (TFPI). Neutralizing TFPI reduces its inhibition of factor Xa and the FVIIa/tissue-factor complex, thereby increasing thrombin generation.',
        {'A':'Antithrombin remains an important inhibitor of coagulation proteases but is not the direct target of marstacimab-hncq.','B':'Correct. TFPI normally restrains factor Xa and FVIIa/tissue-factor activity, and marstacimab neutralizes this inhibition.','C':'Activated protein C regulates factors Va and VIIIa but is not directly blocked by this antibody.','D':'Plasmin belongs to fibrinolysis rather than the extrinsic-pathway checkpoint targeted here.','E':'Protein S is a cofactor for activated protein C and is not the direct target of marstacimab-hncq.'},
        'Link TFPI antagonism with enhanced factor Xa/FVIIa-tissue-factor activity and increased thrombin generation in hemophilia.',
        'HYMPAVZI- marstacimab-hncq injection','a2cc631e-13a6-40c2-acf9-065ccedfb90a','C',
        'Activated protein C inhibition could also increase coagulation, but the drug-specific mechanism is neutralization of TFPI at its Kunitz-2 domain.'
    ))

    items.append(make(
        1558,'vorasidenib','Nervous System & Special Senses',['Pharmacology','Biochemistry'],
        'A glioma carries an IDH1 mutation. After treatment with vorasidenib, cellular differentiation partially recovers and the concentration of an oncometabolite falls markedly.',
        'Which metabolite is most directly decreased?',
        {'A':'Succinate','B':'Fumarate','C':'2-hydroxyglutarate','D':'Methylmalonate','E':'Homocysteine'},
        'C','Reduction of 2-hydroxyglutarate produced by mutant IDH1/IDH2 enzymes',
        'Vorasidenib inhibits IDH1 and IDH2, including clinically relevant mutant variants. Mutant IDH enzymes produce the oncometabolite 2-hydroxyglutarate (2-HG); vorasidenib reduces 2-HG and can partially restore cellular differentiation.',
        {'A':'Succinate accumulates in succinate dehydrogenase deficiency rather than being the characteristic mutant-IDH oncometabolite.','B':'Fumarate accumulates with fumarate hydratase deficiency and is not the principal metabolite reduced by vorasidenib.','C':'Correct. Mutant IDH1/2 produce 2-hydroxyglutarate, which decreases with vorasidenib.','D':'Methylmalonate accumulates in methylmalonyl-CoA mutase or vitamin B12-related disorders, not mutant IDH glioma.','E':'Homocysteine is linked to methionine/folate metabolism rather than mutant IDH activity.'},
        'Associate mutant IDH1/2 activity with production of 2-hydroxyglutarate and recognize reduction of this oncometabolite after IDH inhibition.',
        'VORANIGO- vorasidenib tablet, film coated','31405fee-55b7-4857-987e-2724ee76be84','A',
        'Succinate and fumarate are also oncometabolites in other metabolic tumor syndromes, but mutant IDH specifically drives 2-hydroxyglutarate production.'
    ))

    items.append(make(
        1559,'elacestrant','Reproductive System & Breast',['Pharmacology','Cell Biology'],
        'ER-positive breast cancer cells with an ESR1 mutation are treated with elacestrant. Estrogen-dependent proliferation falls, and the abundance of estrogen receptor-alpha protein decreases even though ESR1 DNA remains intact.',
        'Which cellular process most directly accounts for the decrease in receptor abundance?',
        {'A':'Lysosomal degradation after receptor endocytosis','B':'Suppression of ESR1 transcription by DNA methylation','C':'RNA interference-mediated cleavage of ESR1 mRNA','D':'Proteasomal degradation of estrogen receptor-alpha','E':'Caspase-mediated cleavage of estrogen receptor-alpha during apoptosis'},
        'D','ERα antagonism coupled to proteasomal degradation of ERα protein',
        'Elacestrant is an estrogen receptor antagonist that binds ERα. In ER-positive breast cancer cells it inhibits estrogen-mediated proliferation at concentrations that induce proteasome-mediated degradation of ERα protein.',
        {'A':'The labeled mechanism describes proteasomal rather than lysosomal degradation of ERα.','B':'Elacestrant does not primarily lower receptor abundance through ESR1 promoter methylation.','C':'It is not an RNA-interference therapy and does not directly cleave ESR1 mRNA.','D':'Correct. Elacestrant induces proteasome-mediated degradation of ERα protein.','E':'The receptor loss is not explained as a secondary consequence of caspase-mediated apoptosis in the labeled mechanism.'},
        'Recognize proteasomal ERα degradation as part of the direct cellular action of elacestrant.',
        'ORSERDU- elacestrant tablet, film coated','aa66ae5c-2bd2-4444-8178-b55651e054ef','A',
        'Lysosomal receptor turnover is a plausible degradation pathway, but the label specifically identifies proteasome-mediated ERα degradation.'
    ))

    items.append(make(
        1560,'crovalimab-akkz','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology'],
        'Erythrocytes from a patient with paroxysmal nocturnal hemoglobinuria are exposed to complement-active serum in the presence of crovalimab-akkz. Terminal complement-mediated intravascular hemolysis is suppressed.',
        'Which complement event is most directly inhibited?',
        {'A':'C1q binding to antibody Fc','B':'Cleavage of C3 into C3a and C3b','C':'Factor B activation in the alternative pathway','D':'Decay of C3 convertase by factor H','E':'Cleavage of C5 into C5a and C5b, preventing membrane attack complex formation'},
        'E','High-affinity C5 binding that blocks C5 cleavage and membrane attack complex formation',
        'Crovalimab-akkz is a monoclonal antibody that binds complement protein C5 with high affinity. This inhibits cleavage of C5 into C5a and C5b and prevents downstream formation of the membrane attack complex, reducing terminal complement-mediated hemolysis.',
        {'A':'C1q initiates the classical pathway upstream and is not the direct target of crovalimab-akkz.','B':'C3 cleavage occurs upstream of C5 and is not the direct blocked step.','C':'Factor B participates in alternative-pathway C3 convertase formation but is not the direct target.','D':'Factor H accelerates decay of alternative-pathway C3 convertase; crovalimab does not act by increasing factor H activity.','E':'Correct. Crovalimab binds C5 and prevents its cleavage to C5a and C5b, thereby blocking membrane attack complex formation.'},
        'Link C5 inhibition with prevention of membrane attack complex formation and reduced intravascular hemolysis in PNH.',
        'PIASKY- crovalimab-akkz injection','2597efc2-a97b-487c-b500-a67fd282a73b','B',
        'C3 cleavage is another major complement checkpoint, but the drug-specific target is C5 and the blocked terminal event is C5 cleavage with subsequent MAC formation.'
    ))

    b={
        'batch_id':'Q1556-Q1560-20260912',
        'created_at':TODAY,
        'status':'AUTHOR_QA_PASS_PENDING_TECHNICAL_FREEZE_AND_INDEPENDENT_AUDIT',
        'production_import_ready':False,
        'candidate_count':5,
        'canonical_count_before':1555,
        'canonical_count_after':1555,
        'canonical_db_blob':DB_BLOB,
        'answer_key_sequence':'ABCDE',
        'answer_key_distribution':{L:1 for L in 'ABCDE'},
        'technical_integrity':{
            'source_hashes_fabricated':False,
            'source_hashes_complete':False,
            'independent_audit_complete':False,
            'trusted_importer_complete':False
        },
        'items':items
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    assert [x['num'] for x in items]==list(range(1556,1561))
    assert ''.join(x['item']['intended_key'] for x in items)=='ABCDE'
    assert len({x['drug'].casefold() for x in items})==5
    assert 'ncjmm' not in OUT.read_text().casefold()
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_INDEPENDENT_AUDIT','items':5,'keys':'ABCDE'}))

if __name__=='__main__':
    main()
