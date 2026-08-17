# References

The chapter text cites sources at the decision they support. This consolidated list is organized for review and maintenance. Product behavior and documentation change; verify version-specific details before applying an example to production.

This book’s production decisions are Northwind’s. Chapters that make no product or standards claim beyond inherited contracts have no external vendor or framework entries.

## Series books

- *Practical DevOps Engineering* v1.0 — one team’s production delivery path: fast feedback, verifiable artifacts, reconciled infrastructure, bounded runtime, workload identity, observable outcomes, progressive delivery, compatible data change, safe asynchronous processing, **GitOps (Git-based operations)**, cost of one workload, incident coordination, and reconstruction from durable evidence.
- *Practical DevSecOps Engineering* v1.0 — security of that same path: assets and harms, threat and risk, attributable identity, privileged delegation, supply-chain trust, vulnerability treatment, secrets, data protection, policy, runtime confinement, detection, investigation, eradication, bounded restored trust, and operational governance.
- *Practical Platform Engineering* v1.0 — owned internal platform product: users, jobs, tenancy, catalog, paved road, environments, contracts, control plane, guardrails, developer-experience measurement, quota, fleet, support, and bounded plane restore. Remaining owner `reliability-program` holds portfolio **SLO (Service Level Objective)** governance. Chapter 14 recorded `not-regional-loss` and `not-portfolio-rto`.

## Inherited contracts this book consumes

The SRE lab does not read earlier labs’ working trees at runtime. It carries reduced, checksum-identified interface fixtures under `inherited/devops-v1.1/`, `inherited/devsecops-v1.0/`, and `inherited/platform-v1.0/`.

- DevOps provisional Storefront **SLIs (Service Level Indicators)** and burn policy — candidate input to Chapters 2 and 5, not a chapter to rewrite.
- DevOps one-change incident evidence — role interface for Chapter 10; insufficient to close a portfolio incident.
- DevOps one-environment reconstruction — insufficient for Chapters 12–14.
- DevSecOps `self_approval_forbidden` — named authorization field consumed by Chapter 6 on-call authority.
- DevSecOps independent-producer requirement — consumed by Chapter 11 learning verification.
- Platform job proofs `time-to-first-environment`, `paved-road-completion`, and `catalog-freshness` — a **job-time budget**, never a portfolio SLO.
- Platform catalog escalations `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall` — contacts, not an on-call system.
- Platform fleet step `storage-1-0-to-2-0` — referenced by Chapter 4 error-budget freeze; upgrade freeze window, cohort, and rollback are not copied.
- Platform plane last known good `1.0` and contract last known good `tenant-storage-1.0` — distinct insufficient identities for regional loss.
- Platform limitations `not-regional-loss` and `not-portfolio-rto` — the gap Chapters 12–14 close.

## Chapter 14 — Regional fail-over

No public-cloud multi-region reference or enterprise disaster-recovery program is cited. Modeled **Evidence of portfolio recovery** is computed from inventoried regional evidence, tenant isolation, numeric **RTO (Recovery Time Objective)** and **RPO (Recovery Point Objective)**, and independent journey observations. It does not prove a live multi-region estate.
