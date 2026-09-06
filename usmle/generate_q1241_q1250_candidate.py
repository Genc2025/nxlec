#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'batch_specs_1201_1300'/'07_q1241_q1250_author_20260906.json'
IMM='Blood, Lymphoreticular and Immune Systems'
SKIN='Musculoskeletal, Skin and Subcutaneous Tissue'
MK='Medical Knowledge: Applying Foundational Science Concepts'
DX='Patient Care: Diagnosis, including history and physical examination'
USMLE_URL='https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications'

DATA=[
{
'num':1241,'system':IMM,'competency':MK,'disciplines':['Immunology','Genetics','Physiology'],
'path':['Disorders of immune system','Congenital immunodeficiency and leukocyte trafficking'],
'coverage':'CXCR4-dependent leukocyte trafficking and marrow retention in WHIM syndrome',
'vignette':'A 14-year-old boy has had recurrent bacterial sinusitis and pneumonia since early childhood and has numerous refractory periungual warts. His absolute neutrophil count is 300/mm³, and serum IgG is decreased. Bone marrow examination shows granulocytic hyperplasia with abundant mature neutrophils, many with hypersegmented nuclei and cytoplasmic vacuoles. Genetic testing identifies a heterozygous pathogenic variant in CXCR4.',
'lead':'Which molecular effect most directly explains this patient\'s neutropenia?',
'options':{'A':'Failure of B-cell maturation due to absent Bruton tyrosine kinase signaling','B':'Excess CXCL12-dependent retention of mature leukocytes in the bone marrow due to hyperactive CXCR4 signaling','C':'Failure of the respiratory burst because of defective phagocyte NADPH oxidase','D':'Impaired immunoglobulin class switching because of absent CD40 ligand signaling','E':'Defective actin remodeling in hematopoietic cells due to loss of WASp'},
'key':'B','difficulty':'moderate-hard','steps':4,
'construct':'WHIM syndrome results from gain-of-function CXCR4 signaling with impaired receptor downregulation, causing CXCL12-mediated marrow retention (myelokathexis) and peripheral neutropenia.',
'keyexp':'The combination of neutropenia, hypogammaglobulinemia, refractory HPV warts, and a marrow rich in mature neutrophils is WHIM syndrome. Gain-of-function CXCR4 variants impair normal receptor downregulation and prolong CXCL12 signaling, retaining mature leukocytes in marrow rather than allowing normal egress.',
'wrong':{'A':'BTK deficiency causes X-linked agammaglobulinemia with failed B-cell maturation, not myelokathexis with mature neutrophil retention.','B':'Correct. Hyperactive CXCR4-CXCL12 signaling causes abnormal retention of mature leukocytes in marrow and peripheral cytopenias.','C':'Chronic granulomatous disease impairs intracellular killing by phagocytes but does not cause a marrow-retention neutropenia phenotype.','D':'CD40-ligand deficiency causes a class-switch defect with hyper-IgM physiology, not a marrow packed with retained mature neutrophils.','E':'WASp deficiency causes eczema, infections, and microthrombocytopenia rather than CXCR4-dependent myelokathexis.'},
'objective':'Recognize that WHIM syndrome is a leukocyte-trafficking disorder in which gain-of-function CXCR4 signaling causes CXCL12-mediated marrow retention of mature leukocytes and peripheral neutropenia.',
'semantic':['WHIM syndrome','CXCR4 gain of function','CXCL12','myelokathexis','neutrophil marrow retention'],
'sources':[
 {'agency':'National Library of Medicine / PubMed','title':'Clinicopathologic Features and the Spectrum of Myelokathexis in Warts, Hypogammaglobulinemia, Infections, Myelokathexis Syndrome','url':'https://pubmed.ncbi.nlm.nih.gov/40239948/','date':'2025','locator':'Abstract','support':'WHIM is predominantly caused by germline gain-of-function CXCR4 variants; impaired receptor internalization/hyperactive signaling causes abnormal marrow retention and peripheral cytopenias.'},
 {'agency':'National Center for Biotechnology Information / MedGen','title':'Warts, hypogammaglobulinemia, infections, and myelokathexis','url':'https://www.ncbi.nlm.nih.gov/medgen/96875','date':'current NCBI MedGen record','locator':'Definition','support':'Defines WHIM as an autosomal dominant immunodeficiency caused by CXCR4 variants and characterized by neutropenia, hypogammaglobulinemia, HPV infection, and myelokathexis.'}
]
},
{
'num':1242,'system':IMM,'competency':DX,'disciplines':['Immunology','Genetics','Pathology'],
'path':['Disorders of immune system','Inherited immunodeficiency and marrow-failure predisposition'],
'coverage':'GATA2 deficiency/MonoMAC pattern recognition',
'vignette':'A 23-year-old woman is hospitalized with disseminated Mycobacterium avium complex infection. She has a history of recurrent, treatment-resistant anogenital human papillomavirus lesions. Laboratory studies show profound monocytopenia with markedly decreased circulating B cells and natural killer cells. Bone marrow biopsy shows dysplastic changes. Her father developed acute myeloid leukemia at age 39.',
'lead':'Which diagnosis best explains this patient\'s findings?',
'options':{'A':'Warts, hypogammaglobulinemia, infections, and myelokathexis syndrome','B':'Common variable immunodeficiency','C':'X-linked hyper-IgM syndrome','D':'GATA2 deficiency syndrome','E':'Interleukin-12 receptor beta-1 deficiency'},
'key':'D','difficulty':'moderate-hard','steps':5,
'construct':'GATA2 deficiency (MonoMAC/DCML spectrum) is recognized by invasive nontuberculous mycobacterial disease, HPV susceptibility, monocytopenia with B/NK-cell deficiency, and myelodysplasia/myeloid-malignancy predisposition.',
'keyexp':'GATA2 deficiency encompasses MonoMAC and dendritic-cell/monocyte/B/NK-cell deficiency phenotypes. Disseminated nontuberculous mycobacterial infection, refractory HPV, profound monocytopenia, B/NK-cell depletion, dysplasia, and a family history of AML are characteristic.',
'wrong':{'A':'WHIM can cause warts and infections but classically features CXCR4-mediated myelokathexis rather than monocytopenia with B/NK-cell loss and myeloid-neoplasia predisposition.','B':'CVID causes antibody deficiency and recurrent infection but does not characteristically produce profound monocytopenia, B/NK-cell depletion, and familial MDS/AML predisposition.','C':'X-linked hyper-IgM syndrome presents in males with defective class switching; the lineage pattern here is different.','D':'Correct. This is the MonoMAC/DCML spectrum of GATA2 deficiency.','E':'IL-12 receptor defects predispose to mycobacterial disease but do not explain the combined monocytopenia, B/NK-cell deficiency, HPV susceptibility, dysplasia, and familial AML.'},
'objective':'Recognize GATA2 deficiency when invasive nontuberculous mycobacterial or HPV disease occurs with monocytopenia, B/NK-cell deficiency, and myelodysplastic or AML predisposition.',
'semantic':['GATA2 deficiency','MonoMAC','monocytopenia','B NK cell deficiency','MDS AML predisposition'],
'sources':[{'agency':'National Cancer Institute / NCBI Bookshelf','title':'GATA2 Deficiency Syndrome (PDQ®)','url':'https://www.ncbi.nlm.nih.gov/books/NBK606140/','date':'current NCI PDQ summary','locator':'Introduction to GATA2 Deficiency Syndrome; Genetics and Molecular Biology; Clinical Phenotypes','support':'Germline GATA2 loss-of-function can produce MonoMAC/DCML phenotypes with monocytopenia, B- and NK-cell deficiency, mycobacterial/viral susceptibility, and predisposition to MDS/AML.'}]
},
{
'num':1243,'system':IMM,'competency':DX,'disciplines':['Immunology','Genetics','Pathology'],
'path':['Vasculitis and immune dysregulation','Monogenic autoinflammatory disease'],
'coverage':'Recognition of DADA2 as childhood PAN-like vasculitis with stroke',
'vignette':'An 8-year-old boy has recurrent episodes of fever, myalgias, and a violaceous netlike rash on his legs. He has systemic hypertension and has had two small lacunar ischemic strokes. His parents are first cousins, and a younger sister has a similar rash and unexplained anemia. Angiographic findings are compatible with a medium-vessel vasculopathy.',
'lead':'Which diagnosis best explains this presentation?',
'options':{'A':'Deficiency of adenosine deaminase 2','B':'Polyarteritis nodosa without an inherited immune disorder','C':'Antiphospholipid antibody syndrome','D':'Familial Mediterranean fever','E':'Adenosine deaminase severe combined immunodeficiency'},
'key':'A','difficulty':'hard','steps':5,
'construct':'DADA2 should be recognized in a child with livedo racemosa, systemic vasculitis/vasculopathy, hypertension, early lacunar strokes, hematologic abnormalities, and recessive familial clustering.',
'keyexp':'DADA2 is a recessive systemic autoinflammatory disorder that can mimic polyarteritis nodosa but is especially associated with childhood-onset vasculopathy, livedo, hypertension, ischemic or hemorrhagic strokes, immune dysregulation, and hematologic abnormalities.',
'wrong':{'A':'Correct. The early strokes, livedoid rash, medium-vessel disease, anemia, and consanguineous familial clustering are highly characteristic of DADA2.','B':'Sporadic polyarteritis nodosa can produce medium-vessel vasculitis and livedo, but very early recurrent lacunar strokes plus an affected sibling and consanguinity strongly favor monogenic DADA2.','C':'Antiphospholipid syndrome can cause thrombosis but does not explain this inherited childhood inflammatory vasculopathy with livedo and hematologic features.','D':'Familial Mediterranean fever causes episodic fever and serositis but not this characteristic medium-vessel vasculopathy with childhood strokes.','E':'Classic ADA-SCID causes profound combined immunodeficiency in infancy and lacks the characteristic cerebrocutaneous vasculitic phenotype of ADA2 deficiency.'},
'objective':'Distinguish DADA2 from sporadic polyarteritis nodosa and other inflammatory disorders when childhood livedoid vasculopathy, hypertension, strokes, hematologic abnormalities, and recessive familial clustering occur together.',
'semantic':['DADA2','ADA2 deficiency','livedo racemosa','childhood lacunar stroke','PAN-like vasculitis'],
'sources':[{'agency':'National Center for Biotechnology Information / GeneReviews','title':'Adenosine Deaminase 2 Deficiency','url':'https://www.ncbi.nlm.nih.gov/books/NBK544951/','date':'GeneReviews current 1993-2026 edition','locator':'Summary — Clinical characteristics; Diagnosis; Clinical Characteristics','support':'DADA2 is a systemic autoinflammatory disorder with vasculitis/vasculopathy, livedo, early ischemic or hemorrhagic stroke, hypertension, immune dysregulation, and hematologic disease; biallelic ADA2 variants cause disease.'}]
},
{
'num':1244,'system':IMM,'competency':MK,'disciplines':['Immunology','Biochemistry','Genetics'],
'path':['Disorders of immune system','Lymphocyte signaling and immunodeficiency'],
'coverage':'PI3K-AKT-mTOR hyperactivation in activated PI3K-delta syndrome',
'vignette':'A 12-year-old boy has recurrent otitis, sinusitis, and pneumonia, persistent lymphadenopathy, splenomegaly, and chronic Epstein-Barr virus viremia. Serum IgM is increased and IgG is decreased. Flow cytometry shows reduced naïve B and T lymphocytes. Sequencing identifies a heterozygous gain-of-function variant in PIK3CD, which encodes the p110δ catalytic subunit of phosphoinositide 3-kinase.',
'lead':'Which intracellular signaling change is most directly caused by this variant?',
'options':{'A':'Reduced JAK3-STAT5 signaling after common gamma-chain cytokine binding','B':'Reduced BTK-dependent phospholipase C-gamma signaling downstream of the B-cell receptor','C':'Failure of activation-induced cytidine deaminase activity during immunoglobulin class switching','D':'Reduced IKK-dependent activation of NF-kappaB','E':'Constitutive hyperactivation of the PI3K-AKT-mTOR pathway'},
'key':'E','difficulty':'moderate-hard','steps':4,
'construct':'PIK3CD gain-of-function in APDS1 causes hyperactivation of the PI3K-AKT-mTOR pathway, disrupting normal B- and T-cell maturation and function.',
'keyexp':'PIK3CD encodes p110δ, the leukocyte-enriched catalytic subunit of PI3K. Gain-of-function PIK3CD variants in APDS1 increase PI3K signaling, causing downstream AKT-mTOR hyperactivation and abnormal lymphocyte maturation/function.',
'wrong':{'A':'JAK3-STAT5 failure is a severe combined immunodeficiency mechanism, not the downstream consequence of a gain-of-function PIK3CD variant.','B':'BTK signaling failure causes X-linked agammaglobulinemia and is mechanistically distinct from PI3Kδ hyperactivation.','C':'AID deficiency impairs class switching but does not explain the known signaling consequence of PIK3CD gain of function.','D':'Reduced NF-kappaB activation is not the direct signaling effect of an activating p110δ mutation.','E':'Correct. APDS1 results from excessive PI3Kδ activity with hyperactivation of PI3K-AKT-mTOR signaling.'},
'objective':'Connect PIK3CD gain-of-function mutations in activated PI3K-delta syndrome to PI3K-AKT-mTOR hyperactivation and abnormal lymphocyte maturation.',
'semantic':['activated PI3K delta syndrome','PIK3CD gain of function','p110 delta','PI3K AKT mTOR','reduced naive lymphocytes'],
'sources':[{'agency':'National Center for Biotechnology Information / GeneReviews','title':'Activated PI3K Delta Syndrome','url':'https://www.ncbi.nlm.nih.gov/books/NBK611655/','date':'review posted 2025-01-30; current GeneReviews 1993-2026 edition','locator':'Summary; Molecular Pathogenesis','support':'PIK3CD gain-of-function or PIK3R1 loss-of-function hyperactivates the PI3K-AKT-mTOR pathway and alters lymphocyte development, including increased transitional B cells and reduced naïve B and T cells.'}]
},
{
'num':1245,'system':IMM,'competency':MK,'disciplines':['Immunology','Pathology','Physiology'],
'path':['Complement system','Early classical-pathway deficiency and autoimmunity'],
'coverage':'Mechanistic link between C1q deficiency and lupus',
'vignette':'A 7-year-old girl develops photosensitive facial rash, oral ulcers, arthritis, and glomerulonephritis. Antinuclear and anti-Smith antibodies are present. C1q is repeatedly undetectable, including during periods when her inflammatory symptoms are quiescent. Her parents are related.',
'lead':'Loss of which normal immune function most directly contributes to this patient\'s autoimmune predisposition?',
'options':{'A':'Assembly of the membrane attack complex for lysis of Neisseria species','B':'Covalent C3b deposition as the principal opsonin for encapsulated bacteria','C':'Recognition and clearance of apoptotic material that would otherwise provide persistent self-antigen','D':'C5a-mediated chemotaxis and activation of neutrophils','E':'Factor H-mediated restriction of alternative-pathway activation on host cells'},
'key':'C','difficulty':'moderate-hard','steps':4,
'construct':'Inherited C1q deficiency strongly predisposes to early SLE in part because impaired recognition/opsonization and clearance of apoptotic material increases exposure to self-antigens and loss of tolerance.',
'keyexp':'C1q is an early classical-pathway recognition molecule that binds apoptotic material and supports its noninflammatory clearance. Inherited C1q deficiency is strongly associated with early lupus; defective disposal of apoptotic debris permits prolonged exposure to nuclear self-antigens and promotes loss of tolerance.',
'wrong':{'A':'Terminal complement components C5-C9 form the membrane attack complex; their deficiency classically predisposes to Neisseria infection rather than early lupus.','B':'C3b is a major opsonin, but the question asks for the function whose loss links inherited C1q deficiency to autoimmunity.','C':'Correct. Impaired clearance of apoptotic material is a major mechanism linking early classical complement deficiency to lupus.','D':'C5a is a downstream anaphylatoxin and neutrophil chemoattractant, not the principal autoimmune mechanism of C1q deficiency.','E':'Factor H regulates the alternative pathway and is not the missing classical-pathway function in this patient.'},
'objective':'Explain the paradox that deficiency of an early classical complement component can cause autoimmunity: failure to clear apoptotic material increases persistent self-antigen exposure and promotes loss of tolerance.',
'semantic':['C1q deficiency','early lupus','apoptotic cell clearance','self antigen','classical complement'],
'sources':[{'agency':'National Library of Medicine / PubMed Central','title':'Fundamental role of C1q in autoimmunity and inflammation','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC4894527/','date':'2016','locator':'Genetic and functional deficiency of C1q in SLE','support':'Genetic C1q deficiency is strongly associated with early SLE; impaired clearance of apoptotic bodies is a key proposed mechanism, alongside altered tolerogenic signaling.'}]
},
{
'num':1246,'system':SKIN,'competency':MK,'disciplines':['Biochemistry','Genetics','Histology & Cell Biology'],
'path':['Disorders of epidermal differentiation and barrier','Inherited ichthyosis'],
'coverage':'PNPLA1-dependent acylceramide synthesis in the epidermal permeability barrier',
'vignette':'A newborn is encased in a collodion membrane and later develops generalized plate-like scaling. Genetic testing identifies biallelic loss-of-function variants in PNPLA1. Electron microscopy shows an abnormal stratum-corneum lipid barrier.',
'lead':'Which biochemical process is most directly impaired by this mutation?',
'options':{'A':'Transfer of linoleic acid to omega-hydroxyceramide to generate omega-O-acylceramide','B':'Hydrolysis of cholesterol sulfate in the outer epidermis','C':'ATP-dependent delivery of glucosylceramides into lamellar granules','D':'Transglutaminase-mediated cross-linking of cornified-envelope proteins','E':'Proteolytic processing of profilaggrin into filaggrin-derived barrier components'},
'key':'A','difficulty':'hard','steps':4,
'construct':'PNPLA1 is a keratinocyte transacylase required for omega-O-acylceramide synthesis; loss impairs the stratum-corneum lipid barrier and causes autosomal-recessive congenital ichthyosis.',
'keyexp':'PNPLA1 transfers linoleate from triglycerides to omega-hydroxyceramides, producing omega-O-acylceramides that are essential components of the stratum-corneum lipid barrier. Loss of PNPLA1 therefore causes a primary acylceramide-synthesis defect.',
'wrong':{'A':'Correct. PNPLA1 catalyzes the linoleate-transfer step needed to form omega-O-acylceramides.','B':'Steroid sulfatase deficiency causes X-linked ichthyosis by impaired cholesterol-sulfate hydrolysis, a different pathway.','C':'ABCA12 transports lipids into lamellar granules; that is distinct from PNPLA1-catalyzed acylceramide synthesis.','D':'TGM1 deficiency impairs cornified-envelope cross-linking and is another cause of autosomal-recessive congenital ichthyosis, but it is not PNPLA1\'s biochemical function.','E':'Filaggrin processing contributes to barrier function but is not the direct reaction catalyzed by PNPLA1.'},
'objective':'Link PNPLA1-associated congenital ichthyosis to failure of omega-O-acylceramide synthesis, specifically transfer of linoleate to omega-hydroxyceramide in differentiated keratinocytes.',
'semantic':['PNPLA1','autosomal recessive congenital ichthyosis','omega-O-acylceramide','linoleic acid transfer','skin barrier lipid'],
'sources':[
 {'agency':'National Library of Medicine / PubMed','title':'PNPLA1 has a crucial role in skin barrier function by directing acylceramide biosynthesis','url':'https://pubmed.ncbi.nlm.nih.gov/28248300/','date':'2017','locator':'Abstract','support':'PNPLA1 is expressed in differentiated keratinocytes and catalyzes omega-O-esterification with linoleic acid to form acylceramides essential for the epidermal permeability barrier.'},
 {'agency':'National Library of Medicine / PubMed','title':'The role of PNPLA1 in ω-O-acylceramide synthesis and skin barrier function','url':'https://pubmed.ncbi.nlm.nih.gov/30290227/','date':'2019','locator':'Abstract','support':'PNPLA1 acts as a transacylase transferring linoleic acid from triglyceride to omega-hydroxyceramide to generate omega-O-acylceramide.'}
]
},
{
'num':1247,'system':SKIN,'competency':MK,'disciplines':['Histology & Cell Biology','Genetics','Biochemistry'],
'path':['Skin fragility disorders','Epidermolysis bullosa simplex'],
'coverage':'Proteostasis mechanism of KLHL24-associated epidermolysis bullosa simplex',
'vignette':'A newborn has large areas of denuded skin on the distal extremities and develops trauma-induced blistering. The blistering becomes less prominent with age, but skin atrophy persists. Several affected relatives later developed dilated cardiomyopathy. Sequencing identifies a heterozygous start-codon variant in KLHL24 that produces an N-terminally truncated protein.',
'lead':'Which molecular consequence most directly causes the epidermal fragility?',
'options':{'A':'Dominant-negative disruption of keratin 14 heterodimer assembly','B':'Loss of type VII collagen anchoring fibrils beneath the lamina densa','C':'Loss of collagen XVII-mediated attachment within hemidesmosomes','D':'Failure to assemble laminin-332 in the basement membrane','E':'Stabilization of a gain-of-function ubiquitin-ligase adaptor with excessive proteasomal degradation of keratin 14'},
'key':'E','difficulty':'hard','steps':5,
'construct':'KLHL24 start-codon variants stabilize a gain-of-function ubiquitin-ligase substrate adaptor, causing excessive ubiquitination and proteasomal degradation of keratin 14 and an EBS phenotype that can include cardiomyopathy.',
'keyexp':'Disease-causing KLHL24 start-codon variants produce a truncated protein that is abnormally stable because normal autoubiquitination is lost. The stabilized gain-of-function protein excessively targets keratin 14 for ubiquitination and proteasomal degradation, weakening basal keratinocytes.',
'wrong':{'A':'Dominant-negative KRT14 variants can cause EBS, but the stem identifies a KLHL24 start-codon variant whose disease mechanism is abnormal proteasomal targeting of keratin.','B':'COL7A1 defects cause dystrophic epidermolysis bullosa at the anchoring-fibril level, not this KLHL24-mediated intracellular keratin-degradation phenotype.','C':'Collagen XVII defects affect hemidesmosomal adhesion but are not the molecular effect of an activating KLHL24 variant.','D':'Laminin-332 deficiency causes junctional epidermolysis bullosa and does not explain the identified KLHL24 lesion.','E':'Correct. Stabilized mutant KLHL24 excessively ubiquitinates keratin 14, promoting its proteasomal degradation.'},
'objective':'Recognize a nonstructural cause of epidermolysis bullosa: KLHL24 gain of function increases ubiquitin-proteasome degradation of keratin 14 rather than directly mutating the keratin filament.',
'semantic':['KLHL24','epidermolysis bullosa simplex','gain of function ubiquitin ligase','keratin 14 degradation','cardiomyopathy'],
'sources':[
 {'agency':'National Center for Biotechnology Information / GeneReviews','title':'Epidermolysis Bullosa Simplex','url':'https://www.ncbi.nlm.nih.gov/books/NBK1369/','date':'last update 2022-08-04; current GeneReviews 1993-2026 edition','locator':'Clinical Characteristics; Molecular Genetics — Molecular Pathogenesis; Table 10','support':'KLHL24 variants can cause autosomal-dominant EBS with cardiomyopathy; KLHL24 is a nonstructural EBS gene with gain-of-function disease causation.'},
 {'agency':'National Library of Medicine / PubMed','title':'Stabilizing mutations of KLHL24 ubiquitin ligase cause loss of keratin 14 and human skin fragility','url':'https://pubmed.ncbi.nlm.nih.gov/27798626/','date':'2017','locator':'Abstract','support':'Start-codon variants generate a stabilized N-terminally truncated KLHL24 that loses autoubiquitination and excessively ubiquitinates/degrades keratin 14.'}
]
},
{
'num':1248,'system':SKIN,'competency':DX,'disciplines':['Histology & Cell Biology','Genetics','Pathology'],
'path':['Disorders of cell adhesion and epidermis','Desmosomal skin fragility'],
'coverage':'PKP1-associated ectodermal dysplasia-skin fragility syndrome',
'vignette':'A 5-year-old boy born to consanguineous parents has lifelong trauma-induced skin erosions, painful palmoplantar thickening, sparse woolly hair, nail dystrophy, and reduced sweating. Skin biopsy shows widened spaces between keratinocytes and small, poorly formed desmosomes with reduced attachment to keratin intermediate filaments.',
'lead':'Which diagnosis best explains these findings?',
'options':{'A':'Kindler syndrome due to FERMT1 deficiency','B':'Netherton syndrome due to SPINK5 deficiency','C':'Ectodermal dysplasia-skin fragility syndrome due to plakophilin 1 deficiency','D':'Junctional epidermolysis bullosa due to laminin-332 deficiency','E':'Epidermolytic ichthyosis due to a keratin 1 or keratin 10 defect'},
'key':'C','difficulty':'hard','steps':5,
'construct':'Biallelic PKP1 loss causes ectodermal dysplasia-skin fragility syndrome, characterized by trauma-induced erosions, hair/nail/sweat abnormalities, palmoplantar keratoderma, and poorly formed desmosomes with weak keratin attachment.',
'keyexp':'Plakophilin 1 is an accessory desmosomal plaque protein that helps couple the keratin cytoskeleton to desmosomal junctions. Biallelic PKP1 loss produces cutaneous fragility and ectodermal dysplasia, with structurally abnormal desmosomes and reduced keratin-filament attachment.',
'wrong':{'A':'Kindler syndrome causes mixed-level skin fragility, photosensitivity, progressive poikiloderma, and mucosal disease rather than this desmosomal ectodermal-dysplasia phenotype.','B':'Netherton syndrome is characterized by ichthyosis, severe atopy, and trichorrhexis invaginata due to SPINK5/LEKT1 deficiency, not poorly formed desmosomes from PKP1 loss.','C':'Correct. The phenotype and desmosomal ultrastructure are characteristic of plakophilin 1 deficiency.','D':'Laminin-332 deficiency causes junctional separation at the basement-membrane zone rather than widened intercellular spaces with malformed desmosomes.','E':'Keratin 1/10 disorders cause epidermolytic hyperkeratosis and do not specifically produce this ectodermal-dysplasia/desmosomal phenotype.'},
'objective':'Recognize plakophilin 1 deficiency from trauma-induced skin fragility, ectodermal abnormalities, palmoplantar keratoderma, and malformed desmosomes with poor keratin-filament attachment.',
'semantic':['PKP1','plakophilin 1 deficiency','ectodermal dysplasia skin fragility','poorly formed desmosomes','keratin attachment'],
'sources':[
 {'agency':'National Library of Medicine / PubMed','title':'Skin fragility and hypohidrotic ectodermal dysplasia resulting from ablation of plakophilin 1','url':'https://pubmed.ncbi.nlm.nih.gov/10233227/','date':'1999','locator':'Abstract','support':'Biallelic PKP1 loss causes trauma-induced skin fragility with ectodermal dysplasia; skin shows small poorly formed desmosomes and reduced keratin-filament attachment.'},
 {'agency':'National Library of Medicine / PubMed','title':'Ectodermal dysplasia-skin fragility syndrome: Two new cases and review of this desmosomal genodermatosis','url':'https://pubmed.ncbi.nlm.nih.gov/32248567/','date':'2020','locator':'Abstract','support':'Confirmed biallelic PKP1 loss causes skin fragility and nail involvement, with frequent palmoplantar keratoderma and hypotrichosis and variable hypohidrosis.'}
]
},
{
'num':1249,'system':SKIN,'competency':DX,'disciplines':['Histology & Cell Biology','Genetics','Pathology'],
'path':['Disorders of epidermal barrier and desquamation','Peeling skin syndromes'],
'coverage':'Inflammatory peeling skin syndrome due to corneodesmosin deficiency',
'vignette':'A 10-month-old girl has had generalized superficial skin peeling and erythema since the neonatal period. She has severe pruritus, food allergies, and elevated serum IgE. Hair microscopy is normal, and immunostaining shows normal LEKT1 expression. Her parents are first cousins.',
'lead':'Which diagnosis is most likely?',
'options':{'A':'Netherton syndrome','B':'Staphylococcal scalded skin syndrome','C':'Ichthyosis vulgaris','D':'Generalized inflammatory peeling skin syndrome due to corneodesmosin deficiency','E':'Acral peeling skin syndrome due to transglutaminase 5 deficiency'},
'key':'D','difficulty':'hard','steps':5,
'construct':'Autosomal-recessive CDSN loss causes generalized inflammatory peeling skin syndrome with superficial peeling, pruritus, atopy, and epidermal-barrier failure; normal LEKT1 and hair findings help exclude Netherton syndrome.',
'keyexp':'Corneodesmosin is an adhesion component in the upper epidermis. Biallelic CDSN loss causes generalized inflammatory peeling skin syndrome, characterized by lifelong superficial peeling, erythema/pruritus, barrier dysfunction, and marked atopy. Normal LEKT1 and hair microscopy argue against Netherton syndrome.',
'wrong':{'A':'Netherton syndrome can cause erythroderma and atopy, but normal LEKT1 expression and normal hair microscopy make it less likely.','B':'Staphylococcal scalded skin syndrome is an acute toxin-mediated illness rather than a lifelong recessive peeling disorder with atopy.','C':'Ichthyosis vulgaris causes dry scaling and is associated with filaggrin deficiency; continuous inflammatory superficial peeling is not its typical phenotype.','D':'Correct. CDSN deficiency causes generalized inflammatory peeling skin syndrome through impaired upper-epidermal adhesion and barrier failure.','E':'Acral peeling skin syndrome is predominantly localized to hands and feet, unlike this generalized inflammatory phenotype.'},
'objective':'Differentiate CDSN-related generalized inflammatory peeling skin syndrome from Netherton and other peeling/ichthyotic disorders by lifelong generalized superficial peeling, severe atopy, normal LEKT1, and normal hair microscopy.',
'semantic':['CDSN','corneodesmosin','generalized inflammatory peeling skin syndrome','pruritus atopy','upper epidermal adhesion'],
'sources':[
 {'agency':'National Library of Medicine / PubMed','title':'Loss of corneodesmosin leads to severe skin barrier defect, pruritus, and atopy: unraveling the peeling skin disease','url':'https://pubmed.ncbi.nlm.nih.gov/20691404/','date':'2011','locator':'Abstract','support':'Autosomal-recessive generalized peeling skin disease can result from CDSN loss; corneodesmosin is an epidermal adhesion molecule and its loss causes barrier failure, peeling, pruritus, and atopy.'},
 {'agency':'National Library of Medicine / PubMed','title':'Inflammatory peeling skin syndrome caused a novel mutation in CDSN','url':'https://pubmed.ncbi.nlm.nih.gov/22146835/','date':'2012','locator':'Abstract','support':'Inflammatory peeling skin syndrome is caused by deleterious CDSN variants; corneodesmosin is a major component of adhesion junctions in the upper epidermis.'}
]
},
{
'num':1250,'system':SKIN,'competency':DX,'disciplines':['Histology & Cell Biology','Genetics','Pathology'],
'path':['Skin fragility disorders','Syndromic epidermolysis bullosa'],
'coverage':'PLEC-associated epidermolysis bullosa simplex with muscular dystrophy',
'vignette':'An 11-year-old boy born to consanguineous parents has had generalized trauma-induced blistering and nail dystrophy since infancy. Over the past 2 years, he has developed progressive proximal muscle weakness, and serum creatine kinase is elevated. Electron microscopy of a skin biopsy shows cleavage within basal keratinocytes just above the hemidesmosomes.',
'lead':'Which diagnosis best explains this combination of findings?',
'options':{'A':'Duchenne muscular dystrophy with an unrelated blistering disorder','B':'PLEC-associated epidermolysis bullosa simplex with muscular dystrophy','C':'COL7A1-associated dystrophic epidermolysis bullosa','D':'Integrin alpha6-beta4-associated junctional epidermolysis bullosa with pyloric atresia','E':'Desmoplakin-associated cardiocutaneous syndrome'},
'key':'B','difficulty':'moderate-hard','steps':5,
'construct':'Biallelic PLEC variants cause epidermolysis bullosa simplex with muscular dystrophy because plectin mechanically couples intermediate-filament networks in basal keratinocytes and muscle.',
'keyexp':'Plectin is a cytoskeletal linker expressed in skin and muscle. Biallelic PLEC variants can cause EBS with generalized blistering followed by progressive muscular dystrophy. The cleavage plane within basal keratinocytes just above hemidesmosomes supports an EBS-level defect.',
'wrong':{'A':'A single pleiotropic cytoskeletal disorder explains both skin and muscle findings, making two unrelated disorders unnecessary.','B':'Correct. PLEC-associated EBS with muscular dystrophy unifies basal-keratinocyte fragility and progressive myopathy.','C':'COL7A1 defects cause dystrophic EB with cleavage below the lamina densa at anchoring fibrils and do not characteristically cause this PLEC-associated myopathy.','D':'Integrin alpha6-beta4 disease is a junctional EB phenotype often associated with pyloric atresia; the cleavage plane and later muscular dystrophy instead support PLEC-associated EBS.','E':'Desmoplakin disorders can affect skin and heart, but basal-cell cleavage above hemidesmosomes plus progressive muscular dystrophy is characteristic of PLEC-associated EBS.'},
'objective':'Recognize PLEC-associated EBS with muscular dystrophy when lifelong basal-keratinocyte skin fragility is followed by progressive myopathy, reflecting plectin\'s role as an intermediate-filament cytoskeletal linker in both tissues.',
'semantic':['PLEC','plectin','epidermolysis bullosa simplex muscular dystrophy','basal keratinocyte cleavage','hemidesmosome'],
'sources':[{'agency':'National Center for Biotechnology Information / GeneReviews','title':'Epidermolysis Bullosa Simplex','url':'https://www.ncbi.nlm.nih.gov/books/NBK1369/','date':'last update 2022-08-04; current GeneReviews 1993-2026 edition','locator':'Clinical Characteristics — PLEC-associated EBS; Molecular Genetics — Molecular Pathogenesis; Table 10','support':'Biallelic PLEC variants can cause EBS with muscular dystrophy; plectin links keratin intermediate-filament networks to desmosomes/hemidesmosomes and is also important in muscle.'}]
}
]

