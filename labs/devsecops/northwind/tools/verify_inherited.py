from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "inherited" / "devops-v1.1"


def verify() -> None:
    manifest = yaml.safe_load((BASE / "MANIFEST.yaml").read_text(encoding="utf-8"))
    if manifest["source"]["companion_lab_commit"] != "4c6dc1ff486d101c12e6dbee1480a49ec9eca485":
        raise ValueError("unexpected inherited DevOps commit")
    for interface in manifest["interfaces"]:
        path = BASE / interface["local_path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        content = path.read_bytes()
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != interface["local_sha256"]:
            raise ValueError(f"inherited interface checksum mismatch: {path}")
        document = yaml.safe_load(content)
        if document.get("schema_version") != 1:
            raise ValueError(f"unsupported inherited interface: {path}")


if __name__ == "__main__":
    verify()
    print("inherited interface verification: passed")
