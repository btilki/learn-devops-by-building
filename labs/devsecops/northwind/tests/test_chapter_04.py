import copy
import importlib.util
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "checkpoints/chapter-04/evaluate.py"
s = importlib.util.spec_from_file_location("c4", p)
assert s and s.loader
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)


def test_valid_workflow():
    a, b, c = (copy.deepcopy(x) for x in m.inputs())
    next(x for x in a["subjects"] if x["id"] == "release-workflow")["status"] = "active"
    assert (
        m.authorize(
            "release-workflow",
            {"issuer": "northwind-oidc", "audience": "northwind-registry", "lifetime_seconds": 600},
            "publish-artifact",
            "northwind-registry",
            "build",
            a,
            b,
            c,
            record=False,
        )["result"]
        == "allow"
    )


def test_wrong_audience_denied():
    a, b, c = m.inputs()
    assert (
        "audience-rejected"
        in m.authorize(
            "release-workflow",
            {
                "issuer": "northwind-oidc",
                "audience": "northwind-production",
                "lifetime_seconds": 600,
            },
            "publish-artifact",
            "northwind-registry",
            "build",
            a,
            b,
            c,
            record=False,
        )["reasons"]
    )


def test_active_compromised_session_retains_source_access_before_containment():
    a, b, c = (copy.deepcopy(x) for x in m.inputs())
    next(x for x in a["subjects"] if x["id"] == "compromised-session")["status"] = "active"
    assert (
        m.authorize(
            "compromised-session",
            {
                "issuer": "northwind-human-idp",
                "audience": "northwind-source",
                "lifetime_seconds": 600,
            },
            "propose-change",
            "northwind-source",
            "repository",
            a,
            b,
            c,
            record=False,
        )["result"]
        == "allow"
    )


def test_revocation_denies_previously_valid_source_access():
    a, b, c = (copy.deepcopy(x) for x in m.inputs())
    next(x for x in a["subjects"] if x["id"] == "compromised-session")["status"] = "revoked"
    decision = m.authorize(
        "compromised-session",
        {"issuer": "northwind-human-idp", "audience": "northwind-source", "lifetime_seconds": 600},
        "propose-change",
        "northwind-source",
        "repository",
        a,
        b,
        c,
        record=False,
    )
    assert "revoked-subject" in decision["reasons"]


def test_start_state_allows_inherited_production_authority():
    a, b, c = m.start_state()
    decision = m.authorize(
        "northwind-ci",
        {
            "issuer": "northwind-shared",
            "audience": "northwind-production",
            "lifetime_seconds": 86400,
            "reusable": True,
        },
        "reconcile-deployment",
        "northwind-production",
        "production",
        a,
        b,
        c,
        record=False,
    )
    assert decision["result"] == "allow"
    assert m.trace_errors(decision)


PRODUCTION_ATTEMPT = (
    "compromised-session",
    {
        "issuer": "northwind-human-idp",
        "audience": "northwind-production",
        "lifetime_seconds": 86400,
        "reusable": True,
    },
    "reconcile-deployment",
    "northwind-production",
    "production",
)


EVERY_AUDIENCE = ["northwind-source", "northwind-registry", "northwind-production"]


def widen_issuer_audiences(subjects, roles, trust):
    for issuer in trust["issuers"]:
        issuer["audiences"] = list(EVERY_AUDIENCE)


def widen_subject_audiences(subjects, roles, trust):
    for subject in subjects["subjects"]:
        subject["audiences"] = list(EVERY_AUDIENCE)


def extend_sessions(subjects, roles, trust):
    trust["max_session_seconds"] = 86400


def allow_reusable_tokens(subjects, roles, trust):
    trust["reusable_tokens_allowed"] = True


def accumulate_production_role(subjects, roles, trust):
    for subject in subjects["subjects"]:
        subject["roles"] = ["source-maintainer", "production-reconciler"]


MUTATIONS = {
    widen_issuer_audiences: "audience-rejected",
    widen_subject_audiences: "audience-rejected",
    extend_sessions: "session-too-long",
    allow_reusable_tokens: "reusable-token-rejected",
    accumulate_production_role: "authorization-denied",
}


def decide(mutations):
    a, b, c = (copy.deepcopy(x) for x in m.inputs())
    next(x for x in a["subjects"] if x["id"] == "compromised-session")["status"] = "active"
    for mutate in mutations:
        mutate(a, b, c)
    subject, claims, action, resource, env = PRODUCTION_ATTEMPT
    return m.authorize(subject, claims, action, resource, env, a, b, c, record=False)


def test_every_control_removed_permits_the_attempt():
    assert decide(MUTATIONS)["result"] == "allow"


def test_each_control_independently_denies_production_reconciliation():
    for kept, reason in MUTATIONS.items():
        decision = decide([x for x in MUTATIONS if x is not kept])
        assert decision["result"] == "deny", (kept.__name__, decision)
        assert reason in decision["reasons"], (kept.__name__, decision)


def test_subject_audience_binding_survives_issuer_mutation():
    a, b, c = (copy.deepcopy(x) for x in m.inputs())
    widen_issuer_audiences(a, b, c)
    decision = m.authorize(
        "release-workflow",
        {"issuer": "northwind-oidc", "audience": "northwind-production", "lifetime_seconds": 600},
        "publish-artifact",
        "northwind-registry",
        "build",
        a,
        b,
        c,
        record=False,
    )
    assert "audience-rejected" in decision["reasons"]


def test_decision_trace_is_complete():
    a, b, c = m.inputs()
    decision = m.authorize(
        "maintainer-alice",
        {"issuer": "northwind-human-idp", "audience": "northwind-source", "lifetime_seconds": 1800},
        "reconcile-deployment",
        "northwind-production",
        "production",
        a,
        b,
        c,
        record=False,
    )
    assert decision["result"] == "deny"
    assert m.trace_errors(decision) == []
