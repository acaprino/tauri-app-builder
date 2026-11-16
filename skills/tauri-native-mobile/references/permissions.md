# Permissions: diagnose the full chain

An OS permission cannot repair a rejected Tauri command. A capability cannot grant an Android runtime permission. A website's microphone prompt cannot add a missing manifest declaration.

| Layer | Check | Typical failure |
|---|---|---|
| Build/platform | Correct Rust dependency, registration, Kotlin/Swift module, JS binding version | `command not found`, missing module |
| Tauri ACL | Exact permission name from the installed plugin's permission files, correct window/webview and platform | IPC rejected before native code |
| Native declaration | Merged Android manifest; iOS usage description and entitlements | No prompt, rejection or platform termination |
| OS state | Granted, denied, permanently denied, limited/approximate or revoked | First launch works differently from later launch |
| WebView | Secure context, origin policy, WebChromeClient/Wry resource mapping | `getUserMedia`/geolocation fails despite an OS grant |
| Lifecycle | Correct permission callback and one pending request owner | User accepts but Promise never settles |

For `tauri-plugin-native-camera`, verify `native-camera:allow-take-picture` against the installed permission definitions. Its default set can exist yet be empty; granting that default does not authorize capture. Package names and ACL namespaces need not match.

For WebView microphone capture, inspect the installed Wry handler and merged manifest: `RECORD_AUDIO` and, in some integrations, the normal install-time `MODIFY_AUDIO_SETTINGS` declaration are both checked. Only the former is a dangerous runtime permission. Location needs the matching coarse/fine declarations; approximate access and disabled service are distinct from denial.

Request access at the feature's entry point. On denial, explain the affected feature and keep independent actions such as gallery available. Use the platform's app-settings entry point for recovery when another prompt is unavailable. On resume, recheck permission and let the user retry; do not loop prompts or auto-start capture. Android 13+ notification permission is separate from channel configuration, scheduling and device notification settings.

For a custom native bridge, allow only trusted app origins and a small validated message schema. An origin captured from the first incoming message is not sufficient by itself unless navigation/frame trust is independently enforced. Do not use a wildcard bridge as a permission bypass.

Test fresh request, denial, repeated denial, revoke in settings, grant in settings, background/resume and screen closed while prompt is open. Do not pre-grant permissions when testing the first-request UX.

Sources: [Tauri capabilities](https://v2.tauri.app/security/capabilities/) and [Android permission requests](https://developer.android.com/training/permissions/requesting).
