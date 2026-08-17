from datetime import UTC, datetime

from evaluate import ROOT, evaluate, inputs, load, write

state_path = ROOT / "build/chapter-11-exception-state.json"
if not state_path.exists():
    raise SystemExit("run chapter-11-contain before recovery")
rules, points, exceptions, governance = inputs()
now = datetime(2026, 8, 15, 12, 1, tzinfo=UTC)
expired = evaluate(rules, points, exceptions, governance, now)
if not any(error.startswith("exception-expired:") for error in expired):
    raise SystemExit("exception did not expire automatically")
write(state_path, {"kind": "exception-state", "exceptions": []})
normal = {**exceptions, "exceptions": []}
if evaluate(rules, points, normal, governance) or load(state_path)["exceptions"]:
    raise SystemExit("normal enforcement did not resume after exception removal")
record = {
    "kind": "policy-recovery-evidence",
    "removed_exception": exceptions["exceptions"][0]["id"],
    "removed_bypass": "bypass-release-pressure",
    "active_exception_ids": [],
    "normal_enforcement": "verified",
    "policy_version": rules["version"],
}
path = ROOT / "build/chapter-11-recovery.json"
write(path, record)
print(f"chapter 11 recovery: state emptied and blocking enforcement resumed; record={path}")
