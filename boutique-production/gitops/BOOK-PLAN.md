# Practical GitOps on Amazon EKS — Book Plan

**Planning status:** Active draft  
**Draft date:** 2026-08-18  
**Source repository:** `boutique-eks-gitops`  
**Series:** [Boutique Production Series](../BOUTIQUE-SERIES.md)

## Promise

Make Git the only deploy authority for Online Boutique on a single Amazon **EKS (Elastic Kubernetes Service)** cluster: digest-only images, **CI (Continuous Integration)** that never deploys, Argo CD pull reconciliation, human promotion `dev → stage → prod`, frontend canary, a security and observability baseline, production-readiness evidence, mandatory teardown, and honest Phase 12 scaffolds.

The reader will be able to explain, from this repository, why a pipeline that can `kubectl apply` is a design failure, how a digest merge request becomes cluster state, what CODEOWNERS and manual prod sync actually gate, and what the pilot refuses to claim.

## Audience

Intermediate-to-advanced DevOps, platform, cloud, and GitOps practitioners. The book does not teach AWS, Terraform, Kubernetes, or Helm from first principles.

## System under study

Clone or open:

```text
https://github.com/btilki/boutique-eks-gitops
```

Local path on the author's machine: `/Users/biroltilki/Documents/Cursor/boutique-eks-gitops`.

The lived pilot ran in `eu-central-1`, reached **M3 + M4 PASS**, and then destroyed AWS resources. Public DNS names are inactive until a rebuild. Practice is file-backed. Live rebuild is optional and costs money.

## Coverage rule

Every setup topic (01–19), architecture document, ADR (0001–0010), Terraform module, GitOps tree, Helm chart family, GitLab CI contract, Kyverno policy, rollout, observability stack, promotion/rollback path, operations handbook, teardown, test, and Phase 12 scaffold must appear in at least one chapter as a cited path. Scaffolds stay labeled scaffold.

## Index

0. How to Use This Book
1. Charter a Production Pilot, Not a Demo Cluster
2. Write Constraints as ADRs Before You Apply
3. Make the Repository the Control Plane
4. Reconcile AWS Foundation Through Terraform
5. Put HTTPS on the Edge Without Making CI the Ingress Owner
6. Bootstrap Argo CD as the Only Deployer
7. Enforce Digest, Secrets, and Network Baseline
8. Explain Production From On-Cluster Signals
9. Pin Boutique by Helm Digest Overlays
10. Build, Scan, and Sign — Then Open a Digest Merge Request
11. Promote by Copying Digests, Not by Redeploying
12. Canary the Frontend on Stage and Prod
13. Prove Readiness With Checklists and Runbooks
14. Tear Down as a Production Control
15. Author Hardening Scaffolds Before You Pay for the Next Cluster
16. Conclusion — Git Remains the Deploy Authority
17. Interview Questions From This Repository

## Back matter

- Glossary and Abbreviations
- References

## Topic map

| Chapter | Setup / ADR / area |
|---|---|
| 1 | README, ROADMAP, ARCHITECTURE, cost model, plan § scope |
| 2 | architecture 01–10, ADRs 0001–0005 |
| 3 | setup 01–02, versions, CODEOWNERS, Makefile, pre-commit |
| 4 | setup 03–04, terraform modules, network design |
| 5 | setup 05, ADRs 0003–0004, LB controller, external-dns, cert-manager |
| 6 | setup 06, gitops bootstrap/apps, deployment flow, ADR-0001 sync model |
| 7 | setup 07, Kyverno, ESO, NetworkPolicy, security architecture |
| 8 | setup 08, ADR-0005, monitoring stack, alerting runbook |
| 9 | setup 09, charts/*, gitops/envs/* |
| 10 | setup 10, `.gitlab-ci.yml`, docs/ci.md, ADR-0006 |
| 11 | setup 11, promotion.md, rollback.md, CODEOWNERS prod |
| 12 | setup 12, argo-rollouts, frontend rollout.yaml |
| 13 | setup 13, PRODUCTION_CHECKLIST, runbooks, operations 01–20 |
| 14 | setup 14, teardown runbook, cost model, M4 |
| 15 | setup 15–19, ADRs 0007–0010, tests/policy, waf, falco, analysis, AppProjects |

## Recurring principles

1. Git is the only deploy authority.
2. Image identity is digest, not tag.
3. CI has ECR and Git permission, not cluster deploy permission.
4. One cluster and three namespaces are a cost decision, not isolation.
5. Teardown after the pilot is required, not optional hygiene.
6. Scaffold in Git is not lived proof.
