#!/usr/bin/env python3
"""Offline validation of a bounded inspection package, never a Flink runner.

No network, subprocess, engine installation, native checkpoint access, or
experiment execution. A trusted Git checkout, not this editable manifest alone,
is the integrity trust anchor. Passing proves consistency of supplied files only.
"""
import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

SOURCE_COMMIT = '5a3971445307f117285128e5d075ce2ecc7a95eb'
PUBLIC_BASE = 'e669b323a956e92908f7cbae18876501f1389a15'
PAPER_BASE = '03e715348b5dbe3a0f3656c5bfb95d0f7735cf51'
CASES = ('FLINK-25429', 'FLINK-25524', 'FLINK-28843', 'FLINK-38483')
POLICIES = ('fresh-only', 'configuration-only', 'history-aware', 'incident-oracle')
REVISIONS = {
    'FLINK-25429': ('11f74d875a8fa0f4a7e4987026c10a3748820ab1', '804eb8dda556a2bea35c69a2662f13d1dafb9255'),
    'FLINK-25524': ('34de3989a613cf7124f9e301cb8284080f4df4ac', 'd0927dd41e2f0441e4e5825ff423dd0e903713f3'),
    'FLINK-28843': ('0e6e4198ad84227c20e2c61c2dd8b0616324aa31', '7f708d0ba42f727b3f8c3d77cef2108206cad2de'),
    'FLINK-38483': ('17c1b22d53cadca05416fa9b7acf4ac6f279df43', 'cc55c56ace4401c2a4023153d9e17001ab5fcc85'),
}
RECEIPT_KEYS = {'effective_configuration', 'persisted_state_identity', 'lineage_predecessor', 'realized_regime', 'target_phase'}
INTEGRITY = 'artifacts/manifests/integrity.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_json(path):
    def nonfinite(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object, parse_constant=nonfinite)


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames and len(set(reader.fieldnames)) == len(reader.fieldnames), 'duplicate/empty CSV header: ' + path.name)
        rows = list(reader)
        require(all(None not in row and all(value is not None for value in row.values()) for row in rows), 'malformed CSV: ' + path.name)
        return rows


def safe_relative(value):
    require(isinstance(value, str) and value, 'invalid path')
    p = PurePosixPath(value)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in value and p.as_posix() == value, 'unsafe/noncanonical relative path: ' + value)
    return value


def package_files(root):
    paths = []
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if '.git' in rel.parts or '__pycache__' in rel.parts:
            continue
        require(not path.is_symlink(), 'symlink is not a package artifact: ' + str(rel))
        if path.is_file():
            paths.append(rel.as_posix())
    return sorted(paths)


def check_integrity(root):
    manifest = load_json(root / INTEGRITY)
    require(manifest['schema'] == 'lifecycle-regime-ci.compact-integrity.v1', 'integrity schema')
    entries = manifest['files']
    names = [safe_relative(x['path']) for x in entries]
    require(len(names) == len(set(names)), 'duplicate inventory path')
    require(set(package_files(root)) == set(names) | {INTEGRITY}, 'package membership differs from integrity inventory')
    for entry in entries:
        data = (root / entry['path']).read_bytes()
        require(len(data) == entry['bytes'] and sha256(data) == entry['sha256'], 'integrity mismatch: ' + entry['path'])
    return len(entries) + 1


