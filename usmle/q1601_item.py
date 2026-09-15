def build(make):
 x=make(1601,'maribavir','Multisystem Processes & Disorders',['Pharmacology','Microbiology'],
 'A transplant recipient with refractory cytomegalovirus infection receives maribavir. Viral protein phosphorylation falls, but CMV DNA polymerase activity is not directly inhibited.',
 'Which viral enzyme is directly inhibited?',
 {'A':'CMV pUL97 protein kinase','B':'CMV DNA polymerase UL54','C':'CMV terminase complex UL56','D':'Viral thymidine kinase','E':'HIV reverse transcriptase'},
 'A','Competitive inhibition of CMV pUL97 protein kinase',
 'Maribavir directly and competitively inhibits the protein kinase activity of human CMV pUL97, reducing phosphorylation of viral proteins. It does not directly inhibit CMV DNA polymerase.',
 {'A':'Correct. Maribavir directly inhibits CMV pUL97 protein kinase.','B':'UL54 DNA polymerase is targeted by other anti-CMV drugs but is not directly inhibited by maribavir.','C':'The terminase complex is targeted by letermovir rather than maribavir.','D':'Viral thymidine kinase is not the relevant CMV target.','E':'HIV reverse transcriptase is unrelated to CMV replication.'},
 'Recognize CMV pUL97 protein kinase as the direct antiviral target of maribavir.',
 'LIVTENCITY- maribavir tablet, coated','c94fc2c5-e840-4f18-b7d8-d5eacb26d3a0','B',
 'CMV DNA polymerase is a strong antiviral distractor, but maribavir specifically inhibits pUL97 kinase rather than UL54 polymerase.')
 loc='12.4 Microbiology'; x['sources'][0]['section_locator']=loc
 for e in x['evidence_map']: e['source_locator']=loc
 return x
