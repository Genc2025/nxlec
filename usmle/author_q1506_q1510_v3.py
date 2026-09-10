#!/usr/bin/env python3
from __future__ import annotations
import json
import author_q1506_q1510 as a
import author_q1506_q1510_v2 as v2

def main():
 v2.main(); b=json.loads(a.OUT.read_text()); xs={x['num']:x for x in b['items']}
 xs[1508]=a.make(1508,'nirogacestat','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Biochemistry'],
  'Desmoid-tumor cells are exposed to nirogacestat. Cleavage-dependent activation of Notch receptors decreases, while receptor abundance at the cell surface and downstream kinase signaling through unrelated receptor tyrosine kinases are preserved.',
  'Which direct action best explains these findings?',
  {'A':'Antagonism of the extracellular Notch ligand-binding site','B':'Inhibition of proteasomal degradation of Notch','C':'Inhibition of gamma secretase, preventing proteolytic activation of Notch receptors','D':'Inhibition of MEK1 and MEK2','E':'Neutralization of transforming growth factor beta'},'C','Gamma-secretase inhibition blocking proteolytic Notch activation',
  'Nirogacestat is a gamma-secretase inhibitor that blocks proteolytic activation of the Notch receptor. Dysregulated Notch signaling can contribute to tumor growth.',
  {'A':'Ligand-site antagonism would not directly identify the cleavage machinery measured in the experiment.','B':'Preventing proteasomal degradation would tend to preserve Notch protein rather than block its required proteolytic activation step.','C':'Correct. Gamma-secretase inhibition prevents proteolytic activation of Notch receptors.','D':'MEK inhibition targets MAP-kinase signaling and does not directly block Notch proteolysis.','E':'TGF-beta neutralization is a distinct extracellular signaling mechanism.'},
  'Recognize gamma-secretase inhibition as blockade of the proteolytic activation step required for Notch signaling.','OGSIVEO- nirogacestat tablet, film coated','f172e6ff-3190-41b0-b95a-58a7ef9e9e1e','A','Direct blockade of Notch ligand binding could also reduce Notch signaling, but the measured loss of cleavage-dependent receptor activation localizes the effect to gamma secretase.')
 b['items']=[xs[n] for n in range(1506,1511)]; b['technical_integrity']['source_hashes_complete']=False
 a.OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
 assert ''.join(x['item']['intended_key'] for x in b['items'])=='ABCDE'; assert xs[1508]['drug']=='nirogacestat'; assert xs[1509]['drug']=='gepotidacin'; assert 'ncjmm' not in a.OUT.read_text().casefold()
 print(json.dumps({'status':'AUTHOR_V3_COLLISION_REPAIR','replaced':[1508],'keys':'ABCDE'}))
if __name__=='__main__': main()
