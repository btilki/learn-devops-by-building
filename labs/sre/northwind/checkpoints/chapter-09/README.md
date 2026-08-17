# Chapter 9 checkpoint

The baseline proves that unbounded `order-worker` retries, accepting work that cannot finish, counting those accepts as success, and paging Fulfillment as the payment cause turn a Storefront payment slowness into a portfolio outage with green graphs.

The completed checkpoint verifies a named payment-overload mode with user-visible refuse, journey-burn accounting, retry limit equal to the Chapter 8 payment budget, refuse-new-accepts, and a cascade denial that Fulfillment is not the payment page.

It cannot inject live overload, and it does not prove that one retry or refuse-new-accepts is the right commercial shed.
