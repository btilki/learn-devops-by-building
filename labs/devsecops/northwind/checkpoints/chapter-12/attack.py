import json

from evaluate import ROOT, evaluate_behavior, inputs, load

contract, policy = inputs()
attack = load(ROOT / "checkpoints/chapter-12/cases/attack-behaviors.yaml")
events = [evaluate_behavior({**attack, **item}, contract, policy) for item in attack["behaviors"]]
outcomes = {event["action"]: event["outcome"] for event in events}
expected = {
    "credential-discovery": "detected",
    "shell-execution": "blocked",
    "undeclared-egress": "blocked",
}
if outcomes != expected or any(event["errors"] for event in events):
    raise SystemExit(events)
path = ROOT / "runtime/events.jsonl"
path.write_text("".join(json.dumps(event) + "\n" for event in events))
print(f"chapter 12 attack: discovery detected; shell and egress blocked; events={path}")
