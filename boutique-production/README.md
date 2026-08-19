# Boutique Production Series

A repo-backed series for GitOps, SRE, and DevSecOps. Each title cites one lived repository. There is no Northwind companion lab.

This series lives under `books/boutique-production/`. The frozen Northwind Practical Engineering Series is a separate tree: [`../practical-engineering/`](../practical-engineering/).

Contract: [BOUTIQUE-SERIES.md](BOUTIQUE-SERIES.md) · Editorial: [BOUTIQUE-EDITORIAL-CONVENTIONS.md](BOUTIQUE-EDITORIAL-CONVENTIONS.md)

## Books

| Book | Path | Source repo |
| --- | --- | --- |
| Practical GitOps on Amazon EKS | [gitops/](gitops/) | [boutique-eks-gitops](https://github.com/btilki/boutique-eks-gitops) |
| Practical SRE on Google Kubernetes Engine | [gke-sre/](gke-sre/) | [boutique-gke-sre](https://github.com/btilki/boutique-gke-sre) |
| Practical DevSecOps on Azure Kubernetes Service | [aks-devsecops/](aks-devsecops/) | [boutique-aks-devsecops](https://github.com/btilki/boutique-aks-devsecops) |

Reading order is optional. Start each title with `00-how-to-use-this-book.md`.

## Tools

Citation drift-check (local clones, no GitHub API):

```bash
# from books/boutique-production/
python3 tools/citation_drift_check.py
python3 tools/citation_drift_check.py --book gitops
```

See [tools/README.md](tools/README.md).

## License

© Birol Tilki. Licensed under [CC BY 4.0](../LICENSE).
