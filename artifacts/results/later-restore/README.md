# Later FLINK-28843 nulls, kept separate from the original positive

These are later executions of the same issue/fix pair under an amended development harness. They are not a fifth independent incident, do not replace the original T3 positive, and are never pooled into the original 66 launches or 96 logical policy cells.

- `stabilized-null/`: 18/18 valid cells; every parent and child target passes under full-history-native, latest-native-anchor, and early-native-anchor. Retained decision: `L2_INCIDENT_NULL`.
- `replication-technical-invalid/`: a complete 18-cell attempt with a transient first child/full-history Surefire fork-start failure and no test report. Retained decision: `L2_TECHNICAL_INVALID`. It is not a valid null, and its rows are never substituted into the replication.
- `replicated-null/`: a separate receipt-complete replication on another host, 18/18 valid cells, all targets pass; retained decision: `L2_INCIDENT_NULL`.

The prior L2 v1 attempt was also technical-invalid, with a checkpoint-expiry signature, and is not combined with v2. V2 applied the recorded upstream stabilization (`a72a5ca8a393fee58c6a5e06584f9197ccb09ef0`): controlled progress and periodic checkpoint completion; producer materialization interval `-1`; target interval `1000` ms. The cause of the changed outcome relative to the original T3 positive remains unresolved.

The archived v2 rows fail the later R3 admission schema because topology and requested-versus-effective setting receipts are absent: 0/18 admitted, 18/18 rejected under that different rule. That post-hoc coverage analysis does not invalidate the original L2 decision under its frozen rule. The later receipt-complete replication records those fields but remains null.

Costs in the unchanged decision/row files are historical development-harness Maven command measurements, not throughput, latency, performance benefits, or a policy winner. The null reference cannot establish a useful fidelity/cost tradeoff or phase-cut efficacy. No new execution or timing was performed to make this package.

The public directory names describe evidence roles rather than private host identities. Exact repository source paths and hashes remain in `../../manifests/provenance.json`; those are source references, not addresses of accessible execution products. Native checkpoints, raw logs, host identities, and external storage addresses are excluded.
