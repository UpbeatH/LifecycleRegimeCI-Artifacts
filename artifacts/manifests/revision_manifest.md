# Revision, environment, and provenance guide

- `revisions.json` binds all four issue/fix pairs and the later restore stability amendment to exact engine commits.
- `environments.json` separates original matrix environments, later child capture environments, later null/replication environments, and the offline inspection environment. The uploader matrix was a Windows workflow; the other original full matrices were Linux. Do not describe the study as a uniform one-host benchmark. Null toolchain entries mean an exact version is not established by this bounded export, not an inferred default.
- `provenance.json` gives exact source repository, commit, repository-relative path, Git blob identity, SHA-256, transformation, and local destination for each evidence-bearing artifact. Original source files are unchanged. Relative source paths containing historical host labels are provenance identifiers only; no host address or external evidence root is supplied.
- `integrity.json` seals all regular package files except itself. The validator checks exact membership, byte lengths, SHA-256, Git blob hashes for literal copies, protocol excerpt identity, schemas, and cross-file scientific consistency. A trusted Git checkout is the trust anchor; an editable checksum file is not a signature or independent proof of an experiment.

Scientific manuscript baseline: `03e715348b5dbe3a0f3656c5bfb95d0f7735cf51`.
Bounded source export: `UpbeatH/DataAnalyticsTune@5a3971445307f117285128e5d075ce2ecc7a95eb`.
Existing public package baseline: `UpbeatH/LifecycleRegimeCI-Artifacts@e669b323a956e92908f7cbae18876501f1389a15`.

Native checkpoints, raw execution logs, source/toolchain archives, host/user identities, credentials, and external storage are not distributed. Repository source links may require source-repository access; all advertised compact inspection and validation works without that access. Hashes bind the selected source bytes; they do not assert that omitted native evidence was retrieved, rehashed, backed up, or independently reproduced.
