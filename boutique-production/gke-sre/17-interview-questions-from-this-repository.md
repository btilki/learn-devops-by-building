# 17 — Interview Questions From This Repository

Answer from `boutique-gke-sre`. Infrastructure was decommissioned on **2026-07-04**. Public **DNS (Domain Name System)** is **inactive**. Only game day 03 has an executed report. If the clone is newer than this manuscript, start at `ROADMAP.md` and `docs/release/` — this repository has no `CHANGELOG.md`.

## 1. What does reliability protect on this platform?

Browse and checkout user journeys, not cluster Ready or Argo **CD (Continuous Delivery)** UI uptime. Catalog: `docs/sre/slos/catalog.md`. Browse **SLO (Service Level Objective)** 99.9% / p95 < 500ms; checkout 99.95% / p95 < 1000ms. Chapter 1 refuses uptime theater. `PROJECT.md` production bar is the charter, not a green kubelet.

## 2. Why page on burn rate instead of CPU?

CPU > 80% pages on a symptom. Burn pages when remaining error budget is being consumed too fast for the SLO window. Multi-window: 14.4× / 6× / 3× / 1× with a Cloud Monitoring **API (Application Programming Interface)** 24h lookback caveat. `docs/sre/slos/burn-rate-alerting.md`, `observability/monitoring/alert-policies/`. Playbook **G1** is the short public argument.

## 3. What happens when error budget is exhausted?

Policy bands in `docs/sre/error-budget-policy.md`: >50% normal, 25–50% cautious, <25% freeze, 0% **SEV2 (Severity 2)**. Freeze is a GitHub issue plus append-only `docs/sre/error-budget/freeze-log.md`, not a Slack message. Remaining budget authorizes or freezes digest syncs and risky infra.

## 4. Why is Argo sync manual on a single cluster?

ADR-003: promotion discipline. Surprise auto-sync is how a bad digest becomes production without a human. `docs/adr/003-manual-argocd-sync.md`, setup topic 09. This is consumed GitOps, not the thesis of the book. The thesis is what happens after the sync: SLOs, pages, freeze, game days.

## 5. How do you avoid long-lived GCP service-account keys in CI?

**WIF (Workload Identity Federation)** / **OIDC (OpenID Connect)** only. ADR-002 prohibits SA JSON keys in GitHub. `terraform/modules/wif/`, `docs/setup/07-github-wif.md`, `.github/workflows/build-scan-sign.yml`. Playbook **G2**.

## 6. What is the Phase 4 gate?

Do not deploy Boutique until Argo CD, **ESO (External Secrets Operator)**, Kyverno, and NetworkPolicy pass. `PROJECT.md`, `docs/bootstrap.md`, setup topics 09–11. The gate exists so a storefront on an ungoverned cluster cannot be called an SRE platform.

## 7. Walk the path from SLO to a human with a runbook.

User-facing **SLI (Service Level Indicator)** → SLO → error budget → burn-rate alert with documentation URL → PagerDuty → `docs/sre/runbooks/`. Registry: `observability/monitoring/runbooks.yaml`. CI: `scripts/validate-runbook-links.sh` / `make runbook-lint`. A dashboard without a runbook URL is not a page.

## 8. What did game day 03 actually prove?

On 2026-07-04, scaling `redis-cart` to zero produced storefront HTTP 500. Restore was blocked by **BA (Binary Authorization)** until a time-boxed DRYRUN. PagerDuty was **not** verified. Report: `docs/sre/game-days/reports/2026-07-04-redis-cart-down.md`. STATUS: `docs/sre/game-days/reports/STATUS.md`. Game days 01, 02, and 04 have guides and **no** executed reports. Do not claim they ran.

## 9. How do you roll back a bad deploy?

Git digest revert + manual Argo sync. `docs/operations/rollback.md`, `docs/sre/runbooks/bad-deploy-rollback.md`. Cluster-only `kubectl rollout undo` is not the system of record.

## 10. How do you tear down without leaving orphans?

`docs/teardown.md`, `scripts/teardown/pre-destroy-checklist.sh`, `scripts/teardown/orphan-resource-scan.sh` (report only — never pipe to delete). Destroy order matters: Ingress/LB before cluster/VPC. Teardown is a reliability control, not optional hygiene. DNS stays inactive until rebuild.

## How to use this appendix

Keep production-style language. Do not say enterprise **HA (High Availability)** or multi-region. Point at the Redis report when asked for evidence of learning. Playbook G1–G3 are further reading; the files remain the system.
