# 15. Backup, Tear Down, and Rebuild Without Orphans

A platform that cannot die cleanly will bill forever and cannot be trusted to live again. The production question is:

> How do backup, destroy, orphan scan, and rebuild work so Redis/cart state and Git/Terraform state survive — without leftover IPs, and without calling a new Ready cluster a reliability success?

Setup topic **19** is **repo-ready / apply on rebuild** (`enable_monitoring_iac` / `enable_backup_iac` default **false**). Phase 8 teardown **lived** on 2026-07-04. `docs/teardown.md`, `scripts/teardown/`, `redis-restore.md`, `cluster-rebuild.md`, and Terraform `monitoring` / `backup` modules are the contract.

## 1. An unsafe starting state: terraform destroy from the VPC first

Destroying the network while Ingress still holds forwarding rules fails or orphans. Deleting `gs://boutique-gke-tfstate` first loses the map of what exists. Skipping Redis backup discards cart state against a documented RPO. Leaving global addresses reserved is monthly cost with inactive DNS still looking like a brand.

## 2. The production model: reverse bootstrap, backup as a flag, rebuild from Git

> *Theory — Lifecycle as a reliability control*
>
> This model enables the team to decommission with a scanned empty project, restore cart state from a named backup plan, and rebuild the cluster from Terraform state plus Git — without treating node Ready as journey recovery.

### Teardown order

`docs/teardown.md`:

```text
Argo Apps deleted → Ingress/LB released → GKE cluster destroyed
  → terraform destroy (VPC, NAT, DNS, IPs) → orphan scan → billing check
```

Steps include scale/delete Applications (`boutique`, `observability`, `policies`), wait 5–15 minutes for GCE LB release, decide PVC/Redis retain vs discard, `./scripts/teardown/pre-destroy-checklist.sh`, `terraform destroy`, `./scripts/teardown/orphan-resource-scan.sh`, optionally delete the state bucket **last**.

Validation: empty instance/cluster/forwarding-rule/address lists; `dig +short` empty for both names (**Inactive** is success).

### Backup module (9-C scaffold until flag on)

`terraform/modules/backup/main.tf` `google_gke_backup_backup_plan`: cron, retain days, selected namespaces, volume data. Root module:

```hcl
module "backup" {
  count  = var.enable_backup_iac ? 1 : 0
  ...
}
```

Topic 19: `backup_plan_name = "boutique-daily"`, retain 7 days, cron `0 3 * * *`. Architecture §12: Redis RPO &lt; 1h, RTO &lt; 30m — **targets**. Lived Phase 8 validated backup/restore procedures per `redis-restore.md` note; do not inflate that into continuous backups after destroy.

### Monitoring IaC dual path

`terraform/modules/monitoring/main.tf` recreates HTTPS uptime checks for storefront `/` and Argo `healthz`, optional PagerDuty channel. SLO burn policies remain script/YAML-driven until optional follow-up C2. With IaC on, skip duplicate `create-uptime-check.sh` hosts.

### Rebuild

`docs/sre/runbooks/cluster-rebuild.md`: GCS state intact, Git unchanged; `terraform apply`; bootstrap Argo (topic 09); sync policies; sync apps; verify HTTPS. Then apply topics **17–20** because Phase 9 was never lived on the new cluster automatically.

`docs/sre/runbooks/redis-restore.md`: scale down cartservice, restore from GKE Backup, scale up, smoke cart. Expect in-flight session loss.

**Best Practice:** Pre-destroy checklist before `terraform destroy`.

**Production Practice:** Orphan scan is report-only (`scripts/teardown/README.md`). Human review against Terraform state. Series principle: teardown is a production control.

## 3. How this repository implements it

> **Practice — Read teardown as the reverse of bootstrap.md**
>
> Open `docs/teardown.md` and `docs/bootstrap.md` stage table. Phase 8 is on the roadmap as complete.

`scripts/teardown/README.md` lists `pre-destroy-checklist.sh` and `orphan-resource-scan.sh`. Cadence doc (Chapter 13) reuses the same scan weekly while live.

> **Practice — See flags default off**
>
> `terraform/environments/boutique/main.tf` comments: Phase 9-C optional IaC default off while torn down. Enabling flags on a non-existent cluster is a rebuild step, not an offline apply.

Topic 19 still runs burn-rate scripts after monitoring IaC for SLOs. Uptime-check-failed policy must OR both check IDs when Argo check exists.

DNS names inactive is documented in `docs/dns.md` as teardown verification, not an incident.

Backup plan resource (abridged):

```hcl
resource "google_gke_backup_backup_plan" "this" {
  backup_schedule {
    cron_schedule = var.cron_schedule
  }
  backup_config {
    include_volume_data = var.include_volume_data
    selected_namespaces {
      namespaces = var.include_namespaces
    }
  }
}
```

Monitoring module creates `google_monitoring_uptime_check_config.boutique_storefront` (path `/`, port 443, validate SSL) and `argocd_ui` (configurable health path). Those checks are synthetics. They are still not browse/checkout SLOs.

