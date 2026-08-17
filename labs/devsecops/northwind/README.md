# Northwind DevSecOps Companion Lab

This is the cumulative companion lab for *Practical DevSecOps Engineering*. It is independent of the frozen DevOps lab and consumes only reduced, checksum-identified interface fixtures under `inherited/devops-v1.1/`.

The working tree currently implements Chapters 1–16. Snapshot tags `v1.0-chapter-NN-start`, `v1.0-chapter-NN-complete`, and the reader-facing aliases `chapter-NN-start` / `chapter-NN-complete` are published in this lab repository. They are curated exercise snapshots, not merge milestones. Begin guided work from a start tag, or compare start with complete. Do not infer the teaching contract from Git ancestry.

The committed operational registers are the **Chapter 14 start state**: original identity subjects are active, `payment-v2` is active, the incident digest `sha256:9f4e…` is deployed, runtime policy is `runtime-v1` with credential discovery detected rather than prevented, and incident `INC-2026-0815-01` is `investigating`. Attack, containment, and recovery reports are generated from a complete snapshot. After Chapter 14–15 mutations, restore that incident-ready start with:

```bash
make lab-reset
```

## Environment

Use Python 3.13:

```bash
python3 -m venv .venv
source .venv/bin/activate
make bootstrap
make test
make lint
make audit
```

`make` prefers `.venv/bin/python` when that interpreter exists.

## Commands

Chapter targets follow the pattern in Chapter 0. Not every chapter uses every command. `make chapter-NN-recover` is chapter-scoped. Only `make chapter-15-verify-recovery` produces the bounded restored-trust claim.

Some commands mutate operational files. Those mutations persist. Files later chapters may change include:

- `identity/subjects.yaml`
- `runtime/contracts/order-worker.yaml`
- `runtime/policies/behavior.yaml`
- `supply-chain/deployment-evidence.yaml`
- `response/case/incident.yaml`
- `policy/enforcement-points.yaml`
- `secrets/inventory.yaml`

`make lab-reset` restores those files, plus provenance, secret references, provider state, and payment reconciliation, to the Chapter 14 start state.

### Chapters 12–16 chain

When generated evidence or live incident state is missing, run:

```text
make chapter-12-attack
make chapter-13-attack
make chapter-14-open
make chapter-14-baseline
make chapter-14-checkpoint
make chapter-14-contain
make chapter-14-recover
make chapter-15-baseline
# … Chapter 15 guided work …
make chapter-15-verify-recovery
make chapter-16-baseline
```

`chapter-14-open` writes incident `INC-2026-0815-01` as `investigating` and sets `compromised-session` to `active`. After Chapter 15 those live files are recovered; `make lab-reset` restores the start state above.

A Make `matrix` target is not part of this freeze. Verify a snapshot from a clean checkout of that tag.

## Schemas

Governed artifacts under this tree are validated by `make audit` against JSON Schema files in `schemas/`. The frozen planning inventory named shared envelopes such as `artifact-envelope.schema.json` and `owner.schema.json`. Implementation uses chapter-specific schemas instead: every governed artifact still carries `schema_version` and `kind`, ownership lives in `ownership.schema.json`, and `policy/bundle/rules.yaml` is validated by `policy-bundle.schema.json`.

Planning leftovers that were not created as named paths:

- policy tests live under `tests/`, not `policy/tests/`
- inherited observability is `inherited/devops-v1.1/observability/interface.yaml`, not `observability/contract.json`
- Chapter 2 has no generated threat-model review report; the reviewed register is `threat-model/`
- attack and observation fixtures live under each chapter's `checkpoints/chapter-NN/cases/`
- there is no Make `matrix` target; verify tags from a clean checkout

## Evidence limits

The lab validates deterministic local models. It does not prove that a real repository, identity provider, registry, cloud account, Kubernetes cluster, telemetry backend, or external dependency enforces the modeled behavior.

No fixture contains a real credential, personal data, active malware, or external attack target.