def check_provenance(root):
    manifest = load_json(root / 'artifacts/manifests/provenance.json')
    require(manifest['schema'] == 'lifecycle-regime-ci.compact-provenance.v1', 'provenance schema')
    require(manifest['source_snapshot_commit'] == SOURCE_COMMIT and manifest['scientific_manuscript_baseline'] == PAPER_BASE and manifest['existing_public_package_baseline'] == PUBLIC_BASE, 'source/baseline identity changed')
    entries = manifest['artifacts']
    paths = [safe_relative(x['artifact_path']) for x in entries]
    require(len(paths) == len(set(paths)), 'duplicate provenance destination')
    required = {p for p in package_files(root) if p.startswith(('artifacts/protocols/', 'artifacts/results/', 'artifacts/receipts/'))}
    required |= {'artifacts/manifests/revisions.json', 'artifacts/manifests/environments.json', 'artifacts/manifests/revision_manifest.md'}
    require(set(paths) == required, 'evidence/provenance coverage differs')
    for entry in entries:
        data = (root / entry['artifact_path']).read_bytes()
        require(entry['sources'], 'missing source reference')
        for source in entry['sources']:
            safe_relative(source['path'])
            expected_commit = SOURCE_COMMIT if source['repository'] == 'UpbeatH/DataAnalyticsTune' else PUBLIC_BASE if source['repository'] == 'UpbeatH/LifecycleRegimeCI-Artifacts' else None
            require(expected_commit and source['commit'] == expected_commit, 'unrecognized source repository/commit')
            require(re.fullmatch('[0-9a-f]{40}', source['git_blob_sha1']) and re.fullmatch('[0-9a-f]{64}', source['sha256']), 'malformed source digest')
            require(source['url'] == 'https://github.com/{}/blob/{}/{}'.format(source['repository'], source['commit'], source['path']), 'source URL mismatch')
        if entry['transformation'] in ('byte-for-byte copy of selected compact source', 'unchanged existing public compact summary'):
            source = entry['sources'][0]
            require(len(entry['sources']) == 1 and len(data) == source['bytes'] and sha256(data) == source['sha256'] and git_blob(data) == source['git_blob_sha1'], 'literal source copy mismatch: ' + entry['artifact_path'])
        if 'source_line_ranges' in entry:
            require(entry['source_line_ranges'] == [[1, 193]], 'protocol excerpt range changed')
            excerpt = data.split(b'\n---\n\n', 1)
            require(len(excerpt) == 2 and sha256(excerpt[1]) == entry['excerpt_sha256'], 'protocol excerpt changed')
        if 'removed_json_keys' in entry:
            require(entry['removed_json_keys'] == ['host_label'] and 'host_label' not in load_json(root / entry['artifact_path']), 'capture redaction differs')
    return len(entries)


