# 9. Page on Burn Rate, Not on Every Symptom

Chapter 8 made journeys visible. Visibility without policy pages on every red tile. The production question is:

> Which **SLOs (Service Level Objectives)** exist, how does multi-window burn page versus ticket, and why is an uptime check not browse success?

Setup topic **13** SLO/alert half (**Lived**), topic **17** (**repo-ready / apply on rebuild**), `docs/sre/slos/catalog.md`, `burn-rate-alerting.md`, `observability/monitoring/slos/`, `observability/monitoring/alert-policies/`. PagerDuty attach is Chapter 10; this chapter defines what is worth paging.

## 1. An unsafe starting state: page on CPU, Ready, and raw 5xx

CPU high pages. Replica Ready pages. A single 5xx in five minutes pages. Checkout latency never pages. Remaining error budget is a dashboard curiosity. Google’s multi-window burn exists because a short window false-pages and a long window misses fast outages.

`docs/sre/slos/catalog.md` common mistakes: SLO on a lagging indicator only; missing runbook URL on the alert policy. Those are this chapter’s refusals.

## 2. The production model: journey SLIs, budgets, multi-window burn

> *Theory — SLO burn-rate paging*
>
> This model enables on-call to wake on consumption of browse and checkout error budget rather than on every symptom that happens to have a metric.

### Catalog

From `docs/sre/slos/catalog.md`:

| Journey | SLI | Target | Window |
| --- | --- | --- | --- |
| Browse | Successful HTTP / total to frontend | **99.9%** | 30-day rolling |
| Browse | p95 duration | **&lt; 500ms** | 30-day rolling |
| Checkout | Successful completions / attempts | **99.95%** | 30-day rolling |
| Checkout | p95 checkout path | **&lt; 1000ms** | 30-day rolling |

Browse journey: home, product browse, cart view (pre-checkout). Checkout journey: place order via `checkoutservice`.

Approximate monthly error budget: 99.9% ≈ 43.2 minutes; 99.95% ≈ 21.6 minutes. Policy that consumes those minutes is Chapter 13.

Availability SLOs were created in lived topic 13 (HTTPS LB / custom metrics). Latency SLOs, log-based `boutique/checkout_latency`, and `*-latency-burn.yaml` are topic **17 apply on rebuild**. Do not pretend latency burn paged in production after teardown.

### Burn windows

`docs/sre/slos/burn-rate-alerting.md`:

| Window | Multiplier | Response |
| --- | --- | --- |
| 1h | 14.4× | Page |
| 6h | 6× | Page |
| 1d | 3× | Ticket |
| 3d | 1× | Ticket (slow burn) |

Cloud Monitoring API maximum lookback is **24 h**. The catalog’s 3d/1× becomes a 24h/1× approximation in `scripts/create-burn-rate-policies.sh`. That limit is recorded in `browse-availability-burn.yaml` comments — not hidden.

**Best Practice:** Combine short and long windows (AND in the SRE workbook sense; this repo’s YAML uses combiner OR per condition list with distinct page vs ticket responses — read the policy file, do not assume AND).

Lived `observability/monitoring/alert-policies/browse-availability-burn.yaml`:

```yaml
displayName: browse-availability-burn
combiner: OR
userLabels:
  runbook: browse-availability-burn
  slo: browse-availability
documentation:
  runbook: https://github.com/btilki/boutique-gke-sre/blob/main/docs/sre/runbooks/browse-availability-burn.md
```

Every page must have a runbook URL. Registry: `observability/monitoring/runbooks.yaml`. Lint: `make runbook-lint`.

### Uptime is adjacent

`uptime-check-failed` probes `boutique.biroltilki.art` (and later `argocd-ui` in topic 18). It is a synthetic. It can page when DNS/TLS/LB dies. It is **not** the browse availability SLO. A shop that returns 200 on `/` and fails checkout can burn checkout while uptime stays green.

**Production Practice:** Do not use the same burn multiplier for browse and checkout. Budgets differ.

## 3. How this repository implements it

> **Practice — Map every page to a runbook**
>
> Open `docs/sre/slos/catalog.md` alert table and `observability/monitoring/runbooks.yaml`.

Policies: `browse-availability-burn`, `checkout-availability-burn`, `browse-latency-burn`, `checkout-latency-burn`, `uptime-check-failed`, `bad-deploy-rollback`, `redis-cart-down`. Latency pair is 9-A. `argocd-ui` uptime YAML is 9-B.

> **Practice — Distinguish lived topic 13 from topic 17**
>
> Topic 13: availability SLOs + burn scripts + uptime check + runbook URLs. Topic 17: latency SLOs, `scripts/create-latency-burn-rate-policies.sh`, Grafana golden-signal JSON. ROADMAP labels 17 **Repo ready (apply on rebuild)**.

SLO YAML lives in `observability/monitoring/slos/` (`browse-latency.yaml`, `checkout-latency.yaml` for 9-A; availability created in Console/API during lived 13). Screenshot `assets/diagrams/slo-browse-checkout.png` is inactive mechanism evidence.

Topic 13 validation `gcloud monitoring slos list` only works on a live project. Reading the catalog in Git is the offline practice.

Lived browse-latency file (apply on rebuild) states the contract:

