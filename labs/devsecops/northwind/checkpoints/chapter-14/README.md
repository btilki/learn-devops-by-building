# Chapter 14 checkpoint

The baseline proves that a correlated alert exists while attacker authority and incident scope remain open.

The completed checkpoint verifies evidence custody, an ordered timeline, and a staged containment plan. `make chapter-14-open` writes incident `INC-2026-0815-01` as `investigating` and sets `compromised-session` to `active` before the baseline.

Containment is the first operational revocation of `compromised-session` in `identity/subjects.yaml`. Recovery records `trust_restored: false`.

It is not a forensic acquisition or legal chain-of-custody system.
