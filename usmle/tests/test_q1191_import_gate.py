"""Regression checks for importing unsubstantiated audit labels.

Synthetic dictionaries below test validation only; they are not clinical audits.
"""
import copy
import importlib.util
import json
import pathlib
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('q1191_importer', ROOT / 'step2_import_q1191_q1215.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


class AuditGateTests(unittest.TestCase):
    def fixture(self):
        return {
            'scores': {name: 10 for name in importer.AUDIT_SCORE_DOMAINS},
            'verdict': 'PASS_WITH_NO_CHANGES',
            'defects': [], 'suggested_changes': [],
            'blind_audit': {
                'selected_key': importer.KEY_SCHEDULE[1191],
                'alternative_defensible_options': [],
                'missing_assumptions': [], 'cueing_findings': [],
            },
        }

    def test_recorded_fields_are_necessary(self):
        for field in ('scores', 'verdict', 'defects', 'suggested_changes', 'blind_audit'):
            with self.subTest(field=field):
                audit = self.fixture()
                del audit[field]
                with self.assertRaises(SystemExit):
                    importer.require_recorded_audit(audit, 1191)

    def test_scores_cannot_be_rounded_or_coerced(self):
        for value in (9, 10.0, True, '10'):
            with self.subTest(value=value):
                audit = self.fixture()
                audit['scores']['evidence_quality'] = value
                with self.assertRaises(SystemExit):
                    importer.require_recorded_audit(audit, 1191)

    def test_unresolved_findings_and_wrong_key_fail(self):
        variants = [
            ('verdict', 'REJECT'),
            ('defects', ['Unsupported claim']),
            ('suggested_changes', ['Correct the citation']),
        ]
        for field, value in variants:
            with self.subTest(field=field):
                audit = self.fixture()
                audit[field] = value
                with self.assertRaises(SystemExit):
                    importer.require_recorded_audit(audit, 1191)
        for field, value in (
            ('selected_key', 'A'),
            ('alternative_defensible_options', ['A']),
            ('missing_assumptions', ['Unstated condition']),
            ('cueing_findings', ['Answer length']),
        ):
            with self.subTest(blind_field=field):
                audit = self.fixture()
                audit['blind_audit'][field] = value
                with self.assertRaises(SystemExit):
                    importer.require_recorded_audit(audit, 1191)

    def test_gate_does_not_mutate_recorded_audit(self):
        audit = self.fixture()
        before = copy.deepcopy(audit)
        importer.require_recorded_audit(audit, 1191)
        self.assertEqual(before, audit)

    def test_all_original_staged_audits_lack_required_scores(self):
        for number in importer.NEW_RANGE:
            with self.subTest(item=number):
                audit = json.loads((importer.AUDIT_DIR / f'Q{number:04d}_FINAL_10_10_AUDIT.json').read_text())
                with self.assertRaisesRegex(SystemExit, 'missing recorded ten-domain auditor scores'):
                    importer.require_recorded_audit(audit, number)

    def test_staged_run_stops_before_opening_database(self):
        with patch.object(importer.sqlite3, 'connect') as connect:
            with self.assertRaisesRegex(SystemExit, 'missing recorded ten-domain auditor scores'):
                importer.main()
            connect.assert_not_called()


if __name__ == '__main__':
    unittest.main()
