# References

Primary system under study. Do not treat this list as a substitute for opening the cited paths in each chapter.

## Repository

- Public: https://github.com/btilki/boutique-gke-sre
- Upstream application: https://github.com/GoogleCloudPlatform/microservices-demo
- Sister GitOps platform: https://github.com/btilki/boutique-eks-gitops
- Sister DevSecOps platform: https://github.com/btilki/boutique-aks-devsecops

## Charter, roadmap, bootstrap

- `README.md` — decommissioned 2026-07-04; inactive DNS; SRE lens
- `PROJECT.md` — production bar; Phase 4 session rule
- `ROADMAP.md` — Phases 1–8 lived; 9-A–9-D apply on rebuild
- `ARCHITECTURE.md` — executive stack flow
- `docs/bootstrap.md` — ordered path; gate before Boutique
- `docs/architecture/overview.md` — 16-section design
- `docs/dns.md` — inactive hostnames; delegation
- `docs/teardown.md` — destroy order; orphan validation
- `REPOSITORY_STRUCTURE.md` — layout

## ADRs

- `docs/adr/001-single-cluster.md`
- `docs/adr/002-wif-over-sa-keys.md`
- `docs/adr/003-manual-argocd-sync.md`

## Setup topics 01–20

- `docs/setup/README.md` — index and dependency graph
- `docs/setup/01-gcp-project-apis.md` through `16-smoke-validation.md` — lived bootstrap
- `docs/setup/17-latency-slos-dashboards.md` — Phase 9-A apply on rebuild
- `docs/setup/18-sre-operability-game-days.md` — Phase 9-B apply on rebuild
- `docs/setup/19-monitoring-backup-terraform.md` — Phase 9-C apply on rebuild
- `docs/setup/20-sre-practices-capacity-toil.md` — Phase 9-D cadence

## Terraform

- `terraform/environments/boutique/` — root wiring, backend, flags
- `terraform/modules/project-apis/`
- `terraform/modules/networking/`
- `terraform/modules/gke/`
- `terraform/modules/ingress-edge/`
- `terraform/modules/dns/`
- `terraform/modules/wif/`
- `terraform/modules/artifact-registry/`
- `terraform/modules/binary-authorization/`
- `terraform/modules/armor/`
- `terraform/modules/monitoring/`
- `terraform/modules/backup/`

## GitOps and policy

- `gitops/bootstrap/root-app.yaml`
- `gitops/bootstrap/argocd/`
- `gitops/bootstrap/external-secrets/`
- `gitops/apps/argocd-apps/`
- `gitops/apps/boutique/` — Helm chart, `values.yaml`, `values-images.yaml`, HPA/PDB templates
- `gitops/policies/kyverno/`
- `gitops/policies/network-policies/`

## CI and tests

- `.github/workflows/build-scan-sign.yml`
- `.github/workflows/ci.yml` — includes `scripts/validate-runbook-links.sh`
- `.github/workflows/mirror-platform-images.yml`
- `.github/trivy/upstream-mirror.trivyignore`
- `tests/manifest/digest-only.sh`
- `tests/kyverno/`

## Observability and SRE

- `observability/README.md`
- `observability/otel/collector/`
- `observability/prometheus/`
- `observability/grafana/`
- `observability/monitoring/slos/`
- `observability/monitoring/alert-policies/`
- `observability/monitoring/uptime-checks/`
- `observability/monitoring/log-based-metrics/`
- `observability/monitoring/runbooks.yaml`
- `docs/sre/README.md`
- `docs/sre/slos/catalog.md`
- `docs/sre/slos/burn-rate-alerting.md`
- `docs/sre/error-budget-policy.md`
- `docs/sre/error-budget/`
- `docs/sre/capacity/baseline.md`
- `docs/sre/oncall/`
- `docs/sre/incident-response/severity.md`
- `docs/sre/incident-response/comms.md`
- `docs/sre/runbooks/` — all alert-linked and DR runbooks
- `docs/sre/game-days/` — guides 01–04
- `docs/sre/game-days/reports/STATUS.md`
- `docs/sre/game-days/reports/2026-07-04-redis-cart-down.md`
- `docs/sre/postmortems/2026-07-04-redis-cart-down.md`
- `.github/ISSUE_TEMPLATE/error_budget_freeze.md`

