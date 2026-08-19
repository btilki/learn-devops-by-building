# 14 — Tear Down as a Production Control

Leaving a “successful” **EKS (Elastic Kubernetes Service)** cluster up is how pilots become unowned production. Topic 14 is **M4 (Milestone 4)**: ordered destroy immediately after tests. FR-11 is not optional hygiene.

> How do you decommission GitOps-managed **ALBs (Application Load Balancers)**, the cluster, and (optionally) Terraform state so no orphan billables remain — without destroying state while resources still exist?

## 1. The unsafe starting state: keep-alive for demos

After M3, the storefront is the best screenshot you will have. NAT, EKS, and ALBs continue at the monthly band in `docs/architecture/10-cost-model.md` (~$350–500). So do **IAM (Identity and Access Management)** roles and public DNS. The attack surface outlives the proof.

The cost model already ordered teardown. Topic 14 (`docs/setup/14-teardown.md`) and `docs/runbooks/teardown.md` execute it. **Lived.** Appendix T: M4 PASS 2026-07-19/20. AWS boutique resources are gone.

## 2. The production model: prune edge, then foundation, then state

> *Theory — Ordered decommission*
>
> Release controller-managed Load Balancers while the API server still exists; destroy Terraform foundation next; delete or retain the state backend last; audit orphans; never invert that order.

```13:22:docs/runbooks/teardown.md
## Order (do not reorder)

```text
0. Stop CI / schedules that recreate load
1. Prune GitOps: workloads → platform → bootstrap (ALBs/TGs/PVCs release)
2. Confirm no stray ALBs / Target Groups / blocking ENIs
3. terraform destroy (terraform/envs/prod)
4. Decide remote state bucket + lock table (last)
5. Orphan audit (EKS, NAT, ELB, EIP, EC2, ECR policy)
6. Sign Appendix T + ROADMAP Phase 11 ✅
```
```

Hard rules: do not destroy VPC while ALBs remain; do not empty the state bucket first.

## 3. How this repository implements teardown

> **Practice — Read Appendix T as the lived record**
>
> Open `docs/PRODUCTION_CHECKLIST.md` Appendix T. Pair it with `docs/setup/14-teardown.md` Step 14.1 and the cost-model teardown list.

### Stop CI, prune GitOps

Topic 14 disables GitLab schedules, refreshes kubeconfig, deletes ApplicationSet `boutique-workloads` first so Ingress/ALBs release, then platform AppSets, then root. Friction notes in Appendix T: stop Argo controllers (or delete `root`) before AppSet delete or they recreate; strip `ingress.k8s.aws/resources` finalizers if the LB controller is already gone.

**CI (Continuous Integration)** must not rebuild load during destroy. After M4, workflow `when: never` (Chapter 10) is the lasting dormancy switch.

### Terraform destroy, then state

```41:51:docs/architecture/10-cost-model.md
## Teardown reference

Ordered destroy (details in Setup `14-teardown` / `docs/runbooks/teardown.md`):

1. Stop CI schedules that would recreate load  
2. Prune Argo apps (workloads → platform) to release ALBs  
3. Confirm ELBv2/ENI cleanup  
4. `terraform destroy` foundation  
5. Handle ECR empty/delete  
6. Destroy or retain empty state backend **last**  
7. Verify no EKS cluster / NAT / stray ALBs  

**Do not** destroy Terraform state while resources still exist.
```

**Lived.** Appendix T: GitOps prune ✅; ELBv2 count **0**; `terraform destroy` exit 0 ~23:13Z; state backend **Deleted (Option B)** 2026-07-20 (`boutique-eks-gitops-tfstate-868480224481` + lock table); orphan audit 2026-07-20 full wipe including leftover launch templates, EKS log group, IAM `microservice-policy`. Account scaffolding left (default VPC, login user, AWS service-linked roles) is named, not hidden.

Remote state itself was Topic 03’s first billable:

```1:9:terraform/envs/prod/backend.tf
# Remote state backend — S3 + DynamoDB locking
# Setup Topic 03. Partial backend config is supplied via -backend-config=../../backend.hcl
# (file is gitignored; start from terraform/backend.hcl.example).

terraform {
  backend "s3" {
    # bucket, key, region, dynamodb_table, encrypt — set via backend.hcl (Step 3.4)
  }
}
```

**Lived**, then deleted. `backend.hcl` never belonged in Git. A rebuild recreates bucket + lock table *before* VPC. Topic 14’s remaining Setup steps are ELBv2 describe, `terraform destroy`, ECR force-delete when images remain, and the orphan audit commands. ROADMAP Phase 11 ✅ is the public status line.

`docs/architecture/08-resilience-and-dr.md` “Teardown vs DR” is the conceptual split: if you still need the shop, you are in DR (hours RTO). If the pilot is over, you are in FR-11. Mixing them produces a half-destroyed VPC and a live NAT.

### Rebuild is Topic 01 zone → 03 → 04+

`ROADMAP.md` current focus: no live AWS; rebuild starts at Topic 01 (zone) then remote state. Git remains. That is the point of GitOps after the cluster dies (`docs/operations/05-disaster-recovery.md`: if the pilot is over, teardown and stop).

