# Chapter 8 checkpoint

The baseline proves that a reconciler with a cluster-admin token can apply Fulfillment intent onto Storefront, approve its own plane upgrade, continue past a failed upgrade without last known good, rewrite source, and drop inherited federated identity.

The completed checkpoint verifies a tenant-scoped plane subject on `kubernetes-control-plane`, admission of Chapter 7 contract versions, inherited GitOps state without source rewrite, inherited authorization fields with self-approval denied, and a failed plane upgrade that retains last known good.

`make chapter-08-failure` injects cluster-admin onto the completed plane subject and a Fulfillment reconcile that mutates Storefront, with identity, GitOps, admission, and last known good left intact, and proves shared plane-admin and cross-tenant reconcile still fail.

It cannot prove that a real Kubernetes control plane reconciled a live object.
