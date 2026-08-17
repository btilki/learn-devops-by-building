from evaluate import ROOT, evaluate, inputs, load

_, policy, _ = inputs()
inventory = load(ROOT / "checkpoints/chapter-09/cases/pre-rotation-inventory.yaml")
unsafe = load(ROOT / "checkpoints/chapter-09/cases/unsafe-reference.yaml")
permissive = {
    **policy,
    "require_reference_only": False,
    "approved_storage": [*policy["approved_storage"], "ci-variable"],
    "plaintext_markers": [],
}
errors = evaluate(inventory, permissive, unsafe)
if errors:
    raise SystemExit(errors)
print("chapter 09 baseline: plaintext synthetic credential passed permissive reference policy")
