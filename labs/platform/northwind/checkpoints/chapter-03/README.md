# Chapter 3 checkpoint

The baseline proves that granting Fulfillment cluster-admin “temporarily” to ship collapses isolation into a shared cluster, with namespace labels standing in for isolation dimensions.

The completed checkpoint verifies tenant owners, required isolation dimensions, prohibited inherited roles, tenant-scoped bindings, and denied sharing of cluster-admin.

It cannot discover unknown real cluster sharing outside the declared model.
