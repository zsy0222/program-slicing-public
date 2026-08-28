# Seeded-fault smoke-test suite

These eleven tiny C programs are deliberately seeded fault pairs. They have a
known correct reference and a single mutated statement, so they provide ground
truth for validating the experiment pipeline and the pure-tool ranking before
using real-world faults.

They are **not** part of the final effectiveness benchmark and must be reported
separately from SV-COMP and real-bug results. The faulty inputs contain no
ground-truth comments, preventing source-only LLM baselines from receiving an
oracle hint.

`Seed02_guard_boundary.c` and `Seed03_initial_value.c` are retained only as an
auditable preliminary attempt. They are not listed in the manifest because the
two files happened to have identical faulty code with different intended
references, which would create ambiguous ground truth. The `_v2` pairs replace
them with distinct faulty programs.

`Seed04`–`Seed11` are the 2026-08-23 extension. Each adds exactly one
source-level fault to a paired reference, covering update magnitude, loop
boundary, initialization, guard predicate, update direction, special-iteration
guard, and counter increment. A case is eligible for the V2 comparison only if
all of the following hold: the faulty program fails at runtime, the reference
passes, the Error-Invariant analyzer completes, and the emitted trajectory can
be parsed. Cases failing a tool-stage condition are retained in run-status
records and excluded rather than silently replaced.
