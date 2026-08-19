# Editorial Conventions — Practical SRE on Google Kubernetes Engine

This book follows the Boutique Production Series conventions.

**Series file (canonical):** [BOUTIQUE-EDITORIAL-CONVENTIONS.md](../BOUTIQUE-EDITORIAL-CONVENTIONS.md)

**Series contract:** [BOUTIQUE-SERIES.md](../BOUTIQUE-SERIES.md)

Do not copy Northwind lab commands, `make chapter-NN-*` checkpoints, or companion-lab snapshots into this manuscript. The system under study is the public repository [boutique-gke-sre](https://github.com/btilki/boutique-gke-sre). Practice means opening a real path in that repository, interpreting a lived or scaffolded decision, and stating what evidence would prove a change. Rebuilds cost money and are optional unless a chapter is explicitly about teardown or rebuild.

## Book-local principles

These six series principles apply throughout. Dedicated failure sections name only those that the scenario actually exercises.

1. **Git is the deploy authority** unless the chapter is a bounded exception (bootstrap, teardown, emergency Binary Authorization break-glass).
2. **Identity is digest, not tag.** Floating tags and `:latest` are failures.
3. **CI never deploys** the cluster. GitHub Actions produces scanned, signed evidence and proposes digest PRs.
4. **Namespaces on one cluster are not multi-account isolation.** ADR 001 chose one project and one regional cluster.
5. **Teardown is a production control**, not an afterthought. Orphan scan and inactive DNS are in the reliability contract.
6. **Lived evidence beats scaffold.** Phases 1–8 ran. Phases 9-A–9-D are repo-ready and apply on rebuild. Only game day 03 has a dated executed report.

## Reliability refusals (this title)

- Cluster Ready, kubelet Ready, and Argo CD UI uptime are not reliability success.
- **SLOs (Service Level Objectives)** protect browse and checkout user journeys.
- A STATUS table without a dated game-day report is a false claim.
- Remaining error budget authorizes, slows, or freezes change.

## Honesty labels

- **Lived:** Topics and milestones that ran on the real `boutique-gke` cluster before teardown on 2026-07-04.
- **Scaffold:** Files in Git that were not live-validated on this pilot (Phase 9 apply-on-rebuild work, deferred game days 01, 02, and 04).
- **Inactive:** DNS names and screenshots that remain after teardown (`boutique.biroltilki.art`, `argocd.boutique.biroltilki.art`).
