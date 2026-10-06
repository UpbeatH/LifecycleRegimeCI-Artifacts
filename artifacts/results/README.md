# Compact evidence and denominator guide

The three original public CSV summaries are unchanged. In `reproduction_matrix.csv`, `OK` means the fixed construction exposes the prescribed parent/child disagreement; `X` means no disagreement was exposed in that valid original construction. It does not mean a process failed. Manual-reference is the paper's name for the original `incident-oracle` policy; lifecycle-history maps to `history-aware`, fresh maps to `fresh-only`, and configuration_only maps to `configuration-only`.

`t3-policy-detection.csv` and `t3-summary.json` are unchanged frozen source summaries. `original/` contains the exact eight row/decision sources cited by that summary. Four cases, 66 physical launches, 96 logical policy cells: fresh 0/4, configuration 1/4, history/manual-reference 4/4, selected-history child false positives 0/4. These are purposively fixed cases, not a probability sample or prevalence estimate. The uploader's configuration-sufficient negative stays in the denominator.

`live-capture-summary.csv` and `live-capture-aggregate.json` retain their original bytes, including historical T6 and references to omitted evidence. The selected endpoint is T7/T9/T10: raw 2/3, normalized 3/3. The public `fidelity_summary.csv` reports that selection. T7's raw failure remains a No-Go. `capture/` retains complete selected result values with only the private host-label field removed. The raw-to-normalized distinction does not imply functional reproduction. Historical component timings remain descriptive and are not new performance claims.

`later-restore/` contains separately named stabilized null, technical-invalid replication attempt, and receipt-complete replicated null. Each valid null matrix has 18 valid cells with all targets passing. The original positive is retained. Do not pool conditions, infer a policy winner, or infer why the oracle disappeared.

The copied source summaries can name historical files not included here. Their presence is provenance, not a claim that all native evidence is public. This package's complete local membership is listed in `../manifests/integrity.json`.
