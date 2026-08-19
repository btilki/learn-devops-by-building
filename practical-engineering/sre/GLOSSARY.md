# Glossary and Abbreviations

## Abbreviations

| Abbreviation and full form | Use in this book |
|---|---|
| **CI/CD (Continuous Integration and Continuous Delivery)** | Inherited delivery surface. This book does not teach it from first principles. |
| **DR (disaster recovery)** | A restore of one backup or one environment. It is not a portfolio game-day program and not regional fail-over. |
| **GitOps (Git-based operations)** | Inherited reconciliation from DevOps. Reconstruction of one environment remains insufficient for regional loss. |
| **RPO (Recovery Point Objective)** | How much journey state may be lost in a regional fail-over. Teaching value: 900 seconds. |
| **RTO (Recovery Time Objective)** | How long the portfolio may take to serve Chapter 1 journeys from the surviving region. Teaching value: 14400 seconds. Platform recorded `not-portfolio-rto`. |
| **SLA (Service Level Agreement)** | A customer or legal promise. It is not an SLO target. |
| **SLI (Service Level Indicator)** | A user-visible measurement of a protected journey, or an adjacent platform-product job-time proof. Component uptime is rejected. |
| **SLO (Service Level Objective)** | The internal reliability contract for a journey over a window. Error budget is computed from it. |
| **SRE (Site Reliability Engineering)** | Reliability engineering across a service portfolio: SLOs, error budgets, on-call, learning, game days, and regional fail-over. |

How to Use This Book writes **SRE (Site Reliability Engineering)**, **CI/CD (Continuous Integration and Continuous Delivery)**, **SLOs (Service Level Objectives)**, and **SLIs (Service Level Indicators)** on first use. Later reader-facing chapters expand an abbreviation again on first use in that document.

## Production terms

**Availability theater**  
A green graph that does not represent a user-visible journey. Cluster uptime, replica Ready, and portal availability are theater unless they are refused with a remaining owner.

**Error budget**  
Remaining unreliability for a portfolio SLO. Reserve the phrase for SRE governance. A Platform fleet freeze for an upgrade is not an error-budget freeze.

**Evidence of portfolio recovery**  
Proof that a lost region was failed over, tenant isolation held, journey SLOs were met from independent observations, and inherited restores were not treated as recovery. It is not DevSecOps restored trust and not Platform restored isolation.

**Job-time budget**  
Platform-product unreliability for jobs such as time-to-first-environment. It is never a portfolio SLO.

**On-call system**  
Rotation, load, handoff, and authority bound to a living primary. Catalog contacts `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall` are inputs, not the system.

**Toil**  
Operational work that scales with production and does not permanently improve the system. A numeric bound protects engineering time; a breach blocks new critical SLO scope.
