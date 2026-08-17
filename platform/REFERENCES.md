# References

The chapter text cites sources at the decision they support. This consolidated list is organized by chapter for review and maintenance. Product behavior and documentation change; verify version-specific details before applying an example to production.

This book’s production decisions are Northwind’s. Chapters that make no product or standards claim—product definition, intake, tenancy, catalog, paved road, environments, contracts, control plane, guardrails, measurement, quota, fleet, support, restore, and the conclusion—have no external vendor or framework entries. They inherit delivery and security contracts from the earlier books rather than citing a portal-product manual, operator textbook, or landing-zone guide.

## Series books

- *Practical DevOps Engineering* v1.0 — one team’s production delivery path: fast feedback, verifiable artifacts, reconciled infrastructure, bounded runtime, workload identity, observable outcomes, progressive delivery, compatible data change, safe asynchronous processing, **GitOps (Git-based operations)**, cost of one workload, incident coordination, and reconstruction from durable evidence.
- *Practical DevSecOps Engineering* v1.0 — security of that same path: assets and harms, threat and risk, attributable identity, privileged delegation, supply-chain trust, vulnerability treatment, secrets, data protection, policy, runtime confinement, detection, investigation, eradication, bounded restored trust, and operational governance.
- *Practical SRE Engineering* — planned fourth book. Portfolio **SLO (Service Level Objective)** programs, error-budget governance, on-call systems, regional-loss architecture, recurring game days, and reliability learning across a service portfolio.

## Inherited contracts this book consumes

The Platform lab does not read the DevOps or DevSecOps working trees at runtime. It carries reduced, checksum-identified interface fixtures. Reader-facing chapters join those contracts by identifier, not by restating the earlier implementations.

- DevOps release expectations — artifact identity and promotion used by paved-road defaults and infrastructure contracts.
- DevOps workload identity — subject, issuer, audience, and expiry used by environment leases and the control plane.
- DevOps observability contract — `order_success_ratio` and `order_latency` retained as tenant-workload non-metrics.
- DevOps GitOps reconciliation — reviewed intent and `controller_may_rewrite_source: false` used by the plane and fleet.
- DevOps incident-recovery expectations — tenant-path recovery evidence that must not close a platform incident.
- DevOps restore contract — reconstruction roots and traffic-return gates used by isolated plane restore.
- DevSecOps authorization, exception, control, and evidence-map shapes — self-approval forbidden, exception IDs referenced rather than copied, independent producer required.

## Chapter 7 — Infrastructure contracts

No external module catalog is cited. Tenant-visible parameters and hidden internals are Northwind’s contract design. Terraform, Helm, and provider documentation remain the earlier books’ concern where a single team applied infrastructure.

## Chapter 8 — Shared control plane

No Kubernetes control-plane operations guide is cited as a product claim. `kubernetes-control-plane` is Northwind’s shared product identifier. Last known good after a failed upgrade is a platform retention rule, not a quoted kube-apiserver runbook.

## Chapter 14 — Isolated restore

No enterprise disaster-recovery or multi-region program is cited. The inherited DevOps restore contract supplies reconstruction identity. Regional-loss architecture and portfolio **RTO (Recovery Time Objective)** remain **SRE (Site Reliability Engineering)**.
