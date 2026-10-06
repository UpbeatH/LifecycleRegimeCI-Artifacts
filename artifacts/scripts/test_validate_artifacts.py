"""Regression tests for compact inspection checks; no native execution."""
import csv
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import validate_artifacts as validator


class CompactArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='lrci-inspection-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        source = Path(__file__).resolve().parents[2]
        shutil.copytree(source, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def change_json(self, relative, change):
        path = self.root / relative
        data = validator.load_json(path)
        change(data)
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

    def change_csv(self, relative, change):
        path = self.root / relative
        rows = validator.read_csv(path)
        change(rows)
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        path.write_text(stream.getvalue(), encoding='utf-8')

    def refresh_source_summary_hash(self, filename):
        digest = validator.sha256((self.root / 'artifacts/results/original' / filename).read_bytes())
        def change(data):
            for row in data['source_files']:
                if row['path'].endswith('/' + filename):
                    row['sha256'] = digest
        self.change_json('artifacts/results/t3-summary.json', change)

    def test_complete_package_passes(self):
        result = validator.validate(self.root)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['original_cases'], 4)
        self.assertFalse(result['native_reproduction_performed'])

    def test_tampered_bytes_fail_integrity(self):
        with (self.root / 'README.md').open('a') as stream:
            stream.write('unreviewed change\n')
        with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
            validator.check_integrity(self.root)

    def test_missing_artifact_fails(self):
        (self.root / 'artifacts/receipts/T9-reference.json').unlink()
        with self.assertRaisesRegex(ValueError, 'membership'):
            validator.check_integrity(self.root)

    def test_extra_artifact_fails(self):
        (self.root / 'unreviewed.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'membership'):
            validator.check_integrity(self.root)

    def test_symlink_fails(self):
        (self.root / 'linked.json').symlink_to(self.root / 'artifacts/receipts/T9-reference.json')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            validator.check_integrity(self.root)

    def test_inventory_traversal_fails(self):
        self.change_json(validator.INTEGRITY, lambda d: d['files'][0].update(path='../outside.json'))
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            validator.check_integrity(self.root)

    def test_duplicate_json_keys_fail(self):
        path = self.root / 'duplicate.json'
        path.write_text('{"x":1,"x":2}')
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            validator.load_json(path)

    def test_nonfinite_json_fails(self):
        path = self.root / 'nonfinite.json'
        path.write_text('{"x":NaN}')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            validator.load_json(path)

    def test_private_absolute_path_fails(self):
        private_path = '/' + 'home' + '/private-user/evidence'
        with (self.root / 'README.md').open('a') as stream:
            stream.write(private_path)
        with self.assertRaisesRegex(ValueError, 'private absolute'):
            validator.check_boundaries(self.root)

    def test_source_copy_identity_fails(self):
        with (self.root / 'artifacts/protocols/FLINK-25524-MATRIX-PREREGISTRATION.md').open('a') as stream:
            stream.write('changed\n')
        with self.assertRaisesRegex(ValueError, 'source copy mismatch'):
            validator.check_provenance(self.root)

    def test_denominator_change_fails_semantics(self):
        self.change_json('artifacts/results/t3-summary.json', lambda d: d.update(independent_incidents=5))
        with self.assertRaisesRegex(ValueError, 'denominator'):
            validator.check_original(self.root)

    def test_duplicate_matrix_cell_fails_semantics(self):
        name = 'flink-25524-matrix.csv'
        self.change_csv('artifacts/results/original/' + name, lambda rows: rows.__setitem__(1, dict(rows[0])))
        self.refresh_source_summary_hash(name)
        with self.assertRaisesRegex(ValueError, 'duplicate/missing'):
            validator.check_original(self.root)

    def test_notification_oracle_is_not_process_success(self):
        name = 'flink-25524-matrix.csv'
        def change(rows):
            for row in rows:
                if row['role'] == 'child' and row['executed_policy'] == 'history-aware':
                    row['observed_checkpoint_id'] = '0'
        self.change_csv('artifacts/results/original/' + name, change)
        self.refresh_source_summary_hash(name)
        with self.assertRaisesRegex(ValueError, 'forwarded-ID oracle'):
            validator.check_original(self.root)

    def test_existing_compact_summary_drift_fails(self):
        self.change_csv('artifacts/results/reproduction_matrix.csv', lambda rows: rows[0].update(configuration_only='X'))
        with self.assertRaisesRegex(ValueError, 'public compact summary'):
            validator.check_original(self.root)

    def test_later_null_cannot_be_reclassified(self):
        path = 'artifacts/results/later-restore/stabilized-null/decision.json'
        self.change_json(path, lambda d: d.update(decision='L2_FULL_HISTORY_ONLY'))
        with self.assertRaisesRegex(ValueError, 'null/invalid relabeled'):
            validator.check_later_nulls(self.root)

    def test_technical_invalid_cannot_be_pooled_as_null(self):
        path = 'artifacts/results/later-restore/replication-technical-invalid/decision.json'
        self.change_json(path, lambda d: d.update(decision='L2_INCIDENT_NULL'))
        with self.assertRaisesRegex(ValueError, 'null/invalid relabeled'):
            validator.check_later_nulls(self.root)

    def test_receipt_schema_change_fails(self):
        self.change_json('artifacts/receipts/T9-captured.json', lambda d: d.pop('lineage_predecessor'))
        with self.assertRaisesRegex(ValueError, 'five-field'):
            validator.check_receipts(self.root)

    def test_t7_raw_mismatch_must_survive(self):
        def change(data):
            data['effective_configuration']['restart_strategy'] = 'none'
        self.change_json('artifacts/receipts/T7-captured.json', change)
        with self.assertRaisesRegex(ValueError, 'raw fidelity endpoint'):
            validator.check_receipts(self.root)

    def test_t7_no_go_cannot_be_rewritten(self):
        self.change_json('artifacts/results/capture/T7-result.json', lambda d: d.update(decision='GO'))
        with self.assertRaisesRegex(ValueError, 'raw No-Go'):
            validator.check_receipts(self.root)

    def test_unknown_alias_fails_closed_and_original_is_unchanged(self):
        contract = validator.load_json(self.root / 'artifacts/receipts/canonicalization-contract.json')
        receipt = validator.load_json(self.root / 'artifacts/receipts/T7-reference.json')
        normalized = validator.normalize(receipt, validator.REVISIONS['FLINK-38483'][1], contract)
        self.assertEqual(receipt['effective_configuration']['restart_strategy'], 'none')
        self.assertEqual(normalized['effective_configuration']['restart_strategy'], 'disable')
        receipt['effective_configuration']['restart_strategy'] = 'unrecognized-value'
        with self.assertRaisesRegex(ValueError, 'unknown covered'):
            validator.normalize(receipt, validator.REVISIONS['FLINK-38483'][1], contract)

    def test_unknown_revision_fails_closed(self):
        contract = validator.load_json(self.root / 'artifacts/receipts/canonicalization-contract.json')
        receipt = validator.load_json(self.root / 'artifacts/receipts/T7-reference.json')
        with self.assertRaisesRegex(ValueError, 'exact-revision'):
            validator.normalize(receipt, '0' * 40, contract)

    def test_original_mixed_environments_must_survive(self):
        self.change_json('artifacts/manifests/environments.json', lambda d: d['historical_original_matrices'][0].update(os_family='Linux'))
        with self.assertRaisesRegex(ValueError, 'mixed original'):
            validator.check_manifests(self.root)


if __name__ == '__main__':
    unittest.main()
