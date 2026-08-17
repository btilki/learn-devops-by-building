#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import os
from pathlib import Path

def dockerignore(root: Path) -> list[tuple[str, bool]]:
    ignore_file = root / ".dockerignore"
    lines = ignore_file.read_text(encoding="utf-8").splitlines() if ignore_file.exists() else []
    rules: list[tuple[str, bool]] = []
    for raw in [*lines, ".git"]:
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        included_again = value.startswith("!")
        pattern = value[1:] if included_again else value
        rules.append((pattern.strip("/"), included_again))
    return rules


def ignored(relative: Path, rules: list[tuple[str, bool]], *, directory: bool = False) -> bool:
    candidate = relative.as_posix().rstrip("/")
    result = False
    for pattern, included_again in rules:
        directory_match = candidate == pattern or candidate.startswith(pattern + "/")
        glob_match = fnmatch.fnmatch(candidate, pattern) or fnmatch.fnmatch(relative.name, pattern)
        if directory_match or glob_match:
            result = not included_again
    return result


def measure(root: Path) -> tuple[int, list[tuple[int, Path]]]:
    rules = dockerignore(root)
    total = 0
    files: list[tuple[int, Path]] = []
    for directory, directories, filenames in os.walk(root):
        directory_path = Path(directory)
        directories[:] = [
            name
            for name in directories
            if not ignored((directory_path / name).relative_to(root), rules, directory=True)
        ]
        for filename in filenames:
            path = Path(directory) / filename
            relative = path.relative_to(root)
            if ignored(relative, rules):
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            total += size
            files.append((size, relative))
    return total, sorted(files, reverse=True)[:5]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--limit-bytes", type=int, required=True)
    parser.add_argument("--virtual-file-bytes", type=int, default=0)
    args = parser.parse_args()
    root = args.root.resolve()
    measured, largest = measure(root)
    total = measured + args.virtual_file_bytes
    ok = total <= args.limit_bytes
    print(f"context_bytes={total}")
    print(f"limit_bytes={args.limit_bytes}")
    for size, path in largest:
        print(f"included_file={path} bytes={size}")
    print(f"context_ok={str(ok).lower()}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
