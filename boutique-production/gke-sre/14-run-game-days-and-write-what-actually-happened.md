# 14. Run Game Days and Write What Actually Happened

A game-day folder full of guides is not a reliability program. The production question is:

> Which failure exercises exist, which one actually ran, and what did 2026-07-04 prove versus what STATUS still refuses to claim?

Setup topic **18** is **repo-ready / apply on rebuild**. Guides 01–04, `docs/sre/game-days/reports/STATUS.md`, the Redis report and postmortem, `scripts/game-days/`, and HPA/PDB templates are in Git. **Only game day 03 was executed.** PagerDuty was **not** verified. Binary Authorization **blocked restore**.

## 1. An unsafe starting state: STATUS green without a dated report

`docs/sre/game-days/reports/STATUS.md` rule:

> Do **not** mark a scenario executed without a dated report under this directory.

The unsafe default is to tick 01–04 because YAML exists. That is a false claim. Recurring book principle: game-day STATUS without a dated report is a false claim.

## 2. The production model: inject, observe journeys, restore, write, promote gaps

> *Theory — Honest game-day evidence*
>
> This model enables the team to treat a dated report as the only execution proof, and a postmortem as the promotion path when restore surprises appear — rather than a checklist of intended chaos.

### Four scenarios

`docs/sre/game-days/README.md` and STATUS:

| # | Scenario | Script / method | Status |
| --- | --- | --- | --- |
| 01 | Bad deploy rollback | Git revert + manual Argo sync | **Deferred** — needs live cluster |
| 02 | Zone / pod failure | `scripts/game-days/inject-pod-failure.sh` | **Deferred** — needs live cluster; PDB/HPA credibility |
| 03 | Redis / cart down | `scripts/game-days/inject-redis-down.sh` | **Executed** 2026-07-04 |
| 04 | Alert routing | `docs/sre/oncall/test-alerts.md` | **Deferred** — needs live cluster + PagerDuty |

After each run: copy `reports/TEMPLATE.md` → dated file; update STATUS; postmortem from `postmortems/TEMPLATE.md` if gaps warrant. GD03 warranted one.

### HA GitOps is a prerequisite for GD02, not a trophy

Topic 18: sync HPA/PDB. `gitops/apps/boutique/templates/hpa.yaml` and `pdb.yaml` render from values. Capacity baseline: frontend/checkout HPA min 2; cartservice 2; **redis-cart Ready 1**. Until those are synced on a rebuilt cluster, game day 02 is theater. Files in Git today are **scaffold** relative to the torn-down cluster.

Argo CD uptime check (`observability/monitoring/uptime-checks/argocd-ui.yaml`, `scripts/create-argocd-uptime-check.sh`) is also topic 18 apply-on-rebuild. It is operability, not a user-journey SLO.

**Best Practice:** Time-box injects; require `CONFIRM=yes` on destructive scripts.

**Production Practice:** Prefer GD04 (routing) before chaotic injects on rebuild — topic 18 suggested order. GD03 historically ran without that proof.

## 3. How this repository implements it — including the lived Redis day

> **Practice — Read STATUS before any guide**
>
> Open `docs/sre/game-days/reports/STATUS.md`. Three deferred, one executed with gaps.

`scripts/game-days/inject-redis-down.sh`:

```bash
if [[ "${CONFIRM}" != "yes" ]]; then
  echo "Refusing to run without CONFIRM=yes"
  exit 1
fi
kubectl scale deployment "${REDIS_DEPLOY}" -n "${NAMESPACE}" --replicas=0
```

Restore comment in the script is `kubectl scale ... --replicas=1`. The lived report shows that was **insufficient** under BA enforce.

> **Practice — Read the report and the postmortem as a pair**
>
> `docs/sre/game-days/reports/2026-07-04-redis-cart-down.md` and `docs/sre/postmortems/2026-07-04-redis-cart-down.md`.

Facts (UTC, 2026-07-04):

| Time | Event |
| --- | --- |
| 18:30 | Baseline: redis-cart 1/1, storefront HTTP 200, BA `ENFORCED_BLOCK_AND_AUDIT_LOG` |
| 18:31 | Inject `CONFIRM=yes ./scripts/game-days/inject-redis-down.sh` |
| 18:31 | Storefront **HTTP 500**; redis-cart 0/0 |
| 18:31–18:33 | `kubectl scale --replicas=1` — new pod **denied by BA** (no cosign attestation on `boutique/redis-cart@sha256:18e7e25…`) |
| 18:37 | Terraform BA `DRYRUN_AUDIT_LOG_ONLY`; rollout restart; pod 1/1 |
| 18:38 | Storefront HTTP 200; BA re-enforced |

**TTD:** immediate (synthetic curl + deployment status). **TTR:** ~7 minutes including BA workaround. **PagerDuty / `redis-cart-down` alert: not verified.** User impact: browse and checkout path broken — 5xx while cart backend was down. That is journey evidence, not cluster NotReady.

Blameless framing in the postmortem: policy worked as designed. Gap was operational readiness (signed images + runbook coverage), not “BA misconfiguration.” Action items (sign redis-cart, document BA in runbook, restore fallback in GD03 guide, re-run with PD ack) were **Open** in the committed postmortem.

Infrastructure was decommissioned **the same calendar day**. There was no second run.

