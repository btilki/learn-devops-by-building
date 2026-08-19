# 15. Destroy ACR When You Tear Down

Leaving a registry “for next week” keeps signed images, pull costs, and a forgotten identity surface. This chapter is Setup Topic **13**: `scripts/operations/teardown.sh`, [ADR-0010](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0010-destroy-acr-on-teardown.md), and the cost model. Teardown is a production control.

The production question is:

> What must be destroyed so spend and image trust stop, and what must be kept so a rebuild does not start from folklore?

## 1. Unsafe starting state

The unsafe default is to delete the AKS cluster in the portal and keep **ACR (Azure Container Registry)** because “mirroring takes time.” ADR-0010 forbids that. The other default is to destroy Terraform bootstrap state first and lose the map to remaining disks and DNS.

Unsigned images cannot reach a cluster that is gone — but they can sit in ACR for the next accidental attach.

## 2. The production model: destroy billable trust stores, keep Git

> *Theory — Teardown as control*
>
> This model enables cost stop and image-trust stop in one destroy, while Git, public cosign PEM, and optional remote state remain the rebuild kit.

ADR-0010: Phase 14 teardown **destroys ACR** along with AKS and other billable resources. Consequence: rebuild requires Topic 09 again.

`docs/architecture/11-cost-model.md`: typical active test ~€150–220/month with two nodes (Log Analytics removed). ACR Basic is ~€5 plus storage — small money, real trust residue.

Retain by default: Terraform remote state backend (~€1–2/month) so `environments/dev` can be destroyed and later re-init'd.

## 3. How this repository implements Topic 13

> **Practice — Read the guarded script**
>
> Open `docs/setup/13-teardown.md` and `scripts/operations/teardown.sh`.

```bash
./scripts/operations/teardown.sh --confirm destroy-boutique-platform
./scripts/operations/teardown.sh --confirm destroy-boutique-platform --dry-run
./scripts/operations/teardown.sh --confirm destroy-boutique-platform --destroy-bootstrap
```

The script refuses to run without the exact phrase `destroy-boutique-platform`. It destroys `terraform/environments/dev`: AKS, ACR, Key Vault, VNet, Azure DNS zone, platform RG. Bootstrap is extra and explicit.

Header comment: **ACR is destroyed per ADR-0010**. That is the teaching sentence.

Pre-teardown checklist in Topic 13:

| Item | After teardown |
|------|----------------|
| Git repo | GitHub — **kept** |
| Cosign public key | Kyverno policy in Git — **kept** |
| Cosign private key | Key Vault — **destroyed** |
| Signed images | ACR — **destroyed** |
| TF state (dev) | Bootstrap blob — **kept** unless `--destroy-bootstrap` |

Pause ADO pipelines so jobs do not hammer a dying API. Optional last smoke: `./tests/integration/promotion-smoke.sh all`. Registrar NS may need update when the Azure DNS zone goes away.

`docs/runbooks/teardown.md` is the operations copy. `docs/architecture/08-resilience-and-dr.md` rebuild order is the inverse: bootstrap (if kept) → env → Argo CD → Kyverno → **CI mirror/sign** → Boutique → observability. Skipping mirror after ACR destroy is how unsigned `:latest` returns.

`docs/runbooks/teardown.md` and Topic 13 Step 13.2 dry-run (`terraform plan -destroy`) are mandatory before the confirm phrase. The script requires `az` and `terraform` on PATH. It does not delete the GitHub repo, ADO project, or registrar domain — those can still cost or still publish dead FQDNs.

Cosign public key in Git is kept so Kyverno policy history remains reviewable. After destroy it does not verify any live image. Next Topic 09 **must** generate a new pair (old private key died with the vault) and update the PEM. Reusing a public key whose private key is gone is a dead verifier.

Cost model guardrails: user pool `max_count: 3`, SKUs locked, Loki 10Gi, Prometheus 15d, teardown mandatory for cost stop. Verification: `az consumption usage list`. Screenshot the empty AKS/ACR list as teardown evidence the way Topic 10 screenshotted the storefront.

`docs/architecture/08-resilience-and-dr.md` teardown bullet: destroys AKS, ACR, load balancers; bootstrap optional. Reverse order is Topic 13; forward order after rebuild starts at Topic 01 or 02 if state remains.

Cost verification command in the cost model (`az consumption usage list`) is how you prove spend stopped — not a dashboard anecdote.

## Lived operator commands (Topic 13)

From `docs/setup/13-teardown.md` and the script header — these are the commands the pilot used, not new targets:

```bash
./tests/integration/promotion-smoke.sh all 2>/dev/null || true
./scripts/operations/teardown.sh --confirm destroy-boutique-platform --dry-run
./scripts/operations/teardown.sh --confirm destroy-boutique-platform
# optional:
./scripts/operations/teardown.sh --confirm destroy-boutique-platform --destroy-bootstrap
az acr show --name acrboutiquedevgwc   # expect failure after destroy
az aks list -o table                     # expect no boutique cluster
```

