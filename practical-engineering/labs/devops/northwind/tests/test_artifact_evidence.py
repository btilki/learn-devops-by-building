from __future__ import annotations

import json
from pathlib import Path

from tools import artifact_evidence


def test_deterministic_artifact_has_stable_digest(tmp_path: Path) -> None:
    first = tmp_path / "first.tar"
    second = tmp_path / "second.tar"
    artifact_evidence.deterministic_artifact(first)
    artifact_evidence.deterministic_artifact(second)
    assert artifact_evidence.sha256(first) == artifact_evidence.sha256(second)


def test_build_binds_manifest_and_provenance_to_artifact(tmp_path: Path, monkeypatch) -> None:
    policy = {
        "artifactName": "ghcr.io/northwind-commerce/storefront-api",
        "sourceRepository": "https://github.com/northwind-commerce/storefront",
        "sourceRevision": "test-revision",
        "builderId": "https://github.com/northwind-commerce/storefront/.github/workflows/release.yml@refs/heads/main",
        "buildType": "https://northwind.example/build-types/storefront-container/v1",
    }
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    monkeypatch.setattr(artifact_evidence, "ARTIFACT", tmp_path / "artifact.tar")
    monkeypatch.setattr(artifact_evidence, "EVIDENCE", tmp_path / "evidence")
    artifact_evidence.build(policy_path)
    ok, checks = artifact_evidence.verify(policy_path)
    assert ok
    assert all(checks.values())

