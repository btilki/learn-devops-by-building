# Chapter 11 checkpoint

The baseline proves that Fulfillment can burst to 24 units on `cluster-capacity-pool` after isolation labels exist but tenant floors do not, leaving Storefront below its lease commitment, while showback bills that burst as a useful unit and Storefront order-success as platform cost.

The completed checkpoint verifies Chapter 3 tenants with floors and ceilings on `cluster-capacity-pool`, Chapter 6 lease commitments as the floor minimum, quality-gated `environment-hour` and `successful-provision` units, and showback that cannot count a starved burst or a tenant-workload metric as a useful platform unit.

`make chapter-11-failure` injects Fulfillment environment-hour usage of 24 onto the completed showback, with Storefront usage, successful-provision, and both floors left intact, and proves ceiling overflow, Storefront floor starvation, denied unlimited burst, and ungated useful-unit billing still fail.

It cannot prove that a real cloud bill or scheduler enforced the floor.
