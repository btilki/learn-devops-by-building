# Practical SRE on Google Kubernetes Engine — Book Plan

**Planning status:** Active draft  
**Draft date:** 2026-08-18  
**Source repository:** `boutique-gke-sre`  
**Series:** [Boutique Production Series](../BOUTIQUE-SERIES.md)

## Promise

Govern reliability of Online Boutique on a private regional **GKE (Google Kubernetes Engine)** cluster: user-visible **SLOs (Service Level Objectives)** and burn-rate pages, error-budget policy that can freeze change, PagerDuty on-call, runbooks that match alerts, game days with honest status, supply-chain and edge controls that reliability depends on, and teardown that leaves no orphans.

The reader will be able to explain, from this repository, which journeys SLOs protect, why remaining budget changes engineering behavior, why a dashboard is not recovery evidence, and what the 2026-07-04 Redis game day actually proved.

## Audience

Intermediate-to-advanced SRE, platform, and cloud practitioners. Delivery and GitOps mechanics are consumed, not retaught as the point of the book. Reliability decisions are the point.

## System under study

```text
https://github.com/btilki/boutique-gke-sre
```

Local path: `/Users/biroltilki/Documents/Cursor/boutique-gke-sre`.

Phases 1–8 lived. Infrastructure was decommissioned on 2026-07-04. Phases 9-A–9-D are repo-ready and apply on rebuild. DNS names are inactive. Only game day 03 has an executed report.

## Coverage rule

Every setup topic (01–20), architecture overview, ADR (001–003), Terraform module, GitOps tree, observability tree, `docs/sre/` tree, security doc, workflow, game-day script, teardown script, and release note must appear in at least one chapter. Label Phase 9 and deferred game days honestly.

## Index

0. How to Use This Book
1. Define the Reliability Platform, Not a Green Cluster
2. Record Architecture and ADRs That Bound Blast Radius
3. Build Private Foundation: Project, State, VPC, GKE
4. Put DNS, TLS, and Ingress on a Recoverable Edge
5. Federate Identity and Pin a Signed Supply Chain
6. Pass the Phase 4 Gate Before Boutique Exists
7. Deploy Boutique by Digest and Manual Sync
8. Make User Journeys Observable
9. Page on Burn Rate, Not on Every Symptom
10. Design On-Call, Severity, and Incident Comms
11. Harden the Edge: Cloud Armor and Binary Authorization
12. Treat Runbooks as Product, Not Wiki Pages
13. Govern Error Budget, Capacity, and Toil
14. Run Game Days and Write What Actually Happened
15. Backup, Tear Down, and Rebuild Without Orphans
16. Conclusion — Reliability Is Behavior Under Loss
17. Interview Questions From This Repository

## Back matter

- Glossary and Abbreviations
- References

## Topic map

| Chapter | Setup / area |
|---|---|
| 1 | README, PROJECT, ROADMAP, bootstrap, production bar |
| 2 | ARCHITECTURE, overview, ADRs 001–003, diagrams |
| 3 | setup 01–04, terraform project-apis/networking/gke |
| 4 | setup 05–06, dns, ingress-edge, managed certificates |
| 5 | setup 07–08, WIF, AR, Binary Auth, GitHub workflows, supply-chain.md |
| 6 | setup 09–11, Argo, ESO, Kyverno, NetworkPolicy, ADR 003 |
| 7 | setup 12, gitops/apps/boutique, rollback, digest-only tests |
| 8 | setup 13 (stack), otel/prometheus/grafana |
| 9 | setup 13/17, slos, burn policies, uptime checks, dashboards |
| 10 | setup 14, oncall, incident-response, PagerDuty |
| 11 | setup 15–16, armor, smoke validation, edge-hardening |
| 12 | docs/sre/runbooks, runbooks.yaml, runbook-lint CI |
| 13 | setup 20, error-budget-policy, capacity, orphan cadence |
| 14 | setup 18, game-days, postmortems, HPA/PDB, STATUS honesty |
| 15 | setup 19, monitoring/backup modules, teardown, cluster-rebuild |

## Recurring principles

1. User-visible journeys, not cluster Ready, count as reliability success.
2. Remaining error budget authorizes or freezes change.
3. Every page has a runbook URL.
4. Manual Argo sync is promotion discipline, not missing automation.
5. Game-day STATUS without a dated report is a false claim.
6. Teardown with orphan scan is part of the reliability contract.
