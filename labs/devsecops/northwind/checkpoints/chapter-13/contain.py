from evaluate import ROOT, correlate, inputs, load, normalize, write

alert_path = ROOT / "build/chapter-13-alert.json"
if not alert_path.exists() or load(alert_path)["result"] != "alert":
    raise SystemExit("run chapter-13-attack before containment")
contract, hypotheses, rule, events = inputs()
broken = {"events": [dict(event) for event in events["events"]]}
broken["events"][1].pop("artifact_digest")
broken_path = ROOT / "build/chapter-13-broken-events.json"
write(broken_path, broken)
normalized, gaps = normalize(broken, contract, rule)
alert = correlate(normalized, hypotheses["hypotheses"][0], rule)
if not gaps or not contract["missing_telemetry_alert"] or alert["result"] != "no-alert":
    raise SystemExit("missing telemetry was interpreted as safety")
record = {
    "kind": "detection-containment",
    "alert": str(alert_path.relative_to(ROOT)),
    "telemetry_gap_alarm": gaps,
    "incomplete_events": str(broken_path.relative_to(ROOT)),
    "attack_path_result": alert["result"],
    "evidence_loss_impact": "correlation-incomplete",
}
path = ROOT / "build/chapter-13-containment.json"
write(path, record)
print(
    f"chapter 13 containment: context gap alarmed and incomplete path did not alert; record={path}"
)
