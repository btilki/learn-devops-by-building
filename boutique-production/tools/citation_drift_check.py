#!/usr/bin/env python3
"""Check Boutique Production Series citations against local clones.

Extracts repository-relative paths from manuscript Markdown and verifies each
path exists in the bound source repository. The clone wins if a path is missing.

Usage (from books/boutique-production/):
  python3 tools/citation_drift_check.py
  python3 tools/citation_drift_check.py --book gitops
  python3 tools/citation_drift_check.py --json

Does not call the GitHub API. Point SOURCE_ROOT at the Cursor folder if needed:

  SOURCE_ROOT=/path/to/Cursor python3 tools/citation_drift_check.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

BOOKS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = Path("/Users/biroltilki/Documents/Cursor")

BOOKS = {
    "gitops": {
        "manuscript": BOOKS_ROOT / "gitops",
        "repo": "boutique-eks-gitops",
    },
    "gke-sre": {
        "manuscript": BOOKS_ROOT / "gke-sre",
        "repo": "boutique-gke-sre",
    },
    "aks-devsecops": {
        "manuscript": BOOKS_ROOT / "aks-devsecops",
        "repo": "boutique-aks-devsecops",
    },
}

# Fence header: ```12:34:docs/ci.md  or  ```docs/ci.md
FENCE_HEADER = re.compile(
    r"^```(?:[\w.+-]+)?\s*\n?(?:(\d+):(\d+):)?([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)\s*$",
    re.MULTILINE,
)
FENCE_INLINE = re.compile(
    r"^```(\d+):(\d+):([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)\s*$",
    re.MULTILINE,
)

# Backtick paths that look like repo files, not manuscript files.
# Require a file extension so prose like `docs/architecture/02` is ignored.
BACKTICK_PATH = re.compile(
    r"`("
    r"(?:docs|gitops|terraform|charts|policies|pipelines|observability|tests|"
    r"examples|scripts|assets|ci|\.github)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+|"
    r"(?:README|ARCHITECTURE|ROADMAP|PROJECT|SECURITY|CHANGELOG|CONTRIBUTING|"
    r"CODEOWNERS|REPOSITORY_STRUCTURE|LICENSE)\.md|"
    r"\.gitlab-ci\.yml|versions\.yaml|Makefile|\.pre-commit-config\.yaml|"
    r"\.checkov\.yaml|\.gitleaks\.toml"
    r")`"
)

SKIP_PREFIXES = (
    "books/",
    "books-prompts/",
    "../",
)

MANUSCRIPT_ONLY = {
    "00-how-to-use-this-book.md",
    "BOOK-PLAN.md",
    "GLOSSARY.md",
    "REFERENCES.md",
    "README.md",
    "EDITORIAL-CONVENTIONS.md",
}

# Honesty claims: the manuscript cites a path that must not exist (teaching absence).
KNOWN_ABSENT = {
    "gke-sre": {"CHANGELOG.md"},
    "aks-devsecops": {
        ".github/workflows/ci.yml",
        ".github/workflows/mirror.yml",
    },
}


def normalize(path: str) -> str:
    while path.startswith("./"):
        path = path[2:]
    return path


def extract_paths(text: str) -> set[str]:
    found: set[str] = set()
    for match in FENCE_INLINE.finditer(text):
        found.add(normalize(match.group(3)))
    for match in BACKTICK_PATH.finditer(text):
        path = normalize(match.group(1))
        if path in MANUSCRIPT_ONLY:
            continue
        if path.startswith(SKIP_PREFIXES):
            continue
        found.add(path)
    return found


def check_book(book_id: str, source_root: Path) -> dict:
    cfg = BOOKS[book_id]
    manuscript = cfg["manuscript"]
    repo = source_root / cfg["repo"]
    missing: list[dict] = []
    cited: dict[str, list[str]] = {}

    if not repo.is_dir():
        return {
            "book": book_id,
            "repo": str(repo),
            "error": "source repository not found",
            "cited": 0,
            "missing": [],
        }

    for md in sorted(manuscript.glob("*.md")):
        if md.name in {"BOOK-PLAN.md", "EDITORIAL-CONVENTIONS.md"}:
            continue
        text = md.read_text(encoding="utf-8")
        for path in extract_paths(text):
            if path in KNOWN_ABSENT.get(book_id, set()):
                continue
            cited.setdefault(path, []).append(md.name)
            target = repo / path
            if not target.exists():
                missing.append(
                    {
                        "path": path,
                        "chapter": md.name,
                    }
                )

    unique_missing = []
    seen = set()
    for item in missing:
        key = (item["path"], item["chapter"])
        if key in seen:
            continue
        seen.add(key)
        unique_missing.append(item)

    return {
        "book": book_id,
        "repo": str(repo),
        "cited": len(cited),
        "missing": unique_missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", choices=sorted(BOOKS), help="Check one title only")
    parser.add_argument(
        "--source-root",
        default=os.environ.get("SOURCE_ROOT", str(DEFAULT_SOURCE_ROOT)),
        help="Directory that contains the three boutique clones",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    source_root = Path(args.source_root)
    book_ids = [args.book] if args.book else list(BOOKS)
    reports = [check_book(book_id, source_root) for book_id in book_ids]

    if args.json:
        json.dump(reports, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        total_missing = 0
        for report in reports:
            print(f"{report['book']}: {report.get('cited', 0)} cited paths")
            if report.get("error"):
                print(f"  ERROR: {report['error']}")
                total_missing += 1
                continue
            if not report["missing"]:
                print("  OK — every extracted path exists in the clone")
                continue
            total_missing += len(report["missing"])
            for item in report["missing"]:
                print(f"  MISSING {item['path']}  (from {item['chapter']})")
        if total_missing:
            print(f"\n{total_missing} missing citation(s). The clone wins; fix the manuscript.")
        else:
            print("\nNo missing citations.")

    return 1 if any(r.get("error") or r.get("missing") for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
