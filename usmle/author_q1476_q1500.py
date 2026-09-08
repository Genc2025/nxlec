#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import author_q1451_q1475 as a

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'batch_specs_1401_1500'/'04_q1476_q1500_author_20260908.json'
PRIOR_FILES=[
 ROOT/'batch_specs_1301_1400'/'01_q1301_q1305_author_20260907.json',
 ROOT/'batch_specs_1301_1400'/'02_q1306_q1330_author_20260907.json',
 ROOT/'batch_specs_1301_1400'/'03_q1331_q1355_author_20260907.json',
 ROOT/'batch_specs_1301_1400'/'04_q1356_q1380_author_20260908.json',
 ROOT/'batch_specs_1301_1400'/'05_q1381_q1400_author_20260908.json',
 ROOT/'batch_specs_1401_1500'/'01_q1401_q1425_author_20260908_schema_repaired.json',
 ROOT/'batch_specs_1401_1500'/'02_q1426_q1450_author_20260908_schema_repaired.json',
 ROOT/'batch_specs_1401_1500'/'03_q1451_q1475_author_20260908_collision_repaired.json',
]

def S(q,title,setid,locator='12.1 Mechanism of Action'):
    return [a.src(q,'LABEL',title,f'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}',setid,locator,'2026-09-08','Current DailyMed label checked 2026-09-08; locator identifies the cited mechanism section and no separate PI revision date is inferred from this metadata.')]

def prior_drugs():
    out={}
    for p in PRIOR_FILES:
        b=json.loads(p.read_text())
        for x in b.get('items',[]):
            q=x.get('num'); d=str(x.get('drug','')).strip().casefold()
            if isinstance(q,int) and 1301<=q<=1475 and d:
                if d in out: raise SystemExit(f'duplicate prior drug already in workstream: {d} Q{out[d]} Q{q}')
                out[d]=q
    assert len({q for q in out.values()})==175
    return out

