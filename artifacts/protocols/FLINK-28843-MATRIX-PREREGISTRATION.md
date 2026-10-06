# FLINK-28843 T3 full-matrix preregistration

Date: 2026-09-10

Status: frozen before any full-matrix outcome was opened.

## Fixed contexts

- `fresh-only`: start a changelog-enabled job with the same backend and 20-byte
  small-file threshold, checkpoint once, and do not restore prior state.
- `configuration-only`: create a native-backend checkpoint, claim-restore once
  while enabling changelog, and checkpoint. This preserves the effective
  configuration and backend switch but omits the second-generation checkpoint
  lineage and second restore that trigger FLINK-28843.
- `history-aware`: execute the upstream native checkpoint, first claim restore
  with changelog, second checkpoint, and second claim restore unchanged.
- `incident-oracle`: identical to history-aware and shares its physical rows.

Each executed context/revision has three launches. The 18 physical cells are
24 logical policy cells. Each target launch contains the upstream three
delegated-backend parameterizations.

## Frozen order and decision

Seed 28843 fixes the following blocks:

1. parent-history, child-fresh, parent-fresh, child-configuration, parent-configuration, child-history;
2. parent-fresh, parent-history, child-configuration, child-fresh, parent-configuration, child-history;
3. parent-history, parent-configuration, child-fresh, parent-fresh, child-history, child-configuration.

A valid control cell exits zero with three passing tests. A valid history
parent cell runs three tests and contains the target `FileNotFoundException`;
a valid history child cell exits zero with three passing tests. All three
blocks per role/context must agree.

- `T3_FLINK_28843_HISTORY_ADVANTAGE`: history/oracle detect while fresh and
  configuration do not, all child cells pass, and all 18 cells are valid.
- `T3_FLINK_28843_VALID_CONTROL_DETECTS`: a control also detects; retain as
  negative evidence for incremental history advantage.
- `T3_FLINK_28843_VALID_NULL`: history does not detect.
- `T3_FLINK_28843_TECHNICAL_INVALID`: any missing or inconsistent cell.

No source revision, context, order, repetition, timeout, or oracle may change
after execution starts. Stop after one invocation.
