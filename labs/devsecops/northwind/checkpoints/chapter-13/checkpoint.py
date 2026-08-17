from evaluate import correlate, inputs, normalize

contract, hypotheses, rule, events = inputs()
normalized, gaps = normalize(events, contract, rule)
alert = correlate(normalized, hypotheses["hypotheses"][0], rule)
if gaps or alert["result"] != "alert" or not alert["owner"] or not alert["response"]:
    raise SystemExit(gaps or alert)
print("chapter 13 checkpoint: normalized evidence, correlation, owner, and response verified")
