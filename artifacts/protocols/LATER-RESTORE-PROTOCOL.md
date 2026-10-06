# Later FLINK-28843 protocol: bounded source excerpt

This is a documentary excerpt, not a runnable task. Original lines 1–193 are reproduced below; the operational interference/safety section is omitted. The original scientific claim boundary is stated in the reviewer result note. The original source remains unchanged.

---

# FLINK-28843 version-native anchor baseline technical amendment v2

Date: 2026-09-14
Status: frozen technical amendment; target-native execution not yet started
Evidence role: outcome-exposed technical adjudication of the unchanged L2 question

## Research question

For the unchanged FLINK-28843 parent/child oracle, is the latest checkpoint
produced natively by each evaluated revision sufficient, or must a replay
system select an earlier phase-consistent lifecycle cut?

This question is narrower than automatic schedule inference. The incident and
its full schedule are already known. The experiment can falsify the proposed
cut-selection mechanism on one development case; it cannot measure discovery,
prevalence, or generality.

## Why v2 exists and what may change

The complete v1 attempt is retained at
`../DAT-LRCI-L2-anchor-baselines/RESULT.md` as `L2_TECHNICAL_INVALID`. Its only
invalid cell reproduced the exact 617-second checkpoint-expiry signature of
Apache Flink test-stability issue FLINK-28529. The v1 harness used the same
pre-fix ingredients identified upstream: an infinite source, manual
`triggerCheckpoint()`, and a 100 ms target materialization interval.

V2 applies only the upstream technical stabilization from PR 20404 / commit
`a72a5ca8a393fee58c6a5e06584f9197ccb09ef0`:

- use the inherited `ControlledSource` and periodic checkpoint completion
  rather than an infinite source plus manual triggering/cancellation;
- use materialization interval `-1` for the two checkpoint-producing phases;
- use materialization interval `1000` ms for the target phase; and
- emit a backend start marker so any incomplete backend is observable.

The parent/child revisions, three policies, fresh-state ownership, three
blocks, fixed order, target oracle, receipts, cost fields, validity rules, and
frozen decisions do not change. No v1 row is imported or substituted. Because
the v1 outcomes are known, v2 is not represented as an independent blind
replication.

## Fixed identities

- Parent revision: `0e6e4198ad84227c20e2c61c2dd8b0616324aa31`.
- Child revision: `7f708d0ba42f727b3f8c3d77cef2108206cad2de`.
- The child must have the parent as its direct Git parent.
- Harness: `Flink28843AnchorBaselineITCase.java` in this directory.
- Runner: `run-flink-28843-anchor-baselines.sh` in this directory.
- Test target: the upstream three delegated state-backend parameterizations.
- Target oracle: exactly one of the parent's three delegated-backend tests
  exposes the same `FileNotFoundException` during the second restore, with no
  unrelated failure; all three child tests pass.
- Restore mode: `CLAIM`.
- Small-file threshold: `20b`.
- Maximum retained checkpoints: one.
- Upstream stability amendment: FLINK-28529 / PR 20404, with producer
  materialization interval `-1` and target interval `1000` ms.

## Fixed policies

1. `full-history-native`: each revision creates its native first checkpoint,
   performs the backend transition, creates its second checkpoint, and enters
   the target restore in one invocation.
2. `latest-native-anchor`: each revision first creates its own first and second
   checkpoints in a producer invocation; a separate consumer invocation
   restores that second checkpoint directly at the target.
3. `early-native-anchor`: each revision first creates its own first checkpoint;
   a separate consumer restores it, performs the transition and second
   checkpoint, and enters the target restore.

Every role, repetition, and policy receives a fresh task-owned state root. An
anchor is consumed once. Parent and child never share an artifact or path.
Common-origin state reuse and old-version upgrade state are excluded because
their compatibility and oracle contracts are not qualified.

## Source qualification and timing isolation

After the harness is copied into the two detached source trees and before any
matrix cell runs, the runner invokes the Maven `test` lifecycle once for the
parent and once for the child with `skipTests=true`. This compiles the injected
test class but must execute no test. Qualification requires Maven exit zero,
the expected test-class file, and no target Surefire XML or text report. A
failed qualification stops before the matrix and cannot yield a scientific
decision.