def items():
    z=[]
    z.append(a.mk(1476,'enlicitide','Cardiovascular System',['Pharmacology','Physiology'],
      'Hepatocytes are exposed to an orally active macrocyclic peptide. Surface LDL-receptor abundance rises and extracellular LDL clearance increases without inhibition of HMG-CoA reductase. Biochemical assays show direct binding to circulating PCSK9.',
      'Which molecular interaction best explains the increase in hepatocyte LDL-receptor abundance?',
      {'A':'Blockade of the PCSK9-LDL receptor interaction','B':'Inhibition of ATP citrate lyase','C':'Inhibition of microsomal triglyceride transfer protein','D':'Activation of hepatic LDL-receptor transcription through thyroid hormone receptors','E':'Binding of bile acids in the intestinal lumen'},'A',
      'PCSK9 binding blockade prevents LDL-receptor degradation','moderate',
      'Enlicitide binds PCSK9 and blocks its interaction with the LDL receptor, reducing PCSK9-mediated receptor degradation and increasing LDL-receptor availability for LDL clearance.',
      {'A':'Enlicitide binds PCSK9 and blocks its interaction with the LDL receptor, reducing PCSK9-mediated receptor degradation and increasing LDL-receptor availability for LDL clearance.','B':'ATP citrate lyase inhibition lowers cholesterol synthesis upstream of HMG-CoA reductase but is not enlicitide’s direct target.','C':'Microsomal triglyceride transfer protein inhibition reduces apoB-containing lipoprotein assembly rather than preventing LDL-receptor degradation.','D':'Thyroid-receptor activation is not the labeled mechanism of this PCSK9-binding peptide.','E':'Bile-acid sequestration acts in the intestine and does not directly block PCSK9-LDLR binding.'},
      'Connect PCSK9-LDLR binding blockade with preservation of hepatocyte LDL receptors.',S(1476,'LIPFENDRA- enlicitide tablet, film coated','100ec543-fbd0-44fc-b740-db9cdff39145'),'B','Reduced cholesterol synthesis can increase LDL receptors indirectly, but the direct labeled action here is blockade of PCSK9-LDLR binding.'))
    z.append(a.mk(1477,'baxdrostat','Cardiovascular System',['Pharmacology','Physiology','Biochemistry'],
      'Adrenal zona glomerulosa cells are incubated with a drug that lowers aldosterone production while largely sparing cortisol synthesis. Steroid profiling shows accumulation upstream of the terminal aldosterone-synthesis reactions.',
      'Which enzyme is directly inhibited?',
      {'A':'11β-hydroxylase (CYP11B1)','B':'Aldosterone synthase (CYP11B2)','C':'21-hydroxylase (CYP21A2)','D':'17α-hydroxylase (CYP17A1)','E':'Cholesterol side-chain cleavage enzyme (CYP11A1)'},'B',
      'Selective CYP11B2 inhibition lowers aldosterone synthesis','moderate',
      'Baxdrostat selectively inhibits aldosterone synthase (CYP11B2), the enzyme responsible for the terminal steps of aldosterone synthesis, with selectivity over CYP11B1.',
      {'A':'CYP11B1 is required for cortisol synthesis; relative sparing of cortisol argues against it as the direct target.','B':'Baxdrostat selectively inhibits aldosterone synthase (CYP11B2), the enzyme responsible for the terminal steps of aldosterone synthesis, with selectivity over CYP11B1.','C':'CYP21A2 deficiency would impair both mineralocorticoid and glucocorticoid pathways upstream.','D':'CYP17A1 inhibition changes cortisol and sex-steroid synthesis and is not the selective terminal aldosterone target.','E':'CYP11A1 catalyzes the first steroidogenic step and would broadly suppress adrenal steroid synthesis.'},
      'Differentiate CYP11B2-selective aldosterone synthase inhibition from broader adrenal steroidogenic enzyme blockade.',S(1477,'BAXFENDY- baxdrostat tablet, film coated','b1fc1ee7-facc-4099-b3db-a4c1daeaa4be'),'A','CYP11B1 is structurally related, but cortisol sparing and the current label identify selective CYP11B2 inhibition.'))
    z.append(a.mk(1478,'icotrokinra','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Immunology'],
      'Activated T cells are cultured with a peptide therapeutic. Exposure to interleukin-23 no longer sustains downstream signaling, whereas signaling initiated by unrelated cytokine receptors is preserved.',
      'Which receptor is directly bound by the drug?',
      {'A':'IL-17 receptor A','B':'IL-12 receptor β1','C':'IL-23 receptor','D':'TNF receptor 1','E':'IL-6 receptor'},'C',
      'Selective IL-23 receptor binding blocks IL-23 signaling','moderate',
      'Icotrokinra is a peptide that selectively binds the IL-23 receptor and blocks IL-23-mediated signaling.',
      {'A':'IL-17RA is downstream of a different cytokine axis and is not the direct labeled target.','B':'IL-12Rβ1 participates in IL-12/23 receptor biology, but the drug is labeled as selectively binding IL-23R.','C':'Icotrokinra is a peptide that selectively binds the IL-23 receptor and blocks IL-23-mediated signaling.','D':'TNFR1 blockade would interrupt TNF signaling, not selectively IL-23 responses.','E':'IL-6R antagonism affects a distinct cytokine pathway.'},
      'Identify IL-23 receptor blockade as distinct from neutralizing downstream IL-17 or other inflammatory cytokines.',S(1478,'ICOTYDE- icotrokinra tablet, film coated','aee3c963-edc0-4252-8769-cdf6c7cdc21a'),'B','IL-12Rβ1 is related to IL-23 receptor signaling, but the current label specifies direct selective binding to IL-23R.'))
    z.append(a.mk(1479,'tividenofusp alfa','Multisystem Processes & Disorders',['Pharmacology','Biochemistry','Histology & Cell Biology'],
      'A recombinant lysosomal enzyme fusion protein is added to a blood-brain barrier model. The fusion crosses brain endothelial cells more efficiently than unmodified enzyme and subsequently enters target-cell lysosomes through mannose-6-phosphate receptors.',
      'Which interaction enables the enhanced transcytosis across brain endothelium?',
      {'A':'Binding to LDL receptor-related protein 1','B':'Binding to neonatal Fc receptor','C':'Binding to mannose-6-phosphate receptor on the luminal endothelial surface','D':'Binding to transferrin receptor','E':'Binding to integrin αvβ3'},'D',
      'Transferrin-receptor binding enables receptor-mediated transcytosis across the blood-brain barrier','hard',
      'Tividenofusp alfa contains an Fc-based transport component that binds the transferrin receptor, enabling receptor-mediated transcytosis across the blood-brain barrier before lysosomal uptake of the enzyme.',
      {'A':'LRP1 can mediate transport of selected ligands but is not the labeled brain-shuttle target of tividenofusp alfa.','B':'FcRn regulates IgG recycling and transport, but the labeled CNS transport mechanism uses transferrin receptor binding.','C':'Mannose-6-phosphate receptors mediate cellular lysosomal targeting after distribution; they are not the labeled endothelial transcytosis shuttle.','D':'Tividenofusp alfa contains an Fc-based transport component that binds the transferrin receptor, enabling receptor-mediated transcytosis across the blood-brain barrier before lysosomal uptake of the enzyme.','E':'Integrin αvβ3 is not the labeled endothelial transport receptor for this fusion protein.'},
      'Separate transferrin-receptor-mediated BBB transcytosis from subsequent mannose-6-phosphate-dependent lysosomal uptake.',S(1479,'AVLAYAH- tividenofusp alfa-eknm injection, powder, lyophilized, for solution','014d92c1-b643-4680-8ca6-f0b3307da915'),'C','M6P receptor is essential for lysosomal delivery, but it acts after distribution; transferrin receptor binding is the BBB-transcytosis step.'))
    z.append(a.mk(1480,'vepdegestrant','Reproductive & Endocrine Systems',['Pharmacology','Biochemistry'],
      'ER-positive breast-cancer cells are treated with a heterobifunctional small molecule. Estrogen-receptor protein rapidly decreases despite unchanged ESR1 messenger-RNA abundance. Proteasome inhibition prevents the loss of receptor protein.',
      'Which recruited protein best explains this effect?',
      {'A':'HSP90','B':'MDM2','C':'β-arrestin','D':'BRD4','E':'Cereblon'},'E',
      'Cereblon recruitment drives ubiquitination and proteasomal estrogen-receptor degradation','hard',
      'Vepdegestrant is a heterobifunctional degrader that binds estrogen receptor and the E3-ligase substrate receptor cereblon, leading to CRBN-mediated polyubiquitination and proteasomal ER degradation.',
      {'A':'HSP90 chaperones several signaling proteins but is not the recruited E3-ligase component in vepdegestrant action.','B':'MDM2 is an E3 ligase best known for p53 regulation, but it is not the recruited ligase receptor in this drug.','C':'β-arrestin regulates GPCR trafficking rather than the labeled ER degradation cascade.','D':'BRD4 is a chromatin reader and is not the recruited E3-ligase substrate receptor.','E':'Vepdegestrant is a heterobifunctional degrader that binds estrogen receptor and the E3-ligase substrate receptor cereblon, leading to CRBN-mediated polyubiquitination and proteasomal ER degradation.'},
      'Recognize cereblon-recruiting targeted protein degradation as distinct from transcriptional suppression of ESR1.',S(1480,'VEPPANU- vepdegestrant tablet, film coated','484e21ba-8fe1-4c6d-b923-8ba4cf5b2f20'),'B','Another E3 ligase could theoretically degrade ER, but the current label specifically identifies cereblon recruitment.'))
    z.append(a.mk(1481,'bulevirtide','Gastrointestinal System',['Pharmacology','Microbiology'],
      'Primary human hepatocytes are exposed to a synthetic lipopeptide before inoculation with hepatitis D virus. Viral attachment and entry fall, while intracellular viral replication machinery is not directly inhibited.',
      'Which hepatocyte membrane protein is occupied by the drug?',
      {'A':'Sodium taurocholate cotransporting polypeptide (NTCP)','B':'Organic anion transporting polypeptide 1B1','C':'ASGPR1','D':'CD81','E':'Scavenger receptor class B type I'},'A',
      'NTCP binding blocks hepatitis D virus attachment and entry','moderate',
      'Bulevirtide binds the hepatocyte sodium taurocholate cotransporting polypeptide (NTCP), the HDV entry receptor, and blocks viral attachment.',
      {'A':'Bulevirtide binds the hepatocyte sodium taurocholate cotransporting polypeptide (NTCP), the HDV entry receptor, and blocks viral attachment.','B':'OATP1B1 transports many organic anions but is not the HDV entry receptor targeted by bulevirtide.','C':'ASGPR1 mediates hepatic uptake of galactose-terminated ligands but is not the labeled HDV receptor.','D':'CD81 participates in hepatitis C entry, not the labeled HDV entry mechanism here.','E':'SR-BI also participates in hepatitis C entry and lipid uptake, not NTCP-mediated HDV attachment.'},
      'Identify NTCP as the hepatocyte entry receptor blocked by bulevirtide in hepatitis D.',S(1481,'HEPCLUDEX- bulevirtide injection, powder, lyophilized, for solution','12391cc2-38c2-4cf5-86d3-2be9370127fc','12.4 Microbiology — Mechanism of Action'),'D','CD81 is a familiar viral-entry receptor, but it is associated with HCV; HDV entry is blocked at NTCP.'))
    z.append(a.mk(1482,'atacicept','Respiratory & Renal/Urinary Systems',['Pharmacology','Immunology'],
      'A soluble fusion protein containing the extracellular ligand-binding portion of TACI and a modified IgG Fc region is added to B-cell cultures. Signaling by two survival ligands falls and production of galactose-deficient IgA1 decreases.',
      'Which pair of ligands is directly sequestered?',
      {'A':'IL-6 and IL-21','B':'BAFF and APRIL','C':'CD40 ligand and BAFF','D':'APRIL and CXCL13','E':'IL-4 and IL-13'},'B',
      'TACI-Fc sequestration of BAFF and APRIL reduces B-cell survival signaling','moderate-hard',
      'Atacicept is a TACI-Fc fusion protein that binds BAFF and APRIL, reducing signaling mediated by both B-cell survival ligands.',
      {'A':'IL-6 and IL-21 can influence B-cell differentiation but are not the direct TACI ligands bound by atacicept.','B':'Atacicept is a TACI-Fc fusion protein that binds BAFF and APRIL, reducing signaling mediated by both B-cell survival ligands.','C':'BAFF is relevant, but CD40L is not one of the two direct ligands identified for atacicept.','D':'APRIL is relevant, but CXCL13 is a chemokine rather than the second TACI ligand targeted here.','E':'IL-4 and IL-13 signal through distinct cytokine receptors and are not TACI ligands.'},
      'Recognize TACI-Fc as a dual BAFF/APRIL ligand trap.',S(1482,'TRUTAKNA- atacicept injection, solution','24aa29f6-ccff-45d3-89af-4d26e525cef8'),'C','BAFF blockade alone is plausible in B-cell biology, but atacicept directly binds both BAFF and APRIL.'))
    z.append(a.mk(1483,'linerixibat','Gastrointestinal System',['Pharmacology','Physiology'],
      'A patient with cholestatic pruritus receives a drug that increases fecal bile-acid loss. Ileal enterocytes show reduced uptake of conjugated bile acids from the intestinal lumen without inhibition of hepatic bile-acid synthesis enzymes.',
      'Which transporter is directly inhibited?',
      {'A':'Bile salt export pump (BSEP)','B':'Na+/K+ ATPase','C':'Ileal bile acid transporter (IBAT/ASBT)','D':'Organic solute transporter α/β','E':'Multidrug resistance protein 3'},'C',
      'IBAT inhibition interrupts enterohepatic bile-acid reabsorption','moderate',
      'Linerixibat reversibly inhibits the ileal bile acid transporter (IBAT/ASBT) in the terminal ileum, reducing bile-acid reabsorption and increasing fecal bile-acid elimination.',
      {'A':'BSEP exports bile acids from hepatocytes into bile; inhibiting it would not explain reduced ileal uptake.','B':'Na+/K+ ATPase supports many transport processes but is not the selective labeled target.','C':'Linerixibat reversibly inhibits the ileal bile acid transporter (IBAT/ASBT) in the terminal ileum, reducing bile-acid reabsorption and increasing fecal bile-acid elimination.','D':'OSTα/β mediates basolateral export from enterocytes rather than the apical uptake step targeted here.','E':'MDR3 translocates phosphatidylcholine in hepatocytes and is not the ileal bile-acid uptake transporter.'},
      'Locate IBAT/ASBT at the apical terminal ileum and connect its inhibition with increased fecal bile-acid loss.',S(1483,'LYNAVOY- linerixibat tablet, film coated','c00317c8-709c-4707-a6d1-632bff123026'),'D','OSTα/β is also in enterohepatic transport, but it handles basolateral efflux rather than luminal uptake.'))
    z.append(a.mk(1484,'navepegritide','Musculoskeletal, Skin & Subcutaneous Tissue',['Pharmacology','Physiology','Biochemistry'],
      'Growth-plate chondrocytes from a child with activating FGFR3 signaling are exposed to a long-acting C-type natriuretic peptide prodrug. Intracellular cyclic GMP rises and MAPK signaling downstream of FGFR3 decreases.',
      'Which receptor mediates the rise in cyclic GMP?',
      {'A':'NPR-A','B':'FGFR3','C':'Growth hormone receptor','D':'NPR-B','E':'IGF-1 receptor'},'D',
      'CNP activation of NPR-B raises cGMP and antagonizes FGFR3-MAPK signaling','moderate-hard',
      'Navepegritide releases C-type natriuretic peptide, which activates natriuretic peptide receptor B (NPR-B), increasing cGMP/PKG signaling and antagonizing FGFR3-mediated MAPK signaling in growth plate cartilage.',
      {'A':'NPR-A preferentially mediates ANP/BNP signaling rather than the CNP growth-plate pathway.','B':'FGFR3 signaling is antagonized downstream; it is not the receptor activated by CNP.','C':'The growth hormone receptor signals largely through JAK2/STAT pathways, not the CNP-cGMP mechanism.','D':'Navepegritide releases C-type natriuretic peptide, which activates natriuretic peptide receptor B (NPR-B), increasing cGMP/PKG signaling and antagonizing FGFR3-mediated MAPK signaling in growth plate cartilage.','E':'IGF-1 receptor is a receptor tyrosine kinase and does not mediate the CNP-induced rise in cGMP.'},
      'Connect CNP-NPR-B signaling to cGMP generation and antagonism of FGFR3-MAPK activity in achondroplasia.',S(1484,'YUVIWEL- navepegritide kit','e01c1197-338f-414c-b804-808e129ebc8c'),'A','NPR-A is also a membrane guanylyl cyclase, but CNP preferentially signals through NPR-B in growth plate chondrocytes.'))
    z.append(a.mk(1485,'pegzilarginase','Multisystem Processes & Disorders',['Pharmacology','Biochemistry'],
      'Plasma from a patient with arginase 1 deficiency is incubated with a pegylated recombinant enzyme. Arginine concentration falls while ornithine and urea increase.',
      'Which reaction is directly catalyzed by the therapeutic enzyme?',
      {'A':'Ornithine to citrulline','B':'Citrulline to argininosuccinate','C':'Argininosuccinate to arginine and fumarate','D':'Carbamoyl phosphate plus ornithine to citrulline','E':'Arginine to ornithine and urea'},'E',
      'Exogenous arginase hydrolyzes arginine to ornithine and urea','moderate',
      'Pegzilarginase is an arginine-specific enzyme that converts arginine to ornithine and urea, replacing the deficient metabolic step.',
      {'A':'Ornithine transcarbamylase uses ornithine to form citrulline; that is a different urea-cycle step.','B':'Argininosuccinate synthetase forms argininosuccinate from citrulline and aspartate.','C':'Argininosuccinate lyase generates arginine and fumarate, upstream of arginase.','D':'Ornithine transcarbamylase catalyzes this mitochondrial reaction.','E':'Pegzilarginase is an arginine-specific enzyme that converts arginine to ornithine and urea, replacing the deficient metabolic step.'},
      'Identify the arginase reaction as arginine hydrolysis to ornithine and urea.',S(1485,'LOARGYS- pegzilarginase-nbln injection','d5ceabf2-43a0-4746-9371-d98a39cf6cfc'),'C','Argininosuccinate lyase is adjacent in the urea cycle, but the therapeutic directly supplies arginase activity.'))
    z.append(a.mk(1486,'copper histidinate','Multisystem Processes & Disorders',['Pharmacology','Biochemistry','Genetics'],
      'A child with pathogenic ATP7A variants receives daily subcutaneous copper histidinate. Copper availability to cuproenzymes improves despite persistence of the intestinal copper-transport defect.',
      'Which therapeutic principle best explains the treatment?',
      {'A':'Parenteral copper delivery bypasses impaired gastrointestinal copper absorption','B':'Chelation increases urinary copper excretion','C':'ATP7A transcription is activated by the drug','D':'Copper is replaced with zinc in cuproenzymes','E':'Intestinal metallothionein is irreversibly inhibited'},'A',
      'Parenteral copper replacement bypasses defective intestinal ATP7A-dependent copper transport','moderate',
      'Copper histidinate provides bioavailable copper by the subcutaneous route, bypassing impaired gastrointestinal copper absorption associated with ATP7A dysfunction in Menkes disease.',
      {'A':'Copper histidinate provides bioavailable copper by the subcutaneous route, bypassing impaired gastrointestinal copper absorption associated with ATP7A dysfunction in Menkes disease.','B':'Copper chelation would further reduce available copper and is used for copper overload rather than Menkes disease.','C':'The therapy supplies copper; it does not correct the ATP7A mutation by inducing transcription.','D':'Zinc cannot substitute for copper in copper-dependent enzymes.','E':'The labeled therapeutic principle is copper replacement, not irreversible metallothionein inhibition.'},
      'Understand why parenteral copper can partially bypass ATP7A-dependent intestinal copper transport failure.',S(1486,'ZYCUBO- copper histidinate injection, powder, lyophilized, for solution','e3aeefc2-f44d-4337-9c2e-3dba44a89e48'),'C','Gene-expression rescue would address the root defect, but copper histidinate is replacement therapy rather than gene correction.'))
    z.append(a.mk(1487,'crinecerfont','Reproductive & Endocrine Systems',['Pharmacology','Physiology'],
      'Pituitary corticotrophs are exposed to a selective receptor antagonist. Corticotropin-releasing factor can no longer increase ACTH secretion, and adrenal androgen production subsequently falls.',
      'Which receptor is blocked?',
      {'A':'Glucocorticoid receptor','B':'CRF type 1 receptor','C':'Melanocortin 2 receptor','D':'Mineralocorticoid receptor','E':'GnRH receptor'},'B',
      'Pituitary CRF1 antagonism lowers ACTH drive and adrenal androgen production','moderate',
      'Crinecerfont selectively antagonizes CRF type 1 receptors in the pituitary, inhibiting CRF-driven ACTH secretion and thereby reducing ACTH-mediated adrenal androgen production.',
      {'A':'Glucocorticoid receptors mediate cortisol feedback but are not the direct target of crinecerfont.','B':'Crinecerfont selectively antagonizes CRF type 1 receptors in the pituitary, inhibiting CRF-driven ACTH secretion and thereby reducing ACTH-mediated adrenal androgen production.','C':'MC2R is the adrenal ACTH receptor downstream of pituitary secretion, not the drug’s direct target.','D':'Mineralocorticoid receptors regulate sodium balance and are not the CRF signaling receptor.','E':'GnRH receptors regulate gonadotropins rather than ACTH secretion.'},
      'Place CRF1 antagonism upstream of ACTH and adrenal androgen production in classic CAH.',S(1487,'CRENESSITY- crinecerfont capsule CRENESSITY- crinecerfont solution','fd3a6fbd-9137-428a-ba46-df6606f07d28'),'C','Blocking adrenal ACTH receptors could also reduce steroidogenesis, but crinecerfont acts one level upstream at pituitary CRF1.'))
    z.append(a.mk(1488,'ziftomenib','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Biochemistry','Genetics'],
      'NPM1-mutant acute myeloid leukemia cells are treated with a small molecule. Expression of leukemogenic transcriptional programs falls and myeloid differentiation markers rise. The drug disrupts a protein-protein interaction required for recruitment of a chromatin-regulatory complex to target genes.',
      'Which interaction is directly disrupted?',
      {'A':'BCL2-BAX','B':'FLT3-STAT5','C':'Menin-KMT2A','D':'PML-RARα','E':'RUNX1-CBFβ'},'C',
      'Menin inhibition disrupts the menin-KMT2A interaction and oncogenic transcription','hard',
      'Ziftomenib inhibits menin and blocks the menin-KMT2A protein-protein interaction, disrupting leukemogenic transcriptional programs and promoting differentiation in susceptible NPM1-mutant leukemia.',
      {'A':'BCL2-BAX controls mitochondrial apoptosis but is not the labeled protein interaction targeted by ziftomenib.','B':'FLT3-STAT5 signaling can drive AML but is not the direct menin-inhibitor target.','C':'Ziftomenib inhibits menin and blocks the menin-KMT2A protein-protein interaction, disrupting leukemogenic transcriptional programs and promoting differentiation in susceptible NPM1-mutant leukemia.','D':'PML-RARα is the defining fusion in acute promyelocytic leukemia and is not the target here.','E':'RUNX1-CBFβ is a transcription-factor complex but not the menin-associated interaction blocked by this drug.'},
      'Recognize menin-KMT2A interaction blockade as a transcriptional vulnerability in NPM1-mutant AML.',S(1488,'KOMZIFTI- ziftomenib capsule','b650f696-3391-4274-8b55-a5f5e9d04769'),'B','FLT3 signaling is common in AML, but the differentiation phenotype and label specifically identify menin-KMT2A disruption.'))
    z.append(a.mk(1489,'doxecitine/doxribtimine','Multisystem Processes & Disorders',['Pharmacology','Biochemistry','Genetics'],
      'Skeletal-muscle cells with thymidine kinase 2 deficiency have depleted mitochondrial DNA. They are supplied with two oral pyrimidine nucleosides; mitochondrial DNA copy number increases without correction of the TK2 gene.',
      'Which process is most directly supported by this treatment?',
      {'A':'Transcription of mitochondrial ribosomal RNA','B':'Import of nuclear-encoded respiratory-chain proteins','C':'Mitochondrial fatty-acid β-oxidation','D':'Incorporation of deoxycytidine and deoxythymidine into mitochondrial DNA','E':'Repair of mitochondrial DNA double-strand breaks by homologous recombination'},'D',
      'Pyrimidine nucleoside supplementation supports mitochondrial DNA synthesis in TK2 deficiency','moderate-hard',
      'Doxecitine and doxribtimine provide deoxycytidine and deoxythymidine intended for incorporation into skeletal-muscle mitochondrial DNA, restoring mitochondrial DNA copy number despite TK2 deficiency.',
      {'A':'Mitochondrial RNA transcription is not the direct substrate-replacement mechanism.','B':'Protein import is required for mitochondrial function but does not explain nucleoside-driven restoration of mtDNA copy number.','C':'Fatty-acid oxidation is not the direct pathway supplemented by these pyrimidine nucleosides.','D':'Doxecitine and doxribtimine provide deoxycytidine and deoxythymidine intended for incorporation into skeletal-muscle mitochondrial DNA, restoring mitochondrial DNA copy number despite TK2 deficiency.','E':'The therapy supplies nucleotide precursors rather than activating homologous recombination repair.'},
      'Connect pyrimidine nucleoside replacement in TK2 deficiency with restoration of mitochondrial DNA synthesis.',S(1489,'KYGEVVI- doxecitine and doxribtimine powder, for oral solution','7d5ce670-9314-4fd7-8b0a-1447910dcf9e'),'B','Improved mitochondrial protein function is downstream, but the direct labeled mechanism is nucleotide incorporation into mtDNA.'))
    z.append(a.mk(1490,'sepiapterin','Multisystem Processes & Disorders',['Pharmacology','Biochemistry'],
      'Hepatocytes with residual phenylalanine hydroxylase protein are exposed to a precursor that is converted to tetrahydrobiopterin. Phenylalanine hydroxylase activity rises and phenylalanine concentration falls.',
      'Which molecule is functionally replenished by the treatment?',
      {'A':'Pyridoxal phosphate','B':'FAD','C':'Thiamine pyrophosphate','D':'S-adenosylmethionine','E':'Tetrahydrobiopterin'},'E',
      'Sepiapterin replenishes BH4, the PAH cofactor','moderate',
      'Sepiapterin is a precursor of tetrahydrobiopterin (BH4), the enzymatic cofactor that activates phenylalanine hydroxylase.',
      {'A':'Pyridoxal phosphate is a vitamin B6-derived cofactor used by many aminotransferases but is not the PAH cofactor.','B':'FAD is a flavin cofactor and is not replenished by sepiapterin.','C':'Thiamine pyrophosphate supports oxidative decarboxylation and transketolase reactions, not PAH.','D':'S-adenosylmethionine is a methyl donor rather than the cofactor activated by sepiapterin.','E':'Sepiapterin is a precursor of tetrahydrobiopterin (BH4), the enzymatic cofactor that activates phenylalanine hydroxylase.'},
      'Identify tetrahydrobiopterin as the phenylalanine-hydroxylase cofactor replenished by sepiapterin.',S(1490,'SEPHIENCE- sepiapterin powder','9fabfee2-9488-4d03-b203-8fa50f9a7f55'),'A','Several vitamin cofactors participate in amino-acid metabolism, but PAH specifically requires BH4.'))
    z.append(a.mk(1491,'acoltremon','Behavioral Health & Nervous Systems/Special Senses',['Pharmacology','Physiology'],
      'Topical ocular administration of a small molecule increases basal tear production. Experimental stimulation activates trigeminal sensory signaling from the ocular surface without directly activating muscarinic receptors.',
      'Which ion channel is agonized?',
      {'A':'TRPM8','B':'TRPV1','C':'TRPA1','D':'ASIC3','E':'Piezo2'},'A',
      'TRPM8 thermoreceptor agonism activates trigeminal signaling and basal tear production','moderate',
      'Acoltremon is an agonist of TRPM8 thermoreceptors; TRPM8 stimulation activates trigeminal nerve signaling and increases basal tear production.',
      {'A':'Acoltremon is an agonist of TRPM8 thermoreceptors; TRPM8 stimulation activates trigeminal nerve signaling and increases basal tear production.','B':'TRPV1 senses heat and irritants but is not the labeled thermoreceptor target of acoltremon.','C':'TRPA1 detects diverse irritants and is not the identified drug target.','D':'ASIC3 responds to extracellular acidity rather than the labeled cooling-thermoreceptor mechanism.','E':'Piezo2 is a mechanosensitive channel and is not the direct target described for this drug.'},
      'Associate TRPM8 sensory-neuron activation with reflex basal tear production.',S(1491,'TRYPTYR- acoltremon solution','2b7715a1-035c-4002-b582-5238efee5d58'),'B','TRPV1 is a prominent ocular sensory channel, but the label specifically identifies TRPM8 agonism.'))
    z.append(a.mk(1492,'ensitrelvir','Multisystem Processes & Disorders',['Pharmacology','Microbiology'],
      'SARS-CoV-2-infected respiratory epithelial cells are treated with an antiviral. Viral polyproteins pp1a and pp1ab are synthesized but are not efficiently processed into functional nonstructural proteins.',
      'Which viral enzyme is directly inhibited?',
      {'A':'RNA-dependent RNA polymerase','B':'Main protease (3CLpro/Mpro)','C':'Papain-like protease only','D':'Spike furin-cleavage site','E':'Viral helicase nsp13'},'B',
      'SARS-CoV-2 main-protease inhibition prevents viral polyprotein processing','moderate',
      'Ensitrelvir directly inhibits the SARS-CoV-2 main protease (Mpro/3CLpro, nsp5), preventing processing of pp1a and pp1ab and thereby blocking viral replication.',
      {'A':'Polymerase inhibition blocks RNA synthesis rather than the proteolytic processing defect described.','B':'Ensitrelvir directly inhibits the SARS-CoV-2 main protease (Mpro/3CLpro, nsp5), preventing processing of pp1a and pp1ab and thereby blocking viral replication.','C':'The label identifies Mpro/3CLpro rather than selective inhibition of the papain-like protease.','D':'The furin cleavage site is a substrate motif, not the viral protease target described for ensitrelvir.','E':'Helicase inhibition would impair RNA unwinding rather than polyprotein cleavage.'},
      'Link SARS-CoV-2 Mpro inhibition to failed processing of pp1a/pp1ab polyproteins.',S(1492,'XOCOVA- ensitrelvir tablet','526acf60-abc3-2cc2-e063-6294a90affa6','12.4 Microbiology — Mechanism of Action'),'A','Polymerase inhibition is a common antiviral mechanism, but the preserved polyprotein synthesis with failed cleavage localizes the target to Mpro.'))
    z.append(a.mk(1493,'islatravir','Multisystem Processes & Disorders',['Pharmacology','Microbiology','Biochemistry'],
      'HIV-infected lymphocytes are exposed to a deoxyadenosine analog that is phosphorylated by host kinases. The active triphosphate is incorporated into nascent viral DNA and both immediate and delayed termination of DNA synthesis are observed.',
      'Which viral enzyme is directly inhibited by the active metabolite?',
      {'A':'HIV integrase','B':'HIV protease','C':'HIV reverse transcriptase','D':'CCR5 coreceptor','E':'RNase H-independent host DNA polymerase γ'},'C',
      'Islatravir triphosphate inhibits HIV reverse transcriptase after incorporation into viral DNA','moderate',
      'Islatravir is phosphorylated to islatravir-triphosphate, which is incorporated into nascent HIV DNA and inhibits reverse transcriptase through translocation blockade and chain-termination mechanisms.',
      {'A':'Integrase acts after reverse transcription to insert viral DNA into the host genome.','B':'HIV protease cleaves viral polyproteins and is not inhibited by this nucleoside analog.','C':'Islatravir is phosphorylated to islatravir-triphosphate, which is incorporated into nascent HIV DNA and inhibits reverse transcriptase through translocation blockade and chain-termination mechanisms.','D':'CCR5 blockade prevents viral entry and would not require intracellular phosphorylation.','E':'The antiviral target is viral reverse transcriptase, not mitochondrial DNA polymerase γ.'},
      'Recognize phosphorylated nucleoside analog inhibition of HIV reverse transcriptase by incorporation into viral DNA.',S(1493,'IDVYNSO- doravirine, islatravir tablet, film coated','11aaeb53-9848-433c-be7f-db8a5bc0b26f','12.4 Microbiology — Mechanism of Action'),'A','Integrase inhibition also blocks HIV replication, but the incorporation and chain-termination phenotype localizes the drug to reverse transcriptase.'))
    z.append(a.mk(1494,'relacorilant','Reproductive & Endocrine Systems',['Pharmacology','Physiology'],
      'Tumor cells exposed to cortisol show reduced pro-inflammatory cytokine production. Addition of a reversible receptor antagonist prevents this cortisol response but has no agonist or antagonist activity at the mineralocorticoid receptor.',
      'Which receptor is directly antagonized?',
      {'A':'Progesterone receptor','B':'Androgen receptor','C':'Mineralocorticoid receptor','D':'Glucocorticoid receptor','E':'Estrogen receptor'},'D',
      'Selective glucocorticoid-receptor antagonism blocks cortisol signaling','moderate',
      'Relacorilant is a reversible glucocorticoid receptor antagonist and lacks agonist or antagonist activity at the mineralocorticoid receptor in functional assays.',
      {'A':'Progesterone-receptor antagonism is not the labeled mechanism.','B':'Androgen-receptor antagonism would not selectively block cortisol signaling.','C':'The vignette explicitly notes lack of mineralocorticoid-receptor activity, excluding this receptor.','D':'Relacorilant is a reversible glucocorticoid receptor antagonist and lacks agonist or antagonist activity at the mineralocorticoid receptor in functional assays.','E':'Estrogen-receptor antagonism is unrelated to the cortisol response described.'},
      'Distinguish selective glucocorticoid-receptor antagonism from mineralocorticoid-receptor blockade.',S(1494,'LIFYORLI- relacorilant capsule','6fcebfb5-19d6-4f63-b852-999d68a13729'),'C','Mineralocorticoid receptor blockade can alter steroid physiology, but relacorilant is specifically GR-selective in the label.'))
    z.append(a.mk(1495,'iberdomide','Blood & Lymphoreticular/Immune Systems',['Pharmacology','Biochemistry','Immunology'],
      'Multiple-myeloma cells are exposed to a small molecule that binds a substrate-recognition component of an E3 ubiquitin ligase. Two lymphoid transcription factors are then ubiquitinated and rapidly degraded by the proteasome.',
      'Which transcription factors are degraded?',
      {'A':'STAT3 and STAT5','B':'MYC and MAX','C':'NF-κB p50 and p65','D':'BCL6 and IRF4','E':'Ikaros and Aiolos'},'E',
      'Cereblon modulation promotes Ikaros and Aiolos degradation','hard',
      'Iberdomide binds cereblon and promotes recruitment, ubiquitination, and proteasomal degradation of the transcription factors Ikaros and Aiolos.',
      {'A':'STAT3/STAT5 are cytokine-signaling transcription factors but are not the labeled cereblon neo-substrates.','B':'MYC/MAX regulate proliferation but are not the direct iberdomide degradation pair.','C':'NF-κB subunits are not the specific cereblon-recruited substrates identified in the label.','D':'BCL6 and IRF4 are important lymphoid regulators but are not the named pair recruited for degradation by iberdomide.','E':'Iberdomide binds cereblon and promotes recruitment, ubiquitination, and proteasomal degradation of the transcription factors Ikaros and Aiolos.'},
      'Identify Ikaros and Aiolos as cereblon-dependent neo-substrates degraded by iberdomide.',S(1495,'ZENBEXUS- iberdomide capsule','3663d9cb-3f66-48ae-bf0a-6958bc0888de'),'D','IRF4 is important in myeloma biology, but the direct labeled cereblon-recruited substrates are Ikaros and Aiolos.'))
    z.append(a.mk(1496,'zoliflodacin','Multisystem Processes & Disorders',['Pharmacology','Microbiology'],
      'Neisseria gonorrhoeae is exposed to a spiropyrimidinetrione. Double-stranded DNA cleavage complexes accumulate because re-ligation fails. The drug contacts conserved residues in a type II topoisomerase subunit.',
      'Which bacterial protein is the principal target?',
      {'A':'DNA gyrase B','B':'DNA gyrase A quinolone-resistance determining region','C':'RNA polymerase β subunit','D':'Dihydrofolate reductase','E':'Penicillin-binding protein 2'},'A',
      'Zoliflodacin traps cleaved DNA-gyrase complexes through gyrase B interactions','hard',
      'Zoliflodacin inhibits bacterial type II topoisomerases by binding within the cleaved DNA-gyrase complex, blocking re-ligation, and interacting with conserved amino acids in gyrase B; gyrase B is the principal target in N. gonorrhoeae.',
      {'A':'Zoliflodacin inhibits bacterial type II topoisomerases by binding within the cleaved DNA-gyrase complex, blocking re-ligation, and interacting with conserved amino acids in gyrase B; gyrase B is the principal target in N. gonorrhoeae.','B':'Fluoroquinolones commonly interact with gyrase A/topoisomerase IV quinolone-resistance regions; zoliflodacin has a distinct binding mode centered on gyrase B.','C':'RNA polymerase β is targeted by rifamycins, not this topoisomerase inhibitor.','D':'Dihydrofolate reductase inhibition blocks folate metabolism and does not trap DNA cleavage complexes.','E':'PBP2 inhibition blocks peptidoglycan cross-linking rather than DNA re-ligation.'},
      'Differentiate zoliflodacin’s gyrase-B-associated type II topoisomerase mechanism from fluoroquinolone binding.',S(1496,'NUZOLVENCE- zoliflodacin for suspension','4beda35a-21b0-4b34-84ea-be6ea8cae50f','12.4 Microbiology — Mechanism of Action'),'B','Gyrase A is the familiar fluoroquinolone target, but zoliflodacin’s distinct binding mode involves conserved gyrase B residues.'))
    z.append(a.mk(1497,'gepotidacin','Multisystem Processes & Disorders',['Pharmacology','Microbiology'],
      'A bacterial isolate is exposed to a triazaacenaphthylene antibiotic. DNA replication stops after simultaneous inhibition of the two bacterial type II topoisomerases, using a binding mode distinct from fluoroquinolones.',
      'Which pair of enzymes is directly inhibited?',
      {'A':'DNA polymerase III and primase','B':'DNA gyrase and topoisomerase IV','C':'Topoisomerase I and DNA ligase','D':'RNA polymerase and DNA gyrase','E':'DNA gyrase and transpeptidase'},'B',
      'Gepotidacin inhibits bacterial DNA gyrase and topoisomerase IV','moderate',
      'Gepotidacin inhibits bacterial DNA gyrase and topoisomerase IV, blocking bacterial DNA replication through a distinct type II topoisomerase-binding mechanism.',
      {'A':'Polymerase III and primase synthesize DNA but are not the labeled gepotidacin targets.','B':'Gepotidacin inhibits bacterial DNA gyrase and topoisomerase IV, blocking bacterial DNA replication through a distinct type II topoisomerase-binding mechanism.','C':'Topoisomerase I and ligase are not the paired targets identified for this drug.','D':'RNA polymerase inhibition is characteristic of other antibacterial classes, not gepotidacin.','E':'Transpeptidase inhibition affects cell-wall synthesis rather than the dual type II topoisomerase mechanism.'},
      'Recognize dual inhibition of bacterial DNA gyrase and topoisomerase IV by gepotidacin.',S(1497,'BLUJEPA- gepotidacin tablet, film coated','80b57cfe-7819-4d95-a57d-014af42f118d','12.4 Microbiology — Mechanism of Action'),'A','Replication enzymes are plausible, but the label identifies the two bacterial type II topoisomerases.'))
    z.append(a.mk(1498,'aficamten','Cardiovascular System',['Pharmacology','Physiology'],
      'Cardiac sarcomeres from a patient with obstructive hypertrophic cardiomyopathy are exposed to a small molecule. Actin-activated ATPase activity and the number of myosin heads entering force-generating states both decrease.',
      'Which protein is directly inhibited?',
      {'A':'Cardiac troponin C','B':'L-type calcium channel','C':'Cardiac myosin','D':'Myosin light-chain kinase','E':'SERCA2a'},'C',
      'Allosteric cardiac-myosin inhibition reduces contractile motor activity','moderate',
      'Aficamten is a reversible allosteric inhibitor of cardiac myosin motor activity, reducing the number of myosin heads participating in force generation and lowering hypercontractility.',
      {'A':'Troponin C regulates calcium-dependent thin-filament activation but is not the labeled direct target.','B':'L-type calcium-channel inhibition reduces calcium entry but does not directly inhibit myosin motor ATPase.','C':'Aficamten is a reversible allosteric inhibitor of cardiac myosin motor activity, reducing the number of myosin heads participating in force generation and lowering hypercontractility.','D':'Myosin light-chain kinase regulates smooth muscle and selected myosin states but is not aficamten’s target.','E':'SERCA2a pumps calcium into the sarcoplasmic reticulum and is not directly inhibited by this drug.'},
      'Connect cardiac-myosin inhibition with reduced sarcomeric force generation in obstructive HCM.',S(1498,'MYQORZO- aficamten tablet, film coated','fd778507-1274-4d1a-a659-5431d55c543a'),'B','Calcium-channel blockade can reduce contractility, but the direct biochemical finding is myosin motor inhibition.'))
    z.append(a.mk(1499,'aceclidine','Behavioral Health & Nervous Systems/Special Senses',['Pharmacology','Physiology'],
      'A topical ophthalmic agent produces marked miosis with relatively little effect on distance refraction. Contraction of the iris sphincter creates a pinhole effect that improves near vision.',
      'Which receptor class is directly activated?',
      {'A':'α1-adrenergic receptors','B':'β2-adrenergic receptors','C':'Nicotinic acetylcholine receptors','D':'Muscarinic acetylcholine receptors','E':'Prostaglandin FP receptors'},'D',
      'Muscarinic agonism contracts the iris sphincter and produces miosis','moderate',
      'Aceclidine is a muscarinic receptor agonist that contracts the iris sphincter, producing miosis and a pinhole effect that improves depth of focus.',
      {'A':'α1 stimulation contracts the iris dilator and causes mydriasis, the opposite effect.','B':'β2 activation is not the primary pathway controlling iris-sphincter miosis.','C':'Nicotinic receptors mediate fast synaptic transmission at autonomic ganglia and neuromuscular junctions rather than direct iris-sphincter contraction.','D':'Aceclidine is a muscarinic receptor agonist that contracts the iris sphincter, producing miosis and a pinhole effect that improves depth of focus.','E':'FP-receptor agonists primarily increase uveoscleral outflow rather than directly causing the described pupil-selective muscarinic effect.'},
      'Connect ocular muscarinic agonism with iris-sphincter contraction and miosis.',S(1499,'VIZZ- aceclidine solution/ drops','7aed8024-ad30-44d6-8f3b-63338ad3ce52'),'E','Prostaglandin analogs are common ophthalmic drugs, but the immediate sphincter-mediated miosis points to muscarinic agonism.'))
    z.append(a.mk(1500,'atrasentan','Respiratory & Renal/Urinary Systems',['Pharmacology','Physiology'],
      'Glomerular cells are exposed to an endothelin-receptor antagonist that reduces endothelin-driven vasoconstrictive and profibrotic signaling while preserving signaling through the other major endothelin receptor subtype.',
      'Which receptor is selectively blocked?',
      {'A':'Angiotensin II type 1 receptor','B':'Endothelin B receptor','C':'Mineralocorticoid receptor','D':'Adenosine A1 receptor','E':'Endothelin A receptor'},'E',
      'Selective endothelin-A receptor antagonism reduces pathogenic endothelin signaling','moderate',
      'Atrasentan is a selective endothelin A (ETA) receptor antagonist, reducing ETA-mediated vasoconstrictive, inflammatory, and fibrotic signaling while relatively sparing ETB signaling.',
      {'A':'AT1 blockade targets angiotensin II rather than endothelin signaling.','B':'ETB is the other major endothelin receptor subtype and is relatively spared by selective ETA antagonism.','C':'Mineralocorticoid-receptor antagonism modifies aldosterone signaling, not the direct endothelin pathway.','D':'A1-receptor signaling participates in tubuloglomerular feedback but is not the labeled target of atrasentan.','E':'Atrasentan is a selective endothelin A (ETA) receptor antagonist, reducing ETA-mediated vasoconstrictive, inflammatory, and fibrotic signaling while relatively sparing ETB signaling.'},
      'Differentiate selective ETA antagonism from ETB, RAAS, and tubuloglomerular-feedback targets.',S(1500,'VANRAFIA- atrasentan tablet, film coated','9a7e7f85-bfd0-44a0-beda-3bcfa8215c64'),'B','ETB is part of the same ligand system, but the labeled pharmacology is selective ETA blockade.'))
    return z