`docs/sre/game-days/01-bad-deploy-rollback.md` injects a documented non-fatal misconfig via PR → merge → **manual** sync — not a random unsigned image. `02-zone-pod-failure.md` uses `CONFIRM=yes NAMESPACE=boutique DEPLOYMENT=frontend ./scripts/game-days/inject-pod-failure.sh`. `04-alert-routing.md` is the PD path using `test-alerts.md`. None of those three have dated reports. STATUS Notes for 03 already say “PD/alert not verified; BA blocked restore.”

HPA template (`gitops/apps/boutique/templates/hpa.yaml`) emits `autoscaling/v2` objects only when `.Values.services.*.autoscaling.enabled`. PDB template similarly. Until topic 18 syncs them on a live cluster, quoting the templates as “HA validated” is scaffold.

`reports/TEMPLATE.md` requires date, scenario link, baseline `curl`, inject command, timeline, TTD/TTR, what went well/poorly, and action items. STATUS without that file is Deferred. GD03 filled it and then promoted gaps to `postmortems/2026-07-04-redis-cart-down.md`.

## 4. Test the design under failure

### Independent control failure — Calling GD03 a passed on-call drill

> **Practice — Separate journey proof from page-path proof**
>
> STATUS notes: “PD/alert not verified; BA blocked restore.” Marking 03 as “SRE complete” would hide both.

**Severity:** high as a governance failure (false confidence).  
**Plausible harm:** rebuild skips signing Redis; next inject repeats 6 minutes of 5xx plus DRYRUN; on-call app never tested.  
**Potential blast radius:** checkout SLO; BA trust (if DRYRUN left on); the STATUS table as an organizational lie.  
**Bounded by:** STATUS definitions (Executed vs Deferred vs Partial); postmortem required when restore surprises appear.  
**Primary principles:** Lived evidence beats scaffold; Identity is digest, not tag; Git is the deploy authority.

GD03 is **Executed** with known gaps — closer to STATUS’s **Partial** spirit, but the table honestly says Executed and documents the gaps in Notes. Do not “upgrade” it to clean.

#### Diagnosis

HTTP 500 proved Redis is on the browse/checkout path (frontend returned 5xx, not a quiet cart-empty). That is valuable. It did not prove burn policies, PagerDuty, or runbook BA steps. HPA/PDB were not the exercise. GD01/02/04 remain deferred.

#### Correction

Keep STATUS honest. On rebuild: sign images first, apply topic 18 HA, run GD04, then re-run GD03 with PD ack. Write a new dated report; do not edit 2026-07-04 into a success.

That correction is the chapter.

## 5. Production reality

### Common errors

#### Marking GD01 executed because rollback.md exists

STATUS definitions: Executed means live inject (or approved tabletop) **with dated report committed**. Guide ≠ report.

#### Running GD02 before HPA/PDB sync

Topic 18: without multi-replica credibility, zone/pod failure is theater. `inject-pod-failure.sh` will recreate a single replica and teach the wrong lesson.

#### Editing the 2026-07-04 report to hide BA

The postmortem exists because restore surprised the team. Cleaning the report would violate lived evidence beats scaffold.

#### Counting HTTP 500 as “cluster failed”

Nodes stayed Ready. The journey failed. That is the point of Chapter 1.

#### Skipping CONFIRM=yes by editing the script

The gate is there because the inject is user-visible 5xx. Circumventing it is how game days become unplanned incidents.

#### Declaring HA because `templates/hpa.yaml` renders locally

`helm template | rg HorizontalPodAutoscaler` is mechanism evidence. Game day 02 is still deferred.

## 6. What changed

| Before | After |
| --- | --- |
| Four guides implied four successes. | STATUS: 01/02/04 deferred; 03 executed with gaps. |
| Restore = scale Redis. | Recreate under BA needs attestation or time-boxed DRYRUN. |
| PD assumed because topic 14 existed. | PD not verified on GD03. |
| HPA/PDB claimed. | Apply on rebuild (topic 18). |

## 7. What You Learned

Game days are only real with dated reports. Only GD03 ran (2026-07-04). It proved user-visible 5xx when Redis scaled to zero, and that BA enforce turns scale-to-zero into a recreate that needs attestations. It did not verify PagerDuty. GD01, GD02, and GD04 are deferred. HPA/PDB and Argo uptime are apply-on-rebuild. Cluster Ready was never the success criterion — HTTP 200 vs 500 on the storefront was.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| STATUS | `docs/sre/game-days/reports/STATUS.md` | Honesty gate |
| Report | `docs/sre/game-days/reports/2026-07-04-redis-cart-down.md` | Lived timeline |
| Postmortem | `docs/sre/postmortems/2026-07-04-redis-cart-down.md` | BA restore lesson |
| Guides 01–04 | `docs/sre/game-days/` | Including deferred |
| Scripts | `scripts/game-days/` | CONFIRM=yes injects |
| HA templates | `gitops/apps/boutique/templates/hpa.yaml`, `pdb.yaml` | Topic 18 |
| Setup 18 | `docs/setup/18-sre-operability-game-days.md` | Apply path |

> **Independent Practice — Draft STATUS notes for a hypothetical GD02**
>
> You deleted one frontend pod. Storefront stayed 200. You did not drain a zone. PD did not fire (no burn).

1. Is that Executed, Partial, or still Deferred if you forgot the dated report?
2. Does HTTP 200 prove PDBs across zone loss?
3. What would you refuse to write in README.md about “HA validated”?
4. Which SLO would you watch if you **did** drain a node?

Do not backfill dates. If it did not happen, it is Deferred.
