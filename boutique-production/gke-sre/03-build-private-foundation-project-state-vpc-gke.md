# 3. Build Private Foundation: Project, State, VPC, GKE

Browse and checkout cannot run on public nodes with Terraform state on a laptop. The production question is:

> How do you provision a private regional runtime that later chapters can observe, page, and tear down — without calling node Ready a reliability win?

Setup topics **01–04** (**Lived**) build that runtime: project and APIs, remote state, **VPC (Virtual Private Cloud)** plus Cloud NAT, then private **GKE (Google Kubernetes Engine)**. This chapter is foundation, not SLO success.

## 1. An unsafe starting state: APIs off, state local, nodes public

Applying Terraform against disabled APIs produces opaque `SERVICE_DISABLED` errors. Local state on a laptop cannot survive teardown or a second operator. Public node IPs invert the privacy requirement in architecture NF8.

Topic 01 exists because every later resource depends on project `boutique-gke` with billing and enabled service APIs. Topic 02 exists because state must live in a versioned GCS bucket separate from workload infrastructure so teardown can destroy apps before the bucket. Topic 03 exists because private nodes need Private Google Access and NAT for image pulls. Topic 04 exists because Argo CD, Boutique, Kyverno, ESO, and collectors need a cluster — still not a user journey.

## 2. The production model: tenancy, durable state, private egress

> *Theory — Private regional foundation*
>
> This model enables later GitOps and SRE controls to land on a project-bounded, remotely stated, privately addressed cluster whose Ready condition is necessary and not sufficient.

### Project is the tenancy boundary

Topic 01 sets region `europe-west1` and enables the API set Terraform will also manage: Compute, Container, DNS, IAM, STS, Artifact Registry, Secret Manager, Monitoring, Logging, Trace, Binary Authorization, GKE Backup, Certificate Manager, and related services. `terraform/modules/project-apis/main.tf` loops `google_project_service` with `disable_on_destroy` controlled by variable — teardown must not surprise-disable dependents unless intended.

### State is recovered independently of the cluster

Topic 02 creates `gs://boutique-gke-tfstate` with uniform bucket-level access and versioning. `terraform/environments/boutique/backend.tf` wires:

```hcl
backend "gcs" {
  bucket = "boutique-gke-tfstate"
  prefix = "boutique"
}
```

State locking and object versioning are the reconstruction evidence for Chapter 15. Deleting the bucket before a successful destroy loses tracking.

### Private VPC before cluster

Topic 03 layout:

```text
boutique-vpc (custom, regional)
└── boutique-gke-subnet (10.10.0.0/20)
    ├── secondary: boutique-pods (10.20.0.0/16)
    └── secondary: boutique-services (10.30.0.0/20)
Cloud Router (boutique-router) + boutique-nat → internet egress for private nodes
```

`terraform/modules/networking/main.tf` sets `auto_create_subnetworks = false`, `private_ip_google_access = true` on the subnet, Cloud NAT `ALL_SUBNETWORKS_ALL_IP_RANGES`, and a firewall allowing GCE health-check ranges `35.191.0.0/16` and `130.211.0.0/22` to tagged `boutique-gke-node` instances. Without that rule, later Ingress health checks fail while pods look Ready.

### Regional private cluster with Workload Identity

`terraform/modules/gke/main.tf` creates a regional cluster, removes the default node pool, enables private nodes with a public control-plane endpoint (`enable_private_endpoint = false`), allocates secondary ranges, and sets `workload_pool = "${var.project_id}.svc.id.goog"`. The primary pool autoscales, auto-repairs, auto-upgrades, and uses `GKE_METADATA` so pods can use Workload Identity rather than node SA keys.

**Best Practice:** Target Phase 1 modules on first apply so GKE and DNS do not appear unexpectedly.

**Production Practice:** `terraform/environments/boutique/main.tf` lists later modules in one root. Topic 03 uses `-target=module.project_apis` and `-target=module.networking`. Topic 04 may `-target=module.gke`. Targeted apply is bootstrap discipline, not a substitute for a full plan once the foundation is live.

## 3. How this repository implements it

> **Practice — Walk topics 01–04 as the Phase 1–2 runtime**
>
> Open the setup guides and the root module wiring. Do not apply unless you are rebuilding.

`terraform/environments/boutique/main.tf` Phase 1:

```hcl
module "project_apis" {
  source = "../../modules/project-apis"
  project_id = var.project_id
}

resource "time_sleep" "wait_for_apis" {
  depends_on      = [module.project_apis]
  create_duration = "60s"
}

module "networking" {
  source     = "../../modules/networking"
  project_id = var.project_id
  region     = var.region
  depends_on = [time_sleep.wait_for_apis]
}
```

API enablement lags; `time_sleep` exists to avoid flaky networking creates. That is production humility, not decoration.

Topic 03 expected outputs after apply: `network_name = "boutique-vpc"`, `subnet_name = "boutique-gke-subnet"`, plus pod and service range names. Topic 04 then:

```bash
gcloud container clusters get-credentials boutique-gke \
  --region europe-west1 --project boutique-gke
kubectl get nodes -o wide
```

