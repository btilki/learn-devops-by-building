# Enforce Guardrails Without a Golden Cage

Chapter 8 scoped the reconciler. The plane is a product. Delivery and security defaults from earlier books are still either mandatory with no exit or optional with no owner. A cage drives unofficial forks. Missing defaults recreate the copy-paste path Chapter 5 already failed. Chapter 5 named remaining guardrails: `artifact-digest`, `workload-identity-claims`, and `no-cluster-admin`. An exit is not an exception to digest identity. This chapter must bind those defaults, not invent a third naming scheme.

The production question is now:

> Which defaults must the platform enforce, and how do exceptions stay temporary without trapping teams?

A golden cage blocks the Chapter 5 exit. A scorecard that stays green after an inherited exception expires, while Fulfillment disables digest pinning, is not a road. This chapter records owned defaults, scorecards that cannot emit their own grade, and exception rows that only bind an inherited DevSecOps exception ID. Owner, scope, compensation, and expiry stay on the inherited record. The platform adds tenant, remaining isolation, and scorecard effect.

## 1. A green scorecard after the exception expired

A weak record says:

```yaml
system: fulfillment-api
defaults_present: [workload-identity-claims, no-cluster-admin]
reported_status: green
exception: exception-dependency-mirror-2026-08
owner: platform-security
expires_at: "2026-12-01T00:00:00Z"
```

It does not identify Chapter 5 remaining guardrails as the default set, a living platform owner, an exit that is still allowed, or expiry resolved from the inherited exception. Copying `expires_at` onto the platform row lets someone extend a date without renewing the DevSecOps exception. Forbidding exits turns the paved road into a cage. “Green” may describe a portal badge. It cannot survive an expired exception and a disabled digest.

Work from the lab working tree using the How to Use This Book procedure. From the Platform lab root, run the Chapter 9 baseline:

```bash
make chapter-09-baseline
```

The command succeeds when it detects the intended unsafe guardrails:

```text
chapter 09 baseline: expired exception green scorecard correctly detected
```

The fixture forbids exits, copies owner and expiry onto the binding, leaves `exception-dependency-mirror-2026-08` expired against `as_of`, lets Fulfillment drop `artifact-digest`, and still reports green. The plane is scoped. The defaults are not a product.

That substitution drives the chapter.

## 2. The production model: defaults you can exit, exceptions you cannot copy

> *Theory — Guardrail and exception binding*
>
> This model enables Fulfillment to finish `ship-on-paved-road` with inherited digest and identity defaults enforced, and Storefront to keep the Chapter 5 exit, without treating a scorecard badge as policy.

### A guardrail is a default with an owner, not a cage

The defaults this chapter enforces are the Chapter 5 remaining guardrails:

| Default | Why it exists | Enforcement surface |
|---|---|---|
| `artifact-digest` | Inherited DevOps promotion identity | artifact-promotion |
| `workload-identity-claims` | Inherited federated identity claims | workload-identity |
| `no-cluster-admin` | Chapter 3 / Chapter 8 prohibited inheritance | kubernetes-control-plane |

They apply on the paved road and on a supported exit. They do not apply by trapping teams on the scaffold. `exits_allowed: true` keeps the Chapter 5 exit a road. `exits_allowed: false` is a golden cage.

Do not rename these ids. Chapter 9 binds them. It does not invent `digest-pinned-artifact` as a default, or treat `golden-template-scaffold` as a remaining guardrail. An exit may lose the template. It may not lose digest identity.

The inherited control catalog may be exposed. It may not be rebuilt. Threat-model rebuild remains a Platform Chapter 1 non-goal.

### An exception is a binding, not a second lifecycle

Leaving a contract, leaving a scaffold, and waiving a default are three different acts:

| Act | Chapter | What it is |
|---|---|---|
| Supported exit | 5 | Leave the scaffold; remaining guardrails stay |
| Contract version bump | 7 | Leave a tenant-visible API version with a migration note |
| Guardrail exception | 9 | Temporary deviation from a default; expiry lives on the inherited DevSecOps record |

An exception is not an exit. An exit is not an exception to `artifact-digest`. A version bump is not a scorecard waiver.

