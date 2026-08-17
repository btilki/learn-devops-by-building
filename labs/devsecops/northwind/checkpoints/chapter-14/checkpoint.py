import json

from evaluate import (
    ROOT,
    collect_evidence,
    containment_errors,
    evidence_sources,
    load,
    manifest,
    timeline,
    verify_manifest,
    write,
)

plan = load(ROOT / "response/containment-plan.yaml")
if containment_errors(plan):
    raise SystemExit(containment_errors(plan))
collected = collect_evidence(evidence_sources())
evidence = manifest(collected)
manifest_path = ROOT / "response/evidence-manifest.yaml"
write(manifest_path, evidence)
if verify_manifest(load(manifest_path)):
    raise SystemExit("evidence verification failed")
evidence_root = ROOT / "response/evidence"
events = [
    json.loads(line)
    for line in (evidence_root / "runtime/events.jsonl").read_text().splitlines()
]
alert = json.loads((evidence_root / "build/chapter-13-alert.json").read_text())
entries = timeline(
    [*events, {"time": "2026-08-15T10:13:00Z", "kind": "alert", "result": alert["result"]}]
)
write(ROOT / "response/timeline.jsonl", entries)
case_path = ROOT / "response/case/incident.yaml"
case = load(case_path)
reconciliation = load(evidence_root / "data-security/payment-reconciliation.yaml")
payment_unknown = "whether payment effects diverged from order state"
if not reconciliation["divergence_found"] and payment_unknown in case["unknowns"]:
    case["unknowns"].remove(payment_unknown)
    case["facts"].append("sampled payment effects reconcile with recorded order state")
    write(case_path, case)
print("chapter 14 checkpoint: evidence custody, ordered timeline, and staged containment verified")
