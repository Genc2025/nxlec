#!/usr/bin/env python3
from __future__ import annotations
import audit_q1261_q1270_readonly as a

# Tighten the anchor gate after direct canonical diagnosis:
# - Q1266 was a true PLN/SERCA2a duplicate and has been replaced by FLNC.
# - Q1270's generic 'bicuspid aortic valve' hit was incidental in a Q-fever item;
#   NOTCH1 itself had no canonical hit, so use construct-specific anchors only.
a.UNIQUE[1266]=['flnc','filamin c truncating']
a.UNIQUE[1270]=['notch1']

# Rebuild the adversarial alternative for the repaired Q1266. The prior text
# belonged to the discarded PLN item and must not be allowed to contaminate
# the final audit of the FLNC replacement.
a.SECOND[1266]=(
    'E',
    'Some FLNC variants, particularly classes associated with myofibrillar skeletal myopathy, can produce skeletal-muscle aggregates and weakness. However, truncating FLNC variants are well documented in predominantly cardiac arrhythmogenic/dilated cardiomyopathy with ventricular arrhythmias, myocardial fibrosis, cell-cell adhesion abnormalities, and no obligatory skeletal-muscle phenotype; the vignette explicitly matches that cardiac-restricted truncating-variant pattern.'
)

if __name__=='__main__':
    a.main()
