"""Regression checks for importing unsubstantiated audit labels.

Synthetic dictionaries below test validation only; they are not clinical audits.
"""
import copy
import importlib.util
import json
import pathlib
import tempfile
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

    def test_missing_scores_rejected_for_every_batch_key(self):
        for number in importer.NEW_RANGE:
            with self.subTest(item=number):
                audit = self.fixture()
                audit['blind_audit']['selected_key'] = importer.KEY_SCHEDULE[number]
                del audit['scores']
                with self.assertRaisesRegex(SystemExit, 'missing recorded ten-domain auditor scores'):
                    importer.require_recorded_audit(audit, number)

    def test_incomplete_audit_stops_before_opening_database(self):
        # Isolate the historical import from subsequently updated repo artifacts.
        # Keep the real load_audits/require_recorded_audit path under test.
        with tempfile.TemporaryDirectory() as directory:
            audit = self.fixture()
            del audit['scores']
            pathlib.Path(directory, 'Q1191_FINAL_10_10_AUDIT.json').write_text(json.dumps(audit))
            with (patch.object(importer, 'AUDIT_DIR', pathlib.Path(directory)),
                  patch.object(importer, 'db_blob', return_value=importer.EXPECTED_PRE_DB_BLOB),
                  patch.object(importer, 'load_specs', return_value={}),
                  patch.object(importer, 'load_preflight', return_value={}),
                  patch.object(importer.sqlite3, 'connect') as connect):
                with self.assertRaisesRegex(SystemExit, 'missing recorded ten-domain auditor scores'):
                    importer.main()
                connect.assert_not_called()

    def test_changed_database_stops_before_loading_or_writing(self):
        with (patch.object(importer, 'db_blob', return_value='different-db-blob'),
              patch.object(importer, 'load_specs') as specs,
              patch.object(importer.sqlite3, 'connect') as connect):
            with self.assertRaisesRegex(SystemExit, 'authoritative DB blob changed'):
                importer.main()
            specs.assert_not_called()
            connect.assert_not_called()


if __name__ == '__main__':
    unittest.main()
