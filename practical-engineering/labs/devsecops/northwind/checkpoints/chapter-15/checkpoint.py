from evaluate import (
    ROOT,
    eradication_errors,
    inherited_interfaces,
    invalidated_digests,
    inventory_errors,
    load,
    load_module,
)

inventory = load(ROOT / "recovery/trust-inventory.yaml")
plan = load(ROOT / "recovery/eradication-plan.yaml")
manifest = load(ROOT / "recovery/rebuild-manifest.yaml")
interfaces = inherited_interfaces()
chapter_14 = load_module("chapter-14", "evaluate")
custody = load(ROOT / "response/evidence-manifest.yaml")
errors = {
    "inventory": inventory_errors(inventory),
    "eradication": eradication_errors(plan),
    "custody": chapter_14.verify_manifest(custody),
}
if set(manifest["required_roots"]) != set(interfaces["recovery"]["required_roots"]):
    errors["recovery_roots"] = ["inherited-recovery-roots-mismatch"]
if not set(manifest["invalidated_digests"]).issubset(invalidated_digests(inventory)):
    errors["invalidated_digests"] = ["rebuild-invalidations-not-in-inventory"]
failures = {name: values for name, values in errors.items() if values}
if failures:
    raise SystemExit(failures)
print("chapter 15 checkpoint: trust graph, eradication order, and recovery gates verified")
