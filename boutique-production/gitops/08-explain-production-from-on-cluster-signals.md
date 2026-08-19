# 8 — Explain Production From On-Cluster Signals

A storefront that is “up” in Argo **CD (Continuous Delivery)** can still be invisible to operators if metrics live in a billing account nobody opens. CloudWatch-plus-PagerDuty is a valid design. It is not this pilot’s design. Topic 08 is **M2 (Milestone 2)** together with Topics 06–07: Grafana reachable, a test critical alert in email.

> How do you explain Boutique and platform health from Prometheus, Loki, Grafana, and Alertmanager on the same cluster — without outsourcing the signal path or pretending traces exist?

## 1. The unsafe starting state: GitOps without a story

After Topic 07, admission works and SMTP *can* be delivered. If you skip observability, the first prod incident is a user tweet. If you add CloudWatch Logs ingestion, the cost model is already false. If you page a vendor on a two-day pilot, you will debug the vendor.

ADR-0005 forbids CloudWatch, PagerDuty, and **OTel (OpenTelemetry)** in v1. `docs/architecture/09-observability.md` scopes metrics, logs, email alerts, and the explicit “no traces.”

**Lived** as M2. After teardown, Grafana at `grafana.boutique.biroltilki.art` is **inactive**. The values and PrometheusRule remain.

## 2. The production model: on-cluster RED-enough, email for critical

> *Theory — Self-operated signal path*
>
> Keep metrics, logs, and alert routing on the cluster so cost and failure domains match the pilot; prove the email path once; disable the always-firing test rule; do not confuse dashboard presence with a shop SLO.

```3:12:docs/architecture/09-observability.md
## Scope (v1)

| Signal | Included | Tool |
|--------|----------|------|
| Metrics | Yes | Prometheus (kube-prometheus-stack) |
| Logs | Yes | Grafana Loki |
| Alerts | Yes | Alertmanager → **email** |
| Traces | **No** | OTel/Tempo deferred |
| CloudWatch | **No** | Cost |
| PagerDuty | **No** | Email instead |
```

Retention targets: Prometheus 7–15 days, Loki ~7 days. Resource caps exist because three `m6i.large` nodes (8 GiB) are a real bottleneck — `docs/architecture/08-resilience-and-dr.md` lists Prometheus/Loki memory first.

## 3. How this repository implements the stack

> **Practice — Follow SMTP from Secrets Manager to the inbox**
>
> Open `gitops/platform/monitoring/values-kube-prometheus.yaml` (Alertmanager config placeholders), `gitops/platform/monitoring/manifests/externalsecret-smtp.yaml`, and `docs/runbooks/alerting.md`. State where the password must *not* appear.

### kube-prometheus-stack and Loki

ApplicationSet wave 30 installs chart `69.8.0` with `gitops/platform/monitoring/values-kube-prometheus.yaml` and Loki chart `6.24.0`. Grafana Ingress uses the locked hostname and **ACM (AWS Certificate Manager)** on **ALB (Application Load Balancer)** — same edge as Chapter 5. **CI (Continuous Integration)** does not install this stack.

Topic 08 (`docs/setup/08-observability.md`) substitutes ACM ARN and SMTP host/user/from/to in values. The password stays in AWS Secrets Manager, synced by **ESO (External Secrets Operator)** to `alertmanager-smtp`.

### PrometheusRule: prove email, then stop the noise

```14:37:gitops/platform/monitoring/manifests/prometheusrule-boutique.yaml
spec:
  groups:
    - name: boutique.email-test
      rules:
        - alert: AlertmanagerEmailTest
          expr: vector(0)
          for: 0m
          labels:
            severity: critical
          annotations:
            summary: "Alertmanager email path test (Topic 08)"
            description: "Always-firing test alert. Delete/disable this rule after email is confirmed."
    - name: boutique.critical
      rules:
        - alert: BoutiqueIngressDown
          # Probe via kube-prometheus blackbox optional later; placeholder uses absent ingress metrics
          expr: |
            absent(kube_ingress_info{namespace="prod",ingress=~".*boutique.*"})
              and on() (vector(1) == 0)
          for: 15m
          labels:
            severity: critical
          annotations:
            summary: "Boutique ingress missing/down (prod)"
```

**Lived.** `AlertmanagerEmailTest` was fired, inbox confirmed, then set to `vector(0)` (`840c9f6` in the checklist). `BoutiqueIngressDown` remains a placeholder expression — operations `10-alerting.md` says so. Do not treat that rule as a proven blackbox probe.

### Alerting runbook

```9:25:docs/runbooks/alerting.md
## Purpose

Receive critical alerts by email. No PagerDuty in v1.

## Components

| Piece | Location |
|-------|----------|
| Alertmanager | `monitoring` namespace (kube-prometheus-stack) |
| SMTP password | AWS SM `boutique-eks-gitops/alertmanager-smtp` → ESO → Secret `alertmanager-smtp` |
| Test rule | `AlertmanagerEmailTest` in `prometheusrule-boutique.yaml` |
| Prod intent | `BoutiqueIngressDown` (enabled for real probes after Topic 09) |

## First-time email proof (Topic 08 Step 8.5)

1. Confirm Secret exists: `kubectl -n monitoring get secret alertmanager-smtp`
2. Confirm Alertmanager pods mount the secret and config has `smtp_smarthost` set
3. Ensure `AlertmanagerEmailTest` is loaded: Prometheus UI → Alerts
4. Check inbox for `<SMTP_TO>`
5. **Disable** the test rule after success
```

**Lived** as the M2 email proof. After teardown, the runbook is still the procedure for a rebuild.

