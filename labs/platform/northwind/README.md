# Northwind Platform Companion Lab

This is the cumulative companion lab for *Practical Platform Engineering*. It is independent of the DevOps and DevSecOps labs and consumes only reduced, checksum-identified interface fixtures under `inherited/devops-v1.1/` and `inherited/devsecops-v1.0/`.

The working tree currently implements Chapters 1–14. Snapshot tags `v1.0-chapter-NN-start`, `v1.0-chapter-NN-complete`, and the reader-facing aliases `chapter-NN-start` / `chapter-NN-complete` are published in this lab repository. They are curated exercise snapshots, not merge milestones. Begin guided work from a start tag, or compare start with complete. Do not infer the teaching contract from Git ancestry.

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

```text
make chapter-01-baseline
make chapter-01-checkpoint
make chapter-02-baseline
make chapter-02-checkpoint
make chapter-03-baseline
make chapter-03-checkpoint
make chapter-04-baseline
make chapter-04-checkpoint
make chapter-04-failure
make chapter-05-baseline
make chapter-05-checkpoint
make chapter-05-failure
make chapter-06-baseline
make chapter-06-checkpoint
make chapter-06-failure
make chapter-07-baseline
make chapter-07-checkpoint
make chapter-07-failure
make chapter-08-baseline
make chapter-08-checkpoint
make chapter-08-failure
make chapter-09-baseline
make chapter-09-checkpoint
make chapter-09-failure
make chapter-10-baseline
make chapter-10-checkpoint
make chapter-10-failure
make chapter-11-baseline
make chapter-11-checkpoint
make chapter-11-failure
make chapter-12-baseline
make chapter-12-checkpoint
make chapter-12-failure
make chapter-13-baseline
make chapter-13-checkpoint
make chapter-13-failure
make chapter-14-baseline
make chapter-14-checkpoint
make chapter-14-failure
```

A successful baseline means the evaluator correctly found the expected unsafe product definition or intake decision. It does not mean the platform product is already healthy.

## Schemas

The frozen planning inventory named a shared `artifact-envelope.schema.json`. Implementation uses kind-specific schemas instead, the same refinement as DevSecOps: every governed artifact carries `schema_version`, `kind`, and `id`. The full decision envelope (`owner`, `status`, `effective_at`, `review`) is for later decision records, not Chapter 1 list registers. Chapter 2 intake decisions record owner and review trigger on each row without promoting the register into that later envelope. Chapter 3 tenancy records owner, isolation dimensions, prohibited inheritance, and blast radius on each tenant without that later envelope. Chapter 4 catalog ownership records living owners, escalation, and `last_reviewed_at`; freshness is computed by the evaluator and is not a self-emitted green status. Chapter 5 paved-road conformance is computed from path, defaults, and registered exits; unofficial forks cannot emit their own passing grade. Chapter 6 environment leases bind Chapter 3 environment ids, consume inherited federated identity, and treat isolation as a computed invariant joined from Chapter 3 `denied_inheritance`; a lease cannot emit its own passing isolation status. Chapter 7 infrastructure contracts bind those same environment ids to versioned capabilities; hidden module internals are not tenant API, and compatibility is computed. The Chapter 7 evaluator reuses that same live join so a tenant-network binding cannot reintroduce `peer-tenant-workload-network`. A contract cannot emit its own passing grade. Chapter 8 operates `kubernetes-control-plane` as a product with a tenant-scoped subject, admission of Chapter 7 versions, inherited GitOps state, and last known good; the evaluator joins Chapter 3 sharing so `cluster-admin` on the reconciler fails. A plane cannot emit its own passing health. Chapter 9 binds Chapter 5 remaining guardrails as owned defaults; exception rows reference inherited DevSecOps IDs and must not copy owner, scope, compensation, or expiry. A scorecard cannot emit green. Expiry is resolved from the inherited exception record. Chapter 10 retains Chapter 1 later proofs as platform-product SLIs with samples; vanity and inherited tenant-outcome metrics are required non-metrics with distinct exclusion categories. A measurement file cannot emit its own passing grade. Completeness is computed. The lab does not survey real developers. Chapter 11 allocates floors and ceilings on the same `cluster-capacity-pool` Chapter 3 shared and Chapter 6 bound; showback uses quality-gated platform units. A cheaper shared bill cannot replace job time, and a burst that leaves a peer below its floor fails. The lab does not read a real cloud bill. Chapter 12 onboards tenants without cluster-admin, upgrades a contract version with freeze, cohort, and rollback, and keeps 1.0 legal until migration evidence exists. An all-at-once v2 apply that breaks still-legal v1 fails. The lab does not upgrade a live fleet. Chapter 13 maps every catalog system to a product or application owner and escalation contact; unofficial plane-admin edits fail; the platform-product job-time budget is Chapter 10 job time, not Storefront order-success. The lab does not operate a real ticketing system. Chapter 14 restores `kubernetes-control-plane` from independently verified last known good and keeps tenant continue or freeze explicit; a mixed newest backup that replays Fulfillment into Storefront fails. The frozen planning inventory named `plane-recovery.schema.json`. Implementation uses four kind-specific schemas. Completeness is computed. A verification file cannot emit `status: recovered`. The lab cannot prove regional loss or a portfolio recovery-time objective; those remain SRE.

## Evidence limits

The lab validates deterministic local models. It does not prove that a real developer portal, identity provider, cluster fleet, cost system, ticketing system, or disaster-recovery program behaves as the fixture does.
