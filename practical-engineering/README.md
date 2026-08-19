# Practical Engineering Series

Production books for **DevOps**, **DevSecOps**, **Platform Engineering**, and **SRE**.

Each book is a numbered manuscript under its folder. Start with `00-how-to-use-this-book.md`, then the numbered chapters.

The books share one Northwind Commerce system. Later books inherit the earlier path; they do not repeat it as new work.

This series lives under `books/practical-engineering/`. The Boutique Production Series is a separate tree: [`../boutique-production/`](../boutique-production/).

## Books

| Book | Path | PDF |
| --- | --- | --- |
| Practical DevOps Engineering | [devops/](devops/) | [v1.0](releases/practical-devops-engineering-v1.0.pdf) |
| Practical DevSecOps Engineering | [devsecops/](devsecops/) | [v1.0](releases/practical-devsecops-engineering-v1.0.pdf) |
| Practical Platform Engineering | [platform/](platform/) | [v1.0](releases/practical-platform-engineering-v1.0.pdf) |
| Practical SRE Engineering | [sre/](sre/) | [v1.0](releases/practical-sre-engineering-v1.0.pdf) |

Reading order: DevOps → DevSecOps → Platform → SRE.

Those four titles share one Northwind Commerce lab. Their manuscripts are frozen. See [SERIES-DECISIONS.md](SERIES-DECISIONS.md).

## Companion labs

Runnable Northwind labs live under [labs/](labs/). Each book’s lab root is `labs/<book>/northwind/`.

From the repository root:

```text
books/practical-engineering/labs/<book>/northwind/
```

## Series files

| Path | Purpose |
| --- | --- |
| [SERIES-DECISIONS.md](SERIES-DECISIONS.md) | Cross-book decisions |
| [SERIES-PUBLICATION-STYLE.md](SERIES-PUBLICATION-STYLE.md) | Publication style |
| [releases/](releases/) | Published PDFs (Word files are not in this repository) |
| [tools/docx/](tools/docx/) and [tools/pdf/](tools/pdf/) | Local Word/PDF builders (not published) |

Frozen identity tables (`sre/BOOK-PLAN.md`, `SERIES-DECISIONS.md`) are relative to this folder, which is the old series root.

## License

© Birol Tilki. Licensed under [CC BY 4.0](../LICENSE).
