# Experiments

This directory contains the release-ready experiment layer.

- `prototypes/`: self-authored prototype code, prompt builders, validators, and test utilities.
- `benchmarks/`: self-authored seeded faults and license-reviewed benchmark manifests.
- `results/`: small, structured evidence trajectories suitable for review.
- `reports/`: experiment design documents, summary reports, and reproducibility notes.
- `outputs/`: temporary local run output only; it is excluded from Git.

Raw LLM requests/responses, traces, instrumented binaries, complete logs, transient builds, and QA render folders are retained under `90_local_only/experiment_runs/`.
