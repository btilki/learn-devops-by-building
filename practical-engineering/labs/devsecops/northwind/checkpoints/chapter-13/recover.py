from evaluate import ROOT, correlate, inputs, load, normalize, write

contract, hypotheses, rule, _ = inputs()
broken_path = ROOT / "build/chapter-13-broken-events.json"
if not broken_path.exists():
    raise SystemExit("run chapter-13-contain before recovery")
corrected = load(broken_path)
deployment = load(ROOT / "supply-chain/deployment-evidence.yaml")
dependency = next(
    event for event in corrected["events"] if event["action"] == "unusual-dependency-change"
)
dependency["artifact_digest"] = deployment["artifact_digest"]
corrected_path = ROOT / "build/chapter-13-corrected-events.json"
write(corrected_path, corrected)
normalized, gaps = normalize(corrected, contract, rule)
alert = correlate(normalized, hypotheses["hypotheses"][0], rule)
if gaps or alert["result"] != "alert" or alert["evidence_count"] != 4:
    raise SystemExit(gaps or alert)
record = {
    "kind": "detection-recovery-evidence",
    "controlled_attack_detected": True,
    "required_context_complete": True,
    "corrected_events": str(corrected_path.relative_to(ROOT)),
    "correction_source": "supply-chain/deployment-evidence.yaml",
    "alert": alert,
    "coverage_limit": "modeled sources and controlled actions only",
}
path = ROOT / "build/chapter-13-recovery.json"
write(path, record)
print(f"chapter 13 recovery: controlled path detected with complete context; record={path}")
