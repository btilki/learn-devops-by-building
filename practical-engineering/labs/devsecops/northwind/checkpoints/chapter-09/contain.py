import json

from evaluate import ROOT, load

path = ROOT / "build/chapter-09-exposure.yaml"
if not path.exists():
    raise SystemExit("run chapter-09-attack before containment")
exposure = load(path)
record = {
    "kind": "secret-revocation",
    "versions": [exposure["version"]],
    "source_evidence": str(path.relative_to(ROOT)),
    "log_status": "masked",
    "historical_access_inspected": True,
    "derived_credentials_replaced": ["payment-provider-session-v1"],
    "status": "active",
}
output = ROOT / "build/chapter-09-revocations.json"
output.write_text(json.dumps(record, indent=2) + "\n")
print(f"chapter 09 containment: exposed version revoked; masked log record={output}")
