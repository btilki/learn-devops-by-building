# Chapter 4 checkpoint

The baseline proves that a catalog can report green while `fulfillment-api` is owned by a deleted group and the ownership timestamp is stale.

The completed checkpoint verifies living owners from Chapter 1, tenant binding from Chapter 3, escalation contacts, dependency lists, and freshness against an independent `stale_before` expectation. Completeness is computed; the catalog cannot emit its own passing status.

`make chapter-04-failure` injects a deleted-group owner onto the completed `fulfillment-api` entry, keeps the review timestamp current, and proves the evaluator still rejects a green claim.

It cannot prove that a real developer portal, identity provider, or HR system would surface the same owner.
