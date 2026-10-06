# FLINK-25429 configuration-sufficient control

The prospective screen requires a filesystem stream whose second close is observable, one successful changelog upload, a valid upload result, and exactly one close of the underlying stream. The fresh construction closes a stream without the real uploader context. Configuration-only, lifecycle-history, and manual-reference select the same real uploader construction; the latter three reuse the same six matched physical rows.

The parent is `11f74d875a8fa0f4a7e4987026c10a3748820ab1`; the child is `804eb8dda556a2bea35c69a2662f13d1dafb9255`. The prescribed parent error is `IOException: underlying stream closed more than once`; the child emits `DAT_T3_FLINK_25429_PASS close_count=1`.

Across three repetitions, fresh passes on both revisions and does not detect the disagreement. The uploader fails on the parent and passes on the child. The matrix contains 12 physical launches and 24 logical policy cells. This valid configuration-sufficient control is negative evidence for incremental history advantage and stays in the four-case denominator. The initial PowerShell launcher stop produced no scientific cell.

Inspect the unchanged selection protocol, result note, row CSV, and decision JSON. No launcher or reproduction harness is distributed here.
