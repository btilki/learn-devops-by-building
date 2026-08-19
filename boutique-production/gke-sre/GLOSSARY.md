# Glossary and Abbreviations

First use in each reader-facing chapter writes **ABBR (Full Form)** in bold. This glossary is the book-wide list. Do not expand abbreviations inside code fences, filenames, or version identifiers.

## A

**ADR (Architecture Decision Record)**  
A dated, accepted decision in `docs/adr/`. This book uses 001 (single cluster), 002 (WIF over SA keys), and 003 (manual Argo CD sync).

**AR (Artifact Registry)**  
Regional Docker repository `europe-west1-docker.pkg.dev/boutique-gke/boutique` for digest-pinned images.

## B

**BA (Binary Authorization)**  
GKE admission policy that requires cosign attestations (enforce) or logs violations (dry-run). Lived collision: 2026-07-04 Redis restore.

**Blast radius**  
The set of users, namespaces, and controls affected by a change or failure. Namespaces on one cluster are not multi-account isolation.

## C

**CI (Continuous Integration)**  
GitHub Actions workflows. CI produces scans, signatures, and digest PRs. It does not deploy the cluster.

**Cloud Armor**  
Google Cloud WAF / rate-limit policies attached to HTTP(S) load-balancer backends (`boutique-owasp-crs`, `argocd-edge`).

**Cloud Monitoring**  
GCP service hosting SLOs, uptime checks, and burn-rate alert policies.

**CRS (OWASP ModSecurity Core Rule Set)**  
Preconfigured Cloud Armor expressions (for example `xss-stable`, `sqli-stable`).

## D

**Digest**  
Immutable image identity `sha256:…`. Tags and `:latest` are failures of identity.

**DNS (Domain Name System)**  
Cloud DNS zone and A records for `boutique.biroltilki.art` and `argocd.boutique.biroltilki.art`. **Inactive** after 2026-07-04 teardown.

**DRYRUN**  
Binary Authorization mode `DRYRUN_AUDIT_LOG_ONLY`: violations logged, deploys still succeed. Emergency break-glass when time-boxed.

## E

**Error budget**  
Allowed unreliability complementary to an SLO target over the window. Remaining budget selects continue / cautious / freeze / SEV2.

**ESO (External Secrets Operator)**  
Cluster operator that materializes Kubernetes Secrets from Secret Manager. Plain Secrets in Git are denied by Kyverno.

**Evidence (four kinds)**  
Mechanism, decision, outcome, and recovery evidence — see How to Use. A dashboard is not outcome evidence for browse/checkout.

## F

**Freeze**  
Error-budget response below 25% remaining (and SEV2 at 0%): non-critical deploys stop; tracked in freeze-log + GitHub issue.

## G

**GCP (Google Cloud Platform)**  
Cloud for project `boutique-gke`.

**GKE (Google Kubernetes Engine)**  
Regional private cluster `boutique-gke` in `europe-west1`.

**GitOps (Git-based operations)**  
Desired cluster state in Git, reconciled by Argo CD. Manual sync is ADR 003.

**GMP (Google Managed Prometheus)**  
Metrics backend used with the OTel collector exporter.

## H

**HA (high availability)**  
Multi-replica + HPA/PDB defaults in GitOps. Topic 18 apply-on-rebuild; not fully proved by GD02 (deferred).

**HPA (Horizontal Pod Autoscaler)**  
CPU-based scaling for frontend and checkout (min 2, max 6 in the capacity baseline).

## I

**Inactive**  
Honesty label: DNS names and screenshots that remain after teardown; not proof the platform is live.

## K

**Kyverno**  
Admission controller. Five ClusterPolicies: digest, probes, resources, netpol labels, block plain Secrets.

## L

**Lived**  
Honesty label: ran on the real cluster before 2026-07-04 teardown (Phases 1–8, topics 01–16, GD03).

## N

**NAT (Cloud NAT)**  
Egress for private GKE nodes in `boutique-vpc`.

**NetworkPolicy**  
Kubernetes default-deny plus explicit allows for Boutique and observability.

## O

**OIDC (OpenID Connect)**  
Token issuer `token.actions.githubusercontent.com` trusted by the WIF provider.

**OTel (OpenTelemetry)**  
OTLP traces/metrics from Boutique to the collector, then Cloud Trace and GMP.

**Orphan**  
Leftover GCP resource after destroy (static IP, forwarding rule, disk). Scan is report-only.

## P

**PDB (Pod Disruption Budget)**  
`minAvailable` on frontend, checkout, cart, redis-cart. Does not make single-instance Redis multi-master.

**Phase 4 gate**  
Topics 09–11 (Argo CD, ESO, Kyverno/NetworkPolicy) before Boutique deploy.

**Phase 9**  
Topics 17–20: latency SLOs/dashboards, operability/game days, monitoring/backup Terraform, SRE practices. **Repo-ready / apply on rebuild.**

## R

**RPO (Recovery Point Objective)** / **RTO (Recovery Time Objective)**  
Architecture targets for Redis (&lt; 1h / &lt; 30m) and cluster rebuild (hours). Targets are not proofs.

**Runbook**  
Versioned procedure linked from an alert policy via `observability/monitoring/runbooks.yaml`.

## S

**Scaffold**  
Honesty label: files in Git not live-validated on this pilot after teardown (much of Phase 9; deferred game days).

**SEV (severity)**  
SEV1–SEV4 taxonomy in `docs/sre/incident-response/severity.md`. Exhausted error budget is SEV2 minimum.

**SLI (Service Level Indicator)**  
Quantitative measure of a user journey (availability ratio, p95 latency).

**SLO (Service Level Objective)**  
Internal target on an SLI (browse 99.9% / 500ms; checkout 99.95% / 1000ms). Not a customer SLA. Not cluster Ready.

**SRE (Site Reliability Engineering)**  
The discipline this book practices: journeys, SLOs, burn, freeze, on-call, game days, teardown.

## T

**TLS (Transport Layer Security)**  
Google-managed certificates on GCE Ingress.

## U

**Uptime check**  
Cloud Monitoring synthetic against storefront and (topic 18) Argo CD `/healthz`. Adjacent to SLOs, not a substitute.

## V

**VPC (Virtual Private Cloud)**  
`boutique-vpc` with subnet and secondary pod/service ranges.

## W

**WAF (Web Application Firewall)**  
Cloud Armor policies at the HTTPS load balancer.

**WIF (Workload Identity Federation)**  
GitHub OIDC to GCP without JSON keys (ADR 002). Also used for ESO and OTel service accounts to GCP APIs.
