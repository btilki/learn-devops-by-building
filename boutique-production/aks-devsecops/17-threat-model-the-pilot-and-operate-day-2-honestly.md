# 17. Threat-Model the Pilot and Operate Day-2 Honestly

Controls without a threat model become a tool list. A threat model without operations becomes a slide. This chapter reads `docs/security/threat-model.md`, architecture **07** and **08**, `docs/operations/`, and `docs/runbooks/incident-response.md`. Day-2 assumes Topics 00–12 once lived; the reference Azure test is **offline**.

The production question is:

> What can still harm this single-cluster pilot, what would you do at 02:00 as the only operator, and what recovery evidence is possible after teardown?

## 1. Unsafe starting state

The unsafe default is to copy an enterprise STRIDE spreadsheet and score “AKS = high” without naming the cosign key, the ADO subject, or the shared blast radius. The other default is a 20-person on-call rota in the operations README. This repo's escalation table is **You** at L1, L2, and L3.

Boutique uses mock payments. Do not threat-model PCI as if card data were in Redis.

## 2. The production model: assets, boundaries, proportionate IR

> *Theory — Pilot threat model*
>
> This model enables day-2 action to protect signing keys, Git desired state, and admission — without claiming SOC detection or multi-region failovers the architecture refused.

`docs/security/threat-model.md` assets:

