# 9 — Pin Boutique by Helm Digest Overlays

A chart that interpolates `{{ .Values.image.tag }}` will lose to Kyverno on this cluster. A pipeline that builds first cannot invent the first image either. Topic 09 is the chicken-and-egg close: Helm contract + env overlays + one-time **ECR (Elastic Container Registry)** bootstrap so Argo **CD (Continuous Delivery)** can sync before **CI (Continuous Integration)** exists.

> How do you run seven Boutique services plus Redis from Git-pinned digests across `dev` / `stage` / `prod` without tags, without CI deploy, and without pretending the three namespaces are isolated accounts?

## 1. The unsafe starting state: upstream tags and a laptop Helm install

Google’s Online Boutique examples often use moving tags. Installing them with `helm upgrade --install` from a workstation skips Git, skips Kyverno’s intended path, and skips promotion. Putting the same tag in three env folders is not promotion; it is copy-paste of a mutable name.

Topic 09 (`docs/setup/09-boutique-charts.md`) requires `image.repository` + `image.digest` on every chart. Kyverno Enforce (Chapter 7) will block anything else in app namespaces.

**Lived.** Digests in `gitops/envs/**` are the pins that ran. After teardown they do not pull anywhere; they are historical identity.

## 2. The production model: chart identity, overlay identity, bootstrap exception

> *Theory — Digest overlays as environment identity*
>
> Charts expose immutable image fields; env overlays pin concrete digests and hostname/canary scalars; a one-time ECR push unblocks GitOps before the digest pipeline; promotion later copies digests rather than rebuilding.

`docs/architecture/04-data-flows.md` shows the storefront path: user → ALB → frontend → catalog, cart/Redis, checkout → currency, payment, shipping. Those seven plus Redis are in scope. Ads and recommendation are deferred.

## 3. How this repository implements charts and overlays

> **Practice — Lint the image contract**
>
> From the clone, run the Topic 09 loop: for each chart, `grep` `repository:` / `digest:` and `helm template` until you see `@sha256:`. Open `charts/frontend/values.yaml` and `charts/cartservice/values.yaml`.

### Frontend chart contract

```1:6:charts/frontend/values.yaml
# Image contract: repository + digest (ADR-0001). Never use :latest.
# REPLACE digest after Topic 09 bootstrap ECR push.
image:
  repository: "REPLACE_ACCOUNT.dkr.ecr.eu-central-1.amazonaws.com/boutique-eks-gitops/frontend"
  digest: "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  pullPolicy: IfNotPresent
```

The Rollout template (Topic 12) concatenates them: `"{{ .Values.image.repository }}@{{ .Values.image.digest }}"`. Dev keeps `canary.enabled: false` so the chart renders a Deployment.

### Backend example: cartservice

```1:28:charts/cartservice/values.yaml
# Image contract: repository + digest (ADR-0001). Never use :latest.
# REPLACE digest after Topic 09 bootstrap ECR push.
image:
  repository: "REPLACE_ACCOUNT.dkr.ecr.eu-central-1.amazonaws.com/boutique-eks-gitops/cartservice"
  digest: "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  pullPolicy: IfNotPresent

replicaCount: 1

service:
  type: ClusterIP
  port: 7070
...
env:
  REDIS_ADDR: "redis:6379"
  PORT: "7070"
```

**Lived** contract. Same shape on productcatalog, checkout, currency, payment, shipping, redis.

### Env overlays pin real digests and hosts

Dev frontend overlay (canary off):

```1:19:gitops/envs/dev/values/frontend.yaml
# Env overlay — dev / frontend
# REPLACE repository account + digest after Topic 09 bootstrap (Steps 9.2–9.3)
image:
  repository: "868480224481.dkr.ecr.eu-central-1.amazonaws.com/boutique-eks-gitops/frontend"
  digest: "sha256:be8651bb65c21cac85ba282d4fd33a47b4bcac0541234c82dbfdb30d0acdfb7a"
ingress:
  enabled: true
  className: alb
  host: "dev-boutique.biroltilki.art"
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/certificate-arn: "arn:aws:acm:eu-central-1:868480224481:certificate/9363fd9a-7ed5-41da-aea5-f37f53a94269"
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    external-dns.alpha.kubernetes.io/hostname: "dev-boutique.biroltilki.art"
# Topic 12 — canary is stage+prod only (FR-09). Dev stays Deployment.
canary:
  enabled: false
```

Prod overlay pins a different digest (`563ebf12…`) and `boutique.biroltilki.art`, with `canary.enabled: true`. Stage sits between. **Lived** pins; **inactive** hosts.

### ApplicationSet wires chart × env

`gitops/apps/workload-apps/boutique-applicationset.yaml` (Chapter 6) renders `charts/{{.service}}` with `$values/gitops/envs/{{.env}}/values/{{.service}}.yaml`. Prod remains manual sync. Wave 40 is after platform waves.

Topic 09 bootstrap: pull Boutique **v0.10.6**, retag into ECR, write digests into overlays, then Argo sync **dev** first. That push is an operator exception, recorded in ADR-0001 consequences, not a standing CI deploy.

