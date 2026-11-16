# Remote push, background work and offline data

## Remote push is a separate service

Local notifications and [exact alarms](notifications-alarms.md) do not establish FCM/APNs registration or remote delivery. Inspect the chosen Tauri bridge and native SDK integration. Configure Android sender/app identity and iOS push entitlement, provisioning, APNs environment and provider credentials. Notification display permission, push token registration and message receipt are separate observations.

Register refresh callbacks, send current installation tokens to an authenticated backend and remove invalid/stale registrations. Bind tokens to installation and account, not a single global user field; detach old-account routing at logout/switch and handle reinstall/restore. Tokens can rotate. Never ship server send credentials in the client. [FCM token management](https://firebase.google.com/docs/cloud-messaging/manage-tokens).

Define foreground presentation and notification/data-message behavior while backgrounded. Avoid double display when the OS already presents a message. Persist message/action IDs, deduplicate receipt and route taps only after navigation and authentication readiness. A notification tap payload does not authorize access to the target account/resource. [FCM Android delivery](https://firebase.google.com/docs/cloud-messaging/android/receive-messages).

Treat remote delivery as delayed, duplicated or absent. Silent/background push on iOS is discretionary and may be throttled; it is not an exact scheduler or an always-on synchronization channel. Fetch authoritative state on resume. Keep sensitive information out of lock-screen payloads where the product requires it. [Apple background pushes](https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app).

## Background execution

Persist job intent/progress outside the WebView. Use Android WorkManager for suitable deferrable durable work, with constraints, unique work and bounded retry. Foreground services have use-case/type/launch constraints; adding a service does not grant unlimited execution. Neither a JS timer nor a Web Worker nor an open WebSocket guarantees survival. [Android WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager).

On iOS choose the supported background strategy: system-scheduled app refresh/processing, a qualifying foreground-started task, or background URLSession transfers as appropriate. Register handlers early, handle expiration, checkpoint and finish exactly once. The OS decides scheduling opportunities; don't promise a fixed polling interval. Background modes must match the actual task. [Apple background strategies](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app).

## Offline and network boundaries

Connectivity callbacks and navigator.onLine are hints, not proof that the authenticated API is reachable. Handle captive portals, radio changes, TLS failure, timeout and expired authorization separately. Native HTTP scopes/TLS and browser CORS are different controls; don't broadly disable either to make a request work.

Use a durable transactional outbox: operation ID, account, payload/schema version, retry state and server acknowledgment. Make retries idempotent, checkpoint large transfers, resolve version conflicts deliberately and retain deletion tombstones where needed. Prevent old-account jobs from running under a new login. Report “saved on device” separately from “synced”; bound retries and expose a recoverable failure state. Treat these as application contracts, not behavior automatically supplied by a plugin.

Test offline edits, restart mid-write, duplicate/out-of-order delivery, token rotation, logout before push tap, no notification permission, suspended/force-stopped app, expired worker, network loss during upload and server commit followed by client timeout. Validate the release APNs/FCM environment on the intended hardware.