| Asset | Sensitivity | Location |
|-------|-------------|----------|
| Cosign private key | **Critical** | Key Vault |
| Grafana / Argo admin creds | High | K8s Secrets / KV |
| Signed container images | High | ACR |
| Git repository | High | GitHub (the table's “Azure DevOps” cell is a slip — Git is GitHub; ADO is pipelines) |
| Terraform state | High | Bootstrap blob |
| Application user traffic | Medium | Boutique ingress |
| Platform telemetry | Low | Prometheus / Loki |

Trust boundaries: Internet → NGINX → namespaces; ADO OIDC → ACR/KV; Git → Argo → API; Kyverno on the API.

STRIDE is summarized in-repo: spoofing mitigated by OIDC subject lock; tampering by cosign + `verifyImages`; repudiation by ADO approval + Git (no SIEM); disclosure by KV + CSI; DoS by limits and alerts (single cluster); elevation by PSS + deny privileged (platform NS excluded).

Residual: Kyverno down; federation misconfig; Topic 15 NetworkPolicy not lived-enforced.

## 3. How this repository implements day-2

> **Practice — Read security architecture against the threat model**
>
> Open `docs/architecture/07-security-architecture.md` and `08-resilience-and-dr.md`.

Architecture 07 zones: untrusted Internet, semi-trusted edge TLS, trusted workloads, highly trusted control plane, restricted ACR/KV. Identity table: humans via Entra; ADO via OIDC; kubelet AcrPull; pods WI; cert-manager WI for DNS-01. Blast radius: Boutique pod can still reach cluster network until Topic 15 NPM; a single namespace is not a tenant.

Architecture 08: node loss automatic; AZ outage is rebuild; GitOps desync is Argo; unsigned deploy is Kyverno deny; TF lock is blob versioning; cert-manager is DNS-01 runbook; ACR unavailable needs re-mirror. **RTO (Recovery Time Objective)** 4–8 hours. **RPO (Recovery Point Objective)** 0 for state; Redis ephemeral. Multi-region out of scope.

> **Practice — Walk the operations catalog as a solo operator**
>
> Open `docs/operations/README.md` and sample sections 03, 07, 15, 17, 19.

On-call quick links (all “You”):

| Situation | First stop |
|-----------|------------|
| Boutique down | `docs/operations/17-common-incidents.md` |
| Bad digest | `docs/operations/03-rollback.md` |
| GitOps stuck | Applications in `argocd` |
| TLS | `14-certificate-rotation.md` |
| Teardown | `docs/runbooks/teardown.md` |

The index lists sections 01–20: overview, deployment, rollback, scaling, DR, backup, incident response, health checks, monitoring, alerting, logging, maintenance, upgrades, certificate rotation, secret rotation, troubleshooting, common incidents, recovery, postmortem, automation opportunities. Automation (`20-automation-opportunities.md`) is a backlog — it fed Phase 15+; it is not a bypass of `docs/setup/`.

> **Practice — Read the lightweight IR runbook**
>
> Open `docs/runbooks/incident-response.md`.

Severities S1–S4 (storefront down → informational). First response: acknowledge, smoke tests, Grafana, recent Git/Argo/pipeline/Terraform, **stop prod sync**. Suspected compromise: revoke ADO connection, rotate cosign keys, scale affected deploys to 0, preserve Loki/`kubectl logs`/Argo audit, rebuild from signed known-good digests. There is no forensics vendor and no 24×7 SOC.

Secret rotation (`docs/operations/15-secret-rotation.md`) and `docs/security/secrets-management.md` are the day-2 path for the critical asset. Certificate rotation is cert-manager plus DNS-01 troubleshooting.

`docs/operations/07-incident-response.md` assigns SEV and forbids Terraform destroy as first response:

| Severity | Example |
|----------|---------|
| SEV-1 | Prod storefront down |
| SEV-2 | Argo cannot sync; Kyverno down |
| SEV-3 | Single non-critical CrashLoop |
| SEV-4 | Dashboard gap |

You are the incident commander. Common-incident playbooks live in `17-common-incidents.md` (≥6 playbooks per the operations checklist). Recovery procedures: `18-recovery-procedures.md`. Postmortem: `19-postmortem-checklist.md` for SEV-1/2.

Architecture 07 tradeoffs table matches the book: Kyverno vs Azure Policy, key vs keyless, ADO approval vs PR reviewers, destroy ACR vs retain. Day-2 must not silently reverse those without an ADR.

`docs/operations/05-disaster-recovery.md` is thin by design: rebuild-from-git. `06-backup-and-restore.md` is thin: no Boutique database. Redis emptyDir is not backed up. Do not write an enterprise backup RPO you cannot test.

After teardown, IR is documentary: you cannot `kubectl`. Preserve Git, pipeline logs in ADO (if retention remains), and screenshots. That is the honest remaining evidence.

Review triggers in the threat model: external users, extra CI/registries, real PII/payment data, corporate Entra policies. Each trigger should reopen ADRs, not only dashboards.

## Operations files this chapter requires

Open with the threat model, not instead of it:

- `docs/operations/01-overview.md` through `20-automation-opportunities.md` — full catalog
- `docs/operations/03-rollback.md` — Git revert
- `docs/operations/07-incident-response.md` — SEV, no destroy-first
- `docs/operations/14-certificate-rotation.md` / `15-secret-rotation.md`
- `docs/operations/16-troubleshooting.md` / `17-common-incidents.md`
- `docs/operations/18-recovery-procedures.md` / `19-postmortem-checklist.md`
- `docs/runbooks/incident-response.md` / `promotion-rollback.md` / `teardown.md`
- `docs/troubleshooting/README.md` — symptom index

Automation opportunities fed Phase 15+; they are not permission to skip setup topics. After teardown, treat kubectl snippets as historical. Git, ADO logs (if retained), and screenshots are the remaining case file.

Limits: mock payments, no SOC, no pentest, no HSM. Review triggers in the threat model (external users, extra CI, real PII) reopen ADRs. Architecture 07’s pod blast radius still includes cluster network until Topic 15 NPM is lived.

## 4. Test the design under failure

### Independent control failure — Treat a restored storefront as restored trust

> **Practice — Separate availability from key compromise**
>
> Frontend `/_healthz` is 200 after a rollback. The incident was a leaked `cosign-private-key`. Grafana is green.

**Severity:** critical; signing authority may still be valid.  
**Plausible harm:** attacker signs a new digest; Kyverno admits it; Git looks “healthy.”  
**Potential blast radius:** all ACR repos and all Boutique namespaces on the cluster.  
**Bounded by:** Key Vault RBAC, key rotation in supply-chain.md, Kyverno PEM update, re-sign, ADO SC disable, ACR destroy on teardown.  
**Primary principles:** recovery, trustworthy evidence, identity is digest not tag, teardown is a production control.

#### Diagnosis

Smoke tests prove the SLI, not that the old private key is dead. Architecture 07 lists the key as restricted-zone material. Threat model lists it as critical.

#### Correction

Disable the pipeline connection. Rotate keys; update `02-verify-image-signatures.yaml`; re-sign; verify old signatures fail. If the incident is during teardown week, destroying ACR and the vault (Topic 13) is containment — then rebuild with a new pair. Postmortem: `docs/operations/19-postmortem-checklist.md`. Outcome evidence is Boutique up; recovery evidence is old key cannot admit images.

## Production reality

**Best Practice:** a written threat model that names signing keys and Git, plus runbooks a solo operator can execute.

**Production Practice:** STRIDE residual “Kyverno down” is operationally more likely than a novel APT. Alert `KyvernoAdmissionDown` plus fail-closed behavior is the control. “No SIEM” means repudiation evidence is ADO + Git, not Splunk.

Do not start `teardown.sh` as IR unless the decision is to eradicate the estate (compromise of subscription). Topic 13 is cost control and planned destroy, not first-response.

### Common errors

- Scoring every STRIDE cell “high” so nothing is prioritized.
- Copying GKE PagerDuty into this ops README.
- Declaring recovered because frontend 200 after a key leak.

## 5. What You Learned

The threat model names the cosign key, Git, ACR, and OIDC as the real assets. Architecture 07/08 bound isolation and DR to one region and a Git rebuild. Operations docs are a solo-operator handbook, not a SOC playbook. Incident response can freeze promotion and rotate keys. After teardown, honesty is that detection is offline and Git remains.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Threat model | `docs/security/threat-model.md` | Assets, STRIDE, residuals |
| Security architecture | `docs/architecture/07-security-architecture.md` | Zones and identities |
| Resilience | `docs/architecture/08-resilience-and-dr.md` | Failure table, RTO/RPO |
| Operations catalog | `docs/operations/README.md` plus 01–20 | Day-2 sections |
| IR runbook | `docs/runbooks/incident-response.md` | S1–S4 and compromise steps |
| Related | `docs/security/secrets-management.md`, `supply-chain.md` | Rotation |

## What changed

| Before | After |
|--------|--------|
| Tool list without assets. | **Threat model names the cosign key as critical.** |
| Git listed under ADO. | **Correct to GitHub vs pipelines (Independent Practice).** |
| Enterprise IR roster. | **You at L1–L3; SEV table in `07-incident-response.md`.** |
| Availability = recovery. | **Key rotation and ACR destroy as trust recovery.** |

`docs/operations/01-overview.md`, `02-deployment.md`, `08-health-checks.md`, `12-maintenance.md`, and `13-upgrades.md` complete the catalog even when this chapter sampled 03/07/15/17/19. Version upgrades must follow `versions.yaml` and ADRs, not `helm upgrade` memory. `docs/security/README.md` indexes threat-model, secrets, and supply-chain.

> **Independent Practice — Fix the Git hosting cell**
>
> The threat-model table places the Git repository under “Azure DevOps.” Write the corrected row (GitHub vs ADO) and one spoofing threat that mixing those platforms would create. Do not weaken OIDC to make the table “simpler.”
