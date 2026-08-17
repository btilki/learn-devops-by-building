# Glossary and Abbreviations

## Abbreviations

| Abbreviation and full form | Use in this book |
|---|---|
| **API (Application Programming Interface)** | The tenant-visible contract for a platform capability, not the hidden Terraform or module internals. |
| **CI/CD (Continuous Integration and Continuous Delivery)** | The inherited delivery surface this book productizes; it is not taught from first principles. |
| **CNI (Container Network Interface)** | A hidden network-plugin detail. Tenants bind a network contract version; they do not set CNI config. |
| **CSAT (Customer Satisfaction)** | A vanity non-metric. A smiling survey cannot prove a job finished or close a platform incident. |
| **FinOps (Financial Operations)** | Cost of a useful, quality-gated unit. This book applies that idea to platform showback, not to Storefront’s order path. |
| **GitOps (Git-based operations)** | Inherited reconciliation that forbids source rewrite. A fleet upgrade or plane restore is reviewed intent, not a controller edit. |
| **IAM (Identity and Access Management)** | A hidden identity-provider detail. Tenants bind workload-identity parameters; they do not name role ARNs. |
| **OIDC (OpenID Connect)** | A hidden federation detail used by the platform to keep short-lived identity. It is not a tenant API field. |
| **RTO (Recovery Time Objective)** | Maximum acceptable time to restore a required outcome. Portfolio RTO programs remain SRE. |
| **SLI (Service Level Indicator)** | A measurement of a platform-product job, such as time-to-first-environment. It is not a tenant-workload metric. |
| **SLO (Service Level Objective)** | An acceptable target for an SLI over a window. Portfolio SLO governance remains SRE. |
| **SRE (Site Reliability Engineering)** | Reliability engineering through service objectives, operations, and learning. The planned fourth book. |
| **TTL (Time To Live)** | The Chapter 6 lease lifetime. Chapter 12’s freeze window is one TTL: 168 hours. |
| **VPC (Virtual Private Cloud)** | A real network the local lab does not provision. A lease models isolation; it does not create a VPC. |

Chapter 0 writes **CI/CD (Continuous Integration and Continuous Delivery)** on first use for the combined delivery surface. **SLI** and **SLO** are expanded on first use in each reader-facing chapter because the book must keep platform-product indicators distinct from portfolio objectives.

## Production terms

**Blast radius**  
The tenants, environments, jobs, or authority exposed to a change, failure, or restore. Fulfillment’s blast radius must stop at Fulfillment.

**Catalog freshness**  
Computed proof that a catalog owner and escalation contact are still living. A catalog file cannot emit `reported_status: green`.

**Cohort**  
A fleet upgrade group of one or more tenants. Storefront can complete `tenant-storage` `2.0` without Fulfillment absorbing `sku` in the same step.

**Contract version bump**  
The Chapter 7 leaving act: a tenant-visible API version with a migration note. It is not a paved-road exit, a guardrail exception, or a fleet apply.

**Decision evidence**  
Proof that an owner evaluated users, jobs, isolation, and trade-offs and made a bounded decision.

**Evidence of bounded platform-product recovery**  
Proof that the modeled platform-product recovery invariant holds: mixed backup rejected, plane last known good restored, tenant isolation held in the model, platform jobs still named. It is not proof a live portal, cluster, or backup platform recovered, and it is not DevSecOps restored trust.

**Evidence of restored isolation**  
Proof that tenant blast radius held after a modeled plane restore: mixed backup rejected, last known good restored, per-tenant continue or freeze explicit. It is not DevSecOps restored trust.

**Exception binding**  
A platform row that references an inherited DevSecOps exception ID. It must not copy owner, scope, compensation, or expiry.

**Freeze window**  
A fleet change halt with a start and end. Northwind’s freeze is one Chapter 6 TTL.

**Guardrail**  
A remaining default that still applies on the paved road and after a supported exit. It is not a golden cage and not a temporary chat waiver.

