# 12. Treat Runbooks as Product, Not Wiki Pages

A page without a matching runbook trains on-call to improvise. A runbook that does not match the alert name is a wiki page with a YAML costume. The production question is:

> How does every alert policy resolve to a reviewed runbook URL, and how does **CI (Continuous Integration)** refuse drift?

All files under `docs/sre/runbooks/` listed in the repo index, `observability/monitoring/runbooks.yaml`, and `make runbook-lint` (`scripts/validate-runbook-links.sh` in `.github/workflows/ci.yml`) are the product. Latency runbooks are **repo-ready / apply on rebuild** with topic 17.

## 1. An unsafe starting state: tribal steps in a doc nobody links

Alerts fire with empty documentation. Someone pastes kubectl into Slack. A year later Redis restore is in a private notebook. CI does not know the registry exists. Game day 03’s restore gap — BA not mentioned — is what happens when the runbook is thinner than the failure.

`docs/sre/runbooks/README.md` contract: **one runbook per Cloud Monitoring alert policy**. Notifications must include the runbook URL.

## 2. The production model: registry, lint, per-alert procedures, DR extras

> *Theory — Runbooks as versioned product*
>
> This model enables a page to open a GitHub blob URL that CI has verified still exists and still maps from the policy name — so on-call does not search a wiki during SEV2.

### Registry is the source of truth for URLs

`observability/monitoring/runbooks.yaml` binds policy names to filenames, flags `pagerduty: true`, and states GitHub blob URLs are the notification payload source of truth (public, no auth).

Alert-linked:

| Policy | Runbook | Phase honesty |
| --- | --- | --- |
| `browse-availability-burn` | `browse-availability-burn.md` | Lived 6–7 |
| `checkout-availability-burn` | `checkout-availability-burn.md` | Lived 6–7 |
| `browse-latency-burn` | `browse-latency-burn.md` | 17 / A apply-on-rebuild |
| `checkout-latency-burn` | `checkout-latency-burn.md` | 17 / A apply-on-rebuild |
| `uptime-check-failed` | `uptime-check-failed.md` | Lived 6–7 |
| `bad-deploy-rollback` | `bad-deploy-rollback.md` | Lived 5–7 |
| `redis-cart-down` | `redis-cart-down.md` | Lived 7; BA gap documented in postmortem |

DR runbooks **not** in the pager registry: `redis-restore.md`, `cluster-rebuild.md`. They are invoked from other runbooks and from teardown. Operations runbook `docs/operations/operations-runbook.md` is also listed in the YAML as non-alert-linked.

### Lint in CI

`.github/workflows/ci.yml` and `release.yml` run `./scripts/validate-runbook-links.sh`. `make runbook-lint` is the local alias. Screenshot `runbook-lint-success.png` is inactive mechanism evidence. A PR that adds an alert policy without a file, or a file without a registry row, should fail merge.

**Best Practice:** Put policy name, SLO link, and initial triage that includes a **user-visible** check in every alert runbook.

**Production Practice:** `uptime-check-failed.md` already notes inactive DNS after teardown — empty `dig` is not a live SEV. Runbooks must age with the platform state.

## 3. How this repository implements it

> **Practice — Open every alert-linked runbook’s first triage step**
>
> Confirm none of them start with “check if the cluster is Ready” as success.

- `browse-availability-burn.md`: `curl -I` storefront, SLO console, frontend pods, Ingress/Armor.
- `checkout-availability-burn.md`: checkout SLO, PlaceOrder logs, Trace, `checkoutservice` pods, log-based metrics; common causes include Redis and downstream gRPC.
- `browse-latency-burn.md`: `time_total` curl, LB latency, HPA/PDB, Grafana topic 17 if available, recent Argo sync; diagnostic tree splits slow vs availability burn.
- `checkout-latency-burn.md`: checkout path p95 vs catalog 1000ms (pair file in the same directory).
- `uptime-check-failed.md`: which check fired; `dig`/`curl` both edges; do not assume total storefront loss if only Argo failed.
- `bad-deploy-rollback.md`: curl + Argo health; last good digest in `values-images.yaml`; Git revert + manual sync (matches `docs/operations/rollback.md`).
- `redis-cart-down.md`: Redis pods, cartservice logs, add-to-cart test; mitigate restart/scale; restore via `redis-restore.md`. Postmortem says BA + scale-to-zero was missing at exercise time — treat the postmortem as errata until the runbook is updated (action still Open in the 2026-07-04 doc).

`browse-latency-burn.md` diagnostic tree (topic 17): high LB latency with healthy pods → upstream + Trace; Pending/OOM → capacity; recent deploy → bad-deploy-rollback; availability also burning → browse-availability-burn. Fast burn pauses non-critical deploys if budget is falling — that sentence is the bridge to Chapter 13.

> **Practice — Distinguish DR from paging**
>
> `redis-restore.md`: scale down cartservice, restore volume from GKE Backup, smoke cart. `cluster-rebuild.md`: terraform apply, bootstrap Argo, sync policies, sync apps, verify HTTPS. Neither is a CPU alert.

CI wiring from `.github/workflows/ci.yml`:

```yaml
      - name: Runbook link lint
        run: ./scripts/validate-runbook-links.sh
```

The same script runs in `release.yml`. `ci.yml` also terraform-validates, Kyverno-tests, and digest-checks — runbook lint is a peer of those gates, not a docs afterthought.

`checkout-latency-burn.md` (topic 17) triage already names Trace PlaceOrder spans, log-based `boutique/checkout_latency`, and a diagnostic tree: payment/cart dominant vs Redis vs empty metric extractor vs recent digest. That tree is what “product” looks like. `redis-cart-down.md` at exercise time was shorter and omitted BA — the postmortem is the quality backlog.

