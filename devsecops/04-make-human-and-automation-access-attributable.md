# Make Human and Automation Access Attributable

Northwind has selected controls for the compromised-maintainer path. The first implementation problem is identity. A valid credential can still represent the wrong subject, target the wrong audience, live too long, or exercise authority accumulated for another purpose.

This chapter makes human and automation actions attributable and authorization decisions bounded by subject, action, resource, environment, issuer, audience, lifetime, and current status.

## 1. Valid credentials with ambiguous authority

Northwind begins with shared access patterns, reusable automation tokens, and inherited roles. A maintainer credential can propose source changes, but accumulated production authority makes the same session capable of attempting deployment. Automation tokens survive beyond one run and can be replayed outside their intended system.

Work from the lab working tree using the How to Use This Book procedure. From the DevSecOps lab root, run:

```bash
make chapter-04-baseline
```

The baseline succeeds when it reproduces the unsafe start state:

```text
chapter 04 baseline: shared subject allowed unattributable production authority with a reusable day-long token
```

One shared subject, `northwind-ci`, presents a day-long reusable token to production and is allowed to reconcile the deployment. The decision also carries no policy version, so nothing in the record explains which rules produced it or which human or workflow acted. Both halves matter: the authority is too broad, and the evidence cannot survive later investigation.

## 2. The production model: identity claims authorize context, not possession

> *Theory — Attributable identity and bounded authorization*
>
> This model enables Northwind to distinguish a verified subject from the actions that subject may perform in one resource, environment, audience, and time boundary.

### Authentication and authorization answer different questions

Authentication establishes which subject a verifier believes is present and why. Authorization decides whether that subject may perform one action on one resource under the current context.

Session assurance is the confidence attached to that authentication event: how the subject authenticated, whether stronger factors or device checks were required, how recently authentication occurred, and whether the session satisfies the sensitivity of the requested action. It is contextual evidence, not a permanent property of the user.

| Decision | Question | Required context |
|---|---|---|
| Authentication | Which subject presented this claim, and which issuer vouches for it? | Subject, issuer, session assurance, expiry |
| Authorization | May this subject perform this action here and now? | Action, resource, environment, role or attributes, policy version |
| Attribution | Can later evidence connect the action to the subject and decision? | Stable subject, claim identity, request context, result, reason |

Authentication success must not imply authorization. A maintainer may be authentic and still have no production deployment authority.

### Human, automation, and workload identities need distinct subjects

A shared account destroys attribution. A human, release workflow, deployment controller, and runtime workload have different lifecycles, evidence, and authority. They must not collapse into “CI” or “service account.”

Automation should exchange short-lived federated proof for target-specific access. The token audience identifies the intended receiver. Lifetime bounds replay. The subject identifies the workflow or controller. Policy restricts the permitted action and resource.

### Issuer trust is not subject authorization

An issuer can mint tokens for several audiences. Trusting `northwind-oidc` for both registry and production does not mean every subject from that issuer belongs in both systems.

Northwind therefore binds audiences twice:

- the trust policy states which audiences an issuer may assert; and
- the subject register states which of those audiences belong to that subject.

This prevents a release workflow from presenting a cryptographically valid production-audience token when its purpose is artifact publication.

## 3. Implement the identity and authorization contract

> **Practice — Register attributable subjects**
>
> Replace shared identities with stable human and automation subjects, explicit issuers, audiences, roles, and revocation state.

Replace the shared `northwind-ci` entry in `identity/subjects.yaml` with subjects that have their own issuer, audience, role, and status:

```yaml
subjects:
  - {id: maintainer-alice, type: human, issuer: northwind-human-idp, audiences: [northwind-source], roles: [source-maintainer], status: active}
  - {id: release-workflow, type: automation, issuer: northwind-oidc, audiences: [northwind-registry], roles: [artifact-publisher], status: active}
  - {id: deployment-controller, type: automation, issuer: northwind-oidc, audiences: [northwind-production], roles: [production-reconciler], status: active}
  - {id: compromised-session, type: human, issuer: northwind-human-idp, audiences: [northwind-source], roles: [source-maintainer], status: active}
```

