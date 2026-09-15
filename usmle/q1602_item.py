def build(make):
 x=make(1602,'fostemsavir','Multisystem Processes & Disorders',['Pharmacology','Microbiology'],
 'An adult with multidrug-resistant HIV-1 receives fostemsavir. The active moiety generated from this prodrug prevents viral attachment before membrane fusion.',
 'Which viral protein is directly bound by the active drug?',
 {'A':'gp41','B':'gp120','C':'HIV-1 integrase','D':'CCR5','E':'Reverse transcriptase'},
 'B','Temsavir binding to HIV-1 gp120, preventing attachment to CD4',
 'Fostemsavir is a prodrug of temsavir. Temsavir binds directly to the gp120 subunit of the HIV-1 envelope glycoprotein and inhibits gp120 interaction with cellular CD4 receptors, preventing viral attachment.',
 {'A':'gp41 mediates membrane fusion but is not the direct binding target of temsavir.','B':'Correct. Temsavir directly binds HIV-1 gp120 and blocks attachment to CD4.','C':'Integrase inhibitors act after reverse transcription and do not prevent initial viral attachment.','D':'CCR5 is a host coreceptor; fostemsavir binds viral gp120 rather than CCR5.','E':'Reverse transcriptase is not the direct target of fostemsavir.'},
 'Differentiate gp120 attachment inhibition from fusion inhibition, coreceptor blockade, integrase inhibition, and reverse-transcriptase inhibition.',
 'RUKOBIA- fostemsavir tromethamine tablet, film coated, extended release','a21006b7-6d6f-4f06-81b4-17978756452b','C',
 'gp41 is another envelope target involved in entry, but temsavir specifically binds gp120 and prevents attachment to CD4.')
 loc='12.4 Microbiology'; x['sources'][0]['section_locator']=loc
 for e in x['evidence_map']: e['source_locator']=loc
 return x