GUIDE_TEMPLATE.md / DOCUMENTATION.md define structure. Some runbooks are still short (“Full steps expanded in Phase 7”). Honesty: product quality is uneven; lint proves **linkage**, not that every tree is complete. Lived GD03 proved incompleteness is user-visible.

Complete inventory from `docs/sre/runbooks/README.md`: four burn runbooks (two lived availability, two latency apply-on-rebuild), `uptime-check-failed.md`, `bad-deploy-rollback.md`, `redis-cart-down.md`, plus DR `redis-restore.md` and `cluster-rebuild.md`. Operations runbook `docs/operations/operations-runbook.md` is linked from the YAML `operations_runbook` key for PagerDuty custom details, not as a seventh burn policy.

## 4. Test the design under failure

### Independent control failure — Policy without registry row

> **Practice — Diagnose a black-hole page**
>
> A new `checkout-availability-burn` clone is created in Console. PagerDuty fires. Documentation field is empty. On-call greps Slack.

**Severity:** high during the incident; medium as process.  
**Plausible harm:** wrong runbook; delayed TTR; freeze never considered.  
**Potential blast radius:** every future policy created only in Console.  
**Bounded by:** runbook-lint; topic 13/17 scripts that read `runbooks.yaml`.  
**Primary principles:** Git is the deploy authority; Lived evidence beats scaffold; CI never deploys (CI still **gates** docs).

#### Diagnosis

Console is convenient. It does not update `runbooks.yaml`. Dual path (scripts vs ClickOps) needs the registry or drift is guaranteed.

#### Correction

Add file + registry row + policy documentation URL in the same PR. Run `make runbook-lint`. Do not declare SRE complete because Grafana exists.

That correction changes later decisions:

- Chapter 13 toil includes keeping lint green.
- Chapter 14 game days must name the runbook they exercise.
- Topic 17 cannot add latency burns without the two latency runbooks (already in Git as scaffold).

## 5. Production reality

### Common errors

#### Creating policies only in Console

CI `validate` job runs `./scripts/validate-runbook-links.sh`. Console-only policies never join `runbooks.yaml`. Black-hole pages follow.

#### Latency runbooks missing because “topic 17 is later”

The files already exist: `browse-latency-burn.md`, `checkout-latency-burn.md`. Lint should already include them. Apply-on-rebuild is the Cloud Monitoring objects, not an excuse to skip Git.

#### DR runbooks expected to page

`redis-restore.md` and `cluster-rebuild.md` are invoked from other runbooks and teardown. They are not in the `policies:` map. Do not invent a fake alert for rebuild.

#### Treating lint green as runbook completeness

GD03: `redis-cart-down.md` was linked and still omitted BA recreate. Lint checks names and URLs. Humans still review triage trees. `checkout-latency-burn.md` diagnostic tree (payment vs Redis vs metric extractor) is the quality bar.

#### Uptime runbook paging after teardown

`uptime-check-failed.md` lab note: empty `dig` is expected offline. Product quality includes aging with platform state.

## 6. What changed

| Before | After |
| --- | --- |
| Wiki steps in Slack. | One file per policy under `docs/sre/runbooks/`. |
| URLs optional. | `runbooks.yaml` + CI lint. |
| Rollback folklore. | `bad-deploy-rollback.md` matches `docs/operations/rollback.md`. |
| Redis restore = scale. | Postmortem errata: BA attestation required. |

## 7. What You Learned

Runbooks are a product: one per page, URLs in a registry, CI lint, DR documents off to the side. Lint is mechanism evidence. GD03 showed a linked runbook can still omit the restore prerequisite that actually bit. Update the product when the game day does.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Index | `docs/sre/runbooks/README.md` | Complete list |
| Nine runbooks | `docs/sre/runbooks/*.md` | Alert + DR procedures |
| Registry | `observability/monitoring/runbooks.yaml` | Policy → file |
| Lint | `scripts/validate-runbook-links.sh`, `ci.yml` | Merge gate |
| Operations runbook | `docs/operations/operations-runbook.md` | Non-alert-linked ops |

> **Independent Practice — Patch the Redis runbook from the postmortem without inventing a cluster**
>
> Postmortem P1: document BA + scale-to-zero in `redis-cart-down.md`.

1. Where in Initial triage would you detect BA deny (events vs logs)?
2. What mitigation is scale vs DRYRUN vs sign-and-redeploy?
3. Which principle forbids leaving DRYRUN on after the exercise?
4. What `make runbook-lint` would **not** catch about this gap?

Your durable output is the reasoning. Do not modify the boutique-gke-sre repository from this book’s workspace.

Also decide whether `redis-restore.md` should be linked from the Redis-down runbook’s Mitigation step (it already is) and whether a page should ever open `cluster-rebuild.md` directly. Rebuild is DR, not a burn policy. A SEV1 that lasts hours might escalate there — say when, in one sentence, without making rebuild a seventh SLO.

You can demonstrate this chapter when you can name all nine runbook files, show the registry row for a given policy, and explain what lint proves versus what GD03 proved.

**Figure 12.1 — Inactive.** `make runbook-lint` success on the lived CI path.

![runbook-lint success](https://raw.githubusercontent.com/btilki/boutique-gke-sre/main/assets/diagrams/runbook-lint-success.png)

Source: `assets/diagrams/runbook-lint-success.png`. Lint proves URLs resolve in Git; it does not prove a journey recovered.

`docs/sre/runbooks/browse-availability-burn.md` starts with storefront `curl`, not kubelet Ready. That first triage line is the Chapter 1 refusal encoded as an operator step.