`compromised-session` is the modeled stolen maintainer session used by later attack, detection, and containment evidence. It remains `active` in the operational register through Chapter 13. Chapter 4 containment writes a generated revocation snapshot; Chapter 14 is the first command that revokes this subject in `identity/subjects.yaml`. Keeping a stable identifier lets denial, replay, and incident evidence stay attributable rather than collapsing into an unknown subject.

> **Practice — Bound roles by action, resource, and environment**
>
> Make authority narrow enough that a valid identity cannot silently inherit production actions.

Split the accumulated `maintainer` role in `identity/roles.yaml` into one role per authority. `source-maintainer` permits `propose-change` on `northwind-source` in the repository environment:

```yaml
policy_version: "2026-08-15.1"
roles:
  - id: source-maintainer
    allows:
      - {action: propose-change, resource: northwind-source, environment: repository}
```

It does not permit artifact publication or production reconciliation. Separate automation subjects own those actions. The `policy_version` is not decoration: every decision trace records it, so a later investigation can tell whether an allowed action was permitted by the rules in force at the time or by rules that have since changed.

> **Practice — Validate issuer, audience, lifetime, and replay behavior**
>
> Reject claims that are valid-looking but intended for another receiver, too long-lived, reusable, or revoked.

Bound sessions and replay in `identity/trust-policy.yaml` with `max_session_seconds: 3600` and `reusable_tokens_allowed: false`, then narrow each issuer to the audiences it may assert. The evaluator now checks subject status, issuer, issuer audience, subject audience, maximum session lifetime, reusable-token policy, role, action, resource, and environment. Its result retains denial reasons instead of returning an unexplained Boolean.

> **Practice — Emit a decision trace that survives the decision**
>
> Make every allow and deny reconstructable without access to the running evaluator.

Each decision appends one line to `identity/access-events.jsonl` binding subject, action, resource, environment, issuer, audience, session lifetime, reusable claim, both policy versions, result, and reasons. Abridged to the fields that carry the denial:

```json
{"subject": "release-workflow", "action": "publish-artifact", "resource": "northwind-registry",
 "audience": "northwind-production", "result": "deny", "reasons": ["audience-rejected"]}
```

An allow with no trace and a deny with no reason are equally unusable later. Chapter 13 correlates these events with dependency, elevation, and runtime signals, so the fields it needs must exist at the moment of the decision, not be reconstructed afterward.

### Prove the capability

```bash
make audit
make chapter-04-checkpoint
```

The checkpoint proves that a maintainer can propose source, the release workflow can publish to the registry, and only the deployment controller can reconcile production. It also proves the two denials that matter most — a maintainer session attempting production reconciliation, and the release workflow presenting a production audience — and it fails if any emitted trace is missing a field. It does not exercise a real identity provider or cloud authorization service.

## 4. Test the design under failure

### Cumulative attack — Reuse maintainer identity as production authority

> **Practice — Deny and recover from compromised identity use**
>
> Exercise the reusable-token and inherited-role attempt, revoke its subject, and prove legitimate automation remains functional.

**Severity:** high; successful misuse could change the production workload.  
**Plausible harm:** malicious release, loss of attribution, unauthorized production state, and progression toward payment authority.  
**Potential blast radius:** Northwind production resources reachable by the inherited role.  
**Bounded by:** subject-specific audiences, short lifetime, non-reusable proof, narrow roles, explicit denial evidence, and revocation.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Release authority and order outcomes are exposed to malicious production change.
- **Trust and authority:** A valid maintainer session has source authority only; it must not inherit registry or production authority.
- **Detection after prevention fails:** Denial events preserve subject, attempted action, resource, audience, and reason.
- **Evidence of restored trust:** Not yet applicable. Chapter-local recovery: the compromised subject fails after generated revocation while legitimate release automation still publishes with the correct audience.

#### Diagnosis

