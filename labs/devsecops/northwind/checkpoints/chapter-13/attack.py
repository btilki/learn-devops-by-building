from evaluate import ROOT, correlate, inputs, normalize, write

contract, hypotheses, rule, events = inputs()
normalized, gaps = normalize(events, contract, rule)
alert = correlate(normalized, hypotheses["hypotheses"][0], rule)
if gaps or alert["result"] != "alert":
    raise SystemExit(gaps or alert)
path = ROOT / "build/chapter-13-alert.json"
write(path, alert)
print(f"chapter 13 attack: cumulative intrusion correlated into actionable alert; alert={path}")
