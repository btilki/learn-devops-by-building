# Chapter 9 checkpoint

The baseline proves that a scorecard can report green while Fulfillment disables `artifact-digest`, an inherited exception has expired, the binding copies owner and expiry, and exits are forbidden.

The completed checkpoint verifies Chapter 5 defaults as owned guardrails on paved and exit paths, scorecards that cannot emit green, exception rows that only bind inherited DevSecOps IDs, and expiry resolved from the inherited record.

`make chapter-09-failure` injects an expired-exception binding and a green Fulfillment scorecard with digest pinning off onto the completed snapshot, with identity, cluster-admin prohibition, and the Chapter 5 exit left intact, and proves green status, expiry, and the missing digest still fail.

It cannot prove that a real admission webhook enforced the default.
