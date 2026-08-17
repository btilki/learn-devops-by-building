from __future__ import annotations

import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPROMISED_DIGEST = (
    "sha256:9f4e7b3e0ac870d986f228f4d3869f46a7c506f77d5f4eaa59a24a1867d65f09"
)


def load(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def reset() -> None:
    copy(ROOT / "response/evidence/identity/subjects.yaml", ROOT / "identity/subjects.yaml")
    copy(
        ROOT / "response/evidence/supply-chain/deployment-evidence.yaml",
        ROOT / "supply-chain/deployment-evidence.yaml",
    )
    copy(
        ROOT / "response/evidence/data-security/payment-reconciliation.yaml",
        ROOT / "data-security/payment-reconciliation.yaml",
    )
    copy(
        ROOT / "checkpoints/chapter-09/cases/recovered-inventory.yaml",
        ROOT / "secrets/inventory.yaml",
    )
    copy(
        ROOT / "checkpoints/chapter-09/cases/recovered-references.yaml",
        ROOT / "secrets/references.yaml",
    )
    copy(
        ROOT / "checkpoints/chapter-14/cases/open-incident.yaml",
        ROOT / "response/case/incident.yaml",
    )

    contract = load(ROOT / "checkpoints/chapter-12/cases/order-worker-contract.yaml")
    contract["status"] = "active"
    write(ROOT / "runtime/contracts/order-worker.yaml", contract)

    write(
        ROOT / "runtime/policies/behavior.yaml",
        {
            "schema_version": 1,
            "kind": "runtime-behavior-policy",
            "policy_version": "runtime-v1",
            "actions": {
                "shell-execution": "prevent",
                "credential-discovery": "detect",
                "undeclared-egress": "prevent",
                "privilege-escalation": "prevent",
                "root-filesystem-write": "prevent",
            },
            "require_attribution": True,
            "require_deployment_context": True,
        },
    )

    write(
        ROOT / "supply-chain/provenance.yaml",
        {
            "schema_version": 1,
            "kind": "build-provenance",
            "artifact": {"name": "order-worker", "digest": COMPROMISED_DIGEST},
            "source": {"revision": "8a19e60"},
            "dependency_resolution": (
                "sha256:3bf2802d2beeaf1c327954060aa2f4df1dbdb538d25b64420e018fb810c10e2e"
            ),
            "builder": {
                "id": "northwind-builder-v3",
                "isolated": True,
                "hermetic": True,
            },
            "parameters": {"release": True},
            "signature": {"valid": True, "key_id": "release-key-v3"},
            "sbom_digest": (
                "sha256:1c91cf4b66cb3de446641f528886d0bfa447a7fcb04ebb27c20d37f07dc5f842"
            ),
            "transparency_entry": "northwind-log-0815",
            "release": {
                "requester": "release-workflow",
                "approvers": ["release-manager"],
                "target": "production",
            },
        },
    )

    write(
        ROOT / "secrets/provider-state.yaml",
        {
            "schema_version": 1,
            "kind": "modeled-payment-provider-state",
            "expected_effects": ["payment-order-1042-authorized"],
            "observed_effects": ["payment-order-1042-authorized"],
            "accepted_versions": ["payment-v2"],
            "service_health": "healthy",
        },
    )

    points = load(ROOT / "policy/enforcement-points.yaml")
    production = next(item for item in points["points"] if item["id"] == "production-deploy")
    production["status"] = "active"
    write(ROOT / "policy/enforcement-points.yaml", points)

    print(
        "lab reset: identity, secrets, runtime, deployment, provenance, "
        "and incident restored to the Chapter 14 start state"
    )


if __name__ == "__main__":
    reset()