Pause ADO pipelines in the GUI before destroy so retries do not fill logs. Export `terraform.tfvars` locally if you will rebuild; it is gitignored. Preserve the public PEM in `policies/kyverno/cluster/02-verify-image-signatures.yaml` even though the matching private key will die with Key Vault — the next Topic 09 replaces both.

## Limits of this chapter

Teardown does not delete GitHub, the ADO project, Let's Encrypt rate-limit state, or registrar NS. Those leftovers are cheap compared with AKS but they can confuse a rebuild (stale pipelines, wrong NS). The script is not `az group delete` — it is Terraform destroy of `environments/dev`, which is the only way state stays honest.

Destroying Key Vault with purge protection disabled still soft-deletes. Topic 03’s `list-deleted` check exists for the next apply. If you enabled Topic 19 purge protection on a rebuild, Topic 13 becomes harder on purpose — that is ADR-0016 versus ADR-0010, and you must choose.

## 4. Test the design under failure

### Independent control failure — Portal-delete AKS, keep ACR

> **Practice — Name the leftover trust**
>
> An engineer deletes the cluster in Azure Portal to “save money tonight” and leaves `acrboutiquedevgwc` plus the pipeline UAMI.

**Severity:** high; cost partially stopped, trust not.  
**Plausible harm:** next week's cluster attaches the old registry; old signatures and possible stale tags return; Key Vault and DNS leftovers; Terraform state lies.  
**Potential blast radius:** next rebuild plus any identity that still has AcrPush.  
**Bounded by:** ADR-0010, teardown script vs click-ops, Git as remaining source of truth.  
**Primary principles:** teardown is a production control, identity is digest not tag, reconciliation, recovery.

#### Diagnosis

Portal delete does not run `terraform destroy`. State still thinks AKS exists. ACR still holds manifests. Kyverno PEM in Git still matches a key that may live in an undestroyed vault — or the vault is gone and the PEM is an orphan public key waiting for a new pair.

#### Correction

Use the script (or `terraform destroy` in `environments/dev` after a dry-run). Confirm `az acr show` fails for the old name. Confirm no AKS resource group. Re-mirror on rebuild; generate keys if the vault was destroyed. Do not “just docker push” unsigned images to a leftover registry to save time.

A second failure: destroying bootstrap first. Correction: env destroy first; keep versioned blob until you choose `--destroy-bootstrap`.

## Production reality

**Best Practice:** destroy the registry when you destroy the cluster.

**Production Practice:** confirm phrase `destroy-boutique-platform` is a human lock, not cryptography. `--dry-run` first. Do not wrap the script in a scheduled ADO job without the same phrase and a second person — this repo is a solo pilot; scheduled destroy would be a new ADR.

Keeping ACR to “save mirror time” is how unsigned or stale signed images return. Mirror time is the price of ADR-0010.

### Common errors

- `terraform destroy` in bootstrap while env still references the blob.
- Deleting DNS at the registrar before you intended, then blaming cert-manager on the next rebuild.
- Leaving ADO pipelines enabled to retry against a dead ACR (noise, not safety).

## 5. What You Learned

Topic 13 stops spend by destroying AKS **and** ACR. That is intentional. Git, screenshots, public PEM, and optional state storage remain. Rebuild is hours (RTO 4–8), not a tag pull from a pet registry. Unsigned images have nowhere to live in Azure after a correct teardown.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 13 guide | `docs/setup/13-teardown.md` | Checklist and destroy order |
| Script | `scripts/operations/teardown.sh` | Confirm phrase; ACR in scope |
| ADR-0010 | `docs/adr/0010-destroy-acr-on-teardown.md` | Why ACR dies |
| Cost model | `docs/architecture/11-cost-model.md` | €150–250 active; ~€1–2 if only state |
| DR | `docs/architecture/08-resilience-and-dr.md` | Rebuild includes Topic 09 |
| Runbook | `docs/runbooks/teardown.md` | Operator copy |

## What changed

| Before | After |
|--------|--------|
| Portal-delete the cluster, keep ACR. | **Terraform destroy includes ACR (ADR-0010).** |
| Spend continues at ~€150–250/mo. | **Cost stop; optional ~€1–2 state blob.** |
| Signatures assumed durable. | **Re-mirror required on rebuild.** |
| Confirm-less destroy scripts. | **`--confirm destroy-boutique-platform`.** |

`docs/runbooks/teardown.md` and Topic 13 are the two copies operators actually open. `ARCHITECTURE.md` cost section and `11-cost-model.md` must stay aligned. After destroy, README hostnames stay in the table with **Test offline** — that sentence is teardown’s public evidence.

> **Independent Practice — Write the rebuild first day**
>
> After a correct teardown, list Topics 00–09 in order and mark which ones are no-ops if bootstrap state was kept. Circle Topic 09. Explain why Kyverno would deny Boutique if you skipped it.

## Further reading

Playbook article **A3** is the short public argument for destroying ACR on teardown.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/A3.md
