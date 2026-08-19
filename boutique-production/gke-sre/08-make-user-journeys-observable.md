# 8. Make User Journeys Observable

A shop without traces, metrics, and dashboards leaves on-call guessing from `kubectl logs`. Observability still must not replace SLOs. The production question is:

> How do browse and checkout emit signals that SRE can query — without treating Grafana uptime as the journey?

Setup topic **13**’s **stack half** (**Lived**): **OTel (OpenTelemetry)** Collector, **GMP (Google Managed Prometheus)** / Prometheus values, Grafana, export to Cloud Trace and Cloud Monitoring. SLO objects and burn policies are Chapter 9. Topic 17 Grafana dashboards JSON is **repo-ready / apply on rebuild**.

## 1. An unsafe starting state: logs only, or dashboards as SLOs

Running Boutique with stdout in Cloud Logging is not observability for SRE. Neither is a Grafana folder named “Golden Signals” that no one wired to an SLO. Architecture §13 splits ownership: SRE owns SLOs/SLIs and uptime checks; platform owns dashboards, metrics, traces, logs plumbing.

The unsafe collapse is: “we installed kube-prometheus-stack, therefore we have SRE.” Topic 13’s goal lists both the stack **and** Cloud Monitoring SLOs. This chapter isolates the stack so Chapter 9 can attach objectives without pretending the collector is a 99.9% target.

## 2. The production model: OTLP in, GCP backends out, Grafana for triage

> *Theory — Journey telemetry pipeline*
>
> This model enables checkout debugging from traces and browse/checkout SLI queries from metrics and logs, while Grafana remains a triage surface rather than the source of error budget.

### Data flow

`observability/README.md`:

```text
Online Boutique pods (OTLP)
  → OTel Collector
  → Cloud Trace + Managed Prometheus
  → Grafana dashboards + Cloud Monitoring SLOs
  → Burn-rate alerts → PagerDuty
```

The last two arrows are later chapters. The first three are this one.

### Collector contract

`observability/otel/collector/config.yaml` receives OTLP gRPC `4317` and HTTP `4318`, batches, memory-limits, upserts `service.namespace=boutique`, exports `googlecloud` traces to project `boutique-gke` and `googlemanagedprometheus` metrics. Workload Identity on the collector SA (`otel-collector@boutique-gke.iam.gserviceaccount.com`) replaces JSON keys — same federation idea as CI, different SA.

Boutique `values.yaml` points `collectorServiceAddr: otel-collector.observability.svc:4317`. NetworkPolicy `boutique-allow` must permit that egress or traces vanish while HTTP 200 continues — a reminder that missing telemetry is not journey success.

### Grafana is not Git-secret based

Topic 13: Grafana admin from Secret Manager via ESO. Kyverno blocks plain `kubectl create secret`. Datasources: `observability/grafana/datasources.yaml` — Managed Prometheus and Cloud Monitoring. Port-forward for operators; the public journey remains the storefront hostname.

**Best Practice:** Sync `observability` Application with namespace label `network-policy.biroltilki.art/tier: platform`. Do not `kubectl create namespace observability` alone.

**Production Practice:** Platform images (OTel, Grafana) need the `mirror-platform-images.yml` workflow before first sync if digests are not in AR. Otherwise BA/Kyverno fights the stack.

## 3. How this repository implements it

> **Practice — Open the observability tree as the Phase 6 stack**
>
> Read `observability/README.md` layout: `otel/`, `prometheus/`, `grafana/`, `monitoring/`.

Collector receivers and exporters (abridged from `observability/otel/collector/config.yaml`):

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
exporters:
  googlecloud:
    project: boutique-gke
  googlemanagedprometheus:
    project: boutique-gke
