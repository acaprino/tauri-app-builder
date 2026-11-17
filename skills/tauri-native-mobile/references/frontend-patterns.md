# Frontend/native boundary

Use a small typed adapter for native operations and normalize errors there. Keep platform routing separate from component state. `platform()` in the current `@tauri-apps/plugin-os` API is synchronous (`Platform`); check the installed declarations instead of assuming it returns a Promise. [OS API](https://v2.tauri.app/reference/javascript/os/).

Register Channel handlers before passing channels to native code. A Channel is a stream-capable communication object, not a guaranteed one-message/one-shot abstraction. Design cancellation, bounded queues and subscription identity explicitly.

Event/deep-link registration returns an asynchronous unlisten function. If disposal happens before registration resolves, run the unlisten immediately after resolution; catch registration errors. Ignore late messages for a closed component/request. An AbortController only cancels APIs actually wired to its signal; calling `abort()` does not cancel Tauri `invoke` by itself.

Don't collapse `cancelled`, `unavailable`, `denied` and `failed` into null. Don't mutate another account's state from a stale auth or sync reply. Keep browser picker actions in the user gesture when required.

Sources: [IPC](https://v2.tauri.app/develop/calling-rust/), [events](https://v2.tauri.app/develop/calling-frontend/), [camera outcomes](camera-media.md).