Nodes in Ready are the **expected output of topic 04**. They are not browse success. Capacity later (`docs/sre/capacity/baseline.md`) assumes this pool: `e2-standard-4`, autoscaling 1–3 **per zone**, region `europe-west1`.

> **Practice — Name what teardown must destroy**
>
> Foundation resources are the expensive leftovers if Chapter 15 is skipped: NAT, regional cluster, global addresses, disks.

`docs/setup/README.md` Terraform phase table: topics 01–03 apply `project_apis`, `time_sleep`, `networking`; topic 04 applies `gke` (and may show `ingress_edge` and `dns` in plan). Keep Terraform and GitOps changes in separate PRs when possible — bootstrap.md best practice.

Binary Authorization evaluation mode on the cluster is already wired in the GKE module (`binary_authorization { evaluation_mode = ... }`). Enforce vs dry-run is a later topic. Do not enable enforce before images are attested (Chapter 11 and the 2026-07-04 lesson).

## 4. Test the design under failure

### Independent control failure — Public nodes or local state

> **Practice — Diagnose a foundation that cannot be torn down cleanly**
>
> Local `terraform.tfstate` on a laptop and public node IPs both expand blast radius: lost state and an internet-reachable kubelet plane.

**Severity:** high; reconstruction and privacy both fail.  
**Plausible harm:** cannot destroy what you cannot see in state; scanners reach node IPs; NAT never existed so private-cluster design is fiction.  
**Potential blast radius:** entire project `boutique-gke`; every later secret and image pull path.  
**Bounded by:** topic 02 bucket versioning; topic 03 private Google access + NAT; topic 04 `enable_private_nodes = true`.  
**Primary principles:** Teardown is a production control; Git is the deploy authority (state is not Git, but remote state is the IaC authority).

#### Diagnosis

Skipping topic 02 “until we need a team” leaves a single laptop as the recovery plan. Skipping NAT “because the cluster works with public nodes” contradicts ADR-aligned NF8. Ready nodes hide both mistakes.

#### Correction

Follow topics 01–04 in order. Confirm `terraform output network_name` and private node IPs (`kubectl get nodes -o wide`). Treat `make validate` after Phase 1 as mechanism evidence for Terraform formatting and docs, not as an SLO.

That correction changes later decisions:

- Chapter 4’s static IP and Cloud DNS assume this VPC and cluster exist.
- Chapter 5’s WIF assumes Workload Identity is enabled on the cluster.
- Chapter 15’s destroy order assumes state lives in GCS, not on disk.

## 5. Production reality

### Common errors

#### Enabling APIs only in the Console and never in Terraform

Topic 01 CLI enable is optional if topic 03 `module.project_apis` applies soon. Console-only enablement drifts from Git and surprises teardown (`disable_on_destroy`).

#### Applying the entire root module on day one

`main.tf` lists GKE, DNS, WIF, AR, BA, Armor, monitoring, backup. Topic 03 uses `-target` so Phase 1 stays Phase 1. A surprise GKE create is a cost and blast-radius event.

#### Reading `kubectl get nodes` as capacity proof

Capacity baseline assumes this pool but also HPA/PDB (topic 18) and error-budget freeze (topic 20). Ready nodes with Pending Boutique pods is a later story.

#### Turning on BA enforce in the GKE resource before CI has attestations

The GKE module already has a `binary_authorization` block. Evaluation mode must follow image signing (Chapters 5 and 11), not topic 04 enthusiasm.

## 6. What changed

| Before | After |
| --- | --- |
| Project might exist with random APIs. | Topic 01 + `project-apis` module own the API set. |
| State lived on a laptop. | Versioned GCS backend `boutique-gke-tfstate`. |
| Nodes could be public. | Private nodes, PGA, Cloud NAT, health-check firewall. |
| Cluster Ready was the milestone. | Ready is topic 04 validation only. |

## 7. What You Learned

Topics 01–04 build the private regional foundation: APIs, versioned remote state, VPC with pod/service CIDRs and NAT, regional private GKE with Workload Identity. Node Ready is a topic-04 validation. It is not reliability success. The same foundation is what teardown must empty without orphans.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Setup 01–04 | `docs/setup/01-gcp-project-apis.md` … `04-gke-cluster.md` | Lived bootstrap commands |
| Root wiring | `terraform/environments/boutique/main.tf` | Phase modules and `time_sleep` |
| APIs / VPC / GKE | `terraform/modules/project-apis`, `networking`, `gke` | The actual resources |

> **Independent Practice — Decide whether to apply ingress in the same topic 04 plan**
>
> Topic 04 notes that `ingress_edge` and `dns` may appear in plan if Phase 2 code is present.

1. If you `-target=module.gke` only, what remains uncreated that Chapter 4 needs?
2. If you apply the full plan, what DNS/TLS work still cannot finish until registrar NS delegation?
3. What evidence would prove the cluster is private (not merely Ready)?
4. Which output would you record before walking away from the session?

Do not treat a green `kubectl get nodes` as browse availability.
