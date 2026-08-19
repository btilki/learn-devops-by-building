from evaluate import ROOT, load, write_json

path = ROOT / "build/chapter-07-attack-decision.json"
if not path.exists():
    raise SystemExit("run chapter-07-attack before containment")
attack = load(path)
if attack["result"] != "deny":
    raise SystemExit("attack artifact was not denied")
revocations = {
    "kind": "build-trust-revocation",
    "builders": [attack["builder"]],
    "signing_keys": [attack["signing_key"]],
    "source_decision": str(path.relative_to(ROOT)),
    "status": "active",
}
output = ROOT / "build/chapter-07-revocations.json"
write_json(output, revocations)
print(f"chapter 07 containment: decision subjects revoked; record={output}")
