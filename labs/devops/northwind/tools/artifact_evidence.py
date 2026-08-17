#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "dist/storefront-api.tar"
EVIDENCE = ROOT / "evidence/chapter-02"
INPUTS = [
    ROOT / "Dockerfile",
    ROOT / "requirements.txt",
    ROOT / "services/storefront-api/app/__init__.py",
    ROOT / "services/storefront-api/app/main.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def deterministic_artifact(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w") as archive:
        for source in sorted(INPUTS, key=lambda item: item.relative_to(ROOT).as_posix()):
            relative = source.relative_to(ROOT).as_posix()
            content = source.read_bytes()
            info = tarfile.TarInfo(relative)
            info.size = len(content)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = "root"
            info.gname = "root"
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(content))


def requirements() -> list[tuple[str, str]]:
    packages: list[tuple[str, str]] = []
    for raw in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        name, separator, version = value.partition("==")
        packages.append((name, version if separator else "NOASSERTION"))
    return packages


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(policy_path: Path) -> dict[str, object]:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    deterministic_artifact(ARTIFACT)
    digest = sha256(ARTIFACT)
    artifact_ref = f"{policy['artifactName']}@sha256:{digest}"
    manifest = {
        "artifact": artifact_ref,
        "digest": {"sha256": digest},
        "promoteWithoutRebuild": True,
    }
    sbom = {
        "SPDXID": "SPDXRef-DOCUMENT",
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "name": "storefront-api-local-build-inputs",
        "documentNamespace": f"https://northwind.example/sbom/{digest}",
        "creationInfo": {"creators": ["Tool: northwind-artifact-evidence"]},
        "packages": [
            {
                "SPDXID": f"SPDXRef-Package-{index}",
                "name": name,
                "versionInfo": version,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
            }
            for index, (name, version) in enumerate(requirements(), start=1)
        ],
    }
    provenance = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [{"name": policy["artifactName"], "digest": {"sha256": digest}}],
        "predicate": {
            "buildDefinition": {
                "buildType": policy["buildType"],
                "externalParameters": {
                    "source": policy["sourceRepository"],
                    "revision": policy["sourceRevision"],
                },
                "internalParameters": {},
                "resolvedDependencies": [],
            },
            "runDetails": {"builder": {"id": policy["builderId"]}, "metadata": {}},
        },
    }
    write_json(EVIDENCE / "manifest.json", manifest)
    write_json(EVIDENCE / "sbom.spdx.json", sbom)
    write_json(EVIDENCE / "provenance.json", provenance)
    return manifest


def verify(policy_path: Path) -> tuple[bool, dict[str, bool]]:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    sbom = json.loads((EVIDENCE / "sbom.spdx.json").read_text(encoding="utf-8"))
    provenance = json.loads((EVIDENCE / "provenance.json").read_text(encoding="utf-8"))
    actual = sha256(ARTIFACT)
    subject = provenance["subject"][0]
    definition = provenance["predicate"]["buildDefinition"]
    checks = {
        "artifact_digest_matches_manifest": manifest["digest"]["sha256"] == actual,
        "artifact_digest_matches_provenance": subject["digest"]["sha256"] == actual,
        "artifact_name_expected": subject["name"] == policy["artifactName"],
        "predicate_type_expected": provenance["predicateType"]
        == "https://slsa.dev/provenance/v1",
        "builder_expected": provenance["predicate"]["runDetails"]["builder"]["id"]
        == policy["builderId"],
        "source_expected": definition["externalParameters"]["source"]
        == policy["sourceRepository"],
        "revision_expected": definition["externalParameters"]["revision"]
        == policy["sourceRevision"],
        "build_type_expected": definition["buildType"] == policy["buildType"],
        "sbom_is_spdx_23": sbom["spdxVersion"] == "SPDX-2.3",
        "sbom_lists_direct_dependencies": {item["name"] for item in sbom["packages"]}
        == {name for name, _ in requirements()},
        "promotion_uses_digest": manifest["artifact"].endswith(f"@sha256:{actual}"),
        "promotion_does_not_rebuild": manifest["promoteWithoutRebuild"] is True,
    }
    return all(checks.values()), checks


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("build", "verify"):
        child = subparsers.add_parser(command)
        child.add_argument("--policy", type=Path, default=ROOT / "release/expectations.json")
    tamper = subparsers.add_parser("tamper")
    tamper.add_argument("--artifact", type=Path, default=ARTIFACT)
    args = parser.parse_args()
    if args.command == "build":
        print(json.dumps(build(args.policy), indent=2))
        return 0
    if args.command == "tamper":
        with args.artifact.open("ab") as stream:
            stream.write(b"tampered-after-build\n")
        print(f"tampered={args.artifact.relative_to(ROOT)}")
        return 0
    ok, checks = verify(args.policy)
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

