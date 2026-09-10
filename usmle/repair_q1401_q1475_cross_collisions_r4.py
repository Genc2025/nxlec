#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import repair_q1401_q1475_cross_collisions_r3 as r3

P1=Path('usmle/batch_specs_1401_1500/01_q1401_q1425_author_20260908_schema_repaired.json')
P2=Path('usmle/batch_specs_1401_1500/02_q1426_q1450_author_20260908_schema_repaired.json')
P3=Path('usmle/batch_specs_1401_1500/03_q1451_q1475_author_20260908_collision_repaired.json')

def main():
 r3.main()
 docs=[json.loads(P1.read_text()),json.loads(P2.read_text()),json.loads(P3.read_text())]
 xs={x['num']:x for b in docs for x in b['items']}
 assert xs[1402]['drug']=='crinecerfont'
 assert xs[1411]['drug']=='zanidatamab-hrii'
 assert xs[1414]['drug']=='zenocutuzumab-zbco'
 assert xs[1435]['drug']=='mirdametinib'
 assert xs[1475]['drug']=='zongertinib'
 R={}
 R[1402]=r3.make(1402,'revakinagene taroretcel-lwey','Behavioral Health & Nervous Systems/Special Senses',['Pharmacology','Histology & Cell Biology'],
  'An intravitreal encapsulated-cell implant contains allogeneic retinal pigment epithelial cells engineered to express recombinant human ciliary neurotrophic factor. After implantation, rhCNTF is detected locally while the host retinal genome is unchanged.',
  'Which direct property of the implant best explains the local biologic effect?',
  {'A':'Permanent editing of host photoreceptor DNA','B':'Secretion of recombinant human ciliary neurotrophic factor by encapsulated engineered cells','C':'Neutralization of vascular endothelial growth factor','D':'Replacement of retinal pigment epithelium by unrestricted donor-cell engraftment','E':'Inhibition of complement C5'},'B','Encapsulated engineered-cell secretion of recombinant human CNTF',
  'Revakinagene taroretcel-lwey is an encapsulated allogeneic cell-based gene therapy whose engineered retinal pigment epithelial cells secrete recombinant human ciliary neurotrophic factor (rhCNTF).',
  {'A':'The implant does not require editing the recipient retinal genome.','B':'Correct. Encapsulated engineered cells locally secrete rhCNTF.','C':'Anti-VEGF neutralization is a different retinal pharmacologic strategy.','D':'The defining mechanism is secretion from encapsulated cells rather than unrestricted donor-cell tissue replacement.','E':'Complement C5 blockade does not explain rhCNTF detection from the implant.'},
  'Distinguish an encapsulated engineered-cell protein-delivery strategy from host genome editing, anti-VEGF therapy, and cell replacement.','ENCELTO- revakinagene taroretcel-lwey implant','1ae9482a-b478-4e21-9166-b5fd52d3ef9c','12.1 Mechanism of Action','D','Donor-cell replacement is superficially plausible because the product contains allogeneic retinal pigment epithelial cells, but the cells are encapsulated and the labeled pharmacologic output is rhCNTF secretion.')
 R[1411]=r3.make(1411,'linvoseltamab-gcpt','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Immunology'],
  'Multiple-myeloma cells expressing BCMA are cocultured with T cells. Linvoseltamab-gcpt causes T-cell activation, cytokine release, and myeloma-cell lysis only when both cell populations are present.',
  'Which direct binding pattern best explains these findings?',
  {'A':'Simultaneous binding to CD3 on T cells and BCMA on myeloma cells','B':'Binding to CD20 on B cells and FcRn on endothelium','C':'Neutralization of soluble BCMA without T-cell engagement','D':'Binding to PD-1 and PD-L1 simultaneously','E':'Direct inhibition of proteasomes within myeloma cells'},'A','Bispecific CD3-by-BCMA T-cell engagement',
  'Linvoseltamab-gcpt is a bispecific T-cell-engaging antibody that binds CD3 on T cells and BCMA on multiple-myeloma cells, activating T cells and causing tumor-cell lysis.',
  {'A':'Correct. Dual CD3 and BCMA binding physically redirects T-cell cytotoxicity toward BCMA-expressing cells.','B':'CD20/FcRn binding does not match the labeled targets.','C':'Soluble-ligand neutralization alone would not explain T-cell-dependent killing.','D':'Checkpoint-pair binding is a different immunotherapy mechanism.','E':'Proteasome inhibition acts intracellularly and does not require T-cell coculture.'},
  'Recognize bispecific T-cell engagement from simultaneous CD3 and tumor-antigen binding with T-cell-dependent cytotoxicity.','LYNOZYFIC- linvoseltamab-gcpt injection, solution, concentrate','e9fd0739-1b3f-4b8b-824a-1f0a902384d3','12.1 Mechanism of Action','C','BCMA targeting alone is plausible, but the dependence on T cells and CD3 engagement uniquely identifies a BCMA-by-CD3 bispecific mechanism.')
 R[1414]=r3.make(1414,'avutometinib/defactinib','Multisystem Processes & Disorders',['Pharmacology','Biochemistry'],
  'KRAS-mutant tumor cells are exposed to a two-drug regimen. One component promotes inactive RAF-MEK complexes and prevents RAF-mediated MEK1/2 phosphorylation; the other reduces focal adhesion kinase autophosphorylation.',
  'Which paired direct actions best explain the findings?',
  {'A':'BRAF V600E inhibition plus PI3K-alpha inhibition','B':'ERK1/2 inhibition plus SRC inhibition','C':'KRAS G12C inhibition plus mTOR inhibition','D':'MEK1-pathway inhibition by avutometinib plus FAK/Pyk2 inhibition by defactinib','E':'HER2 inhibition plus MET inhibition'},'D','Combined RAF-MEK pathway modulation and FAK/Pyk2 inhibition',
  'Avutometinib is a MEK1 inhibitor that induces inactive RAF/MEK complexes and prevents RAF phosphorylation of MEK1/2; defactinib inhibits FAK and Pyk2.',
  {'A':'Neither paired target matches the documented components.','B':'Downstream ERK and SRC inhibition are not the labeled direct pair.','C':'The regimen is not a KRAS-G12C/mTOR inhibitor combination.','D':'Correct. Avutometinib modulates RAF-MEK signaling while defactinib inhibits FAK/Pyk2.','E':'HER2/MET inhibition is unrelated to the specified biochemical assays.'},
  'Distinguish combined RAF-MEK pathway modulation plus FAK-family inhibition from other kinase-pair strategies.','AVMAPKI FAKZYNJA CO-PACK- avutometinib potassium and defactinib hydrochloride kit','65889527-1406-45df-8a85-e2690dcf427d','12.1 Mechanism of Action','B','ERK phosphorylation can fall downstream of MEK inhibition, but the direct observations of inactive RAF-MEK complexes and FAK autophosphorylation identify the specific two-component regimen.')
 R[1435]=r3.make(1435,'taletrectinib','Respiratory & Renal/Urinary Systems',['Pharmacology','Biochemistry'],
  'A non-small-cell lung cancer cell line contains a ROS1 fusion with a resistance-associated kinase-domain mutation. Taletrectinib suppresses ROS1-driven proliferation; a parallel assay also shows activity against TRKA, TRKB, and TRKC.',
  'Which direct target profile best explains these findings?',
  {'A':'Selective EGFR exon-20 inhibition','B':'ALK inhibition without ROS1 activity','C':'MET inhibition only','D':'KRAS G12C inhibition','E':'ROS1 kinase inhibition, including resistance mutations, with additional TRK inhibition'},'E','ROS1 kinase inhibition including resistant variants with TRK activity',
  'Taletrectinib inhibits ROS1 tyrosine kinase, including ROS1 resistance mutations, and also shows inhibitory activity against TRKA, TRKB, and TRKC.',
  {'A':'EGFR inhibition does not match the ROS1-fusion assay.','B':'The drug directly inhibits ROS1 rather than lacking ROS1 activity.','C':'MET-only inhibition would not explain ROS1-driven suppression.','D':'KRAS G12C is a different oncogenic target.','E':'Correct. The documented profile includes ROS1, resistant ROS1 variants, and TRK kinases.'},
  'Differentiate a ROS1 inhibitor active against resistance variants from EGFR, ALK-only, MET, and KRAS-targeted strategies.','IBTROZI- taletrectinib capsule','51ac8e52-3269-4102-8dc8-dba22d82128c','12.1 Mechanism of Action','B','ALK-directed agents can overlap clinically with ROS1-positive NSCLC, but the stipulated resistant ROS1 inhibition and TRK activity select taletrectinib.')
 R[1475]=r3.make(1475,'donidalorsen','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Biochemistry'],
  'Hepatocytes take up a GalNAc-conjugated antisense oligonucleotide. Prekallikrein mRNA decreases, prekallikrein protein falls, and downstream bradykinin generation is reduced without editing the PKK gene.',
  'Which direct molecular process best explains these changes?',
  {'A':'CRISPR-mediated disruption of the prekallikrein gene','B':'Monoclonal-antibody neutralization of circulating kallikrein','C':'Small-molecule inhibition of bradykinin B2 receptors','D':'siRNA-mediated RISC cleavage of factor XII mRNA','E':'RNase H1-mediated degradation of prekallikrein mRNA after antisense binding'},'E','GalNAc antisense oligonucleotide induction of RNase-H1 degradation of PKK mRNA',
  'Donidalorsen is a GalNAc-conjugated antisense oligonucleotide that binds prekallikrein (PKK) mRNA and causes RNase H1-mediated degradation, lowering PKK protein and downstream bradykinin generation.',
  {'A':'The genomic sequence remains unchanged, excluding genome editing.','B':'Protein neutralization would not selectively reduce PKK mRNA.','C':'B2-receptor blockade acts downstream of bradykinin production.','D':'The labeled nucleic-acid mechanism targets PKK mRNA via antisense/RNase H1, not factor XII via RISC.','E':'Correct. Antisense binding recruits RNase H1 to degrade PKK mRNA.'},
  'Distinguish RNase-H1 antisense oligonucleotide pharmacology from gene editing, protein neutralization, receptor blockade, and siRNA-RISC mechanisms.','DAWNZERA- donidalorsen injection, solution','3ff501e0-f75f-07da-e063-6294a90a0cb7','12.1 Mechanism of Action','D','Both siRNA and antisense therapies reduce specific mRNAs, but donidalorsen uses antisense binding with RNase H1 against PKK mRNA rather than RISC against factor XII.')
 for q,new in R.items(): xs[q].clear(); xs[q].update(new)
 for b,p in zip(docs,(P1,P2,P3)):
  assert ''.join(x['item']['intended_key'] for x in b['items'])==b['answer_key_sequence']
  b.setdefault('collision_repair_r4',{})['reverified_2026_09_10']=True
  p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':'PASS','replaced':sorted(R),'count':len(R)}))
if __name__=='__main__': main()