def check_boundaries(root):
    absolute = re.compile(r'(?<![A-Za-z0-9_])/(?:data|home|mnt|root|workspace)/|[A-Za-z]:\\(?:[^\s\\]+\\)+')
    credentials = re.compile(r'(?:AKI' + r'A[0-9A-Z]{16}|gh' + r'p_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
    for name in package_files(root):
        path = root / name
        require(path.suffix in {'.md', '.json', '.jsonl', '.csv', '.py'}, 'non-text/raw artifact type: ' + name)
        data = path.read_bytes()
        require(len(data) < 200000, 'file exceeds bounded compact size: ' + name)
        text = data.decode('utf-8')
        require('\0' not in text and not absolute.search(text), 'private absolute path or binary content: ' + name)
        require(not credentials.search(text), 'credential-like content: ' + name)
    readme = (root / 'README.md').read_text()
    for boundary in ('not a complete native reproduction environment', 'not a reconstruction framework', 'four original issue/fix cases', 'later null', 'No new experiment'):
        require(boundary in readme, 'missing README boundary: ' + boundary)


def check_original(root):
    base = root / 'artifacts/results'
    policy = read_csv(base / 't3-policy-detection.csv')
    summary = load_json(base / 't3-summary.json')
    compact = read_csv(base / 'reproduction_matrix.csv')
    require([x['incident'] for x in policy] == list(CASES) and [x['case'] for x in compact] == list(CASES), 'original four-case identities/order changed')
    require(summary['independent_incidents'] == 4 and summary['physical_launches'] == 66 and summary['logical_policy_cells'] == 96 and summary['selected_history_child_false_positives'] == 0 and summary['all_rows_valid_and_consistent'] is True, 'original denominator or validity changed')
    expected_counts = {'fresh-only': 0, 'configuration-only': 1, 'history-aware': 4, 'incident-oracle': 4}
    require(summary['detection_counts'] == expected_counts, 'original detection counts changed')
    for item in summary['source_files']:
        local = base / 'original' / PurePosixPath(item['path']).name
        require(sha256(local.read_bytes()) == item['sha256'], 'summary source hash mismatch: ' + local.name)
    for case, aggregate, published in zip(CASES, policy, compact):
        digits = case.split('-')[1]
        uploader = digits == '25429'
        name = 'flink-' + digits + ('-runs.csv' if uploader else '-matrix.csv')
        rows = read_csv(base / 'original' / name)
        decision = load_json(base / 'original' / ('flink-' + digits + ('-decision.json' if uploader else '-matrix-decision.json')))
        contexts = ('fresh-only', 'history-aware') if uploader else POLICIES[:3]
        require(len(rows) == (12 if uploader else 18), 'physical row count: ' + case)
        keys = [(r['role'], r['executed_policy'], r['rep'] if uploader else r['block']) for r in rows]
        expected = {(role, policy_name, str(rep)) for role in ('parent', 'child') for policy_name in contexts for rep in (1, 2, 3)}
        require(len(keys) == len(set(keys)) and set(keys) == expected, 'duplicate/missing role/context/block: ' + case)
        require(len({r['run_id'] for r in rows}) == len(rows), 'duplicate run ID: ' + case)
        for row in rows:
            parent = row['role'] == 'parent'
            history = row['executed_policy'] == 'history-aware'
            require(row['revision'] == REVISIONS[case][0 if parent else 1], 'engine revision mismatch: ' + case)
            if uploader:
                fail = parent and history
                require(int(row['exit_code']) == int(fail) and int(row['marker']) == int(not fail), 'uploader oracle mismatch')
                aliases = 'configuration-only;history-aware;incident-oracle' if history else 'fresh-only'
                require(row['scored_policies'] == aliases, 'uploader shared-row alias changed')
            else:
                is_notification = digits == '25524'
                fail = parent and history and not is_notification
                require(int(row['command_exit_code']) == int(fail) and int(row['failures']) == int(fail) and int(row['errors']) == 0, 'target result differs: ' + case)
                require(int(row['tests']) == {'25524': 1, '28843': 3, '38483': 5}[digits], 'target parameterization count: ' + case)
                if is_notification:
                    require(int(row['observed_checkpoint_id']) == (200 if history and not parent else 0), 'notification forwarded-ID oracle changed')
                else:
                    field = 'file_not_found' if digits == '28843' else 'target_exception'
                    require(row[field] == ('true' if fail else 'false'), 'target exception changed: ' + case)
                    if digits == '38483':
                        require(row['skipped'] == '0', 'topology skipped tests')
        detections = dict(zip(POLICIES, (0, int(uploader), 1, 1)))
        require(all(int(aggregate[p]) == detections[p] for p in POLICIES), 'case detection summary differs')
        require(int(aggregate['physical_launches']) == len(rows) and int(aggregate['logical_policy_cells']) == 24 and aggregate['selected_history_child_false_positive'] == '0', 'case accounting differs')
        expected_decision = 'T3_FLINK_25429_VALID_CONFIG_BASELINE_DETECTS' if uploader else 'T3_FLINK_' + digits + '_HISTORY_ADVANTAGE'
        require(aggregate['retained_decision'] == decision['decision'] == expected_decision, 'retained decision differs')
        if uploader:
            require([decision[k] for k in ('fresh_detection', 'configuration_detection', 'history_detection', 'oracle_detection')] == list(detections.values()) and decision['physical_launches'] == 12 and decision['logical_policy_cells'] == 24 and decision['child_false_positive'] == 0, 'uploader decision accounting differs')
        else:
            require(decision['incident_detection'] == {k: bool(v) for k, v in detections.items()} and decision['physical_cells'] == 18 and decision['logical_cells'] == 24 and decision['consistent'] is True, 'matrix decision accounting differs')
            require(decision['child_expectations_pass' if digits == '25524' else 'child_cells_pass'] is True, 'child validity differs')
        for output, p in zip(('fresh', 'configuration_only', 'lifecycle_history', 'manual_reference'), POLICIES):
            require(published[output] == ('OK' if detections[p] else 'X'), 'existing public compact summary differs')
    require(sum(int(x['physical_launches']) for x in policy) == 66 and sum(int(x['logical_policy_cells']) for x in policy) == 96, 'cross-case accounting differs')


def check_later_nulls(root):
    base = root / 'artifacts/results/later-restore'
    policies = {'full-history-native', 'latest-native-anchor', 'early-native-anchor'}
    for label in ('stabilized-null', 'replication-technical-invalid', 'replicated-null'):
        rows = read_csv(base / label / 'flink-28843-anchor-baselines.csv')
        decision = load_json(base / label / 'decision.json')
        invalid = label == 'replication-technical-invalid'
        require(len(rows) == 18 and decision['physical_cells'] == 18, 'later matrix row count')
        require(decision['decision'] == ('L2_TECHNICAL_INVALID' if invalid else 'L2_INCIDENT_NULL'), 'later null/invalid relabeled')
        require(decision['consistent_and_valid'] is (not invalid), 'later validity mismatch')
        require(decision['incident_detection'] == {p: False for p in policies}, 'later incident detection changed')
        keys = [(r['role'], r['policy'], r['block']) for r in rows]
        require(len(set(keys)) == 18 and set(keys) == {(role, p, str(b)) for role in ('parent', 'child') for p in policies for b in (1, 2, 3)}, 'later duplicate/missing cells')
        bad = []
        for row in rows:
            require(row['revision'] == REVISIONS['FLINK-28843'][0 if row['role'] == 'parent' else 1], 'later revision mismatch')
            if row['target_exit_code'] != '0' or row['target_tests'] != '3' or row['target_failures'] != '0' or row['target_errors'] != '0':
                bad.append((row['role'], row['policy'], row['block']))
            require(row['target_file_not_found'] == 'false', 'later target exception differs')
            if not invalid:
                require(row['target_phase_receipts'] == '3' and row['target_other_failures'] == '0', 'later target receipt/failure differs')
                require(int(row['total_ns']) == int(row['prepare_ns']) + int(row['target_ns']), 'later cost ledger arithmetic differs')
                if label == 'replicated-null':
                    require(row['topology_receipts'] == '3' and row['effective_setting_receipts'] == '3', 'replication receipt completeness differs')
        require(bad == [('child', 'full-history-native', '1')] if invalid else not bad, 'later technical-invalid sentinel changed or null contains failure')


def normalize(receipt, revision, contract):
    profiles = [p for p in contract['profiles'] if p['source_revision'] == revision]
    require(len(profiles) == 1, 'missing/duplicate exact-revision profile')
    result = copy.deepcopy(receipt)
    for rule in profiles[0]['rules']:
        require(rule['path'] == ['effective_configuration', 'restart_strategy'], 'unexpected normalization path')
        require(rule['canonical_value'] == 'disable' and rule['accepted_values'] == ['disable', 'none', 'off'], 'alias contract changed')
        node = result['effective_configuration']
        if 'restart_strategy' in node:
            require(node['restart_strategy'] in rule['accepted_values'], 'unknown covered configuration value')
            node['restart_strategy'] = rule['canonical_value']
    return result


def check_receipts(root):
    receipt_dir = root / 'artifacts/receipts'
    results = root / 'artifacts/results'
    contract = load_json(receipt_dir / 'canonicalization-contract.json')
    summary = read_csv(results / 'live-capture-summary.csv')
    aggregate = load_json(results / 'live-capture-aggregate.json')
    compact = read_csv(results / 'fidelity_summary.csv')
    require([r['gate'] for r in summary] == ['T6', 'T7', 'T9', 'T10'], 'historical capture rows changed')
    require(aggregate['selected_gates'] == ['T9', 'T10', 'T7'] and aggregate['selected_mechanisms'] == 3 and aggregate['raw_value_fidelity_mechanisms'] == 2 and aggregate['normalized_fidelity_mechanisms'] == 3 and aggregate['live_runs'] == 4, 'selected capture denominator changed')
    for gate, case in [('T9', 'FLINK-25524'), ('T10', 'FLINK-28843'), ('T7', 'FLINK-38483')]:
        reference = load_json(receipt_dir / (gate + '-reference.json'))
        captured = load_json(receipt_dir / (gate + '-captured.json'))
        require(set(reference) == set(captured) == RECEIPT_KEYS, 'five-field receipt schema differs')
        raw_equal = reference == captured
        require(raw_equal is (gate != 'T7'), 'raw fidelity endpoint changed')
        require(normalize(reference, REVISIONS[case][1], contract) == normalize(captured, REVISIONS[case][1], contract), 'bounded normalized comparison differs')
        events_path = receipt_dir / (gate + '-events.jsonl')
        events = [json.loads(x, object_pairs_hook=unique_object) for x in events_path.read_text().splitlines()]
        require(len(events) == 4 and [x['seq'] for x in events] == [1, 2, 3, 4] and [x['type'] for x in events] == ['effective-config', 'state-lineage', 'realized-regime', 'target-phase'], 'compact projection event order differs')
        expected_event_fields = [{'effective_configuration'}, {'persisted_state_identity', 'lineage_predecessor'}, {'realized_regime'}, {'target_phase'}]
        folded = {}
        for event, fields in zip(events, expected_event_fields):
            require(set(event) == fields | {'seq', 'type'}, 'unexpected compact event fields')
            folded.update({k: event[k] for k in fields})
        require(folded == captured, 'supplied event projection differs from captured receipt')
        result = load_json(results / 'capture' / (gate + '-result.json'))
        require('host_label' not in result and result['source_revision'] == REVISIONS[case][1], 'capture identity/redaction mismatch')
        for suffix, key in [('reference.json', 'expected_receipt_sha256'), ('captured.json', 'captured_receipt_sha256'), ('events.jsonl', 'live_event_sha256')]:
            require(sha256((receipt_dir / (gate + '-' + suffix)).read_bytes()) == result[key], 'capture source digest mismatch')
        require(result['live_event_count'] == 4 and result['live_event_bytes'] == len(events_path.read_bytes()), 'capture event count/size mismatch')
        require(result['test_report']['valid'] is True and result['test_report']['failures'] == result['test_report']['errors'] == 0, 'capture workload validity changed')
        if gate == 'T7':
            require(result['decision'] == 'T7_CROSS_MECHANISM_CAPTURE_NO_GO' and result['exact_receipt_fidelity'] is False and result['canonical_receipt_fidelity'] is False, 'T7 raw No-Go relabeled')
        else:
            require(result['raw_receipt_fidelity'] is True and result['normalized_receipt_fidelity'] is True, 'selected equality changed')
        row = next(r for r in summary if r['gate'] == gate)
        require(row['incident'] == case and row['raw_value_fidelity'] == str(raw_equal).lower() and row['normalized_fidelity'] == 'true', 'capture summary differs')
        public = next(r for r in compact if r['mechanism'] == case)
        require(public['raw_comparison'] == ('equal' if raw_equal else 'unequal') and public['normalized_comparison'] == 'equal', 'existing fidelity summary differs')
    require(len(compact) == 3 and {r['mechanism'] for r in compact} == set(CASES[1:]), 'fidelity case selection differs')


def check_manifests(root):
    revisions = load_json(root / 'artifacts/manifests/revisions.json')
    require(revisions['scientific_manuscript_baseline'] == PAPER_BASE and revisions['source_snapshot'] == {'repository': 'UpbeatH/DataAnalyticsTune', 'commit': SOURCE_COMMIT}, 'revision source identity differs')
    require([r['case'] for r in revisions['cases']] == list(CASES), 'revision case denominator changed')
    for row in revisions['cases']:
        require((row['parent'], row['child']) == REVISIONS[row['case']] and row['engine_repository'] == 'apache/flink', 'revision mapping differs')
    env = load_json(root / 'artifacts/manifests/environments.json')
    require(env['inspection_environment']['network_required'] is False and env['inspection_environment']['Flink_required'] is False, 'inspection environment expanded')
    require([x['os_family'] for x in env['historical_original_matrices']] == ['Windows', 'Linux', 'Linux', 'Linux'], 'mixed original environments lost')
    require(env['historical_later_restore']['replication_on_distinct_host'] is True, 'later replication environment collapsed')
    relationships = read_csv(root / 'artifacts/results/lifecycle_relationships.csv')
    require([(r['case'], r['category'], r['relationship']) for r in relationships] == [('FLINK-25524', 'notification_lineage', 'materialization_checkpoint_association'), ('FLINK-28843', 'checkpoint_restore_lineage', 'restore_chain_generation_order'), ('FLINK-38483', 'topology_transition_context', 'source_target_topology_relation')], 'existing lifecycle relationship map differs')


def validate(root):
    root = Path(root).resolve()
    count = check_integrity(root)
    provenance = check_provenance(root)
    check_boundaries(root)
    check_manifests(root)
    check_original(root)
    check_later_nulls(root)
    check_receipts(root)
    return {'status': 'PASS', 'package_files': count, 'provenance_entries': provenance, 'original_cases': 4, 'physical_launches': 66, 'logical_policy_cells': 96, 'selected_capture_mechanisms': 3, 'native_reproduction_performed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2], help='package root (default: inferred from script location)')
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root), indent=2))
    except (ValueError, KeyError, OSError, TypeError, StopIteration) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
