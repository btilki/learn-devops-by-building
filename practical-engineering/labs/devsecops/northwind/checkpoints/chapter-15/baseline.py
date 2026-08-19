from evaluate import COMPROMISED_DIGEST, ROOT, load

verification = load(ROOT / "build/chapter-14-verification.json")
case = load(ROOT / "response/case/incident.yaml")
subjects = load(ROOT / "identity/subjects.yaml")
release = next(item for item in subjects["subjects"] if item["id"] == "release-workflow")
deployment = load(ROOT / "supply-chain/deployment-evidence.yaml")
if verification["trust_restored"] is not False:
    raise SystemExit("chapter 14 containment must leave trust restoration open")
if "whether another persistence path exists" not in case["unknowns"]:
    raise SystemExit("persistence unknown was not inherited")
if release["status"] != "active" or deployment["artifact_digest"] != COMPROMISED_DIGEST:
    raise SystemExit("modeled automation and artifact persistence paths were not reproduced")
print("chapter 15 baseline: harm contained but trust roots and persistence remain unresolved")
