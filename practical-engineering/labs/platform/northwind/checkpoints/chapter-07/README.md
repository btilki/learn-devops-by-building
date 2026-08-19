# Chapter 7 checkpoint

The baseline proves that a storage module can become the tenant API, that Fulfillment can still send `class` after a silent `sku` rename, that compatibility does not name breaking parameter changes, that identity drops inherited federated identity, and that a network binding can reintroduce Chapter 3’s `peer-tenant-workload-network`.

The completed checkpoint verifies tenant bindings to versioned capabilities, hidden module internals kept off the tenant API, inherited artifact-digest and federated identity, live join to Chapter 3 network `denied_inheritance`, and a compatibility policy that treats parameter add/remove/rename as breaking.

`make chapter-07-failure` injects a `class` → `sku` rename onto the completed `tenant-storage` v1.0 contract, with identity, network, and other bindings left intact, and proves a breaking change without a version bump, a missing migration note, and Fulfillment’s stale `class` parameter still fail.

It cannot prove that a real Terraform or Helm module was applied.
