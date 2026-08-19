# Editorial Conventions — Practical GitOps on Amazon EKS

This book follows the Boutique Production Series conventions.

**Series file (canonical):** [BOUTIQUE-EDITORIAL-CONVENTIONS.md](../BOUTIQUE-EDITORIAL-CONVENTIONS.md)

**Series contract:** [BOUTIQUE-SERIES.md](../BOUTIQUE-SERIES.md)

Do not copy Northwind lab commands or companion-lab snapshots into this manuscript. The system under study is [boutique-eks-gitops](https://github.com/btilki/boutique-eks-gitops). Practice means opening a real path, interpreting a lived or scaffolded decision, and stating what evidence would prove a change.

## Book-local principles

1. **Git is the only deploy authority.**
2. **Image identity is digest, not tag.**
3. **CI (Continuous Integration)** has **ECR (Elastic Container Registry)** and Git permission, not cluster deploy permission.
4. **One cluster and three namespaces are a cost decision, not isolation.**
5. **Teardown after the pilot is required**, not optional hygiene.
6. **Scaffold in Git is not lived proof.** Topics 15–19 and ADRs 0007–0010 stay labeled scaffold.

## Honesty labels

- **Lived:** Setup Topics 01–14 and ADRs 0001–0006; milestones M1–M4 PASS, then AWS destroyed.
- **Scaffold:** Setup Topics 15–19 (verify/SBOM, CI gates, AppProjects, AnalysisTemplates, WAF/Falco).
- **Inactive:** DNS names after teardown. Pipelines are dormant unless `ENABLE_PILOT_CI` or `ENABLE_REPO_GATES` is set.
