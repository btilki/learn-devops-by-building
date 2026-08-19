# Boutique series tools

These helpers belong to the **Boutique Production Series**, not the frozen Northwind labs.

| Script | Purpose |
| --- | --- |
| [citation_drift_check.py](citation_drift_check.py) | Extract cited repo paths from `gitops/`, `gke-sre/`, and `aks-devsecops/` manuscripts and verify they exist in the local clones |

```bash
# From books-prompts/books/boutique-production/
python3 tools/citation_drift_check.py
python3 tools/citation_drift_check.py --book gitops
```

The checker reads local clones under `SOURCE_ROOT` (default `/Users/biroltilki/Documents/Cursor`). It does not call the GitHub API, so it does not burn unauthenticated rate limits.

Absence can be a teaching point. `KNOWN_ABSENT` in the script lists paths the manuscript must keep citing as **missing** (GKE has no `CHANGELOG.md`; AKS has no GitHub Actions workflows). Do not add those files to “make the check green.”

If a cited path is missing and is not in `KNOWN_ABSENT`, **the clone wins**. Update the manuscript; do not invent the file.
