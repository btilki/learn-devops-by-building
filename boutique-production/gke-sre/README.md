# Practical SRE on Google Kubernetes Engine

Govern reliability of [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) on a private regional **GKE (Google Kubernetes Engine)** cluster. The system under study is the public repository:

```text
https://github.com/btilki/boutique-gke-sre
```

Infrastructure was decommissioned on **2026-07-04**. Public **DNS (Domain Name System)** names are **inactive**. Phases 1–8 **lived**. Phases 9-A–9-D are **repo-ready** and apply on rebuild. Only game day 03 has an executed report.

This is not a Northwind companion lab. There is no invented storefront. Open the files this book cites.

## Read in order

| # | Chapter |
| --- | --- |
| 0 | [How to Use This Book](00-how-to-use-this-book.md) |
| 1 | [Define the Reliability Platform, Not a Green Cluster](01-define-the-reliability-platform-not-a-green-cluster.md) |
| 2 | [Record Architecture and ADRs That Bound Blast Radius](02-record-architecture-and-adrs-that-bound-blast-radius.md) |
| 3 | [Build Private Foundation: Project, State, VPC, GKE](03-build-private-foundation-project-state-vpc-gke.md) |
| 4 | [Put DNS, TLS, and Ingress on a Recoverable Edge](04-put-dns-tls-and-ingress-on-a-recoverable-edge.md) |
| 5 | [Federate Identity and Pin a Signed Supply Chain](05-federate-identity-and-pin-a-signed-supply-chain.md) |
| 6 | [Pass the Phase 4 Gate Before Boutique Exists](06-pass-the-phase-4-gate-before-boutique-exists.md) |
| 7 | [Deploy Boutique by Digest and Manual Sync](07-deploy-boutique-by-digest-and-manual-sync.md) |
| 8 | [Make User Journeys Observable](08-make-user-journeys-observable.md) |
| 9 | [Page on Burn Rate, Not on Every Symptom](09-page-on-burn-rate-not-on-every-symptom.md) |
| 10 | [Design On-Call, Severity, and Incident Comms](10-design-on-call-severity-and-incident-comms.md) |
| 11 | [Harden the Edge: Cloud Armor and Binary Authorization](11-harden-the-edge-cloud-armor-and-binary-authorization.md) |
| 12 | [Treat Runbooks as Product, Not Wiki Pages](12-treat-runbooks-as-product-not-wiki-pages.md) |
| 13 | [Govern Error Budget, Capacity, and Toil](13-govern-error-budget-capacity-and-toil.md) |
| 14 | [Run Game Days and Write What Actually Happened](14-run-game-days-and-write-what-actually-happened.md) |
| 15 | [Backup, Tear Down, and Rebuild Without Orphans](15-backup-tear-down-and-rebuild-without-orphans.md) |
| 16 | [Conclusion — Reliability Is Behavior Under Loss](16-conclusion.md) |
| 17 | [Interview Questions From This Repository](17-interview-questions-from-this-repository.md) |

## Back matter

- [Glossary and Abbreviations](GLOSSARY.md)
- [References](REFERENCES.md)
- [Editorial conventions](EDITORIAL-CONVENTIONS.md)
- [Book plan](BOOK-PLAN.md) (planning artifact; not a chapter)

## Sister titles

- *Practical GitOps on Amazon EKS* — `boutique-eks-gitops`
- *Practical DevSecOps on Azure Kubernetes Service* — `boutique-aks-devsecops`

Reading order across the series is optional. This title uniquely owns **SLOs (Service Level Objectives)** on browse and checkout, burn-rate pages, error-budget freeze, on-call, runbooks, and honest game-day status.
