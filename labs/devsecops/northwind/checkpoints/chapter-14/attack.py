import shutil
from copy import deepcopy

from evaluate import ROOT, digest, load, verify_manifest, write

preserved = load(ROOT / "response/evidence-manifest.yaml")
if verify_manifest(preserved):
    raise SystemExit("preserved evidence was invalid before the controlled test")
test_manifest = deepcopy(preserved)
first = test_manifest["items"][0]
source = ROOT / first["path"]
changed = ROOT / "build/chapter-14-tampered-evidence"
shutil.copy2(source, changed)
first["path"] = str(changed.relative_to(ROOT))
changed.write_bytes(changed.read_bytes() + b"\ncontrolled mutation\n")
findings = verify_manifest(test_manifest)
expected = [{"path": first["path"], "finding": "digest-mismatch"}]
if findings != expected:
    raise SystemExit({"expected": expected, "observed": findings})
record = {
    "kind": "investigation-failure",
    "changed_item": first["path"],
    "expected": first["sha256"],
    "observed": digest(changed),
    "custody_valid": False,
    "findings": findings,
}
write(ROOT / "build/chapter-14-attack.json", record)
print("chapter 14 attack: unverified evidence mutation invalidated the investigation claim")