Helm values keep the password out of Git and route default noise to null:

```19:35:gitops/platform/monitoring/values-kube-prometheus.yaml
alertmanager:
  enabled: true
  config:
    global:
      resolve_timeout: 5m
      smtp_smarthost: "smtp.gmail.com:587"
      smtp_from: "btilkidata@gmail.com"
      smtp_require_tls: true
      smtp_auth_username: "btilkidata@gmail.com"
      smtp_auth_password_file: /etc/alertmanager/secrets/alertmanager-smtp/password
    route:
      # Default null so EKS noise/warnings do not hammer Gmail SMTP
      receiver: "null"
      group_by: ["alertname", "severity"]
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 4h
```

**Lived** SMTP host/user in values; password file mount only. Critical routes (not shown here) must still select `severity=critical` to reach the mailbox. Default `null` is why the cluster does not spam you.

`docs/architecture/08-resilience-and-dr.md` lists observability-down as a failure: detection is Argo app unhealthy plus manual checks; recovery is re-sync the monitoring app. That is honest about a single-cluster design: when Prometheus is down, you are flying the GitOps UI and `curl`. There is no CloudWatch backup dashboard. ADR-0005 accepted that.

Retention and caps in `gitops/platform/monitoring/` exist because three `m6i.large` nodes share Boutique, Argo, Kyverno, and Loki. The cost model forbids “just add CloudWatch Logs.” If memory pressure appears, the documented vertical move is `m6i.xlarge` — a Terraform node-type change — not a silent console resize.

Operations `09-monitoring.md`, `10-alerting.md`, and `11-logging.md` are the day-2 restatement: Explore in Grafana, email route, Loki retention. `10-alerting.md` warns that `BoutiqueIngressDown` is still a placeholder. Do not page yourself from a rule that cannot fire correctly.

> **Practice — Read M2 evidence without a live Grafana**
>
> Open `docs/PRODUCTION_CHECKLIST.md` rows A11–A12. Those HTTPS 302 and pod counts are historical. State what you would re-collect on a rebuild versus what Git already proves (values, rule, runbook).

## 4. Test the design under failure

**Scenario:** SMTP secret missing; Alertmanager silently drops critical mail; shop is down.

**Severity:** operators are blind while users fail.  
**Plausible harm:** prolonged storefront outage with no email; engineers watch Argo “Healthy” because Ingress objects exist.  
**Potential blast radius:** all user traffic to `boutique.biroltilki.art` plus lost signal for platform alerts.  
**Bounded by:** ESO sync status, alerting runbook, Grafana/Prometheus UI (when live), on-cluster-only design (no second paging channel — accepted).  
**Primary principles:** teardown after the pilot is required; Git is the only deploy authority; one cluster and three namespaces are a cost decision, not isolation.

### Diagnosis

`kubectl -n monitoring get externalsecret` not SecretSynced. Alertmanager logs show auth or timeout. Inbox empty. Prometheus `/alerts` shows firing but route mismatch (`severity` not `critical`). After teardown, you diagnose from Git: if `externalsecret-smtp.yaml` is absent or password was committed to values, the design is already wrong.

### Recovery

Fix the Secret in AWS; wait for ESO refresh; do not paste SMTP passwords into Helm values. Confirm a *new* test alert, then disable it again. For shop-down, follow `docs/runbooks/ingress.md` and operations `17-common-incidents.md` — email recovery is not shop recovery. Absence of PagerDuty means email-when-online is the honest SLO (`docs/operations/01-overview.md`).

`gitops/platform/monitoring/manifests/externalsecret-smtp.yaml` is the Git-side of the password path: an ExternalSecret, not a value. If that file ever contains a password, Chapter 7 failed. Loki values under `gitops/platform/monitoring/loki/values.yaml` cap retention. Together with kube-prometheus values they are the ADR-0005 implementation.

## 5. What You Learned

Production explanation here is Prometheus + Loki + Grafana + Alertmanager email, with a proven then-disabled test rule and a placeholder shop-down alert. You can now walk Topic 08, monitoring values, the PrometheusRule, and the alerting runbook as M2.

### Durable outputs

- Setup: `docs/setup/08-observability.md`
- ADR: `docs/adr/0005-observability-on-cluster.md`
- Stack: `gitops/platform/monitoring/`
- Rule: `gitops/platform/monitoring/manifests/prometheusrule-boutique.yaml`
- Runbook: `docs/runbooks/alerting.md`
- Design: `docs/architecture/09-observability.md`

> **Independent Practice — Add a shop probe without CloudWatch**
>
> Replace the placeholder `BoutiqueIngressDown` expression with a design that uses blackbox exporter *or* ALB target metrics already in-cluster. Name the Git paths you would change, the false-positive risk, and why this still is not an **SLO (Service Level Objective)** contract. Do not add PagerDuty.

**Figure 8.1 — Inactive.** Grafana dashboards from kube-prometheus-stack on the lived pilot.

![Grafana Dashboards](https://raw.githubusercontent.com/btilki/boutique-eks-gitops/main/assets/images/setup/08-grafana-dashboards.png)

Source: `assets/images/setup/08-grafana-dashboards.png`. DNS is inactive.

M2 lived evidence in the checklist: Grafana HTTPS 302, Topic 08 email received, test rule set to `vector(0)` (`840c9f6`), `monitoring` namespace 10 pods Running. Those numbers are not a live SLO. On rebuild, prove email again, then disable the test rule again. Leaving `AlertmanagerEmailTest` firing is how you train yourself to ignore mail.

## Next

Chapter 9 pins Boutique with Helm charts and env digest overlays so Argo has something digest-shaped to deploy.
