from evaluate import inputs

_, findings, _, decisions, _, policy = inputs()
severity = {name: rank for rank, name in enumerate(policy["severity_order"])}
by_severity = sorted(findings["findings"], key=lambda item: severity[item["severity"]])
by_decision = sorted(decisions["decisions"], key=lambda item: item["priority"])
if by_severity[0]["id"] == by_decision[0]["finding"]:
    raise SystemExit("severity-only queue did not reproduce the unsafe ordering")
print("chapter 08 baseline: Northwind severity ordering displaced the exploitable order-path flaw")
