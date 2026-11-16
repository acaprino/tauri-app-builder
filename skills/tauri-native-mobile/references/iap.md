# Purchases and entitlement reconciliation

Choose an actively maintained plugin version and inspect its installed Rust/JS declarations. Check `purchase`/`getProducts` arguments and enum names against that version. If a release needs a JS typing shim or a vendored native fix, document the upstream defect and removal condition; package version and vendor source revision are separate pins.

Treat the store as the authority for purchase state and the backend as the authority for app entitlement. Verify package/bundle, product, environment, purchase ownership, status, expiry/revocation and replay handling. Expiry alone is insufficient. Bind each purchase to an authenticated user; atomically prevent the same purchase token being claimed by multiple accounts.

Pending purchases don't grant entitlement. For Google, acknowledge eligible completed purchases within the applicable deadline (normally three days); start that window when a pending purchase becomes purchased. Make verification, durable entitlement recording and acknowledgment retryable/idempotent. A frontend acknowledgment before backend verification is not a safe generic recipe. [Google billing security](https://developer.android.com/google/play/billing/security).

Authenticate notifications, deduplicate them and requery authoritative state when needed. Notification type alone is not proof to activate/revoke: events can be stale or reordered. Apple transaction JWS verification is not by itself proof of a currently active subscription; renewal metadata belongs to the appropriate renewal/status data.

Test pending, cancel, interrupted purchase, reinstall/restore, account switch, grace/hold, refund/revoke, plan replacement and duplicate/out-of-order notifications. For multiple payment providers, bind asynchronous results to the intended account and define how competing purchases are reconciled. Refund and provider-switch policies belong to the product; any resulting mutation must be idempotent.

Sources: [Play subscriptions](https://developer.android.com/google/play/billing/lifecycle/subscriptions), [Apple server API](https://developer.apple.com/documentation/appstoreserverapi).