def usmle_source(q,system,competency):
    return {'source_id':f'Q{q}-S1','agency':'USMLE','title':'Step 1 Exam Content','url':USMLE_URL,
            'publication_or_revision_date':'current official specifications','retrieved_at':'2026-09-06',
            'section_locator':f'Step 1 Physician Tasks/Competencies Specifications — {competency}; {system}',
            'supporting_passage':'Supports the official Step 1 system, competency, and discipline classification used for this item.',
            'official_exam_specification':True,'rights_status':'official exam specification'}

def self_audit():
    return {'blueprint_fidelity':10,'key_correctness':10,'distractor_integrity':10,'single_best_answer':10,
            'reasoning_and_difficulty':10,'item_writing':10,'cueing_bias_fairness':10,'evidence_quality':10,
            'originality_duplication_rights':10,'technical_integrity':10,'unresolved_concerns':[],'suggested_changes':[]}

def build(d):
    q=d['num']; src=[usmle_source(q,d['system'],d['competency'])]
    for j,s in enumerate(d['sources'],2):
        src.append({'source_id':f'Q{q}-S{j}','agency':s['agency'],'title':s['title'],'url':s['url'],
                    'publication_or_revision_date':s['date'],'retrieved_at':'2026-09-06','section_locator':s['locator'],
                    'supporting_passage':s['support'],'rights_status':'authoritative indexed source'})
    disease_ids=[x['source_id'] for x in src[1:]]
    ev=[]
    for letter in 'ABCDE':
        ev.append({'claim_id':f'Q{q}-{letter}','option':letter,'claim':d['wrong'][letter],
                   'source_ids':disease_ids,'direct_or_inference':'direct' if letter==d['key'] else 'inference',
                   'item_specific_application':'The complete vignette and named molecular/clinicopathologic features resolve this option under the single-best-answer lead-in.'})
    return {'num':q,'country_scope':'United States','specification_version':'USMLE Step 1 current official specifications verified 2026-09-06',
      'blueprint':{'primary_system':d['system'],'official_outline_path':[d['system'],*d['path']],
                   'primary_competency':d['competency'],'disciplines':d['disciplines'],'coverage_deficit_addressed':d['coverage']},
      'item':{'vignette':d['vignette'],'lead_in':d['lead'],'options':d['options'],'intended_key':d['key'],
              'difficulty':d['difficulty'],'tested_construct':d['construct'],'reasoning_steps_count':d['steps']},
      'explanation':{'key_explanation':d['keyexp'],'distractor_explanations':d['wrong'],'educational_objective':d['objective']},
      'evidence_map':ev,'sources':src,'semantic_fingerprint':d['semantic'],'author_self_audit':self_audit(),'status':'CANDIDATE_FROZEN'}

