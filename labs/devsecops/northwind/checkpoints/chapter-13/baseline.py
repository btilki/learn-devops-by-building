from evaluate import alerts, inputs, normalize

contract, _, rule, events = inputs()
normalized, gaps = normalize(events, contract, rule)
empty_catalog = {"hypotheses": []}
if (
    gaps
    or len({event["source"] for event in normalized}) != 4
    or alerts(normalized, empty_catalog, rule)
):
    raise SystemExit("fragmented evidence baseline did not reproduce")
print("chapter 13 baseline: four valid signals had no detection hypothesis and produced no alert")
