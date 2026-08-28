# Benchmark policy

This directory separates self-authored and externally sourced cases.

- `seeded_faults/` contains self-authored, paired faulty/correct C programs used for controlled ground-truth checks. These are the default release-ready cases.
- `pilot/` contains normalized pilot inputs and manifests derived from the SV-COMP selection used during early experiments. Preserve the source attribution in each manifest.
- The downloaded `sv-benchmarks` clone is retained locally in `90_local_only/external_benchmarks/`. It is not committed as an embedded Git repository. Its Apache-2.0 source notices and upstream attribution must be preserved if a reviewed subset is later added.

Do not add benchmark archives of uncertain origin. Downloaded benchmark packages, binaries, and unreviewed samples belong in `90_local_only/` until their redistribution status has been checked.
