from evaluate import ROOT, decide, inputs, load, write

classification, uses, policy, _, _ = inputs()
request = load(ROOT / "checkpoints/chapter-10/cases/unsafe-request.yaml")
decision = decide(request, classification, uses, policy)
required = {
    "field-not-permitted:payment_reference",
    "store-class-exceeded:customer_email",
    "store-class-exceeded:order_total",
    "store-class-exceeded:payment_reference",
    "store-not-permitted:telemetry",
}
if decision["result"] != "deny" or not required.issubset(decision["reasons"]):
    raise SystemExit(decision)
path = ROOT / "build/chapter-10-attack-decision.json"
write(path, decision)
exposure = load(ROOT / "checkpoints/chapter-10/cases/exposed-fixture.yaml")
copies = {
    "kind": "modeled-exposed-copies",
    "copies": [
        {"id": "attack-telemetry-copy", **exposure, "store": "telemetry"},
        {"id": "attack-nonproduction-copy", **exposure, "store": "nonproduction"},
    ],
}
write(ROOT / "build/chapter-10-exposed-copies.json", copies)
print(f"chapter 10 attack: unnecessary payment field and telemetry store denied; decision={path}")
