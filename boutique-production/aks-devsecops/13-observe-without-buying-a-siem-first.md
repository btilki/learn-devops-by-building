# 13. Observe Without Buying a SIEM First

A DevSecOps platform that cannot see frontend replicas or admission controller health will promote blindly. This chapter is Setup Topic **11**: kube-prometheus-stack, Loki, Promtail, Grafana, and a test **SLO (Service Level Objective)**. [ADR-0012](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0012-loki-in-cluster-logging.md) rejects Azure Log Analytics on the default path. This is not a **SOC (Security Operations Center)** **SIEM (Security Information and Event Management)**.

The production question is:

> What observability is enough to pause a promotion, and what must you refuse to claim because you did not buy a SIEM?

## 1. Unsafe starting state

The unsafe default is Container Insights plus a Log Analytics workspace “for security.” ADR-0012's context: ingestion can cost more than the rest of the stack. The other default is Grafana with no alert that Kyverno is down — admission failure then looks like a random deploy issue.

Traces to Tempo/Jaeger are deferred. `ARCHITECTURE.md` limitations say so. Do not describe this chapter as distributed tracing production.

## 2. The production model: in-cluster metrics and logs

> *Theory — Proportionate observability*
>
> This model enables the operator to detect Boutique, ingress, node, and Kyverno failure on the same cluster that runs the app — without an Azure Monitor bill or a 24×7 on-call roster.

Stack from `docs/architecture/10-observability.md`:

| Layer | Technology | Path |
|-------|------------|------|
| Metrics | Prometheus (kube-prometheus-stack) | `gitops/platform/monitoring/kube-prometheus-stack/` |
| Dashboards | Grafana | same |
| Alerting | Alertmanager | same |
| Logs | Loki + Promtail | `loki/`, `promtail/` |
| Traces | OTel Collector baseline | `otel/` |

Retention: Prometheus 15d; Loki ~10Gi PVC. Grafana hostname `grafana-boutique.biroltilki.art` (inactive after teardown).

No automated paging in v1. The SLO doc says the operator checks Grafana after deploys. That is honest for a solo pilot.

## 3. How this repository implements Topic 11

> **Practice — Read the GitOps waves**
>
> Open `docs/setup/11-observability.md` and `gitops/platform/monitoring/`.

Sync waves: Loki 38, Promtail 39, kube-prometheus-stack 40, otel-collector 41, extras 45. Chart pins: kube-prometheus-stack `58.2.2`, Loki `6.23.0`, Promtail `6.16.6`, otel `0.95.0`.

Grafana admin credentials follow the Topic 07 pattern (Key Vault / Kubernetes Secret), not a password in `values.yaml` on Git.

> **Practice — Read the pilot SLO**
>
> Open `docs/slo/boutique-availability.md`.

| Field | Value |
|-------|-------|
| **SLI** | HTTP `GET /_healthz` on frontend via ingress |
| Availability | **99.5%** / 30 days |
| Error budget | ~3.6 hours/month |
| Latency p95 | < 500 ms informational / 7 days |

Error budget policy: below 25% remaining, freeze promotions to stage/prod; exhausted budget triggers incident review and digest rollback. This is not the GKE sister's PagerDuty burn-rate pages. It is a written freeze rule for a solo operator.

Canonical alerts (`gitops/platform/monitoring/extras/alerts/`):

| Alert | Condition |
|-------|-----------|
| `BoutiqueFrontendDown` | frontend replicas &lt; 1 for 5m |
| `BoutiqueDevPodsNotReady` | Ready pods &lt; 80% for 10m |
| `IngressCertExpiringSoon` | cert &lt; 14 days |
| `NodeNotReady` | node NotReady 10m |
| `KyvernoAdmissionDown` | Kyverno admission replicas &lt; 1 for 5m |

`KyvernoAdmissionDown` is a security-relevant alert. A SIEM would correlate it with policy reports; this pilot correlates it with Grafana and `kubectl get clusterpolicy`.

Lived screenshots: `11-grafana-dashboards-list.png`, `11-grafana-alertmanager-overview.png`, `11-grafana-boutique-overview.png`. Use them when the hostname is dead.

OTel collector accepts **OTLP (OpenTelemetry Protocol)** at ~10% sampling. There is no Tempo backend. Trace “support” is a receiver, not a product.

Grafana values set hostname `grafana-boutique.biroltilki.art` and Prometheus retention `15d`. Loki SingleBinary + 10Gi PVC is the ADR-0012 cost trade: logs compete with Boutique for node disk. Promtail DaemonSet is the tax on every node. That is cheaper than Log Analytics ingestion at debug volume, not free.

Example LogQL from architecture 10: `{namespace="boutique-dev", app="frontend"}`. Use it during Topic 12 failures before guessing Kyverno. `docs/operations/11-logging.md` and `09-monitoring.md` are the operator expansions.

Alert `IngressCertExpiringSoon` at 14 days is the TLS coupling to Chapter 8. `NodeNotReady` is ADR-0002’s shared fate: one node pool, three namespaces.

The GKE sister pages on burn rate. This book’s SLO freeze is a paragraph. If you add PagerDuty here without error-budget policy and a roster, you have copied a logo. `docs/slo/boutique-availability.md` exclusions: planned maintenance, platform outages tracked separately, loadgenerator failures not user SLI.

