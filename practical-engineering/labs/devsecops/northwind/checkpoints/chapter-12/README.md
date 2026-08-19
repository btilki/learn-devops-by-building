# Chapter 12 checkpoint

The baseline proves that a detection-only runtime policy allows shell execution to proceed.

The completed checkpoint verifies legitimate identity, privilege, filesystem, and egress behavior for `order-worker`.

Attack writes `runtime/events.jsonl`. Containment writes `build/chapter-12-contained-subjects.yaml` and does not mutate the operational identity register.

It cannot prove that a real runtime sandbox or sensor blocks the same behavior.