The fixed build order is parent then child. Its two monotonic-clock durations
are recorded in `source-build-costs.csv` and summed as one common adaptation
cost. Dependency-cache warming can affect the split between those two rows, so
neither row may be assigned to a policy or used to compare revisions. Every
paired policy receives the same parent-plus-child build sum when a cold total
is reported. Matrix command timing begins only after both source trees are
qualified, preventing the first policy for each revision from absorbing cold
compilation cost. This is build-only qualification, not an outcome-exposed
smoke run.

## Fixed order and repetitions

There are three blocks and eighteen logical cells. Each Maven invocation runs
the three upstream backend parameterizations. The fixed order, generated with
seed `2884302`, is:

1. child-latest, parent-early, child-full, parent-latest, parent-full,
   child-early;
2. child-early, parent-early, child-latest, child-full, parent-latest,
   parent-full;
3. parent-early, parent-latest, parent-full, child-early, child-full,
   child-latest.

Anchor policies execute their producer and consumer invocations consecutively
inside the logical cell. The order, repetitions, modes, target oracle, or
revisions may not change after execution begins.

## Validity

A version-native anchor preparation is valid only when:

- all three parameterized tests pass;
- exactly three backend-specific receipts exist;
- the backend identities are `hashmap`, `rocksdb-incremental`, and
  `rocksdb-full`;
- every checkpoint and `_metadata` file exists below its cell root; and
- a pre-consumption file/byte/hash inventory is retained;
- each anchor receipt binds its producer revision, producer mode, realized
  anchor phase, next phase, event prefix, restore mode, effective checkpoint
  settings including whether changelog state is enabled at the anchor,
  checkpoint path, and metadata path; and
- all three backend identities are present exactly once.

A target cell must contain exactly three backend-specific receipts binding the
consumer revision, consumer mode, second-restore attempt, event suffix,
effective checkpoint settings, restore mode, checkpoint path, and metadata
identity. A parent target cell is valid when either all three tests pass or
Maven exits exactly `1` while exactly one failure/error contains the target
`FileNotFoundException` and no other failure occurs; these are the
scientifically meaningful non-detection and detection outcomes. A timeout or
other nonstandard nonzero exit is invalid even if a partial report contains the
target exception. A child target cell is valid only when all three tests pass
without that exception. Any unrelated or mixed parent failure is invalid. All
three blocks must agree.

The event and phase fields are harness-grounded receipts: each prefix is
written only after its preceding native operations complete, and each target
receipt is written immediately before the second-restore attempt. They verify
this development harness's realized control path; they are not evidence that a
generic event-capture or obligation compiler has been implemented.

An invalid v2 cell is retained. It is not silently rerun or replaced. V2 has a
fresh task root and result identity; v1 remains immutable evidence.

## Metrics and cost boundary

Primary outcome: verdict preservation relative to `full-history-native`.

Secondary observations:

- parent and child source-qualification time, recorded separately as one
  shared setup cost;
- producer-command time;
- target-command time;
- their sum per logical cell;
- checkpoint/state file count and bytes before and after consumption;
- Maven exit code and Surefire test/failure/error counts; and
- exact target-`FileNotFoundException` and non-target failure counts;
- anchor and target-phase receipt counts and identities; and
- host load, I/O pressure, and available memory immediately before and after
  each command.

All command durations use `time.monotonic_ns()` and are reported in seconds by
the analyzer. Maven command time is a replay-cost observation, not application
performance. The report must show source qualification, anchor preparation,
and target execution separately. It must include anchor preparation in each
logical-cell total and add the identical parent-plus-child qualification sum to
each policy's paired cold total. It may additionally discuss session-level or
downstream-consumer amortization, but may not assign common build cost to the
first scheduled policy or omit anchor production from a one-comparison total.

## Frozen decisions

- `L2_TECHNICAL_INVALID`: any missing/inconsistent row, invalid source-build
  ledger, failed preparation, missing receipt, escaping checkpoint path, or
  invalid parent/child target.
- `L2_INCIDENT_NULL`: technically valid execution in which full history no
  longer reproduces the paired verdict.
- `L2_SIMPLE_LATEST_ANCHOR_SUFFICIENT`: full history and latest native anchor
  both preserve the paired verdict. This falsifies a nontrivial cut-selection
  claim on FLINK-28843 regardless of which has lower one-shot cost.
- `L2_EARLY_PHASE_CUT_WITNESS`: full history and early native anchor preserve
  the paired verdict, while latest native anchor does not. This admits planner
  implementation on the development case, but not generality claims.
- `L2_FULL_HISTORY_ONLY`: full history preserves the verdict while neither
  native anchor policy does. Retain as evidence that replay matters; do not
  claim successful cut selection.

