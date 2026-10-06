# FLINK-25429 held-out result

Date: 2026-09-09

Decision: `T3_FLINK_25429_VALID_CONFIG_BASELINE_DETECTS`.

## Observation

The one-pair admission separated the exact revisions: parent
`11f74d875a8fa0f4a7e4987026c10a3748820ab1` failed with
`IOException: underlying stream closed more than once`, while child
`804eb8dda556a2bea35c69a2662f13d1dafb9255` passed and emitted
`DAT_T3_FLINK_25429_PASS close_count=1`.

The full matrix completed 12 physical JVM launches, representing 24 logical
policy cells. Across three repetitions:

- fresh-only passed on both parent and child;
- the real uploader context failed on the parent 3/3 times and passed on the
  child 3/3 times;
- configuration-only, history-aware, and incident-oracle selected the same
  uploader context, so they intentionally reuse the same six matched rows;
- incident-level detection was 0/1 fresh-only and 1/1 for each of
  configuration-only, history-aware, and incident-oracle;
- observed child false positives were 0/1.

The first PowerShell invocation stopped before compilation because a dotted
Maven `-D` property was not quoted. It produced no scientific cell and is not
included in the matrix.

## Inference and decision

FLINK-25429 is a technically valid new holdout and remains in the T3
denominator. It is negative evidence for incremental history-aware advantage:
configuration-only already exposes the same non-idempotent close behavior.
Repeating identical contexts would add JVM launches but no information, so the
three selectors share the same physical rows.

T3 progress is 1/4 valid new incidents. No cross-holdout generalization claim
is supported. The next gate is only the FLINK-25524 matched parent/child
admission pair.
