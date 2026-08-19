# 4 — Reconcile AWS Foundation Through Terraform

Laptop `terraform.tfstate` is not a production backend. A GitLab job with `eks:*` is not a convenient bootstrap. The unsafe default is to apply a monolith from `/tmp`, store state next to the laptop, and widen **IAM (Identity and Access Management)** until something works.

> How do you provision one **EKS (Elastic Kubernetes Service)** cluster, registries, and least-privilege identities so later GitOps topics have a foundation — without giving **CI (Continuous Integration)** deploy permission?

## 1. The unsafe starting state: local state and a deploy-capable CI role

Topic 03 (`docs/setup/03-remote-state.md`) exists because concurrent applies and laptop loss corrupt infrastructure truth. Topic 04 (`docs/setup/04-network-eks-ecr-iam.md`) is the first **high cost** step: **EKS** control plane, three `m6i.large` nodes, and one **NAT (Network Address Translation)** gateway.

Without remote state, two operators plan against different worlds. Without a scoped GitLab **OIDC (OpenID Connect)** role, the pipeline that should only push **ECR (Elastic Container Registry)** becomes a second cluster admin. ADR-0001 is then a README sentence.

**Lived** on 2026-07 during the pilot. **Inactive** now: those AWS resources were destroyed at M4. The Terraform in Git is the rebuild contract, not a live inventory.

## 2. The production model: locked state, then a modular foundation

> *Theory — Remote-state then least-privilege foundation*
>
> Create durable, locked Terraform state first, then apply a modular VPC/EKS/ECR/IAM stack whose CI identity can push images but cannot call the cluster API.

Topic 03 creates an **S3 (Simple Storage Service)** bucket with versioning, encryption, and public-access block, plus a DynamoDB lock table. `terraform/backend.hcl` is gitignored. `terraform/envs/prod/backend.tf` points at that backend. You do not create a VPC in Topic 03.

Topic 04 then composes modules. The root module is the map:

```36:85:terraform/envs/prod/main.tf
module "network" {
  source = "../../modules/network"

  name     = local.name
  vpc_cidr = var.vpc_cidr
  azs      = local.azs
  tags     = local.tags
}

module "eks" {
  source = "../../modules/eks"

  name                         = var.cluster_name
  cluster_version              = var.cluster_version
  vpc_id                       = module.network.vpc_id
  private_subnet_ids           = module.network.private_subnet_ids
  node_instance_types          = var.node_instance_types
  node_desired_size            = var.node_desired_size
  node_min_size                = var.node_min_size
  node_max_size                = var.node_max_size
  endpoint_public_access_cidrs = var.endpoint_public_access_cidrs
  tags                         = local.tags
}

module "ecr" {
  source = "../../modules/ecr"

  repository_names = [for s in local.ecr_services : "${var.project_name}/${s}"]
  tags             = local.tags
}

module "dns" {
  source = "../../modules/dns"

  zone_name                 = var.dns_zone_name
  certificate_domain_name   = "boutique.${var.dns_zone_name}"
  subject_alternative_names = local.acm_sans
  tags                      = local.tags
}

module "iam_gitlab_oidc" {
  source = "../../modules/iam_gitlab_oidc"

  name                = local.name
  gitlab_url          = var.gitlab_url
  gitlab_project_path = var.gitlab_project_path
  gitlab_project_id   = var.gitlab_project_id
  ecr_repository_arns = values(module.ecr.repository_arns)
  tags                = local.tags
}
```

**Lived** as applied foundation. `terraform.tfvars` stays gitignored. `enable_waf` (module `waf`) is **scaffold** / off by default — Chapter 15.

## 3. How this repository implements the modules

> **Practice — Trace identity from module to CI contract**
>
> Open `terraform/modules/iam_gitlab_oidc/main.tf` and `docs/setup/04-network-eks-ecr-iam.md` Step 4.1. Confirm the CI role is ECR-only. Open `terraform/modules/irsa/main.tf` and list which controllers get **IRSA (IAM Roles for Service Accounts)** in `terraform/envs/prod/main.tf`.

### Network: private nodes, one NAT, endpoints

`terraform/modules/network/main.tf` builds a VPC with public subnets tagged `kubernetes.io/role/elb=1` and private subnets tagged `kubernetes.io/role/internal-elb=1`. A single NAT serves private egress. **S3** and ECR VPC endpoints cut NAT GB for image pulls. That is `docs/architecture/06-network-design.md` in code: multi-AZ nodes, single-NAT SPOF accepted.

```33:67:terraform/modules/network/main.tf
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = merge(local.tags, { Name = "${var.name}-vpc" })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags   = merge(local.tags, { Name = "${var.name}-igw" })
}

resource "aws_subnet" "public" {
  for_each = { for idx, az in var.azs : az => { az = az, cidr = local.public_subnet_cidrs[idx], idx = idx } }

  vpc_id                  = aws_vpc.this.id
  availability_zone       = each.value.az
  cidr_block              = each.value.cidr
  map_public_ip_on_launch = true
  tags = merge(local.tags, {
    Name                     = "${var.name}-public-${each.value.idx}"
    "kubernetes.io/role/elb" = "1"
  })
}
```

### EKS: 1.31, ASG 2–5, tighten the API CIDR

