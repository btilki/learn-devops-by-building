from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
CHAPTERS = range(1, 15)


def run(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode, output


def git_state() -> tuple[str, bool]:
    proc = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return "absent (companion-lab freeze pending)", True
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", "."],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if status.stdout.strip():
        return "dirty", False
    return "clean", True


def main() -> None:
    lines = ["Northwind SRE companion-lab matrix", ""]
    failures = 0
    for number in CHAPTERS:
        chapter = f"{number:02d}"
        for kind in ("baseline", "checkpoint"):
            script = ROOT / "checkpoints" / f"chapter-{chapter}" / f"{kind}.py"
            code, output = run([PYTHON, str(script)])
            last = output.splitlines()[-1] if output else f"exit {code}"
            status = "pass" if code == 0 else "FAIL"
            if code != 0:
                failures += 1
            lines.append(f"chapter-{chapter}-{kind}: {status} — {last}")

    git_label, git_ok = git_state()
    lines.append("")
    lines.append(f"git working tree: {git_label}")
    require_clean = os.environ.get("MATRIX_REQUIRE_CLEAN") == "1"
    if require_clean and not git_ok:
        failures += 1
        lines.append("freeze gate: working tree is not clean")
    elif git_label.startswith("absent"):
        lines.append("freeze gate: git tags and release manifest are unpublished")

    report = ROOT / "build" / "matrix-report.txt"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nmatrix report: {report}")
    if failures:
        raise SystemExit(f"matrix failed: {failures} check(s)")
    print("matrix: passed")


if __name__ == "__main__":
    main()
