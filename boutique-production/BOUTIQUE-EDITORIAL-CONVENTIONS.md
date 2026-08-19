# Boutique Production Series — Editorial Conventions

**Status:** Active  
**Applies to:** `gitops/`, `gke-sre/`, `aks-devsecops/`

## Voice

Write as a production engineer teaching from a lived pilot. Be specific. Name files. Quote short real excerpts. Do not market. Do not call a namespace-on-one-cluster design “production-ready” or “enterprise HA.”

## Chapter skeleton

```text
# Numbered Title

Opening production question and why the unsafe default fails.

## 1. Unsafe starting state (or inherited gap)
## 2. The production model
   Theory box
## 3. How this repository implements it
   Practice box + real paths + short excerpts
## 4. Test the design under failure
   Scenario name
   Severity / plausible harm / potential blast radius / Bounded by
   Primary principles:
   Diagnosis
   Correction or recovery
## 5. What You Learned
Durable outputs (existing repo artifacts)
Independent Practice box
```

Adjust heading names when a chapter is concept-led or decision-led. Do not invent a companion lab.

## Practice

Practice means opening a real path, interpreting a real decision, and stating what evidence would prove a change. Do not require the reader to spend cloud money unless the chapter is explicitly about rebuild or teardown. When a command is shown, it is the command the operator used in the setup guide, not a new Makefile target.

## Failure sections

Every core chapter includes a dedicated failure. Classify it. Separate diagnosis from recovery. State `Primary principles:` using only the series principles that the scenario actually exercises.

## Honesty labels

- **Lived:** Topics and milestones that ran on a real cluster before teardown.
- **Scaffold:** Files in Git that were not live-validated on this pilot.
- **Inactive:** DNS and screenshots that remain after teardown.

## Abbreviations

On first use in each reader-facing file: `**CI (Continuous Integration)**`. Do not expand inside code fences or filenames.

## Length

Core chapters: roughly 180–320 lines. How to Use: 120–180 lines. Conclusion: 80–140 lines. Glossary covers every abbreviation the book uses.

## Further reading (playbook)

After Independent Practice, a matching chapter may add:

```text
## Further reading

Playbook article **E1** restates this decision as a short public argument. It is not a second source of truth.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/E1.md
```

Use only articles the source README already lists. Do not invent unpublished IDs.

## Figures (inactive evidence)

```text
**Figure N.M — Inactive.** One sentence of what the screenshot proved on the lived pilot.

![alt](https://raw.githubusercontent.com/btilki/<repo>/main/<path>)

Source: `<path>` in the clone. Public DNS is inactive; this is historical evidence.
```

Prefer GitHub `raw.githubusercontent.com` so the manuscript does not vendor binaries. If the PNG is missing from the clone, remove the figure; do not keep a broken link.

## CHANGELOG

How to Use must tell the reader: if the clone is newer than the manuscript snapshot, start at the repository `CHANGELOG.md`. Do not restate the whole changelog in the book.

## Interview appendix

Numbered file after the conclusion. Ten questions. Each answer names files. Keep production-pilot honesty. Do not answer with a generic textbook paragraph.