Each `guardrails/exceptions.yaml` row references an inherited DevSecOps exception ID. It must not copy owner, scope, compensation, or expiry. The evaluator resolves those fields from `inherited/devsecops-v1.0/exceptions/records.yaml`. The platform row adds tenant, system, paved or exit path, remaining isolation, and scorecard effect. `duplicate_lifecycle_fields_in_platform_bindings` is false. Completeness is computed.

**Best Practice:** Bind remaining isolation on the exception. Waiving digest does not waive `no-cluster-admin` or workload-identity claims.

**Production Practice:** A scorecard cannot emit `reported_status: green`. The inherited evidence map requires an independent producer. Expiry is the inherited `expires_at` compared to `as_of`, not a date the platform row restates.

### Expired means the waiver is gone

`exception-dependency-mirror-2026-08` expired at `2026-08-15T12:00:00Z`. Northwind’s `as_of` is `2026-08-16T12:00:00Z`. Status `active` on the inherited record does not keep it current. A scorecard that still waives `artifact-digest` after that instant fails. Renew the inherited exception, or restore the default. Do not copy a later `expires_at` onto the platform binding.

An active inherited exception may waive digest while remaining isolation holds. That is a reviewed temporary deviation. It is not a paved-road exit and not a contract version.

Do not deploy a real admission webhook here. Do not build Chapter 10 measurements here.

## 3. Publish defaults, scorecards, and bindings

The completed Chapter 9 model uses three files:

```text
guardrails/defaults.yaml
guardrails/scorecards.yaml
guardrails/exceptions.yaml
```

The separation is deliberate. Defaults name the Chapter 5 remaining guardrails, owners, enforcement surfaces, and that exits remain allowed. Scorecards record which defaults each catalog system currently presents. Exception rows only bind. The evaluator joins them to Chapter 5’s contract and exit, Chapter 3 tenants, the catalog, inherited exception records, and the inherited release, identity, control, and evidence interfaces.

> **Practice — Enforce the remaining guardrails on paved and exit paths**
>
> Keep `artifact-digest`, `workload-identity-claims`, and `no-cluster-admin`. Allow the Chapter 5 exit.

Open `guardrails/defaults.yaml`:

```yaml
owner: platform-team
exits_allowed: true
defaults:
  - id: artifact-digest
    owner: platform-team
    enforcement_point: artifact-promotion
    inherited_policy: devops-v1.1-release
    applies_to: [paved, exit]
```

The evaluator loads the inherited release interface and fails if `artifact-digest` is missing while promotion identity is digest. It loads identity and fails if workload-identity claims are missing. It fails if exits are forbidden while Chapter 5 still has a supported exit.

> **Practice — Record observations, not a self-emitted grade**
>
> `defaults_present` is an observation. Completeness is computed. Green is not a field the scorecard may use to pass.

Open `guardrails/scorecards.yaml`. `fulfillment-api` is paved with all three defaults. `notification-service` is the Chapter 5 exit and still presents the remaining guardrails. There is no `reported_status`.

> **Practice — Bind inherited exception IDs without copying lifecycle**
>
> Tenant, remaining isolation, and scorecard effect are platform-local. Owner, scope, compensation, and expiry are not.

Open `guardrails/exceptions.yaml`. The completed product has no active waiver. Bindings is an empty list. That is valid. A later binding must name `exception-dependency-mirror-2026-08` or another inherited id, not a platform-invented exception.

