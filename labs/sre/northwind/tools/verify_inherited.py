from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASES = (
    ROOT / "inherited" / "devops-v1.1",
    ROOT / "inherited" / "devsecops-v1.0",
    ROOT / "inherited" / "platform-v1.0",
)


def verify_tree(base: Path) -> None:
    manifest = yaml.safe_load((base / "MANIFEST.yaml").read_text(encoding="utf-8"))
    expected_commit = {
        "practical-devops-engineering-v1.1": "4c6dc1ff486d101c12e6dbee1480a49ec9eca485",
        "practical-devsecops-engineering-v1.0": "unpublished-working-tree",
        "practical-platform-engineering-v1.0": "unpublished-working-tree",
    }[manifest["id"]]
    if manifest["source"]["companion_lab_commit"] != expected_commit:
        raise ValueError(f"unexpected inherited commit: {base}")
    for interface in manifest["interfaces"]:
        path = base / interface["local_path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        content = path.read_bytes()
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != interface["local_sha256"]:
            raise ValueError(f"inherited interface checksum mismatch: {path}")
        document = yaml.safe_load(content)
        if document.get("schema_version") != 1:
            raise ValueError(f"unsupported inherited interface: {path}")


def verify() -> None:
    for base in BASES:
        verify_tree(base)


if __name__ == "__main__":
    verify()
    print("inherited interface verification: passed")