## Security and operations

- `docs/security/supply-chain.md`
- `docs/security/edge-hardening.md`
- `docs/operations/rollback.md`
- `docs/operations/orphan-scan-cadence.md`
- `docs/operations/operations-runbook.md`

## Scripts

- `scripts/game-days/inject-redis-down.sh`
- `scripts/game-days/inject-pod-failure.sh`
- `scripts/teardown/orphan-resource-scan.sh`
- `scripts/teardown/pre-destroy-checklist.sh`
- `scripts/create-burn-rate-policies.sh`
- `scripts/create-latency-burn-rate-policies.sh`
- `scripts/create-uptime-check.sh`
- `scripts/create-argocd-uptime-check.sh`
- `scripts/attach-argocd-armor.sh`
- `scripts/load/smoke-browse.sh`
- `scripts/validate-runbook-links.sh`

## Diagrams and inactive screenshots

- `assets/diagrams/README.md` — mermaid sources plus lived PNG catalog
- `assets/diagrams/architecture.mmd`
- `assets/diagrams/network-flow.mmd`
- `assets/diagrams/deployment-pipeline.mmd`
- `assets/diagrams/sre-alert-flow.mmd`
- Lived PNGs (inactive DNS): `argocd-applications-healthy-synced.png`, `grafana-boutique-dashboard.png`, `slo-browse-checkout.png`, `pagerduty-test-incident.png`, `kyverno-five-policies.png`, `cloud-armor-ingress.png`, `binary-auth-enforced.png`, `runbook-lint-success.png`, `boutique-storefront-https.png`

This repository has no `CHANGELOG.md`. Use `ROADMAP.md` and `docs/release/` as the rebuild delta.

## Playbook (further reading, not a second source of truth)

- Hub: https://github.com/btilki/devops-engineering-playbook
- Featured brief: https://github.com/btilki/devops-engineering-playbook/blob/main/featured-projects/boutique-gke-sre.md
- G1 — SLOs and burn-rate alerts: https://github.com/btilki/devops-engineering-playbook/blob/main/articles/G1.md
- G2 — WIF over SA keys: https://github.com/btilki/devops-engineering-playbook/blob/main/articles/G2.md
- G3 — Binary Authorization + Cloud Armor: https://github.com/btilki/devops-engineering-playbook/blob/main/articles/G3.md

## Companion books (reference, not replacements)

- Beyer, Jones, Petoff, Murphy, *Site Reliability Engineering* — principles (already linked via sre.google above).
- Beyer, Murphy, Rensin, Kawahara, Thorne, *The Site Reliability Workbook* — alerting on SLOs; closest published companion to Chapters 9–14.
- Do not treat a workbook lab’s green cluster as this repository’s browse/checkout contract.

## External (linked from the repository)

- Google SRE book — Service Level Objectives: https://sre.google/sre-book/service-level-objectives/
- Google SRE workbook — Alerting on SLOs: https://sre.google/workbook/alerting-on-slos/
- Cloud Monitoring SLO alerts: https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring#alerting_on_slo
- Cloud DNS: https://cloud.google.com/dns/docs
- Kyverno: https://kyverno.io/docs/kyverno-cli/
- Argo Helm releases: https://github.com/argoproj/argo-helm/releases

## Series files (manuscript, not the cluster)

- [BOUTIQUE-SERIES.md](../BOUTIQUE-SERIES.md)
- [BOUTIQUE-EDITORIAL-CONVENTIONS.md](../BOUTIQUE-EDITORIAL-CONVENTIONS.md)
- [BOOK-PLAN.md](BOOK-PLAN.md)
