from evaluate import ROOT, decision, evaluate, inputs, load, write_json

revocation_path = ROOT / "build/chapter-07-revocations.json"
if not revocation_path.exists():
    raise SystemExit("run chapter-07-contain before recovery")
provenance, build, admission, resolution = inputs()
old = load(ROOT / "checkpoints/chapter-07/cases/pre-rotation-provenance.yaml")
old_errors = evaluate(old, build, admission, resolution)
if "signing-key-untrusted:release-key-v2" not in old_errors:
    raise SystemExit("retired signing authority still admits the old artifact")
errors = evaluate(provenance, build, admission, resolution)
deployment = load(ROOT / "supply-chain/deployment-evidence.yaml")
if errors or deployment["artifact_digest"] != provenance["artifact"]["digest"]:
    raise SystemExit(errors or "deployed digest does not match rebuilt artifact")
if deployment["policy_version"] != admission["policy_version"]:
    raise SystemExit("deployment used the wrong admission policy")
if deployment["environment"] != provenance["release"]["target"]:
    raise SystemExit("deployment environment does not match release approval")
if deployment["admission_result"] != "allow":
    raise SystemExit("deployment evidence does not record allowed admission")
if old["artifact"]["digest"] == provenance["artifact"]["digest"]:
    raise SystemExit("recovery did not produce a new artifact digest")
output = ROOT / "build/chapter-07-recovery-decision.json"
write_json(output, decision(provenance, admission, errors))
print(f"chapter 07 recovery: old authority denied and rebuilt digest deployed; decision={output}")