```yaml
displayName: browse-latency
goal: 0.95
rollingPeriod: 2592000s # 30 days
# good = latency ≤ 500ms on HTTPS LB total_latencies
```

Replace `url_map_name` after Ingress exists. Do not page on a placeholder filter.

`scripts/create-uptime-check.sh` is the lived imperative path. Topic 19 Terraform `module.monitoring` can recreate uptime checks when `enable_monitoring_iac=true` on rebuild — dual path, avoid duplicate checks.

Alert → runbook mapping in the catalog includes `bad-deploy-rollback` and `redis-cart-down` beside the four burn policies. Those are symptom-adjacent pages that still must link runbooks. They must not replace browse/checkout burn as the program.

## 4. Test the design under failure

### Cumulative reliability failure — Symptom pages, budget ignored

> **Practice — Diagnose alert fatigue that never freezes change**
>
> Node CPU pages at 02:00. Checkout fast burn is a Grafana panel. Error-budget policy never sees a page, so digest PRs continue.

**Severity:** high; on-call learns to ignore pages; checkout budget dies quietly.  
**Plausible harm:** users fail PlaceOrder while heroes reboot nodes.  
**Potential blast radius:** all Boutique services; freeze never declared.  
**Bounded by:** catalog mapping; runbook-lint; error-budget policy (Chapter 13).  
**Primary principles:** Lived evidence beats scaffold; Git is the deploy authority (policy YAML in Git).

#### Diagnosis

Paging on symptoms is easy because kube-state metrics exist. Burn requires an SLO object and a remaining-budget definition. Without that object, Chapter 13 has nothing to freeze.

#### Correction

Page 1h/6h burn on browse and checkout availability (lived). Add latency burn on rebuild (topic 17). Keep CPU as a dashboard. Ticket slow burn. Attach runbook URLs.

That correction changes later decisions:

- Chapter 10 routes these policies to PagerDuty, not email-only.
- Chapter 12 runbooks must exist for each policy name.
- Chapter 14 game day 04 would prove the path — **Deferred**.

## 5. Production reality

### Common errors

#### Alerting on raw 5xx without an SLO object

`burn-rate-alerting.md` common mistake: alerting on a raw metric. Burn needs the SLO so remaining budget is defined.

#### Same multiplier for browse and checkout

Checkout budget is tighter (99.95% vs 99.9%). Copy-pasting 14.4× without reading the catalog treats them as one journey.

#### Documentation URL pointing at a wiki, not GitHub blob

`runbooks.yaml` says public blob URLs are the payload source of truth. On-call at 03:00 cannot open a private Confluence during a page.

#### Assuming 3-day lookback exists in the API

Comments in `browse-availability-burn.yaml`: max 24h. The catalog’s 3d/1× is approximated. Pretending otherwise makes slow-burn tickets a fiction.

#### Latency YAML as lived Phase 6

`observability/monitoring/slos/browse-latency.yaml` is topic 17. It even contains a rebuild note to replace `url_map_name` after Ingress exists. Placeholder url_map names must not be treated as current production.

## 6. What changed

| Before | After |
| --- | --- |
| CPU and Ready pages. | Browse/checkout burn with runbook URLs. |
| Uptime check as the SLO. | Uptime adjacent; catalog is user journeys. |
| Latency undocumented. | Latency files ready; apply on rebuild. |
| Silent Console policies. | Registry + `make runbook-lint`. |

## 7. What You Learned

SLOs protect browse and checkout, not cluster Ready. Multi-window burn pages on fast consumption and tickets on slow consumption. Every alert policy names a runbook. Latency SLOs and extra Grafana dashboards are apply-on-rebuild. Uptime checks are adjacent synthetics.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Catalog | `docs/sre/slos/catalog.md` | Journeys, targets, mappings |
| Burn model | `docs/sre/slos/burn-rate-alerting.md` | Windows and API limit |
| Policies | `observability/monitoring/alert-policies/` | Lived + 9-A YAML |
| Registry | `observability/monitoring/runbooks.yaml` | URL source of truth |
| Setup 13/17 | `docs/setup/13-observability-slos.md`, `17-latency-slos-dashboards.md` | Lived vs apply-on-rebuild |

> **Independent Practice — Reject a proposed “pod restart SLO”**
>
> A teammate wants 99.9% pods Ready as a third SLO.

1. Who is the user when a restart happens without checkout errors?
2. Would remaining budget freeze digest promotion? Should it?
3. Where does `bad-deploy-rollback` already cover restarts?
4. What adjacent dashboard would you offer instead of a new SLO?

You can demonstrate this chapter when you can explain why Argo UI uptime is not checkout, why 24h is the API cap on slow burn, and which topic 17 files are still scaffold.

**Figure 9.1 — Inactive.** Browse and checkout SLO dashboard from the lived Monitoring API view.

![SLO browse and checkout](https://raw.githubusercontent.com/btilki/boutique-gke-sre/main/assets/diagrams/slo-browse-checkout.png)

Source: `assets/diagrams/slo-browse-checkout.png`. DNS is inactive; this is not a live SLO.

## Further reading

Playbook article **G1** is the short public argument for SLOs, burn-rate alerts, PagerDuty, and runbooks.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/G1.md