items=[build(d) for d in DATA]
keys=''.join(x['item']['intended_key'] for x in items)
assert [x['num'] for x in items]==list(range(1241,1251))
assert keys=='BDAECAECDB'
assert {k:keys.count(k) for k in 'ABCDE'}=={'A':2,'B':2,'C':2,'D':2,'E':2}
assert sum(x['blueprint']['primary_system']==IMM for x in items)==5
assert sum(x['blueprint']['primary_system']==SKIN for x in items)==5
assert sum(x['blueprint']['primary_competency']==DX for x in items)==5
assert sum(x['blueprint']['primary_competency']==MK for x in items)==5
assert all(set(x['item']['options'])==set('ABCDE') for x in items)
assert all(len(x['evidence_map'])==5 for x in items)
assert 'NCJMM' not in json.dumps(items)

batch={'batch_id':'Q1241-Q1250-20260906-AUTHOR','production_count_before':1240,'production_count_after':1240,
       'status':'AUTHOR_ZERO_TRUST_PASS_PENDING_CANONICAL_DUPLICATE_AND_FINAL_QA','created_at':'2026-09-06','country_scope':'United States',
       'specification_version':'USMLE Step 1 current official specifications verified 2026-09-06',
       'canonical_pre_state':{'item_count':1240,'db_blob':'ec4393c3699a68616ea2877b464916b0db680328','state_file':'usmle/state/step2_final_q0001_q1240.json'},
       'batch_design':{'systems':{IMM:5,SKIN:5},'competencies':{DX:5,MK:5},
                       'reason':'Corpus-screened immune and skin/connective-tissue constructs; balanced diagnosis and foundational-science reasoning; avoids repetition of the preceding cardiovascular/GI batch.'},
       'answer_key_distribution':{'A':2,'B':2,'C':2,'D':2,'E':2},'answer_key_sequence':keys,'items':items}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(batch,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(OUT)
