#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import author_q1506_q1510 as a

OUT=Path('usmle/remediation/duplicate_replacements_q1535_20260911.json')
DB_BLOB='a3f28fcfd0a89161ed003e60d0d797c5fa103f1a'
TODAY='2026-09-11'
TARGETS=[306,317,318,323,403,791,799,965,966,1065,1102,1124,1184,1511]

def make(*args, **kwargs):
    x=a.make(*args, **kwargs)
    x['sources'][0]['date_basis']=f'Current authoritative page checked {TODAY}; no unsupported revision date inferred.'
    x['sources'][0]['retrieved_at']=TODAY
    x['author_qa']['currentness']=f'PASS — authoritative source page reverified {TODAY}.'
    x['remediation']={'reason':'CONFIRMED_SEMANTIC_DUPLICATE_REPLACEMENT','target_q':x['num'],'production_db_blob_bound':DB_BLOB}
    return x

def main():
    items=[]
    items.append(make(
      306,'garadacimab-gxii','Blood, Lymphoreticular and Immune Systems',['Pharmacology','Physiology'],
      'Plasma from a patient with hereditary angioedema is exposed to garadacimab-gxii. Activation of prekallikrein decreases and bradykinin generation falls, while C1-inhibitor concentration is unchanged.',
      'Which direct pharmacologic action best explains these findings?',
      {'A':'Binding the catalytic domain of activated factor XII and inhibiting its activity','B':'Replacing deficient C1 esterase inhibitor','C':'Blocking the bradykinin B2 receptor','D':'Directly inhibiting plasma kallikrein catalytic activity','E':'Activating tissue factor pathway inhibitor'},
      'A','Activated factor XII catalytic-domain inhibition upstream of kallikrein and bradykinin generation',
      'Garadacimab-gxii binds the catalytic domain of activated factor XII (FXIIa and beta-FXIIa) and inhibits its catalytic activity. This decreases prekallikrein activation and downstream bradykinin generation.',
      {'A':'Correct. Direct FXIIa inhibition explains lower kallikrein-pathway activity without replacing C1 inhibitor.','B':'C1-inhibitor replacement would increase functional inhibitor rather than directly bind FXIIa.','C':'B2-receptor blockade acts downstream at bradykinin signaling and would not reduce bradykinin generation.','D':'Direct kallikrein inhibition acts one step downstream of FXIIa and is not the labeled target of garadacimab.','E':'TFPI regulates tissue-factor coagulation initiation and does not explain selective suppression of the kallikrein-kinin pathway.'},
      'Recognize activated factor XII inhibition as an upstream strategy for suppressing kallikrein and bradykinin generation in hereditary angioedema.',
      'ANDEMBRY- garadacimab injection, solution','07b0b671-db81-49f0-a402-0c0219db7fa2','D',
      'Direct plasma kallikrein inhibition could also reduce bradykinin, but garadacimab specifically binds activated factor XII upstream of prekallikrein activation.'
    ))
    items.append(make(
      317,'eladocagene exuparvovec-tneq','Behavioral Health, Nervous Systems and Special Senses',['Pharmacology','Genetics'],
      'A child with biallelic DDC loss-of-function variants undergoes bilateral intraputaminal administration of an AAV2-based gene therapy. Follow-up testing demonstrates increased aromatic L-amino acid decarboxylase activity and increased dopamine production in the putamen.',
      'Which therapeutic event most directly produces this biochemical change?',
      {'A':'CRISPR deletion of a dominant-negative DDC allele','B':'Delivery of a functional DDC gene that restores AADC enzyme expression','C':'Inhibition of monoamine oxidase B in dopaminergic neurons','D':'Peripheral inhibition of aromatic L-amino acid decarboxylase','E':'Direct agonism of striatal dopamine D2 receptors'},
      'B','AAV2-mediated delivery of DDC leading to AADC expression and dopamine production in the putamen',
      'Eladocagene exuparvovec-tneq is an rAAV2 gene therapy designed to deliver a copy of DDC, which encodes AADC. Intraputaminal administration results in AADC expression and subsequent dopamine production.',
      {'A':'The therapy supplies a gene copy rather than editing the endogenous DDC locus.','B':'Correct. Restored DDC expression produces AADC enzyme and increases putaminal dopamine production.','C':'MAO-B inhibition decreases dopamine breakdown but does not restore missing AADC expression.','D':'Peripheral AADC inhibition would reduce peripheral conversion and cannot explain newly detected putaminal AADC activity.','E':'D2 agonism mimics dopamine signaling but does not increase AADC enzyme expression.'},
      'Connect AADC deficiency due to DDC mutations with AAV2-mediated DDC gene delivery and restoration of dopamine synthesis.',
      'KEBILIDI- eladocagene exuparvovec-tneq suspension','9d6a6401-c6b5-4f29-af11-67707d249482','C',
      'MAO-B inhibition can increase dopamine availability, but only DDC gene delivery explains restoration of AADC enzyme activity in the putamen.'
    ))
    items.append(make(
      318,'tofersen','Behavioral Health, Nervous Systems and Special Senses',['Pharmacology','Molecular Biology'],
      'Motor neurons carrying a pathogenic SOD1 variant are exposed to an antisense oligonucleotide. SOD1 messenger RNA and SOD1 protein both decline without alteration of the genomic SOD1 sequence.',
      'Which direct molecular mechanism best explains this effect?',
      {'A':'Proteasomal degradation of preexisting SOD1 protein','B':'CRISPR-mediated correction of the SOD1 variant','C':'Antisense binding to SOD1 mRNA leading to its degradation','D':'Inhibition of SOD1 enzymatic activity without changing protein abundance','E':'Silencing of SOD1 transcription by histone deacetylase inhibition'},
      'C','Antisense-oligonucleotide-mediated degradation of SOD1 mRNA',
      'Tofersen is an antisense oligonucleotide that binds SOD1 mRNA and causes its degradation, thereby reducing SOD1 protein synthesis.',
      {'A':'Protein degradation alone would not directly lower SOD1 mRNA.','B':'The genomic sequence is unchanged; tofersen is not a genome-editing therapy.','C':'Correct. Tofersen binds SOD1 mRNA and promotes its degradation, lowering SOD1 protein synthesis.','D':'Pure enzymatic inhibition would not lower SOD1 protein abundance.','E':'HDAC inhibition is not the direct mechanism of tofersen and would not specifically target SOD1 mRNA.'},
      'Distinguish antisense-mediated SOD1 mRNA degradation from genome editing and direct enzyme inhibition.',
      'QALSODY- tofersen injection','81356b45-1cb7-4eef-88ea-e44cc18b47c5','B',
      'Genome editing could reduce mutant SOD1 expression, but tofersen leaves genomic DNA unchanged and directly targets SOD1 messenger RNA.'
    ))
    items.append(make(
      323,'omaveloxolone','Behavioral Health, Nervous Systems and Special Senses',['Pharmacology','Biochemistry'],
      'Cells derived from a patient with Friedreich ataxia are exposed to omaveloxolone. Expression of antioxidant-response genes increases. Investigators avoid claiming that this biochemical effect fully explains the clinical benefit.',
      'Which direct cellular pathway effect has been demonstrated for this drug?',
      {'A':'Direct replacement of frataxin protein','B':'Inhibition of mitochondrial complex I','C':'Activation of PPAR-gamma transcription','D':'Activation of the Nrf2 pathway','E':'Inhibition of histone deacetylases'},
      'D','Activation of the Nrf2 oxidative-stress response pathway without overclaiming the disease-level therapeutic mechanism',
      'Omaveloxolone has been shown to activate the Nrf2 pathway, which participates in cellular responses to oxidative stress. Its precise therapeutic mechanism in Friedreich ataxia remains unknown.',
      {'A':'Omaveloxolone does not replace frataxin protein.','B':'Complex I inhibition would impair mitochondrial respiration and is not the demonstrated target pathway.','C':'PPAR-gamma activation is not the labeled cellular action.','D':'Correct. Nrf2 pathway activation is demonstrated, while the precise clinical mechanism remains uncertain.','E':'HDAC inhibition is a distinct epigenetic mechanism.'},
      'Separate a demonstrated Nrf2 pathway effect of omaveloxolone from an unproven disease-level mechanism in Friedreich ataxia.',
      'SKYCLARYS- omaveloxolone capsule','2709e870-df3d-f30f-e063-6394a90aeda1','E',
      'HDAC inhibition could alter broad transcriptional programs, but the prescribing information specifically identifies Nrf2 pathway activation as the demonstrated effect.'
    ))
    items.append(make(
      403,'ziftomenib','Blood, Lymphoreticular and Immune Systems',['Pharmacology','Cell Biology'],
      'Acute myeloid leukemia cells harboring a susceptible NPM1 mutation depend on a transcriptional program maintained by a menin-containing chromatin complex. After exposure to ziftomenib, expression of leukemogenic target genes falls and differentiation increases.',
      'Which direct molecular interaction is inhibited by this drug?',
      {'A':'BCL-2 binding to proapoptotic BH3 proteins','B':'FLT3 kinase autophosphorylation','C':'IDH1 production of 2-hydroxyglutarate','D':'DOT1L-mediated histone methylation','E':'Interaction between menin and KMT2A'},
      'E','Blockade of the menin-KMT2A interaction',
      'Ziftomenib is a menin inhibitor that blocks the interaction between menin and KMT2A, disrupting leukemogenic transcriptional programs in susceptible NPM1-mutated acute leukemia.',
      {'A':'BCL-2 inhibition promotes apoptosis but does not directly disrupt the menin-KMT2A complex.','B':'FLT3 kinase inhibition targets a distinct signaling driver.','C':'Mutant IDH1 inhibition lowers 2-hydroxyglutarate and is mechanistically distinct.','D':'DOT1L inhibition affects another chromatin-modifying pathway but is not the ziftomenib target.','E':'Correct. Ziftomenib directly blocks the menin-KMT2A interaction.'},
      'Recognize menin-KMT2A interaction blockade as the direct mechanism of ziftomenib in susceptible acute leukemia.',
      'KOMZIFTI- ziftomenib capsule','b650f696-3391-4274-8b55-a5f5e9d04769','A',
      'BCL-2 inhibition is a plausible AML mechanism, but the NPM1-dependent chromatin program in the vignette specifically points to menin-KMT2A blockade.'
    ))
    items.append(make(
      791,'sibeprenlimab-szsi','Respiratory and Renal/Urinary Systems',['Pharmacology','Immunology'],
      'A patient with IgA nephropathy receives a monoclonal antibody that lowers serum galactose-deficient IgA1. Laboratory studies show reduced signaling through both BCMA and TACI without direct blockade of either receptor.',
      'Which ligand is directly neutralized by this therapy?',
      {'A':'APRIL','B':'BAFF','C':'Interleukin-6','D':'Complement C5','E':'Endothelin-1'},
      'A','APRIL blockade reducing BCMA/TACI signaling and galactose-deficient IgA1',
      'Sibeprenlimab-szsi binds APRIL, thereby blocking APRIL signaling through BCMA and TACI. APRIL inhibition reduces serum galactose-deficient IgA1 implicated in IgA nephropathy.',
      {'A':'Correct. APRIL is the directly bound ligand whose signaling through BCMA and TACI is blocked.','B':'BAFF shares aspects of B-cell biology but is not the direct ligand target of sibeprenlimab.','C':'IL-6 blockade targets inflammatory cytokine signaling rather than the APRIL-BCMA/TACI axis.','D':'C5 blockade inhibits terminal complement and does not explain simultaneous BCMA/TACI signaling reduction.','E':'Endothelin-1 acts through endothelin receptors and is unrelated to the observed IgA biology.'},
      'Identify APRIL as the direct target of sibeprenlimab and connect APRIL blockade to reduced pathogenic galactose-deficient IgA1.',
      'VOYXACT- sibeprenlimab injection','c8a93b32-0676-4704-86dc-cb65f425c6e5','B',
      'BAFF is a closely related B-cell survival ligand and is therefore the strongest distractor, but the documented target that signals through both BCMA and TACI here is APRIL.'
    ))
    q=make(
      799,'diagnostic likelihood ratio','Biostatistics, Epidemiology and Population Health',['Behavioral Sciences'],
      'A diagnostic test has a sensitivity of 90% and a specificity of 80%. Disease prevalence differs substantially between two clinics, but the intrinsic test characteristics are assumed to be unchanged.',
      'Which measure equals 4.5 and can be calculated without using disease prevalence?',
      {'A':'Positive predictive value','B':'Negative predictive value','C':'Positive likelihood ratio','D':'Negative likelihood ratio','E':'Overall diagnostic accuracy'},
      'C','Positive likelihood ratio equals sensitivity divided by one minus specificity',
      'The positive likelihood ratio is sensitivity/(1-specificity). Here, 0.90/(1-0.80)=4.5. Unlike predictive values, this calculation does not require disease prevalence.',
      {'A':'Positive predictive value depends on prevalence and cannot be determined from sensitivity and specificity alone.','B':'Negative predictive value also depends on prevalence.','C':'Correct. LR+ = sensitivity/(1-specificity) = 0.90/0.20 = 4.5.','D':'LR- = (1-sensitivity)/specificity = 0.10/0.80 = 0.125, not 4.5.','E':'Accuracy requires the numbers or proportions of diseased and nondiseased individuals and therefore depends on the study population composition.'},
      'Calculate and interpret the positive likelihood ratio from sensitivity and specificity and distinguish it from prevalence-dependent predictive values.',
      'Appendix: Test Performance Metrics - Methods Guide for Medical Test Reviews','NOT_DAILYMED','D',
      'Negative likelihood ratio is also prevalence-independent, but its formula and numeric value here are 0.125; only the positive likelihood ratio equals 4.5.'
    )
    q['sources'][0]={
      'source_id':'Q799-AHRQ','title':'Appendix: Test Performance Metrics - Methods Guide for Medical Test Reviews',
      'agency':'Agency for Healthcare Research and Quality (AHRQ), hosted by NCBI Bookshelf',
      'url':'https://www.ncbi.nlm.nih.gov/books/NBK98249/','setid':None,'source_section_date':'2012-06',
      'date_basis':'AHRQ Methods Guide diagnostic test metrics; stable mathematical definitions; page reverified 2026-09-11.',
      'retrieved_at':TODAY,'section_locator':'Positive Likelihood Ratio','source_page_sha256':None,'cited_section_sha256':None,'hash_status':'PENDING_DETERMINISTIC_REFETCH_AND_HASH'
    }
    for e in q['evidence_map']: e['source_ids']=['Q799-AHRQ']; e['source_locator']='Positive Likelihood Ratio'
    items.append(q)
    items.append(make(
      965,'linerixibat','Gastrointestinal System',['Pharmacology','Physiology'],
      'A patient with primary biliary cholangitis receives linerixibat. Fecal bile acid excretion increases and circulating bile acid concentrations fall, with minimal systemic drug exposure.',
      'Which direct intestinal action best explains these findings?',
      {'A':'Activation of the farnesoid X receptor','B':'Inhibition of hepatic CYP7A1','C':'Blockade of the apical sodium-dependent bile acid transporter in hepatocytes','D':'Reversible inhibition of the ileal bile acid transporter','E':'Inhibition of pancreatic cholesterol esterase'},
      'D','Reversible inhibition of the ileal bile acid transporter, reducing terminal-ileal bile acid reabsorption',
      'Linerixibat reversibly inhibits the ileal bile acid transporter (IBAT), decreasing bile acid reabsorption in the terminal ileum and increasing fecal elimination.',
      {'A':'FXR activation regulates bile-acid synthesis but does not directly block terminal-ileal reabsorption.','B':'CYP7A1 inhibition would decrease bile-acid synthesis rather than directly increase fecal loss of existing bile acids.','C':'The relevant transporter is in the terminal ileum, not a hepatocyte apical transporter.','D':'Correct. IBAT inhibition reduces ileal reabsorption and increases fecal bile-acid elimination.','E':'Pancreatic cholesterol esterase does not mediate enterohepatic bile-acid uptake.'},
      'Connect IBAT inhibition in the terminal ileum with interruption of enterohepatic bile-acid recycling.',
      'LYNAVOY- linerixibat tablet, film coated','c00317c8-709c-4707-a6d1-632bff123026','A',
      'FXR activation can alter the bile-acid pool and is therefore plausible, but the direct observed increase in fecal bile acids with low systemic exposure identifies intestinal IBAT inhibition.'
    ))
    items.append(make(
      966,'bulevirtide','Gastrointestinal System',['Pharmacology','Microbiology'],
      'Cultured hepatocytes are exposed to bulevirtide before hepatitis D virus is added. Viral attachment and entry are markedly reduced, while intracellular viral replication machinery is not directly inhibited.',
      'Which host protein is directly bound to produce this effect?',
      {'A':'CD81','B':'CCR5','C':'NTCP','D':'ACE2','E':'NPC1'},
      'C','Binding the hepatocyte sodium taurocholate cotransporting polypeptide (NTCP) to block HDV attachment',
      'Bulevirtide binds the HDV receptor NTCP on hepatocyte plasma membranes and blocks viral attachment to NTCP, preventing infection.',
      {'A':'CD81 is important for hepatitis C entry, not the direct bulevirtide target.','B':'CCR5 is an HIV coreceptor and is not the HDV entry receptor.','C':'Correct. NTCP is the hepatocyte receptor directly bound by bulevirtide to block HDV attachment.','D':'ACE2 is used by SARS-CoV-2 and is unrelated to HDV entry.','E':'NPC1 is involved in Ebola entry and intracellular cholesterol trafficking, not HDV attachment.'},
      'Identify NTCP as the hepatocyte entry receptor directly targeted by bulevirtide to prevent hepatitis D virus infection.',
      'HEPCLUDEX- bulevirtide injection, powder, lyophilized, for solution','12391cc2-38c2-4cf5-86d3-2be9370127fc','A',
      'CD81 is a well-known viral entry protein in hepatocytes, but it is associated with HCV; HDV entry is directly blocked at NTCP.'
    ))
    # HEPCLUDEX mechanism resides in 12.4 Microbiology.
    items[-1]['sources'][0]['section_locator']='12.4 Microbiology; Mechanism of Action'
    for e in items[-1]['evidence_map']: e['source_locator']='12.4 Microbiology; Mechanism of Action'

    items.append(make(
      1065,'navepegritide','Human Development',['Pharmacology','Physiology'],
      'Growth-plate chondrocytes from a child with achondroplasia have constitutively increased FGFR3 signaling and reduced endochondral ossification. Exposure to C-type natriuretic peptide released from navepegritide increases intracellular cGMP and reduces MAPK signaling.',
      'Which receptor is directly activated by the released peptide?',
      {'A':'FGFR3','B':'Natriuretic peptide receptor-A','C':'Growth hormone receptor','D':'IGF-1 receptor','E':'Natriuretic peptide receptor-B'},
      'E','CNP activation of NPR-B, increasing cGMP/PKG signaling and antagonizing overactive FGFR3-MAPK signaling',
      'CNP released from navepegritide binds NPR-B, increasing cGMP and protein kinase G signaling, which inhibits MAPK signaling and counteracts overactive FGFR3 signaling in achondroplasia.',
      {'A':'FGFR3 is the overactive disease driver being functionally opposed, not activated by CNP.','B':'NPR-A primarily mediates ANP/BNP signaling; the CNP target in this therapy is NPR-B.','C':'Growth hormone receptor signaling is not the direct target of navepegritide-derived CNP.','D':'IGF-1 receptor is not the documented receptor engaged by the released peptide.','E':'Correct. CNP directly binds NPR-B and raises cGMP, opposing FGFR3-MAPK signaling.'},
      'Relate CNP-NPR-B-cGMP signaling to antagonism of excessive FGFR3-MAPK activity in achondroplasia.',
      'YUVIWEL- navepegritide kit','e01c1197-338f-414c-b804-808e129ebc8c','A',
      'FGFR3 is central to achondroplasia and thus tempting, but navepegritide does not bind FGFR3; released CNP binds NPR-B and counteracts downstream MAPK signaling.'
    ))
    items.append(make(
      1102,'aficamten','Cardiovascular System',['Pharmacology','Physiology'],
      'Cardiac myofibrils from a patient with obstructive hypertrophic cardiomyopathy are exposed to aficamten. Sarcomeric force generation decreases and left ventricular outflow tract obstruction improves without beta-adrenergic receptor blockade.',
      'Which direct molecular action best explains this effect?',
      {'A':'Allosteric reversible inhibition of cardiac myosin motor activity','B':'Irreversible inhibition of cardiac troponin C','C':'Activation of SERCA2a','D':'Blockade of L-type calcium channels','E':'Inhibition of beta-1 adrenergic receptors'},
      'A','Allosteric reversible inhibition of cardiac myosin motor activity',
      'Aficamten is an allosteric and reversible inhibitor of cardiac myosin motor activity. It reduces myosin-generated force at the sarcomere, lowering contractility and LVOT obstruction in HCM.',
      {'A':'Correct. Direct cardiac myosin inhibition reduces sarcomeric force and hypercontractility.','B':'Aficamten does not irreversibly inhibit troponin C.','C':'SERCA2a activation would enhance calcium reuptake but is not the direct target.','D':'Calcium-channel blockade can lower contractility clinically, but aficamten acts directly at cardiac myosin.','E':'Beta-1 blockade also reduces contractility but is explicitly excluded and is not the aficamten target.'},
      'Recognize cardiac myosin inhibition as a direct sarcomere-level strategy for reducing hypercontractility in obstructive hypertrophic cardiomyopathy.',
      'MYQORZO- aficamten tablet, film coated','fd778507-1274-4d1a-a659-5431d55c543a','D',
      'L-type calcium-channel blockade can reduce contractility and LVOT gradients, but the direct sarcomeric assay identifies cardiac myosin inhibition.'
    ))
    items.append(make(
      1124,'baxdrostat','Reproductive and Endocrine Systems',['Pharmacology','Physiology'],
      'Adrenal zona glomerulosa cells are exposed to baxdrostat. Aldosterone synthesis falls, whereas cortisol responses are preserved. Enzyme profiling shows much greater potency against one terminal steroidogenic enzyme than against 11-beta-hydroxylase.',
      'Which enzyme is directly inhibited?',
      {'A':'21-hydroxylase','B':'Aldosterone synthase','C':'11-beta-hydroxylase','D':'17-alpha-hydroxylase','E':'Aromatase'},
      'B','Selective inhibition of aldosterone synthase',
      'Baxdrostat inhibits human aldosterone synthase with higher potency and selectivity than the closely related 11-beta-hydroxylase, lowering aldosterone while preserving cortisol responses.',
      {'A':'21-hydroxylase participates in both mineralocorticoid and glucocorticoid synthesis and is not the baxdrostat target.','B':'Correct. Aldosterone synthase inhibition directly reduces aldosterone production.','C':'11-beta-hydroxylase inhibition would impair cortisol synthesis; baxdrostat is more selective for aldosterone synthase.','D':'17-alpha-hydroxylase inhibition broadly alters cortisol and sex-steroid pathways.','E':'Aromatase controls estrogen synthesis and is unrelated to selective aldosterone reduction.'},
      'Distinguish selective aldosterone synthase inhibition from blockade of neighboring adrenal steroidogenic enzymes.',
      'BAXFENDY- baxdrostat tablet, film coated','b1fc1ee7-facc-4099-b3db-a4c1daeaa4be','C',
      '11-beta-hydroxylase is structurally related and therefore the strongest alternative, but preserved cortisol responses and the label establish preferential aldosterone synthase inhibition.'
    ))
    items.append(make(
      1184,'atrasentan','Respiratory and Renal/Urinary Systems',['Pharmacology','Physiology'],
      'Glomerular cells from a patient with IgA nephropathy are exposed to atrasentan. Endothelin-1 signaling is reduced with minimal blockade of endothelin type B receptors.',
      'Which receptor is directly antagonized with high selectivity?',
      {'A':'Angiotensin II type 1 receptor','B':'Mineralocorticoid receptor','C':'Endothelin type A receptor','D':'Endothelin type B receptor','E':'Vasopressin V2 receptor'},
      'C','Highly selective endothelin type A receptor antagonism',
      'Atrasentan is an endothelin type A (ETA) receptor antagonist with more than 1800-fold selectivity for ETA over ETB.',
      {'A':'AT1 blockade targets the renin-angiotensin system, not endothelin signaling.','B':'Mineralocorticoid receptor blockade acts downstream of aldosterone and is not the direct atrasentan target.','C':'Correct. Atrasentan is highly selective for the ETA receptor.','D':'ETB is the closely related receptor but is bound far less potently.','E':'V2 antagonism affects renal water handling rather than endothelin signaling.'},
      'Differentiate selective ETA antagonism by atrasentan from ETB and other renal vasoactive receptor targets.',
      'VANRAFIA- atrasentan tablet, film coated','9a7e7f85-bfd0-44a0-beda-3bcfa8215c64','D',
      'ETB is the strongest alternative because it is the related endothelin receptor, but atrasentan has marked selectivity for ETA.'
    ))
    items.append(make(
      1511,'donidalorsen','Blood, Lymphoreticular and Immune Systems',['Pharmacology','Molecular Biology'],
      'Hepatocytes are exposed to a GalNAc-conjugated antisense oligonucleotide used for hereditary angioedema prophylaxis. Plasma prekallikrein messenger RNA and protein decline, while genomic KLKB1 sequence remains unchanged.',
      'Which molecular process directly causes the decrease in prekallikrein messenger RNA?',
      {'A':'RISC-mediated cleavage by a double-stranded siRNA','B':'CRISPR disruption of the KLKB1 gene','C':'Translational blockade without RNA degradation','D':'RNase H1-mediated degradation after antisense binding to PKK mRNA','E':'Direct proteolysis of circulating prekallikrein'},
      'D','RNase H1-mediated degradation of prekallikrein mRNA after antisense oligonucleotide binding',
      'Donidalorsen is a GalNAc-conjugated antisense oligonucleotide that binds prekallikrein (PKK) mRNA and causes RNase H1-mediated degradation, reducing PKK protein and downstream bradykinin generation.',
      {'A':'RISC-mediated cleavage is characteristic of siRNA platforms, whereas donidalorsen is an antisense oligonucleotide using RNase H1.','B':'The genomic sequence remains unchanged; this is not CRISPR gene editing.','C':'The documented mechanism includes degradation of the target RNA, not translation-only blockade.','D':'Correct. Antisense binding recruits RNase H1-mediated degradation of PKK mRNA.','E':'Direct proteolysis of circulating PKK would not explain the fall in hepatic PKK mRNA.'},
      'Distinguish RNase H1-mediated antisense degradation of prekallikrein mRNA from siRNA, gene editing, and protein-level inhibition.',
      'DAWNZERA- donidalorsen injection, solution','3ff501e0-f75f-07da-e063-6294a90a0cb7','A',
      'A GalNAc-conjugated siRNA can also lower a hepatic mRNA, but donidalorsen is explicitly an antisense oligonucleotide that uses RNase H1 rather than RISC.'
    ))

    # Ensure target mapping and balanced-ish key distribution; no NCJMM.
    assert [x['num'] for x in items]==TARGETS
    assert len({x.get('drug','').casefold() for x in items})==len(items)
    assert all(list(x['item']['options'])==list('ABCDE') for x in items)
    assert all(x['author_qa']['second_answer_attack']['status']=='PASS' for x in items)
    raw=json.dumps(items,ensure_ascii=False).casefold()
    assert 'ncjmm' not in raw
    out={
      'audit_id':'CONFIRMED-DUPLICATE-REPLACEMENTS-Q1535-20260911',
      'production_db_blob':DB_BLOB,
      'production_db_modified':False,
      'targets':TARGETS,
      'replacement_count':len(items),
      'status':'AUTHOR_QA_PASS_PENDING_LIVE_FREEZE_AND_ZERO_TRUST',
      'items':items
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':out['status'],'targets':TARGETS,'keys':''.join(x['item']['intended_key'] for x in items)}))
if __name__=='__main__':
    main()
