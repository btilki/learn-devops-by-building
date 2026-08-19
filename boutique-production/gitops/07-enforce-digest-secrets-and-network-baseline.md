# 7 — Enforce Digest, Secrets, and Network Baseline

Admission that is “coming later” does not run. Secrets in Git outlive the engineer who meant to rotate them. Default-allow east-west on a shared cluster makes `dev` a path into `prod`. Topic 07 is the security baseline that must exist before SMTP and Boutique images land.

> How do you enforce digest-only **ECR (Elastic Container Registry)** images, deliver secrets from AWS, and default-deny namespace traffic — without claiming that namespaces are accounts?

## 1. The unsafe starting state: honor-system GitOps

Argo **CD (Continuous Delivery)** will faithfully apply `:latest` if Git says so. Helm will render it. The node will pull it. **CI (Continuous Integration)** scanning an image does not stop a human from committing a public tag into `gitops/envs/prod`.

Without **ESO (External Secrets Operator)**, Topic 08 has nowhere honest to put SMTP passwords. Without NetworkPolicy, ADR-0002’s “isolation” is labels and hope.

`SECURITY.md` states the principles; `docs/architecture/07-security-architecture.md` draws the trust zones. Topic 07 (`docs/setup/07-security-baseline.md`) implements them.

**Lived.** Signature/SBOM verify policies are **scaffold** (Audit, Topic 15).

## 2. The production model: admit, reference, deny-by-default

> *Theory — Admission plus identity-backed secrets plus namespace deny*
>
> Cluster policy must reject floating tags and non-ECR registries; runtime secrets must be references resolved by a scoped operator; east-west traffic must be explicitly allowed per namespace.

Kyverno ClusterPolicies match Pods in `dev` / `stage` / `prod`. ESO ClusterSecretStores use **IRSA (IAM Roles for Service Accounts)** in `external-secrets`. NetworkPolicies ship per env under `gitops/platform/network-policies/`.

## 3. How this repository implements the baseline

> **Practice — Read the three Enforce policies**
>
> Open `gitops/platform/kyverno/policies/deny-latest-tag.yaml`, `require-image-digest.yaml`, and `ecr-registry-allowlist.yaml`. State what a Pod in `prod` must look like to be admitted.

### Deny `:latest` and require digest

```13:32:gitops/platform/kyverno/policies/deny-latest-tag.yaml
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: deny-latest
      match:
        any:
          - resources:
              kinds:
                - Pod
              namespaces:
                - dev
                - stage
                - prod
                - smoke-m1
      validate:
        message: "Using the :latest tag is forbidden. Pin an image digest (ADR-0001)."
        pattern:
          spec:
            containers:
              - image: "!*:latest"
```

```16:34:gitops/platform/kyverno/policies/require-image-digest.yaml
      validate:
        message: "Images must be pinned by digest (@sha256:...). Tags alone are not allowed."
        foreach:
          - list: "request.object.spec.containers"
            pattern:
              image: "*@sha256:*"
          - list: "request.object.spec.initContainers"
            pattern:
              image: "*@sha256:*"
```

**Lived.** Checklist A8 recorded these ClusterPolicies Ready. Topic 07’s negative tests are expected admission failures — that is the proof, not a green `kubectl apply`.

### ECR allowlist

```14:35:gitops/platform/kyverno/policies/ecr-registry-allowlist.yaml
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: ecr-only
      match:
        any:
          - resources:
              kinds:
                - Pod
              namespaces:
                - dev
                - stage
                - prod
      validate:
        message: "Only Amazon ECR images in eu-central-1 are allowed for Boutique workloads."
        foreach:
          - list: "request.object.spec.containers"
            pattern:
              image: "*.dkr.ecr.eu-central-1.amazonaws.com/*"
```

**Lived.** Combined with digest, this is still not signature verification. An unsigned digest in the right registry still admits. ADR-0007’s `verify-image-signatures.yaml` is Audit **scaffold**.

### ESO: secrets never in Git

