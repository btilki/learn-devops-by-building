# Chapter 12 checkpoint

The baseline proves that Fulfillment can be onboarded with cluster-admin, that storage 2.0 can be applied to every tenant in one step without a freeze or rollback, that Fulfillment’s still-legal 1.0 contract can be broken without migration evidence, and that 1.0 can be closed while Fulfillment remains on it with no exception.

The completed checkpoint verifies Fulfillment onboarded as `tenant-operator` on the paved road, a freeze window, Storefront-then-Fulfillment cohorts, rollback to contract 1.0, GitOps source not rewritten, and an open deprecation window while Fulfillment’s 1.0 binding remains legal.

`make chapter-12-failure` injects an all-at-once 2.0 apply and a Fulfillment apply without migration evidence onto the completed snapshot, with onboarding role, deprecation window, and Storefront’s completed migration left intact, and proves freeze skip, all-at-once apply, broken v1, and missing rollback still fail.

It cannot prove that a live fleet upgraded a cluster.
