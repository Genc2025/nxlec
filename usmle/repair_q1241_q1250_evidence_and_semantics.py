#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parent
GEN=ROOT/'generate_q1241_q1250_candidate.py'
AUD=ROOT/'audit_q1241_q1250_readonly.py'

DISCRIMINATORS={
1241:'the pathogenic CXCR4 variant together with marrow retention of abundant mature neutrophils; that genotype-phenotype pair supports hyperactive CXCR4-CXCL12 signaling and myelokathexis',
1242:'the combined monocytopenia, marked B/NK-cell depletion, dysplasia, HPV susceptibility, and familial myeloid-malignancy pattern; that combination supports GATA2 deficiency',
1243:'the recessive childhood syndrome combining livedoid medium-vessel vasculopathy, hypertension, recurrent lacunar strokes, and hematologic disease; that pattern supports DADA2',
1244:'the explicitly identified gain-of-function PIK3CD variant; that lesion directly supports increased PI3K-delta signaling with downstream AKT-mTOR hyperactivation',
1245:'the specific immune function whose loss links inherited C1q deficiency to early lupus: recognition/opsonization and clearance of apoptotic material',
1246:'the biochemical reaction directly attributed to PNPLA1: transfer of linoleate to omega-hydroxyceramide during omega-O-acylceramide synthesis',
1247:'the molecular consequence of the KLHL24 start-codon variant: stabilization of truncated KLHL24 with excessive ubiquitination and proteasomal loss of keratin 14',
1248:'the combined ectodermal abnormalities with small, poorly formed desmosomes and reduced keratin-filament attachment; that pattern supports PKP1 deficiency',
1249:'the generalized lifelong superficial peeling, severe pruritus/atopy, normal LEKT1, and normal hair microscopy; that pattern supports CDSN-related inflammatory peeling skin syndrome',
1250:'the combination of lifelong basal-keratinocyte skin fragility and later progressive muscular dystrophy; that syndromic pattern supports PLEC-associated EBS with muscular dystrophy'
}

UNIQUE_ANCHORS={
1241:['WHIM syndrome','CXCR4 gain of function','myelokathexis'],
1242:['GATA2 deficiency','MonoMAC'],
1243:['DADA2','deficiency of adenosine deaminase 2'],
1244:['activated PI3K delta syndrome','PIK3CD gain of function'],
1245:['C1q deficiency','deficiency of C1q'],
1246:['PNPLA1','omega-O-acylceramide'],
1247:['KLHL24','stabilizing mutations of KLHL24'],
1248:['PKP1','plakophilin 1 deficiency'],
1249:['CDSN deficiency','corneodesmosin deficiency'],
1250:['PLEC-associated epidermolysis bullosa simplex with muscular dystrophy','plectin muscular dystrophy']
}

def patch_generator():
    s=GEN.read_text()
    old="'A':'Dominant-negative disruption of keratin 14 heterodimer assembly'"
    new="'A':'A primary dominant-negative defect intrinsic to keratin 14'"
    if old not in s and new not in s:
        raise SystemExit('Q1247 option A anchor missing')
    s=s.replace(old,new)

    marker='\ndef usmle_source(q,system,competency):\n'
    if 'DISTRACTOR_DISCRIMINATORS=' not in s:
        if marker not in s: raise SystemExit('generator insertion marker missing')
        block='\nDISTRACTOR_DISCRIMINATORS='+repr(DISCRIMINATORS)+'\n\n'
        s=s.replace(marker,block+marker,1)

    old_build="def build(d):\n    q=d['num']; src=[usmle_source(q,d['system'],d['competency'])]"
    new_build="def build(d):\n    q=d['num']; src=[usmle_source(q,d['system'],d['competency'])]\n    grounded_wrong={}\n    for L in 'ABCDE':\n        if L==d['key']:\n            grounded_wrong[L]=d['wrong'][L]\n        else:\n            grounded_wrong[L]=f\"Option {L} proposes '{d['options'][L]}'. It is not selected because it does not account for {DISTRACTOR_DISCRIMINATORS[q]}.\""
    if old_build in s:
        s=s.replace(old_build,new_build,1)
    elif new_build not in s:
        raise SystemExit('build anchor missing')

    old_claim="'claim':d['wrong'][letter],"
    new_claim="'claim':grounded_wrong[letter],"
    if old_claim in s: s=s.replace(old_claim,new_claim,1)
    elif new_claim not in s: raise SystemExit('evidence claim anchor missing')

    old_exp="'explanation':{'key_explanation':d['keyexp'],'distractor_explanations':d['wrong'],'educational_objective':d['objective']},"
    new_exp="'explanation':{'key_explanation':d['keyexp'],'distractor_explanations':grounded_wrong,'educational_objective':d['objective']},"
    if old_exp in s: s=s.replace(old_exp,new_exp,1)
    elif new_exp not in s: raise SystemExit('explanation anchor missing')

    GEN.write_text(s)

def patch_audit():
    s=AUD.read_text()
    marker="SECOND_ANSWER={\n"
    if 'UNIQUE_ANCHORS={' not in s:
        if marker not in s: raise SystemExit('audit unique-anchor insertion marker missing')
        block='UNIQUE_ANCHORS='+repr(UNIQUE_ANCHORS)+'\n\n'
        s=s.replace(marker,block+marker,1)

    old="""        if exact_fp_hits: fail.append('canonical_semantic_fingerprint_hit')\n\n        sa=SECOND_ANSWER[q]"""
    new="""        unique_anchor_hits=[]\n        for anchor in UNIQUE_ANCHORS[q]:\n            na=norm(anchor)\n            for cid,ct in corpus:\n                if na in norm(ct):\n                    unique_anchor_hits.append({'candidate_id':cid,'anchor':na})\n        if unique_anchor_hits: fail.append('canonical_unique_construct_anchor_hit')\n\n        sa=SECOND_ANSWER[q]"""
    if old in s: s=s.replace(old,new,1)
    elif new not in s: raise SystemExit('semantic gate anchor missing')

    old_report="'semantic_fingerprint_hits':exact_fp_hits})"
    new_report="'semantic_fingerprint_hits_advisory':exact_fp_hits,'unique_construct_anchor_hits':unique_anchor_hits})"
    if old_report in s: s=s.replace(old_report,new_report,1)
    elif new_report not in s: raise SystemExit('audit report anchor missing')
    AUD.write_text(s)

if __name__=='__main__':
    patch_generator(); patch_audit()
    print('PATCHED_GENERATOR_AND_AUDIT')
