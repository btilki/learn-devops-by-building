# Establish Trust in Source and Dependencies

Chapter 5 bounded exceptional authority. A valid maintainer identity can still propose unsafe code, and an ordinary dependency update can still resolve to attacker-controlled content. Northwind must decide which inputs may enter a build without treating authentication, review, or a familiar package name as proof of trust.

## 1. A reviewed change with an untrusted result

The compromised maintainer changes the payment dependency from `northwind-payment` to the plausible-looking `northwind-payments`. Resolution selects a high version from a public registry. The same maintainer supplies the only approval.

Work from the lab working tree using the Chapter 0 procedure. From the DevSecOps lab root, run:

```bash
make chapter-06-baseline
```

The start-state policies trust the broad `northwind-` public namespace, treat the compromised maintainer as the payment-path owner, and lock the look-alike package. The command succeeds because it proves that this permissive configuration admits the unsafe input:

```text
chapter 06 baseline: permissive source and dependency policy admitted unsafe input
```

The weakness is not a malfunctioning verifier. Its expectations grant the wrong trust.

## 2. The production model: trust the resolved input, not its label

> *Theory — Source authenticity and dependency provenance*
>
> This model enables Northwind to reconstruct what entered the build and why policy permitted it.

Source authenticity answers where a revision came from and which protected reference contains it. Review independence asks whether someone other than the change author authorized a sensitive change. Neither claim proves that the resulting dependency bytes came from the intended publisher.

Dependency identity is a relationship among name, version, registry, namespace, and content hash. Omitting any part creates ambiguity:

| Evidence | Question answered | What it cannot prove alone |
|---|---|---|
| Origin and revision | Which repository state was evaluated? | That its changes were independently authorized |
| Protected reference | Which governed line of development contains it? | That branch protection was correctly configured in the live host |
| Author and approvers | Who proposed and reviewed the change? | That the resolved package is the intended content |
| Registry and namespace | Which distribution authority supplied the name? | That the selected version and bytes match review |
| Locked version and hash | Which exact content resolution must reproduce? | That the original package or publisher was trustworthy |
| Resolution decision | Why the complete input set passed policy | That the later builder preserved those inputs |