> **Practice — Explain Option B**
>
> Appendix T deleted S3 state. That is correct *after* destroy exit 0 and a second plan of zero resources. State why deleting the bucket *during* a failed destroy is unrecoverable without AWS support archaeology.

## 4. Test the design under failure

**Scenario:** `terraform destroy` while Ingress objects still exist; VPC delete fails; ALBs and ENIs orphan.

**Severity:** bill continues; next destroy is blocked.  
**Plausible harm:** NAT/EKS partially gone, ALBs lingering at hourly cost; engineer deletes state to “clean up” and loses the remaining resource IDs.  
**Potential blast radius:** all leftover ELBv2, ENI, security groups `k8s-*`, NAT EIP, plus any remaining node volumes.  
**Bounded by:** teardown order, Appendix T friction notes, cost-model “do not destroy state while resources exist.”  
**Primary principles:** teardown after the pilot is required; Git is the only deploy authority (desired state remains even when AWS does not); one cluster and three namespaces are a cost decision, not isolation.

### Diagnosis

`aws elbv2 describe-load-balancers` nonempty; `terraform destroy` errors on ENI/SG; `aws eks list-clusters` maybe empty already. Git still has `gitops/` — that is expected.

### Recovery

Re-establish kubeconfig if the cluster remains; prune Ingress/AppSets; detach leftover SGs; retry destroy. If the cluster is gone but ALBs remain, delete ELBv2 by tag from the AWS API using IDs still in state — which is why state must still exist. After a successful zero-resource apply, then decide Option A (retain empty backend) or B (delete). Record leftovers in Appendix T rather than claiming “cluster gone” from memory.

Friction notes worth memorizing: stop Argo (or delete `root`) before ApplicationSet delete or controllers recreate children; strip `ingress.k8s.aws/resources` finalizers if the LB controller is already gone; delete leftover `k8s-*` security groups before VPC destroy; ECR needs force delete when images remain. Those are Appendix T’s gift to the next rebuild, not folklore.

Cost-model 2-day band (~$35–45) only holds if this chapter actually runs. The monthly band is what you pay for “we might demo on Monday.”

## 5. What You Learned

Teardown is a milestone: prune, destroy, audit, sign Appendix T. You can now walk Topic 14, `docs/runbooks/teardown.md`, the cost model, and the lived M4 record. The reader’s clone has no live AWS; that is success.

### Durable outputs

- Setup: `docs/setup/14-teardown.md`
- Runbook: `docs/runbooks/teardown.md`
- Evidence: `docs/PRODUCTION_CHECKLIST.md` Appendix T
- Cost: `docs/architecture/10-cost-model.md`

> **Independent Practice — Abort at Topic 08**
>
> You fail M2 (no email) and must stop spend tonight. Write the teardown order from “furthest topic reached,” including whether Boutique AppSets exist yet. Do not skip ALB prune because “we never installed Boutique.” Grafana Ingress still counts.

### Lived M4 timestamps (historical)

Appendix T is the only allowed “cluster is gone” proof:

| Field | Lived value |
|-------|-------------|
| Teardown start | 2026-07-19 ~22:46 UTC |
| Destroy complete | ~23:13Z, `Resources: 0` |
| State backend | Deleted 2026-07-20 (Option B) |
| Orphan audit | 2026-07-20: EKS/ELB/NAT/ECR/S3/DDB/SM/ACM/R53 = 0 |

Topic 14 Setup still lists the operator commands (`aws eks update-kubeconfig`, `kubectl delete applicationset boutique-workloads`, `terraform destroy`). They are rebuild/abort procedures. Running them today against an empty account should plan zero foundation resources if you recreate state first — which you should not, unless you intend to pay again.

```25:32:docs/runbooks/teardown.md
## Hard rules

| Do | Do not |
|----|--------|
| Prune Ingress/apps **before** `terraform destroy` | Destroy VPC while ALBs still attached |
| Destroy foundation **before** state backend | Empty/delete state bucket first |
| Record leftovers intentionally retained | Ad-hoc deletes outside this runbook |
| Use `eu-central-1` consistently | Assume “cluster gone” without `aws eks list-clusters` |
```

**Lived** as the rule set Appendix T executed.

Setup 14 remaining steps after prune: wait for Ingress ADDRESS to clear (often 3–15 minutes), `aws elbv2 describe-load-balancers`, destroy `terraform/envs/prod`, force-delete ECR if images remain, then Option A (keep empty backend) or B (delete bucket + lock table). The lived pilot chose B on 2026-07-20. `ROADMAP.md` Phase 11 ✅ and “No live AWS pilot resources remain” are the public close. Rebuild is Topic 01 zone check, then 03, then 04+.

Topic 14 is FR-11. The cost model’s “Always run Phase 11 immediately after all tests” is the same sentence. If Appendix T is empty on a rebuild, M4 is not done even if `terraform destroy` felt successful — the orphan audit row is required.

## Further reading

Playbook article **E3** is the short public argument for a cost-honest two-day EKS pilot and mandatory teardown.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/E3.md

## Next

Chapter 15 authors Phase 12 hardening in Git so the next paid cluster does not rediscover signature admission, AppProjects, analysis, **WAF (Web Application Firewall)**, and Falco from a blank page — all labeled **scaffold**.
