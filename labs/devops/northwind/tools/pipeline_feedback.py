#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Stage:
    name: str
    seconds: float
    needs: tuple[str, ...]


def load_pipeline(path: Path) -> tuple[float, list[Stage]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    stages = [
        Stage(item["name"], float(item["seconds"]), tuple(item.get("needs", [])))
        for item in data["stages"]
    ]
    return float(data.get("queue_seconds", 0)), stages


def validate_dependencies(stages: list[Stage]) -> list[str]:
    names = {stage.name for stage in stages}
    errors: list[str] = []
    for stage in stages:
        missing = set(stage.needs) - names
        if missing:
            errors.append(f"{stage.name} depends on missing stages: {sorted(missing)}")
    if len(names) != len(stages):
        errors.append("stage names must be unique")
    return errors


def critical_path(stages: list[Stage]) -> tuple[float, list[str]]:
    by_name = {stage.name: stage for stage in stages}
    memo: dict[str, tuple[float, list[str]]] = {}
    visiting: set[str] = set()

    def visit(name: str) -> tuple[float, list[str]]:
        if name in memo:
            return memo[name]
        if name in visiting:
            raise ValueError(f"dependency cycle includes {name}")
        visiting.add(name)
        stage = by_name[name]
        prior = [visit(dependency) for dependency in stage.needs]
        previous_seconds, previous_path = max(prior, default=(0.0, []), key=lambda item: item[0])
        result = previous_seconds + stage.seconds, [*previous_path, name]
        visiting.remove(name)
        memo[name] = result
        return result

    return max((visit(name) for name in by_name), default=(0.0, []), key=lambda item: item[0])


def has_ancestor(stages: list[Stage], stage_name: str, ancestor_name: str) -> bool:
    by_name = {stage.name: stage for stage in stages}
    pending = list(by_name[stage_name].needs)
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current == ancestor_name:
            return True
        if current not in seen:
            seen.add(current)
            pending.extend(by_name[current].needs)
    return False


def analyze(path: Path, budget_seconds: float) -> dict[str, object]:
    queue_seconds, stages = load_pipeline(path)
    errors = validate_dependencies(stages)
    names = [stage.name for stage in stages]
    required = {"lint", "test", "build"}
    missing_required = sorted(required - set(names))
    if missing_required:
        errors.append(f"missing required stages: {missing_required}")
    try:
        execution_seconds, path_names = critical_path(stages) if not errors else (0.0, [])
    except ValueError as error:
        errors.append(str(error))
        execution_seconds, path_names = 0.0, []
    order_ok = not missing_required and has_ancestor(stages, "test", "lint") and has_ancestor(
        stages, "build", "test"
    )
    total_seconds = queue_seconds + execution_seconds
    return {
        "queue_seconds": queue_seconds,
        "execution_seconds": execution_seconds,
        "total_seconds": total_seconds,
        "budget_seconds": budget_seconds,
        "budget_ok": total_seconds <= budget_seconds,
        "stages": names,
        "critical_path": path_names,
        "order_ok": order_ok,
        "dependency_errors": errors,
        "ok": total_seconds <= budget_seconds and order_ok and not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", type=Path, required=True)
    parser.add_argument("--budget-seconds", type=float, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = analyze(args.pipeline, args.budget_seconds)
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
