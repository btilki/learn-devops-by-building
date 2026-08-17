# Chapter 14 checkpoint

The baseline proves that a corrupted newest plane backup can be applied with mixed tenants, that Fulfillment intent can replay into Storefront, that last known good can move off Chapter 8’s retained plane `1.0`, that Storefront can freeze by accident, and that Storefront order-success can stand in for platform recovery.

The completed checkpoint verifies independently verified plane last known good, explicit tenant continue or freeze, rejection of mixed-tenant replay, inherited restore roots without treating them as isolation, and the limitation that this is not a regional-loss or portfolio RTO program.

`make chapter-14-failure` injects a mixed newest restore with Fulfillment replayed into Storefront and last known good `1.1` onto the completed snapshot, with Fulfillment’s own isolation row left intact, and proves mixed backup, cross-tenant replay, and missing last known good still fail.

It cannot prove regional loss or a portfolio recovery-time objective.
