# Northwind SRE Companion Lab

This is the cumulative companion lab for *Practical SRE Engineering*. It is independent of the DevOps, DevSecOps, and Platform labs and consumes only reduced, checksum-identified interface fixtures under `inherited/devops-v1.1/`, `inherited/devsecops-v1.0/`, and `inherited/platform-v1.0/`.

The working tree currently implements Chapters 1–14. Companion-lab snapshot tags are published: `v1.0-chapter-NN-start` and `v1.0-chapter-NN-complete`, with reader-facing aliases `chapter-NN-start` and `chapter-NN-complete`.

## Environment

Use Python 3.13:

```bash
python3 -m venv .venv
source .venv/bin/activate
make bootstrap
make test
make lint
make audit
make matrix
```

`make` uses `.venv/bin/python` only when that interpreter actually runs. A copied or broken virtualenv is ignored in favor of `python3`. Do not ship `.venv`, `.pytest_cache`, `.ruff_cache`, or `__pycache__` in a release ZIP; recreate the environment locally. Runtime and development pins live in `requirements.in` and `requirements-dev.in`; `requirements.txt` and `requirements-dev.txt` are hashed lockfiles.

`make matrix` runs tests, lint, audit, all Chapter 1–14 baselines, and all Chapter 1–14 checkpoints, then writes `build/matrix-report.txt`. It reports git state. `MATRIX_REQUIRE_CLEAN=1 make matrix` also fails if the lab worktree is dirty.

## Commands

```text
make chapter-01-baseline
make chapter-01-checkpoint
make chapter-02-baseline
make chapter-02-checkpoint
make chapter-03-baseline
make chapter-03-checkpoint
make chapter-04-baseline
make chapter-04-checkpoint
make chapter-05-baseline
make chapter-05-checkpoint
make chapter-06-baseline
make chapter-06-checkpoint
make chapter-07-baseline
make chapter-07-checkpoint
make chapter-08-baseline
make chapter-08-checkpoint
make chapter-09-baseline
make chapter-09-checkpoint
make chapter-10-baseline
make chapter-10-checkpoint
make chapter-11-baseline
make chapter-11-checkpoint
make chapter-12-baseline
make chapter-12-checkpoint
make chapter-13-baseline
make chapter-13-checkpoint
make chapter-14-baseline
make chapter-14-checkpoint
```

A successful baseline means the evaluator correctly found the expected unsafe reliability definition, SLI selection, SLO catalog, error-budget policy, page map, on-call label, toil decision, dependency contract, retry cascade, one-path incident close, unverified learning action, inherited restore claimed as regional recovery, single mixed-backup game day marked complete, or mixed-region replay declared recovered. It does not mean the portfolio is already reliable.

## Schemas

The frozen planning inventory named a shared `artifact-envelope.schema.json`. Implementation uses kind-specific schemas instead, the same refinement as Platform and DevSecOps: every governed artifact carries `schema_version`, `kind`, and `id`. The full decision envelope (`owner`, `status`, `effective_at`, `review`) is for later decision records, not Chapter 1 list registers. Chapter 1 owners may record an empty `journeys` list when the owner is the platform team remaining on job-time proofs. Chapter 2 candidate identifiers keep inherited underscores such as `order_success_ratio`.

## Evidence limits

The lab validates deterministic local models. It does not prove that a real telemetry backend, paging vendor, identity provider, multi-region fleet, or incident-management product behaves as the fixture does. Chapter 1 cannot prove that the chosen journeys are the right journeys for a real company. Chapter 2 cannot prove that an accepted indicator is the objectively correct good-event definition under live traffic. Chapter 3 cannot prove that 99.5 percent or 99.0 percent is the right commercial target, and it does not compute burn from a real telemetry backend. Chapter 4 cannot halt a live release or fleet. Chapter 5 cannot send a real page. Chapter 6 cannot operate a real paging or calendar product. Chapter 7 cannot measure real engineer hours. Chapter 8 cannot query a real provider status page. Chapter 9 cannot inject live overload. Chapter 10 cannot run a real incident-management tool. Chapter 11 cannot prove an organization actually learned. Chapter 12 cannot discover unknown real data gravity. Chapter 13 cannot chaos-test a live fleet. Chapter 14 cannot prove a real multi-region fail-over; it models **Evidence of portfolio recovery** only.