def main():
    prior=prior_drugs(); xs=items()
    assert [x['num'] for x in xs]==list(range(1476,1501))
    assert len(xs)==25
    keys=''.join(x['item']['intended_key'] for x in xs)
    assert keys=='ABCDEABCDEABCDEABCDEABCDE'
    assert Counter(keys)==Counter({'A':5,'B':5,'C':5,'D':5,'E':5})
    seen=set()
    for x in xs:
        d=x['drug'].strip().casefold()
        if d in prior: raise SystemExit(f'exact drug reuse blocked: {x["drug"]} already Q{prior[d]}')
        if d in seen: raise SystemExit(f'within-batch drug reuse blocked: {x["drug"]}')
        seen.add(d)
        assert len(x['evidence_map'])==5
        em={e['option']:e for e in x['evidence_map']}; assert set(em)==set('ABCDE')
        key=x['item']['intended_key']
        for L in 'ABCDE':
            assert em[L]['claim']==x['explanation']['distractor_explanations'][L]
            assert em[L]['direct_or_inference']==('direct' if L==key else 'inference')
        assert len(x['sources'])>=1
        for s in x['sources']:
            assert s.get('setid') and s.get('section_locator') and s.get('retrieved_at')=='2026-09-08'
    raw=json.dumps(xs,ensure_ascii=False).casefold(); assert 'ncjmm' not in raw
    systems=dict(Counter(x['blueprint']['primary_system'] for x in xs))
    b={
      'batch_id':'Q1476-Q1500-20260908','created_at':'2026-09-08',
      'status':'AUTHOR_QA_PASS_PENDING_DETERMINISTIC_PREFLIGHT_AND_INDEPENDENT_AUDIT',
      'production_import_ready':False,'candidate_count':25,'preceding_candidate_range':'Q1301-Q1475',
      'new_workstream_candidate_count':200,'canonical_count_before':1300,'canonical_count_after':1300,
      'answer_key_sequence':keys,'answer_key_distribution':{'A':5,'B':5,'C':5,'D':5,'E':5},
      'systems':systems,
      'shared_sources':[
        {'source_id':'USMLE-SPEC','title':'Step 1 Exam Content','agency':'USMLE','url':'https://www.usmle.org/exam-resources/step-1-materials/step-1-content-outline-and-specifications','retrieved_at':'2026-09-08','section_locator':'Step 1 Content Specifications; Physician Tasks/Competencies Specifications; Discipline Specifications'},
        {'source_id':'USMLE-FORMAT','title':'Step 1 Formats & Questions','agency':'USMLE','url':'https://www.usmle.org/exam-resources/step-1-materials/step-1-test-question-formats','retrieved_at':'2026-09-08','section_locator':'Single-best-answer format'}],
      'items':xs,
      'technical_integrity':{
        'exact_drug_reuse_gate_q1301_q1475':'PASS','evidence_map_a_e_contract':'PASS','answer_key_balance':'PASS','ncjmm':'NOT_APPLICABLE_USMLE',
        'deterministic_live_source_preflight_complete':False,'independent_auditor_a_complete':False,'independent_auditor_b_complete':False,'trusted_importer_complete':False},
      'author_note':'Drafting, evidence mapping, key balance, exact-drug reuse screening and internal adversarial repair were completed before materialization. Full deterministic canonical/workstream/live-source collision preflight remains mandatory on the immutable candidate blob.'
    }
    OUT.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'AUTHOR_QA_PASS_PENDING_DETERMINISTIC_PREFLIGHT','range':'Q1476-Q1500','count':25,'keys':keys,'systems':systems,'prior_exact_drug_reuse':'PASS'},sort_keys=True))

if __name__=='__main__': main()
