# FLINK-38483 T3 full-matrix preregistration

Date: 2026-09-10

Status: frozen after the history-aware admission pair and before any fresh-only
or configuration-only outcome was opened.

## Fixed contexts

- `fresh-only`: start the same mixed-exchange graph at deterministic target
  topology seed 38484 with the target unaligned-checkpoint configuration but
  without creating or restoring a checkpoint.
- `configuration-only`: create one externalized unaligned checkpoint at seed
  38483, then restore it under the same seed and effective configuration. This
  reaches the restore phase but omits the rescale transition.
- `history-aware`: create the externalized unaligned checkpoint at seed 38483
  and restore at target seed 38484, retaining the upstream rescale transition.
- `incident-oracle`: identical to history-aware and shares its physical rows.

Each context/revision has three launches. Every launch retains all five
upstream parameterizations. The 18 physical cells represent 24 logical policy
cells.

## Frozen order and decision

Seed 38483 fixes:

1. parent-history, child-fresh, parent-fresh, child-configuration,
   parent-configuration, child-history;
2. child-configuration, parent-fresh, parent-history, child-history,
   parent-configuration, child-fresh;
3. child-fresh, parent-configuration, child-history, parent-fresh,
   child-configuration, parent-history.

A valid control or history-child cell exits zero with all five tests passing.
A valid history-parent cell runs all five tests and contains the target
`Cannot get old subtasks from a descriptor that represents no state.`
exception. All three blocks per role/context must agree.

- `T3_FLINK_38483_HISTORY_ADVANTAGE`: history/oracle detect while fresh and
  configuration do not, all child cells pass, and all 18 cells are valid.
- `T3_FLINK_38483_VALID_CONTROL_DETECTS`: a control also detects; retain as
  negative evidence for incremental history advantage.
- `T3_FLINK_38483_VALID_NULL`: history does not detect.
- `T3_FLINK_38483_TECHNICAL_INVALID`: any missing or inconsistent cell.

Topology seeds 38483 and 38484 are fixed before execution. No source,
toolchain, context, order, repetition, timeout, or oracle may change after
execution starts. Stop after one invocation.
