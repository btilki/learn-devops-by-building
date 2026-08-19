# Editorial conventions — *Practical DevSecOps on Azure Kubernetes Service*

This book follows the Boutique Production Series contract in [`../BOUTIQUE-EDITORIAL-CONVENTIONS.md`](../BOUTIQUE-EDITORIAL-CONVENTIONS.md) and [`../BOUTIQUE-SERIES.md`](../BOUTIQUE-SERIES.md).

Do not copy Northwind editorial files into this title. The Northwind books remain frozen.

## Series rules that apply here

- Audience: intermediate-to-advanced. Do not teach Linux, Git, containers, or Kubernetes from first principles.
- The repository is the system. There is no companion lab.
- On first use in each reader-facing file: **CI (Continuous Integration)** — abbreviation, then full form in parentheses, complete expression bold.
- One theory box at the start of the main conceptual section: `> *Theory — Model name*` plus one sentence.
- Guided work: `> **Practice — Action name**`. Unguided close: `> **Independent Practice — Action name**`.
- Every dedicated failure section names severity, plausible harm, potential blast radius, bounding controls, and `Primary principles:`.
- Core chapters roughly 180–320 lines. How to Use 120–180. Conclusion 80–140.
- Quote short real excerpts. Cite repository-relative paths from `boutique-aks-devsecops`.

## Book-local principles

These six recurrences are the production contract for this title. Failure sections may name only those that the scenario actually exercises.

1. **GitHub holds Git; Azure DevOps runs pipelines.** Neither gets a long-lived cloud secret. GitHub Actions is absent on purpose.
2. **Unsigned and floating tags must not reach AKS.** Kyverno is the last admission gate. Cosign is key-based with `--tlog-upload=false` ([ADR-0005](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0005-cosign-key-based-signing.md)), unlike the EKS sister's keyless signing.
3. **The same digest is promoted.** CI does not rebuild per environment.
4. **`prod` is a namespace on one cluster**, not a separate production estate. Do not call the platform production-ready.
5. **Destroying ACR on teardown is intentional** ([ADR-0010](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0010-destroy-acr-on-teardown.md)). Rebuild requires re-mirror.
6. **Scaffold-complete is not live-validated.** Topics 00–13 lived and were torn down. Topics 14–20 stay labeled scaffold.

## Honesty labels

| Label | Use |
|-------|-----|
| **Lived** | Setup Topics 00–13 and the ADRs that governed them (0001–0012). |
| **Scaffold** | Setup Topics 14–20 and ADRs 0013–0017. |
| **Inactive** | Public DNS and screenshots after teardown. |

## Voice

Write as a production engineer teaching from a lived pilot. Be specific. Name files. Do not market. Do not call a namespace-on-one-cluster design “enterprise HA.”