`terraform/modules/eks/main.tf` defaults `cluster_version` to `1.31`, nodes `m6i.large`, desired 3, min 2, max 5. `endpoint_public_access_cidrs` defaults to `0.0.0.0/0` with the description “tighten for production.” Topic 04 tells the operator to put a `/32` in tfvars when egress is stable. Namespaces `dev` / `stage` / `prod` are *not* created here; GitOps owns them later. ADR-0002’s blast radius starts at this one cluster.

### ECR, DNS, IRSA

`terraform/modules/ecr` creates one repository per Boutique service plus Redis. `terraform/modules/dns` looks up the Route53 zone and requests the **ACM (AWS Certificate Manager)** certificate for the locked SAN set. `terraform/modules/irsa` binds a service account in a namespace to an IAM role via the cluster OIDC provider. Root wires three: external-dns, AWS LB controller, External Secrets.

`terraform/modules/irsa/main.tf` is the reusable binding: OIDC provider ARN/URL, namespace, service account name, policy JSON. Root instantiates it three times (external-dns, aws-lb-controller, external-secrets). Controllers receive AWS API power; Boutique pods do not. That is `docs/architecture/07-security-architecture.md` identity table in Terraform.

`terraform/modules/ecr` scan-on-push and immutable tags match digest identity:

```14:28:terraform/modules/ecr/main.tf
resource "aws_ecr_repository" "this" {
  for_each = toset(var.repository_names)

  name                 = each.value
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(var.tags, { Name = each.value })
}
```

**Lived.** Immutable tags mean CI cannot retag `:bootstrap` to a new digest; it must push a new digest. That is why overlay identity is `image.digest`, not a floating tag. `terraform/modules/dns` issues the ACM certificate for ADR-0004 SANs. Neither module deploys workloads.

### GitLab OIDC: push images, never deploy

```1:11:terraform/modules/iam_gitlab_oidc/main.tf
# GitLab OIDC → IAM role for ECR push (no EKS deploy)
# Setup Topic 04 / 10 · SECURITY.md

variable "name" {
  type        = string
  description = "Name prefix for OIDC resources"
}

variable "gitlab_url" {
  type        = string
  description = "GitLab issuer URL (no trailing slash), e.g. https://gitlab.com"
```

Topic 04’s security note is the same sentence: do not widen that policy “to unblock deploys.” `docs/architecture/07-security-architecture.md` places CI in a privileged-but-scoped zone: ECR push and MR token, **no** `eks:*`.

> **Practice — Read the apply order without applying**
>
> Open `docs/setup/03-remote-state.md` (bucket naming, encryption, `backend.hcl` gitignore) and `docs/setup/04-network-eks-ecr-iam.md` (tfvars, plan review, kubeconfig). State why destroying the state backend before the foundation is forbidden (Chapter 14).

## 4. Test the design under failure

**Scenario:** CI OIDC role granted `eks:*` after a push failure.

**Severity:** second production principal.  
**Plausible harm:** a leaked GitLab job token can `kubectl delete` prod; Git is no longer the only deploy authority; audit trails split between pipeline logs and Argo.  
**Potential blast radius:** the EKS cluster API and every namespace it serves (`dev`, `stage`, `prod`, platform).  
**Bounded by:** `iam_gitlab_oidc` module scope, ADR-0001, Topic 04 “do not widen,” `.gitlab-ci.yml` forbidden deploy commands.  
**Primary principles:** Git is the only deploy authority; CI has ECR and Git permission, not cluster deploy permission.

### Diagnosis

`aws iam get-role-policy` / attached policies on `boutique-eks-gitops-gitlab-ci` show `eks:*` or `kubectl` in CI logs. Terraform plan on `module.iam_gitlab_oidc` would show the widening if it was applied through Git — if it was clicked in the console, Git is already lying.

### Recovery

Revert the IAM change in Terraform and apply. Rotate any exposed job tokens. Inspect cluster audit for unexpected applies. Restore desired state from Git via Argo, not via the pipeline. After M4, the role does not exist; a rebuild must recreate it *narrow*.

## 5. What You Learned

Foundation is remote state plus modular Terraform whose CI identity cannot deploy. You can now map Topics 03–04 to `terraform/envs/prod` and the modules `network`, `eks`, `ecr`, `dns`, `iam_gitlab_oidc`, and `irsa`, and you can say the live AWS objects are gone.

### Durable outputs

- Remote state bootstrap: `docs/setup/03-remote-state.md`, `terraform/envs/prod/backend.tf`
- Foundation apply: `docs/setup/04-network-eks-ecr-iam.md`, `terraform/envs/prod/main.tf`
- Modules: `terraform/modules/{network,eks,ecr,dns,iam_gitlab_oidc,irsa}`
- Network intent: `docs/architecture/06-network-design.md`

> **Independent Practice — Tighten the API without pretending you are multi-account**
>
> Design the `endpoint_public_access_cidrs` value for a rebuild where operators use a known office `/32` and CI never talks to the API. Explain what still shares blast radius (nodes, control plane, NAT). Do not add a second cluster to “fix” that in this exercise.

## Next

Chapter 5 puts HTTPS on the edge with the AWS Load Balancer Controller, external-dns, and cert-manager — still without letting CI own Ingress.
