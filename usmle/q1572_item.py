def build(make):
 x=make(1572,'lifileucel','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Immunology'],
 'A patient with metastatic melanoma has a tumor lesion resected. Immune cells from that tumor are expanded in culture, cryopreserved, and later infused back into the same patient after lymphodepletion.',
 'Which cellular product is administered?',
 {'A':'Allogeneic donor NK cells','B':'Expanded autologous tumor-derived T lymphocytes','C':'Peripheral-blood T cells engineered with a CD19 CAR','D':'Autologous hematopoietic stem cells with a tumor receptor','E':'Peptide-pulsed dendritic cells'},
 'B','Ex vivo expansion and reinfusion of autologous tumor-derived T cells',
 'Lifileucel is a tumor-derived autologous T-cell immunotherapy manufactured from resected tumor tissue by expanding tumor-derived immune cells in culture for reinfusion into the same patient.',
 {'A':'The product is autologous, not donor-derived.','B':'Correct. Lifileucel is composed primarily of expanded autologous tumor-derived T cells.','C':'It is not a CAR-engineered peripheral-blood T-cell product.','D':'It is not a hematopoietic stem-cell gene therapy.','E':'It is not a dendritic-cell vaccine.'},
 'Distinguish tumor-derived autologous T-cell expansion from other cellular immunotherapy platforms.',
 'AMTAGVI- lifileucel suspension','4121bd3f-2d6e-3bdd-e063-6294a90a3088','C',
 'CAR-T also uses autologous T cells, but lifileucel comes from resected tumor tissue and is not CAR engineered.')
 loc='11 DESCRIPTION'; x['sources'][0]['section_locator']=loc
 for e in x['evidence_map']: e['source_locator']=loc
 return x