`docs/troubleshooting/monitoring-alerting.md` is the symptom index. After teardown, Grafana screenshots are the dashboards.

## Lived operator commands (Topic 11)

```bash
kubectl get appproject -n argocd monitoring
kubectl get pods -n monitoring
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
# Grafana: https://grafana-boutique.biroltilki.art (inactive after teardown)
./tests/integration/dev-smoke.sh
```

LogQL: `{namespace="boutique-dev"}`. Confirm PrometheusRule `BoutiqueFrontendDown` is loaded. Confirm Loki datasource in Grafana. Screenshots `11-grafana-*.png` replace the UI after destroy. Do not enable `oms_agent` to “fill a gap.”

Limits: this is not a SIEM, not PagerDuty, not Tempo. Falco alerts in `extras/alerts/runtime-security.yaml` are scaffold. The SLO freeze is a paragraph you must obey, not an automation. Sister GKE book is where burn-rate paging is the point.

## 4. Test the design under failure

### Independent control failure — Promote while Grafana is dark

> **Practice — Apply the error-budget freeze without a pager**
>
> Boutique Overview is unreachable. Alertmanager is unknown. An engineer still queues prod promotion because “dev looked fine in kubectl.”

**Severity:** high; change without independent health evidence.  
**Plausible harm:** prod namespace served from a degraded ingress or empty frontend; SLO budget spent invisibly.  
**Potential blast radius:** `boutique-prod` on the shared cluster; users of `boutique.biroltilki.art` when live.  
**Bounded by:** Topic 12 preconditions (Grafana + smoke), SLO freeze table, promotion runbook.  
**Primary principles:** trustworthy evidence, Git is the deploy authority, lived evidence beats scaffold.

#### Diagnosis

kubectl `get pods` is not the SLO. The SLI is ingress `/_healthz`. If Grafana is down, you have lost the dashboard, not necessarily Boutique — but you have also lost Kyverno and cert alerts. Promoting is deciding without detection.

#### Correction

Restore monitoring (`docs/troubleshooting/monitoring-alerting.md`) or accept a documented emergency with explicit owner. Do not treat “no SIEM” as “no need to look.” Recovery evidence is smoke test plus dashboard, not a green ADO job.

A second failure: re-enabling Log Analytics to “be more enterprise.” Correction: read ADR-0012 cost context; keep `diagnostics` unwired unless a new ADR accepts the bill.

## Production reality

**Best Practice:** metrics, logs, and a written error-budget freeze before promotion.

**Production Practice:** no Log Analytics on the default path. No SIEM. No 24×7. OTel without Tempo is a receiver. Document those absences in the README limitations table (Chapter 1) so Chapter 13 cannot be retold as “full observability.”

Self-monitoring: if Prometheus is down, you lose `KyvernoAdmissionDown`. kubectl remains. That is the residual.

### Common errors

- Enabling Container Insights and double-paying for logs.
- Alerting every CrashLoop as SEV-1 (see Chapter 17 SEV table).
- Treating loadgenerator 500s as the user SLI.

## 5. What You Learned

Topic 11 puts Prometheus, Grafana, Loki, and a 99.5% frontend SLO on the cluster. It does not provide 24×7 on-call, Tempo, or a SIEM. Kyverno health is an alert. Screenshots survive teardown. Promotion in Chapter 14 is supposed to look here first.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 11 guide | `docs/setup/11-observability.md` | Waves, Grafana secret, validation |
| Monitoring GitOps | `gitops/platform/monitoring/` | Stack and extras alerts |
| ADR-0012 | `docs/adr/0012-loki-in-cluster-logging.md` | Why not Log Analytics |
| SLO | `docs/slo/boutique-availability.md` | Freeze rule |
| Architecture | `docs/architecture/10-observability.md` | Metrics/logs/traces scope |
| Screenshots | `assets/images/setup/11-grafana-*.png` | Inactive UI evidence |

## What changed

| Before | After |
|--------|--------|
| Log Analytics as the default. | **Loki + Promtail in-cluster (ADR-0012).** |
| No promotion freeze. | **99.5% SLO and error-budget table.** |
| Kyverno silent death. | **`KyvernoAdmissionDown` alert.** |
| Tracing as a product claim. | **OTLP receiver, no Tempo.** |

`gitops/platform/monitoring/kube-prometheus-stack/values.yaml` and `loki/values.yaml` are the Helm pins. `extras/alerts/` is the rule SSOT. `docs/operations/10-alerting.md` maps alerts to runbooks via `runbook_url` annotations — add those URLs when you own a GitHub org path.

> **Independent Practice — Map one alert to a runbook**
>
> For `KyvernoAdmissionDown`, write the first five commands and the promotion rule (block or allow) using `docs/operations/README.md` and `docs/runbooks/incident-response.md`. Do not invent a PagerDuty integration.

**Figure 13.1 — Inactive.** Grafana Boutique Overview (replicas / pods / ingress).

![Grafana boutique overview](https://raw.githubusercontent.com/btilki/boutique-aks-devsecops/main/assets/images/setup/11-grafana-boutique-overview.png)

Source: `assets/images/setup/11-grafana-boutique-overview.png`. A dashboard is not a SIEM.
