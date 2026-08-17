# 05 — Replace Static Secrets with Workload Identity

> **Outcome:** Give `order-worker` attributable, scoped, short-lived dependency access and recover from credential compromise without rebuilding the application.

**Current Northwind state:** Chapter 4 establishes the runtime-identity pattern for `storefront-api`, but `order-worker` still uses the default service account and implied static dependency credentials.  
**Prerequisites:** Chapters 1–4, Kubernetes service accounts, and authorization-policy fundamentals.  
**Implementation:** `books/labs/devops/northwind/`  
**Guided time:** approximately 90–120 minutes.

## 1. A service account name is not dependency access

`order-worker` needs the broker, PostgreSQL, cloud services, and the payment provider. The unsafe design mounts long-lived credentials as environment values under the default service account. A copied value remains usable outside the Pod, rotation needs a redeploy, and audit records cannot reliably identify the workload that acted.

> How can Northwind authenticate a workload to each dependency with bounded authority, while still handling a payment provider that accepts only an **API (Application Programming Interface)** key?

> **Practice — Establish the reusable-credential baseline**
>
> Check out the broad static-credential design and prove identity, federation, scope, rotation, revocation, break-glass, and evidence controls are red.

```bash
cd books/labs/devops/northwind
git switch -c my-chapter-05 chapter-05-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-05-baseline
```

## 2. The production model: prove identity, then authorize

> *Theory — Federated workload identity*
>
> Decide which runtime subject may exchange bounded proof for short-lived, dependency-specific access.

A secret answers “who possesses this value?” Workload identity answers “which verified runtime subject is asking, for which audience, through which issuer, and until when?” The dependency or an identity broker validates that proof, applies policy, and returns bounded access.

```text
Pod + dedicated service account
              ↓ projected, short-lived proof
trusted issuer → subject + audience + expiry → dependency policy
              ↓
       short-lived scoped access
```

The proof is not authority by itself. The trust binding maps a precise subject—namespace plus service account—to allowed audiences and roles. A valid token for the wrong audience or an untrusted issuer must fail.

