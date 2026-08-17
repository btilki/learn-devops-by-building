# 03 — Reconcile Infrastructure Through Reviewed Changes

> **Outcome:** Bring an existing production service under declared ownership, review a saved change plan, separate planning from apply authority, detect drift, and reconcile through the reviewed path.

**Current Northwind state:** Chapter 2 produces a verified immutable artifact, but production infrastructure is still changed manually and has no trustworthy state binding.  
**Prerequisites:** Chapters 1–2, Terraform workflow familiarity, Git, and Python 3.12.  
**Implementation:** `books/labs/devops/northwind/`  
**Guided time:** approximately 105–135 minutes.

## 1. Production exists, but ownership is implicit

Northwind already runs `storefront-api`. An engineer created it during an incident and later added a workflow that can apply infrastructure changes from a pull request. State remains on whichever machine ran last.

The service is healthy, but three questions have no reliable answer:

- Which resource address owns the remote service?
- Does production match reviewed intent or an emergency console action?
- Can the organization prove that apply executed the plan reviewers saw?

> How can Northwind make reviewed configuration authoritative without destroying the production object it is adopting?

> **Practice — Establish the unmanaged baseline**
>
> Check out the real red state and observe which ownership, state, authority, and reconciliation contracts are absent.

```bash
cd books/labs/devops/northwind
git switch -c my-chapter-03 chapter-03-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-03-baseline
```

The command succeeds because red is expected. Its report should show no desired state, no resource binding, local unlocked state, one role for plan and apply, pull-request apply authority, and no digest-pinned deployment declaration.

The lab uses a deterministic local cloud fixture so every reader can exercise state, locking, stale plans, drift, and recovery without a cloud account. `tools/reconcile_infra.py` models the control semantics; production Terraform commands and backend boundaries are called out alongside it.

## 2. The production model: three representations, one transition

> *Theory — Desired state, state binding, and observed reality*
>
> Build the model needed to decide whether a difference should be imported, accepted into configuration, or reconciled out of production.

**IaC (Infrastructure as Code)** does not make a configuration file the truth by declaration. A reconciler reasons across three representations:

```text
configuration: what should exist
state:         which declared address owns which remote object
actual:        what the provider reports now
```

