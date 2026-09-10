#!/usr/bin/env python3
from __future__ import annotations
import json
import author_q1506_q1510 as a

def main():
 a.main(); b=json.loads(a.OUT.read_text()); xs={x['num']:x for x in b['items']}
 xs[1508]=a.make(1508,'donidalorsen','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Biochemistry'],
  'Hepatocytes take up a GalNAc-conjugated antisense oligonucleotide directed against prekallikrein. Prekallikrein mRNA and protein decrease, followed by reduced capacity to generate bradykinin. The genomic KLKB1 sequence is unchanged.',
  'Which direct molecular action best explains these findings?',
  {'A':'Irreversible inhibition of plasma kallikrein enzymatic activity','B':'Neutralization of bradykinin B2 receptors','C':'RNase H1-mediated degradation of prekallikrein mRNA after antisense binding','D':'CRISPR disruption of the prekallikrein gene','E':'Inhibition of C1 esterase inhibitor synthesis'},'C','RNase H1-mediated degradation of prekallikrein mRNA by a GalNAc antisense oligonucleotide',
  'Donidalorsen is an ASO-GalNAc conjugate that binds prekallikrein mRNA and causes RNase H1-mediated degradation, reducing prekallikrein protein and excessive bradykinin generation.',
  {'A':'Direct enzyme inhibition would not explain selective loss of prekallikrein mRNA.','B':'Bradykinin-receptor blockade acts downstream and would not lower prekallikrein mRNA or protein.','C':'Correct. Antisense binding recruits RNase H1-mediated degradation of prekallikrein mRNA.','D':'The genomic sequence remains unchanged, excluding gene editing.','E':'Reducing C1 inhibitor would worsen rather than suppress kallikrein-bradykinin pathway activity.'},
  'Distinguish antisense RNase H1-mediated suppression of prekallikrein from downstream kallikrein or bradykinin-receptor blockade.','DAWNZERA- donidalorsen injection, solution','3ff501e0-f75f-07da-e063-6294a90a0cb7','A','Direct plasma-kallikrein inhibition can also reduce bradykinin generation, but it cannot account for the measured loss of prekallikrein mRNA.')
 xs[1509]=a.make(1509,'gepotidacin','Multisystem Processes & Disorders',['Pharmacology','Microbiology'],
  'Bacteria are exposed to gepotidacin. DNA replication stops despite preserved folate synthesis and ribosomal peptide elongation. Enzyme assays demonstrate inhibition of two bacterial type II topoisomerases.',
  'Which direct target profile best explains this antibacterial effect?',
  {'A':'Dihydrofolate reductase and thymidylate synthase','B':'The 30S and 50S ribosomal subunits','C':'Peptidoglycan transpeptidases','D':'DNA gyrase and topoisomerase IV','E':'RNA polymerase beta subunit'},'D','Dual inhibition of bacterial DNA gyrase and topoisomerase IV',
  'Gepotidacin is a triazaacenaphthylene antibacterial that inhibits bacterial type II topoisomerases, including DNA gyrase and topoisomerase IV, thereby inhibiting DNA replication.',
  {'A':'Folate synthesis is preserved in the stem.','B':'Ribosomal inhibition would impair peptide elongation, which remains intact.','C':'Transpeptidase inhibition targets cell-wall synthesis rather than type II topoisomerases.','D':'Correct. Gepotidacin inhibits DNA gyrase and topoisomerase IV.','E':'RNA-polymerase inhibition blocks transcription rather than the measured topoisomerase-dependent DNA-replication step.'},
  'Localize gepotidacin antibacterial activity to bacterial type II topoisomerases rather than folate, ribosomal, cell-wall, or RNA-polymerase targets.','BLUJEPA- gepotidacin tablet, film coated','80b57cfe-7819-4d95-a57d-014af42f118d','C','Cell-wall inhibition is another bactericidal mechanism, but the direct enzyme assays identify DNA gyrase and topoisomerase IV.')
 # Gepotidacin's mechanistic detail is in Microbiology 12.4, not generic 12.1.
 xs[1509]['sources'][0]['section_locator']='12.4 Microbiology; Mechanism of Action'
 for e in xs[1509]['evidence_map']: e['source_locator']='12.4 Microbiology; Mechanism of Action'
 b['items']=[xs[n] for n in range(1506,1511)]; b['answer_key_sequence']='ABCDE'; b['technical_integrity']['source_hashes_complete']=False
 a.OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 assert ''.join(x['item']['intended_key'] for x in b['items'])=='ABCDE'; assert 'ncjmm' not in a.OUT.read_text().casefold()
 print(json.dumps({'status':'AUTHOR_V2_COLLISION_REPAIR','replaced':[1508,1509],'keys':'ABCDE'}))
if __name__=='__main__': main()