Teardown expected commands after destroy: `gcloud compute instances list`, `gcloud container clusters list`, forwarding rules, global addresses, both `dig +short` names. Empty is success. A leftover `boutique-ingress-ip` is a failed reliability control, not a souvenir.

`docs/sre/runbooks/cluster-rebuild.md` high-level: terraform apply, bootstrap Argo per topic 09, sync policies, sync apps, verify both hostnames. It points at topic 19 to enable `module.backup` on rebuild. `redis-restore.md` prerequisites: recent GKE Backup when `enable_backup_iac=true`, or a documented snapshot; expect in-flight cart session loss.

Phase 8 on ROADMAP is marked complete — teardown happened. GitHub remains. Public DNS does not. That pair is the platform’s current production state.

`scripts/teardown/pre-destroy-checklist.sh` is the human gate before destroy. Skipping it is how Redis volumes and forwarding rules become surprises. Cadence after success: scan again +24h.

## 4. Test the design under failure

### Independent control failure — Destroy with orphans and no Redis backup

> **Practice — Diagnose a “cheap” teardown**
>
> Operator runs `terraform destroy` while Ingress exists, ignores errors, deletes the state bucket, never scans. A reserved global IP remains. Cart snapshots never existed.

**Severity:** high for cost and recoverability.  
**Plausible harm:** surprise bill; cannot rebuild from state; cart history gone against NF10.  
**Potential blast radius:** project `boutique-gke` billing; any hostname still delegated at registrar.  
**Bounded by:** teardown wait step; orphan scan +24h; registrar NS documentation.  
**Primary principles:** Teardown is a production control; Lived evidence beats scaffold; Git is the deploy authority (Git remains; GCP must go).

#### Diagnosis

Terraform cannot always delete what Kubernetes still owns. State bucket is the inventory. Orphans are a class of toil that burns money instead of error budget — still in the reliability contract.

#### Correction

Follow destroy order. Scan. Confirm inactive DNS. Keep Git. On rebuild, enable backup **after** GKE exists, restore drills before the next GD03, apply Phase 9 topics explicitly. A Ready cluster after rebuild is topic 04 again — not checkout SLO success.

That correction closes the book’s lifecycle loop.

## 5. Production reality

### Common errors

#### `terraform destroy` while Applications still own Ingress

Forwarding rules linger; destroy errors; humans delete the state bucket to “unblock.” Then orphans cannot be mapped.

#### enable_monitoring_iac and create-uptime-check.sh both on

Topic 19 dual path: duplicate uptime checks, duplicate pages. Pick IaC or scripts for the same hosts.

#### enable_backup_iac=true with empty cluster_id

Backup plan needs a live cluster id. The flag is a rebuild step after GKE exists, not something to apply against the torn-down project.

#### Rebuilding topics 01–16 and calling Phase 9 done

ROADMAP dependency: 17–20 hang off later phases. They do not auto-apply. Latency SLOs stay documentation until topic 17 commands run.

#### Treating cluster-rebuild curl 200 as checkout SLO restored

Same refusal as Chapter 1. Need SLI data, burn policies, PD channel, and a week of budget before claiming the program is back.

## 6. What changed

| Before | After |
| --- | --- |
| Destroy from the VPC. | Reverse bootstrap; wait for LB; then Terraform. |
| Backups as Console folklore. | `module.backup` behind a flag. |
| Uptime only from scripts. | Optional `module.monitoring`. |
| Leftovers accepted. | Orphan scan pre/post; inactive DNS expected. |

## 7. What You Learned

Phase 8 teardown lived: infra decommissioned 2026-07-04, DNS inactive, Git retained. Topic 19 modules recreate uptime and GKE Backup when flags are on. Redis restore and cluster rebuild runbooks are the DR path. Orphan scan without auto-delete is mandatory. Rebuild does not auto-complete Phase 9. User journeys are not proved by a green `gcloud container clusters list`.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Teardown | `docs/teardown.md` | Destroy order + validation |
| Scripts | `scripts/teardown/` | Checklist + orphan scan |
| Backup/monitoring modules | `terraform/modules/backup`, `monitoring` | 9-C IaC |
| Setup 19 | `docs/setup/19-monitoring-backup-terraform.md` | Enable flags |
| DR runbooks | `docs/sre/runbooks/redis-restore.md`, `cluster-rebuild.md` | Restore/rebuild |

> **Independent Practice — Plan a rebuild week without claiming SLOs on day one**
>
> You will re-apply topics 01–16 then 17–20.

1. When is BA enforce safe relative to `build-scan-sign`?
2. When would you schedule GD04 vs GD03?
3. What orphan scan result 24h after destroy is success?
4. Which evidence would prove checkout SLO is live again (not merely HTTPS 200)?

Do not keep `enable_backup_iac=true` in committed tfvars with secrets. Do not skip the scan because destroy “looked clean.”