```

`prometheus/values.yaml` is kube-prometheus-stack Helm values for in-cluster metrics where configured. GMP is the GCP-aligned path. Do not assume every panel in a screenshot is still scraping — `assets/diagrams/grafana-boutique-dashboard.png` is **Inactive**.

Topic 13 creates the collector GCP SA with `roles/cloudtrace.agent` and `roles/monitoring.metricWriter`, then binds Workload Identity user on `boutique-gke.svc.id.goog[observability/otel-collector]`. Same federation pattern as ESO, different SA. Platform images come from `.github/workflows/mirror-platform-images.yml` when digests are not yet in AR.

> **Practice — Confirm tracing is a Boutique config, not a sidecar mesh**
>
> After collector health, topic 13 syncs Boutique and expects checkout logs `Tracing enabled.` There is no Istio. Architecture rejected a mesh default.

GitOps: `gitops/apps/argocd-apps/observability-application.yaml` syncs the Kustomize root `observability/`. Manual sync still applies (ADR 003).

Grafana Kustomize (`observability/grafana/kustomization.yaml`) provisions datasources plus two dashboard ConfigMaps: `dashboards/boutique-golden-signals.json` and `dashboards/slo-overview.json`. Those JSON files are topic 17 apply-on-rebuild. The Deployment and ESO `external-secret.yaml` for admin credentials are the lived Grafana pattern from topic 13.

Topic 13 also creates Cloud Monitoring SLOs in Console — that work is taught in Chapter 9 so this chapter does not smuggle burn-rate paging into “install Grafana.” Scripts `scripts/create-burn-rate-policies.sh` likewise belong to paging.

Log-based metrics under `observability/monitoring/log-based-metrics/` (checkout latency) are **Phase 9-A scaffold** until topic 17 is applied on rebuild. Availability SLIs in the lived Phase 6 used HTTPS LB metrics more than that file.

`docs/architecture/overview.md` §13 table: traces → Cloud Trace for checkout path debugging; metrics → Managed Prometheus for Grafana and SLO queries; logs → Cloud Logging for log-based metrics and triage; errors → Error Reporting. Signal ownership prevents a single team from treating every tile as an SLO.

Boutique tracing env (from `gitops/apps/boutique/values.yaml`): `ENABLE_TRACING` / `COLLECTOR_SERVICE_ADDR` / `OTEL_SERVICE_NAME` via `global.tracing`. Topic 13 expects `kubectl -n boutique logs deploy/checkoutservice` to show `Tracing enabled.` after sync. NetworkPolicy `boutique-allow` must permit OTLP to `otel-collector.observability.svc:4317`. If that allow is missing, HTTP 200 continues and traces vanish — another Ready-looking failure.

## 4. Test the design under failure

### Independent control failure — Collector down, shop still 200

> **Practice — Diagnose a blind control plane**
>
> Architecture §10: monitoring pipeline down → blind spots; detection is missing metric heartbeat; mitigation OTel HPA and Cloud Logging fallback.

**Severity:** medium (shop up) to high (undetected checkout burn).  
**Plausible harm:** SLO no-data; on-call believes silence is health; error budget is not computed.  
**Potential blast radius:** all SLI consumers; PagerDuty never fires.  
**Bounded by:** Cloud Logging still receiving stdout; external uptime checks (Chapter 9) that do not depend on the collector.  
**Primary principles:** Lived evidence beats scaffold; Git is the deploy authority (collector config in Git).

#### Diagnosis

User journeys can succeed while telemetry fails. That is why uptime checks and LB-based browse SLIs matter. It is also why collector health is operability, not the browse SLO.

#### Correction

Keep OTLP export in Git. Alert on pipeline heartbeat as a **ticket-class** signal if you add one — do not replace checkout burn with “collector CPU.” Use Cloud Logging if GMP is silent.

That correction changes later decisions:

- Chapter 9 must not page only on Grafana.
- Chapter 10’s playbook still `curl`s the storefront.
- Topic 17 dashboards on rebuild are triage, still not budget.

## 5. Production reality

### Common errors

#### `kubectl create namespace observability` without the tier label

Kyverno `require-netpol-labels` denies or leaves the namespace non-compliant. Topic 13 warns to use Argo `managedNamespaceMetadata` or `observability/namespace.yaml`.

#### Grafana admin Secret in Git

Kyverno `block-plain-secrets` exists because that pattern returns. GSM + ESO is the path in `observability/grafana/README.md`.

#### Treating Cloud Trace as the checkout SLO

Traces debug PlaceOrder spans (`assets/diagrams/cloud-trace-checkout.png` when live). The SLO is a ratio or distribution in Cloud Monitoring. Empty traces with healthy checkout is possible if sampling or NetworkPolicy blocks OTLP.

#### Enabling kube-prometheus-stack and ignoring GMP export

`observability/README.md` names both. SLO queries in this platform target Cloud Monitoring / GMP, not a forgotten in-cluster Prometheus that nobody pages from.

## 6. What changed

| Before | After |
| --- | --- |
| Logs only. | OTLP → collector → Trace + GMP. |
| Dashboards as the program. | Grafana is triage; SLOs are Chapter 9. |
| Collector JSON keys. | Workload Identity on `otel-collector`. |
| Topic 17 dashboards assumed lived. | JSON is apply-on-rebuild. |

## 7. What You Learned

Topic 13’s stack deploys OTel Collector, Prometheus/GMP integration, and Grafana via GitOps, with Workload Identity and ESO. Boutique emits OTLP to the collector. Dashboards help humans. Error budget still comes from Cloud Monitoring SLOs in the next chapter. Phase 9-A dashboard JSON is apply-on-rebuild.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Stack index | `observability/README.md` | Layout and data flow |
| Collector | `observability/otel/collector/` | OTLP → Trace/GMP |
| Grafana | `observability/grafana/` | Datasources; dashboards (9-A) |
| Prometheus values | `observability/prometheus/` | kube-prometheus-stack Helm values |
| Setup 13 (stack) | `docs/setup/13-observability-slos.md` | Lived install steps |
| Observability app | `gitops/apps/argocd-apps/observability-application.yaml` | GitOps sync of the stack |

> **Independent Practice — Classify each backend**
>
> For Cloud Trace, GMP, Cloud Logging, Grafana, and Error Reporting:

1. Which user journey fails if that backend is down?
2. Which is adjacent (helps debug) vs accepted SLI source per catalog Chapter 9?
3. What would falsify “Grafana is healthy so checkout is healthy”?
4. Should a Grafana outage be SEV1? Why or why not?

Do not put cluster CPU on the SLO catalog because it is easy to graph.

You can demonstrate this chapter when you can trace OTLP from Boutique values to collector exporters, name which backend SRE owns versus platform, and refuse Grafana uptime as browse success. Topic 13 smoke of collector pods is mechanism evidence. Topic 17 dashboard JSON is still apply-on-rebuild. Empty traces with HTTP 200 is a NetworkPolicy or WI failure, not a passing SLO.

**Figure 8.1 — Inactive.** Grafana boutique dashboard with live pod metrics on the lived pilot.

![Grafana boutique dashboard](https://raw.githubusercontent.com/btilki/boutique-gke-sre/main/assets/diagrams/grafana-boutique-dashboard.png)

Source: `assets/diagrams/grafana-boutique-dashboard.png`. A green Grafana is not a browse SLO.
