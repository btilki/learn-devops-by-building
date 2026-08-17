from evaluate import ROOT, evaluate_behavior, inputs, load

contract, policy = inputs()
attack = load(ROOT / "checkpoints/chapter-12/cases/attack-behaviors.yaml")
permissive = {**policy, "actions": {action: "detect" for action in policy["actions"]}}
event = evaluate_behavior({**attack, **attack["behaviors"][1]}, contract, permissive)
if event["outcome"] != "detected":
    raise SystemExit("permissive runtime baseline did not reproduce")
print("chapter 12 baseline: detection-only runtime policy allowed shell execution to proceed")
