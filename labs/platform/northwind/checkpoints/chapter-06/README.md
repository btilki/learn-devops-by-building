# Chapter 6 checkpoint

The baseline proves that a shared `dev-cluster-admin` grant still lets Fulfillment mutate Storefront’s environment and steal quota, while Fulfillment’s own lease has no expiry and drops inherited federated identity.

The completed checkpoint verifies request-to-lease binding, Chapter 3 environment ids, `kubernetes-control-plane` and `cluster-capacity-pool` sharing, tenant-scoped identity claims, TTL, quota bounds, and isolation invariants joined from Chapter 3 `denied_inheritance`.

`make chapter-06-failure` injects a Fulfillment scale of the completed Storefront lease, with current TTL and identity left intact, and proves cross-tenant mutation and `dev-cluster-admin` still fail.

It cannot prove that a real namespace, VPC, or identity provider was provisioned.