**Isolated restore**  
Restoring `kubernetes-control-plane` from independently verified last known good without replaying one tenant’s intent into another.

**Job**  
A finished production outcome a named user must obtain from the platform. Opening a ticket or browsing a catalog is not a job.

**Job-time budget**  
Unreliability permitted against platform-product job time, such as time-to-first-environment. The lab field `error_budget_indicators` records that budget. It is not an SRE portfolio error budget and not Storefront `order_success_ratio`.

**Last known good**  
The version retained after failure. Plane last known good is Chapter 8’s `1.0` after a failed upgrade to `1.1`. Contract last known good is Chapter 12’s `tenant-storage` `1.0`. Do not collapse them because both say `1.0`.

**Mechanism evidence**  
Proof that a catalog, lease, controller, scorecard, or evaluator operated. It does not prove a job finished.

**Mixed backup**  
Plane evidence that contains more than one tenant’s intent, or is newest, corrupt, or unverified. Applying it is the Chapter 14 cumulative product failure.

**Non-goal**  
Work the platform refuses, with a remaining owner. A refusal without an owner is a vacuum, and the ticket returns.

**Non-metric**  
A signal the measurement contract must name so it cannot be used as success. `category: vanity` means the signal is gameable. `category: tenant-workload` means the signal is real and belongs to a tenant path.

**Outcome evidence**  
Proof that a team finished a production job inside the contract, such as computed paved-road completion. It is not a portal launch.

**Paved road**  
The supported default path with inherited defaults, conformance, and a supported exit. Teams may leave the scaffold; remaining guardrails stay.

**Platform product**  
An owned internal capability other teams consume through a contract. It has users, jobs, a promise, refusals, and success evidence that is not vanity.

**Promise**  
The product’s public contract. For Northwind: application teams finish production jobs on a reviewed paved road, inside an explicit tenant boundary, without inheriting shared cluster authority.

**Recovery evidence**  
Proof that tenant blast radius was restored in the model—not merely that a ticket closed or an API answered. Chapters 1–13 do not produce it. Chapter 14 produces **Evidence of restored isolation** and **Evidence of bounded platform-product recovery**.

**Reconciliation**  
Comparing desired tenant intent, admitted contract version, recorded last known good, and actual restore, then making disagreement visible and owned.

**Red capability**  
A runnable baseline result proving that the chapter’s declared weakness is present. A successful baseline is not a healthy product.

**Remaining guardrail**  
A default that survives a supported exit: digest pinning, workload identity, and no cluster-admin stay after a team leaves the scaffold.

**Self-approval**  
An allowed plane change or restore whose `subject` or `approved_by` is a Chapter 8 plane identity. It is not `subject == approved_by`. `platform-team` may appear in both fields; `plane-reconciler` may not.

**Shared control plane**  
`kubernetes-control-plane` consumed as a product. Shared cluster-admin is not shared-control-plane. It is one plane with no tenants.

**Showback**  
Allocation of platform unit cost to tenants. A cheaper shared bill is not a platform-product SLI.

**Supported exit**  
The Chapter 5 leaving act: leave the scaffold while remaining guardrails stay. An unofficial fork is not an exit.

**Tenant**  
An isolation and ownership boundary, not a Kubernetes namespace label. Storefront and Fulfillment are tenants.

**Tenant-workload non-metric**  
A real signal that belongs to a tenant path, such as `order_success_ratio`. It must not prove the platform product is healthy.

**Time-to-first-environment**  
The platform-product SLI for `obtain-bounded-environment`. A created namespace is not that proof.

**Unofficial fork**  
A path that skips the paved road without a supported exit. Conformance fails; support does not cover it.

**Vanity metric**  
A gameable signal treated as success: portal launch, CSAT, ticket volume, or adoption percentage after deleting unofficial paths.

**Workload identity**  
An attributable runtime subject with issuer, audience, and expiry. The platform productizes it; this book does not reteach federation.
