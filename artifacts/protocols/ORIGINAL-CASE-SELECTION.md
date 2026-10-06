# T3 prospective held-out incident screen

Date: 2026-09-09

Decision: `T3_SOURCE_GO_SIX_ORDERED_CANDIDATES`.

## Source frame and exclusion

The official Apache Flink `master` head was read as
`7ebd1522f77d24f78209085bea539d91d2c6a3c6` on 2026-09-09. The screen reuses
the T0 mechanical source extraction but starts a new candidate frame, excludes
FLINK-12064, FLINK-12785, FLINK-17988, and FLINK-24667, and opens only entries
previously marked `NOT_REVIEWED_AFTER_ROLE_FILL`. Each retained candidate is a
single child commit with one first parent and an official issue/commit record.

Public bug outcomes are known because they establish an affected incident.
No local parent/child result for the six candidates has been executed or used
to choose the order, receipt, threshold, or selector rule.

## Fixed order

The first four candidates minimize time to valid real-Flink evidence while
covering three lifecycle families. The last two are replacements only if a
primary candidate is technically invalid. Their exact identities and source
links are in `CANDIDATES.csv`.

1. FLINK-25429: wrapped changelog-upload stream ownership and double close;
2. FLINK-25524: checkpoint-to-materialization notification lineage;
3. FLINK-28843: incremental checkpoint path lineage across claim-mode restore;
4. FLINK-38483: mixed-exchange unaligned-checkpoint rescale with a no-state
   descriptor;
5. FLINK-35379: file-merging checkpoint notification lifecycle;
6. FLINK-21986: RocksDB native-memory release after job restart.

FLINK-25429 is intentionally retained even though configuration-only execution
may reproduce it: a valid null/negative holdout is informative and must not be
silently replaced. FLINK-21986 is last because its production-scale report is
valuable but a clean cgroup memory construction is more expensive.

## Fast execution rule

For each candidate in order, first run one matched parent/child history-aware
pair with the exact source-grounded oracle. A technical invalidity permits the
next candidate; a valid null or reversed result is retained as evidence and
does not permit substitution. Stop admission once four scientifically valid
new incidents exist, whether positive or null.

For the four retained incidents, complete three randomized repetitions per
revision/context and add fresh-only and configuration-only controls. The
already fixed T2B selector receives only its five fields. Construct each
receipt before opening parent/child outcomes. If the selector and the manual
oracle choose an identical replay context before execution, score the same
matched rows for both policies instead of launching a scientifically duplicate
run. Keep equal timeout and launch caps for every policy.

The primary endpoint is incident-level detection, with child false positives,
invalid/time-out accounting, and paired run consistency. Repetitions are not
independent incidents. Do not tune the selector, exclusions, or candidate
order after any result is opened.

## Immediate gate

Implement and run only FLINK-25429's one-pair admission harness. It must use a
filesystem stream whose second close is observable, perform one successful
changelog upload, and pass only when the upload result is valid and the
underlying stream is closed exactly once. Fresh/configuration controls and
repetitions 2--3 wait until the admission result is known.