```1:19:gitops/platform/external-secrets/clustersecretstore.yaml
# ClusterSecretStore — AWS Secrets Manager + SSM via IRSA
# Setup Topic 07 Step 7.4
# ServiceAccount must match IRSA trust: external-secrets/external-secrets
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-cluster-secret-store
  annotations:
    argocd.argoproj.io/sync-wave: "21"
spec:
  provider:
    aws:
      service: SecretsManager
      region: eu-central-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets
            namespace: external-secrets
```

**Lived.** `examples/externalsecret-sample.yaml` is a smoke sample, not prod config. SMTP for Alertmanager arrives in Topic 08 as an ExternalSecret, not as a Helm password.

### NetworkPolicy: default deny, then DNS and peers

```1:14:gitops/platform/network-policies/prod.yaml
# NetworkPolicy baseline — prod (mirror of stage; stricter review in Topic 13)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: prod
  annotations:
    argocd.argoproj.io/sync-wave: "21"
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

**Lived.** `dev.yaml` and `stage.yaml` mirror the pattern. Allow-DNS, allow-same-namespace, ingress from the load-balancer namespace, and metrics scrape are the usual openings. This is **not** multi-account isolation. A node compromise still sees all namespaces’ compute. `SECURITY.md` says that in one sentence.

> **Practice — Map SECURITY.md to files**
>
> Open `SECURITY.md` and `docs/architecture/07-security-architecture.md`. For each principle (least privilege, secrets, supply chain, admission, network, prod governance), name the Git path that implements it. Label signature verify **scaffold**.

## 4. Test the design under failure

**Scenario:** Kyverno `validationFailureAction` switched to Audit on `require-image-digest` to “unblock a demo tag.”

**Severity:** digest contract becomes advisory.  
**Plausible harm:** `:latest` or a moving tag reaches prod; rollback via Git revert no longer maps to a unique image; Trivy gated a different digest than what runs.  
**Potential blast radius:** all Pods in `dev` / `stage` / `prod` (and `smoke-m1` for deny-latest).  
**Bounded by:** Enforce on the three lived policies, Helm `image.digest` contract, CI digest-only MRs, CODEOWNERS.  
**Primary principles:** image identity is digest, not tag; Git is the only deploy authority; scaffold in Git is not lived proof.

### Diagnosis

`kubectl get clusterpolicy require-image-digest -o yaml` shows Audit. `kubectl get pods -n prod -o jsonpath='{..image}'` shows tags without `@sha256:`. Argo still “Healthy.”

### Recovery

Restore Enforce from Git and sync Kyverno policies. Delete non-digest Pods; let Argo recreate from overlays. Do not add a CI `kubectl set image` to “fix” running tags. If a policy deny storm blocks legitimate digest Pods, revert the *policy* MR — `docs/architecture/08-resilience-and-dr.md` lists that recovery — rather than disabling admission.

## 5. What You Learned

The security baseline is Enforce digest/ECR, ESO references, and default-deny NetworkPolicy on a shared cluster you still refuse to call multi-account. You can now walk Topic 07, Kyverno policies, ESO, NetworkPolicies, and `SECURITY.md` as one baseline.

### Durable outputs

- Setup: `docs/setup/07-security-baseline.md`
- Policies: `gitops/platform/kyverno/policies/deny-latest-tag.yaml`, `require-image-digest.yaml`, `ecr-registry-allowlist.yaml`
- Secrets: `gitops/platform/external-secrets/`
- Network: `gitops/platform/network-policies/{dev,stage,prod}.yaml`
- Narrative: `SECURITY.md`, `docs/architecture/07-security-architecture.md`

> **Independent Practice — Exception for a debug sidecar**
>
> An incident lead wants a `nicolaka/netshoot:latest` sidecar in `prod` for ten minutes. Using these policies, write either a time-bounded, namespaced PolicyException (if you would) or a refusal that names blast radius. If you allow it, state how Git still records the exception and when it expires. Do not weaken ClusterPolicies globally.

## Next

Chapter 8 explains production from on-cluster Prometheus, Loki, Grafana, and Alertmanager email — still without CloudWatch or PagerDuty.
