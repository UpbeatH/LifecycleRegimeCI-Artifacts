# LifecycleRegimeCI compact reviewer artifacts

Companion inspection package for **Understanding Lifecycle Context Requirements for Reproducible Stateful Stream Processing: An Empirical Study** (EDBT 2027 EA&B manuscript).

## Start here

1. Read the case-to-evidence map below, then inspect each local protocol and compact result.
2. Read [result/denominator guidance](artifacts/results/README.md), [receipt boundaries](artifacts/receipts/README.md), and the [separate later null](artifacts/results/later-restore/README.md).
3. Inspect [revision/environment/provenance metadata](artifacts/manifests/revision_manifest.md).
4. From this repository root, run the offline checks with Python 3.8 or newer:

```sh
python3 artifacts/scripts/validate_artifacts.py
python3 -B -m unittest discover -s artifacts/scripts -p 'test_*.py' -v
```

Both commands use only the Python standard library, require no network or Flink installation, and validate only the supplied compact artifacts. Passing checks do not establish native reproduction. The tests use temporary local copies; they do not change the package.

## Case → relationship → missing context → oracle → evidence

| Evidence entry | Lifecycle relationship and missing context | Fixed functional oracle | Local inspection route |
|---|---|---|---|
| FLINK-25429, configuration-sufficient control | Wrapped-stream ownership; the real uploader context suffices, with no added history advantage | Parent duplicate-close error, child valid upload/one close | [Control](artifacts/protocols/FLINK-25429-CONTROL.md), [result](artifacts/results/original/FLINK-25429-RESULT.md), [rows](artifacts/results/original/flink-25429-runs.csv) |
| FLINK-25524, original positive | Materialization-to-checkpoint notification association; configuration aliases both IDs to 0 | History forwards parent 0 vs child 200; both JVM probes pass | [Protocol](artifacts/protocols/FLINK-25524-MATRIX-PREREGISTRATION.md), [rows](artifacts/results/original/flink-25524-matrix.csv), [decision](artifacts/results/original/flink-25524-matrix-decision.json), [T9 receipt](artifacts/receipts/T9-captured.json) |
| FLINK-28843, original positive | Checkpoint generation and restore-chain order; configuration omits second-generation lineage/second restore | Target parent FileNotFoundException in one of three parameterizations; child passes three | [Protocol](artifacts/protocols/FLINK-28843-MATRIX-PREREGISTRATION.md), [rows](artifacts/results/original/flink-28843-matrix.csv), [decision](artifacts/results/original/flink-28843-matrix-decision.json), [T10 receipt](artifacts/receipts/T10-captured.json) |
| FLINK-38483, original positive | Source-to-target topology over checkpoint state; same-topology restore omits rescale transition | Parent no-state-descriptor exception in one of five parameterizations; child passes five | [Protocol](artifacts/protocols/FLINK-38483-MATRIX-PREREGISTRATION.md), [rows](artifacts/results/original/flink-38483-matrix.csv), [decision](artifacts/results/original/flink-38483-matrix-decision.json), [T7 receipt](artifacts/receipts/T7-captured.json) |
| FLINK-28843, later null condition | Stabilized full-history and native-anchor constructions; changed harness context limits portability | All parent/child targets pass in each separate valid 18-cell matrix; no incident oracle reproduced | [Amended protocol](artifacts/protocols/LATER-RESTORE-PROTOCOL.md), [null/invalid distinction](artifacts/results/later-restore/README.md), [stabilized decision](artifacts/results/later-restore/stabilized-null/decision.json), [replicated decision](artifacts/results/later-restore/replicated-null/decision.json) |

These are four original issue/fix cases plus a separate later condition, not five independent cases. The unchanged original totals are 66 physical launches and 96 logical policy cells; three repetitions check consistency, and shared policy rows do not enlarge the denominator. Configuration-only detects 1/4 and history/manual-reference 4/4 under the original settings. The negative control, later null, and T7 raw record-fidelity failure are integral evidence.

## What this package establishes

Reviewers can inspect the selected construction/oracle definitions, exact engine revisions, bounded historical environment metadata, original compact row/decision summaries, later null and technical-invalid records, and three receipt examples. Local validation checks byte integrity, source-copy identity, scientific denominators, row/decision/summary agreement, and the limited raw-versus-normalized projection comparison.

Scientific manuscript baseline: `03e715348b5dbe3a0f3656c5bfb95d0f7735cf51`. Source export: `UpbeatH/DataAnalyticsTune@5a3971445307f117285128e5d075ce2ecc7a95eb`. The historical experiment and result files remain unchanged; exported copies and reviewer notes are separately identified in [provenance.json](artifacts/manifests/provenance.json). The source repository is not required for offline inspection; source links may require separate access.

## Limits and exclusions

This artifact is **not a complete native reproduction environment** or raw-evidence backup. Native checkpoints, full logs, source/toolchain archives, credentials, private infrastructure identities, and external evidence storage are not distributed. Their present retrieval or independent backup has not been verified. Native execution still requires the exact revision, fixture, toolchain, validity rules, and oracle.

A compact receipt is an evidence projection, **not a reconstruction framework**. Raw or normalized record equality is distinct from functional reproduction. T7's raw mismatch remains a failure of its raw-fidelity endpoint despite exact-version normalized equality. The later restore null does not erase the earlier positive or establish a phase-cut benefit. No new experiment, performance result, or broader scientific claim is introduced here.