Dependency confusion exploits an authority mismatch: an internal-looking name resolves from a registry whose namespace Northwind does not govern. The class was demonstrated when public packages reused internal names and were selected by version comparison. [Dependency confusion](https://medium.com/@alex.birsan/dependency-confusion-how-i-hacked-into-apple-microsoft-and-dozens-of-other-companies-4a5d60fec610). Typosquatting exploits human recognition: a nearby spelling looks legitimate. Version pinning does not solve either problem if the wrong package was pinned. A hash protects integrity after selection; it does not make a malicious selection trustworthy.

The inverse mistake is equally dangerous. A trusted registry is not permission to consume every package it hosts. Registry approval and namespace approval are separate decisions.

## 3. Enforce source and dependency admission

> **Practice — Govern source authority**
>
> Declare trusted origins, protected references, sensitive paths, independent review, and bounded update automation.

Open `supply-chain/source-policy.yaml`. Changes under `services/payment/` and `supply-chain/` need an approver distinct from the author. `dependency-bot` is the attributable automation subject permitted to prepare routine updates; it cannot approve its own change.

Ownership and approval are related but different. `supply-chain/ownership.yaml` identifies who must care about a path. The source policy determines which review relationship is sufficient to admit a particular change. A broad repository approval must not silently replace sensitive-path ownership.

> **Practice — Bind package identity to its distribution authority**
>
> Approve registries and namespaces together, then require exact locked versions and hashes.

Open `supply-chain/dependency-policy.yaml` and `supply-chain/lock.yaml`. The private registry may supply `northwind-payment`; the public registry may supply only the separately declared public namespace. The lock record binds the approved package to version `3.4.1` and one content hash. It also binds the public transitive dependency `northwind-public-http-signing` to its registry, version, and hash.

Vendoring can reduce registry availability risk and preserve reviewed content locally, but it transfers patch intake, licensing review, storage, and provenance responsibility to Northwind. Automated updates reduce staleness, but their identity, allowed manifests, approval rules, and evidence must remain bounded. Neither technique removes the trust decision.

> **Practice — Reconstruct the resolved graph independently**
>
> Compare observed origin, revision, attributable update claim, path-owner approvals, direct and transitive resolution, registry, version, and hash with policy and lock expectations.

`supply-chain/resolution-evidence.yaml` is the observation presented to the verifier. The policy and lock are separate expectations. Run:

```bash
make audit chapter-06-checkpoint
```

The audit validates all five governed supply-chain artifacts. The checkpoint passes only when a sensitive change has approval from an independent path owner, its update identity has an attributable claim, and every direct and transitive dependency matches its allowed registry namespace and locked content. This local resolver model does not query or secure a hosted repository or registry; production must obtain equivalent facts from those systems and protect the policy source independently.

## 4. Test the design under failure

### Cumulative attack — Admit a look-alike payment package

> **Practice — Separate a valid identity from a trustworthy input**
>
> Exercise the inert resolution fixture containing a look-alike package, public-registry origin, wildcard request, and self-review.

**Severity:** critical; the change targets code that can influence payment effects.  
**Plausible harm:** attacker-controlled build input, fraudulent payment behavior, sensitive-data exposure, or a later production foothold.  
**Potential blast radius:** builds and environments that consume the altered payment dependency.  
**Bounded by:** protected references, sensitive-path ownership, independent approval, registry and namespace policy, exact locks, and hash verification.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Payment authority, release authority, and correct order outcomes drive the decision.
- **Trust and authority:** Source approval grants no implicit authority to introduce a package from an unapproved distribution namespace.
- **Detection after prevention fails:** The admission decision retains the attempted name, registry, version, hash, author, claim, approvers, revision, result, and individual denial reasons for later correlation.
- **Evidence of restored trust:** Not yet applicable. Chapter-local recovery: the unsafe revision remains quarantined, the approved graph is reconstructed, and bounded update automation can still produce an admissible change.

#### Diagnosis

Run `make chapter-06-attack`. The verifier rejects missing independent review, missing path-owner approval, the unapproved namespace, and the unknown package independently. Each reason names the affected path or dependency. The command writes `build/chapter-06-attack-decision.json`; a familiar name and high version do not satisfy any trust contract.

#### Containment

Run `make chapter-06-contain`. It consumes the denied attack decision and writes `build/chapter-06-quarantine.json`. The unsafe revision is now explicitly quarantined rather than assumed different from the approved revision. Record the denial through the Chapter 4 identity path and retain the decision for Chapter 13 detection work. The operational `compromised-session` register remains active until Chapter 14 containment.

Containment stops further admission; it does not prove that earlier builds were clean. Production responders must identify every build and environment that could have consumed the suspect revision.

#### Recovery

Run `make chapter-06-recover`. Recovery requires the quarantine record, reconstructs the approved direct and transitive graph, verifies the policy's attributable-update requirement, and writes a separate allow decision for bounded automation. If the unsafe input had entered a build, recovery would also invalidate affected artifacts and rebuild them through the Chapter 7 trust chain.

## 5. Production reality

**Best Practice:** evaluate source identity, independent authorization, registry namespace, exact resolution, and content integrity as one admission decision.

**Production Practice:** enforce protected references in the Git host, restrict package-manager registry fallback, reserve internal namespaces where possible, authenticate private registries, retain immutable resolution evidence, and alert on policy denials. Test mirror outages and update-bot failure. A control that requires developers to bypass it during ordinary registry failure is not a durable control. GitHub, for example, documents that protected branches can require reviews and restrict who can push. [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

Lockfile changes deserve the same review as the manifest that caused them. Reviewing only the human-readable request while ignoring resolved transitive changes leaves the actual build input unaudited. Conversely, a large mechanical lock change needs tooling that explains origin, version, hash, and ownership without asking reviewers to infer meaning from thousands of lines.

## 6. What changed

| Before | After |
|---|---|
| A valid maintainer could introduce any plausible package name. | **Sensitive changes require independent authorization.** |
| Registry choice was a resolver default. | **Registry and namespace authority are explicit policy.** |
| A version string represented dependency identity. | **Name, registry, version, and hash identify resolved content.** |
| Review covered the manifest but not necessarily its resolution. | **Resolution evidence reconstructs the complete admitted input.** |
| Blocking one change was treated as success. | **Containment preserves the graph; recovery proves trusted updates still work.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Source trust policy | `supply-chain/source-policy.yaml` and `supply-chain/ownership.yaml` | They preserve origin, protected-reference, ownership, approval, and automation authority. |
| Dependency admission policy | `supply-chain/dependency-policy.yaml` and `supply-chain/lock.yaml` | They bind registries and namespaces to exact resolved content. |
| Resolution evidence | `supply-chain/resolution-evidence.yaml` | It records the independently reviewable input admitted to the next build. |
| Admission and quarantine evidence | `build/chapter-06-attack-decision.json`, `build/chapter-06-quarantine.json`, and `build/chapter-06-recovery-decision.json` | They preserve denial, containment, and restored admission as distinct state transitions. |

## What You Learned

Authentication tells Northwind who proposed a change; it does not make the change trustworthy. Source origin, protected references, sensitive-path ownership, independent review, registry namespace, locked resolution, and content hashes form complementary controls. The verifier must reconcile observations against expectations that the resolution mechanism cannot rewrite to approve itself.

### Prove It

> **Independent Practice — Govern a public dependency migration**
>
> Decide how Northwind may replace a private payment client with a public package without trusting its name or popularity.

Specify publisher and registry authority, ownership, independent approvers, namespace, exact version and hash, transitive resolution evidence, rollback conditions, and the observations that would invalidate the decision.

## Next

Northwind now admits only governed source and dependency inputs. Chapter 7 ensures that bounded builders, attestations, release approval, and deployment admission preserve that trust from source to running artifact.
