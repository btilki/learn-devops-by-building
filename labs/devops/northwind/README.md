# Northwind Commerce implementation

This is the cumulative implementation for *Practical DevOps Engineering*. Chapters contain the teaching path; this README contains setup only.

## Chapter 1 setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
make PYTHON=.venv/bin/python chapter-01-checkpoint
```

Docker is optional for Chapter 1. Generated evidence is written under `evidence/` and is not committed.