The ApplicationSet service list is the chart family you must keep in lockstep with Terraform `local.ecr_services` and the promotion `for svc in …` loop: `redis`, `productcatalogservice`, `currencyservice`, `cartservice`, `paymentservice`, `shippingservice`, `checkoutservice`, `frontend`. A twelfth service is a cross-cutting change, not a one-line Helm add. Frontend env overlays also carry Ingress ALB annotations and ACM ARN from Topic 05. Changing host in a digest-only promote MR is a contract violation (`docs/promotion.md`).

`docs/architecture/04-data-flows.md` user sequence is the runtime meaning of those seven services. If checkout cannot reach payment, the overlay digest for `paymentservice` is the identity to compare across envs — not a tag, not “whatever CI last built.”

Stage frontend overlay at the M3 pin (same digest as prod after realign `!13`):

```1:23:gitops/envs/stage/values/frontend.yaml
# Env overlay — stage / frontend
# REPLACE repository account + digest after Topic 09 bootstrap (Steps 9.2–9.3)
image:
  repository: "868480224481.dkr.ecr.eu-central-1.amazonaws.com/boutique-eks-gitops/frontend"
  digest: "sha256:563ebf12a5b98ae558c340ea70d9c56c2c57ad9880e8a6b7416ac54b0b7e1335"
ingress:
  enabled: true
  className: alb
  host: "stage-boutique.biroltilki.art"
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/certificate-arn: "arn:aws:acm:eu-central-1:868480224481:certificate/9363fd9a-7ed5-41da-aea5-f37f53a94269"
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    external-dns.alpha.kubernetes.io/hostname: "stage-boutique.biroltilki.art"
# Topic 12 — frontend canary (ALB traffic split)
# Topic 18 — analysis off by default; see frontend-analysis.example.yaml to enable
canary:
  enabled: true
  analysis:
    enabled: false
```

**Lived** pin; **inactive** host. Canary on, analysis off. Dev overlay used a different digest (`be8651bb…`) and `canary.enabled: false`. That is environment identity: same chart, different overlay.

> **Practice — Diff three env frontends**
>
> Compare `gitops/envs/dev/values/frontend.yaml`, `stage/...`, `prod/...`. List fields that *should* differ (host, canary, digest as promotion proceeds) versus fields that should stay in lockstep (repository, ALB annotation shape).

## 4. Test the design under failure

**Scenario:** Overlay uses a tag `v0.10.6` “until bootstrap finishes.”

**Severity:** admission deny or, if Kyverno is down, mutable production identity.  
**Plausible harm:** Kyverno blocks the app (good) and operators disable policy (bad); or Pods run an unpinned tag that ECR can overwrite.  
**Potential blast radius:** that service in the affected namespace; if policy is disabled, all app namespaces.  
**Bounded by:** Kyverno require-digest/ECR/deny-latest, chart contract, Topic 09 bootstrap steps, digest-only promotion docs.  
**Primary principles:** image identity is digest, not tag; Git is the only deploy authority; CI has ECR and Git permission, not cluster deploy permission.

### Diagnosis

`helm template` shows `image: …:v0.10.6` without `@sha256:`. Argo OutOfSync or Pods Pending `admission webhook denied`. `grep ':latest\|image:.*:[^@]' gitops/envs`.

### Recovery

Write bootstrap digests from `docker inspect` / ECR `describe-images` into overlays. Do not set Kyverno to Audit. Do not `kubectl set image`. After teardown, recovery is “on rebuild, finish Step 9.2 before expecting Healthy apps.”

## 5. What You Learned

Boutique identity in this system is Helm digest overlays per env, with a one-time ECR bootstrap before CI. You can now walk Topic 09, `charts/` (frontend + backends), and `gitops/envs/{dev,stage,prod}`.

### Durable outputs

- Setup: `docs/setup/09-boutique-charts.md`
- Charts: `charts/frontend/`, `charts/cartservice/` (and the other six)
- Overlays: `gitops/envs/{dev,stage,prod}/values/`
- AppSet: `gitops/apps/workload-apps/boutique-applicationset.yaml`

> **Independent Practice — Promote configuration without a new digest**
>
> You must raise frontend `replicaCount` in prod only. Using the overlay-vs-chart split, write an MR description that does *not* mix digest promotion with replica change. Explain why CODEOWNERS still applies and why this is not a CI job.

Topic 09 Setup remaining work: ECR login, pull/push bootstrap images, write digests into all three env folders, sync `*-dev` first, curl `dev-boutique`. Prod stays unsynced until Topic 11. Redis must exist in `module.ecr` or cartservice cannot pull. The placeholder digest of sixty `a`s in chart `values.yaml` is not admitted by Kyverno — overlays must replace it before Argo creates Pods.

Helm `fullnameOverride` keeps Service DNS stable (`frontend`, `cartservice`, …) so Boutique env vars like `CART_SERVICE_ADDR: cartservice:7070` stay simple. Changing those names is not a digest promotion.

## Next

Chapter 10 is the standing loop: build, scan, sign, and open a digest-only merge request — still never deploying.