Terraform state primarily stores bindings between resource instances and remote objects. It is neither a complete design document nor a safe collaboration mechanism when copied between laptops. HashiCorp recommends remote state for team use and warns against storing state in version control because state can contain sensitive values and requires coordinated writes. [Terraform state](https://developer.hashicorp.com/terraform/language/state), [remote state](https://developer.hashicorp.com/terraform/language/state/remote).

A plan refreshes its view of actual objects, compares them with configuration and prior bindings, and proposes actions. It is evidence, not a guarantee: provider data or infrastructure may change after planning. A saved plan binds the reviewed actions to the configuration and inputs used to create it, but the apply path must still reject stale observations and serialize writers.

Locking protects state mutation from concurrent writers. It does not prove that a change is correct, prevent console drift, or replace review. Disabling locking because acquisition fails converts an operational problem into possible state corruption. Force-unlock is an exceptional recovery action and should target only a lock known to be abandoned. [Terraform state locking](https://developer.hashicorp.com/terraform/language/state/locking).

Drift is a difference, not automatically a defect. An emergency scale-up may be the correct actual state and stale configuration may be wrong. Before reconciliation, classify the difference:

1. revert actual infrastructure to reviewed intent;
2. update configuration to preserve an authorized emergency change;
3. import an existing object into the correct address;
4. stop because the plan exposes an unexpected replacement or ownership conflict.

## 3. Adopt the existing service without recreating it

> **Practice — Declare intent and import one binding**
>
> Describe the existing service, preserve Chapter 2's artifact digest, and bind the remote object to one declared address.

Create `infra/environments/production/desired.json`:

```json
{
  "name": "storefront-api",
  "artifact": "ghcr.io/northwind-commerce/storefront-api@sha256:ecc55173e6c10ec59cac9538a34ac7142c52e8ff504d7e045ed3103c650efb32",
  "replicas": 2,
  "admin_cidr": "10.40.0.0/16"
}
```

The **CIDR (Classless Inter-Domain Routing)** range and replica count are Northwind values, not defaults for other systems. The artifact is the digest verified in Chapter 2; infrastructure does not translate it back into a mutable tag.

Reset the fixture and inspect the unmanaged object:

```bash
make chapter-03-reset
python tools/reconcile_infra.py status
```

Now import it:

```bash
make chapter-03-import
python -m json.tool .northwind-infra/state-production.json
```

The state must contain one binding from `northwind_service.storefront` to `svc-northwind-production`. Import establishes ownership; it does not prove the configuration is complete or safe. Terraform likewise expects one remote object to map to one resource address. Declarative `import` blocks allow imports to participate in plan and review, while command-line import changes only state. [Import existing resources](https://developer.hashicorp.com/terraform/cli/import).

## 4. Make shared state a protected production dependency

> **Practice — Define the backend and authority contract**
>
> Replace laptop state and one shared administrator role with encrypted remote state, locking, and separate plan/apply identities.

Edit `infra/backend-policy.json`:

```json
{
  "backend": "remote",
  "encryption": true,
  "locking": true,
  "plan_role": "infrastructure-planner",
  "apply_role": "infrastructure-applier"
}
```

This policy is the runnable lab contract, not a substitute for configuring a real backend. As rechecked for this release, an Amazon **S3 (Simple Storage Service)** Terraform backend can use `encrypt = true`, bucket versioning, restricted object access, and `use_lockfile = true`; HashiCorp marks DynamoDB-based locking as deprecated and says it will be removed in a future minor version. Backend credentials should come from workload identity or the standard credential chain, not hardcoded configuration. [Terraform S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3).

State read access is sensitive too. A consumer of selected remote-state outputs generally has technical access to the entire snapshot. Prefer publishing non-sensitive outputs through a narrower configuration store when consumers do not need state access.

## 5. Reconcile the certificate lifecycle

> **Practice — Provision, renew, and fail closed**
>
> Declare certificate ownership and renewal behavior, verify the replacement served by the endpoint, and prove expiry cannot silently downgrade transport security.

Edit `infra/certificate-lifecycle.json`. Keep the hostname, service owner, issuer, and provisioning method explicit. Reference managed key material without embedding private-key bytes in infrastructure state. For Northwind's provider-neutral lab, use an illustrative 30-day renewal threshold and alert at 21 remaining days when no usable replacement exists. These are policy values, not universal service timings: a managed provider may control when renewal begins and may apply different eligibility rules by certificate origin and deployment. AWS Certificate Manager, for example, automatically renews only eligible certificates and exposes approaching-expiration and renewal-action events whose timing depends on certificate type and account configuration. [ACM managed renewal](https://docs.aws.amazon.com/acm/latest/userguide/managed-renewal.html), [ACM EventBridge events](https://docs.aws.amazon.com/acm/latest/userguide/supported-events.html).

Provisioning is only the first transition:

```text
declare hostname and owner
  → issue certificate
  → attach to endpoint
  → request renewal before expiry
  → overlap old and new validity
  → verify the endpoint serves the replacement
  → fail closed if no valid certificate remains
```

The replacement is not proven merely because the issuer created it. Verify the requested hostname, trust chain, validity window, and serial actually served by the production endpoint. Continue serving the old certificate while it remains valid if renewal is delayed; once no valid certificate exists, **TLS (Transport Layer Security)** must become unavailable rather than falling back to plaintext traffic.

Run the lifecycle conformance check:

```bash
make chapter-03-certificate
```

The evaluator uses `infra/certificate-expectations.json` as independent policy and `fixtures/certificates/renewal.json` as observed timing. It proves that renewal begins before expiry, old and new certificates overlap during the switch, the endpoint serves the verified replacement, an expired certificate fails closed, and plaintext fallback remains forbidden.

These controls cover provisioning, renewal, endpoint conformance, and expiry behavior. Private-key theft, issuer compromise, revocation after compromise, and forensic response belong to the DevSecOps book.

## 6. Produce reviewable change evidence

> **Practice — Create and inspect a saved plan**
>
> Compare declared and actual state, save the proposed transition, and inspect its configuration and observation identities before apply.

```bash
make chapter-03-plan
python -m json.tool .northwind-infra/production.plan.json
```

The first plan should contain no changes because the imported object already matches declared intent. It still records:

- the resource address;
- state serial;
- configuration digest;
- observed-infrastructure digest;
- proposed field changes;
- destructive-change count.

In Terraform automation, `terraform plan -out=tfplan` creates a saved opaque plan and `terraform show -json tfplan` produces machine-readable review input. Saved plan files can contain complete configuration, values, and sensitive data, so do not commit them or publish them as unrestricted artifacts. Applying a saved plan executes without another interactive approval; protection belongs before the apply job. [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan), [create and apply a saved plan](https://developer.hashicorp.com/terraform/tutorials/cli/plan).

```bash
make chapter-03-apply
```

The local apply rejects a changed configuration digest, changed observed digest, or held lock. It then updates actual infrastructure and state serial under the lock. Those checks model why a reviewed plan must not silently become an unreviewed re-plan.

## 7. Separate speculative planning from protected apply

> **Practice — Make pull requests read-only**
>
> Replace direct pull-request apply with a read-only plan job and a protected apply job that consumes the saved plan.

Edit `.github/workflows/infrastructure.yml`. The completed authority shape is:

```yaml
permissions:
  contents: read

jobs:
  plan:
    permissions:
      contents: read
    # Create and publish the short-lived saved plan.

  apply:
    if: github.event_name == 'workflow_dispatch'
    needs: plan
    environment: production-infrastructure
    permissions:
      contents: read
    # Download and apply the saved plan; do not use --auto-plan.
```

The repository's complete workflow contains the runnable local commands and short-lived artifact handoff. In production, plan and apply obtain different cloud identities. The planner needs read access sufficient to refresh and propose changes; the applier needs narrowly scoped mutation access. Repository environment protection, identity policy, and state-backend policy must agree—job names alone create no security boundary.

> **Practice — Verify reviewed reconciliation**
>
> Run one checkpoint across desired state, resource binding, certificate lifecycle, backend policy, workflow authority, actual agreement, and immutable artifact identity.

```bash
make chapter-03-checkpoint
```

Green means the system has an explicit desired state, a single imported binding, a verified certificate lifecycle, a locking/encryption policy, separate roles, protected apply, no pull-request apply path, actual agreement, and a digest-pinned artifact.

## 8. Detect, classify, and reconcile drift

**Severity:** capacity and cost deviation; no immediate outage.  
**Potential blast radius:** one production service.  
**Bounded by:** read-only detection, a one-resource plan, saved-plan freshness checks, and state locking.  
**Primary principles:** reconciliation, trustworthy evidence, and recovery.

> **Practice — Reconcile a console scale-up**
>
> Introduce an out-of-band replica change, inspect the proposed correction, decide whether intent or reality should win, and verify recovery.

```bash
make chapter-03-break
python tools/reconcile_infra.py status
make chapter-03-plan
```

The plan should propose one non-destructive change: replicas from five back to two. Do not apply merely because drift exists. Assume incident command confirms that the scale-up was temporary and the service is stable at two replicas. Reviewed intent should therefore win.

```bash
make chapter-03-apply
make chapter-03-checkpoint
```

If the five replicas were still required, recovery would instead mean changing `desired.json`, reviewing the cost and capacity effect, producing a fresh plan, and applying that intent. A refresh-only operation can inspect or record drift without changing remote infrastructure; it should not be used to make an emergency change authoritative without review. [Manage resource drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift).

## 9. Production reality

**Best Practice:** keep configuration and state under explicit ownership, plan every change, serialize writes, and apply reviewed intent through constrained automation.

**Production Practice:** design for provider failure, stale evidence, sensitive state, partial apply, imports, refactors, certificate renewal failure, and emergency actions.

- Partition state by ownership and blast radius, not merely by folder aesthetics. One global state couples unrelated changes and recovery.
- Back up and version state, but exercise restoration. Never edit state files directly; use supported state commands and preserve lineage and serial protections.
- Treat `-target`, `-refresh=false`, forced state push, and force-unlock as exceptional operations with recorded justification and follow-up reconciliation.
- Review replacements and destructive actions separately. A syntactically valid plan can still delete the wrong production object.
- Use `moved` blocks for reviewed address refactors and import blocks for adoption. Never bind one remote object to multiple addresses.
- Define an emergency-change path that records actor, reason, expiry, and follow-up owner. Drift detection without ownership becomes alert noise.
- Monitor certificate issuance and endpoint conformance separately. An issuer can report success while the load balancer continues serving the old serial.

## 10. What changed

| Before | After |
|---|---|
| Production existed outside declared ownership. | One state address owns the imported remote object. |
| State lived locally without coordination. | Remote, encrypted, locked state is an explicit policy. |
| Pull requests could apply directly. | Planning is read-only; apply uses separate protected authority. |
| Review described source files only. | A saved plan records the proposed transition and observation. |
| Certificate creation implied durable transport security. | Ownership, renewal lead time, overlap, endpoint verification, alerting, and expiry behavior are explicit. |
| Console drift was ambiguous. | Drift is detected, classified, reconciled, and verified. |
| Deployment could lose artifact identity. | Desired infrastructure carries Chapter 2's immutable digest. |

Northwind now has a reviewed reconciliation path. Configuration expresses intent, state records ownership, planning exposes consequences, apply is serialized and protected, and recovery ends only when actual infrastructure agrees with the chosen intent.

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Infrastructure and certificate ownership contract | `infra/environments/production/desired.json`, `infra/backend-policy.json`, and `infra/certificate-lifecycle.json` | Together they record the reviewed resource identity, immutable artifact, desired values, certificate lifecycle, state boundary, locking, encryption, and apply authority. |
| Plan and drift evidence bundle | `.northwind-infra/production.plan.json` and `evidence/chapter-03-green.json` | Retain the reviewed plan with actor, source revision, expiry, and apply result outside the local ignored directory; it is the decision record used to explain adoption, drift, and recovery. |

## What You Learned

Infrastructure as code is an ownership and reconciliation system, not only configuration syntax. You can now adopt an existing resource without recreation, preserve immutable artifact identity, reconcile certificate issuance and renewal, fail closed after expiry, separate planning from apply authority, require locked remote state, interpret a saved plan, classify drift, and verify recovery through agreement among configuration, state, and observed infrastructure.

### Prove It

> **Independent Practice — Adopt a shared production database**
>
> Design an import and state-boundary plan for a database already used by three services without recreating it or granting every team state access.

Specify the resource address and owner, discovery and backup evidence, import method, configuration-completeness check, state boundary, read/apply identities, first saved-plan acceptance criteria, handling of sensitive outputs, rollback limitations, and response to a plan that proposes replacement. Explain how emergency console changes become reviewed intent or are reconciled away.

## Next

Northwind can now reconcile the infrastructure that carries its verified artifact. Chapter 4 establishes the Kubernetes runtime contract: scheduling, resource boundaries, health semantics, disruption control, and safe workload identity inside that infrastructure.
