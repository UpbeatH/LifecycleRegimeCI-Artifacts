# FLINK-25524 T3 full-matrix preregistration

Date: 2026-09-10

Status: frozen before any full-matrix outcome was opened.

## Question and fixed contrasts

Test whether the unchanged five-field selector's history-aware replay detects
the FLINK-25524 parent/child disagreement when controls that omit the
cross-lifecycle ID relation do not.

- `fresh-only`: construct the same changelog backend, do not install an
  explicit materialization, snapshot outer checkpoint 0, and notify completion.
- `configuration-only`: preserve changelog/checkpoint configuration and install
  materialization ID 0 before checkpoint 0. This preserves the effective
  surface while removing the incident-specific 200-to-0 lineage mismatch.
- `history-aware`: install materialization ID 200, snapshot outer checkpoint 0,
  and notify completion, exactly as in admission.
- `incident-oracle`: identical to `history-aware`; score the same physical rows.

The parent and child revisions, harness action, receipt fields, IDs, and target
oracle are unchanged. Each executed context/revision has three launches. The
18 physical cells represent 24 logical policy cells because history-aware and
oracle share six rows.

## Order, endpoint, and decision

Seed 25524 fixes three randomized complete blocks:

1. child-history, child-configuration, parent-fresh, child-fresh, parent-history, parent-configuration;
2. child-fresh, parent-configuration, child-history, parent-history, parent-fresh, child-configuration;
3. child-history, parent-history, parent-fresh, child-fresh, parent-configuration, child-configuration.

Primary endpoint is incident-level parent/child detection per policy. A cell is
valid only when Maven exits zero, exactly one target test passes, and the
observed nested checkpoint ID is 0 or 200. All three rows per role/context must
agree. Expected child values are 0 for fresh/configuration and 200 for history.

- `T3_FLINK_25524_HISTORY_ADVANTAGE`: history/oracle detect, both controls do
  not, child expectations pass, and all 18 cells are valid and consistent.
- `T3_FLINK_25524_VALID_CONTROL_DETECTS`: either control also detects; retain
  as negative evidence for incremental history advantage.
- `T3_FLINK_25524_VALID_NULL`: history-aware does not detect.
- `T3_FLINK_25524_TECHNICAL_INVALID`: any missing, failed, or inconsistent cell.

No threshold, context, repetition, exclusion, or source revision may change
after execution begins. Stop after one matrix invocation.