Run `make chapter-04-attack`. The modeled session is still active, but it is reusable, too long-lived, aimed at the wrong audience, and lacks the production role. Four independent controls deny it before revocation. Read the last line of `identity/access-events.jsonl`: the denial carries a stable claim identifier, subject, attempted action and resource, presented audience, session lifetime, and policy versions. That is what makes the event usable as detection input instead of noise.

Run `make test`. The Chapter 4 mutation tests relax one control at a time — issuer audiences, subject audiences, revocation, session lifetime, reusable tokens, and role scope — and require that the same production attempt still fails. With every control relaxed the attempt is allowed, which is what keeps the test honest: it proves each control is independently load-bearing rather than proving the denial once and calling it depth.

Those mutations exposed a subtler defect. Issuer-level audience trust originally allowed the release workflow to present a production audience, because `northwind-oidc` legitimately serves both the registry and production. Binding audience to the subject as well closed that gap, and the checkpoint now holds the boundary as an explicit deny case.

#### Containment

Run `make chapter-04-contain`. This performs the containment transition in generated state: it copies the register, revokes `compromised-session` in that copy, denies a claim that would otherwise permit source access specifically because of revocation, and writes `build/chapter-04-contained.yaml`. It does not mutate `identity/subjects.yaml`. Preserve the claim identifier and denial reasons in `identity/access-events.jsonl` for Chapter 13 correlation. Operational revocation of this session waits for Chapter 14.

#### Recovery

Run `make chapter-04-recover`. Recovery passes only when the old session remains denied and legitimate registry automation remains allowed. Revocation that breaks every workflow is containment without operational recovery.

## 5. Production reality

**Best Practice:** use individual human identities and short-lived federated automation identities with least authority.

**Production Practice:** validate issuer configuration, subject mapping, audience semantics, session assurance, policy propagation, revocation delay, clock behavior, and audit completeness in the actual systems. **OIDC (OpenID Connect)** requires a client to reject an ID token whose audience does not include that client; a cryptographically valid token for another audience is not authorization. [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html).

Role names are not evidence of narrow authority. Expand them into concrete actions and resources. Review role accumulation, dormant subjects, issuer changes, and machine identities that no owner can explain.

## 6. What changed

| Before | After |
|---|---|
| Shared identities obscured who acted. | **Human and automation subjects are distinct and attributable.** |
| Authentication implied authorization. | **Every decision binds subject, action, resource, environment, and policy context.** |
| Issuer trust applied to every subject audience. | **Issuer and subject audience constraints must both pass.** |
| Reusable tokens survived workflow execution. | **Short-lived, non-reusable proof is required.** |
| Maintainer roles accumulated production authority. | **Source, publication, and reconciliation authority belong to separate subjects.** |
| Decisions left no record of their own context. | **Every allow and deny emits a trace carrying claims, policy versions, and reasons.** |
| Revocation success could break all automation. | **Recovery proves compromised access fails while legitimate automation works.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Identity and trust inventory | `identity/subjects.yaml` and `identity/trust-policy.yaml` | They retain subject, issuer, audience, lifetime, replay, and revocation boundaries. |
| Authorization matrix | `identity/roles.yaml` | It makes permitted actions, resources, environments, policy version, and separation of authority reviewable. |

Decision traces accumulate in `identity/access-events.jsonl`. That file is generated evidence rather than a reviewed artifact, so it stays out of version control, but its field contract is what Chapter 13 builds detections on.

## What You Learned

Authentication establishes a subject claim; authorization decides one contextual action; attribution preserves who attempted what and why it was allowed or denied. Issuer trust, subject audience, lifetime, role, resource, and revocation must all agree. Recovery proves compromised authority stays invalid without disabling legitimate automation.

### Prove It

> **Independent Practice — Add read-only production diagnosis**
>
> Design a short-lived human diagnostic role without turning observation into deployment authority.

Specify the subject, issuer, audience, session assurance, permitted observations, prohibited changes, expiry, revocation, and audit evidence. Explain why reusing the deployment-controller role would destroy attribution and separation of authority.

## Next

Normal identities are now attributable and bounded. Exceptional delegation, temporary elevation, impersonation, and break-glass access can still create an unowned bypass.

Chapter 5 governs privileged operations and delegation.
