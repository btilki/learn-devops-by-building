# Govern Delegation and Privileged Operations

Chapter 4 bounded normal identity and authorization. Production still needs exceptional access: responders isolate workloads, operators revoke identities, support engineers diagnose sensitive failures, and automation sometimes acts on delegated authority. If those paths become permanent, self-approved, or unaudited, they recreate the privilege Chapter 4 removed.

## 1. Emergency access without a contract

A compromised maintainer claims an emergency, approves their own elevation, requests production reconciliation for a day, and records a review before the session has even ended. The word “emergency” does not make the authority legitimate, and a completed field does not prove that a lifecycle occurred.

Work from the lab working tree using the Chapter 0 procedure. From the DevSecOps lab root, run:

```bash
make chapter-05-baseline
```

The baseline reads the unsafe request fixture rather than synthesizing an attack in memory. It succeeds when self-approval, excessive duration, an out-of-scope action, and impossible lifecycle ordering are rejected independently.

## 2. The production model: privilege is bounded delegation

> *Theory — Delegation, elevation, and break glass*
>
> This model enables Northwind to grant exceptional authority without creating a permanent or unowned bypass.

Delegation allows one authorized subject to confer a bounded capability on another. Elevation temporarily increases a subject's authority. Impersonation acts as another subject and therefore demands especially strong purpose and evidence. A support engineer may temporarily elevate or impersonate here, but Chapter 10 decides which customer fields that subject may access for a declared support purpose. Break glass is a predesigned emergency path, not permission to ignore identity and policy.

| Element | Required decision |
|---|---|
| Requester and subject | Who asks, and who will exercise the authority? |
| Approver | Which independent authority may approve it? |
| Purpose | Which declared production condition justifies access? |
| Scope | Which action, resource, and environment are permitted? |
| Duration | When does authority expire automatically? |
| Evidence | Which request, decision, use, and revocation events remain? |
| Review | Who determines whether use was justified and controls should change? |

Just-in-time access limits duration. Just-enough administration limits scope. Neither is sufficient without attribution, independent approval, revocation, and review.

## 3. Define the privileged workflow

> **Practice — Bound privileged authority**
>
> Define the maximum duration, allowed emergency actions, approval separation, and required evidence.

Open `privilege/policy.yaml`. Northwind permits only `isolate-workload` and `revoke-subject` through this break-glass path, for at most 30 minutes. Production reconciliation is deliberately excluded.

> **Practice — Record an independently approved request**
>
> Bind requester, subject, approver, purpose, action, resource, duration, and incident ticket.

The approved fixture gives `responder-alice` permission to isolate `order-worker` for 15 minutes under `SEC-1042`. The incident commander approves; the requester cannot approve themselves. `self_approval_allowed: false` is evaluated policy, not documentation.

> **Practice — Close the delegation lifecycle**
>
> Expire or revoke access and complete after-action review while the decision evidence remains attributable.

Open `privilege/requests/approved.yaml` and follow its timestamps: requested, approved, issued, ended, then reviewed. `privilege/sessions.jsonl` separately preserves requested, approved, used, revoked, and reviewed events. The evaluator rejects an impossible sequence and enforces the policy's maximum duration and review deadline.

The review is not ceremony. It asks whether the emergency path was necessary, whether scope was excessive, whether ordinary controls failed, and whether policy or automation should change. Dual control means the requester cannot authorize their own exceptional authority. For emergency changes to production, this break-glass contract may grant narrow containment actions, but the production change still travels through the separately governed release path.

### Prove the capability

Run:

```bash
make audit chapter-05-checkpoint
```

The audit validates the request against `schemas/privilege-request.schema.json`. The checkpoint verifies required fields, independent approval, bounded duration and action, valid chronology, and timely review. It models the workflow locally; it does not grant real production privilege.

## 4. Test the decision under failure

### Cumulative attack — Invent an emergency and self-approve elevation

> **Practice — Reject privileged self-escalation**
>
> Exercise an invented emergency that requests excessive production authority without independent review.

**Severity:** critical—the request seeks self-approved production authority outside the emergency allowlist.  
**Plausible harm:** malicious deployment, concealment of source compromise, and progression toward payment authority.  
**Potential blast radius:** production resources reachable by the requested reconciliation authority.  
**Bounded by:** action allowlist, independent approval, short expiry, individual identity, revocation, and review.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, and recovery.

#### Security questions

- **Asset and harm:** Release authority and production integrity drive the decision.
- **Trust and authority:** Emergency declaration does not authorize self-approved reconciliation.
- **Detection after prevention fails:** The denied request preserves requester, purpose, scope, duration, and missing review.
- **Evidence of restored trust:** Not yet applicable. Chapter-local correction: no elevation was issued; the initiating identity remains subject to Chapter 4 revocation and investigation.

#### Diagnosis

Run `make chapter-05-attack`. The request fails self-approval, duration, action-scope, and lifecycle-order requirements independently. The attack remains denied even if any one of the other controls were misconfigured.

#### Containment

Run `make chapter-05-contain`. It proves that the denied authority was never issued and has no entry in session-use evidence. The initiating identity remains subject to the revocation and investigation path established in Chapter 4.

#### Recovery

Run `make chapter-05-recover`. Recovery proves more than denial: a legitimate responder can still complete the requested, independently approved, used, revoked, and reviewed lifecycle. Use a real incident identifier, an authorized independent approver, the narrow containment action, a short duration, automatic expiry, attributable session evidence, and after-action review.

## 5. Production reality

**Best Practice:** prefer individual, just-in-time, just-enough privilege with automatic expiry.

**Production Practice:** test approval availability, identity-provider failure, revocation delay, evidence retention, and the ability to use break glass during the very outage it is meant to address. A path that cannot work under failure will be bypassed; a path that never expires will become normal access.

## 6. What changed

| Before | After |
|---|---|
| Emergency access implied broad bypass. | **Break glass permits only declared containment actions.** |
| Requesters could approve themselves. | **Independent approval separates request from authorization.** |
| Privilege persisted until someone remembered it. | **Duration and revocation close authority automatically.** |
| Purpose was free-form justification. | **Purpose, ticket, action, resource, and subject form a reviewable contract.** |
| Use ended without learning. | **After-action review can redesign the failed normal path.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Privileged-access decision contract | `privilege/policy.yaml` and `privilege/requests/approved.yaml` | They retain approval separation, purpose, scope, chronology, duration, and review. |
| Privileged session evidence | `privilege/sessions.jsonl` | It distinguishes request, approval, use, revocation, and review as attributable events. |
| Privilege-request schema | `schemas/privilege-request.schema.json` | It prevents incomplete lifecycle records from being accepted as evidence. |
| Break-glass mini-runbook | `privilege/break-glass-runbook.md` | It preserves the emergency sequence, revocation, and after-action obligations. |

## What You Learned

Privileged access is a bounded delegation lifecycle, not a special role assigned forever. Requester, subject, approver, purpose, scope, duration, evidence, revocation, and review must agree. Break glass remains narrow and attributable even when normal operations fail.

### Prove It

> **Independent Practice — Design provider emergency access**
>
> Define a temporary path for reconciling payment-provider state without granting general payment or deployment authority.

Specify the approver, subject, permitted observations and actions, transaction bounds, duration, evidence, revocation, and after-action review.

## Next

Identity and privilege paths are bounded. Attacker-controlled source and dependency inputs can still enter the build under valid maintainer authority. Chapter 6 establishes trust in source and dependencies.