The lab does not deploy an admission webhook. Completeness is whether defaults stay named, exits stay allowed, bindings stay bindings, and an expired inherited exception cannot keep a green digest-off scorecard.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-09-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 09 checkpoint: guardrail defaults and exception bindings verified
```

The audit validates the three Chapter 9 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- required defaults are the Chapter 5 remaining guardrails and have living owners;
- `artifact-digest` and workload-identity claims still consume inherited interfaces;
- remaining guardrails apply on exit; exits stay allowed;
- scorecards exist for required catalog systems and bind Chapter 3 tenants;
- the Chapter 5 exit still presents remaining guardrails;
- exception rows reference inherited IDs and do not copy lifecycle fields;
- expiry is resolved from the inherited record against `as_of`; and
- `reported_status: green` fails because the producer is not independent.

The expected defaults, systems, and `as_of` live in a separate checkpoint file. A scorecard under test does not emit its own passing grade.

The checkpoint does not prove that a real webhook blocked `latest`, that a real identity provider issued claims, or that a real exception ticket was renewed. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 9 evidence |
|---|---|
| Mechanism evidence | Schemas and the exception-binding evaluator operated successfully. |
| Decision evidence | Defaults, exit permission, remaining isolation, and inherited references are explicit. |
| Outcome evidence | Fulfillment has a computed scorecard with digest present and no expired waiver. That is not proof a webhook fired. |
| Recovery evidence | Not produced. A failed green scorecard is a conformance invariant, not restored isolation after a live policy bypass. |

Chapter 9 produces mechanism, decision, and limited outcome evidence for guardrails on the paved road and the supported exit. Pretending the local checkpoint proves admission in a cluster would weaken Chapter 12’s fleet change.

## 4. Test the design under failure

### Independent control failure — A scorecard stays green after an exception expires and a tenant disables artifact digest pinning

> **Practice — Fail the scorecard when expiry lapses and digest is off**
>
> Inject an expired inherited exception and a green Fulfillment scorecard without `artifact-digest`, and refuse both.

The completed guardrails are healthy. The failure command does not rewrite them. It injects the expired-waiver case against that snapshot:

```bash
make chapter-09-failure
```

Expected output:

```text
chapter 09 failure: expired exception and disabled digest correctly rejected
```

The injected record is:

```yaml
system: fulfillment-api
defaults_present: [workload-identity-claims, no-cluster-admin]
reported_status: green
exception: exception-dependency-mirror-2026-08
scorecard_effect: waive-artifact-digest
```

The binding does not copy owner or expiry. Identity, `no-cluster-admin`, and the Chapter 5 exit stay current. The baseline’s golden cage and copied lifecycle fields are not required for this failure. An exception can expire after the scorecard already looks complete. Green status, inherited expiry, and the missing digest must all fail on their own terms.

**Severity:** high; every later measurement and fleet conversation will treat a green badge as digest pinning.  
**Plausible harm:** `fulfillment-api` promotes `latest` after the mirror exception lapses; Storefront’s path still looks compliant; support debugs a “tenant choice.”  
**Potential blast radius:** every consumer of `fulfillment-api` artifacts, plus any scorecard that trusted this waiver as current.  
**Bounded by:** Chapter 5 remaining guardrails, inherited exception expiry, and independent evidence production. None of those repair a scorecard allowed to stay green.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Platform questions

- **User and job:** Fulfillment must finish `ship-on-paved-road` with digest identity intact. A green badge after disabling pinning is not that job. Storefront must still be able to use the Chapter 5 exit.
- **Isolation:** Guardrails are not a new tenancy model. Chapter-local implication: remaining isolation on an exception must keep `no-cluster-admin`. Waiving digest does not grant plane-admin. Isolation is applicable as a remaining-guardrail constraint, not as recovered live network.
- **Contract and exit:** The contract is the default set plus exception bindings. Teams leave the scaffold through Chapter 5’s exit, not through an expired waiver. They leave a contract version through Chapter 7. An exception is a temporary deviation with inherited expiry, not an exit and not a version bump.
- **Platform-product evidence:** `reported_status: green` is a self-emitted claim. Required proof is computed presence of remaining guardrails against inherited expiry. This is not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling the scorecard green because the portal rendered encourages wiki controls: keep the badge, copy a new expiry, skip digest. After `2026-08-15T12:00:00Z`, the inherited mirror exception cannot waive pinning. Fulfillment’s `defaults_present` without `artifact-digest` is a disabled default. Copying `expires_at` onto the platform row would hide that. Forbidding exits would hide the other failure: teams who cannot leave the scaffold will disable defaults unofficially.

The missing independent producer makes Chapter 4’s green-catalog failure again. The missing inherited join makes DevSecOps expiry ornamental. The missing remaining-guardrail names make Chapter 5’s exit a slogan.

#### Correction

The completed model does not let `fulfillment-api` report green without `artifact-digest`. It does not copy exception lifecycle onto the platform row. Expiry is resolved from the inherited record. A current inherited exception may waive digest with remaining isolation named. An expired one may not. Exits stay allowed. Completeness is computed. The failure command proves the check still fails when only Fulfillment’s digest and a binding are swapped.

This failure is a conformance-contract failure. It is not a runtime plane recovery. Do not call the failed scorecard **Evidence of restored isolation**. Nothing tenant-runtime was restored from a live bypass. The product stopped treating an expired waiver as a green default.

That correction changes later decisions:

- Chapter 10 must not count green scorecards or portal adoption as job completion.
- Chapter 12 must not fleet-upgrade a cohort whose remaining guardrails are waived by an expired exception.
- Chapter 13 must escalate a green digest-off scorecard as a product incident, not a tenant preference.
- Support may not renew expiry by editing `guardrails/exceptions.yaml`.

The design is practical because the failed scorecard is the product. Adding an arbitrary webhook command would not make it more practical.

## 5. Production reality

### Common guardrail errors

#### Copying owner, scope, compensation, or expiry onto the platform row

Those fields already live on the inherited exception. A local copy will drift. Bind the id.

#### Treating an exception as an exit, or an exit as an exception

Exits leave the scaffold. Exceptions waive a default temporarily. Digest identity is remaining on both.

#### Forbidding exits so defaults “always apply”

That is a golden cage. Unofficial forks return. Keep `exits_allowed`.

#### Letting the scorecard emit green

Independent evidence production forbids it. Observe `defaults_present`. Compute the rest.

#### Waiving `no-cluster-admin` to make a webhook stick

Chapter 8 already refused cluster-admin as onboarding. A guardrail exception is not a plane token.

#### Rebuilding the DevSecOps control catalog here

The platform may expose inherited controls. It may not rebuild threat models.

## 6. What changed

| Before | After |
|---|---|
| Fulfillment dropped digest pinning and stayed green after expiry. | **Expired inherited exceptions cannot waive `artifact-digest`; green fails.** |
| Exception rows copied owner and expiry. | **Bindings reference an inherited ID; lifecycle is resolved, not copied.** |
| Defaults were mandatory with no exit, or optional with no owner. | **Chapter 5 remaining guardrails are owned and apply on paved and exit paths.** |
| An exit, an exception, and a version bump were the same idea. | **Each is a distinct leaving act with a distinct record.** |
| A valid schema could appear to prove a webhook. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a guardrail catalog and an exception-binding contract that later measurement, fleet, and support chapters can trust without treating a green badge as digest pinning.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Guardrail catalog | `guardrails/defaults.yaml` | It retains Chapter 5 remaining guardrails, owners, and exit permission later fleet change must not rename. |
| Exception-binding contract | `guardrails/exceptions.yaml` | It retains the rule that platform rows reference inherited exception IDs and do not copy lifecycle. |

These artifacts should change when Northwind’s remaining guardrails or inherited exception set materially change—not whenever a scorecard theme is restyled.

## What You Learned

A guardrail is an owned default that applies on the paved road and on a supported exit. An exception is a binding to an inherited DevSecOps record, not a second expiry calendar. A green scorecard after digest pinning is disabled and the exception has expired is a failed product. Schema checks can prove structural completeness within declared scope. They cannot prove a real webhook. A design earns its place when Fulfillment cannot stay green without `artifact-digest`, and when Storefront can still leave the scaffold.

### Prove It

> **Independent Practice — Bind a Storefront exception without copying the Fulfillment expiry**
>
> `notification-service` already has a Chapter 5 exit. A temporary digest waiver, if it exists at all, must not turn that exit into an unofficial fork.

Extend the Chapter 9 model without adding DevEx measurements yet:

1. Decide whether Storefront needs an exception binding at all, or whether the exit already covers the lost template.
2. If you bind, name the inherited exception ID and the remaining isolation that must still include `no-cluster-admin`.
3. State which field you must not copy, and which inherited timestamp would falsify “the waiver is current.”
4. Choose whether `reported_status: green` may exist on `notification-service` during the waiver.
5. Identify one observation that would collapse exit and exception—for example putting `artifact-digest` in `lost_defaults`.
6. Explain which material change would trigger review of the guardrail catalog, not just one binding.

Do not copy the Fulfillment expired-mirror row and rename it. An exited notification service has different durability and digest consequences than a paved `fulfillment-api`. Your durable output is the binding-or-exit decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 9 capability when you can explain why a green scorecard is not a current exception, trace defaults to Chapter 5 remaining guardrails and inherited interfaces, describe evidence that would falsify expiry, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

Guardrails exist, but success is still counted in portal clicks and survey smiles. Leadership asks for adoption percentage, CSAT, and ticket volume as proof the platform works.

Chapter 10 measures developer experience without vanity metrics, so job-completion time stays the product indicator.