Kubernetes recommends short-lived projected service-account tokens; the kubelet rotates them, and recipients should validate audience and expiry. [Kubernetes service accounts](https://kubernetes.io/docs/concepts/security/service-accounts/).

## 3. Bind a dedicated runtime subject

> **Practice — Replace the default workload identity**
>
> Bind `order-worker` to its dedicated service account and deliver an audience-bound, short-lived, automatically refreshed token through a projected file.

Edit `security/workload-identity.json`. Set `kubernetes_service_account` to `order-worker`. Configure the token as `projected-file`, then enable audience binding, short lifetime, and automatic refresh.

Use a file because rotation replaces projected content while the process remains alive. The client must reread the file or use a credential library that does; reading once at startup converts an automatically rotated token into an eventual outage. Do not mount the projection through `subPath`, because Kubernetes documents that this prevents projected-volume updates from reaching the container. [Projected volumes](https://kubernetes.io/docs/concepts/storage/projected-volumes/).

Disable automatic service-account token mounting for workloads that do not need it. For `order-worker`, request only the audience used by the identity exchange—not a generic administrative audience.

## 4. Federate supported dependencies

> **Practice — Exchange proof instead of distributing credentials**
>
> Enable federation for cloud, broker, and database access, then constrain authorization to dependency-specific roles with default deny.

Set the three federation values to true. Set authorization scope to `dependency-specific` and `default_deny` to true.

The exact exchange is provider-specific. A cloud platform may trust Kubernetes **OIDC (OpenID Connect)** claims and issue temporary role credentials; a broker may map the same subject to publish or consume permissions; a database proxy may mint a short-lived login. The common contract is stable:

- trust the exact issuer rather than any cluster,
- match namespace and service-account subject,
- validate the intended audience,
- grant only required actions and resources,
- limit session duration,
- log issuance and authorization decisions.

Amazon's workload-identity documentation illustrates this boundary: **IAM (Identity and Access Management)** permissions can be scoped to one service account, but containers remain outside the identity mechanism's security boundary and node credential paths must still be restricted. [IAM roles for service accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html).

## 5. Handle a provider that cannot federate

> **Practice — Broker the unavoidable payment secret**
>
> Replace the literal environment value with a brokered file reference that supports overlapping rotation and live reload.

Keep `payment_provider.supports_federation` false. Set credential delivery to `brokered-file-reference`, rotation to `overlapping-live-reload`, and enable an overlap window.

Workload identity authenticates `order-worker` to the secret broker; it does not transform the provider's static key into a federated credential. The broker returns or projects the currently authorized provider key without storing that value in Git, an image, a manifest, or an environment variable.

Rotation uses a measured overlap: introduce the new provider key, make workloads reload it, verify successful calls use the new version, then revoke the old key. The overlap is not indefinite. Record ownership, maximum duration, rollback condition, and evidence that no workload still uses the retiring version.

Never log the token, provider key, authorization header, or projected file content. Record safe metadata such as credential version, subject, audience, issuer, expiry, decision, and request correlation.

## 6. Make revocation and emergency access operational

> **Practice — Define compromise controls**
>
> Allow trust revocation without rebuilding the application and replace shared emergency access with approved, time-bound individual identity.

Enable both revocation controls. Set the break-glass identity to `individual-federated-operator`, then require time bounds and approval.

Short lifetime limits persistence but does not replace revocation. Northwind must be able to disable the subject-to-role binding, quarantine the affected workload, and revoke a brokered provider key independently. Recovery issues fresh access only after workload artifact, configuration, and runtime identity are verified.

Break-glass access is for identity-system or control-plane failure, not convenience. It needs named ownership, strong authentication, narrow emergency scope, expiry, independent approval where available, alerting on use, and a post-use review. A shared administrator token defeats attribution precisely when evidence matters most.

## 7. Prove identity decisions without exposing credentials

> **Practice — Make the identity contract auditable**
>
> Record subject, audience, issuer, expiry, and authorization decision while requiring credential redaction.

Enable every field under `evidence`, then verify the full contract:

```bash
make chapter-05-checkpoint
```

The checkpoint proves policy structure, not a live provider exchange. Production must test token refresh during long-running work, issuer-key rotation, clock skew, broker or identity-provider outage, policy propagation delay, node credential isolation, payment-key rollover, and audit-log delivery failure.

## 8. Reject a stolen token and restore legitimate access

**Severity:** compromised workload credential with attempted lateral access.  
**Potential blast radius:** `order-worker` and explicitly authorized dependency actions.  
**Bounded by:** exact subject binding, audience validation, short expiry, default deny, dependency-specific policy, and independent provider-key revocation.  
**Primary principles:** explicit contracts, blast-radius control, trustworthy evidence, and recovery.

> **Practice — Exercise credential compromise**
>
> Replay a stolen payment-broker token against an administrative audience after revocation, then prove a verified replacement workload can obtain fresh access.

```bash
make chapter-05-break
```

The report must show `wrong_audience_is_rejected`, `revoked_binding_is_rejected`, `static_fallback_is_not_exposed`, and `verified_workload_can_recover` as true.

Rejected replay is containment, not recovery. Quarantine the suspect Pod and node when appropriate, revoke its trust binding, rotate any provider secret it could read, search decision logs for the subject and credential version, verify no unauthorized effect occurred, deploy the verified artifact under fresh identity, and confirm legitimate dependency calls recover.

## 9. Production reality

**Best Practice:** prefer workload federation, short-lived audience-bound proof, dependency-specific authorization, automatic refresh, independent revocation, and attributable emergency access.

**Production Practice:** inventory which dependencies really support federation; test token refresh and policy propagation; restrict alternate credential paths; design rotation overlap; protect issuer keys, identity brokers, and audit pipelines; and retain a rehearsed emergency path. A service account, sidecar, or secret store is not safe merely because it exists—its trust and failure boundaries must be verified.

## 10. What changed

| Before | After |
|---|---|
| The default service account represented multiple workloads. | `order-worker` has an attributable runtime subject. |
| Reusable values supplied dependency access. | Supported dependencies exchange short-lived workload proof. |
| Wildcard policy made compromise lateral. | Audience and dependency-specific default-deny policy bound authority. |
| Payment credentials were literal environment data. | An unavoidable provider key is brokered, referenced, reloaded, and rotated. |
| Rotation and revocation required redeployment. | Trust and credential versions change independently of application builds. |
| Shared emergency access obscured attribution. | Individual, approved, expiring break-glass access is audited. |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Workload identity and authorization contract | `security/workload-identity.json` | It records subject, audience, lifetime, dependency permissions, brokered-secret handling, revocation, and emergency authority without storing credential material. |
| Identity conformance evidence | `evidence/chapter-05-green.json` | It preserves the accepted policy checks so future identity or provider changes can be compared with the last verified boundary. |

## What You Learned

Workload identity separates runtime proof from authorization and removes reusable credentials where dependencies can federate. You can now bind a precise workload subject, constrain audience and policy, handle a non-federating provider honestly, rotate and revoke access independently, and verify compromise recovery without putting credential material into evidence.

### Prove It

> **Independent Practice — Survive identity-provider unavailability**
>
> Design `order-worker` behavior when existing credentials expire in 20 minutes but the identity exchange is unavailable for 45 minutes.

Define refresh timing, retry and jitter, cached-credential rules, admission of new work, queue backpressure, payment behavior, fail-open versus fail-closed decisions, alerts, break-glass authority, recovery verification, and evidence that no expired or wrong-audience credential was accepted. Justify how the design avoids turning identity recovery into duplicate order effects.

## Next

Northwind now has attributable, bounded dependency access. Chapter 6 makes production behavior explainable while keeping tokens, provider keys, and sensitive payloads out of telemetry.
