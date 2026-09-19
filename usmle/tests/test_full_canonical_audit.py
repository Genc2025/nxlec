import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit_full_canonical_compliance import criteria_defects, hobj, review_hash_valid

class AuditRegressionTests(unittest.TestCase):
    def minimal(self):
        return {'item':{'intended_key':'A','options':dict.fromkeys('ABCDE','option')},'blueprint':{'primary_system':'Human Development','official_outline_path':['Human Development','Older adulthood']}}
    def test_hierarchical_outline_is_not_collapsed(self):
        self.assertNotIn('blueprint_path_mismatch',criteria_defects(self.minimal()))
    def test_missing_key_does_not_crash(self):
        p=self.minimal();p['item']['intended_key']=None
        self.assertIn('invalid_key',criteria_defects(p))
    def test_option_order_is_not_a_content_defect(self):
        p=self.minimal();p['item']['options']={k:k for k in 'EDCBA'}
        self.assertNotIn('options_not_exact_A_E',criteria_defects(p))
    def test_direct_evidence_can_exclude_distractors(self):
        p=self.minimal();p['evidence_map']=[{'option':k,'direct_or_inference':'direct'} for k in 'ABCDE']
        defects=criteria_defects(p)
        self.assertNotIn('evidence_key_not_unique',defects)
        self.assertNotIn('distractor_evidence_not_inference',defects)
    def test_legacy_hash_recomputed_not_self_asserted(self):
        p={'verdict':'FINAL_10_10_PASS','defects':[]};digest=hobj(p)
        p['review_sha256']=digest
        self.assertTrue(review_hash_valid(p,digest))
        p['defects']=['changed after hashing']
        self.assertFalse(review_hash_valid(p,digest))
    def test_whole_document_hash(self):
        p={'verdict':'BLOCKED'}
        self.assertTrue(review_hash_valid(p,hobj(p)))

if __name__=='__main__':unittest.main()
