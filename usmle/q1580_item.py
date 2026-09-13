def build(make):
 x=make(1580,'oteseconazole','Reproductive System & Breast',['Pharmacology','Microbiology'],
 'Candida cells are exposed to oteseconazole. Toxic 14-methylated sterols accumulate and synthesis of a membrane sterol required for fungal membrane integrity falls.',
 'Which fungal enzyme is directly inhibited?',
 {'A':'Squalene epoxidase','B':'Beta-1,3-D-glucan synthase','C':'Thymidylate synthase','D':'DNA-dependent RNA polymerase','E':'Sterol 14-alpha-demethylase (CYP51)'},
 'E','Inhibition of fungal sterol 14-alpha-demethylase (CYP51)',
 'Oteseconazole is an azole metalloenzyme inhibitor that targets fungal sterol 14-alpha-demethylase (CYP51), an early enzyme in ergosterol biosynthesis. CYP51 inhibition lowers ergosterol synthesis and causes accumulation of 14-methylated sterols.',
 {'A':'Squalene epoxidase is inhibited by allylamines rather than oteseconazole.','B':'Beta-1,3-D-glucan synthase is targeted by echinocandins.','C':'Thymidylate synthase is not the direct fungal target of oteseconazole.','D':'Fungal RNA polymerase is not inhibited by this azole.','E':'Correct. Oteseconazole directly inhibits fungal CYP51 in the ergosterol biosynthetic pathway.'},
 'Distinguish fungal CYP51 inhibition by oteseconazole from other antifungal and antimetabolite targets.',
 'VIVJOA- oteseconazole capsule','e21d5008-800e-4417-927f-14340341865f','A',
 'Squalene epoxidase inhibition also disrupts ergosterol synthesis, but oteseconazole specifically targets fungal CYP51.')
 loc='12.4 Microbiology'
 x['sources'][0]['section_locator']=loc
 for e in x['evidence_map']: e['source_locator']=loc
 return x
