#!/usr/bin/env python3
from __future__ import annotations
import audit_q1261_q1270_readonly as a

# Tighten the anchor gate after direct canonical diagnosis:
# - Q1266 was a true PLN/SERCA2a duplicate and has been replaced by FLNC.
# - Q1270's generic 'bicuspid aortic valve' hit was incidental in a Q-fever item;
#   NOTCH1 itself had no canonical hit, so use construct-specific anchors only.
a.UNIQUE[1266]=['flnc','filamin c truncating']
a.UNIQUE[1270]=['notch1']

if __name__=='__main__':
    a.main()
