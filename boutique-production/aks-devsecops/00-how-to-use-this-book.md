# How to Use This Book

## Who this book is for

This book is for intermediate-to-advanced **DevSecOps (Development, Security, and Operations)**, platform, and Azure practitioners who need a defensible delivery path on **AKS (Azure Kubernetes Service)**.

You should already be comfortable with Linux, Git, containers, **CI/CD (Continuous Integration and Continuous Delivery)**, Kubernetes, **IaC (Infrastructure as Code)**, identity federation, and incident-response basics. The book does not teach those subjects from first principles. It uses them as the surface on which this repository's security decisions operate.

You do not need a running Azure subscription to learn from the manuscript. The lived pilot was torn down. Git, **ADRs (Architecture Decision Records)**, setup guides, and screenshots are the evidence. Rebuilds cost money and are optional unless a chapter is explicitly about apply or teardown.

## The repository is the system

There is no companion lab and no invented storefront. The system under study is:

```text
https://github.com/btilki/boutique-aks-devsecops
```

Local clone (author's machine): `/Users/biroltilki/Documents/Cursor/boutique-aks-devsecops`.

The application is [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) **v0.10.5**. The platform is one AKS cluster in `germanywestcentral` with three logical environments as namespaces. Do not call that design production-ready. `prod` is the namespace `boutique-prod` on the same cluster as `boutique-dev` and `boutique-stage`.

This title belongs to the Boutique Production Series. Its sisters are *Practical GitOps on Amazon EKS* (`boutique-eks-gitops`) and *Practical SRE on Google Kubernetes Engine* (`boutique-gke-sre`). Reading order is optional. Cross-references appear when a sister platform made a different, equally honest choice.

## GitHub holds Git; Azure DevOps runs pipelines

The CI story is a teaching point, not a convenience:

| Role | Platform | Notes |
|------|----------|-------|
| Source of truth | **GitHub** | Clone, **PRs (pull requests)**, Argo CD sync, digest commits |
| Pipeline runner | **ADO (Azure DevOps)** | Mirror → Trivy → cosign → promote; **OIDC (OpenID Connect)** to Azure |
| GitHub Actions | **Not used** | No `.github/workflows` — by design |

YAML lives in `pipelines/`. Auth is ADO OIDC. There is no long-lived cloud secret in the pipeline. If you add a GitHub Actions workflow because "every repo has one," you have broken the contract this book teaches.

## Lived versus scaffold

Setup Topics **00–13** ran on a real cluster and were then torn down. Topics **14–20** are **scaffold**: files and setup guides exist in Git; they were not live-validated on this pilot.

| Label | Meaning |
|-------|---------|
| **Lived** | Ran on Azure before teardown. Screenshots and Git remain. |
| **Scaffold** | Present in Git. Apply after a Topics 00–12 rebuild. Not a passed milestone. |
| **Inactive** | DNS names and public URLs after teardown. Screenshots are the storefront proof. |

A YAML file in Git is not the same as a passed milestone. Chapter 16 covers Phase 15+ scaffolds without upgrading them into lived claims.

## Teardown includes ACR

**ACR (Azure Container Registry)** is destroyed on teardown ([ADR-0010](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0010-destroy-acr-on-teardown.md)). That is a security and cost control, not an accident. Rebuild requires re-running the mirror/scan/sign pipeline. Do not assume signed images survive a destroy.

## Evidence while DNS is offline

Hostnames such as `dev-boutique.biroltilki.art` resolve only after a rebuild of Topics 02–12. For storefront and UI proof, use the lived screenshots catalogued in `assets/images/README.md`:

- Argo CD healthy applications (`05-argocd-applications-healthy.png`)
- ADO supply-chain pipeline green (`09-ado-pipeline-supply-chain-success.png`)
- ACR `frontend` `v0.10.5` (`09-acr-repositories-frontend.png`)
- Dev / stage / prod storefront pages (`10-` and `12-` screenshots)
- Grafana dashboards (`11-grafana-*.png`)

Practice in this book usually means opening a real path, interpreting a real decision, and stating what evidence would prove a change. Commands shown are the commands from `docs/setup/`, not new Makefile targets invented for a lab.

Several chapters **embed** those PNGs as **Inactive** figures (GitHub raw URLs). If a file is missing from the clone, skip the figure; do not treat a broken image as a live UI.

If the clone is **newer** than this manuscript, start at `CHANGELOG.md`. After the conclusion, [19-interview-questions-from-this-repository.md](19-interview-questions-from-this-repository.md) answers ten design-review questions from these files. Matching chapters point at playbook articles **A1** (GitHub/ADO), **A2** (Kyverno deny), **A3** (destroy ACR). From `books-prompts/books/boutique-production/`, run `python3 tools/citation_drift_check.py --book aks-devsecops` after a repo or manuscript change.

## Rebuild is optional and expensive

You may clone the repository and complete every Practice box without `terraform apply`. When a chapter quotes a command from `docs/setup/`, it is showing what the operator ran during the lived pilot, not assigning you a cloud bill.

If you do rebuild:

1. Follow `docs/setup/` Topics 00–12 in order. The catalog wins over this manuscript if a flag changed.
2. Expect roughly €150–250/month while AKS is up (`docs/architecture/11-cost-model.md`).
3. Region remains `germanywestcentral` unless you amend [ADR-0011](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0011-aks-node-vm-sku.md) and `versions.yaml` together.
4. After you are done, Topic 13 destroys AKS **and** ACR. Keeping the registry is a design violation, not a shortcut.

A rebuild that skips Topic 09 (mirror/scan/sign) will be denied by Kyverno. That is the system working.

## How chapters work

Each core chapter answers one production question, cites repository-relative paths, quotes short real excerpts, and names durable outputs that already exist in the repo.

At the start of the main conceptual section you will see a theory box:

> *Theory — Model name*
>
> One sentence stating the production decision the model enables.

Guided work uses practice boxes. The unguided close is Independent Practice. Every dedicated failure section names severity, plausible harm, potential blast radius, bounding controls, and `Primary principles:` drawn from the series:

1. Git is the deploy authority unless a chapter is a bounded exception (bootstrap, teardown, emergency).
2. Identity is digest, not tag. Floating tags and `:latest` are failures.
3. CI never deploys the cluster. It produces evidence and proposes Git changes.
4. Namespaces on one cluster are not multi-account isolation.
5. Teardown is a production control, not an afterthought.
6. Lived evidence beats scaffold.

Topic numbering in the book is not the same as setup topic numbers. Chapter 10 is the CI pipeline (setup Topic 09). Chapter 11 is admission (setup Topic 08). The setup catalog notes that Kyverno installs after GitOps but signature verify waits for signed digests. Read the chapter titles; then open the mapped setup file in the topic map in `BOOK-PLAN.md`.

## What local reading proves

Opening files and reasoning about ADRs proves that the design is reviewable. It does not prove that Azure still enforces the same **RBAC (role-based access control)**, that Kyverno still admits the same digest, or that Let's Encrypt still issues for `biroltilki.art`. Those claims require a rebuild.

A successful `make pre-commit` or `kyverno test policies/tests` run on a clone proves local structure. It does not prove the cluster is healthy. The cluster is gone.

`make pr-validate` exercises Topic 14's scaffold gates on your laptop. It still does not register an Azure DevOps pipeline. `./tests/ci/dast-zap.sh` will not have a live target until you rebuild Topic 10's hostname.

Do not create Git tags such as `chapter-NN-start`. This series has no companion lab snapshots. The Git history of `boutique-aks-devsecops` is the only snapshot.

## Evidence categories

Security work in this repository produces four kinds of evidence. Do not substitute one for another:

1. **Mechanism evidence** — Kyverno denied a Pod; OIDC token exchange succeeded; `terraform destroy` removed ACR.
2. **Decision evidence** — an ADR is accepted; a Checkov skip is named; prod approval was recorded in ADO.
3. **Outcome evidence** — smoke tests and screenshots show the storefront served HTTPS while the cluster lived.
4. **Recovery evidence** — old signing keys fail verify; leftover ACR is gone; Git matches the intended overlay.

Lived Topics 00–13 produced all four at the time. After teardown, outcome evidence for the *current* Azure subscription is empty unless you rebuild. Mechanism evidence remains in Git and screenshots.

## How to judge your work

Do not ask only whether a control is configured. Ask:

> What asset and harm justify this decision, what trust crosses the boundary, what evidence would falsify the control, what happens when prevention fails, and why unsigned or `:latest` images must not reach AKS?

That question is the reading contract for the chapters ahead.
